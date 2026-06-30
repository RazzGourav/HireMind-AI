"""FastAPI Middlewares."""

import time
import uuid
from collections.abc import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from hiremind.infrastructure import logger


class RequestTimingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        request_id = str(uuid.uuid4())
        start_time = time.perf_counter()

        response = await call_next(request)

        process_time = (time.perf_counter() - start_time) * 1000.0
        response.headers["X-Process-Time-Ms"] = str(round(process_time, 2))
        response.headers["X-Request-ID"] = request_id

        logger.info(
            f"API Request: {request.method} {request.url.path} "
            f"- Status: {response.status_code} "
            f"- Latency: {process_time:.2f}ms"
        )

        return response
