from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.core.circuit_breaker import CircuitBreaker
from app.providers.base import ProviderError
from app.providers.groq_provider import GroqProvider
from app.schemas.chat import ChatRequest, ChatResponse

router = APIRouter()
provider = GroqProvider()
breaker = CircuitBreaker(failure_threshold=3, reset_timeout_seconds=30)


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    if breaker.is_open():
        raise HTTPException(status_code=503, detail="Circuit breaker open — provider temporarily unavailable")

    try:
        response = await provider.complete(request)
        breaker.record_success()
        return response
    except ProviderError as e:
        breaker.record_failure()
        raise HTTPException(status_code=503, detail=str(e)) from e


@router.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    if breaker.is_open():
        raise HTTPException(status_code=503, detail="Circuit breaker open — provider temporarily unavailable")

    async def event_generator():
        try:
            async for chunk in provider.stream(request):
                yield chunk
            breaker.record_success()
        except ProviderError as e:
            breaker.record_failure()
            yield f"\n[ERROR: {e}]"

    return StreamingResponse(event_generator(), media_type="text/plain")