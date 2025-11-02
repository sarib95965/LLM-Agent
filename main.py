# main.py
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from models.request_models import UserRequest, AgentResponse
from llm import LLMClient, Agent
from tools.finance_tool import FinanceTool
from tools.websearch_tool import WebSearchTool
from utils.config import settings
from utils.logger import get_logger

logger = get_logger(__name__)

app = FastAPI(title="LLM Agent")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Instantiate LLM client (mock by default; replace implementation later)
llm_client = LLMClient()

# Register tools
tools = [FinanceTool(), WebSearchTool()]

# Create agent
agent = Agent(llm_client=llm_client, tools=tools)

@app.post("/query", response_model=AgentResponse)
def query_endpoint(req: UserRequest):
    """
    Accepts {"prompt": "..."} and returns the agent's structured response.
    """
    logger.info("Received query: %s", req.prompt)
    try:
        response = agent.respond(req.prompt)
        return AgentResponse(
            original_prompt=req.prompt,
            final_response=response["final_response"],
            tool_plan=response.get("tool_plan"),
            tool_results=response.get("tool_results"),
        )
    except Exception as e:
        logger.exception("Error while responding")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
async def serve_frontend():
    """Serve the frontend HTML file"""
    return FileResponse("static/index.html")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, prompt: str):
    await websocket.accept()
    try:
        await agent.respond_streaming(prompt, websocket)
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
    except Exception as e:
        logger.exception("WebSocket error")
        try:
            await websocket.send_json({"status": "error", "message": str(e)})
        except:
            pass
    finally:
        try:
            await websocket.close()
        except:
            pass