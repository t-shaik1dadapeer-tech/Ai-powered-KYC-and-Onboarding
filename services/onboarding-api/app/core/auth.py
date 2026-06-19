from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.core.config import get_settings

_PUBLIC_PREFIXES = ("/health", "/metrics", "/docs", "/openapi.json", "/redoc")


class ApiKeyMiddleware(BaseHTTPMiddleware):
    """Optional API key gate — disabled when settings.api_key is empty (dev/test)."""

    async def dispatch(self, request: Request, call_next):
        settings = get_settings()
        if not settings.api_key:
            return await call_next(request)

        path = request.url.path
        if any(path == p or path.startswith(f"{p}/") for p in _PUBLIC_PREFIXES):
            return await call_next(request)

        if request.headers.get("X-API-Key") != settings.api_key:
            return JSONResponse(status_code=401, content={"detail": "Invalid or missing API key"})
        return await call_next(request)
