import httpx

from app.core.settings import settings

_ai_client: httpx.AsyncClient | None = None


async def connect_ai():
    global _ai_client

    _ai_client = httpx.AsyncClient(
        base_url=settings.AI_BASE_URL,
        timeout=60.0,
        headers={
            "Authorization": f"Bearer {settings.AI_BASE_URL}",
            "Content-Type": "application/json",
        },
    )


async def disconnect_ai():
    global _ai_client

    if _ai_client:
        await _ai_client.aclose()


def get_ai_client() -> httpx.AsyncClient:
    if _ai_client is None:
        raise RuntimeError("AI client is not initialized.")

    return _ai_client