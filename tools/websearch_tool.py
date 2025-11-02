# tools/websearch_tool.py
import requests
from typing import Any, Dict, List
from . import Tool
from utils.config import settings

class WebSearchTool(Tool):
    name = "WebSearchTool"
    description = "Perform a real web search using Google Custom Search API. Arguments should include 'query' (str) and optional 'num_results' (int)."

    def __init__(self):
        """
        Initialize the Google Custom Search API client.
        """
        self.api_key = settings.api_key
        self.cse_id = settings.cse_id
        self.endpoint = "https://www.googleapis.com/customsearch/v1"

    def _call_google_api(self, query: str, num_results: int = 5) -> List[Dict[str, str]]:
        """
        Internal helper to call the Google Custom Search API.
        """
        params = {
            "key": self.api_key,
            "cx": self.cse_id,
            "q": query,
            "num": num_results
        }

        response = requests.get(self.endpoint, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        items = data.get("items", [])
        results = [
            {
                "title": item.get("title"),
                "snippet": item.get("snippet"),
                "link": item.get("link")
            }
            for item in items
        ]
        return results

    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Executes a real web search using Google Custom Search.
        Expects kwargs like: {"query": "latest AI models 2025", "num_results": 3}
        """
        query = kwargs.get("query")
        num_results = kwargs.get("num_results", 5)

        if not query:
            raise ValueError("Missing 'query' argument for WebSearchTool.execute()")

        try:
            results = self._call_google_api(query, num_results=num_results)
            return {
                "query": query,
                "results": results,
                "source": "google_custom_search_api"
            }
        except requests.RequestException as e:
            return {
                "query": query,
                "error": str(e),
                "results": [],
                "source": "google_custom_search_api"
            }
