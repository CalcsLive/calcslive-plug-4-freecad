"""
Parameter Mapper for FreeCAD ↔ CalcsLive Integration

CalcsLive-Centric Mapping Approach:
1. CalcsLive article defines the calculation interface (r, h, V, etc.)
2. FreeCAD parameters map to CalcsLive PQ symbols via configuration
3. Mapping stored per project/model for reusability

Example Workflow:
- CalcsLive: "r = 30 mm, h = 76 mm, V = π * r² * h"
- Mapping: {"r": "Cylinder_Radius", "h": "Cylinder_Height"}
- FreeCAD: Cylinder_Radius = 50.8 mm → CalcsLive: r = 50.8 mm
"""

import FreeCAD
import json
import os


class ParameterMapper:
    """
    Manages parameter mapping between FreeCAD descriptive names
    and CalcsLive PQ symbols based on CalcsLive article structure
    """

    def __init__(self, model_path=None):
        """
        Initialize parameter mapper for a specific FreeCAD model

        Args:
            model_path: Path to FreeCAD model file (for storing mappings)
        """
        self.model_path = model_path
        self.mapping_config = None
        self.load_mapping_config()

    def load_mapping_config(self):
        """Load parameter mapping configuration for current model"""
        if not self.model_path:
            # Default configuration for testing
            self.mapping_config = {
                "article_id": "demo-cylinder-volume",
                "mapping": {
                    "r": "Cylinder_Radius",
                    "h": "Cylinder_Height",
                    "V": None  # Output only
                }
            }
            return

        # Try to load model-specific mapping file
        config_path = self._get_config_path()
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    self.mapping_config = json.load(f)
                FreeCAD.Console.PrintMessage(f"Loaded parameter mapping from {config_path}\n")
            except Exception as e:
                FreeCAD.Console.PrintWarning(f"Failed to load mapping config: {e}\n")
                self._create_default_config()
        else:
            self._create_default_config()

    def save_mapping_config(self):
        """Save current mapping configuration to file"""
        if not self.model_path or not self.mapping_config:
            return False

        config_path = self._get_config_path()
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(config_path), exist_ok=True)

            with open(config_path, 'w') as f:
                json.dump(self.mapping_config, f, indent=2)

            FreeCAD.Console.PrintMessage(f"Saved parameter mapping to {config_path}\n")
            return True
        except Exception as e:
            FreeCAD.Console.PrintError(f"Failed to save mapping config: {e}\n")
            return False

    def _get_config_path(self):
        """Get path for mapping configuration file"""
        if not self.model_path:
            return None

        # Store mapping config alongside the FreeCAD model
        model_dir = os.path.dirname(self.model_path)
        model_name = os.path.splitext(os.path.basename(self.model_path))[0]
        return os.path.join(model_dir, f"{model_name}_calcslive_mapping.json")

    def _create_default_config(self):
        """Create default mapping configuration"""
        self.mapping_config = {
            "article_id": "",  # User needs to specify
            "mapping": {},     # Empty mapping to start
            "description": "Parameter mapping for CalcsLive integration",
            "created_by": "CalcsLive FreeCAD Workbench"
        }

    def set_calcslive_article(self, article_id):
        """Set the target CalcsLive article for this mapping"""
        if not self.mapping_config:
            self._create_default_config()

        self.mapping_config["article_id"] = article_id
        FreeCAD.Console.PrintMessage(f"Set CalcsLive article to: {article_id}\n")

    def add_mapping(self, calcslive_symbol, freecad_parameter):
        """
        Add or update a parameter mapping

        Args:
            calcslive_symbol: PQ symbol in CalcsLive (e.g., 'r', 'h')
            freecad_parameter: FreeCAD parameter name (e.g., 'Cylinder_Radius')
        """
        if not self.mapping_config:
            self._create_default_config()

        self.mapping_config["mapping"][calcslive_symbol] = freecad_parameter
        FreeCAD.Console.PrintMessage(f"Mapped: {calcslive_symbol} ← {freecad_parameter}\n")

    def remove_mapping(self, calcslive_symbol):
        """Remove a parameter mapping"""
        if self.mapping_config and calcslive_symbol in self.mapping_config["mapping"]:
            del self.mapping_config["mapping"][calcslive_symbol]
            FreeCAD.Console.PrintMessage(f"Removed mapping for: {calcslive_symbol}\n")

    def get_calcslive_inputs(self, freecad_parameters):
        """
        Convert FreeCAD parameters to CalcsLive input format using mapping

        Args:
            freecad_parameters: List of FreeCAD parameter dictionaries

        Returns:
            Dictionary in CalcsLive n8n API format
        """
        if not self.mapping_config or not self.mapping_config.get("mapping"):
            FreeCAD.Console.PrintWarning("No parameter mapping configured\n")
            return {}

        inputs = {}
        mapping = self.mapping_config["mapping"]

        # Create lookup dictionary: FreeCAD param name → parameter data
        freecad_lookup = {param["symbol"]: param for param in freecad_parameters}

        # Map CalcsLive symbols to FreeCAD values
        for calcslive_symbol, freecad_param_name in mapping.items():
            if freecad_param_name is None:
                continue  # Skip output-only parameters

            if freecad_param_name in freecad_lookup:
                param_data = freecad_lookup[freecad_param_name]
                inputs[calcslive_symbol] = {
                    "value": param_data["value"],
                    "unit": param_data["calcslive_unit"]
                }
                FreeCAD.Console.PrintMessage(f"Mapped: {calcslive_symbol} = {param_data['value']} {param_data['calcslive_unit']}\n")
            else:
                FreeCAD.Console.PrintWarning(f"FreeCAD parameter '{freecad_param_name}' not found for CalcsLive symbol '{calcslive_symbol}'\n")

        return inputs

    def get_mapping_summary(self):
        """Get human-readable summary of current mapping"""
        if not self.mapping_config:
            return "No mapping configuration loaded"

        article_id = self.mapping_config.get("article_id", "Not specified")
        mapping = self.mapping_config.get("mapping", {})

        summary = [
            f"CalcsLive Article: {article_id}",
            f"Parameter Mappings: {len(mapping)}",
            ""
        ]

        for calcslive_symbol, freecad_param in mapping.items():
            if freecad_param is None:
                summary.append(f"  {calcslive_symbol}: (output only)")
            else:
                summary.append(f"  {calcslive_symbol}: ← {freecad_param}")

        return "\n".join(summary)

    def update_freecad_from_calcslive(self, calcslive_results, target_object):
        """
        Update FreeCAD model with results from CalcsLive

        Args:
            calcslive_results: Dictionary of CalcsLive calculation results
            target_object: FreeCAD object to update
        """
        if not self.mapping_config:
            return

        from core.UnitMapper import UnitMapper
        mapping = self.mapping_config["mapping"]

        for calcslive_symbol, freecad_param_name in mapping.items():
            if calcslive_symbol in calcslive_results and freecad_param_name:
                result_data = calcslive_results[calcslive_symbol]

                # Convert to FreeCAD internal units
                converted_value, freecad_unit = UnitMapper.calcslive_to_freecad_internal(
                    result_data["value"],
                    result_data["unit"]
                )

                # Add as custom property to FreeCAD object
                prop_name = f"CalcsLive_{calcslive_symbol}"
                description = f"From CalcsLive: {freecad_param_name}"

                if not hasattr(target_object, prop_name):
                    target_object.addProperty("App::PropertyFloat", prop_name, "CalcsLive Results", description)

                setattr(target_object, prop_name, converted_value)
                FreeCAD.Console.PrintMessage(f"Updated: {prop_name} = {converted_value} {freecad_unit}\n")


# Helper function for easy access
def create_parameter_mapper(model_path=None):
    """Factory function to create ParameterMapper instance"""
    return ParameterMapper(model_path)