# prompts/response_prompts.py
from typing import Optional, List, Dict

def get_response_prompt(user_input: str, tool_output: str, memory: Optional[List[Dict[str, str]]] = None) -> str:
    """
    Builds a prompt for final synthesis.
    In production this prompt would be sent to the LLM to craft the final reply.
    
    Args:
        user_input: The current user's input message
        tool_output: The output from tool executions
    """
    return (
        f"You are a helpful financial and web search assistant. The user asked: \"{user_input}\"\n\n"
        f"Here is the data retrieved from tools:\n{tool_output}\n\n"
        "IMPORTANT INSTRUCTIONS:\n"
        "1. Extract the specific numerical values, prices, dates, and key information from the tool output\n"
        "2. Present the information in a clear, human-readable format\n"
        "3. For stock data, include: current price, change amount, change percentage, and trading date\n"
        "4. For search results, summarize the key findings from the search results\n"
        "5. Use the actual values from the data - do not leave placeholders like '$.' or 'October ,'\n"
        "6. Be specific and accurate with numbers, dates, and percentages\n"
        "7. If there are errors in the tool output, mention them clearly\n"
        "8. Use the conversation history to provide context-aware responses and maintain continuity\n\n"
        "Provide a helpful and informative response using the actual data from the tools:"
        "If there is no result from the tools answer the user's question based on your knowledge and you should not tell that the tool output is empty. the user does not need to know that the tool output is empty."
    )
