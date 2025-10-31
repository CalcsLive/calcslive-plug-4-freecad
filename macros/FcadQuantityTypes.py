# FcadQuantityTypes.py
#
# Clean FreeCAD Quantity Types for CalcsLive Integration
#
# DESIGN PHILOSOPHY:
# ==================
# The intent of CalcsLive-FreeCAD integration is to leverage the strengths of both platforms:
# - CalcsLive: Powerful, versatile calculation engine with comprehensive unit support
# - FreeCAD: Robust 3D modeling and parametric design capabilities
#
# FOCUS ON WELL-IMPLEMENTED TYPES:
# =================================
# FreeCAD has inconsistent implementation of quantity property types. Some have clean,
# simple base units (e.g., "mm", "kg", "Pa"), while others have complex formats like:
# "Unit: A (0,0,0,1,0,0,0,0) [ElectricCurrent]"
#
# For our plug-in purpose, we focus ONLY on the well-implemented quantity types with
# clean base units. This covers the most frequently used engineering quantities and
# provides a reliable foundation for FreeCAD ↔ CalcsLive data exchange.
#
# CALCULATION STRATEGY:
# =====================
# - Use CalcsLive for complex calculations (it has 75+ unit categories, Greek letters,
#   expression parsing, dependency graphs, etc.)
# - Use FreeCAD for 3D modeling and parametric geometry
# - Pass sizing results from CalcsLive calculations to update FreeCAD model parameters
#
# This approach eliminates dependence on FreeCAD's incomplete quantity implementations
# while maximizing the strengths of both platforms.

import FreeCAD as App
import json
from QuantityTypesHelper import QuantityTypesExtractor

def get_clean_quantity_types():
    """
    Get clean FreeCAD quantity types for CalcsLive integration

    Returns only quantity types with:
    - Simple, clean base unit formats (e.g., "mm", "kg", "Pa")
    - Reliable CalcsLive category mapping
    - Frequent usage in engineering applications

    Excludes problematic types with complex unit formats that would
    complicate the integration without significant benefit.
    """
    try:
        # Get all quantity types from helper
        extractor = QuantityTypesExtractor()
        all_types = extractor.get_all_quantity_types()

        # Filter criteria for "clean" quantity types
        clean_types = {}

        for prop_type, info in all_types.items():
            base_unit = info.get("base_unit")
            calcslive_category = info.get("calcslive_category")

            # Include only if:
            # 1. Has a base unit defined
            # 2. Base unit is simple format (not complex "Unit: ..." format)
            # 3. Has CalcsLive category mapping
            # 4. Base unit length is reasonable (excludes complex formats)
            if (base_unit and
                calcslive_category and
                not base_unit.startswith("Unit:") and
                len(base_unit) < 20):  # Simple heuristic for clean units

                clean_types[prop_type] = {
                    "freecad_base_unit": base_unit,
                    "calcslive_category": calcslive_category,
                    "category": info.get("category"),
                    "description": f"FreeCAD {info.get('category', 'quantity')} property"
                }

        # Group by FreeCAD base unit for easier conversion processing
        base_units_summary = {}
        for prop_type, info in clean_types.items():
            freecad_unit = info["freecad_base_unit"]
            if freecad_unit not in base_units_summary:
                base_units_summary[freecad_unit] = {
                    "freecad_base_unit": freecad_unit,
                    "calcslive_category": info["calcslive_category"],
                    "property_types": [],
                    "usage_examples": []
                }
            base_units_summary[freecad_unit]["property_types"].append(prop_type)

        # Add usage examples for common base units
        usage_examples = {
            "mm": ["diameter", "height", "thickness", "clearance"],
            "mm²": ["cross_section", "surface_area", "face_area"],
            "mm³": ["part_volume", "material_volume", "cavity_volume"],
            "kg": ["part_mass", "total_weight", "material_mass"],
            "kg/mm³": ["material_density", "bulk_density"],
            
            "rad": ["rotation_angle", "taper_angle", "bend_angle"],
            "N": ["applied_force", "reaction_force", "load"],
            "Pa": ["pressure", "stress", "yield_strength"],
            "mm/s": ["cutting_speed", "feed_rate", "velocity"],
            "mm/s²": ["acceleration", "deceleration"],
            
            "mm³/s": ["flow_rate", "pump_capacity"],
            "W": ["motor_power", "heat_generation"],
            "s": ["cycle_time", "operation_time"],
            "Hz": ["rotation_frequency", "vibration_frequency"],
            "K": ["operating_temperature", "ambient_temperature"],
            "J": ["energy", "work_done"]
        }

        for freecad_unit, summary in base_units_summary.items():
            if freecad_unit in usage_examples:
                summary["usage_examples"] = usage_examples[freecad_unit]

        return {
            "success": True,
            "freecad_version": App.Version(),
            "clean_quantity_types": clean_types,
            "base_units_summary": base_units_summary,
            "stats": {
                "total_clean_types": len(clean_types),
                "unique_base_units": len(base_units_summary),
                "excluded_complex_types": len(all_types) - len(clean_types)
            },
            "integration_notes": {
                "purpose": "Focus on well-implemented FreeCAD quantity types for reliable CalcsLive integration",
                "conversion_strategy": "Use CalcsLive unit conversion system to convert from freecad_base_unit",
                "excluded_reason": "Complex unit formats excluded to maintain integration reliability",
                "calculation_approach": "Use CalcsLive for calculations, FreeCAD for modeling"
            }
        }

    except Exception as e:
        return {
            "success": False,
            "error": "Failed to get clean quantity types",
            "details": str(e)
        }

def handle_quantity_types_request():
    """
    Handle GET /calcslive/quantity-types request for FC_CL_Bridge

    This endpoint provides clean FreeCAD quantity types that can be reliably
    integrated with CalcsLive's calculation system.
    """
    data = get_clean_quantity_types()
    return json.dumps(data, indent=2)

# INTEGRATION INSTRUCTIONS FOR FC_CL_BRIDGE:
# ===========================================
#
# Add this endpoint to FC_CL_Bridge.FCMacro request handler:
#
# elif path == '/calcslive/quantity-types' and method == 'GET':
#     response_body = handle_quantity_types_request()
#     self.send_response(200)
#     self.send_header('Content-type', 'application/json')
#     self.send_header('Access-Control-Allow-Origin', '*')
#     self.end_headers()
#     self.wfile.write(response_body.encode('utf-8'))
#
# USAGE FROM CALCSLIVE:
# =====================
#
# CalcsLive can fetch this data via:
# fetch('http://127.0.0.1:8787/calcslive/quantity-types')
#
# Then use CalcsLive's own unit conversion system to convert from
# freecad_base_unit to CalcsLive base units for seamless integration.

# Test function for development
if __name__ == "__main__":
    data = get_clean_quantity_types()
    print("=== CLEAN FREECAD QUANTITY TYPES ===")
    print(json.dumps(data, indent=2))