"""
Error Handler Utility

Centralized error handling and user feedback for CalcsLive workbench.
Provides consistent error reporting across the application.
"""

import FreeCAD
import traceback
from typing import Optional, Dict, Any
import time


class ErrorHandler:
    """
    Centralized error handling for CalcsLive workbench

    Provides consistent error reporting, logging, and user feedback
    across all workbench components.
    """

    def __init__(self):
        """Initialize error handler"""
        self.error_history = []
        self.max_history = 50

    def handle_error(self, error: Exception, context: str = "",
                    show_dialog: bool = True, log_to_console: bool = True) -> Dict[str, Any]:
        """
        Handle error with logging and optional user notification

        Args:
            error: Exception object
            context: Context description where error occurred
            show_dialog: Whether to show error dialog to user
            log_to_console: Whether to log to FreeCAD console

        Returns:
            Dict with error information
        """

        error_info = {
            'timestamp': time.time(),
            'context': context,
            'error_type': type(error).__name__,
            'error_message': str(error),
            'traceback': traceback.format_exc(),
            'formatted_time': time.strftime('%Y-%m-%d %H:%M:%S')
        }

        # Add to history
        self.error_history.append(error_info)
        if len(self.error_history) > self.max_history:
            self.error_history = self.error_history[-self.max_history:]

        # Console logging
        if log_to_console:
            self._log_to_console(error_info)

        # User notification
        if show_dialog:
            self._show_error_dialog(error_info)

        return error_info

    def handle_warning(self, message: str, context: str = "",
                      show_dialog: bool = False, log_to_console: bool = True):
        """
        Handle warning message

        Args:
            message: Warning message
            context: Context description
            show_dialog: Whether to show warning dialog
            log_to_console: Whether to log to console
        """

        warning_info = {
            'timestamp': time.time(),
            'context': context,
            'message': message,
            'type': 'warning'
        }

        if log_to_console:
            if context:
                FreeCAD.Console.PrintWarning(f"CalcsLive {context}: {message}\n")
            else:
                FreeCAD.Console.PrintWarning(f"CalcsLive: {message}\n")

        if show_dialog:
            self._show_warning_dialog(message, context)

    def handle_info(self, message: str, context: str = "",
                   show_dialog: bool = False, log_to_console: bool = True):
        """
        Handle informational message

        Args:
            message: Info message
            context: Context description
            show_dialog: Whether to show info dialog
            log_to_console: Whether to log to console
        """

        if log_to_console:
            if context:
                FreeCAD.Console.PrintMessage(f"CalcsLive {context}: {message}\n")
            else:
                FreeCAD.Console.PrintMessage(f"CalcsLive: {message}\n")

        if show_dialog:
            self._show_info_dialog(message, context)

    def _log_to_console(self, error_info: Dict[str, Any]):
        """Log error information to FreeCAD console"""

        context = error_info.get('context', '')
        error_type = error_info.get('error_type', 'Error')
        error_message = error_info.get('error_message', 'Unknown error')

        if context:
            FreeCAD.Console.PrintError(f"CalcsLive {context}: {error_type} - {error_message}\n")
        else:
            FreeCAD.Console.PrintError(f"CalcsLive: {error_type} - {error_message}\n")

        # Print traceback for debugging
        traceback_str = error_info.get('traceback', '')
        if traceback_str:
            FreeCAD.Console.PrintLog(f"CalcsLive traceback:\n{traceback_str}\n")

    def _show_error_dialog(self, error_info: Dict[str, Any]):
        """Show error dialog to user"""

        try:
            from PySide2 import QtWidgets

            context = error_info.get('context', '')
            error_type = error_info.get('error_type', 'Error')
            error_message = error_info.get('error_message', 'Unknown error')

            title = f"CalcsLive {context} Error" if context else "CalcsLive Error"

            message = f"{error_type}: {error_message}"

            # Add context-specific guidance
            guidance = self._get_error_guidance(error_info)
            if guidance:
                message += f"\n\nSuggestion: {guidance}"

            QtWidgets.QMessageBox.critical(
                None,
                title,
                message
            )

        except Exception:
            # Fallback if Qt dialogs not available
            FreeCAD.Console.PrintError(f"CalcsLive: Failed to show error dialog\n")

    def _show_warning_dialog(self, message: str, context: str = ""):
        """Show warning dialog to user"""

        try:
            from PySide2 import QtWidgets

            title = f"CalcsLive {context} Warning" if context else "CalcsLive Warning"

            QtWidgets.QMessageBox.warning(
                None,
                title,
                message
            )

        except Exception:
            # Fallback
            FreeCAD.Console.PrintWarning(f"CalcsLive: Failed to show warning dialog\n")

    def _show_info_dialog(self, message: str, context: str = ""):
        """Show info dialog to user"""

        try:
            from PySide2 import QtWidgets

            title = f"CalcsLive {context}" if context else "CalcsLive"

            QtWidgets.QMessageBox.information(
                None,
                title,
                message
            )

        except Exception:
            # Fallback
            FreeCAD.Console.PrintMessage(f"CalcsLive: Failed to show info dialog\n")

    def _get_error_guidance(self, error_info: Dict[str, Any]) -> Optional[str]:
        """Get context-specific error guidance"""

        error_type = error_info.get('error_type', '')
        error_message = error_info.get('error_message', '').lower()
        context = error_info.get('context', '').lower()

        # Connection errors
        if 'connection' in context or 'urlopen' in error_type.lower():
            return "Check your internet connection and API key configuration."

        # API key errors
        if 'unauthorized' in error_message or 'api key' in error_message:
            return "Please verify your CalcsLive API key in the configuration."

        # Article errors
        if 'article' in error_message or 'not found' in error_message:
            return "Please check that the article ID is correct and accessible."

        # Parameter errors
        if 'parameter' in context:
            return "Ensure your FreeCAD model has extractable parameters with units."

        # Sync errors
        if 'sync' in context:
            return "Try refreshing the connection or checking the article configuration."

        # File/config errors
        if 'file' in error_message or 'config' in context:
            return "Check file permissions and configuration settings."

        return None

    def get_error_history(self, limit: int = 10) -> list:
        """Get recent error history"""
        return self.error_history[-limit:] if self.error_history else []

    def clear_error_history(self):
        """Clear error history"""
        self.error_history.clear()

    def get_error_summary(self) -> Dict[str, Any]:
        """Get error statistics summary"""

        if not self.error_history:
            return {
                'total_errors': 0,
                'recent_errors': 0,
                'common_contexts': [],
                'common_types': []
            }

        # Count errors by context and type
        context_counts = {}
        type_counts = {}
        recent_count = 0
        recent_threshold = time.time() - 3600  # Last hour

        for error in self.error_history:
            # Context counting
            context = error.get('context', 'unknown')
            context_counts[context] = context_counts.get(context, 0) + 1

            # Type counting
            error_type = error.get('error_type', 'unknown')
            type_counts[error_type] = type_counts.get(error_type, 0) + 1

            # Recent errors
            if error.get('timestamp', 0) > recent_threshold:
                recent_count += 1

        # Sort by frequency
        common_contexts = sorted(context_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        common_types = sorted(type_counts.items(), key=lambda x: x[1], reverse=True)[:5]

        return {
            'total_errors': len(self.error_history),
            'recent_errors': recent_count,
            'common_contexts': common_contexts,
            'common_types': common_types
        }

    def export_error_log(self, filename: str) -> bool:
        """Export error history to file"""

        try:
            import json

            export_data = {
                'export_time': time.strftime('%Y-%m-%d %H:%M:%S'),
                'error_count': len(self.error_history),
                'errors': self.error_history
            }

            with open(filename, 'w') as f:
                json.dump(export_data, f, indent=2, default=str)

            return True

        except Exception as e:
            FreeCAD.Console.PrintError(f"CalcsLive: Failed to export error log: {e}\n")
            return False

    def create_error_report(self, error_info: Dict[str, Any]) -> str:
        """Create formatted error report"""

        lines = [
            "CalcsLive Error Report",
            "=" * 25,
            f"Time: {error_info.get('formatted_time', 'Unknown')}",
            f"Context: {error_info.get('context', 'Unknown')}",
            f"Error Type: {error_info.get('error_type', 'Unknown')}",
            f"Message: {error_info.get('error_message', 'Unknown')}",
            "",
            "Traceback:",
            error_info.get('traceback', 'No traceback available')
        ]

        return '\n'.join(lines)


# Context managers for error handling
class ErrorContext:
    """Context manager for consistent error handling"""

    def __init__(self, handler: ErrorHandler, context: str,
                 show_dialog: bool = True, reraise: bool = False):
        self.handler = handler
        self.context = context
        self.show_dialog = show_dialog
        self.reraise = reraise

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.handler.handle_error(
                exc_val,
                self.context,
                show_dialog=self.show_dialog
            )

            if self.reraise:
                return False  # Re-raise the exception

            return True  # Suppress the exception

        return False


# Global error handler instance
_error_handler = None


def get_error_handler() -> ErrorHandler:
    """Get global error handler instance"""
    global _error_handler
    if _error_handler is None:
        _error_handler = ErrorHandler()
    return _error_handler


def handle_error(error: Exception, context: str = "",
                show_dialog: bool = True, log_to_console: bool = True) -> Dict[str, Any]:
    """Convenience function for error handling"""
    handler = get_error_handler()
    return handler.handle_error(error, context, show_dialog, log_to_console)


def handle_warning(message: str, context: str = "",
                  show_dialog: bool = False, log_to_console: bool = True):
    """Convenience function for warning handling"""
    handler = get_error_handler()
    handler.handle_warning(message, context, show_dialog, log_to_console)


def handle_info(message: str, context: str = "",
               show_dialog: bool = False, log_to_console: bool = True):
    """Convenience function for info handling"""
    handler = get_error_handler()
    handler.handle_info(message, context, show_dialog, log_to_console)


def error_context(context: str, show_dialog: bool = True, reraise: bool = False):
    """Convenience function for error context manager"""
    handler = get_error_handler()
    return ErrorContext(handler, context, show_dialog, reraise)