"""
Unit Mapping System for FreeCAD ↔ CalcsLive Integration

Provides static unit mappings between FreeCAD's internal unit system
and CalcsLive's Physical Quantity (PQ) unit system.

Following separation of concerns principle:
- FreeCAD handles modeling and units it knows
- CalcsLive handles calculations and its comprehensive unit system
- This mapper provides the bridge between the two systems
"""

import FreeCAD


class UnitMapper:
    """
    Static unit mapping between FreeCAD and CalcsLive

    Maps only the units that FreeCAD actually uses to avoid
    unnecessary complexity and maintain clean separation of concerns.
    """

    # Static mapping table: FreeCAD unit → CalcsLive unit
    FREECAD_TO_CALCSLIVE = {
        # Length units
        'mm': 'mm',         # millimeter (FreeCAD's internal length unit)
        'cm': 'cm',         # centimeter
        'm': 'm',           # meter
        'in': 'in',         # inch
        'ft': 'ft',         # foot

        # Area units
        'mm²': 'mm²',       # square millimeter
        'cm²': 'cm²',       # square centimeter
        'm²': 'm²',         # square meter
        'in²': 'in²',       # square inch
        'ft²': 'ft²',       # square foot

        # Volume units
        'mm³': 'mm³',       # cubic millimeter
        'cm³': 'cm³',       # cubic centimeter
        'm³': 'm³',         # cubic meter
        'in³': 'in³',       # cubic inch
        'ft³': 'ft³',       # cubic foot
        'l': 'L',           # liter (FreeCAD uses 'l', CalcsLive uses 'L')

        # Angular units
        'deg': '°',         # degree (FreeCAD uses 'deg', CalcsLive uses '°')
        'rad': 'rad',       # radian

        # Mass units
        'g': 'g',           # gram
        'kg': 'kg',         # kilogram
        'lb': 'lbm',        # pound mass (FreeCAD 'lb' → CalcsLive 'lbm')

        # Force units
        'N': 'N',           # newton
        'kN': 'kN',         # kilonewton
        'lbf': 'lbf',       # pound force

        # Pressure units
        'Pa': 'Pa',         # pascal
        'kPa': 'kPa',       # kilopascal
        'MPa': 'MPa',       # megapascal
        'bar': 'bar',       # bar
        'psi': 'psi',       # pounds per square inch

        # Time units
        's': 's',           # second
        'min': 'min',       # minute
        'h': 'h',           # hour

        # Temperature units
        'K': 'K',           # kelvin
        '°C': '°C',         # celsius
        '°F': '°F',         # fahrenheit
    }

    # Reverse mapping: CalcsLive unit → FreeCAD unit
    CALCSLIVE_TO_FREECAD = {v: k for k, v in FREECAD_TO_CALCSLIVE.items()}

    # Special cases where reverse mapping needs adjustment
    CALCSLIVE_TO_FREECAD.update({
        'L': 'l',           # CalcsLive 'L' → FreeCAD 'l'
        '°': 'deg',         # CalcsLive '°' → FreeCAD 'deg'
        'lbm': 'lb',        # CalcsLive 'lbm' → FreeCAD 'lb'
    })

    @classmethod
    def freecad_to_calcslive(cls, freecad_unit: str) -> str:
        """
        Map FreeCAD unit to CalcsLive unit

        Args:
            freecad_unit: Unit string from FreeCAD (e.g., 'mm', 'deg', 'mm²')

        Returns:
            CalcsLive unit string (e.g., 'mm', '°', 'mm²')

        Raises:
            ValueError: If unit mapping is not found
        """
        if freecad_unit in cls.FREECAD_TO_CALCSLIVE:
            return cls.FREECAD_TO_CALCSLIVE[freecad_unit]

        # If no mapping found, warn and return original
        FreeCAD.Console.PrintWarning(
            f"UnitMapper: No mapping found for FreeCAD unit '{freecad_unit}', using as-is\n"
        )
        return freecad_unit

    @classmethod
    def calcslive_to_freecad(cls, calcslive_unit: str) -> str:
        """
        Map CalcsLive unit to FreeCAD unit

        Args:
            calcslive_unit: Unit string from CalcsLive (e.g., 'mm', '°', 'mm²')

        Returns:
            FreeCAD unit string (e.g., 'mm', 'deg', 'mm²')

        Raises:
            ValueError: If unit mapping is not found
        """
        if calcslive_unit in cls.CALCSLIVE_TO_FREECAD:
            return cls.CALCSLIVE_TO_FREECAD[calcslive_unit]

        # If no mapping found, warn and return original
        FreeCAD.Console.PrintWarning(
            f"UnitMapper: No mapping found for CalcsLive unit '{calcslive_unit}', using as-is\n"
        )
        return calcslive_unit

    @classmethod
    def is_supported_freecad_unit(cls, unit: str) -> bool:
        """
        Check if FreeCAD unit is supported for mapping

        Args:
            unit: FreeCAD unit string

        Returns:
            True if unit can be mapped to CalcsLive
        """
        return unit in cls.FREECAD_TO_CALCSLIVE

    @classmethod
    def is_supported_calcslive_unit(cls, unit: str) -> bool:
        """
        Check if CalcsLive unit is supported for mapping

        Args:
            unit: CalcsLive unit string

        Returns:
            True if unit can be mapped to FreeCAD
        """
        return unit in cls.CALCSLIVE_TO_FREECAD

    @classmethod
    def get_supported_freecad_units(cls) -> list:
        """
        Get list of all supported FreeCAD units

        Returns:
            List of FreeCAD unit strings that can be mapped
        """
        return list(cls.FREECAD_TO_CALCSLIVE.keys())

    @classmethod
    def get_supported_calcslive_units(cls) -> list:
        """
        Get list of all supported CalcsLive units

        Returns:
            List of CalcsLive unit strings that can be mapped
        """
        return list(cls.CALCSLIVE_TO_FREECAD.keys())

    @classmethod
    def map_parameter_units(cls, parameters: list) -> list:
        """
        Map units for a list of FreeCAD parameters

        Args:
            parameters: List of parameter dictionaries with 'unit' field

        Returns:
            List of parameters with added 'calcslive_unit' field
        """
        mapped_parameters = []

        for param in parameters:
            mapped_param = param.copy()
            freecad_unit = param.get('unit', '')

            # Map the unit
            calcslive_unit = cls.freecad_to_calcslive(freecad_unit)
            mapped_param['calcslive_unit'] = calcslive_unit
            mapped_param['unit_mapped'] = (freecad_unit != calcslive_unit)

            mapped_parameters.append(mapped_param)

            # Log the mapping for debugging
            if mapped_param['unit_mapped']:
                FreeCAD.Console.PrintMessage(
                    f"UnitMapper: '{freecad_unit}' → '{calcslive_unit}'\n"
                )

        return mapped_parameters

    @classmethod
    def validate_mapping(cls) -> dict:
        """
        Validate the unit mapping tables for consistency

        Returns:
            Dictionary with validation results and any issues found
        """
        results = {
            'valid': True,
            'issues': [],
            'stats': {
                'freecad_units': len(cls.FREECAD_TO_CALCSLIVE),
                'calcslive_units': len(cls.CALCSLIVE_TO_FREECAD),
                'bidirectional_mappings': 0
            }
        }

        # Check bidirectional mapping consistency
        bidirectional_count = 0
        for fc_unit, cl_unit in cls.FREECAD_TO_CALCSLIVE.items():
            if cl_unit in cls.CALCSLIVE_TO_FREECAD:
                reverse_mapped = cls.CALCSLIVE_TO_FREECAD[cl_unit]
                if reverse_mapped == fc_unit:
                    bidirectional_count += 1
                else:
                    results['issues'].append(
                        f"Bidirectional mapping issue: {fc_unit} → {cl_unit} → {reverse_mapped}"
                    )
                    results['valid'] = False

        results['stats']['bidirectional_mappings'] = bidirectional_count

        return results


def test_unit_mapper():
    """
    Test function to validate the unit mapping system
    """
    FreeCAD.Console.PrintMessage("Testing UnitMapper...\n")

    # Test individual mappings
    test_cases = [
        ('mm', 'mm'),
        ('deg', '°'),
        ('mm²', 'mm²'),
        ('l', 'L'),
        ('lb', 'lbm')
    ]

    for fc_unit, expected_cl_unit in test_cases:
        cl_unit = UnitMapper.freecad_to_calcslive(fc_unit)
        fc_back = UnitMapper.calcslive_to_freecad(cl_unit)

        FreeCAD.Console.PrintMessage(
            f"  {fc_unit} → {cl_unit} → {fc_back} "
            f"{'✓' if cl_unit == expected_cl_unit else '✗'}\n"
        )

    # Validate mapping consistency
    validation = UnitMapper.validate_mapping()
    FreeCAD.Console.PrintMessage(f"Validation: {'✓ PASSED' if validation['valid'] else '✗ FAILED'}\n")

    if validation['issues']:
        for issue in validation['issues']:
            FreeCAD.Console.PrintWarning(f"  Issue: {issue}\n")

    FreeCAD.Console.PrintMessage(
        f"Stats: {validation['stats']['freecad_units']} FreeCAD units, "
        f"{validation['stats']['calcslive_units']} CalcsLive units, "
        f"{validation['stats']['bidirectional_mappings']} bidirectional\n"
    )


if __name__ == "__main__":
    test_unit_mapper()