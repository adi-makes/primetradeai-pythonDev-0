"""Binance Futures Testnet API client."""

import hashlib
import hmac
import time
import urllib.parse

import requests
from requests.exceptions import HTTPError, RequestException

from .logging_config import get_logger

__all__ = ["BinanceClient"]


class BinanceClient:
    """Wrapper for Binance Futures Testnet REST API."""

    BASE_URL = "https://testnet.binancefuture.com"

    def __init__(self, api_key: str, api_secret: str) -> None:
        """Initialize client with credentials and session."""
        self.api_key = api_key
        self.api_secret = api_secret
        self.session = requests.Session()
        self.session.headers.update({"X-MBX-APIKEY": api_key})
        self.logger = get_logger(__name__)

    def _sign(self, params: dict) -> str:
        """Generate HMAC-SHA256 signature for request params."""
        query = urllib.parse.urlencode(params)
        return hmac.new(
            self.api_secret.encode(),
            query.encode(),
            hashlib.sha256,
        ).hexdigest()

    def get_server_time(self) -> int:
        """Fetch server time from Binance to avoid clock drift."""
        try:
            response = self.session.get(f"{self.BASE_URL}/fapi/v1/time")
            response.raise_for_status()
            return int(response.json()["serverTime"])
        except Exception as e:
            self.logger.warning(
                f"Failed to fetch server time ({e}); falling back to local time."
            )
            return int(time.time() * 1000)

    def get_account_balance(self) -> list:
        """Fetch account balance via GET /fapi/v2/account."""
        params = {"timestamp": self.get_server_time()}
        params["signature"] = self._sign(params)
        response = self.session.get(f"{self.BASE_URL}/fapi/v2/account", params=params)
        response.raise_for_status()
        data = response.json()
        self.logger.debug(f"Account balance fetched: {data.get('assets', [])}")
        return data.get("assets", [])

    def place_order(self, params: dict) -> dict:
        """Place an order on Binance Futures Testnet."""
        # 1. Add timestamp
        params["timestamp"] = self.get_server_time()
        # 2. Add signature
        params["signature"] = self._sign(params)
        # 3. Log request params
        self.logger.debug(f"Request params: {params}")

        max_retries = 3
        for attempt in range(max_retries):
            try:
                # 4. POST with data= (form-encoded), not json=
                response = self.session.post(
                    f"{self.BASE_URL}/fapi/v1/order", data=params
                )
                # 5. Log raw response
                self.logger.debug(f"Raw response: {response.text}")
                # 6. Raise for HTTP errors
                response.raise_for_status()
                # 9. Return parsed JSON
                return response.json()
            except HTTPError:
                # 7. Extract Binance error message
                try:
                    binance_msg = response.json().get("msg", response.text)
                except Exception:
                    binance_msg = response.text

                status_code = response.status_code
                if status_code == 400:
                    self.logger.error(f"HTTP 400 Bad Request: {binance_msg}")
                    raise RuntimeError(f"Bad Request: {binance_msg}")
                elif status_code == 401:
                    self.logger.error(f"HTTP 401 Unauthorized: {binance_msg}")
                    raise RuntimeError(f"Unauthorized: Check API keys. ({binance_msg})")
                elif status_code == 429:
                    self.logger.error(f"HTTP 429 Rate Limit Exceeded: {binance_msg}")
                    raise RuntimeError(f"Rate Limit Exceeded: {binance_msg}")
                elif status_code >= 500:
                    self.logger.error(f"HTTP {status_code} Server Error: {binance_msg}")
                    raise RuntimeError(f"Server Error {status_code}: {binance_msg}")
                else:
                    self.logger.error(f"HTTP error {status_code}: {binance_msg}")
                    raise RuntimeError(f"Binance API error: {binance_msg}")
            except RequestException as e:
                # 8. Network-level error
                if attempt < max_retries - 1:
                    self.logger.warning(
                        f"Network error: {e}. Retrying {attempt + 1}/{max_retries - 1} in 1s..."
                    )
                    time.sleep(1)
                else:
                    self.logger.error(
                        f"Network error after {max_retries} attempts: {e}"
                    )
                    raise
