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

        class InitializePQsCommand:
            def GetResources(self):
                return {
                    'Pixmap': '',
                    'MenuText': 'Initialize PQs VarSet',
                    'ToolTip': 'Create a new VarSet with label "PQs" for CalcsLive compatibility'
                }
            def Activated(self):
                doc = App.ActiveDocument
                if not doc:
                    App.Console.PrintError("✗ No active document. Please create or open a document first.\n")
                    return

                # Check if a VarSet with label "PQs" already exists
                for obj in doc.Objects:
                    if hasattr(obj, 'TypeId') and obj.TypeId == 'App::VarSet':
                        if hasattr(obj, 'Label') and obj.Label == 'PQs':
                            App.Console.PrintWarning(f"⚠ VarSet with label 'PQs' already exists: {obj.Name}\n")
                            return

                # Create new VarSet
                try:
                    varset = doc.addObject('App::VarSet', 'PQs')
                    varset.Label = 'PQs'
                    doc.recompute()
                    App.Console.PrintMessage(f"✓ Created VarSet '{varset.Name}' with label 'PQs'\n")

                    # Pop up Add Property dialog (mimics manual doubleClick behavior)
                    # This is needed for the VarSet to be recognized by export endpoint
                    if hasattr(varset, 'ViewObject') and varset.ViewObject:
                        varset.ViewObject.doubleClicked()
                        App.Console.PrintMessage("✓ Add Property dialog opened - please create first parameter\n")
                        App.Console.PrintMessage("✓ Document will be CalcsLive Plug compatible after adding a parameter\n")
                    else:
                        App.Console.PrintWarning("⚠ Could not open Add Property dialog automatically\n")
                        App.Console.PrintMessage("✓ Please manually add a property to complete initialization\n")
                except Exception as e:
                    App.Console.PrintError(f"✗ Failed to create VarSet: {str(e)}\n")

        class RenameVarSetParamCommand:
            def GetResources(self):
                return {
                    'Pixmap': '',
                    'MenuText': 'Rename VarSet Parameter',
                    'ToolTip': 'Rename a VarSet parameter (workaround for FreeCAD v1.0.2)'
                }
            def Activated(self):
                doc = App.ActiveDocument
                if not doc:
                    App.Console.PrintError("✗ No active document\n")
                    return

                # Get VarSet objects
                varsets = [obj for obj in doc.Objects
                          if hasattr(obj, 'TypeId') and obj.TypeId == 'App::VarSet']

                if not varsets:
                    App.Console.PrintError("✗ No VarSet objects found in document\n")
                    return

                # Show custom dialog combining all selections
                result = self.show_rename_dialog(varsets)
                if not result:
                    return

                varset, old_name, new_name = result

                # Validate new name
                if new_name in varset.PropertiesList:
                    App.Console.PrintError(f"✗ Parameter '{new_name}' already exists\n")
                    return

                # Perform rename
                try:
                    self.rename_varset_param(varset, old_name, new_name)
                    App.Console.PrintMessage(f"✓ Renamed '{old_name}' → '{new_name}' in VarSet '{varset.Label}'\n")
                except Exception as e:
                    App.Console.PrintError(f"✗ Failed to rename parameter: {str(e)}\n")
                    import traceback
                    traceback.print_exc()

            def show_rename_dialog(self, varsets):
                """Show combined dialog for VarSet, parameter selection and new name input"""
                from PySide import QtGui

                class RenameDialog(QtGui.QDialog):
                    def __init__(self, varsets, parent=None):
                        super(RenameDialog, self).__init__(parent)
                        self.varsets = varsets
                        self.setWindowTitle("Rename VarSet Parameter")
                        self.setMinimumWidth(400)

                        layout = QtGui.QVBoxLayout(self)

                        # VarSet selection
                        layout.addWidget(QtGui.QLabel("VarSet:"))
                        self.varset_combo = QtGui.QComboBox()
                        for vs in varsets:
                            self.varset_combo.addItem(f"{vs.Label} ({vs.Name})")
                        layout.addWidget(self.varset_combo)

                        # Parameter selection
                        layout.addWidget(QtGui.QLabel("Parameter:"))
                        self.param_combo = QtGui.QComboBox()
                        layout.addWidget(self.param_combo)

                        # New name input
                        layout.addWidget(QtGui.QLabel("New Name:"))
                        self.new_name_edit = QtGui.QLineEdit()
                        layout.addWidget(self.new_name_edit)

                        # Buttons
                        button_box = QtGui.QDialogButtonBox(
                            QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel
                        )
                        button_box.accepted.connect(self.accept)
                        button_box.rejected.connect(self.reject)
                        layout.addWidget(button_box)

                        # Connect signals
                        self.varset_combo.currentIndexChanged.connect(self.update_params)
                        self.param_combo.currentIndexChanged.connect(self.update_new_name)

                        # Initialize
                        self.update_params()

                    def update_params(self):
                        self.param_combo.clear()
                        idx = self.varset_combo.currentIndex()
                        if idx >= 0:
                            vs = self.varsets[idx]
                            # Use same filter as calcslive-freecad-plug-server.py
                            skip_props = {
                                'Label', 'Label2', 'Name', 'Visibility', 'Content', 'ExpressionEngine',
                                'Document', 'Module', 'TypeId', 'ID', 'State', 'ViewObject', 'FullName',
                                'InList', 'OutList', 'Parents', 'MemSize', 'MustExecute', 'Removing',
                                'NoTouch', 'OldLabel', 'ExportVars'
                            }
                            params = [prop for prop in vs.PropertiesList
                                     if not prop.startswith('_') and prop not in skip_props]
                            self.param_combo.addItems(params)

                    def update_new_name(self):
                        current = self.param_combo.currentText()
                        if current:
                            self.new_name_edit.setText(current)

                    def get_result(self):
                        vs_idx = self.varset_combo.currentIndex()
                        if vs_idx < 0:
                            return None
                        varset = self.varsets[vs_idx]
                        old_name = self.param_combo.currentText()
                        new_name = self.new_name_edit.text()

                        if not old_name or not new_name or old_name == new_name:
                            return None

                        return (varset, old_name, new_name)

                dialog = RenameDialog(varsets)
                if dialog.exec_() == QtGui.QDialog.Accepted:
                    return dialog.get_result()
                return None

            def rename_varset_param(self, vs, old, new):
                """
                Rename a VarSet parameter (workaround for FreeCAD v1.0.2).
                Based on rename_varset_param.FCMacro
                """
                # 1) Get original property group and recreate with same type and group
                t = vs.getTypeIdOfProperty(old) if hasattr(vs, "getTypeIdOfProperty") else "App::PropertyString"

                # Get original group - check if property has group info
                group = ""
                if hasattr(vs, "getGroupOfProperty"):
                    group = vs.getGroupOfProperty(old) or ""

                val = getattr(vs, old)
                vs.addProperty(t, new, group, f"renamed from {old}")
                setattr(vs, new, val)

                # 2) Update expressions across doc: <VarsetName>.<old> -> <VarsetName>.<new>
                doc = vs.Document
                needle, repl = f"{vs.Name}.{old}", f"{vs.Name}.{new}"
                for obj in doc.Objects:
                    if not hasattr(obj, "ExpressionEngine"):
                        continue
                    ee = list(obj.ExpressionEngine)  # list of (prop, expr)
                    changed = False
                    for i, (prop, expr) in enumerate(ee):
                        if expr and needle in expr:
                            ee[i] = (prop, expr.replace(needle, repl))
                            changed = True
                    if changed:
                        obj.ExpressionEngine = ee

                # 3) Remove old and recompute
                if hasattr(vs, "removeProperty"):
                    vs.removeProperty(old)
                doc.recompute()

        # Register commands with new names
        Gui.addCommand('PlugInCalcsLive', PlugInCalcsLiveCommand())
        Gui.addCommand('UnplugCalcsLive', UnplugCalcsLiveCommand())
        Gui.addCommand('PlugStatus', PlugStatusCommand())

        # TODO: Temporarily disabled - unreliable with expression swapping and FreeCAD state sync
        # Gui.addCommand('InitializePQs', InitializePQsCommand())
        # Gui.addCommand('RenameVarSetParam', RenameVarSetParamCommand())

        # Create toolbar with CalcsLive plug commands
        # self.list = ["PlugInCalcsLive", "UnplugCalcsLive", "PlugStatus", "InitializePQs", "RenameVarSetParam"]
        self.list = ["PlugInCalcsLive", "UnplugCalcsLive", "PlugStatus"]  # Removed InitializePQs and RenameVarSetParam
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