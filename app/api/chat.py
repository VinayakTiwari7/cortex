from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.core.circuit_breaker import CircuitBreaker
from app.core.router import AllProvidersFailedError, ProviderRouter
from app.providers.groq_provider import GroqProvider
from app.providers.gemini_provider import GeminiProvider
from app.schemas.chat import ChatRequest, ChatResponse

router = APIRouter()

groq_provider = GroqProvider()
groq_breaker = CircuitBreaker(failure_threshold=3, reset_timeout_seconds=30)

gemini_provider = GeminiProvider()
gemini_breaker = CircuitBreaker(failure_threshold=3, reset_timeout_seconds=30)

cortex_router = ProviderRouter([
    (groq_provider, groq_breaker),
    (gemini_provider, gemini_breaker),
])


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    try:
        return await cortex_router.complete(request)
    except AllProvidersFailedError as e:
        raise HTTPException(status_code=503, detail=f"all providers unavailable: {e}") from e

@router.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    async def event_generator():
        try:
            async for chunk in cortex_router.stream(request):
                yield chunk
        except AllProvidersFailedError as e:
            yield f"\n[ERROR: all providers unavailable: {e}]"

    return StreamingResponse(event_generator(), media_type="text/plain")