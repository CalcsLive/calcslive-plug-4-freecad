"""
CalcsLive FreeCAD Workbench

Bi-directional integration between FreeCAD parametric models and CalcsLive unit-aware calculations.

This workbench provides minimal UI in FreeCAD while leveraging CalcsLive's modern web interface
for 80% of the user interaction through professional parameter mapping and live sync dashboards.

Author: CalcsLive Team
License: MIT
Version: 1.0.0
"""

__version__ = "1.0.0"
__author__ = "CalcsLive Team"
__url__ = "https://github.com/CalcsLive/calcslive-plug-4-freecad"

# Workbench identification
WORKBENCH_NAME = "CalcsLive"
WORKBENCH_TOOLTIP = "CalcsLive Integration"

# CalcsLive API configuration
CALCSLIVE_BASE_URL = "https://www.calcs.live"
CALCSLIVE_API_ENDPOINTS = {
    'calculate': f"{CALCSLIVE_BASE_URL}/api/n8n/v1/calculate",
    'validate': f"{CALCSLIVE_BASE_URL}/api/n8n/v1/validate",
    'freecad_connect': f"{CALCSLIVE_BASE_URL}/freecad/connect",
    'freecad_dashboard': f"{CALCSLIVE_BASE_URL}/freecad/{{article_id}}/dashboard"
}

# Import core modules to ensure they're available
try:
    from .core.CalcsLiveClient import CalcsLiveClient
    from .core.ParameterExtractor import ParameterExtractor
    from .core.ModelUpdater import ModelUpdater
    from .core.SyncEngine import SyncEngine
    from .core.ConfigManager import ConfigManager

    print("CalcsLive Workbench: Core modules loaded successfully")
except ImportError as e:
    print(f"CalcsLive Workbench: Warning - Core module import failed: {e}")

# Import UI modules (optional, may not be available in headless mode)
try:
    from .ui.ConnectionPanel import ConnectionPanel
    from .ui.StatusWidget import StatusWidget
    from .ui.QuickActions import QuickActions

    print("CalcsLive Workbench: UI modules loaded successfully")
except ImportError as e:
    print(f"CalcsLive Workbench: Warning - UI module import failed: {e}")

# Import utilities
try:
    from .utils.PropertyMapper import PropertyMapper
    from .utils.UnitConverter import UnitConverter
    from .utils.ErrorHandler import ErrorHandler
    from .utils.BrowserLauncher import BrowserLauncher

    print("CalcsLive Workbench: Utility modules loaded successfully")
except ImportError as e:
    print(f"CalcsLive Workbench: Warning - Utility module import failed: {e}")

def get_workbench_info():
    """Get workbench information dictionary."""
    return {
        'name': WORKBENCH_NAME,
        'tooltip': WORKBENCH_TOOLTIP,
        'version': __version__,
        'author': __author__,
        'url': __url__,
        'description': 'Bi-directional integration between FreeCAD and CalcsLive'
    }

def get_api_endpoints():
    """Get CalcsLive API endpoints."""
    return CALCSLIVE_API_ENDPOINTS.copy()

# Module exports
__all__ = [
    'WORKBENCH_NAME',
    'WORKBENCH_TOOLTIP',
    'CALCSLIVE_BASE_URL',
    'CALCSLIVE_API_ENDPOINTS',
    'get_workbench_info',
    'get_api_endpoints'
]