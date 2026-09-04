# Cortex — AI Orchestration Gateway

A resilient, provider-agnostic API gateway built with FastAPI that unifies multiple LLM providers behind a single, consistent interface — with real-time streaming, automatic failover, per-provider circuit breaking, and response caching.

Built as a deep-dive learning project into async Python and production-style API design. Every line was hand-written and debugged against real, live provider APIs — including real production-style incidents (model deprecations mid-build, silent failure modes, a leaked-then-rotated API key) that got debugged and fixed along the way, not glossed over.

## Live Demo

🔗 **[cortex-rnhl.onrender.com/docs](https://cortex-rnhl.onrender.com/docs)** — interactive API docs, try it directly in your browser
*(Hosted on a free tier — the first request after ~15 min of inactivity takes 30-60s to wake up.)*

## What it does

Every LLM provider (Groq, Gemini, etc.) has a different request format, response shape, and authentication scheme, and any single provider can fail, rate-limit, or deprecate a model without warning. Cortex abstracts all of that behind one consistent API:

```
POST /chat            → single complete response, cached, with automatic provider failover
POST /chat/stream      → real-time token streaming (Server-Sent Events), with pre-stream failover
GET  /health           → liveness check
GET  /health/deep      → live circuit breaker status per provider
```

If the primary provider is down, degraded, or rate-limited, Cortex automatically retries against a secondary provider — transparently, with no caller-visible downtime. Each caller is itself rate-limited to protect the gateway from being overwhelmed.

## Architecture

- **Abstract provider interface** (`app/providers/base.py`) — every provider implements the same `complete()` / `stream()` contract via Python's `ABC`, so new providers plug in without touching routing code. Two independent providers (Groq, Gemini) are implemented and live.
- **Per-provider circuit breakers** (`app/core/circuit_breaker.py`) — tracks consecutive failures per provider independently, trips open after a threshold to stop hammering a failing service, and half-opens after a cooldown to test recovery automatically.
- **Fallback routing** (`app/core/router.py`) — tries each healthy provider in order; on failure, moves to the next automatically. Implemented for both the non-streaming and streaming paths — the streaming version commits to a provider only after its first chunk succeeds, since headers can't be un-sent once a stream begins.
- **Normalized error handling** — a single `ProviderError` exception absorbs every failure mode (timeouts, malformed responses, HTTP errors, unexpected response shapes) so routing logic has one predictable thing to catch, regardless of the underlying provider.
- **Redis-backed response caching** (`app/core/cache.py`) — identical requests are served from cache with zero LLM API calls; caching is a pure optimization layer that degrades gracefully (silently no-ops) if Redis is unreachable, rather than taking the whole API down.
- **Redis-backed rate limiting** (`app/core/rate_limiter.py`) — atomic, per-caller fixed-window limiting via `INCR`/`EXPIRE`, protecting the gateway itself from being overwhelmed; also fails open if Redis is unreachable, consistent with the caching layer's resilience philosophy.
- **True async streaming** — a chained async generator (provider's SSE stream → provider layer → FastAPI route → client), forwarding tokens the moment they arrive with zero full-response buffering.

```
app/
├── main.py                    # FastAPI app entrypoint
├── config.py                   # centralized settings, loaded from .env
├── api/
│   ├── chat.py                  # /chat and /chat/stream routes
│   └── health.py                # /health and /health/deep routes
├── core/
│   ├── router.py                 # fallback routing across providers
│   ├── circuit_breaker.py        # per-provider failure tracking + recovery
│   ├── cache.py                  # Redis-backed response caching
│   └── rate_limiter.py           # Redis-backed per-caller rate limiting
├── providers/
│   ├── base.py                    # abstract Provider contract
│   ├── groq_provider.py           # Groq implementation
│   └── gemini_provider.py         # Gemini implementation
└── schemas/
    └── chat.py                    # request/response Pydantic models
```

## Tech stack

Python 3.13 · FastAPI · Pydantic v2 · httpx (async HTTP client) · Server-Sent Events · Redis (via Upstash) · python-dotenv · Render (deployment)

## Running locally

```bash
git clone https://github.com/VinayakTiwari7/cortex.git
cd cortex
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and fill in your own keys:
```bash
cp .env.example .env
```

```
GROQ_API_KEY=your_groq_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
REDIS_URL=your_redis_connection_string_here
```

`REDIS_URL` is optional — if omitted, caching silently no-ops and everything else works normally.

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

## License

MIT — see [LICENSE](LICENSE)