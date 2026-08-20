# Cortex — AI Orchestration Gateway

A resilient, provider-agnostic API gateway built with FastAPI that unifies multiple LLM providers behind a single, consistent interface — with real-time streaming, and (in progress) automatic failover and circuit breaking.

Built as a deep-dive learning project into async Python and production-style API design, not a scaffolded tutorial project — every line was hand-written and debugged against real, live provider APIs.

## Live Demo

🔗 **[cortex-xxxx.onrender.com/docs](#)** — interactive API docs, try it directly in your browser
*(Note: hosted on a free tier — the first request after inactivity may take 30–60s to wake up)*

## What it does

Every LLM provider (Anthropic, OpenAI, Groq, etc.) has a different request format, response shape, and authentication scheme. Cortex abstracts all of that behind one consistent API, so calling code never needs to know or care which provider is actually answering.

```
POST /chat            → single complete response
POST /chat/stream      → real-time token streaming (Server-Sent Events)
```

## Architecture

- **Abstract provider interface** (`app/providers/base.py`) — every provider implements the same `complete()` / `stream()` contract via Python's `ABC`, so new providers plug in without touching routing code
- **Normalized error handling** — a single `ProviderError` exception absorbs every failure mode (timeouts, malformed responses, HTTP errors) so upstream logic has one predictable thing to catch
- **True async streaming** — a chained async generator (provider's SSE stream → provider layer → FastAPI route → client), forwarding tokens the moment they arrive with zero full-response buffering
- **Pydantic schemas** as the data contract between layers, giving free request validation and consistent response shapes regardless of which provider answered

```
app/
├── main.py                 # FastAPI app entrypoint
├── config.py                # centralized settings, loaded from .env
├── api/
│   └── chat.py               # /chat and /chat/stream routes
├── providers/
│   ├── base.py                # abstract Provider contract
│   └── groq_provider.py       # Groq implementation
├── core/                    # circuit breaker / routing logic (in progress)
└── schemas/
    └── chat.py                # request/response Pydantic models
```

## Tech stack

Python 3.13 · FastAPI · Pydantic v2 · httpx (async HTTP client) · Server-Sent Events · python-dotenv

## Running locally

```bash
git clone https://github.com/VinayakTiwari7/cortex.git
cd cortex
pip install -r requirements.txt
```

Create a `.env` file in the project root:
```
GROQ_API_KEY=your_groq_api_key_here
```

Run the server:
```bash
python -m uvicorn app.main:app --reload
```

Visit `http://127.0.0.1:8000/docs` for interactive API docs.

## Example usage

```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "What is 7 times 8?"}], "max_tokens": 100}'
```

Streaming:
```bash
curl -N -X POST http://127.0.0.1:8000/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "Tell me a short story"}], "max_tokens": 300}'
```

## Roadmap

- [x] Unified chat endpoint with provider normalization
- [x] Real-time streaming via SSE
- [ ] Circuit breaker for automatic failure detection and recovery
- [ ] Multi-provider fallback routing
- [ ] Response caching (Redis)
- [ ] Rate limiting per API key
- [ ] Structured logging and observability

## License

MIT