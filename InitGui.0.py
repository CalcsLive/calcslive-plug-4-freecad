"""
Working CalcsLive FreeCAD Workbench

This version defines everything in the correct order and should work immediately.
"""

import FreeCAD
import FreeCADGui
import webbrowser


def create_connect_command():
    """Factory function to create ConnectCommand"""

    class ConnectCommand:
        def GetResources(self):
            return {
                'MenuText': 'Connect to CalcsLive',
                'ToolTip': 'Open CalcsLive connection page',
                'Pixmap': '',  # No icon for now
                'Accel': 'Ctrl+Shift+C'
            }

        def IsActive(self):
            return True

        def Activated(self):
            try:
                # Development server URL
                url = "http://localhost:3000/freecad/connect"
                webbrowser.open(url)
                FreeCAD.Console.PrintMessage(f"CalcsLive: Opened {url}\n")
            except Exception as e:
                FreeCAD.Console.PrintError(f"CalcsLive Connect failed: {e}\n")

    return ConnectCommand()


def create_status_command():
    """Factory function to create StatusCommand"""

    class StatusCommand:
        def GetResources(self):
            return {
                'MenuText': 'Show Status',
                'ToolTip': 'Show CalcsLive workbench status',
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
                "• Show Status (Ctrl+Shift+I)\n\n"
                "Next steps:\n"
                "1. Use Connect to open CalcsLive interface\n"
                "2. Create a FreeCAD model with parameters\n"
                "3. Test bi-directional sync"
            )

            FreeCAD.Console.PrintMessage(f"CalcsLive Status:\n{message}")

            try:
                from PySide2 import QtWidgets
                QtWidgets.QMessageBox.information(
                    None,
                    "CalcsLive Status",
                    message
                )
            except ImportError:
                FreeCAD.Console.PrintMessage("Status dialog not available - check console output\n")

    return StatusCommand()


def create_dashboard_command():
    """Factory function to create DashboardCommand"""

    class DashboardCommand:
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
                # For now, use a placeholder article ID
                article_id = "demo-article"
                url = f"http://localhost:3000/freecad/{article_id}/dashboard"
                webbrowser.open(url)
                FreeCAD.Console.PrintMessage(f"CalcsLive: Opened dashboard {url}\n")
            except Exception as e:
                FreeCAD.Console.PrintError(f"CalcsLive Dashboard failed: {e}\n")

    return DashboardCommand()


class CalcsLiveWorkbench(FreeCADGui.Workbench):
    """CalcsLive FreeCAD Workbench - Working Version"""

    def __init__(self):
        self.__class__.MenuText = "CalcsLive"
        self.__class__.ToolTip = "CalcsLive Integration - Working Version"

    def Initialize(self):
        """Initialize workbench commands"""
        print("CalcsLive Workbench: Initializing working version...")

        try:
            # Create and register commands using factory functions
            connect_cmd = create_connect_command()
            status_cmd = create_status_command()
            dashboard_cmd = create_dashboard_command()

            FreeCADGui.addCommand('CalcsLive_Connect', connect_cmd)
            FreeCADGui.addCommand('CalcsLive_Status', status_cmd)
            FreeCADGui.addCommand('CalcsLive_Dashboard', dashboard_cmd)

            # Define toolbar and menu
            self.list = [
                "CalcsLive_Connect",
                "CalcsLive_Dashboard",
                "Separator",
                "CalcsLive_Status"
            ]

            print("CalcsLive Workbench: Working version commands registered successfully!")
            FreeCAD.Console.PrintMessage("CalcsLive Workbench: Ready to use!\n")

        except Exception as e:
            print(f"CalcsLive Workbench: Error in working version: {e}")
            self.list = []

    def Activated(self):
        """Called when workbench is activated"""
        print("CalcsLive Workbench: Working version activated")
        FreeCAD.Console.PrintMessage(
            "CalcsLive Workbench activated!\n"
            "• Connect to CalcsLive: Opens browser to localhost:3000\n"
            "• Show Status: Display workbench information\n"
            "• Open Dashboard: Access parameter mapping interface\n"
        )

    def Deactivated(self):
        """Called when workbench is deactivated"""
        print("CalcsLive Workbench: Working version deactivated")

    def GetClassName(self):
        """Return workbench class name"""
        return "Gui::PythonWorkbench"


# Register the workbench
FreeCADGui.addWorkbench(CalcsLiveWorkbench())