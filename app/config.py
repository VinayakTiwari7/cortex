import os
from dotenv import load_dotenv

load_dotenv(override=True)


class Settings:
    groq_api_key: str = os.getenv("GROQ_API_KEY", "")
    groq_url: str = "https://api.groq.com/openai/v1/chat/completions"

    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    gemini_url: str = "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash-lite:generateContent"
    gemini_stream_url: str = "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash-lite:streamGenerateContent"

    request_timeout_seconds: int = 30


settings = Settings()