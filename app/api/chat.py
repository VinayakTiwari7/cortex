from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import StreamingResponse

from app.core.cache import get_cached, set_cached
from app.core.circuit_breaker import CircuitBreaker
from app.core.rate_limiter import RateLimiter
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

rate_limiter = RateLimiter(max_requests=10, window_seconds=60)


async def enforce_rate_limit(request: Request) -> None:
    client_id = request.client.host if request.client else "unknown"
    allowed = await rate_limiter.is_allowed(client_id)
    if not allowed:
        raise HTTPException(status_code=429, detail="Rate limit exceeded — try again shortly")


@router.post("/chat", response_model=ChatResponse, dependencies=[Depends(enforce_rate_limit)])
async def chat(request: ChatRequest) -> ChatResponse:
    cached = await get_cached(request)
    if cached is not None:
        return cached

    try:
        response = await cortex_router.complete(request)
    except AllProvidersFailedError as e:
        raise HTTPException(status_code=503, detail=f"all providers unavailable: {e}") from e

    await set_cached(request, response)
    return response


@router.post("/chat/stream", dependencies=[Depends(enforce_rate_limit)])
async def chat_stream(request: ChatRequest):
    async def event_generator():
        try:
            async for chunk in cortex_router.stream(request):
                yield chunk
        except AllProvidersFailedError as e:
            yield f"\n[ERROR: all providers unavailable: {e}]"

    return StreamingResponse(event_generator(), media_type="text/plain")