# -*- coding: utf-8 -*-
"""
CalcsLivePlug - Auto-start addon for FreeCAD CalcsLive capability
This file is automatically loaded when FreeCAD starts and the addon is enabled.
Provides a plug interface for CalcsLive calculation capability in FreeCAD.
"""

import FreeCAD as App
import FreeCADGui as Gui
import os
import sys

print("[CalcsLivePlug] InitGui.py loaded")

class CalcsLivePlugWorkbench(Gui.Workbench):
    """
    CalcsLive Plug workbench for FreeCAD.
    Provides plug interface for CalcsLive calculation capability.
    """

    MenuText = "CalcsLive Plug"
    ToolTip = "CalcsLive calculation capability plug for FreeCAD"
    Icon = ""  # Future: add CalcsLive plug icon

    def Initialize(self):
        """Called when the workbench is first loaded"""
        print("[CalcsLivePlug] Workbench initialized")

        # Import CalcsLive plug server using absolute import
        addon_dir = os.path.join(App.getUserAppDataDir(), "Mod", "CalcsLivePlug")
        if addon_dir not in sys.path:
            sys.path.insert(0, addon_dir)

        # Import with the new module name
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "calcslive_plug_server",
            os.path.join(addon_dir, "calcslive-freecad-plug-server.py")
        )
        calcslive_plug_server = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(calcslive_plug_server)

        class PlugInCalcsLiveCommand:
            def GetResources(self):
                return {
                    'Pixmap': '',
                    'MenuText': 'Plug In CalcsLive',
                    'ToolTip': 'Plug in CalcsLive calculation capability HTTP server'
                }
            def Activated(self):
                success = calcslive_plug_server.plug_in()
                if success:
                    App.Console.PrintMessage("✓ CalcsLive plugged in successfully\n")
                else:
                    App.Console.PrintError("✗ Failed to plug in CalcsLive\n")

        class UnplugCalcsLiveCommand:
            def GetResources(self):
                return {
                    'Pixmap': '',
                    'MenuText': 'Unplug CalcsLive',
                    'ToolTip': 'Unplug CalcsLive calculation capability HTTP server'
                }
            def Activated(self):
                success = calcslive_plug_server.unplug()
                if success:
                    App.Console.PrintMessage("✓ CalcsLive unplugged successfully\n")
                else:
                    App.Console.PrintError("✗ Failed to unplug CalcsLive\n")

        class PlugStatusCommand:
            def GetResources(self):
                return {
                    'Pixmap': '',
                    'MenuText': 'Plug Status',
                    'ToolTip': 'Check CalcsLive plug status and functionality'
                }
            def Activated(self):
                test_result = calcslive_plug_server.test_plug()
                status = "✓ Plugged in" if test_result.get("status") == "ok" else "✗ Error"
                App.Console.PrintMessage(f"CalcsLive Plug Status: {status}\n")
                App.Console.PrintMessage(f"Details: {test_result}\n")

        # Register commands with new names
        Gui.addCommand('PlugInCalcsLive', PlugInCalcsLiveCommand())
        Gui.addCommand('UnplugCalcsLive', UnplugCalcsLiveCommand())
        Gui.addCommand('PlugStatus', PlugStatusCommand())

        # Create toolbar with CalcsLive plug commands
        self.list = ["PlugInCalcsLive", "UnplugCalcsLive", "PlugStatus"]
        self.appendToolbar("CalcsLive Plug", self.list)

    def Activated(self):
        """Called when the workbench is activated (user switches to it)"""
        print("[CalcsLivePlug] CalcsLive Plug workbench activated")

    def Deactivated(self):
        """Called when the workbench is deactivated"""
        print("[CalcsLivePlug] CalcsLive Plug workbench deactivated")

# Register the CalcsLive Plug workbench
Gui.addWorkbench(CalcsLivePlugWorkbench())

def auto_plug_calcslive():
    """
    Auto-plug CalcsLive capability when FreeCAD starts.
    This function is called automatically when FreeCAD loads.
    """
    try:
        print("[CalcsLivePlug] Auto-plugging CalcsLive capability...")

        # Import CalcsLive plug server using absolute import
        addon_dir = os.path.join(App.getUserAppDataDir(), "Mod", "CalcsLivePlug")
        if addon_dir not in sys.path:
            sys.path.insert(0, addon_dir)

        # Import with the new module name
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "calcslive_plug_server",
            os.path.join(addon_dir, "calcslive-freecad-plug-server.py")
        )
        calcslive_plug_server = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(calcslive_plug_server)

        # Plug in CalcsLive capability
        success = calcslive_plug_server.plug_in()

        if success:
            print("[CalcsLivePlug] ✓ CalcsLive plugged in successfully!")
            print("[CalcsLivePlug] ✓ HTTP endpoints are now available")

            # Test the plug functionality
            test_result = calcslive_plug_server.test_plug()
            print(f"[CalcsLivePlug] Plug test: {test_result}")

        else:
            print("[CalcsLivePlug] ✗ Failed to plug in CalcsLive")

    except Exception as e:
        print(f"[CalcsLivePlug] ERROR in auto_plug_calcslive: {str(e)}")
        import traceback
        traceback.print_exc()

# Auto-plug CalcsLive when this addon loads
# This runs immediately when FreeCAD starts and loads the addon
print("[CalcsLivePlug] Auto-plugging CalcsLive capability...")
auto_plug_calcslive()

print("[CalcsLivePlug] InitGui.py completed")