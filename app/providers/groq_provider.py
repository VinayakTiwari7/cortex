import json

import httpx

from app.config import settings
from app.providers.base import Provider, ProviderError
from app.schemas.chat import ChatRequest, ChatResponse
from collections.abc import AsyncGenerator


class GroqProvider(Provider):
    name = "groq"

    def __init__(self) -> None:
        self.headers = {
            "Authorization": f"Bearer {settings.groq_api_key}",
            "content-type": "application/json",
        }

    async def complete(self, request: ChatRequest) -> ChatResponse:
        payload = {
            "model": "groq/compound",
            "messages": [m.model_dump() for m in request.messages],
            "max_tokens": request.max_tokens,
        }
        try:
            async with httpx.AsyncClient(timeout=settings.request_timeout_seconds) as client:
                response = await client.post(settings.groq_url, headers=self.headers, json=payload)
                response.raise_for_status()
                data = response.json()
        except (httpx.HTTPError, httpx.TimeoutException) as e:
            raise ProviderError(f"groq call failed: {e}") from e

        answer_text = data["choices"][0]["message"]["content"]
        return ChatResponse(provider=self.name, answer=answer_text)

    async def stream(self, request: ChatRequest) -> AsyncGenerator[str, None]:
        payload = {
            "model": "groq/compound",
            "messages": [m.model_dump() for m in request.messages],
            "max_tokens": request.max_tokens,
            "stream": True,
        }

        try:
            async with httpx.AsyncClient(timeout=settings.request_timeout_seconds) as client:
                async with client.stream(
                    "POST", settings.groq_url, headers=self.headers, json=payload
                ) as response:
                    response.raise_for_status()
                    async for line in response.aiter_lines():
                        if not line.startswith("data:"):
                            continue
                        chunk = line[len("data:"):].strip()
                        if chunk in ("", "[DONE]"):
                            continue
                        event = json.loads(chunk)
                        delta = event["choices"][0]["delta"].get("content")
                        if delta:
                            yield delta
        except (httpx.HTTPError, httpx.TimeoutException, KeyError, json.JSONDecodeError) as e:
            raise ProviderError(f"groq stream failed: {e}") from e