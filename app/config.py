import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    groq_api_key: str = os.getenv("GROQ_API_KEY", "")
    groq_url: str = "https://api.groq.com/openai/v1/chat/completions"
    request_timeout_seconds: int = 30


settings = Settings()