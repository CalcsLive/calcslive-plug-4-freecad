"""
CalcsLive Tools Module - Clean ASCII Version

Contains command definitions following FreeCAD official pattern.
This module is imported by InitGui.py and commands are registered here.
"""

import FreeCAD
import FreeCADGui
import webbrowser
import sys
import os
import urllib.request
import urllib.parse
import urllib.error
import json

# Add workbench path to Python path for core module imports
workbench_path = os.path.dirname(__file__)
if workbench_path not in sys.path:
    sys.path.append(workbench_path)

# Global imports for core modules
try:
    from core.UnitMapper import UnitMapper
    from core.ParameterMapper import create_parameter_mapper
    FreeCAD.Console.PrintMessage("CalcsLive: Core modules imported successfully\n")
except ImportError as e:
    FreeCAD.Console.PrintError(f"CalcsLive: Failed to import core modules: {e}\n")


# Command classes (proven working patterns)
class CalcsLiveConnect:
    """Connect to CalcsLive development server"""

    def GetResources(self):
        return {
            'MenuText': 'Connect to CalcsLive',
            'ToolTip': 'Open CalcsLive connection page in browser',
            'Pixmap': '',
            'Accel': 'Ctrl+Shift+C'
        }

    def IsActive(self):
        return True

    def Activated(self):
        try:
            url = "http://localhost:3000/freecad/connect"
            webbrowser.open(url)
            FreeCAD.Console.PrintMessage(f"CalcsLive: Opened {url}\n")
        except Exception as e:
            FreeCAD.Console.PrintError(f"CalcsLive Connect failed: {e}\n")


class CalcsLiveStatus:
    """Show CalcsLive workbench status"""

    def GetResources(self):
        return {
            'MenuText': 'Show Status',
            'ToolTip': 'Show CalcsLive workbench status and information',
            'Pixmap': '',
            'Accel': 'Ctrl+Shift+I'
        }

    def IsActive(self):
        return True

    def Activated(self):
        message = (
            "CalcsLive Workbench is working!\n\n"
            "Available commands:\n"
            "Connect to CalcsLive (Ctrl+Shift+C)\n"
            "Open Dashboard (Ctrl+Shift+D)\n"
            "Show Status (Ctrl+Shift+I)\n\n"
            "Development server: http://localhost:3000"
        )

        FreeCAD.Console.PrintMessage(f"CalcsLive Status:\n{message}\n")

        try:
            from PySide2 import QtWidgets
            QtWidgets.QMessageBox.information(None, "CalcsLive Status", message)
        except ImportError:
            FreeCAD.Console.PrintMessage("Status dialog not available - check console\n")


class CalcsLiveDashboard:
    """Open CalcsLive parameter mapping dashboard"""

    def GetResources(self):
        return {
            'MenuText': 'Open Dashboard',
            'ToolTip': 'Open CalcsLive parameter mapping dashboard',
            'Pixmap': '',
            'Accel': 'Ctrl+Shift+D'
        }

    def IsActive(self):
        return True

    def Activated(self):
        try:
            article_id = "demo-article"
            url = f"http://localhost:3000/freecad/{article_id}/dashboard"
            webbrowser.open(url)
            FreeCAD.Console.PrintMessage(f"CalcsLive: Opened dashboard {url}\n")
        except Exception as e:
            FreeCAD.Console.PrintError(f"CalcsLive Dashboard failed: {e}\n")


class CalcsLiveExtractParams:

    def extract_unit_symbol(self, unit_obj):
        """Extract clean unit symbol from FreeCAD Unit object"""
        try:
            # Get the unit's signature and try to extract symbol
            unit_str = str(unit_obj)

            # Parse common FreeCAD unit patterns
            if 'Unit: mm' in unit_str and 'Length' in unit_str:
                return 'mm'
            elif 'Unit: deg' in unit_str and 'Angle' in unit_str:
                return 'deg'
            elif 'Unit: m' in unit_str and 'Length' in unit_str:
                return 'm'
            elif 'Unit: cm' in unit_str and 'Length' in unit_str:
                return 'cm'
            elif 'Unit: in' in unit_str and 'Length' in unit_str:
                return 'in'
            elif 'Unit: ft' in unit_str and 'Length' in unit_str:
                return 'ft'
            else:
                # Fallback: try to extract from getUserPreferred()
                if hasattr(unit_obj, 'getUserPreferred'):
                    return unit_obj.getUserPreferred()[2]  # Get unit string
                else:
                    # Last resort: return simplified string
                    return unit_str.split()[1] if len(unit_str.split()) > 1 else 'unknown'
        except Exception as e:
            FreeCAD.Console.PrintWarning(f"Unit extraction failed: {e}, using 'unknown'\n")
            return 'unknown'

    """Extract and display parameters from active FreeCAD model"""

    def GetResources(self):
        return {
            'MenuText': 'Extract Parameters',
            'ToolTip': 'Extract dimensional parameters from active FreeCAD model',
            'Pixmap': '',
            'Accel': 'Ctrl+Shift+E'
        }

    def IsActive(self):
        return FreeCAD.ActiveDocument is not None

    def Activated(self):
        try:
            doc = FreeCAD.ActiveDocument
            if not doc:
                FreeCAD.Console.PrintError("No active document\n")
                return

            FreeCAD.Console.PrintMessage(f"CalcsLive: Extracting parameters from {doc.Name}\n")

            # UnitMapper already imported globally

            # Extract parameters from all objects
            parameters = []
            for obj in doc.Objects:
                FreeCAD.Console.PrintMessage(f"  Checking object: {obj.Name} ({obj.TypeId})\n")

                # Check for dimensional properties
                for prop_name in obj.PropertiesList:
                    prop = getattr(obj, prop_name)

                    # Look for dimensional properties (Length, Distance, etc.)
                    if hasattr(prop, 'Value') and hasattr(prop, 'Unit'):
                        # Extract unit symbol from FreeCAD Unit object
                        freecad_unit = self.extract_unit_symbol(prop.Unit)
                        calcslive_unit = UnitMapper.freecad_to_calcslive_direct(freecad_unit)

                        param_info = {
                            'object': obj.Name,
                            'property': prop_name,
                            'value': prop.Value,
                            'unit': freecad_unit,
                            'calcslive_unit': calcslive_unit,
                            'unit_mapped': (freecad_unit != calcslive_unit),
                            'label': obj.Label if hasattr(obj, 'Label') else obj.Name,
                            'symbol': self.generate_symbol(prop_name, obj.Name)
                        }
                        parameters.append(param_info)

                        # Enhanced logging with unit mapping info
                        mapping_info = f" → {calcslive_unit}" if param_info['unit_mapped'] else ""
                        FreeCAD.Console.PrintMessage(
                            f"    Found parameter: {prop_name} = {prop.Value} {freecad_unit}{mapping_info}\n"
                        )

            # Apply unit mapping to all parameters
            mapped_parameters = UnitMapper.map_parameter_units(parameters)

            # Display results with unit mapping
            if mapped_parameters:
                message = f"Found {len(mapped_parameters)} dimensional parameters with CalcsLive mapping:\n\n"

                for p in mapped_parameters:
                    unit_display = f"{p['unit']}"
                    if p['unit_mapped']:
                        unit_display += f" → {p['calcslive_unit']}"

                    message += f"• {p['symbol']}: {p['value']} {unit_display}\n"
                    message += f"  ({p['object']}.{p['property']})\n\n"

                FreeCAD.Console.PrintMessage(f"CalcsLive Parameter Extraction:\n{message}\n")

                # Store parameters for potential sync operations
                self.last_extracted_parameters = mapped_parameters

                try:
                    from PySide2 import QtWidgets
                    enhanced_message = message + f"\nUnit Mapping Summary:\n"
                    mapped_count = sum(1 for p in mapped_parameters if p['unit_mapped'])
                    enhanced_message += f"• {len(mapped_parameters)} total parameters\n"
                    enhanced_message += f"• {mapped_count} unit mappings applied\n"
                    enhanced_message += f"• Ready for CalcsLive sync\n"

                    QtWidgets.QMessageBox.information(None, "CalcsLive Parameters", enhanced_message)
                except ImportError:
                    FreeCAD.Console.PrintMessage("Dialog not available - check console output\n")
            else:
                message = "No dimensional parameters found in active document"
                FreeCAD.Console.PrintMessage(f"CalcsLive: {message}\n")
                self.last_extracted_parameters = []

                try:
                    from PySide2 import QtWidgets
                    QtWidgets.QMessageBox.information(None, "CalcsLive Parameters", message)
                except ImportError:
                    pass

        except Exception as e:
            FreeCAD.Console.PrintError(f"CalcsLive Parameter extraction failed: {e}\n")
            self.last_extracted_parameters = []

    def generate_symbol(self, prop_name: str, obj_name: str) -> str:
        """
        Generate object-based descriptive symbol for FreeCAD parameters

        Args:
            prop_name: FreeCAD property name (e.g., 'Radius', 'Height')
            obj_name: FreeCAD object name (e.g., 'Cylinder', 'Box001')

        Returns:
            Descriptive symbol (e.g., 'Cylinder_Radius', 'Box001_Height')
        """
        # Create descriptive object-based symbol
        # Format: ObjectName_PropertyName
        # Examples: Cylinder_Radius, Box001_Height, Sketch_Length
        return f"{obj_name}_{prop_name}"


class CalcsLiveSyncToCalcsLive:
    """Sync extracted FreeCAD parameters to CalcsLive calculation"""

    def extract_unit_symbol(self, unit_obj):
        """Extract clean unit symbol from FreeCAD Unit object"""
        try:
            # Get the unit's signature and try to extract symbol
            unit_str = str(unit_obj)

            # Parse common FreeCAD unit patterns
            if 'Unit: mm' in unit_str and 'Length' in unit_str:
                return 'mm'
            elif 'Unit: deg' in unit_str and 'Angle' in unit_str:
                return 'deg'
            elif 'Unit: m' in unit_str and 'Length' in unit_str:
                return 'm'
            elif 'Unit: cm' in unit_str and 'Length' in unit_str:
                return 'cm'
            elif 'Unit: in' in unit_str and 'Length' in unit_str:
                return 'in'
            elif 'Unit: ft' in unit_str and 'Length' in unit_str:
                return 'ft'
            else:
                # Fallback: try to extract from getUserPreferred()
                if hasattr(unit_obj, 'getUserPreferred'):
                    return unit_obj.getUserPreferred()[2]  # Get unit string
                else:
                    # Last resort: return simplified string
                    return unit_str.split()[1] if len(unit_str.split()) > 1 else 'unknown'
        except Exception as e:
            FreeCAD.Console.PrintWarning(f"Unit extraction failed: {e}, using 'unknown'\n")
            return 'unknown'

    def GetResources(self):
        return {
            'MenuText': 'Sync to CalcsLive',
            'ToolTip': 'Send FreeCAD parameters to CalcsLive calculation using n8n API',
            'Pixmap': '',
            'Accel': 'Ctrl+Shift+S'
        }

    def IsActive(self):
        return FreeCAD.ActiveDocument is not None

    def Activated(self):
        try:
            # urllib and json already imported globally

            doc = FreeCAD.ActiveDocument
            if not doc:
                FreeCAD.Console.PrintError("No active document\n")
                return

            FreeCAD.Console.PrintMessage(f"CalcsLive: Syncing parameters from {doc.Name}\n")

            # First extract parameters with unit mapping
            parameters = self.extract_and_map_parameters(doc)

            if not parameters:
                FreeCAD.Console.PrintError("No parameters to sync. Run 'Extract Parameters' first.\n")
                return

            # Prepare data for n8n API (following existing pattern)
            api_data = self.prepare_api_data(doc, parameters)

            # Send to CalcsLive via n8n API
            response = self.send_to_calcslive(api_data)

            if response:
                self.handle_sync_success(response, parameters)
            else:
                self.handle_sync_failure()

        except Exception as e:
            FreeCAD.Console.PrintError(f"[CalcsLiveTools]CalcsLive sync failed: {e}\n")

    def extract_and_map_parameters(self, doc):
        """Extract parameters from FreeCAD model with unit mapping"""
        parameters = []

        for obj in doc.Objects:
            for prop_name in obj.PropertiesList:
                prop = getattr(obj, prop_name)

                if hasattr(prop, 'Value') and hasattr(prop, 'Unit'):
                    freecad_unit = self.extract_unit_symbol(prop.Unit)
                    calcslive_unit = UnitMapper.freecad_to_calcslive_direct(freecad_unit)

                    param_info = {
                        'object': obj.Name,
                        'property': prop_name,
                        'value': prop.Value,
                        'unit': freecad_unit,
                        'calcslive_unit': calcslive_unit,
                        'symbol': self.generate_symbol(prop_name, obj.Name)
                    }
                    parameters.append(param_info)

        return parameters

    def generate_symbol(self, prop_name, obj_name):
        """Generate object-based descriptive symbol (matching ExtractParams logic)"""
        # Create descriptive object-based symbol
        # Format: ObjectName_PropertyName
        # Examples: Cylinder_Radius, Box001_Height, Sketch_Length
        return f"{obj_name}_{prop_name}"

    def prepare_api_data(self, doc, parameters):
        """Prepare data for n8n calculate API using parameter mapping"""
        # ParameterMapper already imported globally

        # Create parameter mapper for current model
        model_path = doc.FileName if hasattr(doc, 'FileName') else None
        mapper = create_parameter_mapper(model_path)

        # Get CalcsLive inputs using mapping configuration
        inputs = mapper.get_calcslive_inputs(parameters)

        if not inputs:
            FreeCAD.Console.PrintError("No parameter mappings configured or no matching parameters found\n")
            FreeCAD.Console.PrintMessage("Available FreeCAD parameters:\n")
            for param in parameters:
                FreeCAD.Console.PrintMessage(f"  - {param['symbol']}\n")
            FreeCAD.Console.PrintMessage("\nPlease configure parameter mapping first\n")
            return None

        # Get article ID from mapping configuration
        article_id = mapper.mapping_config.get("article_id", "")
        if not article_id:
            FreeCAD.Console.PrintError("No CalcsLive article ID configured\n")
            return None

        FreeCAD.Console.PrintMessage(f"\nParameter Mapping Summary:\n{mapper.get_mapping_summary()}\n\n")

        api_data = {
            'articleId': article_id,
            'apiKey': 'n8n_f26596f2e42fe6f89d285ceca528e29895302ac6dcdddc1da8b9c3a821e665f1',  # Real API key
            'inputs': inputs,
            'outputs': {
                'V': {'unit': 'mm³'}  # Request volume result in mm³
            }
        }

        return api_data

    def send_to_calcslive(self, api_data):
        """Send data to CalcsLive using n8n API"""
        try:
            # Use localhost for development
            url = "http://localhost:3000/api/n8n/v1/calculate"

            # Prepare request
            data = json.dumps(api_data).encode('utf-8')
            headers = {
                'Content-Type': 'application/json',
                'User-Agent': 'FreeCAD-CalcsLive-Workbench/1.0'
            }

            req = urllib.request.Request(url, data=data, headers=headers)

            FreeCAD.Console.PrintMessage(f"Sending request to: {url}\n")
            FreeCAD.Console.PrintMessage(f"Data: {json.dumps(api_data, indent=2)}\n")

            # Send request
            with urllib.request.urlopen(req, timeout=30) as response:
                response_data = json.loads(response.read().decode('utf-8'))
                return response_data

        except urllib.error.URLError as e:
            FreeCAD.Console.PrintError(f"Network error: {e}\n")
            return None
        except json.JSONDecodeError as e:
            FreeCAD.Console.PrintError(f"JSON error: {e}\n")
            return None
        except Exception as e:
            FreeCAD.Console.PrintError(f"Request error: {e}\n")
            return None

    def handle_sync_success(self, response, parameters):
        """Handle successful sync response"""
        FreeCAD.Console.PrintMessage("CalcsLive sync successful!\n")
        FreeCAD.Console.PrintMessage(f"Response: {json.dumps(response, indent=2)}\n")

        # Extract results from response
        results = response.get('outputs', {})

        # Display results
        message = f"Sync successful! Sent {len(parameters)} parameters:\n\n"
        for param in parameters:
            message += f"• {param['symbol']}: {param['value']} {param['calcslive_unit']}\n"

        if results:
            message += f"\nCalculation results:\n"
            for symbol, result in results.items():
                message += f"• {symbol}: {result.get('value', 'N/A')} {result.get('unit', '')}\n"

        message += f"\nOpen CalcsLive dashboard to view full calculation"

        try:
            from PySide2 import QtWidgets
            QtWidgets.QMessageBox.information(None, "CalcsLive Sync Success", message)
        except ImportError:
            FreeCAD.Console.PrintMessage(message + "\n")

        # Store results for potential pull operations
        self.last_sync_results = results

    def handle_sync_failure(self):
        """Handle sync failure"""
        message = "Failed to sync with CalcsLive. Check:\n\n"
        message += "• CalcsLive server is running (localhost:3000)\n"
        message += "• API key is configured\n"
        message += "• Network connectivity\n"
        message += "• Article exists and is accessible\n"

        try:
            from PySide2 import QtWidgets
            QtWidgets.QMessageBox.warning(None, "CalcsLive Sync Failed", message)
        except ImportError:
            FreeCAD.Console.PrintMessage(message + "\n")


class CalcsLivePullFromCalcsLive:
    """Pull calculation results from CalcsLive and update FreeCAD model"""

    def GetResources(self):
        return {
            'MenuText': 'Pull from CalcsLive',
            'ToolTip': 'Get calculation results from CalcsLive and update FreeCAD model properties',
            'Pixmap': '',
            'Accel': 'Ctrl+Shift+P'
        }

    def IsActive(self):
        return FreeCAD.ActiveDocument is not None

    def Activated(self):
        try:
            # urllib and json already imported globally

            doc = FreeCAD.ActiveDocument
            if not doc:
                FreeCAD.Console.PrintError("No active document\n")
                return

            FreeCAD.Console.PrintMessage(f"CalcsLive: Pulling results for {doc.Name}\n")

            # For MVP, we'll use a demo calculation ID
            # In future, this would come from previous sync operation
            article_id = "demo-cylinder-volume"

            # Get calculation results from CalcsLive
            results = self.get_calcslive_results(article_id)

            if results:
                self.update_freecad_model(doc, results)
            else:
                self.handle_pull_failure()

        except Exception as e:
            FreeCAD.Console.PrintError(f"CalcsLive pull failed: {e}\n")

    def get_calcslive_results(self, article_id):
        """Get calculation results from CalcsLive (mock for MVP)"""
        try:
            # For MVP, we'll return mock results
            # In production, this would call CalcsLive API to get actual results
            mock_results = {
                'V': {
                    'value': 6283.18,
                    'unit': 'mm³',
                    'symbol': 'V',
                    'description': 'Cylinder Volume'
                },
                'SA': {
                    'value': 1884.96,
                    'unit': 'mm²',
                    'symbol': 'SA',
                    'description': 'Surface Area'
                }
            }

            FreeCAD.Console.PrintMessage(f"Retrieved {len(mock_results)} calculation results\n")
            return mock_results

        except Exception as e:
            FreeCAD.Console.PrintError(f"Failed to get CalcsLive results: {e}\n")
            return None

    def update_freecad_model(self, doc, results):
        """Update FreeCAD model with calculation results"""
        try:
            # UnitMapper already imported globally

            updated_objects = []
            created_properties = []

            # Find the first object that looks like our target (cylinder, etc.)
            target_obj = None
            for obj in doc.Objects:
                if hasattr(obj, 'Shape') and len(obj.Shape.Solids) > 0:
                    target_obj = obj
                    break

            if not target_obj:
                FreeCAD.Console.PrintWarning("No suitable object found for property updates\n")
                return

            # Add calculation results as custom properties
            for symbol, result in results.items():
                calcslive_unit = result['unit']
                calcslive_value = result['value']

                # Convert CalcsLive value and unit to FreeCAD internal units
                converted_value, freecad_unit = UnitMapper.calcslive_to_freecad_internal(calcslive_value, calcslive_unit)
                value = converted_value
                description = result.get('description', f'Calculated {symbol}')

                # Create property name
                prop_name = f"Calc_{symbol}"

                try:
                    # Add custom property to the object
                    # Use App::PropertyFloat for numerical values
                    target_obj.addProperty("App::PropertyFloat", prop_name, "CalcsLive Results", description)
                    setattr(target_obj, prop_name, value)

                    created_properties.append({
                        'object': target_obj.Name,
                        'property': prop_name,
                        'value': value,
                        'unit': freecad_unit,
                        'description': description
                    })

                    FreeCAD.Console.PrintMessage(
                        f"  Added property: {target_obj.Name}.{prop_name} = {value} {freecad_unit}\n"
                    )

                except Exception as e:
                    FreeCAD.Console.PrintWarning(f"Failed to add property {prop_name}: {e}\n")

            # Recompute the document to update the model
            doc.recompute()

            # Display success message
            if created_properties:
                message = f"Successfully updated {target_obj.Name} with {len(created_properties)} calculated properties:\n\n"
                for prop in created_properties:
                    message += f"• {prop['property']}: {prop['value']} {prop['unit']}\n"
                    message += f"  {prop['description']}\n\n"

                message += "Properties added to 'CalcsLive Results' group in object properties."

                try:
                    from PySide2 import QtWidgets
                    QtWidgets.QMessageBox.information(None, "CalcsLive Pull Success", message)
                except ImportError:
                    FreeCAD.Console.PrintMessage(message + "\n")

                # Store update info for reference
                self.last_pull_results = {
                    'object': target_obj.Name,
                    'properties': created_properties,
                    'timestamp': str(FreeCAD.Console.PrintMessage(""))
                }

            else:
                FreeCAD.Console.PrintWarning("No properties were created\n")

        except Exception as e:
            FreeCAD.Console.PrintError(f"Failed to update FreeCAD model: {e}\n")

    def handle_pull_failure(self):
        """Handle pull failure"""
        message = "Failed to pull results from CalcsLive. Check:\n\n"
        message += "• Previous sync operation completed successfully\n"
        message += "• CalcsLive calculation exists and has results\n"
        message += "• Network connectivity to CalcsLive server\n"
        message += "• Calculation has been run and has output values\n"

        try:
            from PySide2 import QtWidgets
            QtWidgets.QMessageBox.warning(None, "CalcsLive Pull Failed", message)
        except ImportError:
            FreeCAD.Console.PrintMessage(message + "\n")


class CalcsLiveConfigureMapping:
    """Configure parameter mapping between FreeCAD and CalcsLive"""

    def GetResources(self):
        return {
            'MenuText': 'Configure Mapping',
            'ToolTip': 'Set up parameter mapping between FreeCAD and CalcsLive PQ symbols',
            'Pixmap': '',
            'Accel': 'Ctrl+Shift+M'
        }

    def IsActive(self):
        return True

    def Activated(self):
        try:
            self.show_mapping_configuration()
        except Exception as e:
            FreeCAD.Console.PrintError(f"CalcsLive Configure Mapping failed: {e}\n")

    def show_mapping_configuration(self):
        """Show mapping configuration interface"""
        # ParameterMapper already imported globally

        doc = FreeCAD.ActiveDocument
        if not doc:
            FreeCAD.Console.PrintError("No active document. Please open a FreeCAD model first.\n")
            return

        # Get current parameters
        extractor = CalcsLiveExtractParams()
        extractor.Activated()  # This will extract and display current parameters

        # Create parameter mapper
        model_path = doc.FileName if hasattr(doc, 'FileName') else None
        mapper = create_parameter_mapper(model_path)

        # Show current mapping summary
        FreeCAD.Console.PrintMessage(f"\n{'='*60}\n")
        FreeCAD.Console.PrintMessage("PARAMETER MAPPING CONFIGURATION\n")
        FreeCAD.Console.PrintMessage(f"{'='*60}\n")
        FreeCAD.Console.PrintMessage(f"{mapper.get_mapping_summary()}\n")
        FreeCAD.Console.PrintMessage(f"{'='*60}\n\n")

        # Show text-based configuration instructions
        self.show_configuration_instructions(mapper)

    def show_configuration_instructions(self, mapper):
        """Show instructions for text-based mapping configuration"""

        instructions = """
TEXT-BASED MAPPING CONFIGURATION:

1. Set CalcsLive Article ID:
   FreeCAD Console: mapper.set_calcslive_article("your-article-id")

2. Add Parameter Mappings:
   FreeCAD Console: mapper.add_mapping("r", "Cylinder_Radius")
   FreeCAD Console: mapper.add_mapping("h", "Cylinder_Height")

3. Save Configuration:
   FreeCAD Console: mapper.save_mapping_config()

EXAMPLE WORKFLOW:
   # Configure for cylinder volume calculation
   mapper.set_calcslive_article("cylinder-volume-demo")
   mapper.add_mapping("r", "Cylinder_Radius")
   mapper.add_mapping("h", "Cylinder_Height")
   mapper.save_mapping_config()

NOTES:
- CalcsLive PQ symbols (r, h) are defined in your CalcsLive article
- FreeCAD parameters are the object-based names shown above
- Output-only PQs (like V for volume) don't need FreeCAD mappings
- Configuration is saved per FreeCAD model

Access the mapper object in Python Console with:
>>> from core.ParameterMapper import create_parameter_mapper
>>> doc = FreeCAD.ActiveDocument
>>> mapper = create_parameter_mapper(doc.FileName if hasattr(doc, 'FileName') else None)
"""

        FreeCAD.Console.PrintMessage(instructions)


# Register commands when module is imported
def register_commands():
    """Register CalcsLive commands with FreeCAD"""
    print("CalcsLiveTools: Registering commands...")

    FreeCADGui.addCommand('CalcsLive_Connect', CalcsLiveConnect())
    FreeCADGui.addCommand('CalcsLive_Status', CalcsLiveStatus())
    FreeCADGui.addCommand('CalcsLive_Dashboard', CalcsLiveDashboard())
    FreeCADGui.addCommand('CalcsLive_ExtractParams', CalcsLiveExtractParams())
    FreeCADGui.addCommand('CalcsLive_ConfigureMapping', CalcsLiveConfigureMapping())
    FreeCADGui.addCommand('CalcsLive_SyncToCalcsLive', CalcsLiveSyncToCalcsLive())
    FreeCADGui.addCommand('CalcsLive_PullFromCalcsLive', CalcsLivePullFromCalcsLive())

    print("CalcsLiveTools: Commands registered successfully!")


def get_calcslive_commands():
    """Return list of CalcsLive command names"""
    return [
        'CalcsLive_Connect',
        'CalcsLive_Dashboard',
        'CalcsLive_ExtractParams',
        'CalcsLive_SyncToCalcsLive',
        'CalcsLive_PullFromCalcsLive',
        'CalcsLive_Status'
    ]


# Auto-register commands when module is imported
if __name__ != "__main__":
    try:
        register_commands()
    except Exception as e:
        print(f"CalcsLiveTools: Failed to register commands: {e}")
        FreeCAD.Console.PrintError(f"CalcsLive command registration failed: {e}\n")