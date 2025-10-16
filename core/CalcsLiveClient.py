"""
CalcsLive HTTP Client for FreeCAD Integration

This module provides HTTP client functionality for communicating with CalcsLive APIs.
Adapted from the successful Google Sheets integration architecture.
"""

import json
import time
from typing import Dict, Any, List, Optional, Union
from urllib.request import urlopen, Request, HTTPError, URLError
from urllib.parse import urlencode, quote


class CalcsLiveClient:
    """
    HTTP client for CalcsLive API integration

    Reuses the proven API architecture from Google Sheets integration
    with the same stable n8n endpoints.
    """

    def __init__(self, api_key: Optional[str] = None, base_url: str = "https://www.calcs.live"):
        """
        Initialize CalcsLive client

        Args:
            api_key: CalcsLive API key (optional for public calculations)
            base_url: Base URL for CalcsLive API (default: production)
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')

        # API endpoints (same as Google Sheets integration)
        self.endpoints = {
            'calculate': f"{self.base_url}/api/n8n/v1/calculate",
            'validate': f"{self.base_url}/api/n8n/v1/validate",
            'freecad_connect': f"{self.base_url}/freecad/connect",
            'freecad_dashboard': f"{self.base_url}/freecad/{{article_id}}/dashboard"
        }

        # Request configuration
        self.timeout = 30  # seconds
        self.max_retries = 3
        self.retry_delay = 1  # seconds

    def validate_article(self, article_id: str) -> Dict[str, Any]:
        """
        Validate access to a CalcsLive article and get metadata

        Args:
            article_id: CalcsLive article ID

        Returns:
            Dict containing validation result and metadata

        Raises:
            CalcsLiveError: If validation fails
        """
        params = {'articleId': article_id}
        if self.api_key:
            params['apiKey'] = self.api_key

        url = f"{self.endpoints['validate']}?{urlencode(params)}"

        try:
            response = self._make_request('GET', url)

            if not response.get('success'):
                raise CalcsLiveError(f"Article validation failed: {response.get('error', 'Unknown error')}")

            return response['data']

        except Exception as e:
            raise CalcsLiveError(f"Failed to validate article: {str(e)}")

    def send_parameters(self, article_id: str, parameters: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Send FreeCAD parameters to CalcsLive for calculation

        Args:
            article_id: CalcsLive article ID
            parameters: Dict of parameter_name -> {value, unit}

        Returns:
            Dict containing calculation results

        Example:
            parameters = {
                'beam_length': {'value': 5000, 'unit': 'mm'},
                'load_force': {'value': 10000, 'unit': 'N'}
            }
        """
        payload = {
            'articleId': article_id,
            'inputs': parameters
        }

        if self.api_key:
            payload['apiKey'] = self.api_key

        try:
            response = self._make_request('POST', self.endpoints['calculate'], payload)

            if not response.get('success'):
                raise CalcsLiveError(f"Calculation failed: {response.get('error', 'Unknown error')}")

            return response['data']

        except Exception as e:
            raise CalcsLiveError(f"Failed to send parameters: {str(e)}")

    def get_calculation_results(self, article_id: str, inputs: Dict[str, Dict[str, Any]],
                              outputs: Optional[Dict[str, Dict[str, str]]] = None) -> Dict[str, Any]:
        """
        Get calculation results with optional output unit conversion

        Args:
            article_id: CalcsLive article ID
            inputs: Input parameters {symbol -> {value, unit}}
            outputs: Optional output unit preferences {symbol -> {unit}}

        Returns:
            Dict containing calculation results with requested units
        """
        payload = {
            'articleId': article_id,
            'inputs': inputs
        }

        if outputs:
            payload['outputs'] = outputs

        if self.api_key:
            payload['apiKey'] = self.api_key

        try:
            response = self._make_request('POST', self.endpoints['calculate'], payload)

            if not response.get('success'):
                raise CalcsLiveError(f"Calculation failed: {response.get('error', 'Unknown error')}")

            return response['data']['calculation']

        except Exception as e:
            raise CalcsLiveError(f"Failed to get calculation results: {str(e)}")

    def test_connection(self) -> bool:
        """
        Test connection to CalcsLive API

        Returns:
            True if connection successful, False otherwise
        """
        try:
            # Use a simple validation request to test connection
            test_article = "test"  # This will fail validation but test connectivity

            params = {'articleId': test_article}
            if self.api_key:
                params['apiKey'] = self.api_key

            url = f"{self.endpoints['validate']}?{urlencode(params)}"

            # Don't retry for connection test
            self._make_request('GET', url, retries=1)
            return True

        except Exception:
            return False

    def get_freecad_connect_url(self, model_id: Optional[str] = None) -> str:
        """
        Get URL for FreeCAD connection setup page

        Args:
            model_id: Optional FreeCAD model ID

        Returns:
            URL to CalcsLive FreeCAD connection page
        """
        url = self.endpoints['freecad_connect']

        params = {}
        if self.api_key:
            params['apiKey'] = self.api_key
        if model_id:
            params['modelId'] = model_id

        if params:
            url += f"?{urlencode(params)}"

        return url

    def get_dashboard_url(self, article_id: str, model_id: Optional[str] = None) -> str:
        """
        Get URL for CalcsLive FreeCAD dashboard

        Args:
            article_id: CalcsLive article ID
            model_id: Optional FreeCAD model ID

        Returns:
            URL to CalcsLive FreeCAD dashboard
        """
        url = self.endpoints['freecad_dashboard'].format(article_id=article_id)

        params = {}
        if model_id:
            params['modelId'] = model_id

        if params:
            url += f"?{urlencode(params)}"

        return url

    def _make_request(self, method: str, url: str, data: Optional[Dict] = None,
                     retries: Optional[int] = None) -> Dict[str, Any]:
        """
        Make HTTP request with retry logic

        Args:
            method: HTTP method (GET, POST)
            url: Request URL
            data: Request payload for POST requests
            retries: Number of retries (default: self.max_retries)

        Returns:
            Parsed JSON response

        Raises:
            CalcsLiveError: If request fails after retries
        """
        if retries is None:
            retries = self.max_retries

        last_error = None

        for attempt in range(retries + 1):
            try:
                # Prepare request
                req = Request(url)
                req.add_header('Content-Type', 'application/json')
                req.add_header('User-Agent', 'CalcsLive-FreeCAD/1.0.0')

                if self.api_key:
                    req.add_header('X-API-Key', self.api_key)

                # Add request data for POST
                if method.upper() == 'POST' and data:
                    req.data = json.dumps(data).encode('utf-8')

                # Make request
                with urlopen(req, timeout=self.timeout) as response:
                    response_data = response.read().decode('utf-8')
                    return json.loads(response_data)

            except HTTPError as e:
                last_error = f"HTTP {e.code}: {e.reason}"
                if e.code < 500:  # Don't retry client errors
                    break

            except URLError as e:
                last_error = f"Network error: {e.reason}"

            except json.JSONDecodeError as e:
                last_error = f"Invalid JSON response: {e}"
                break  # Don't retry JSON errors

            except Exception as e:
                last_error = f"Request failed: {str(e)}"

            # Wait before retry (except on last attempt)
            if attempt < retries:
                time.sleep(self.retry_delay * (attempt + 1))  # Exponential backoff

        raise CalcsLiveError(f"Request failed after {retries + 1} attempts: {last_error}")


class CalcsLiveError(Exception):
    """Custom exception for CalcsLive API errors"""
    pass


# Utility functions for common operations
def create_input_dict(value: Union[int, float], unit: str) -> Dict[str, Any]:
    """
    Create an input parameter dictionary

    Args:
        value: Parameter value
        unit: Parameter unit

    Returns:
        Dict in CalcsLive API format
    """
    return {'value': float(value), 'unit': str(unit)}


def extract_output_value(calculation_result: Dict[str, Any], symbol: str) -> Optional[float]:
    """
    Extract output value from calculation result

    Args:
        calculation_result: Result from get_calculation_results()
        symbol: Output symbol to extract

    Returns:
        Output value or None if not found
    """
    outputs = calculation_result.get('outputs', {})
    if symbol in outputs:
        return outputs[symbol].get('value')
    return None


def extract_output_unit(calculation_result: Dict[str, Any], symbol: str) -> Optional[str]:
    """
    Extract output unit from calculation result

    Args:
        calculation_result: Result from get_calculation_results()
        symbol: Output symbol to extract

    Returns:
        Output unit or None if not found
    """
    outputs = calculation_result.get('outputs', {})
    if symbol in outputs:
        return outputs[symbol].get('unit')
    return None