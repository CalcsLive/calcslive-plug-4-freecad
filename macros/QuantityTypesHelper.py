# QuantityTypesHelper.py
#
# Helper module for extracting FreeCAD quantity types
# Can be imported by FC_CL_Bridge to provide dynamic quantity types data

import FreeCAD as App
import json

class QuantityTypesExtractor:
    """
    Extract and analyze FreeCAD property types for CalcsLive integration
    """

    # Known FreeCAD property types with CLEAN base units (filtered from real FreeCAD data)
    # Based on ExtractQuantityTypes.FCMacro results - only includes simple, usable base unit formats
    KNOWN_PROPERTY_TYPES = {
        # ===== CLEAN QUANTITY TYPES (verified from FreeCAD) =====

        # Geometric quantities (from actual FreeCAD data)
        "App::PropertyLength": {"base_unit": "mm", "category": "Length", "calcslive_category": "Length"},
        "App::PropertyDistance": {"base_unit": "mm", "category": "Length", "calcslive_category": "Length"},
        "App::PropertyArea": {"base_unit": "mm²", "category": "Area", "calcslive_category": "Area"},
        "App::PropertyVolume": {"base_unit": "mm³", "category": "Volume", "calcslive_category": "Volume"},

        # Physical quantities (from actual FreeCAD data)
        "App::PropertyMass": {"base_unit": "kg", "category": "Mass", "calcslive_category": "Mass"},
        "App::PropertyDensity": {"base_unit": "kg/mm³", "category": "Density", "calcslive_category": "Density"},
        "App::PropertyAngle": {"base_unit": "rad", "category": "Angle", "calcslive_category": "Angle"},

        # Mechanical quantities (from actual FreeCAD data)
        "App::PropertyForce": {"base_unit": "N", "category": "Force", "calcslive_category": "Force"},
        "App::PropertyPressure": {"base_unit": "Pa", "category": "Pressure", "calcslive_category": "Pressure"},

        # Motion quantities (from actual FreeCAD data)
        "App::PropertySpeed": {"base_unit": "mm/s", "category": "Velocity", "calcslive_category": "Velocity"},
        "App::PropertyAcceleration": {"base_unit": "mm/s²", "category": "Acceleration", "calcslive_category": "Acceleration"},

        # Energy and power (from actual FreeCAD data)
        "App::PropertyPower": {"base_unit": "W", "category": "Power", "calcslive_category": "Power"},

        # Time and frequency (from actual FreeCAD data)
        "App::PropertyTime": {"base_unit": "s", "category": "Time", "calcslive_category": "Time"},
        "App::PropertyFrequency": {"base_unit": "Hz", "category": "Frequency", "calcslive_category": "Frequency"},

        # Thermal quantities (from actual FreeCAD data)
        "App::PropertyTemperature": {"base_unit": "K", "category": "Temperature", "calcslive_category": "Temperature"},

        # ===== ADDITIONAL TYPES (seen in VarSet UI but not in extraction) =====

        # Additional property types mentioned in VarSet UI
        "App::PropertyStress": {"base_unit": "Pa", "category": "Pressure", "calcslive_category": "Pressure"},
        "App::PropertyVolumeFlowRate": {"base_unit": "mm³/s", "category": "VolumeFlowRate", "calcslive_category": "VolumeFlowRate"},
        "App::PropertyVelocity": {"base_unit": "mm/s", "category": "Velocity", "calcslive_category": "Velocity"},
        "App::PropertyEnergy": {"base_unit": "J", "category": "Energy", "calcslive_category": "Energy"},

        # ===== DIMENSIONLESS QUANTITIES =====

        # Generic quantities (simplified - FreeCAD shows complex "Unit: (0,0,0,0,0,0,0,0)" format)
        "App::PropertyQuantity": {"base_unit": "1", "category": "Dimensionless", "calcslive_category": "Dimensionless"},
        "App::PropertyQuantityConstraint": {"base_unit": "1", "category": "Dimensionless", "calcslive_category": "Dimensionless"},

        # ===== NON-QUANTITY TYPES =====

        # Non-quantity types (from actual FreeCAD data)
        "App::PropertyFloat": {"base_unit": None, "category": "Numeric", "calcslive_category": None},
        "App::PropertyInteger": {"base_unit": None, "category": "Numeric", "calcslive_category": None},
        "App::PropertyBool": {"base_unit": None, "category": "Boolean", "calcslive_category": None},
        "App::PropertyString": {"base_unit": None, "category": "Text", "calcslive_category": None},
        "App::PropertyVector": {"base_unit": None, "category": "Vector", "calcslive_category": None},
        "App::PropertyVectorDistance": {"base_unit": None, "category": "Vector", "calcslive_category": None},
        "App::PropertyPlacement": {"base_unit": None, "category": "Placement", "calcslive_category": None},
        "App::PropertyRotation": {"base_unit": None, "category": "Rotation", "calcslive_category": None},
        "App::PropertyMaterial": {"base_unit": None, "category": "Material", "calcslive_category": None},
        "App::PropertyColor": {"base_unit": None, "category": "Color", "calcslive_category": None},

        # ===== EXCLUDED TYPES (Problematic base unit formats) =====
        #
        # These property types exist in FreeCAD but have complex unit formats:
        # - "App::PropertyElectricCurrent": "Unit: A (0,0,0,1,0,0,0,0) [ElectricCurrent]"
        # - "App::PropertyElectricPotential": "Unit: mm^2*kg/(s^3*A) (2,1,-3,-1,0,0,0,0) [ElectricPotential]"
        #
        # We exclude these until FreeCAD provides cleaner base unit formats
    }

    @classmethod
    def get_all_quantity_types(cls):
        """
        Get all known FreeCAD quantity types
        """
        return cls.KNOWN_PROPERTY_TYPES

    @classmethod
    def get_base_unit_mappings(cls):
        """
        Get mapping of FreeCAD base units to CalcsLive base units
        """
        base_unit_mappings = {}

        for prop_type, info in cls.KNOWN_PROPERTY_TYPES.items():
            freecad_unit = info.get("base_unit")
            calcslive_category = info.get("calcslive_category")

            if freecad_unit and calcslive_category:
                calcslive_unit = cls.get_calcslive_base_unit(calcslive_category)
                if calcslive_unit:
                    base_unit_mappings[freecad_unit] = {
                        "calcslive_base": calcslive_unit,
                        "conversion_factor": cls.get_conversion_factor(freecad_unit, calcslive_unit),
                        "property_types": []
                    }

        # Add property types to each base unit mapping
        for prop_type, info in cls.KNOWN_PROPERTY_TYPES.items():
            freecad_unit = info.get("base_unit")
            if freecad_unit in base_unit_mappings:
                base_unit_mappings[freecad_unit]["property_types"].append(prop_type)

        return base_unit_mappings

    @classmethod
    def get_calcslive_base_unit(cls, calcslive_category):
        """
        Get CalcsLive base unit for a given category
        """
        calcslive_base_units = {
            "Length": "m",
            "Area": "m²",
            "Volume": "m³",
            "Mass": "kg",
            "Density": "kg/m³",
            "Angle": "rad",
            "Force": "N",
            "Pressure": "Pa",
            "Velocity": "m/s",
            "Acceleration": "m/s²",
            "Energy": "J",
            "Power": "W",
            "Time": "s",
            "Frequency": "Hz",
            "Temperature": "K",
            "VolumeFlowRate": "m³/s",
            "ThermalConductivity": "W/(m·K)",
            "ThermalExpansion": "1/K",
            "SpecificHeat": "J/(kg·K)",
            "ElectricCurrent": "A",
            "ElectricPotential": "V",
            "Dimensionless": "1"
        }
        return calcslive_base_units.get(calcslive_category)

    @classmethod
    def get_conversion_factor(cls, freecad_unit, calcslive_unit):
        """
        Get conversion factor from FreeCAD unit to CalcsLive unit
        """
        conversion_factors = {
            # Length: mm → m
            ("mm", "m"): 0.001,
            ("cm", "m"): 0.01,
            ("m", "m"): 1.0,

            # Area: mm² → m²
            ("mm²", "m²"): 1e-6,
            ("cm²", "m²"): 1e-4,
            ("m²", "m²"): 1.0,

            # Volume: mm³ → m³
            ("mm³", "m³"): 1e-9,
            ("cm³", "m³"): 1e-6,
            ("m³", "m³"): 1.0,

            # Mass: already in kg
            ("kg", "kg"): 1.0,
            ("g", "kg"): 0.001,

            # Density: kg/mm³ → kg/m³
            ("kg/mm³", "kg/m³"): 1e9,
            ("kg/cm³", "kg/m³"): 1e6,
            ("kg/m³", "kg/m³"): 1.0,

            # Angle: already in rad
            ("rad", "rad"): 1.0,
            ("deg", "rad"): 3.14159265359 / 180.0,

            # Velocity: mm/s → m/s
            ("mm/s", "m/s"): 0.001,
            ("m/s", "m/s"): 1.0,

            # Acceleration: mm/s² → m/s²
            ("mm/s²", "m/s²"): 0.001,
            ("m/s²", "m/s²"): 1.0,

            # Volume flow rate: mm³/s → m³/s
            ("mm³/s", "m³/s"): 1e-9,
            ("m³/s", "m³/s"): 1.0,

            # Pressure: Pa (same)
            ("Pa", "Pa"): 1.0,
            ("kPa", "Pa"): 1000.0,
            ("MPa", "Pa"): 1e6,

            # Other units (same base units)
            ("N", "N"): 1.0,
            ("J", "J"): 1.0,
            ("W", "W"): 1.0,
            ("s", "s"): 1.0,
            ("Hz", "Hz"): 1.0,
            ("K", "K"): 1.0,
            ("A", "A"): 1.0,
            ("V", "V"): 1.0,
            ("1", "1"): 1.0,
        }

        return conversion_factors.get((freecad_unit, calcslive_unit), 1.0)

    @classmethod
    def get_property_info(cls, property_type):
        """
        Get information about a specific property type
        """
        return cls.KNOWN_PROPERTY_TYPES.get(property_type, {})

    @classmethod
    def is_quantity_type(cls, property_type):
        """
        Check if a property type represents a physical quantity (has units)
        """
        info = cls.get_property_info(property_type)
        return info.get("base_unit") is not None

    @classmethod
    def get_json_output(cls):
        """
        Get JSON output for integration with FC_CL_Bridge
        """
        return {
            "freecad_version": App.Version(),
            "quantity_types": cls.get_all_quantity_types(),
            "base_unit_mappings": cls.get_base_unit_mappings(),
            "timestamp": App.ConfigGet("BuildRevisionDate")
        }

# Convenience function for FC_CL_Bridge integration
def get_quantity_types_data():
    """
    Main function to get quantity types data for FC_CL_Bridge
    """
    return QuantityTypesExtractor.get_json_output()

# Test function
if __name__ == "__main__":
    import json
    data = get_quantity_types_data()
    print(json.dumps(data, indent=2))