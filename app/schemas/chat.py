from pydantic import BaseModel


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: list[ChatMessage]
    max_tokens: int = 200                   
    max_tokens: int = 200                   


class ChatResponse(BaseModel):
    provider: str
    answer: str
    cached: bool = False