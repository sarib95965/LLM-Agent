# llm.py
import json
import time
from typing import Dict, Any, List, Optional
from prompts.tool_prompts import get_tool_decision_prompt
from prompts.response_prompts import get_response_prompt
from prompts.base_prompts import get_agent_system_prompt
from utils.logger import get_logger
from utils.config import settings
from groq import Groq
from fastapi import WebSocket
import asyncio

logger = get_logger(__name__)

class LLMClient:
    """
    Responsible for making the actual LLM call.
    For now this is a mock implementation that returns deterministic outputs.
    Replace generate() with real free-tier provider code later.
    """
    def __init__(self):
        if not settings.API_KEY:
            raise ValueError("❌ Missing GROQ_API_KEY in environment or .env file.")
        self.client = Groq(api_key=settings.API_KEY)
        self.model = settings.MODEL_NAME

    def generate(self, prompt: str, temperature: float = 0.7) -> str:
        """Call the LLM model via Groq API."""
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a helpful financial and web search assistant. Always provide specific numerical values, dates, and percentages from the data provided. Never use placeholders like '$.' or incomplete dates."},
                {"role": "user", "content": prompt},
            ],
            temperature=temperature,
            max_completion_tokens=512,
            top_p=1,
            stream=False,
        )

        # Return the content of the first choice
        return completion.choices[0].message.content.strip()
    
    def generate_and_stream(self, prompt: str, temperature: float = 0.7):
        """Stream the model output token by token."""
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a helpful financial and web search assistant. Always provide specific numerical values, dates, and percentages from the data provided. Never use placeholders like '$.' or incomplete dates."},
                {"role": "user", "content": prompt},
            ],
            temperature=temperature,
            max_completion_tokens=512,
            top_p=1,
            stream=True,
        )

        for chunk in completion:
            yield chunk.choices[0].delta.content or ""


class Agent:
    """
    Orchestrates LLM-based decision making + tool execution + final synthesis.
    Strict OOP: encapsulates the tools and LLM client.
    """
    def __init__(self, llm_client: LLMClient, tools: List[Any]):
        self.llm_client = llm_client
        # tools is a list of Tool instances; index by their name for lookup
        self.tools = {t.name: t for t in tools}
        logger.info("Agent initialized with tools: %s", list(self.tools.keys()))

    def get_available_tools(self):
        return list(self.tools.values())

    def evaluate_prompt(self, user_input: str) -> List[Dict[str, Any]]:
        system = get_agent_system_prompt(self.get_available_tools())
        decision_prompt = get_tool_decision_prompt(user_input, system_prompt=system)
        llm_output = self.llm_client.generate(decision_prompt)
        try:
            plan = json.loads(llm_output)
            if isinstance(plan, dict) and "plans" in plan:
                return plan["plans"]
            elif isinstance(plan, dict):
                # backward compatibility with single-tool output
                return [plan]
            else:
                raise ValueError("Invalid plan structure")
        except Exception as e:
            logger.warning("Failed to parse LLM output: %s", e)
            return [{"tool": None, "args": {}}]

    def call_tool(self, tool_name: str, **kwargs) -> Any:
        """
        Execute a tool by name with kwargs.
        Raises ValueError if tool not found.
        """
        if tool_name not in self.tools:
            raise ValueError(f"Tool '{tool_name}' not registered.")
        tool = self.tools[tool_name]
        logger.info("Calling tool %s with args: %s", tool_name, kwargs)
        result = tool.execute(**kwargs)
        return result

    def synthesize_response(self, user_input: str, tool_results: Dict[str, Any]) -> str:
        """
        Use the LLM to synthesize the final user-facing response.
        """
        # Build a structured summary of tool results
        if tool_results:
            combined_results = json.dumps(tool_results, indent=2)
        else:
            combined_results = "No tool results available."
            
        final_prompt = get_response_prompt(user_input=user_input, tool_output=combined_results)
        logger.info("Final synthesis prompt: %s", final_prompt[:200] + "...")
        final_generated = self.llm_client.generate(final_prompt, temperature=0.3)  # Lower temperature for more consistent output
        return final_generated

    def respond(self, user_input: str) -> Dict[str, Any]:
        plans = self.evaluate_prompt(user_input)
        tool_results = {}

        for plan in plans:
            tool_name = plan.get("tool")
            args = plan.get("args", {}) or {}

            if not tool_name:
                continue  # skip if no tool

            try:
                result = self.call_tool(tool_name, **args)
                tool_results[tool_name] = result
            except Exception as e:
                logger.exception("Tool execution failed for %s", tool_name)
                tool_results[tool_name] = {"error": str(e)}

        final_response = self.synthesize_response(user_input, tool_results)
        return {"final_response": final_response, "tool_plans": plans, "tool_results": tool_results}
    
    async def respond_streaming(self, user_input: str, websocket: WebSocket):
        """Sequential LLM → Tool → Final streaming response via WebSocket."""
        try:
            # 🧠 Step 1: Notify start
            await websocket.send_json({
                "status": "thinking",
                "message": "LLM is analyzing your request..."
            })

            # 🧩 Step 2: Plan tool usage
            plans = self.evaluate_prompt(user_input)
            await websocket.send_json({"status": "plan", "data": plans})

            tool_results = {}

            # 🛠 Step 3: Execute tools sequentially
            for plan in plans:
                tool_name = plan.get("tool")
                args = plan.get("args", {}) or {}

                if not tool_name:
                    continue

                await websocket.send_json({
                    "status": "tool_calling",
                    "tool": tool_name,
                    "args": args,
                    "message": f"Calling {tool_name}..."
                })

                try:
                    result = self.call_tool(tool_name, **args)
                    tool_results[tool_name] = result

                    await websocket.send_json({
                        "status": "tool_result",
                        "tool": tool_name,
                        "result": result
                    })
                except Exception as e:
                    tool_results[tool_name] = {"error": str(e)}
                    await websocket.send_json({
                        "status": "tool_error",
                        "tool": tool_name,
                        "error": str(e)
                    })

            # 💬 Step 4: Stream final synthesis token-by-token
            await websocket.send_json({
                "status": "stream_start",
                "message": "Generating final response..."
            })

            final_prompt = get_response_prompt(
                user_input=user_input,
                tool_output=json.dumps(tool_results, indent=2)
            )
            
            logger.info("Streaming synthesis prompt: %s", final_prompt[:300] + "...")

            # ⛔ Don't send again here — _stream_llm_tokens already sends chunks
            async for _ in self._stream_llm_tokens(final_prompt, websocket, temperature=0.3):
                pass

            # ✅ Done
            await websocket.send_json({"status": "done"})

        except Exception as e:
            logger.exception("Error in respond_streaming")
            await websocket.send_json({"status": "error", "message": str(e)})

    async def _stream_llm_tokens(self, prompt: str, websocket: Optional[WebSocket] = None, temperature: float = 0.7):
        """Async generator yielding streamed LLM tokens, sending directly to WebSocket with smart buffering."""
        buffer = ""
        last_send_time = time.time()
        flush_interval = 0.05  # Send every 50ms or when buffer reaches natural breakpoints
        buffer_size = 20  # Maximum buffer size before forcing a send
        
        async def flush_buffer():
            """Helper to flush the buffer if it has content."""
            nonlocal buffer, last_send_time
            if buffer:
                if websocket:
                    await websocket.send_text(buffer)
                result = buffer
                buffer = ""
                last_send_time = time.time()
                return result
            return ""
        
        for chunk in self.llm_client.generate_and_stream(prompt, temperature=temperature):
            if not chunk:
                continue
            
            buffer += chunk
            
            current_time = time.time()
            time_since_send = current_time - last_send_time
            
            # Flush conditions:
            # 1. Buffer is too large
            # 2. Enough time has passed (flush_interval)
            # 3. Natural breakpoint (space, newline, or punctuation)
            should_flush = (
                len(buffer) >= buffer_size or
                time_since_send >= flush_interval or
                (buffer and buffer[-1] in [' ', '\n', '.', ',', ':', ';', '!', '?', '\t'])
            )
            
            if should_flush:
                flushed = await flush_buffer()
                if flushed:
                    yield flushed
        
        # Send any remaining buffer at the end
        flushed = await flush_buffer()
        if flushed:
            yield flushed