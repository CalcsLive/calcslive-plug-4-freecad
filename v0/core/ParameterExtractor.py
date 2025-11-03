"""
FreeCAD Parameter Extractor

Extracts parameters from FreeCAD objects and converts them to CalcsLive format.
Handles dimensional properties, constraints, and custom parameters.
"""

import FreeCAD
import Part
from typing import Dict, Any, List, Optional, Union
import re


class ParameterExtractor:
    """
    Extracts parameters from FreeCAD objects and prepares them for CalcsLive

    Handles various FreeCAD property types and converts them to CalcsLive's
    value/unit format for calculations.
    """

    def __init__(self):
        """Initialize parameter extractor"""
        self.supported_types = {
            'Length', 'Distance', 'Angle', 'Area', 'Volume', 'Mass',
            'Force', 'Pressure', 'Velocity', 'Acceleration', 'Power',
            'Energy', 'Frequency', 'Temperature', 'Float', 'Integer'
        }

        # FreeCAD unit mapping to CalcsLive units
        self.unit_mapping = {
            'mm': 'mm',
            'cm': 'cm',
            'm': 'm',
            'km': 'km',
            'in': 'in',
            'ft': 'ft',
            'deg': '°',
            'rad': 'rad',
            'mm^2': 'mm²',
            'cm^2': 'cm²',
            'm^2': 'm²',
            'mm^3': 'mm³',
            'cm^3': 'cm³',
            'm^3': 'm³',
            'kg': 'kg',
            'g': 'g',
            'N': 'N',
            'Pa': 'Pa',
            'MPa': 'MPa',
            'GPa': 'GPa'
        }

    def extract_document_parameters(self, doc: Optional[FreeCAD.Document] = None) -> Dict[str, Dict[str, Any]]:
        """
        Extract all relevant parameters from FreeCAD document

        Args:
            doc: FreeCAD document (uses active doc if None)

        Returns:
            Dict of parameter_name -> {value, unit, source_object, property_name}
        """
        if doc is None:
            doc = FreeCAD.ActiveDocument

        if not doc:
            raise ValueError("No active document found")

        parameters = {}

        # Extract from all objects in document
        for obj in doc.Objects:
            obj_params = self.extract_object_parameters(obj)
            parameters.update(obj_params)

        # Extract spreadsheet parameters
        spreadsheet_params = self.extract_spreadsheet_parameters(doc)
        parameters.update(spreadsheet_params)

        return parameters

    def extract_object_parameters(self, obj: FreeCAD.DocumentObject) -> Dict[str, Dict[str, Any]]:
        """
        Extract parameters from a single FreeCAD object

        Args:
            obj: FreeCAD object to extract from

        Returns:
            Dict of parameter_name -> {value, unit, source_object, property_name}
        """
        parameters = {}

        # Get all properties with dimensional quantities
        for prop_name in obj.PropertiesList:
            try:
                prop_value = getattr(obj, prop_name)
                prop_type = obj.getTypeIdOfProperty(prop_name)

                # Check if property has dimensional value
                if self._is_dimensional_property(prop_type, prop_value):
                    param_info = self._extract_dimensional_parameter(
                        obj, prop_name, prop_value, prop_type
                    )

                    if param_info:
                        # Create unique parameter name
                        param_name = f"{obj.Label}_{prop_name}"
                        param_name = self._sanitize_parameter_name(param_name)
                        parameters[param_name] = param_info

            except Exception as e:
                FreeCAD.Console.PrintWarning(f"Failed to extract {prop_name} from {obj.Label}: {e}\n")

        return parameters

    def extract_spreadsheet_parameters(self, doc: FreeCAD.Document) -> Dict[str, Dict[str, Any]]:
        """
        Extract parameters from FreeCAD spreadsheets

        Args:
            doc: FreeCAD document

        Returns:
            Dict of parameter_name -> {value, unit, source_object, property_name}
        """
        parameters = {}

        # Find all spreadsheet objects
        spreadsheets = [obj for obj in doc.Objects if obj.TypeId == 'Spreadsheet::Sheet']

        for sheet in spreadsheets:
            try:
                # Scan spreadsheet cells for parameters
                sheet_params = self._extract_sheet_cells(sheet)
                parameters.update(sheet_params)

            except Exception as e:
                FreeCAD.Console.PrintWarning(f"Failed to extract from spreadsheet {sheet.Label}: {e}\n")

        return parameters

    def get_selected_parameters(self) -> Dict[str, Dict[str, Any]]:
        """
        Extract parameters from currently selected objects

        Returns:
            Dict of parameter_name -> {value, unit, source_object, property_name}
        """
        import FreeCADGui

        parameters = {}
        selection = FreeCADGui.Selection.getSelection()

        for obj in selection:
            obj_params = self.extract_object_parameters(obj)
            parameters.update(obj_params)

        return parameters

    def _is_dimensional_property(self, prop_type: str, prop_value: Any) -> bool:
        """Check if property contains dimensional quantity"""

        # Check for FreeCAD quantity types
        if hasattr(prop_value, 'Value') and hasattr(prop_value, 'Unit'):
            return True

        # Check for supported property types
        dimensional_types = [
            'App::PropertyLength', 'App::PropertyDistance', 'App::PropertyAngle',
            'App::PropertyArea', 'App::PropertyVolume', 'App::PropertyMass',
            'App::PropertyForce', 'App::PropertyPressure', 'App::PropertyVelocity',
            'App::PropertyAcceleration', 'App::PropertyPower', 'App::PropertyEnergy',
            'App::PropertyFrequency', 'App::PropertyTemperature'
        ]

        return prop_type in dimensional_types

    def _extract_dimensional_parameter(self, obj: FreeCAD.DocumentObject,
                                     prop_name: str, prop_value: Any,
                                     prop_type: str) -> Optional[Dict[str, Any]]:
        """Extract dimensional parameter information"""

        try:
            # Handle FreeCAD Quantity objects
            if hasattr(prop_value, 'Value') and hasattr(prop_value, 'Unit'):
                value = float(prop_value.Value)
                unit = str(prop_value.Unit)

                # Convert FreeCAD unit to CalcsLive format
                calcslive_unit = self._convert_unit(unit)

                return {
                    'value': value,
                    'unit': calcslive_unit,
                    'source_object': obj.Name,
                    'source_label': obj.Label,
                    'property_name': prop_name,
                    'property_type': prop_type,
                    'original_unit': unit
                }

            # Handle numeric properties with inferred units
            elif isinstance(prop_value, (int, float)):
                inferred_unit = self._infer_unit_from_property_type(prop_type)

                if inferred_unit:
                    return {
                        'value': float(prop_value),
                        'unit': inferred_unit,
                        'source_object': obj.Name,
                        'source_label': obj.Label,
                        'property_name': prop_name,
                        'property_type': prop_type,
                        'inferred_unit': True
                    }

        except Exception as e:
            FreeCAD.Console.PrintWarning(f"Failed to extract parameter {prop_name}: {e}\n")

        return None

    def _extract_sheet_cells(self, sheet: FreeCAD.DocumentObject) -> Dict[str, Dict[str, Any]]:
        """Extract parameters from spreadsheet cells"""
        parameters = {}

        # Scan common cell ranges for parameters
        for row in range(1, 101):  # Rows 1-100
            for col_letter in 'ABCDEFGHIJ':  # Columns A-J
                cell_addr = f"{col_letter}{row}"

                try:
                    # Get cell content
                    cell_content = sheet.getCellFromAlias(cell_addr)

                    if cell_content and self._looks_like_parameter(cell_content):
                        param_info = self._parse_spreadsheet_parameter(
                            sheet, cell_addr, cell_content
                        )

                        if param_info:
                            param_name = f"{sheet.Label}_{cell_addr}"
                            param_name = self._sanitize_parameter_name(param_name)
                            parameters[param_name] = param_info

                except Exception:
                    continue  # Skip invalid cells

        return parameters

    def _convert_unit(self, freecad_unit: str) -> str:
        """Convert FreeCAD unit string to CalcsLive format"""

        # Clean up FreeCAD unit string
        unit_clean = freecad_unit.strip()

        # Direct mapping
        if unit_clean in self.unit_mapping:
            return self.unit_mapping[unit_clean]

        # Handle compound units
        if '^' in unit_clean:
            # Convert exponent notation
            unit_clean = unit_clean.replace('^2', '²').replace('^3', '³')

        # Default fallback
        return unit_clean if unit_clean else 'dimensionless'

    def _infer_unit_from_property_type(self, prop_type: str) -> Optional[str]:
        """Infer unit from FreeCAD property type"""

        type_unit_map = {
            'App::PropertyLength': 'mm',
            'App::PropertyDistance': 'mm',
            'App::PropertyAngle': '°',
            'App::PropertyArea': 'mm²',
            'App::PropertyVolume': 'mm³',
            'App::PropertyMass': 'kg',
            'App::PropertyForce': 'N',
            'App::PropertyPressure': 'Pa',
            'App::PropertyVelocity': 'm/s',
            'App::PropertyAcceleration': 'm/s²',
            'App::PropertyPower': 'W',
            'App::PropertyEnergy': 'J',
            'App::PropertyFrequency': 'Hz',
            'App::PropertyTemperature': '°C'
        }

        return type_unit_map.get(prop_type)

    def _looks_like_parameter(self, content: str) -> bool:
        """Check if spreadsheet cell content looks like a parameter"""

        if not content or not isinstance(content, str):
            return False

        # Look for patterns like "5.0 mm", "25 deg", "100 N"
        pattern = r'^\s*[\d\.\-\+]+\s*[a-zA-Z²³°]+\s*$'
        return bool(re.match(pattern, content.strip()))

    def _parse_spreadsheet_parameter(self, sheet: FreeCAD.DocumentObject,
                                   cell_addr: str, content: str) -> Optional[Dict[str, Any]]:
        """Parse parameter from spreadsheet cell content"""

        try:
            # Pattern to extract value and unit
            pattern = r'^\s*([\d\.\-\+]+)\s*([a-zA-Z²³°]+)\s*$'
            match = re.match(pattern, content.strip())

            if match:
                value = float(match.group(1))
                unit = match.group(2)

                # Convert to CalcsLive unit
                calcslive_unit = self._convert_unit(unit)

                return {
                    'value': value,
                    'unit': calcslive_unit,
                    'source_object': sheet.Name,
                    'source_label': sheet.Label,
                    'property_name': cell_addr,
                    'property_type': 'Spreadsheet::Cell',
                    'original_unit': unit,
                    'cell_address': cell_addr
                }

        except Exception as e:
            FreeCAD.Console.PrintWarning(f"Failed to parse spreadsheet parameter {cell_addr}: {e}\n")

        return None

    def _sanitize_parameter_name(self, name: str) -> str:
        """Sanitize parameter name for CalcsLive compatibility"""

        # Replace invalid characters with underscores
        sanitized = re.sub(r'[^a-zA-Z0-9_]', '_', name)

        # Ensure it starts with letter or underscore
        if sanitized and sanitized[0].isdigit():
            sanitized = f"param_{sanitized}"

        # Limit length
        if len(sanitized) > 50:
            sanitized = sanitized[:50]

        return sanitized or "unnamed_param"

    def format_for_calcslive(self, parameters: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """
        Format extracted parameters for CalcsLive API

        Args:
            parameters: Raw extracted parameters

        Returns:
            Dict formatted for CalcsLive inputs: {symbol -> {value, unit}}
        """
        formatted = {}

        for param_name, param_info in parameters.items():
            formatted[param_name] = {
                'value': param_info['value'],
                'unit': param_info['unit']
            }

        return formatted

    def get_parameter_summary(self, parameters: Dict[str, Dict[str, Any]]) -> str:
        """Generate human-readable summary of extracted parameters"""

        if not parameters:
            return "No parameters extracted."

        summary_lines = [f"Extracted {len(parameters)} parameters:"]

        for param_name, param_info in parameters.items():
            source = param_info.get('source_label', param_info.get('source_object', 'Unknown'))
            prop = param_info.get('property_name', 'Unknown')
            value = param_info['value']
            unit = param_info['unit']

            summary_lines.append(f"  {param_name}: {value} {unit} (from {source}.{prop})")

        return '\n'.join(summary_lines)


# Utility functions for common operations
def extract_document_parameters(doc: Optional[FreeCAD.Document] = None) -> Dict[str, Dict[str, Any]]:
    """Convenience function to extract parameters from document"""
    extractor = ParameterExtractor()
    return extractor.extract_document_parameters(doc)


def extract_selected_parameters() -> Dict[str, Dict[str, Any]]:
    """Convenience function to extract parameters from selection"""
    extractor = ParameterExtractor()
    return extractor.get_selected_parameters()


def format_parameters_for_calcslive(parameters: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """Convenience function to format parameters for CalcsLive"""
    extractor = ParameterExtractor()
    return extractor.format_for_calcslive(parameters)