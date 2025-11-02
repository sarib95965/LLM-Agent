# tools/finance_tool.py
import requests
from typing import Any, Dict

from utils.config import settings
from . import Tool

class FinanceTool(Tool):
    name = "FinanceTool"
    description = """Fetch real-time financial market data (stocks, crypto, forex) using Finnhub API. Expected kwargs:
          - type: 'stock' | 'crypto' | 'forex'
          - symbol: e.g., 'AAPL', 'BTC', 'EUR/USD'
        """

    def __init__(self):
        self.api_key = settings.finnhub_api_key
        self.endpoint = "https://finnhub.io/api/v1"

    def _call_api(self, path: str, params: Dict[str, Any]) -> Dict[str, Any]:
        params["token"] = self.api_key
        response = requests.get(f"{self.endpoint}{path}", params=params, timeout=10)
        response.raise_for_status()
        return response.json()

    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Execute a finance query.
        Expected kwargs:
          - type: 'stock' | 'crypto' | 'forex'
          - symbol: e.g., 'AAPL', 'BTC', 'EUR/USD'
        """
        query_type = kwargs.get("type", "stock")
        symbol = kwargs.get("symbol")

        if not symbol:
            raise ValueError("Missing 'symbol' argument for FinanceTool.execute()")

        try:
            if query_type == "stock":
                # Real-time stock price
                data = self._call_api("/quote", {"symbol": symbol})
                return {"symbol": symbol, "type": query_type, "data": data, "source": "finnhub"}

            elif query_type == "crypto":
                # Crypto symbols must be prefixed (e.g., 'BINANCE:BTCUSDT')
                data = self._call_api("/quote", {"symbol": symbol})
                return {"symbol": symbol, "type": query_type, "data": data, "source": "finnhub"}

            elif query_type == "forex":
                # Forex pairs must be in format 'OANDA:EUR_USD' or similar
                data = self._call_api("/quote", {"symbol": symbol})
                return {"symbol": symbol, "type": query_type, "data": data, "source": "finnhub"}

            else:
                raise ValueError(f"Unsupported type '{query_type}' for FinanceTool.")

        except requests.RequestException as e:
            return {"error": str(e), "symbol": symbol, "type": query_type, "data": {}, "source": "finnhub"}
