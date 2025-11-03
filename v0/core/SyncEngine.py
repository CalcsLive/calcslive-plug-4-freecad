"""
CalcsLive Sync Engine

Orchestrates bi-directional synchronization between FreeCAD and CalcsLive.
Manages parameter extraction, calculation requests, and model updates.
"""

import json
import time
from typing import Dict, Any, List, Optional, Callable
import threading

from .CalcsLiveClient import CalcsLiveClient, CalcsLiveError
from .ParameterExtractor import ParameterExtractor
from .ModelUpdater import ModelUpdater
from .ConfigManager import ConfigManager


class SyncEngine:
    """
    Bi-directional synchronization engine between FreeCAD and CalcsLive

    Coordinates parameter extraction from FreeCAD, sends to CalcsLive for calculation,
    and updates FreeCAD model with results.
    """

    def __init__(self):
        """Initialize sync engine"""
        self.config_manager = ConfigManager()
        self.client = None
        self.extractor = ParameterExtractor()
        self.updater = ModelUpdater()

        # Sync state
        self.is_syncing = False
        self.last_sync_time = None
        self.sync_history = []
        self.error_count = 0

        # Callbacks for UI updates
        self.sync_callbacks = {
            'on_sync_start': [],
            'on_sync_progress': [],
            'on_sync_complete': [],
            'on_sync_error': []
        }

        # Auto-sync settings
        self.auto_sync_enabled = False
        self.auto_sync_interval = 5  # seconds
        self.auto_sync_thread = None

    def initialize(self, api_key: Optional[str] = None) -> bool:
        """
        Initialize sync engine with CalcsLive connection

        Args:
            api_key: CalcsLive API key (optional, will try config if not provided)

        Returns:
            True if initialization successful
        """
        try:
            # Use provided API key or get from config
            if not api_key:
                api_key = self.config_manager.get_api_key()

            # Create CalcsLive client
            self.client = CalcsLiveClient(api_key)

            # Test connection
            if self.client.test_connection():
                print("CalcsLive Sync Engine: Initialized successfully")
                return True
            else:
                print("CalcsLive Sync Engine: Connection test failed")
                return False

        except Exception as e:
            print(f"CalcsLive Sync Engine: Initialization failed: {e}")
            return False

    def sync_with_calcslive(self, article_id: str, sync_options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Perform complete sync with CalcsLive article

        Args:
            article_id: CalcsLive article ID
            sync_options: Optional sync configuration

        Returns:
            Dict with sync results and statistics
        """
        if not self.client:
            raise CalcsLiveError("Sync engine not initialized")

        if self.is_syncing:
            return {'success': False, 'error': 'Sync already in progress'}

        sync_options = sync_options or {}
        self.is_syncing = True

        try:
            # Notify sync start
            self._notify_callbacks('on_sync_start', {'article_id': article_id})

            sync_result = {
                'success': False,
                'article_id': article_id,
                'timestamp': time.time(),
                'steps': {},
                'statistics': {},
                'errors': []
            }

            # Step 1: Validate article
            self._notify_callbacks('on_sync_progress', {'step': 'validate', 'progress': 10})
            try:
                article_info = self.client.validate_article(article_id)
                sync_result['steps']['validate'] = {'success': True, 'data': article_info}
            except Exception as e:
                sync_result['steps']['validate'] = {'success': False, 'error': str(e)}
                sync_result['errors'].append(f"Article validation failed: {e}")
                return sync_result

            # Step 2: Extract FreeCAD parameters
            self._notify_callbacks('on_sync_progress', {'step': 'extract', 'progress': 30})
            try:
                extracted_params = self.extractor.extract_document_parameters()
                sync_result['steps']['extract'] = {
                    'success': True,
                    'parameter_count': len(extracted_params)
                }
                sync_result['statistics']['extracted_parameters'] = len(extracted_params)
            except Exception as e:
                sync_result['steps']['extract'] = {'success': False, 'error': str(e)}
                sync_result['errors'].append(f"Parameter extraction failed: {e}")
                return sync_result

            # Step 3: Send to CalcsLive for calculation
            self._notify_callbacks('on_sync_progress', {'step': 'calculate', 'progress': 60})
            try:
                # Format parameters for CalcsLive
                calcslive_inputs = self.extractor.format_for_calcslive(extracted_params)

                # Get calculation results
                calculation_results = self.client.get_calculation_results(
                    article_id,
                    calcslive_inputs,
                    sync_options.get('output_units')
                )

                sync_result['steps']['calculate'] = {
                    'success': True,
                    'input_count': len(calcslive_inputs),
                    'output_count': len(calculation_results.get('outputs', {}))
                }
                sync_result['statistics']['calculation_outputs'] = len(calculation_results.get('outputs', {}))

            except Exception as e:
                sync_result['steps']['calculate'] = {'success': False, 'error': str(e)}
                sync_result['errors'].append(f"CalcsLive calculation failed: {e}")
                return sync_result

            # Step 4: Update FreeCAD model (if enabled)
            if sync_options.get('update_model', True):
                self._notify_callbacks('on_sync_progress', {'step': 'update', 'progress': 80})
                try:
                    # Create or use provided parameter mapping
                    parameter_mapping = sync_options.get('parameter_mapping')
                    if not parameter_mapping:
                        calcslive_outputs = list(calculation_results.get('outputs', {}).keys())
                        parameter_mapping = self.updater.create_parameter_mapping(
                            extracted_params,
                            calcslive_outputs
                        )

                    # Update model
                    update_stats = self.updater.update_model_from_calcslive(
                        calculation_results,
                        parameter_mapping
                    )

                    sync_result['steps']['update'] = {
                        'success': update_stats['failed_updates'] == 0,
                        'statistics': update_stats
                    }
                    sync_result['statistics'].update(update_stats)

                except Exception as e:
                    sync_result['steps']['update'] = {'success': False, 'error': str(e)}
                    sync_result['errors'].append(f"Model update failed: {e}")

            # Complete
            self._notify_callbacks('on_sync_progress', {'step': 'complete', 'progress': 100})
            sync_result['success'] = len(sync_result['errors']) == 0
            sync_result['duration'] = time.time() - sync_result['timestamp']

            # Update sync history
            self.last_sync_time = sync_result['timestamp']
            self.sync_history.append(sync_result)

            # Keep only last 10 sync results
            if len(self.sync_history) > 10:
                self.sync_history = self.sync_history[-10:]

            return sync_result

        except Exception as e:
            sync_result = {
                'success': False,
                'article_id': article_id,
                'timestamp': time.time(),
                'error': str(e),
                'errors': [str(e)]
            }
            return sync_result

        finally:
            self.is_syncing = False
            self._notify_callbacks('on_sync_complete', sync_result)

    def sync_selection_with_calcslive(self, article_id: str, sync_options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Sync only selected FreeCAD objects with CalcsLive

        Args:
            article_id: CalcsLive article ID
            sync_options: Optional sync configuration

        Returns:
            Dict with sync results
        """
        # Extract parameters from selection only
        try:
            selected_params = self.extractor.get_selected_parameters()
            if not selected_params:
                return {
                    'success': False,
                    'error': 'No parameters found in selected objects'
                }

            # Override extraction step to use selection
            modified_options = (sync_options or {}).copy()
            modified_options['_use_selection'] = True
            modified_options['_selected_params'] = selected_params

            return self.sync_with_calcslive(article_id, modified_options)

        except Exception as e:
            return {
                'success': False,
                'error': f"Selection sync failed: {str(e)}"
            }

    def validate_sync_readiness(self, article_id: str) -> Dict[str, Any]:
        """
        Validate that sync is ready to proceed

        Args:
            article_id: CalcsLive article ID

        Returns:
            Dict with validation results
        """
        validation = {
            'ready': False,
            'checks': {},
            'warnings': [],
            'errors': []
        }

        # Check 1: Engine initialized
        validation['checks']['engine_initialized'] = self.client is not None
        if not self.client:
            validation['errors'].append("Sync engine not initialized")

        # Check 2: Article accessible
        if self.client:
            try:
                article_info = self.client.validate_article(article_id)
                validation['checks']['article_accessible'] = True
                validation['article_info'] = article_info
            except Exception as e:
                validation['checks']['article_accessible'] = False
                validation['errors'].append(f"Article not accessible: {e}")

        # Check 3: FreeCAD document available
        import FreeCAD
        doc = FreeCAD.ActiveDocument
        validation['checks']['document_available'] = doc is not None
        if not doc:
            validation['errors'].append("No active FreeCAD document")

        # Check 4: Parameters available
        if doc:
            try:
                params = self.extractor.extract_document_parameters(doc)
                validation['checks']['parameters_available'] = len(params) > 0
                validation['parameter_count'] = len(params)

                if len(params) == 0:
                    validation['warnings'].append("No extractable parameters found in document")

            except Exception as e:
                validation['checks']['parameters_available'] = False
                validation['errors'].append(f"Parameter extraction failed: {e}")

        # Overall readiness
        validation['ready'] = all(validation['checks'].values()) and len(validation['errors']) == 0

        return validation

    def enable_auto_sync(self, article_id: str, interval: int = 5):
        """
        Enable automatic synchronization

        Args:
            article_id: CalcsLive article ID to sync with
            interval: Sync interval in seconds
        """
        if self.auto_sync_enabled:
            self.disable_auto_sync()

        self.auto_sync_enabled = True
        self.auto_sync_interval = interval

        def auto_sync_worker():
            while self.auto_sync_enabled:
                try:
                    if not self.is_syncing:
                        sync_result = self.sync_with_calcslive(article_id, {'update_model': True})
                        if not sync_result['success']:
                            self.error_count += 1
                            if self.error_count >= 3:  # Stop after 3 consecutive errors
                                print("CalcsLive Auto-sync: Stopping due to repeated errors")
                                self.disable_auto_sync()
                                break
                        else:
                            self.error_count = 0

                    time.sleep(self.auto_sync_interval)

                except Exception as e:
                    print(f"CalcsLive Auto-sync error: {e}")
                    self.error_count += 1
                    if self.error_count >= 3:
                        self.disable_auto_sync()
                        break
                    time.sleep(self.auto_sync_interval)

        self.auto_sync_thread = threading.Thread(target=auto_sync_worker, daemon=True)
        self.auto_sync_thread.start()

        print(f"CalcsLive Auto-sync: Enabled (interval: {interval}s)")

    def disable_auto_sync(self):
        """Disable automatic synchronization"""
        self.auto_sync_enabled = False
        if self.auto_sync_thread and self.auto_sync_thread.is_alive():
            self.auto_sync_thread.join(timeout=1)
        print("CalcsLive Auto-sync: Disabled")

    def get_sync_status(self) -> Dict[str, Any]:
        """Get current sync engine status"""
        return {
            'initialized': self.client is not None,
            'is_syncing': self.is_syncing,
            'auto_sync_enabled': self.auto_sync_enabled,
            'auto_sync_interval': self.auto_sync_interval,
            'last_sync_time': self.last_sync_time,
            'sync_count': len(self.sync_history),
            'error_count': self.error_count
        }

    def get_sync_history(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get recent sync history"""
        return self.sync_history[-limit:] if self.sync_history else []

    def register_sync_callback(self, event: str, callback: Callable):
        """
        Register callback for sync events

        Args:
            event: Event name ('on_sync_start', 'on_sync_progress', 'on_sync_complete', 'on_sync_error')
            callback: Callback function
        """
        if event in self.sync_callbacks:
            self.sync_callbacks[event].append(callback)

    def unregister_sync_callback(self, event: str, callback: Callable):
        """Unregister sync callback"""
        if event in self.sync_callbacks and callback in self.sync_callbacks[event]:
            self.sync_callbacks[event].remove(callback)

    def _notify_callbacks(self, event: str, data: Dict[str, Any]):
        """Notify registered callbacks of sync event"""
        for callback in self.sync_callbacks.get(event, []):
            try:
                callback(data)
            except Exception as e:
                print(f"CalcsLive Sync callback error ({event}): {e}")

    def create_sync_report(self, sync_result: Dict[str, Any]) -> str:
        """Generate human-readable sync report"""
        if not sync_result:
            return "No sync result available"

        lines = [
            "CalcsLive Sync Report",
            "=" * 20,
            f"Article ID: {sync_result.get('article_id', 'Unknown')}",
            f"Status: {'Success' if sync_result.get('success') else 'Failed'}",
            f"Duration: {sync_result.get('duration', 0):.2f} seconds"
        ]

        # Add step details
        steps = sync_result.get('steps', {})
        if steps:
            lines.append("\nSteps:")
            for step_name, step_info in steps.items():
                status = "✓" if step_info.get('success') else "✗"
                lines.append(f"  {status} {step_name.title()}")

        # Add statistics
        stats = sync_result.get('statistics', {})
        if stats:
            lines.append("\nStatistics:")
            for key, value in stats.items():
                if isinstance(value, (int, float)):
                    lines.append(f"  {key.replace('_', ' ').title()}: {value}")

        # Add errors
        errors = sync_result.get('errors', [])
        if errors:
            lines.append("\nErrors:")
            for error in errors:
                lines.append(f"  - {error}")

        return '\n'.join(lines)

    def export_sync_history(self, filename: str) -> bool:
        """Export sync history to JSON file"""
        try:
            with open(filename, 'w') as f:
                json.dump(self.sync_history, f, indent=2, default=str)
            return True
        except Exception as e:
            print(f"Failed to export sync history: {e}")
            return False


# Global sync engine instance
_sync_engine = None


def get_sync_engine() -> SyncEngine:
    """Get global sync engine instance"""
    global _sync_engine
    if _sync_engine is None:
        _sync_engine = SyncEngine()
    return _sync_engine


def sync_with_calcslive(article_id: str, sync_options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Convenience function for complete sync"""
    engine = get_sync_engine()
    return engine.sync_with_calcslive(article_id, sync_options)


def sync_selection_with_calcslive(article_id: str, sync_options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Convenience function for selection sync"""
    engine = get_sync_engine()
    return engine.sync_selection_with_calcslive(article_id, sync_options)