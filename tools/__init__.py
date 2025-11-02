# tools/__init__.py
from abc import ABC, abstractmethod
from typing import Any, Dict

class Tool(ABC):
    """
    Abstract Tool interface. All tools must implement name, description, and execute().
    """
    name: str = "Tool"
    description: str = "Abstract tool"

    @abstractmethod
    def execute(self, **kwargs) -> Any:
        raise NotImplementedError
