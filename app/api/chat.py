from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.providers.base import ProviderError
from app.providers.groq_provider import GroqProvider
from app.schemas.chat import ChatRequest, ChatResponse

router = APIRouter()
provider = GroqProvider()


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    try:
        return await provider.complete(request)
    except ProviderError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e


@router.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    async def event_generator():
        try:
            async for chunk in provider.stream(request):
                yield chunk
        except ProviderError as e:
            yield f"\n[ERROR: {e}]"

    return StreamingResponse(event_generator(), media_type="text/plain")