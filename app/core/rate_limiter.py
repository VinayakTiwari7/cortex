from app.config import settings
import redis.asyncio as redis

_redis_client = redis.from_url(settings.redis_url, decode_responses=True) if settings.redis_url else None


class RateLimiter:
    def __init__(self, max_requests: int = 10, window_seconds: int = 60) -> None:
        self.max_requests = max_requests
        self.window_seconds = window_seconds

    async def is_allowed(self, client_id: str) -> bool:
        if _redis_client is None:
            return True

        key = f"cortex:ratelimit:{client_id}"
        try:
            count = await _redis_client.incr(key)
            if count == 1:
                await _redis_client.expire(key, self.window_seconds)
            return count <= self.max_requests
        except Exception:
            return True