# LLM Agent

An intelligent agent system built with FastAPI that uses LLM (Large Language Model) to analyze user queries, execute tools, and provide synthesized responses. The agent can perform financial data retrieval and web searches, making it useful for financial queries and general information gathering.

## Features

- 🤖 **LLM-Powered Agent**: Uses Groq API for intelligent decision-making and response synthesis
- 💰 **Finance Tool**: Fetches real-time financial market data (stocks, crypto, forex) via Finnhub API
- 🔍 **Web Search Tool**: Performs web searches using Google Custom Search API
- 🌐 **WebSocket Support**: Real-time streaming responses for enhanced user experience
- 📡 **REST API**: Standard HTTP endpoints for query processing
- 🎨 **Web Interface**: Built-in HTML frontend for interactive usage

## Tools Used

### 1. Finance Tool (`FinanceTool`)
- **Purpose**: Retrieves real-time financial market data
- **API**: Finnhub API
- **Supported Types**:
  - **Stocks**: Real-time stock quotes (e.g., AAPL, MSFT, GOOGL)
  - **Crypto**: Cryptocurrency prices (e.g., BTC, ETH)
  - **Forex**: Foreign exchange rates (e.g., EUR/USD)
- **Required Environment Variable**: `FINNHUB_API_KEY`
- **Usage**: Agent automatically uses this tool when financial queries are detected

### 2. Web Search Tool (`WebSearchTool`)
- **Purpose**: Performs real-time web searches
- **API**: Google Custom Search API
- **Features**: Returns search results with titles, snippets, and links
- **Required Environment Variables**: 
  - `GOOGLE_API_KEY`
  - `GOOGLE_CSE_ID`
- **Usage**: Agent uses this tool for general information queries and research

### 3. LLM Client (`LLMClient`)
- **Purpose**: Interfaces with Groq API for LLM inference
- **Model**: Configurable via `LLM_MODEL_NAME` environment variable
- **Features**:
  - Standard text generation
  - Streaming token-by-token generation for real-time responses
- **Required Environment Variable**: `GROQ_API_KEY`

## Class Structure

### Core Classes

#### `LLMClient` (`llm.py`)
```python
class LLMClient:
    """
    Responsible for making LLM API calls via Groq.
    """
    - generate(prompt, temperature): Synchronous text generation
    - generate_and_stream(prompt, temperature): Streaming token generation
```

#### `Agent` (`llm.py`)
```python
class Agent:
    """
    Orchestrates LLM-based decision making, tool execution, and response synthesis.
    """
    - __init__(llm_client, tools): Initialize with LLM client and tool list
    - evaluate_prompt(user_input): Analyze query and decide which tools to use
    - call_tool(tool_name, **kwargs): Execute a specific tool
    - synthesize_response(user_input, tool_results): Generate final response
    - respond(user_input): Complete request-response cycle
    - respond_streaming(user_input, websocket): Stream response via WebSocket
```

#### `Tool` (Abstract Base Class) (`tools/__init__.py`)
```python
class Tool(ABC):
    """
    Abstract interface that all tools must implement.
    """
    - name: str (tool identifier)
    - description: str (tool description for LLM)
    - execute(**kwargs): Abstract method for tool execution
```

#### `FinanceTool` (`tools/finance_tool.py`)
```python
class FinanceTool(Tool):
    """
    Fetches financial data from Finnhub API.
    """
    - execute(type, symbol): Retrieve financial data
      - type: 'stock' | 'crypto' | 'forex'
      - symbol: Ticker symbol or pair
```

#### `WebSearchTool` (`tools/websearch_tool.py`)
```python
class WebSearchTool(Tool):
    """
    Performs web searches via Google Custom Search API.
    """
    - execute(query, num_results): Execute web search
      - query: Search query string
      - num_results: Number of results to return (default: 5)
```

### Supporting Classes

#### `Settings` (`utils/config.py`)
- Manages configuration via environment variables
- Uses `python-dotenv` to load `.env` file

#### Request/Response Models (`models/request_models.py`)
- `UserRequest`: Input model for API requests
- `AgentResponse`: Output model for API responses

## Project Structure

```
LLM Agent/
├── main.py                 # FastAPI application entry point
├── llm.py                  # LLMClient and Agent classes
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── models/
│   └── request_models.py  # Pydantic models for API
├── prompts/
│   ├── base_prompts.py    # System prompts
│   ├── tool_prompts.py   # Tool decision prompts
│   └── response_prompts.py # Response synthesis prompts
├── tools/
│   ├── __init__.py        # Tool abstract base class
│   ├── finance_tool.py   # FinanceTool implementation
│   └── websearch_tool.py # WebSearchTool implementation
├── utils/
│   ├── config.py          # Configuration settings
│   └── logger.py          # Logging utility
└── static/
    └── index.html         # Web interface
```

## Installation

1. **Clone the repository** (if applicable) or navigate to the project directory

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**:
   - **Windows**:
     ```bash
     venv\Scripts\activate
     ```
   - **Linux/Mac**:
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Install additional dependencies** (if not already installed):
   ```bash
   pip install groq python-dotenv requests
   ```

## Configuration

Create a `.env` file in the project root with the following environment variables:

```env
# LLM Configuration
GROQ_API_KEY=your_groq_api_key_here
LLM_MODEL_NAME=llama3.1-8b-instant  # or your preferred model

# Finance Tool
FINNHUB_API_KEY=your_finnhub_api_key_here

# Web Search Tool
GOOGLE_API_KEY=your_google_api_key_here
GOOGLE_CSE_ID=your_google_cse_id_here
```

### Getting API Keys

1. **Groq API Key**: 
   - Visit [console.groq.com](https://console.groq.com)
   - Sign up/login and generate an API key

2. **Finnhub API Key**:
   - Visit [finnhub.io](https://finnhub.io)
   - Sign up for a free account and get your API key

3. **Google Custom Search API**:
   - Visit [Google Cloud Console](https://console.cloud.google.com)
   - Enable Custom Search API
   - Create API credentials and get your API key
   - Set up a Custom Search Engine at [cse.google.com](https://cse.google.com) and get your CSE ID

## How to Run

### Start the Development Server

Run the FastAPI application using Uvicorn:

```bash
uvicorn main:app --reload
```

The server will start on `http://localhost:8000` by default.

### Access the Application

- **Web Interface**: Open your browser and navigate to `http://localhost:8000`
- **API Documentation**: Visit `http://localhost:8000/docs` for interactive API documentation
- **Alternative Docs**: Visit `http://localhost:8000/redoc` for ReDoc documentation

## API Endpoints

### POST `/query`
Submit a query to the agent and receive a structured response.

**Request Body**:
```json
{
  "prompt": "What is the current price of Apple stock?"
}
```

**Response**:
```json
{
  "original_prompt": "What is the current price of Apple stock?",
  "final_response": "The current price of Apple (AAPL) is...",
  "tool_plan": [...],
  "tool_results": {...}
}
```

### GET `/`
Serves the HTML frontend interface.

### WebSocket `/ws?prompt=<your_query>`
Real-time streaming endpoint for live responses.

**Example** (JavaScript):
```javascript
const ws = new WebSocket('ws://localhost:8000/ws?prompt=What is Bitcoin price?');
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log(data);
};
```

## How It Works

1. **User Query**: User submits a query via API or web interface
2. **Tool Decision**: The LLM analyzes the query and determines which tools (if any) are needed
3. **Tool Execution**: The agent executes the selected tools with appropriate parameters
4. **Response Synthesis**: The LLM synthesizes the tool results into a natural language response
5. **Return Result**: The final response is returned to the user

For streaming requests (WebSocket), the process sends real-time updates:
- Thinking status
- Tool plan
- Tool execution progress
- Token-by-token response generation

## Example Queries

- **Finance**: "What's the current price of Tesla stock?"
- **Finance**: "Show me Bitcoin price"
- **Web Search**: "What are the latest developments in AI?"
- **Combined**: "Search for recent news about Apple and then get its current stock price"

## Development

### Adding New Tools

1. Create a new tool class in `tools/` directory
2. Inherit from the `Tool` abstract base class
3. Implement `name`, `description`, and `execute()` method
4. Register the tool in `main.py`:
   ```python
   tools = [FinanceTool(), WebSearchTool(), YourNewTool()]
   ```

### Customizing Prompts

Modify the prompt functions in the `prompts/` directory:
- `base_prompts.py`: System behavior and tool descriptions
- `tool_prompts.py`: Tool selection logic
- `response_prompts.py`: Response formatting instructions

## Troubleshooting

- **Missing API Keys**: Ensure all required environment variables are set in your `.env` file
- **Import Errors**: Make sure all dependencies are installed (`pip install -r requirements.txt`)
- **API Errors**: Check that your API keys are valid and have sufficient quota
- **Port Already in Use**: Change the port using `uvicorn main:app --port 8001`

## License

This project is provided as-is for educational and development purposes.

