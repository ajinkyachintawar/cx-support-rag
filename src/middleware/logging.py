import json
import time
from datetime import datetime, timezone
from pathlib import Path

import structlog
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from src.config import settings

logger = structlog.get_logger()


def append_audit_log(entry: dict):
    path = Path(settings.audit_log_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a") as f:
        f.write(json.dumps(entry, default=str) + "\n")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.perf_counter()
        response = await call_next(request)
        latency_ms = int((time.perf_counter() - start) * 1000)

        if request.url.path not in ("/health", "/docs", "/openapi.json"):
            logger.info(
                "http_request",
                method=request.method,
                path=request.url.path,
                status=response.status_code,
                latency_ms=latency_ms,
            )

        return response
