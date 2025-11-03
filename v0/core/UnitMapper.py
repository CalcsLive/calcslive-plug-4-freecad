"""
Simplified Unit System for FreeCAD ↔ CalcsLive Integration

Simplified approach based on user feedback:
1. Send FreeCAD units directly to CalcsLive (CalcsLive understands them)
2. Only convert when sending data back from CalcsLive to FreeCAD internal units
3. Let CalcsLive handle unit parsing and FreeCAD handle display units

Example workflow:
- FreeCAD: Cylinder_Radius = 50.8 mm → CalcsLive: Cylinder_Radius = 50.8 mm (direct)
- CalcsLive: r = 20 in → FreeCAD: 508 mm (convert to internal units)
"""

import FreeCAD


class UnitMapper:
    """
    Simplified unit handling for FreeCAD ↔ CalcsLive integration

    Philosophy: Let each system handle what it does best
    - FreeCAD: Handles internal units and display preferences
    - CalcsLive: Handles unit parsing and conversions
    - Mapper: Only converts CalcsLive results back to FreeCAD internal units
    """

    # Only map units when converting CalcsLive → FreeCAD internal units
    CALCSLIVE_TO_FREECAD_INTERNAL = {
        # Length units → mm (FreeCAD internal)
        'mm': 1.0,          # millimeter (already internal)
        'cm': 10.0,         # centimeter → mm
        'm': 1000.0,        # meter → mm
        'in': 25.4,         # inch → mm
        'ft': 304.8,        # foot → mm

        # Angular units → deg (FreeCAD internal)
        '°': 1.0,           # degree (already internal)
        'deg': 1.0,         # degree (already internal)
        'rad': 57.29578,    # radian → degree

        # Area units → mm² (FreeCAD internal)
        'mm²': 1.0,         # square millimeter (already internal)
        'cm²': 100.0,       # square centimeter → mm²
        'm²': 1000000.0,    # square meter → mm²
        'in²': 645.16,      # square inch → mm²
        'ft²': 92903.04,    # square foot → mm²

        # Volume units → mm³ (FreeCAD internal)
        'mm³': 1.0,         # cubic millimeter (already internal)
        'cm³': 1000.0,      # cubic centimeter → mm³
        'L': 1000000.0,     # liter → mm³
        'm³': 1000000000.0, # cubic meter → mm³
        'in³': 16387.064,   # cubic inch → mm³
        'ft³': 28316846.6,  # cubic foot → mm³
    }

    @classmethod
    def freecad_to_calcslive_direct(cls, freecad_unit: str) -> str:
        """
        Pass FreeCAD unit directly to CalcsLive (simplified approach)

        CalcsLive can understand FreeCAD units directly, so no conversion needed.
        Only handle special cases where FreeCAD uses different notation.

        Args:
            freecad_unit: Unit string from FreeCAD (e.g., 'mm', 'deg')

        Returns:
            Unit string for CalcsLive (usually the same)
        """
        # Special case mappings where FreeCAD and CalcsLive use different notation
        special_cases = {
            'deg': '°',         # FreeCAD uses 'deg', CalcsLive prefers '°'
        }

        return special_cases.get(freecad_unit, freecad_unit)

    @classmethod
    def calcslive_to_freecad_internal(cls, value: float, calcslive_unit: str) -> tuple:
        """
        Convert CalcsLive value with unit to FreeCAD internal units

        Args:
            value: Numeric value from CalcsLive
            calcslive_unit: Unit string from CalcsLive (e.g., 'in', '°C', 'ft³')

        Returns:
            tuple: (converted_value, freecad_internal_unit)

        Example:
            calcslive_to_freecad_internal(20, 'in') → (508.0, 'mm')
            calcslive_to_freecad_internal(45, '°') → (45.0, 'deg')
        """
        if calcslive_unit in cls.CALCSLIVE_TO_FREECAD_INTERNAL:
            conversion_factor = cls.CALCSLIVE_TO_FREECAD_INTERNAL[calcslive_unit]
            converted_value = value * conversion_factor

            # Determine FreeCAD internal unit based on unit type
            if calcslive_unit in ['mm', 'cm', 'm', 'in', 'ft']:
                freecad_unit = 'mm'
            elif calcslive_unit in ['°', 'deg', 'rad']:
                freecad_unit = 'deg'
            elif calcslive_unit in ['mm²', 'cm²', 'm²', 'in²', 'ft²']:
                freecad_unit = 'mm²'
            elif calcslive_unit in ['mm³', 'cm³', 'L', 'm³', 'in³', 'ft³']:
                freecad_unit = 'mm³'
            else:
                freecad_unit = calcslive_unit  # Fallback

            return (converted_value, freecad_unit)
        else:
            # Unknown unit - pass through with warning
            FreeCAD.Console.PrintWarning(f"UnitMapper: Unknown CalcsLive unit '{calcslive_unit}', using as-is\n")
            return (value, calcslive_unit)

    @classmethod
    def map_parameter_units(cls, parameters):
        """
        Apply simplified unit mapping to parameter list

        For FreeCAD → CalcsLive: Pass units directly (CalcsLive handles parsing)
        For CalcsLive → FreeCAD: Convert to internal units when needed

        Args:
            parameters: List of parameter dictionaries

        Returns:
            List of parameters with appropriate unit mappings applied
        """
        mapped_parameters = []

        for param in parameters:
            # Create a copy to avoid modifying original
            mapped_param = param.copy()

            # For FreeCAD → CalcsLive: Use direct unit passing
            original_unit = param.get('unit', '')
            calcslive_unit = cls.freecad_to_calcslive_direct(original_unit)

            mapped_param['calcslive_unit'] = calcslive_unit
            mapped_param['unit_mapped'] = (calcslive_unit != original_unit)

            mapped_parameters.append(mapped_param)

        return mapped_parameters

    @classmethod
    def create_parameter_summary(cls, parameters):
        """
        Create a summary of parameter mapping for logging

        Args:
            parameters: List of mapped parameters

        Returns:
            Dictionary with mapping statistics
        """
        total_params = len(parameters)
        mapped_count = sum(1 for p in parameters if p.get('unit_mapped', False))

        return {
            'total_parameters': total_params,
            'unit_mappings_applied': mapped_count,
            'direct_passthrough': total_params - mapped_count
        }