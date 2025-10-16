"""
CalcsLive Tools Module - Clean ASCII Version

Contains command definitions following FreeCAD official pattern.
This module is imported by InitGui.py and commands are registered here.
"""

import FreeCAD
import FreeCADGui
import webbrowser


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

            # Extract parameters from all objects
            parameters = []
            for obj in doc.Objects:
                FreeCAD.Console.PrintMessage(f"  Checking object: {obj.Name} ({obj.TypeId})\n")

                # Check for dimensional properties
                for prop_name in obj.PropertiesList:
                    prop = getattr(obj, prop_name)

                    # Look for dimensional properties (Length, Distance, etc.)
                    if hasattr(prop, 'Value') and hasattr(prop, 'Unit'):
                        param_info = {
                            'object': obj.Name,
                            'property': prop_name,
                            'value': prop.Value,
                            'unit': str(prop.Unit),
                            'label': obj.Label if hasattr(obj, 'Label') else obj.Name
                        }
                        parameters.append(param_info)
                        FreeCAD.Console.PrintMessage(
                            f"    Found parameter: {prop_name} = {prop.Value} {prop.Unit}\n"
                        )

            # Display results
            if parameters:
                message = f"Found {len(parameters)} dimensional parameters:\n\n"
                for p in parameters:
                    message += f"• {p['object']}.{p['property']}: {p['value']} {p['unit']}\n"

                FreeCAD.Console.PrintMessage(f"CalcsLive Parameter Extraction:\n{message}\n")

                try:
                    from PySide2 import QtWidgets
                    QtWidgets.QMessageBox.information(None, "CalcsLive Parameters", message)
                except ImportError:
                    FreeCAD.Console.PrintMessage("Dialog not available - check console output\n")
            else:
                message = "No dimensional parameters found in active document"
                FreeCAD.Console.PrintMessage(f"CalcsLive: {message}\n")

                try:
                    from PySide2 import QtWidgets
                    QtWidgets.QMessageBox.information(None, "CalcsLive Parameters", message)
                except ImportError:
                    pass

        except Exception as e:
            FreeCAD.Console.PrintError(f"CalcsLive Parameter extraction failed: {e}\n")


# Register commands when module is imported
def register_commands():
    """Register CalcsLive commands with FreeCAD"""
    print("CalcsLiveTools: Registering commands...")

    FreeCADGui.addCommand('CalcsLive_Connect', CalcsLiveConnect())
    FreeCADGui.addCommand('CalcsLive_Status', CalcsLiveStatus())
    FreeCADGui.addCommand('CalcsLive_Dashboard', CalcsLiveDashboard())
    FreeCADGui.addCommand('CalcsLive_ExtractParams', CalcsLiveExtractParams())

    print("CalcsLiveTools: Commands registered successfully!")


def get_calcslive_commands():
    """Return list of CalcsLive command names"""
    return [
        'CalcsLive_Connect',
        'CalcsLive_Dashboard',
        'CalcsLive_ExtractParams',
        'CalcsLive_Status'
    ]


# Auto-register commands when module is imported
if __name__ != "__main__":
    try:
        register_commands()
    except Exception as e:
        print(f"CalcsLiveTools: Failed to register commands: {e}")
        FreeCAD.Console.PrintError(f"CalcsLive command registration failed: {e}\n")