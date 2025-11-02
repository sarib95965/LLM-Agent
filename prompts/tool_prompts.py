# prompts/tool_prompts.py
from typing import Optional, List, Dict

def get_tool_decision_prompt(user_input: str, system_prompt: Optional[str] = None, memory: Optional[List[Dict[str, str]]] = None) -> str:
    """
    Builds a prompt to ask the LLM to decide which tool to call.
    Returns a string. In production you'd want to instruct the LLM to only reply with JSON.
    
    Args:
        user_input: The current user's input message
        system_prompt: Optional system prompt describing available tools
    """
    system_part = system_prompt + "\n\n" if system_prompt else ""
    
    return (
        f"{system_part}"
        "Decide which tool (if any) should be used for the user's request. You can get creative.\n\n"
        "You can call all the registered tools. any one of them, or none.\n\n"
        "You can breakdown the pormpt into multiple parts and call multiple tools for each part if needed.\n\n"
        "Return only a JSON object in this exact format:  {\"plans\": [{\"tool\": \"ToolName\", \"args\": {...}}, ...]}.\n\n"
        "No reasoning, just the JSON.\n\n"
        f"User input: \"{user_input}\"\n"
    )
