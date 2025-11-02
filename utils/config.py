# utils/config.py
import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass
class Settings:
    MODEL_NAME: str = os.getenv("LLM_MODEL_NAME")
    API_KEY: str = os.getenv("GROQ_API_KEY")
    cse_id: str = os.getenv("GOOGLE_CSE_ID")
    api_key: str = os.getenv("GOOGLE_API_KEY")
    finnhub_api_key: str = os.getenv("FINNHUB_API_KEY")
    finnhub_endpoint: str = os.getenv("FINNHUB_ENDPOINT")
    # Add other config keys (e.g., finance API keys) later

settings = Settings()
