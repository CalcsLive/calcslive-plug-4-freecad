"""
Browser Launcher Utility

Cross-platform browser launching for CalcsLive web interfaces.
Handles different operating systems and browser preferences.
"""

import os
import sys
import subprocess
import webbrowser
from typing import Optional
import FreeCAD


class BrowserLauncher:
    """
    Cross-platform browser launcher for CalcsLive web interfaces

    Provides reliable browser launching across Windows, macOS, and Linux
    with fallback mechanisms and user preferences.
    """

    def __init__(self):
        """Initialize browser launcher"""
        self.platform = sys.platform
        self.preferred_browsers = self._get_preferred_browsers()

    def open_url(self, url: str, browser: Optional[str] = None) -> bool:
        """
        Open URL in web browser

        Args:
            url: URL to open
            browser: Specific browser to use (optional)

        Returns:
            True if URL was opened successfully
        """
        try:
            FreeCAD.Console.PrintMessage(f"CalcsLive: Opening URL in browser: {url}\n")

            # Try specific browser first
            if browser:
                success = self._open_with_browser(url, browser)
                if success:
                    return True

            # Try preferred browsers
            for browser_name in self.preferred_browsers:
                success = self._open_with_browser(url, browser_name)
                if success:
                    return True

            # Fallback to system default
            return self._open_with_system_default(url)

        except Exception as e:
            FreeCAD.Console.PrintError(f"CalcsLive: Failed to open URL in browser: {e}\n")
            return False

    def _get_preferred_browsers(self):
        """Get list of preferred browsers for current platform"""

        if self.platform.startswith('win'):
            # Windows
            return ['chrome', 'firefox', 'edge', 'iexplore']

        elif self.platform == 'darwin':
            # macOS
            return ['chrome', 'firefox', 'safari']

        else:
            # Linux and others
            return ['chrome', 'firefox', 'chromium', 'opera']

    def _open_with_browser(self, url: str, browser_name: str) -> bool:
        """Try to open URL with specific browser"""

        try:
            # Browser executable mappings
            browser_executables = {
                'chrome': self._get_chrome_executable(),
                'firefox': self._get_firefox_executable(),
                'edge': self._get_edge_executable(),
                'safari': 'safari',
                'iexplore': 'iexplore',
                'chromium': 'chromium-browser',
                'opera': 'opera'
            }

            executable = browser_executables.get(browser_name.lower())
            if not executable:
                return False

            # Try to launch browser directly
            if self.platform.startswith('win'):
                # Windows
                subprocess.Popen([executable, url], shell=True)
                return True

            elif self.platform == 'darwin':
                # macOS
                if browser_name.lower() == 'safari':
                    subprocess.Popen(['open', '-a', 'Safari', url])
                else:
                    subprocess.Popen(['open', '-a', executable, url])
                return True

            else:
                # Linux
                subprocess.Popen([executable, url])
                return True

        except Exception:
            return False

    def _open_with_system_default(self, url: str) -> bool:
        """Open URL with system default browser"""

        try:
            # Use Python's webbrowser module as fallback
            webbrowser.open(url)
            return True

        except Exception as e:
            FreeCAD.Console.PrintWarning(f"CalcsLive: System default browser failed: {e}\n")

            # Ultimate fallback - try OS-specific commands
            try:
                if self.platform.startswith('win'):
                    os.startfile(url)
                elif self.platform == 'darwin':
                    subprocess.Popen(['open', url])
                else:
                    subprocess.Popen(['xdg-open', url])
                return True

            except Exception:
                return False

    def _get_chrome_executable(self) -> Optional[str]:
        """Get Chrome executable path for current platform"""

        if self.platform.startswith('win'):
            # Windows Chrome locations
            chrome_paths = [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe")
            ]

            for path in chrome_paths:
                if os.path.exists(path):
                    return path

        elif self.platform == 'darwin':
            # macOS Chrome
            chrome_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
            if os.path.exists(chrome_path):
                return "Google Chrome"

        else:
            # Linux Chrome
            chrome_commands = ['google-chrome', 'chrome', 'chromium-browser']
            for cmd in chrome_commands:
                if self._command_exists(cmd):
                    return cmd

        return None

    def _get_firefox_executable(self) -> Optional[str]:
        """Get Firefox executable path for current platform"""

        if self.platform.startswith('win'):
            # Windows Firefox locations
            firefox_paths = [
                r"C:\Program Files\Mozilla Firefox\firefox.exe",
                r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe"
            ]

            for path in firefox_paths:
                if os.path.exists(path):
                    return path

        elif self.platform == 'darwin':
            # macOS Firefox
            firefox_path = "/Applications/Firefox.app/Contents/MacOS/firefox"
            if os.path.exists(firefox_path):
                return "Firefox"

        else:
            # Linux Firefox
            if self._command_exists('firefox'):
                return 'firefox'

        return None

    def _get_edge_executable(self) -> Optional[str]:
        """Get Microsoft Edge executable path"""

        if self.platform.startswith('win'):
            # Windows Edge locations
            edge_paths = [
                r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
                r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"
            ]

            for path in edge_paths:
                if os.path.exists(path):
                    return path

        elif self.platform == 'darwin':
            # macOS Edge
            edge_path = "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"
            if os.path.exists(edge_path):
                return "Microsoft Edge"

        return None

    def _command_exists(self, command: str) -> bool:
        """Check if command exists in system PATH"""

        try:
            subprocess.check_output(['which', command], stderr=subprocess.STDOUT)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def get_available_browsers(self):
        """Get list of available browsers on current system"""

        available = []

        for browser in self.preferred_browsers:
            if browser == 'chrome' and self._get_chrome_executable():
                available.append('chrome')
            elif browser == 'firefox' and self._get_firefox_executable():
                available.append('firefox')
            elif browser == 'edge' and self._get_edge_executable():
                available.append('edge')
            elif browser in ['safari', 'iexplore', 'chromium', 'opera']:
                # Basic availability check for other browsers
                if self.platform == 'darwin' and browser == 'safari':
                    available.append('safari')
                elif self.platform.startswith('win') and browser == 'iexplore':
                    available.append('iexplore')
                elif browser in ['chromium', 'opera'] and self._command_exists(browser):
                    available.append(browser)

        return available

    def set_preferred_browser(self, browser: str):
        """Set preferred browser (moves it to front of list)"""

        if browser in self.preferred_browsers:
            self.preferred_browsers.remove(browser)

        self.preferred_browsers.insert(0, browser)

    def open_calcslive_connect(self, api_key: Optional[str] = None, model_id: Optional[str] = None) -> bool:
        """
        Open CalcsLive connection page with parameters

        Args:
            api_key: CalcsLive API key
            model_id: FreeCAD model identifier

        Returns:
            True if opened successfully
        """

        try:
            from ..core.CalcsLiveClient import CalcsLiveClient

            client = CalcsLiveClient(api_key)
            connect_url = client.get_freecad_connect_url(model_id)

            return self.open_url(connect_url)

        except Exception as e:
            FreeCAD.Console.PrintError(f"CalcsLive: Failed to open connect page: {e}\n")
            return False

    def open_calcslive_dashboard(self, article_id: str, api_key: Optional[str] = None,
                               model_id: Optional[str] = None) -> bool:
        """
        Open CalcsLive dashboard for article

        Args:
            article_id: CalcsLive article ID
            api_key: CalcsLive API key
            model_id: FreeCAD model identifier

        Returns:
            True if opened successfully
        """

        try:
            from ..core.CalcsLiveClient import CalcsLiveClient

            client = CalcsLiveClient(api_key)
            dashboard_url = client.get_dashboard_url(article_id, model_id)

            return self.open_url(dashboard_url)

        except Exception as e:
            FreeCAD.Console.PrintError(f"CalcsLive: Failed to open dashboard: {e}\n")
            return False


# Global browser launcher instance
_browser_launcher = None


def get_browser_launcher() -> BrowserLauncher:
    """Get global browser launcher instance"""
    global _browser_launcher
    if _browser_launcher is None:
        _browser_launcher = BrowserLauncher()
    return _browser_launcher


def open_url(url: str, browser: Optional[str] = None) -> bool:
    """Convenience function to open URL"""
    launcher = get_browser_launcher()
    return launcher.open_url(url, browser)


def open_calcslive_connect(api_key: Optional[str] = None, model_id: Optional[str] = None) -> bool:
    """Convenience function to open CalcsLive connect page"""
    launcher = get_browser_launcher()
    return launcher.open_calcslive_connect(api_key, model_id)


def open_calcslive_dashboard(article_id: str, api_key: Optional[str] = None,
                           model_id: Optional[str] = None) -> bool:
    """Convenience function to open CalcsLive dashboard"""
    launcher = get_browser_launcher()
    return launcher.open_calcslive_dashboard(article_id, api_key, model_id)