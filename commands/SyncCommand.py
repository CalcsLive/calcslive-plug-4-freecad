"""
CalcsLive Sync Command

FreeCAD command to synchronize parameters with CalcsLive calculations.
"""

import FreeCAD
import FreeCADGui
from core.SyncEngine import get_sync_engine
from core.ConfigManager import get_config_manager


class SyncCommand:
    """Command to sync with CalcsLive"""

    def GetResources(self):
        """Return command resources (icon, menu text, etc.)"""
        return {
            'Pixmap': 'CalcsLive_Sync.svg',
            'MenuText': 'Sync with CalcsLive',
            'ToolTip': 'Synchronize FreeCAD parameters with CalcsLive calculations',
            'Accel': 'Ctrl+Shift+S'
        }

    def IsActive(self):
        """Check if command should be active"""
        # Active if we have an active document
        return FreeCAD.ActiveDocument is not None

    def Activated(self):
        """Execute the command"""
        try:
            # Get article ID and sync options from user
            sync_info = self._get_sync_info()

            if not sync_info:
                return

            article_id = sync_info['article_id']
            sync_options = sync_info['options']

            # Initialize sync engine
            sync_engine = get_sync_engine()
            config_manager = get_config_manager()

            if not sync_engine.initialize(config_manager.get_api_key()):
                self._show_error_dialog("Failed to initialize CalcsLive connection. Please check your API key.")
                return

            # Validate sync readiness
            validation = sync_engine.validate_sync_readiness(article_id)

            if not validation['ready']:
                self._show_validation_errors(validation)
                return

            # Show progress dialog
            progress_dialog = self._create_progress_dialog()

            try:
                # Register progress callback
                def on_progress(data):
                    if progress_dialog:
                        step = data.get('step', 'unknown')
                        progress = data.get('progress', 0)
                        progress_dialog.update_progress(step, progress)

                sync_engine.register_sync_callback('on_sync_progress', on_progress)

                # Perform sync
                if sync_options.get('sync_selection', False):
                    sync_result = sync_engine.sync_selection_with_calcslive(article_id, sync_options)
                else:
                    sync_result = sync_engine.sync_with_calcslive(article_id, sync_options)

                # Close progress dialog
                if progress_dialog:
                    progress_dialog.close()

                # Show results
                self._show_sync_results(sync_result)

                # Add to recent articles
                config_manager.add_recent_article(article_id)

            finally:
                # Cleanup
                sync_engine.unregister_sync_callback('on_sync_progress', on_progress)
                if progress_dialog:
                    progress_dialog.close()

        except Exception as e:
            FreeCAD.Console.PrintError(f"CalcsLive Sync failed: {str(e)}\n")
            self._show_error_dialog(str(e))

    def _get_sync_info(self):
        """Get sync information from user"""
        try:
            from PySide2 import QtWidgets, QtCore

            config_manager = get_config_manager()
            recent_articles = config_manager.get_recent_articles()

            # Create sync dialog
            dialog = QtWidgets.QDialog()
            dialog.setWindowTitle("CalcsLive Sync")
            dialog.setWindowModality(QtCore.Qt.ApplicationModal)
            dialog.resize(450, 400)

            layout = QtWidgets.QVBoxLayout(dialog)

            # Title
            title = QtWidgets.QLabel("Synchronize with CalcsLive")
            title.setStyleSheet("font-size: 14px; font-weight: bold;")
            layout.addWidget(title)

            # Article ID
            article_group = QtWidgets.QGroupBox("Article")
            article_layout = QtWidgets.QVBoxLayout(article_group)

            article_input = QtWidgets.QLineEdit()
            article_input.setPlaceholderText("Enter CalcsLive article ID")
            article_layout.addWidget(article_input)

            # Recent articles dropdown
            if recent_articles:
                recent_combo = QtWidgets.QComboBox()
                recent_combo.addItem("Select from recent articles...")

                for article in recent_articles[:5]:
                    display_text = f"{article['id']} - {article.get('title', 'Untitled')}"
                    recent_combo.addItem(display_text, article['id'])

                def on_recent_selected():
                    if recent_combo.currentIndex() > 0:
                        article_id = recent_combo.currentData()
                        article_input.setText(article_id)

                recent_combo.currentIndexChanged.connect(on_recent_selected)
                article_layout.addWidget(recent_combo)

            layout.addWidget(article_group)

            # Sync options
            options_group = QtWidgets.QGroupBox("Sync Options")
            options_layout = QtWidgets.QVBoxLayout(options_group)

            # Scope
            scope_layout = QtWidgets.QHBoxLayout()
            scope_layout.addWidget(QtWidgets.QLabel("Scope:"))

            sync_all_radio = QtWidgets.QRadioButton("All parameters")
            sync_all_radio.setChecked(True)
            sync_selection_radio = QtWidgets.QRadioButton("Selected objects only")

            scope_layout.addWidget(sync_all_radio)
            scope_layout.addWidget(sync_selection_radio)
            scope_layout.addStretch()
            options_layout.addLayout(scope_layout)

            # Update model
            update_model_check = QtWidgets.QCheckBox("Update FreeCAD model with results")
            update_model_check.setChecked(config_manager.should_update_model_on_sync())
            options_layout.addWidget(update_model_check)

            # Confirm updates
            confirm_updates_check = QtWidgets.QCheckBox("Confirm updates before applying")
            confirm_updates_check.setChecked(config_manager.should_confirm_updates())
            options_layout.addWidget(confirm_updates_check)

            layout.addWidget(options_group)

            # Buttons
            button_layout = QtWidgets.QHBoxLayout()

            sync_button = QtWidgets.QPushButton("Start Sync")
            sync_button.setDefault(True)
            sync_button.clicked.connect(dialog.accept)

            cancel_button = QtWidgets.QPushButton("Cancel")
            cancel_button.clicked.connect(dialog.reject)

            button_layout.addWidget(sync_button)
            button_layout.addWidget(cancel_button)
            layout.addLayout(button_layout)

            # Show dialog
            if dialog.exec_() == QtWidgets.QDialog.Accepted:
                article_id = article_input.text().strip()
                if not article_id:
                    return None

                return {
                    'article_id': article_id,
                    'options': {
                        'sync_selection': sync_selection_radio.isChecked(),
                        'update_model': update_model_check.isChecked(),
                        'confirm_updates': confirm_updates_check.isChecked()
                    }
                }
            else:
                return None

        except Exception as e:
            FreeCAD.Console.PrintWarning(f"Could not show sync dialog: {e}\n")
            return None

    def _create_progress_dialog(self):
        """Create progress dialog for sync operation"""
        try:
            from PySide2 import QtWidgets, QtCore

            class ProgressDialog(QtWidgets.QDialog):
                def __init__(self):
                    super().__init__()
                    self.setWindowTitle("CalcsLive Sync Progress")
                    self.setWindowModality(QtCore.Qt.ApplicationModal)
                    self.resize(400, 150)

                    layout = QtWidgets.QVBoxLayout(self)

                    self.status_label = QtWidgets.QLabel("Initializing sync...")
                    layout.addWidget(self.status_label)

                    self.progress_bar = QtWidgets.QProgressBar()
                    self.progress_bar.setRange(0, 100)
                    layout.addWidget(self.progress_bar)

                    self.detail_label = QtWidgets.QLabel("")
                    self.detail_label.setStyleSheet("color: gray; font-size: 10px;")
                    layout.addWidget(self.detail_label)

                    # Cancel button
                    self.cancel_button = QtWidgets.QPushButton("Cancel")
                    self.cancel_button.clicked.connect(self.reject)
                    layout.addWidget(self.cancel_button)

                def update_progress(self, step, progress):
                    step_names = {
                        'validate': 'Validating article...',
                        'extract': 'Extracting parameters...',
                        'calculate': 'Calculating results...',
                        'update': 'Updating model...',
                        'complete': 'Sync completed!'
                    }

                    self.status_label.setText(step_names.get(step, f"Processing {step}..."))
                    self.progress_bar.setValue(int(progress))
                    self.detail_label.setText(f"Step: {step} ({progress}%)")

                    QtWidgets.QApplication.processEvents()

            dialog = ProgressDialog()
            dialog.show()
            return dialog

        except Exception as e:
            FreeCAD.Console.PrintWarning(f"Could not create progress dialog: {e}\n")
            return None

    def _show_sync_results(self, sync_result):
        """Show sync results dialog"""
        try:
            from PySide2 import QtWidgets, QtCore

            dialog = QtWidgets.QDialog()
            dialog.setWindowTitle("CalcsLive Sync Results")
            dialog.setWindowModality(QtCore.Qt.ApplicationModal)
            dialog.resize(500, 400)

            layout = QtWidgets.QVBoxLayout(dialog)

            # Status icon and title
            title_layout = QtWidgets.QHBoxLayout()

            if sync_result.get('success'):
                status_text = "✓ Sync Completed Successfully"
                status_style = "color: green; font-size: 14px; font-weight: bold;"
            else:
                status_text = "✗ Sync Failed"
                status_style = "color: red; font-size: 14px; font-weight: bold;"

            status_label = QtWidgets.QLabel(status_text)
            status_label.setStyleSheet(status_style)
            title_layout.addWidget(status_label)
            title_layout.addStretch()

            layout.addLayout(title_layout)

            # Results details
            details_text = QtWidgets.QTextEdit()
            details_text.setReadOnly(True)

            # Format sync report
            sync_engine = get_sync_engine()
            report = sync_engine.create_sync_report(sync_result)
            details_text.setPlainText(report)

            layout.addWidget(details_text)

            # Buttons
            button_layout = QtWidgets.QHBoxLayout()

            if sync_result.get('success'):
                dashboard_button = QtWidgets.QPushButton("Open Dashboard")
                dashboard_button.clicked.connect(lambda: self._open_dashboard(sync_result.get('article_id')))
                button_layout.addWidget(dashboard_button)

            button_layout.addStretch()

            close_button = QtWidgets.QPushButton("Close")
            close_button.clicked.connect(dialog.accept)
            button_layout.addWidget(close_button)

            layout.addLayout(button_layout)

            dialog.exec_()

        except Exception as e:
            FreeCAD.Console.PrintWarning(f"Could not show sync results: {e}\n")
            # Fallback: print to console
            sync_engine = get_sync_engine()
            report = sync_engine.create_sync_report(sync_result)
            FreeCAD.Console.PrintMessage(f"CalcsLive Sync Results:\n{report}\n")

    def _show_validation_errors(self, validation):
        """Show validation errors dialog"""
        try:
            from PySide2 import QtWidgets

            error_text = "Cannot proceed with sync due to the following issues:\n\n"

            for error in validation.get('errors', []):
                error_text += f"• {error}\n"

            if validation.get('warnings'):
                error_text += "\nWarnings:\n"
                for warning in validation['warnings']:
                    error_text += f"• {warning}\n"

            QtWidgets.QMessageBox.warning(
                None,
                "CalcsLive Sync Validation",
                error_text
            )

        except Exception:
            FreeCAD.Console.PrintWarning("Sync validation failed. Check console for details.\n")
            for error in validation.get('errors', []):
                FreeCAD.Console.PrintError(f"Validation error: {error}\n")

    def _show_error_dialog(self, error_message):
        """Show error dialog"""
        try:
            from PySide2 import QtWidgets

            QtWidgets.QMessageBox.critical(
                None,
                "CalcsLive Sync Error",
                f"Sync operation failed:\n\n{error_message}"
            )

        except Exception:
            FreeCAD.Console.PrintError(f"CalcsLive sync error: {error_message}\n")

    def _open_dashboard(self, article_id):
        """Open dashboard for article"""
        try:
            if article_id:
                # Use the dashboard command
                FreeCADGui.runCommand('CalcsLive_Dashboard')

        except Exception as e:
            FreeCAD.Console.PrintWarning(f"Could not open dashboard: {e}\n")


# Register command
FreeCADGui.addCommand('CalcsLive_Sync', SyncCommand())