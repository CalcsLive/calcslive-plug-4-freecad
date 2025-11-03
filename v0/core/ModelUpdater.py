"""
FreeCAD Model Updater

Updates FreeCAD objects with calculation results from CalcsLive.
Handles parameter mapping, unit conversion, and constraint updates.
"""

import FreeCAD
import Part
from typing import Dict, Any, List, Optional, Union
import re


class ModelUpdater:
    """
    Updates FreeCAD model with CalcsLive calculation results

    Applies calculation results back to FreeCAD objects, handling
    unit conversion and parameter mapping.
    """

    def __init__(self):
        """Initialize model updater"""
        self.update_history = []  # Track updates for undo functionality

        # CalcsLive to FreeCAD unit mapping
        self.unit_mapping = {
            'mm': 'mm',
            'cm': 'cm',
            'm': 'm',
            'km': 'km',
            'in': 'in',
            'ft': 'ft',
            '°': 'deg',
            'rad': 'rad',
            'mm²': 'mm^2',
            'cm²': 'cm^2',
            'm²': 'm^2',
            'mm³': 'mm^3',
            'cm³': 'cm^3',
            'm³': 'm^3',
            'kg': 'kg',
            'g': 'g',
            'N': 'N',
            'Pa': 'Pa',
            'MPa': 'MPa',
            'GPa': 'GPa'
        }

    def update_model_from_calcslive(self, calculation_results: Dict[str, Any],
                                  parameter_mapping: Dict[str, Dict[str, str]],
                                  doc: Optional[FreeCAD.Document] = None) -> Dict[str, Any]:
        """
        Update FreeCAD model with CalcsLive calculation results

        Args:
            calculation_results: Results from CalcsLive API
            parameter_mapping: Map CalcsLive symbols to FreeCAD objects/properties
            doc: FreeCAD document (uses active doc if None)

        Returns:
            Dict with update status and statistics
        """
        if doc is None:
            doc = FreeCAD.ActiveDocument

        if not doc:
            raise ValueError("No active document found")

        update_stats = {
            'successful_updates': 0,
            'failed_updates': 0,
            'skipped_updates': 0,
            'updated_objects': set(),
            'errors': []
        }

        # Extract outputs from calculation results
        outputs = calculation_results.get('outputs', {})

        # Update each mapped parameter
        for calcslive_symbol, mapping_info in parameter_mapping.items():
            if calcslive_symbol in outputs:
                try:
                    result = self._update_single_parameter(
                        calcslive_symbol,
                        outputs[calcslive_symbol],
                        mapping_info,
                        doc
                    )

                    if result['success']:
                        update_stats['successful_updates'] += 1
                        update_stats['updated_objects'].add(mapping_info['object_name'])
                    else:
                        update_stats['failed_updates'] += 1
                        update_stats['errors'].append(result['error'])

                except Exception as e:
                    update_stats['failed_updates'] += 1
                    update_stats['errors'].append(f"Update {calcslive_symbol}: {str(e)}")

            else:
                update_stats['skipped_updates'] += 1
                FreeCAD.Console.PrintWarning(f"CalcsLive symbol '{calcslive_symbol}' not found in results\n")

        # Recompute affected objects
        if update_stats['updated_objects']:
            try:
                doc.recompute()
                FreeCAD.Console.PrintMessage(f"Updated {len(update_stats['updated_objects'])} objects\n")
            except Exception as e:
                update_stats['errors'].append(f"Recompute failed: {str(e)}")

        return update_stats

    def update_selected_objects(self, calculation_results: Dict[str, Any],
                              parameter_mapping: Dict[str, Dict[str, str]]) -> Dict[str, Any]:
        """
        Update only selected FreeCAD objects with calculation results

        Args:
            calculation_results: Results from CalcsLive API
            parameter_mapping: Map CalcsLive symbols to FreeCAD objects/properties

        Returns:
            Dict with update status and statistics
        """
        import FreeCADGui

        selection = FreeCADGui.Selection.getSelection()
        if not selection:
            return {
                'successful_updates': 0,
                'failed_updates': 0,
                'skipped_updates': 0,
                'updated_objects': set(),
                'errors': ['No objects selected']
            }

        # Filter mapping to only include selected objects
        selected_names = {obj.Name for obj in selection}
        filtered_mapping = {
            symbol: mapping for symbol, mapping in parameter_mapping.items()
            if mapping.get('object_name') in selected_names
        }

        return self.update_model_from_calcslive(calculation_results, filtered_mapping)

    def create_parameter_mapping(self, extracted_params: Dict[str, Dict[str, Any]],
                               calcslive_symbols: List[str]) -> Dict[str, Dict[str, str]]:
        """
        Create parameter mapping between CalcsLive symbols and FreeCAD parameters

        Args:
            extracted_params: Parameters extracted from FreeCAD
            calcslive_symbols: Available CalcsLive output symbols

        Returns:
            Dict mapping CalcsLive symbols to FreeCAD object/property info
        """
        mapping = {}

        # Simple name-based mapping for now
        for calcslive_symbol in calcslive_symbols:
            # Try to find matching FreeCAD parameter
            best_match = self._find_best_parameter_match(calcslive_symbol, extracted_params)

            if best_match:
                param_info = extracted_params[best_match]
                mapping[calcslive_symbol] = {
                    'object_name': param_info['source_object'],
                    'property_name': param_info['property_name'],
                    'freecad_param_name': best_match,
                    'mapping_confidence': 'automatic'
                }

        return mapping

    def validate_parameter_mapping(self, parameter_mapping: Dict[str, Dict[str, str]],
                                 doc: Optional[FreeCAD.Document] = None) -> Dict[str, Any]:
        """
        Validate that parameter mapping references exist in FreeCAD model

        Args:
            parameter_mapping: Map CalcsLive symbols to FreeCAD objects/properties
            doc: FreeCAD document (uses active doc if None)

        Returns:
            Dict with validation results
        """
        if doc is None:
            doc = FreeCAD.ActiveDocument

        if not doc:
            return {'valid': False, 'error': 'No active document'}

        validation = {
            'valid_mappings': 0,
            'invalid_mappings': 0,
            'missing_objects': [],
            'missing_properties': [],
            'errors': []
        }

        for calcslive_symbol, mapping_info in parameter_mapping.items():
            object_name = mapping_info.get('object_name')
            property_name = mapping_info.get('property_name')

            # Check if object exists
            if not object_name or not hasattr(doc, object_name):
                validation['invalid_mappings'] += 1
                validation['missing_objects'].append(object_name)
                continue

            obj = getattr(doc, object_name)

            # Check if property exists
            if not property_name or property_name not in obj.PropertiesList:
                validation['invalid_mappings'] += 1
                validation['missing_properties'].append(f"{object_name}.{property_name}")
                continue

            validation['valid_mappings'] += 1

        validation['is_valid'] = validation['invalid_mappings'] == 0
        return validation

    def _update_single_parameter(self, calcslive_symbol: str, calcslive_result: Dict[str, Any],
                               mapping_info: Dict[str, str], doc: FreeCAD.Document) -> Dict[str, Any]:
        """Update a single FreeCAD parameter from CalcsLive result"""

        try:
            object_name = mapping_info['object_name']
            property_name = mapping_info['property_name']

            # Get FreeCAD object
            if not hasattr(doc, object_name):
                return {'success': False, 'error': f"Object '{object_name}' not found"}

            obj = getattr(doc, object_name)

            # Check property exists
            if property_name not in obj.PropertiesList:
                return {'success': False, 'error': f"Property '{property_name}' not found on {object_name}"}

            # Extract value and unit from CalcsLive result
            calcslive_value = calcslive_result.get('value')
            calcslive_unit = calcslive_result.get('unit')

            if calcslive_value is None:
                return {'success': False, 'error': f"No value in CalcsLive result for {calcslive_symbol}"}

            # Convert unit if needed
            freecad_unit = self._convert_unit_to_freecad(calcslive_unit)

            # Update the property
            success = self._set_object_property(obj, property_name, calcslive_value, freecad_unit)

            if success:
                # Record update for history
                self.update_history.append({
                    'timestamp': FreeCAD.now(),
                    'object_name': object_name,
                    'property_name': property_name,
                    'calcslive_symbol': calcslive_symbol,
                    'new_value': calcslive_value,
                    'new_unit': calcslive_unit
                })

                return {'success': True}
            else:
                return {'success': False, 'error': f"Failed to set property {property_name}"}

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def _set_object_property(self, obj: FreeCAD.DocumentObject, property_name: str,
                           value: float, unit: str) -> bool:
        """Set FreeCAD object property with value and unit"""

        try:
            current_prop = getattr(obj, property_name)

            # Handle different property types
            if hasattr(current_prop, 'Value') and hasattr(current_prop, 'Unit'):
                # FreeCAD Quantity - set value and unit
                new_quantity = FreeCAD.Units.Quantity(value, unit)
                setattr(obj, property_name, new_quantity)

            elif isinstance(current_prop, (int, float)):
                # Numeric property - set value directly
                setattr(obj, property_name, float(value))

            else:
                # Try to set as string representation
                setattr(obj, property_name, f"{value} {unit}")

            return True

        except Exception as e:
            FreeCAD.Console.PrintError(f"Failed to set {property_name}: {e}\n")
            return False

    def _convert_unit_to_freecad(self, calcslive_unit: str) -> str:
        """Convert CalcsLive unit to FreeCAD format"""

        if not calcslive_unit:
            return ''

        # Direct mapping
        if calcslive_unit in self.unit_mapping:
            return self.unit_mapping[calcslive_unit]

        # Handle superscript notation
        unit_clean = calcslive_unit.replace('²', '^2').replace('³', '^3')

        return unit_clean

    def _find_best_parameter_match(self, calcslive_symbol: str,
                                 extracted_params: Dict[str, Dict[str, Any]]) -> Optional[str]:
        """Find best matching FreeCAD parameter for CalcsLive symbol"""

        # Try exact match first
        if calcslive_symbol in extracted_params:
            return calcslive_symbol

        # Try case-insensitive match
        for param_name in extracted_params:
            if param_name.lower() == calcslive_symbol.lower():
                return param_name

        # Try partial matches
        for param_name in extracted_params:
            if calcslive_symbol.lower() in param_name.lower():
                return param_name

        # Try reverse partial matches
        for param_name in extracted_params:
            if param_name.lower() in calcslive_symbol.lower():
                return param_name

        return None

    def get_update_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent update history"""
        return self.update_history[-limit:] if self.update_history else []

    def clear_update_history(self):
        """Clear update history"""
        self.update_history.clear()

    def create_update_report(self, update_stats: Dict[str, Any]) -> str:
        """Generate human-readable update report"""

        lines = [
            "CalcsLive Model Update Report",
            "=" * 30,
            f"Successful updates: {update_stats['successful_updates']}",
            f"Failed updates: {update_stats['failed_updates']}",
            f"Skipped updates: {update_stats['skipped_updates']}",
            f"Objects updated: {len(update_stats['updated_objects'])}"
        ]

        if update_stats['updated_objects']:
            lines.append("\nUpdated Objects:")
            for obj_name in sorted(update_stats['updated_objects']):
                lines.append(f"  - {obj_name}")

        if update_stats['errors']:
            lines.append("\nErrors:")
            for error in update_stats['errors']:
                lines.append(f"  - {error}")

        return '\n'.join(lines)

    def suggest_parameter_mappings(self, extracted_params: Dict[str, Dict[str, Any]],
                                 calcslive_outputs: List[str]) -> Dict[str, List[str]]:
        """
        Suggest parameter mappings between CalcsLive and FreeCAD

        Args:
            extracted_params: Parameters extracted from FreeCAD
            calcslive_outputs: Available CalcsLive output symbols

        Returns:
            Dict mapping CalcsLive symbols to suggested FreeCAD parameters
        """
        suggestions = {}

        for calcslive_symbol in calcslive_outputs:
            candidates = []

            # Find all potential matches
            for freecad_param in extracted_params:
                score = self._calculate_match_score(calcslive_symbol, freecad_param)
                if score > 0:
                    candidates.append((freecad_param, score))

            # Sort by match score and take top candidates
            candidates.sort(key=lambda x: x[1], reverse=True)
            suggestions[calcslive_symbol] = [param for param, score in candidates[:3]]

        return suggestions

    def _calculate_match_score(self, calcslive_symbol: str, freecad_param: str) -> float:
        """Calculate similarity score between CalcsLive symbol and FreeCAD parameter"""

        # Exact match
        if calcslive_symbol == freecad_param:
            return 1.0

        # Case-insensitive exact match
        if calcslive_symbol.lower() == freecad_param.lower():
            return 0.9

        # Substring matches
        calcslive_lower = calcslive_symbol.lower()
        freecad_lower = freecad_param.lower()

        if calcslive_lower in freecad_lower:
            return 0.7 * (len(calcslive_lower) / len(freecad_lower))

        if freecad_lower in calcslive_lower:
            return 0.6 * (len(freecad_lower) / len(calcslive_lower))

        # Common prefix/suffix
        common_prefix = len(self._common_prefix(calcslive_lower, freecad_lower))
        common_suffix = len(self._common_suffix(calcslive_lower, freecad_lower))

        if common_prefix > 2 or common_suffix > 2:
            return 0.4 * (common_prefix + common_suffix) / max(len(calcslive_lower), len(freecad_lower))

        return 0.0

    def _common_prefix(self, s1: str, s2: str) -> str:
        """Find common prefix of two strings"""
        i = 0
        while i < min(len(s1), len(s2)) and s1[i] == s2[i]:
            i += 1
        return s1[:i]

    def _common_suffix(self, s1: str, s2: str) -> str:
        """Find common suffix of two strings"""
        i = 0
        while i < min(len(s1), len(s2)) and s1[-(i+1)] == s2[-(i+1)]:
            i += 1
        return s1[-i:] if i > 0 else ""


# Utility functions for common operations
def update_model_from_calcslive(calculation_results: Dict[str, Any],
                              parameter_mapping: Dict[str, Dict[str, str]],
                              doc: Optional[FreeCAD.Document] = None) -> Dict[str, Any]:
    """Convenience function to update model from CalcsLive results"""
    updater = ModelUpdater()
    return updater.update_model_from_calcslive(calculation_results, parameter_mapping, doc)


def suggest_parameter_mappings(extracted_params: Dict[str, Dict[str, Any]],
                             calcslive_outputs: List[str]) -> Dict[str, List[str]]:
    """Convenience function to suggest parameter mappings"""
    updater = ModelUpdater()
    return updater.suggest_parameter_mappings(extracted_params, calcslive_outputs)