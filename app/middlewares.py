from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
import time

from app.logger import log


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware для логирования HTTP запросов.
    """

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        status_code = 500
        try:
            response = await call_next(request)
            status_code = response.status_code
            return response
        finally:
            duration_ms = round((time.time() - start_time) * 1000, 2)
            log.bind(
                method=request.method,
                path=request.url.path,
                status_code=status_code,
                duration_ms=duration_ms,
            ).info("http_request")


def setup_middlewares(app: FastAPI) -> None:
    """
    Настройка middleware для приложения.
    """
    # CORS middleware уже добавлен в main.py
    # Добавляем logging middleware
    app.add_middleware(LoggingMiddleware)