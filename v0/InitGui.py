"""
CalcsLive FreeCAD Workbench - Final Official Pattern

Following the exact same pattern as FreeCAD's Draft workbench.
Uses appendToolbar() method instead of self.list.
"""

import os
import FreeCAD
import FreeCADGui

__title__ = "FreeCAD CalcsLive Workbench"
__author__ = "CalcsLive Team"
__url__ = "https://www.calcs.live"


class CalcsLiveWorkbench(FreeCADGui.Workbench):
    """CalcsLive FreeCAD Workbench - Final Official Pattern"""

    def __init__(self):
        """Initialize workbench"""
        def QT_TRANSLATE_NOOP(context, text):
            return text

        self.__class__.MenuText = QT_TRANSLATE_NOOP("CalcsLive", "CalcsLive")
        self.__class__.ToolTip = QT_TRANSLATE_NOOP("CalcsLive",
                                                   "Unit-aware calculations for FreeCAD")

    def Initialize(self):
        """When the workbench is first loaded (following Draft pattern exactly)"""
        def QT_TRANSLATE_NOOP(context, text):
            return text

        print("CalcsLive Workbench: Initializing (final official pattern)...")

        # Import CalcsLive tools (following Draft pattern)
        try:
            import CalcsLiveTools
            import calcsliveutils.init_tools as it

            # Get command list from tools module
            self.calcslive_commands = it.get_calcslive_commands()

            # Set up toolbars using appendToolbar (following Draft pattern exactly)
            it.init_toolbar(self,
                          QT_TRANSLATE_NOOP("Workbench", "CalcsLive"),
                          self.calcslive_commands)

            # Set up menus (following Draft pattern)
            it.init_menu(self,
                       [QT_TRANSLATE_NOOP("Workbench", "CalcsLive")],
                       self.calcslive_commands)

            print(f"CalcsLive Workbench: Loaded {len(self.calcslive_commands)} commands")
            FreeCAD.Console.PrintMessage("CalcsLive Workbench: Ready with toolbar!\n")

        except Exception as exc:
            print(f"CalcsLive Workbench: Error loading tools: {exc}")
            FreeCAD.Console.PrintError(f"CalcsLive Workbench initialization failed: {exc}\n")
            self.calcslive_commands = []

    def GetClassName(self):
        """Return workbench class name"""
        return "Gui::PythonWorkbench"

    def Activated(self):
        """When the workbench is activated"""
        print("CalcsLive Workbench: Activated (final pattern)")
        FreeCAD.Console.PrintMessage(
            "CalcsLive Workbench activated!\n"
            "Connect: Open development server\n"
            "Dashboard: Parameter mapping interface\n"
            "Status: Show workbench information\n"
        )

    def Deactivated(self):
        """When the workbench is deactivated"""
        print("CalcsLive Workbench: Deactivated (final pattern)")

    def ContextMenu(self, recipient):
        """Add CalcsLive commands to context menus"""
        if recipient == "View":
            return self.calcslive_commands
        return []


# Register the workbench (Draft pattern) - DISABLED for CalcsLive addon
# print("Registering CalcsLive workbench (final official pattern)...")
# FreeCADGui.addWorkbench(CalcsLiveWorkbench())
print("CalcsLiveWorkbench disabled - using CalcsLive addon instead")