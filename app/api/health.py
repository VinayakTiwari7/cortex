from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health():
    """Cheap liveness check — no external calls."""
    return {"status": "ok"}


@router.get("/health/deep")
async def deep_health():
    """Reports real breaker state for each provider, without making live calls."""
    from app.api.chat import groq_breaker, gemini_breaker

    providers = {
        "groq": {"circuit_open": groq_breaker.is_open()},
        "gemini": {"circuit_open": gemini_breaker.is_open()},
    }
    overall_ok = any(not p["circuit_open"] for p in providers.values())
    return {"status": "ok" if overall_ok else "degraded", "providers": providers}