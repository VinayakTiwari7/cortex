from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator

from app.schemas.chat import ChatRequest, ChatResponse


class ProviderError(Exception):
    """Raised when a provider call fails for any reason (timeout, bad response, etc.)."""


class Provider(ABC):
    name: str

    @abstractmethod
    async def complete(self, request: ChatRequest) -> ChatResponse:
        """Send the request to this provider and return a normalized ChatResponse.
        Must raise ProviderError on any failure — never let raw provider
        exceptions leak upward."""

    @abstractmethod
    async def stream(self, request: ChatRequest) -> AsyncGenerator[str, None]:
        """Yield text chunks as they arrive from the provider.
        Must raise ProviderError on any failure."""