# prompts/base_prompts.py
from typing import List
from tools import Tool

def get_agent_system_prompt(tools: List[Tool]) -> str:
    """
    System prompt describing the agent's behavior.
    Lists all available tools and their purpose.
    """
    tool_descriptions = "\n".join(
        [f"- {t.name}: {t.description}" for t in tools]
    )

    prompt = (
        "You are an intelligent assistant capable of calling external tools to perform tasks.\n"
        "When given a user's query, analyze whether to use a tool or respond directly.\n"
        "If using a tool, produce a JSON object with:\n"
        "  {\n"
        "    'tool': '<tool_name>',  # or null if no tool is needed\n"
        "    'args': {<arguments_for_the_tool>}\n"
        "  }\n\n"
        f"Available tools:\n{tool_descriptions}\n"
    )

    return prompt
