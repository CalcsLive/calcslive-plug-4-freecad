"""
CalcsLive Connect Command

FreeCAD command to establish connection with CalcsLive.
Opens the CalcsLive connection interface in a web browser.
"""

import FreeCAD
import FreeCADGui
from core.CalcsLiveClient import CalcsLiveClient
from core.ConfigManager import get_config_manager
from utils.BrowserLauncher import BrowserLauncher


class ConnectCommand:
    """Command to connect FreeCAD with CalcsLive"""

    def GetResources(self):
        """Return command resources (icon, menu text, etc.)"""
        return {
            'Pixmap': 'CalcsLive_Connect.svg',  # Icon file
            'MenuText': 'Connect to CalcsLive',
            'ToolTip': 'Establish connection with CalcsLive for bi-directional parameter sync',
            'Accel': 'Ctrl+Shift+C'  # Keyboard shortcut
        }

    def IsActive(self):
        """Check if command should be active"""
        # Always active - no specific document requirements
        return True

    def Activated(self):
        """Execute the command"""
        try:
            config_manager = get_config_manager()

            # Get current API key
            api_key = config_manager.get_api_key()

            # Create CalcsLive client to get connection URL
            client = CalcsLiveClient(api_key if api_key else None)

            # Get FreeCAD model ID (if available)
            model_id = self._get_current_model_id()

            # Get connection URL
            connect_url = client.get_freecad_connect_url(model_id)

            # Open connection page in browser
            browser_launcher = BrowserLauncher()
            success = browser_launcher.open_url(connect_url)

            if success:
                FreeCAD.Console.PrintMessage(f"CalcsLive: Opened connection page in browser\n")
                FreeCAD.Console.PrintMessage(f"URL: {connect_url}\n")

                # Show connection dialog
                self._show_connection_dialog(connect_url)

            else:
                # Fallback: show URL to user
                self._show_url_dialog(connect_url)

        except Exception as e:
            FreeCAD.Console.PrintError(f"CalcsLive Connect failed: {str(e)}\n")
            self._show_error_dialog(str(e))

    def _get_current_model_id(self):
        """Get identifier for current FreeCAD model"""
        try:
            doc = FreeCAD.ActiveDocument
            if doc:
                # Use document name and file path as model ID
                model_parts = []

                if doc.FileName:
                    model_parts.append(doc.FileName)
                else:
                    model_parts.append(doc.Name)

                # Add object count as additional identifier
                model_parts.append(f"objects_{len(doc.Objects)}")

                return "_".join(model_parts).replace(" ", "_").replace("/", "_").replace("\\", "_")

            return None

        except Exception:
            return None

    def _show_connection_dialog(self, connect_url):
        """Show connection status dialog"""
        try:
            from PySide2 import QtWidgets, QtCore, QtGui

            # Create dialog
            dialog = QtWidgets.QDialog()
            dialog.setWindowTitle("CalcsLive Connection")
            dialog.setWindowModality(QtCore.Qt.ApplicationModal)
            dialog.resize(500, 300)

            # Layout
            layout = QtWidgets.QVBoxLayout(dialog)

            # Icon and title
            title_layout = QtWidgets.QHBoxLayout()

            # Add icon if available
            icon_label = QtWidgets.QLabel()
            icon_label.setPixmap(QtGui.QPixmap(":/icons/CalcsLive_Connect.svg").scaled(32, 32))
            title_layout.addWidget(icon_label)

            title_label = QtWidgets.QLabel("Connect to CalcsLive")
            title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
            title_layout.addWidget(title_label)
            title_layout.addStretch()

            layout.addLayout(title_layout)

            # Instructions
            instructions = QtWidgets.QLabel(
                "The CalcsLive connection page has been opened in your web browser.\n\n"
                "Follow these steps:\n"
                "1. Configure your API key (if needed)\n"
                "2. Select or create a calculation article\n"
                "3. Test the connection\n"
                "4. Return to FreeCAD and use the Dashboard command"
            )
            instructions.setWordWrap(True)
            layout.addWidget(instructions)

            # URL display
            url_group = QtWidgets.QGroupBox("Connection URL")
            url_layout = QtWidgets.QVBoxLayout(url_group)

            url_text = QtWidgets.QLineEdit(connect_url)
            url_text.setReadOnly(True)
            url_layout.addWidget(url_text)

            copy_button = QtWidgets.QPushButton("Copy URL")
            copy_button.clicked.connect(lambda: QtWidgets.QApplication.clipboard().setText(connect_url))
            url_layout.addWidget(copy_button)

            layout.addWidget(url_group)

            # Buttons
            button_layout = QtWidgets.QHBoxLayout()

            open_button = QtWidgets.QPushButton("Open in Browser")
            open_button.clicked.connect(lambda: BrowserLauncher().open_url(connect_url))
            button_layout.addWidget(open_button)

            button_layout.addStretch()

            close_button = QtWidgets.QPushButton("Close")
            close_button.clicked.connect(dialog.accept)
            button_layout.addWidget(close_button)

            layout.addLayout(button_layout)

            # Show dialog
            dialog.exec_()

        except Exception as e:
            FreeCAD.Console.PrintWarning(f"Could not show connection dialog: {e}\n")
            self._show_url_dialog(connect_url)

    def _show_url_dialog(self, connect_url):
        """Show simple URL dialog as fallback"""
        try:
            from PySide2 import QtWidgets

            QtWidgets.QMessageBox.information(
                None,
                "CalcsLive Connection",
                f"Please open this URL in your web browser to connect:\n\n{connect_url}\n\n"
                "The URL has been copied to your clipboard."
            )

            # Copy URL to clipboard
            QtWidgets.QApplication.clipboard().setText(connect_url)

        except Exception as e:
            FreeCAD.Console.PrintMessage(f"CalcsLive connection URL: {connect_url}\n")

    def _show_error_dialog(self, error_message):
        """Show error dialog"""
        try:
            from PySide2 import QtWidgets

            QtWidgets.QMessageBox.critical(
                None,
                "CalcsLive Connection Error",
                f"Failed to establish CalcsLive connection:\n\n{error_message}\n\n"
                "Please check your internet connection and try again."
            )

        except Exception:
            FreeCAD.Console.PrintError(f"CalcsLive connection error: {error_message}\n")


# Register command
FreeCADGui.addCommand('CalcsLive_Connect', ConnectCommand())