import hashlib
import json

import redis.asyncio as redis

from app.config import settings
from app.schemas.chat import ChatRequest, ChatResponse

_redis_client = redis.from_url(settings.redis_url, decode_responses=True) if settings.redis_url else None


def _cache_key(request: ChatRequest) -> str:
    raw = json.dumps(
        {
            "messages": [m.model_dump() for m in request.messages],
            "max_tokens": request.max_tokens,
        },
        sort_keys=True,
    )
    digest = hashlib.sha256(raw.encode()).hexdigest()
    return f"cortex:chat:{digest}"


async def get_cached(request: ChatRequest) -> ChatResponse | None:
    if _redis_client is None:
        return None
    try:
        raw = await _redis_client.get(_cache_key(request))
    except Exception:
        return None
    if raw is None:
        return None
    data = json.loads(raw)
    data["cached"] = True
    return ChatResponse(**data)


async def set_cached(request: ChatRequest, response: ChatResponse) -> None:
    if _redis_client is None:
        return
    try:
        await _redis_client.set(
            _cache_key(request),
            response.model_dump_json(),
            ex=settings.cache_ttl_seconds,
        )
    except Exception:
        pass