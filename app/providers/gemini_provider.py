import json

import httpx

from app.config import settings
from app.providers.base import Provider, ProviderError
from app.schemas.chat import ChatRequest, ChatResponse
from collections.abc import AsyncGenerator


class GeminiProvider(Provider):
    name = "gemini"

    def _to_gemini_contents(self, request: ChatRequest) -> list[dict]:
        return [
            {"role": "user" if m.role == "user" else "model", "parts": [{"text": m.content}]}
            for m in request.messages
        ]

    async def complete(self, request: ChatRequest) -> ChatResponse:
        params = {"key": settings.gemini_api_key}
        payload = {
            "contents": self._to_gemini_contents(request),
            "generationConfig": {"maxOutputTokens": request.max_tokens},
        }

        try:
            async with httpx.AsyncClient(timeout=settings.request_timeout_seconds) as client:
                response = await client.post(settings.gemini_url, params=params, json=payload)
                response.raise_for_status()
                data = response.json()
        except (httpx.HTTPError, httpx.TimeoutException) as e:
            raise ProviderError(f"gemini call failed: {e}") from e

        try:
            answer_text = data["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError) as e:
            raise ProviderError(f"gemini returned unexpected shape: {e}") from e

        return ChatResponse(provider=self.name, answer=answer_text)

    async def stream(self, request: ChatRequest) -> AsyncGenerator[str, None]:
        params = {"key": settings.gemini_api_key, "alt": "sse"}
        payload = {
            "contents": self._to_gemini_contents(request),
            "generationConfig": {"maxOutputTokens": request.max_tokens},
        }

        try:
            async with httpx.AsyncClient(timeout=settings.request_timeout_seconds) as client:
                async with client.stream(
                    "POST", settings.gemini_stream_url, params=params, json=payload
                ) as response:
                    response.raise_for_status()
                    async for line in response.aiter_lines():
                        if not line.startswith("data:"):
                            continue
                        chunk = line[len("data:"):].strip()
                        if chunk == "":
                            continue
                        event = json.loads(chunk)
                        delta = event["candidates"][0]["content"]["parts"][0]["text"]
                        if delta:
                            yield delta
        except (httpx.HTTPError, httpx.TimeoutException, KeyError, IndexError, json.JSONDecodeError) as e:
            raise ProviderError(f"gemini stream failed: {e}") from e