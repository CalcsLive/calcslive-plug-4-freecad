"""
CalcsLive Configuration Manager

Manages CalcsLive workbench configuration including API keys,
connection settings, and user preferences.
"""

import os
import json
import tempfile
from typing import Dict, Any, Optional, List
import FreeCAD


class ConfigManager:
    """
    Manages CalcsLive workbench configuration

    Handles storage and retrieval of API keys, connection settings,
    and user preferences in a secure and persistent manner.
    """

    def __init__(self):
        """Initialize configuration manager"""
        self.config_file = self._get_config_file_path()
        self.config_data = {}
        self.load_config()

    def _get_config_file_path(self) -> str:
        """Get path to configuration file"""

        # Try FreeCAD user data directory first
        try:
            user_data_dir = FreeCAD.getUserAppDataDir()
            config_dir = os.path.join(user_data_dir, 'CalcsLive')

            # Create directory if it doesn't exist
            os.makedirs(config_dir, exist_ok=True)

            return os.path.join(config_dir, 'config.json')

        except Exception:
            # Fallback to temp directory
            temp_dir = tempfile.gettempdir()
            config_dir = os.path.join(temp_dir, 'CalcsLive')
            os.makedirs(config_dir, exist_ok=True)

            return os.path.join(config_dir, 'config.json')

    def load_config(self) -> bool:
        """
        Load configuration from file

        Returns:
            True if loaded successfully
        """
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    self.config_data = json.load(f)
                return True
            else:
                # Initialize with defaults
                self.config_data = self._get_default_config()
                return self.save_config()

        except Exception as e:
            FreeCAD.Console.PrintWarning(f"CalcsLive: Failed to load config: {e}\n")
            self.config_data = self._get_default_config()
            return False

    def save_config(self) -> bool:
        """
        Save configuration to file

        Returns:
            True if saved successfully
        """
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)

            with open(self.config_file, 'w') as f:
                json.dump(self.config_data, f, indent=2)
            return True

        except Exception as e:
            FreeCAD.Console.PrintError(f"CalcsLive: Failed to save config: {e}\n")
            return False

    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            'api_settings': {
                'api_key': '',
                'base_url': 'https://www.calcs.live',
                'timeout': 30,
                'max_retries': 3
            },
            'sync_settings': {
                'auto_sync_enabled': False,
                'auto_sync_interval': 5,
                'update_model_on_sync': True,
                'confirm_updates': True
            },
            'ui_settings': {
                'show_connection_status': True,
                'show_sync_progress': True,
                'open_dashboard_in_browser': True,
                'remember_article_connections': True
            },
            'recent_articles': [],
            'parameter_mappings': {},
            'version': '1.0.0'
        }

    # API Settings
    def get_api_key(self) -> str:
        """Get stored API key"""
        return self.config_data.get('api_settings', {}).get('api_key', '')

    def set_api_key(self, api_key: str) -> bool:
        """
        Set API key

        Args:
            api_key: CalcsLive API key

        Returns:
            True if saved successfully
        """
        if 'api_settings' not in self.config_data:
            self.config_data['api_settings'] = {}

        self.config_data['api_settings']['api_key'] = api_key
        return self.save_config()

    def get_base_url(self) -> str:
        """Get CalcsLive base URL"""
        return self.config_data.get('api_settings', {}).get('base_url', 'https://www.calcs.live')

    def set_base_url(self, base_url: str) -> bool:
        """Set CalcsLive base URL"""
        if 'api_settings' not in self.config_data:
            self.config_data['api_settings'] = {}

        self.config_data['api_settings']['base_url'] = base_url.rstrip('/')
        return self.save_config()

    def get_timeout(self) -> int:
        """Get API timeout in seconds"""
        return self.config_data.get('api_settings', {}).get('timeout', 30)

    def set_timeout(self, timeout: int) -> bool:
        """Set API timeout"""
        if 'api_settings' not in self.config_data:
            self.config_data['api_settings'] = {}

        self.config_data['api_settings']['timeout'] = max(5, min(300, timeout))  # 5-300 seconds
        return self.save_config()

    # Sync Settings
    def is_auto_sync_enabled(self) -> bool:
        """Check if auto-sync is enabled"""
        return self.config_data.get('sync_settings', {}).get('auto_sync_enabled', False)

    def set_auto_sync_enabled(self, enabled: bool) -> bool:
        """Enable/disable auto-sync"""
        if 'sync_settings' not in self.config_data:
            self.config_data['sync_settings'] = {}

        self.config_data['sync_settings']['auto_sync_enabled'] = enabled
        return self.save_config()

    def get_auto_sync_interval(self) -> int:
        """Get auto-sync interval in seconds"""
        return self.config_data.get('sync_settings', {}).get('auto_sync_interval', 5)

    def set_auto_sync_interval(self, interval: int) -> bool:
        """Set auto-sync interval"""
        if 'sync_settings' not in self.config_data:
            self.config_data['sync_settings'] = {}

        self.config_data['sync_settings']['auto_sync_interval'] = max(1, min(3600, interval))  # 1s - 1hr
        return self.save_config()

    def should_update_model_on_sync(self) -> bool:
        """Check if model should be updated on sync"""
        return self.config_data.get('sync_settings', {}).get('update_model_on_sync', True)

    def set_update_model_on_sync(self, update: bool) -> bool:
        """Set whether to update model on sync"""
        if 'sync_settings' not in self.config_data:
            self.config_data['sync_settings'] = {}

        self.config_data['sync_settings']['update_model_on_sync'] = update
        return self.save_config()

    def should_confirm_updates(self) -> bool:
        """Check if updates should be confirmed by user"""
        return self.config_data.get('sync_settings', {}).get('confirm_updates', True)

    def set_confirm_updates(self, confirm: bool) -> bool:
        """Set whether to confirm updates"""
        if 'sync_settings' not in self.config_data:
            self.config_data['sync_settings'] = {}

        self.config_data['sync_settings']['confirm_updates'] = confirm
        return self.save_config()

    # UI Settings
    def should_show_connection_status(self) -> bool:
        """Check if connection status should be shown"""
        return self.config_data.get('ui_settings', {}).get('show_connection_status', True)

    def should_show_sync_progress(self) -> bool:
        """Check if sync progress should be shown"""
        return self.config_data.get('ui_settings', {}).get('show_sync_progress', True)

    def should_open_dashboard_in_browser(self) -> bool:
        """Check if dashboard should open in browser"""
        return self.config_data.get('ui_settings', {}).get('open_dashboard_in_browser', True)

    def set_ui_setting(self, setting: str, value: bool) -> bool:
        """Set UI setting"""
        if 'ui_settings' not in self.config_data:
            self.config_data['ui_settings'] = {}

        self.config_data['ui_settings'][setting] = value
        return self.save_config()

    # Recent Articles
    def get_recent_articles(self) -> List[Dict[str, str]]:
        """Get list of recent articles"""
        return self.config_data.get('recent_articles', [])

    def add_recent_article(self, article_id: str, title: str = '') -> bool:
        """
        Add article to recent list

        Args:
            article_id: CalcsLive article ID
            title: Article title (optional)

        Returns:
            True if saved successfully
        """
        if 'recent_articles' not in self.config_data:
            self.config_data['recent_articles'] = []

        recent = self.config_data['recent_articles']

        # Remove if already exists
        recent = [item for item in recent if item.get('id') != article_id]

        # Add to front
        recent.insert(0, {
            'id': article_id,
            'title': title or article_id,
            'last_used': FreeCAD.now()
        })

        # Keep only last 10
        self.config_data['recent_articles'] = recent[:10]

        return self.save_config()

    def remove_recent_article(self, article_id: str) -> bool:
        """Remove article from recent list"""
        if 'recent_articles' not in self.config_data:
            return True

        self.config_data['recent_articles'] = [
            item for item in self.config_data['recent_articles']
            if item.get('id') != article_id
        ]

        return self.save_config()

    # Parameter Mappings
    def get_parameter_mapping(self, article_id: str) -> Dict[str, Dict[str, str]]:
        """Get saved parameter mapping for article"""
        mappings = self.config_data.get('parameter_mappings', {})
        return mappings.get(article_id, {})

    def save_parameter_mapping(self, article_id: str, mapping: Dict[str, Dict[str, str]]) -> bool:
        """
        Save parameter mapping for article

        Args:
            article_id: CalcsLive article ID
            mapping: Parameter mapping dictionary

        Returns:
            True if saved successfully
        """
        if 'parameter_mappings' not in self.config_data:
            self.config_data['parameter_mappings'] = {}

        self.config_data['parameter_mappings'][article_id] = mapping
        return self.save_config()

    def remove_parameter_mapping(self, article_id: str) -> bool:
        """Remove parameter mapping for article"""
        if 'parameter_mappings' not in self.config_data:
            return True

        if article_id in self.config_data['parameter_mappings']:
            del self.config_data['parameter_mappings'][article_id]

        return self.save_config()

    # General Configuration
    def get_all_settings(self) -> Dict[str, Any]:
        """Get all configuration settings"""
        return self.config_data.copy()

    def reset_to_defaults(self) -> bool:
        """Reset configuration to defaults"""
        self.config_data = self._get_default_config()
        return self.save_config()

    def import_config(self, config_file: str) -> bool:
        """
        Import configuration from file

        Args:
            config_file: Path to configuration file

        Returns:
            True if imported successfully
        """
        try:
            with open(config_file, 'r') as f:
                imported_config = json.load(f)

            # Validate basic structure
            if not isinstance(imported_config, dict):
                return False

            # Merge with defaults to ensure all keys exist
            default_config = self._get_default_config()
            self._merge_config(default_config, imported_config)
            self.config_data = default_config

            return self.save_config()

        except Exception as e:
            FreeCAD.Console.PrintError(f"CalcsLive: Failed to import config: {e}\n")
            return False

    def export_config(self, config_file: str) -> bool:
        """
        Export configuration to file

        Args:
            config_file: Path to save configuration

        Returns:
            True if exported successfully
        """
        try:
            with open(config_file, 'w') as f:
                json.dump(self.config_data, f, indent=2)
            return True

        except Exception as e:
            FreeCAD.Console.PrintError(f"CalcsLive: Failed to export config: {e}\n")
            return False

    def _merge_config(self, base: Dict[str, Any], overlay: Dict[str, Any]):
        """Recursively merge configuration dictionaries"""
        for key, value in overlay.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._merge_config(base[key], value)
            else:
                base[key] = value

    def get_config_file_path(self) -> str:
        """Get path to configuration file"""
        return self.config_file

    def get_config_summary(self) -> str:
        """Get human-readable configuration summary"""
        lines = [
            "CalcsLive Configuration",
            "=" * 25,
            f"Config file: {self.config_file}",
            "",
            "API Settings:",
            f"  API Key: {'Set' if self.get_api_key() else 'Not set'}",
            f"  Base URL: {self.get_base_url()}",
            f"  Timeout: {self.get_timeout()}s",
            "",
            "Sync Settings:",
            f"  Auto-sync: {'Enabled' if self.is_auto_sync_enabled() else 'Disabled'}",
            f"  Sync interval: {self.get_auto_sync_interval()}s",
            f"  Update model: {'Yes' if self.should_update_model_on_sync() else 'No'}",
            f"  Confirm updates: {'Yes' if self.should_confirm_updates() else 'No'}",
            "",
            "Recent Articles:",
            f"  Count: {len(self.get_recent_articles())}",
            "",
            "Parameter Mappings:",
            f"  Saved mappings: {len(self.config_data.get('parameter_mappings', {}))}"
        ]

        return '\n'.join(lines)


# Global config manager instance
_config_manager = None


def get_config_manager() -> ConfigManager:
    """Get global configuration manager instance"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager