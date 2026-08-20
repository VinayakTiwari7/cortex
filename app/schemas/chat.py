from pydantic import BaseModel


class ChatMessage(BaseModel):
    role: str       # "user" or "system" or "assistant"
    content: str


class ChatRequest(BaseModel):
    messages: list[ChatMessage]
    max_tokens: int = 200


class ChatResponse(BaseModel):
    provider: str
    answer: str