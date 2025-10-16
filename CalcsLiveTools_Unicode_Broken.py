"""
CalcsLive Tools Module

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
            "✓ CalcsLive Workbench is working!\n\n"
            "Available commands:\n"
            "• Connect to CalcsLive (Ctrl+Shift+C)\n"
            "• Open Dashboard (Ctrl+Shift+D)\n"
            "• Show Status (Ctrl+Shift+I)\n\n"
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
        return FreeCAD.ActiveDocument is not None

    def Activated(self):
        try:
            article_id = "demo-article"
            url = f"http://localhost:3000/freecad/{article_id}/dashboard"
            webbrowser.open(url)
            FreeCAD.Console.PrintMessage(f"CalcsLive: Opened dashboard {url}\n")
        except Exception as e:
            FreeCAD.Console.PrintError(f"CalcsLive Dashboard failed: {e}\n")


# Register commands when module is imported (following FreeCAD pattern)
def register_commands():
    """Register CalcsLive commands with FreeCAD"""
    print("CalcsLiveTools: Registering commands...")

    FreeCADGui.addCommand('CalcsLive_Connect', CalcsLiveConnect())
    FreeCADGui.addCommand('CalcsLive_Status', CalcsLiveStatus())
    FreeCADGui.addCommand('CalcsLive_Dashboard', CalcsLiveDashboard())

    print("CalcsLiveTools: Commands registered successfully!")


def get_calcslive_commands():
    """Return list of CalcsLive command names (following FreeCAD pattern)"""
    return [
        'CalcsLive_Connect',
        'CalcsLive_Dashboard',
        'CalcsLive_Status'
    ]


# Auto-register commands when module is imported (FreeCAD pattern)
if __name__ != "__main__":
    # Only register when imported, not when run directly
    try:
        register_commands()
    except Exception as e:
        print(f"CalcsLiveTools: Failed to register commands: {e}")
        FreeCAD.Console.PrintError(f"CalcsLive command registration failed: {e}\n")