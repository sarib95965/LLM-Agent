# models/request_models.py
from pydantic import BaseModel
from typing import Optional, Any, Dict

class UserRequest(BaseModel):
    prompt: str

class AgentResponse(BaseModel):
    original_prompt: str
    final_response: str
    tool_plan: Optional[Dict[str, Any]] = None
    tool_results: Optional[Dict[str, Any]] = None
