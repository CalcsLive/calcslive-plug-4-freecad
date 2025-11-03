"""
CalcsLive Dashboard Command

FreeCAD command to open the CalcsLive parameter mapping dashboard.
"""

import FreeCAD
import FreeCADGui
from core.CalcsLiveClient import CalcsLiveClient
from core.ConfigManager import get_config_manager
from utils.BrowserLauncher import BrowserLauncher


class DashboardCommand:
    """Command to open CalcsLive dashboard"""

    def GetResources(self):
        """Return command resources (icon, menu text, etc.)"""
        return {
            'Pixmap': 'CalcsLive_Dashboard.svg',
            'MenuText': 'Open Dashboard',
            'ToolTip': 'Open CalcsLive parameter mapping dashboard in web browser',
            'Accel': 'Ctrl+Shift+D'
        }

    def IsActive(self):
        """Check if command should be active"""
        # Active if we have an active document
        return FreeCAD.ActiveDocument is not None

    def Activated(self):
        """Execute the command"""
        try:
            # Get article ID from user
            article_id = self._get_article_id()

            if not article_id:
                return

            config_manager = get_config_manager()
            api_key = config_manager.get_api_key()

            # Create CalcsLive client
            client = CalcsLiveClient(api_key if api_key else None)

            # Get model ID
            model_id = self._get_current_model_id()

            # Get dashboard URL
            dashboard_url = client.get_dashboard_url(article_id, model_id)

            # Open dashboard in browser
            browser_launcher = BrowserLauncher()
            success = browser_launcher.open_url(dashboard_url)

            if success:
                FreeCAD.Console.PrintMessage(f"CalcsLive: Opened dashboard for article {article_id}\n")
                FreeCAD.Console.PrintMessage(f"URL: {dashboard_url}\n")

                # Add to recent articles
                config_manager.add_recent_article(article_id)

                # Show dashboard info
                self._show_dashboard_info(article_id, dashboard_url)

            else:
                self._show_url_dialog(dashboard_url)

        except Exception as e:
            FreeCAD.Console.PrintError(f"CalcsLive Dashboard failed: {str(e)}\n")
            self._show_error_dialog(str(e))

    def _get_article_id(self):
        """Get article ID from user input"""
        try:
            from PySide2 import QtWidgets, QtCore

            config_manager = get_config_manager()
            recent_articles = config_manager.get_recent_articles()

            # Create input dialog
            dialog = QtWidgets.QDialog()
            dialog.setWindowTitle("CalcsLive Dashboard")
            dialog.setWindowModality(QtCore.Qt.ApplicationModal)
            dialog.resize(400, 300)

            layout = QtWidgets.QVBoxLayout(dialog)

            # Title
            title = QtWidgets.QLabel("Select CalcsLive Article")
            title.setStyleSheet("font-size: 14px; font-weight: bold;")
            layout.addWidget(title)

            # Article ID input
            input_group = QtWidgets.QGroupBox("Article ID")
            input_layout = QtWidgets.QVBoxLayout(input_group)

            article_input = QtWidgets.QLineEdit()
            article_input.setPlaceholderText("Enter CalcsLive article ID (e.g., ABC123)")
            input_layout.addWidget(article_input)

            layout.addWidget(input_group)

            # Recent articles (if any)
            if recent_articles:
                recent_group = QtWidgets.QGroupBox("Recent Articles")
                recent_layout = QtWidgets.QVBoxLayout(recent_group)

                recent_list = QtWidgets.QListWidget()
                for article in recent_articles[:5]:  # Show last 5
                    item_text = f"{article['id']} - {article.get('title', 'Untitled')}"
                    item = QtWidgets.QListWidgetItem(item_text)
                    item.setData(QtCore.Qt.UserRole, article['id'])
                    recent_list.addItem(item)

                # Handle selection
                def on_recent_selected():
                    current_item = recent_list.currentItem()
                    if current_item:
                        article_id = current_item.data(QtCore.Qt.UserRole)
                        article_input.setText(article_id)

                recent_list.itemClicked.connect(on_recent_selected)
                recent_list.itemDoubleClicked.connect(dialog.accept)

                recent_layout.addWidget(recent_list)
                layout.addWidget(recent_group)

            # Buttons
            button_layout = QtWidgets.QHBoxLayout()

            ok_button = QtWidgets.QPushButton("Open Dashboard")
            ok_button.setDefault(True)
            ok_button.clicked.connect(dialog.accept)

            cancel_button = QtWidgets.QPushButton("Cancel")
            cancel_button.clicked.connect(dialog.reject)

            button_layout.addWidget(ok_button)
            button_layout.addWidget(cancel_button)
            layout.addLayout(button_layout)

            # Show dialog
            if dialog.exec_() == QtWidgets.QDialog.Accepted:
                return article_input.text().strip()
            else:
                return None

        except Exception as e:
            FreeCAD.Console.PrintWarning(f"Could not show article selection dialog: {e}\n")

            # Fallback: simple input
            try:
                from PySide2 import QtWidgets
                article_id, ok = QtWidgets.QInputDialog.getText(
                    None,
                    "CalcsLive Dashboard",
                    "Enter CalcsLive article ID:"
                )
                return article_id.strip() if ok else None

            except Exception:
                FreeCAD.Console.PrintMessage("Please enter article ID in console:\n")
                return input("CalcsLive article ID: ").strip()

    def _get_current_model_id(self):
        """Get identifier for current FreeCAD model"""
        try:
            doc = FreeCAD.ActiveDocument
            if doc:
                model_parts = []

                if doc.FileName:
                    model_parts.append(doc.FileName)
                else:
                    model_parts.append(doc.Name)

                model_parts.append(f"objects_{len(doc.Objects)}")
                return "_".join(model_parts).replace(" ", "_").replace("/", "_").replace("\\", "_")

            return None

        except Exception:
            return None

    def _show_dashboard_info(self, article_id, dashboard_url):
        """Show dashboard information dialog"""
        try:
            from PySide2 import QtWidgets, QtCore

            dialog = QtWidgets.QDialog()
            dialog.setWindowTitle("CalcsLive Dashboard")
            dialog.setWindowModality(QtCore.Qt.ApplicationModal)
            dialog.resize(500, 200)

            layout = QtWidgets.QVBoxLayout(dialog)

            # Info
            info_text = (
                f"Dashboard opened for article: {article_id}\n\n"
                "Use the web interface to:\n"
                "• Map FreeCAD parameters to CalcsLive symbols\n"
                "• Configure calculation settings\n"
                "• Test parameter synchronization\n\n"
                "Return to FreeCAD and use the Sync command to apply calculations."
            )

            info_label = QtWidgets.QLabel(info_text)
            info_label.setWordWrap(True)
            layout.addWidget(info_label)

            # URL
            url_layout = QtWidgets.QHBoxLayout()
            url_text = QtWidgets.QLineEdit(dashboard_url)
            url_text.setReadOnly(True)

            copy_button = QtWidgets.QPushButton("Copy")
            copy_button.clicked.connect(lambda: QtWidgets.QApplication.clipboard().setText(dashboard_url))

            url_layout.addWidget(url_text)
            url_layout.addWidget(copy_button)
            layout.addLayout(url_layout)

            # Close button
            close_button = QtWidgets.QPushButton("Close")
            close_button.clicked.connect(dialog.accept)
            layout.addWidget(close_button)

            dialog.exec_()

        except Exception as e:
            FreeCAD.Console.PrintWarning(f"Could not show dashboard info: {e}\n")

    def _show_url_dialog(self, dashboard_url):
        """Show URL dialog as fallback"""
        try:
            from PySide2 import QtWidgets

            QtWidgets.QMessageBox.information(
                None,
                "CalcsLive Dashboard",
                f"Please open this URL in your web browser:\n\n{dashboard_url}\n\n"
                "The URL has been copied to your clipboard."
            )

            QtWidgets.QApplication.clipboard().setText(dashboard_url)

        except Exception:
            FreeCAD.Console.PrintMessage(f"CalcsLive dashboard URL: {dashboard_url}\n")

    def _show_error_dialog(self, error_message):
        """Show error dialog"""
        try:
            from PySide2 import QtWidgets

            QtWidgets.QMessageBox.critical(
                None,
                "CalcsLive Dashboard Error",
                f"Failed to open dashboard:\n\n{error_message}"
            )

        except Exception:
            FreeCAD.Console.PrintError(f"CalcsLive dashboard error: {error_message}\n")


# Register command
FreeCADGui.addCommand('CalcsLive_Dashboard', DashboardCommand())