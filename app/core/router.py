import logging

from app.core.circuit_breaker import CircuitBreaker
from app.providers.base import Provider, ProviderError
from app.schemas.chat import ChatRequest, ChatResponse

logger = logging.getLogger("cortex.router")


class AllProvidersFailedError(Exception):
    pass


class ProviderRouter:
    def __init__(self, providers: list[tuple[Provider, CircuitBreaker]]) -> None:
        self.providers = providers

    async def complete(self, request: ChatRequest) -> ChatResponse:
        last_error: Exception | None = None

        for provider, breaker in self.providers:
            if breaker.is_open():
                logger.warning("%s circuit open, skipping", provider.name)
                continue

            try:
                response = await provider.complete(request)
                breaker.record_success()
                return response
            except ProviderError as e:
                logger.warning("%s failed: %s", provider.name, e)
                breaker.record_failure()
                last_error = e
                continue

        raise AllProvidersFailedError(str(last_error) if last_error else "no providers available")