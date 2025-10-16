"""
CalcsLive Status Command

FreeCAD command to show CalcsLive connection and sync status.
"""

import FreeCAD
import FreeCADGui
from core.SyncEngine import get_sync_engine
from core.ConfigManager import get_config_manager
from core.CalcsLiveClient import CalcsLiveClient


class StatusCommand:
    """Command to show CalcsLive status"""

    def GetResources(self):
        """Return command resources (icon, menu text, etc.)"""
        return {
            'Pixmap': 'CalcsLive_Status.svg',
            'MenuText': 'Show Status',
            'ToolTip': 'Show CalcsLive connection and synchronization status',
            'Accel': 'Ctrl+Shift+I'  # Info
        }

    def IsActive(self):
        """Check if command should be active"""
        # Always active
        return True

    def Activated(self):
        """Execute the command"""
        try:
            # Gather status information
            status_info = self._gather_status_info()

            # Show status dialog
            self._show_status_dialog(status_info)

        except Exception as e:
            FreeCAD.Console.PrintError(f"CalcsLive Status failed: {str(e)}\n")
            self._show_error_dialog(str(e))

    def _gather_status_info(self):
        """Gather comprehensive status information"""
        status = {
            'timestamp': FreeCAD.now(),
            'freecad': {},
            'config': {},
            'connection': {},
            'sync': {},
            'recent_activity': []
        }

        # FreeCAD status
        try:
            doc = FreeCAD.ActiveDocument
            status['freecad'] = {
                'active_document': doc.Name if doc else None,
                'document_path': doc.FileName if doc and doc.FileName else None,
                'object_count': len(doc.Objects) if doc else 0,
                'has_selection': len(FreeCADGui.Selection.getSelection()) > 0 if doc else False
            }
        except Exception as e:
            status['freecad']['error'] = str(e)

        # Configuration status
        try:
            config_manager = get_config_manager()
            status['config'] = {
                'api_key_set': bool(config_manager.get_api_key()),
                'base_url': config_manager.get_base_url(),
                'auto_sync_enabled': config_manager.is_auto_sync_enabled(),
                'auto_sync_interval': config_manager.get_auto_sync_interval(),
                'recent_articles_count': len(config_manager.get_recent_articles()),
                'config_file': config_manager.get_config_file_path()
            }
        except Exception as e:
            status['config']['error'] = str(e)

        # Connection status
        try:
            config_manager = get_config_manager()
            api_key = config_manager.get_api_key()

            if api_key:
                client = CalcsLiveClient(api_key)
                connection_test = client.test_connection()

                status['connection'] = {
                    'api_key_configured': True,
                    'connection_successful': connection_test,
                    'base_url': client.base_url,
                    'timeout': client.timeout
                }
            else:
                status['connection'] = {
                    'api_key_configured': False,
                    'connection_successful': False,
                    'message': 'No API key configured'
                }

        except Exception as e:
            status['connection']['error'] = str(e)

        # Sync engine status
        try:
            sync_engine = get_sync_engine()
            sync_status = sync_engine.get_sync_status()
            sync_history = sync_engine.get_sync_history(3)

            status['sync'] = sync_status
            status['recent_activity'] = sync_history

        except Exception as e:
            status['sync']['error'] = str(e)

        return status

    def _show_status_dialog(self, status_info):
        """Show comprehensive status dialog"""
        try:
            from PySide2 import QtWidgets, QtCore

            dialog = QtWidgets.QDialog()
            dialog.setWindowTitle("CalcsLive Status")
            dialog.setWindowModality(QtCore.Qt.ApplicationModal)
            dialog.resize(600, 500)

            layout = QtWidgets.QVBoxLayout(dialog)

            # Title
            title = QtWidgets.QLabel("CalcsLive Integration Status")
            title.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
            layout.addWidget(title)

            # Create tabs for different status categories
            tab_widget = QtWidgets.QTabWidget()

            # Overview tab
            overview_tab = self._create_overview_tab(status_info)
            tab_widget.addTab(overview_tab, "Overview")

            # Configuration tab
            config_tab = self._create_config_tab(status_info)
            tab_widget.addTab(config_tab, "Configuration")

            # Connection tab
            connection_tab = self._create_connection_tab(status_info)
            tab_widget.addTab(connection_tab, "Connection")

            # Sync History tab
            history_tab = self._create_history_tab(status_info)
            tab_widget.addTab(history_tab, "Sync History")

            layout.addWidget(tab_widget)

            # Buttons
            button_layout = QtWidgets.QHBoxLayout()

            refresh_button = QtWidgets.QPushButton("Refresh")
            refresh_button.clicked.connect(lambda: self._refresh_status(dialog))

            test_connection_button = QtWidgets.QPushButton("Test Connection")
            test_connection_button.clicked.connect(self._test_connection)

            close_button = QtWidgets.QPushButton("Close")
            close_button.clicked.connect(dialog.accept)

            button_layout.addWidget(refresh_button)
            button_layout.addWidget(test_connection_button)
            button_layout.addStretch()
            button_layout.addWidget(close_button)

            layout.addLayout(button_layout)

            dialog.exec_()

        except Exception as e:
            FreeCAD.Console.PrintWarning(f"Could not show status dialog: {e}\n")
            self._show_simple_status(status_info)

    def _create_overview_tab(self, status_info):
        """Create overview tab widget"""
        try:
            from PySide2 import QtWidgets

            widget = QtWidgets.QWidget()
            layout = QtWidgets.QVBoxLayout(widget)

            # Status indicators
            indicators_layout = QtWidgets.QGridLayout()

            row = 0

            # FreeCAD status
            self._add_status_indicator(indicators_layout, row, "FreeCAD Document",
                                     status_info['freecad'].get('active_document', 'None'))
            row += 1

            # API key status
            api_configured = status_info['config'].get('api_key_set', False)
            self._add_status_indicator(indicators_layout, row, "API Key",
                                     "✓ Configured" if api_configured else "✗ Not configured")
            row += 1

            # Connection status
            connection_ok = status_info['connection'].get('connection_successful', False)
            self._add_status_indicator(indicators_layout, row, "Connection",
                                     "✓ Connected" if connection_ok else "✗ Disconnected")
            row += 1

            # Sync engine status
            sync_initialized = status_info['sync'].get('initialized', False)
            self._add_status_indicator(indicators_layout, row, "Sync Engine",
                                     "✓ Ready" if sync_initialized else "✗ Not initialized")
            row += 1

            layout.addLayout(indicators_layout)

            # Recent activity summary
            if status_info.get('recent_activity'):
                layout.addWidget(QtWidgets.QLabel("Recent Activity:"))

                activity_list = QtWidgets.QListWidget()
                activity_list.setMaximumHeight(150)

                for activity in status_info['recent_activity']:
                    article_id = activity.get('article_id', 'Unknown')
                    success = activity.get('success', False)
                    timestamp = activity.get('timestamp', 0)

                    status_icon = "✓" if success else "✗"
                    item_text = f"{status_icon} {article_id} - {FreeCAD.formatTime(timestamp)}"

                    activity_list.addItem(item_text)

                layout.addWidget(activity_list)

            layout.addStretch()
            return widget

        except Exception as e:
            FreeCAD.Console.PrintWarning(f"Could not create overview tab: {e}\n")
            return QtWidgets.QLabel("Error creating overview")

    def _create_config_tab(self, status_info):
        """Create configuration tab widget"""
        try:
            from PySide2 import QtWidgets

            widget = QtWidgets.QWidget()
            layout = QtWidgets.QFormLayout(widget)

            config = status_info.get('config', {})

            # Configuration details
            layout.addRow("API Key:", QtWidgets.QLabel("Set" if config.get('api_key_set') else "Not set"))
            layout.addRow("Base URL:", QtWidgets.QLabel(config.get('base_url', 'Unknown')))
            layout.addRow("Auto-sync:", QtWidgets.QLabel("Enabled" if config.get('auto_sync_enabled') else "Disabled"))
            layout.addRow("Sync Interval:", QtWidgets.QLabel(f"{config.get('auto_sync_interval', 0)} seconds"))
            layout.addRow("Recent Articles:", QtWidgets.QLabel(str(config.get('recent_articles_count', 0))))
            layout.addRow("Config File:", QtWidgets.QLabel(config.get('config_file', 'Unknown')))

            return widget

        except Exception as e:
            FreeCAD.Console.PrintWarning(f"Could not create config tab: {e}\n")
            return QtWidgets.QLabel("Error creating configuration tab")

    def _create_connection_tab(self, status_info):
        """Create connection tab widget"""
        try:
            from PySide2 import QtWidgets

            widget = QtWidgets.QWidget()
            layout = QtWidgets.QVBoxLayout(widget)

            connection = status_info.get('connection', {})

            # Connection details
            details_layout = QtWidgets.QFormLayout()

            api_configured = connection.get('api_key_configured', False)
            details_layout.addRow("API Key:", QtWidgets.QLabel("Configured" if api_configured else "Not configured"))

            if api_configured:
                connection_successful = connection.get('connection_successful', False)
                details_layout.addRow("Connection Test:",
                                    QtWidgets.QLabel("✓ Success" if connection_successful else "✗ Failed"))

                details_layout.addRow("Base URL:", QtWidgets.QLabel(connection.get('base_url', 'Unknown')))
                details_layout.addRow("Timeout:", QtWidgets.QLabel(f"{connection.get('timeout', 0)} seconds"))

            if connection.get('error'):
                error_label = QtWidgets.QLabel(connection['error'])
                error_label.setStyleSheet("color: red;")
                details_layout.addRow("Error:", error_label)

            layout.addLayout(details_layout)

            # Connection actions
            if api_configured:
                test_button = QtWidgets.QPushButton("Test Connection Now")
                test_button.clicked.connect(self._test_connection)
                layout.addWidget(test_button)

            layout.addStretch()
            return widget

        except Exception as e:
            FreeCAD.Console.PrintWarning(f"Could not create connection tab: {e}\n")
            return QtWidgets.QLabel("Error creating connection tab")

    def _create_history_tab(self, status_info):
        """Create sync history tab widget"""
        try:
            from PySide2 import QtWidgets

            widget = QtWidgets.QWidget()
            layout = QtWidgets.QVBoxLayout(widget)

            sync_info = status_info.get('sync', {})
            recent_activity = status_info.get('recent_activity', [])

            # Sync statistics
            stats_layout = QtWidgets.QFormLayout()
            stats_layout.addRow("Is Syncing:", QtWidgets.QLabel("Yes" if sync_info.get('is_syncing') else "No"))
            stats_layout.addRow("Auto-sync:", QtWidgets.QLabel("Enabled" if sync_info.get('auto_sync_enabled') else "Disabled"))
            stats_layout.addRow("Total Syncs:", QtWidgets.QLabel(str(sync_info.get('sync_count', 0))))
            stats_layout.addRow("Error Count:", QtWidgets.QLabel(str(sync_info.get('error_count', 0))))

            layout.addLayout(stats_layout)

            # Recent sync history
            if recent_activity:
                layout.addWidget(QtWidgets.QLabel("Recent Sync Operations:"))

                history_text = QtWidgets.QTextEdit()
                history_text.setReadOnly(True)
                history_text.setMaximumHeight(200)

                history_content = ""
                for activity in recent_activity:
                    sync_engine = get_sync_engine()
                    report = sync_engine.create_sync_report(activity)
                    history_content += report + "\n" + "="*50 + "\n"

                history_text.setPlainText(history_content)
                layout.addWidget(history_text)

            layout.addStretch()
            return widget

        except Exception as e:
            FreeCAD.Console.PrintWarning(f"Could not create history tab: {e}\n")
            return QtWidgets.QLabel("Error creating history tab")

    def _add_status_indicator(self, layout, row, label, value):
        """Add status indicator to grid layout"""
        try:
            from PySide2 import QtWidgets

            label_widget = QtWidgets.QLabel(f"{label}:")
            label_widget.setStyleSheet("font-weight: bold;")

            value_widget = QtWidgets.QLabel(str(value))

            # Color coding for status
            if "✓" in str(value):
                value_widget.setStyleSheet("color: green;")
            elif "✗" in str(value):
                value_widget.setStyleSheet("color: red;")

            layout.addWidget(label_widget, row, 0)
            layout.addWidget(value_widget, row, 1)

        except Exception as e:
            FreeCAD.Console.PrintWarning(f"Could not add status indicator: {e}\n")

    def _refresh_status(self, dialog):
        """Refresh status information"""
        try:
            # Close current dialog and reopen with fresh data
            dialog.accept()
            self.Activated()

        except Exception as e:
            FreeCAD.Console.PrintWarning(f"Could not refresh status: {e}\n")

    def _test_connection(self):
        """Test CalcsLive connection"""
        try:
            from PySide2 import QtWidgets

            config_manager = get_config_manager()
            api_key = config_manager.get_api_key()

            if not api_key:
                QtWidgets.QMessageBox.warning(
                    None,
                    "Connection Test",
                    "No API key configured. Please set up your API key first."
                )
                return

            # Test connection
            client = CalcsLiveClient(api_key)
            success = client.test_connection()

            if success:
                QtWidgets.QMessageBox.information(
                    None,
                    "Connection Test",
                    "✓ Connection to CalcsLive successful!"
                )
            else:
                QtWidgets.QMessageBox.warning(
                    None,
                    "Connection Test",
                    "✗ Connection to CalcsLive failed. Please check your API key and internet connection."
                )

        except Exception as e:
            FreeCAD.Console.PrintError(f"Connection test failed: {e}\n")
            try:
                from PySide2 import QtWidgets
                QtWidgets.QMessageBox.critical(
                    None,
                    "Connection Test Error",
                    f"Connection test failed:\n\n{str(e)}"
                )
            except:
                pass

    def _show_simple_status(self, status_info):
        """Show simple status as fallback"""
        try:
            from PySide2 import QtWidgets

            # Create simple status text
            status_text = "CalcsLive Status:\n\n"

            # FreeCAD
            doc_name = status_info['freecad'].get('active_document', 'None')
            status_text += f"Active Document: {doc_name}\n"

            # Configuration
            api_set = status_info['config'].get('api_key_set', False)
            status_text += f"API Key: {'Set' if api_set else 'Not set'}\n"

            # Connection
            connected = status_info['connection'].get('connection_successful', False)
            status_text += f"Connection: {'Connected' if connected else 'Disconnected'}\n"

            QtWidgets.QMessageBox.information(
                None,
                "CalcsLive Status",
                status_text
            )

        except Exception:
            # Ultimate fallback - console output
            FreeCAD.Console.PrintMessage("CalcsLive Status - check console for details\n")
            FreeCAD.Console.PrintMessage(f"Status info: {status_info}\n")

    def _show_error_dialog(self, error_message):
        """Show error dialog"""
        try:
            from PySide2 import QtWidgets

            QtWidgets.QMessageBox.critical(
                None,
                "CalcsLive Status Error",
                f"Failed to retrieve status:\n\n{error_message}"
            )

        except Exception:
            FreeCAD.Console.PrintError(f"CalcsLive status error: {error_message}\n")


# Register command
FreeCADGui.addCommand('CalcsLive_Status', StatusCommand())