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
        response = await call_next(request)
        process_time = time.time() - start_time

        log.info(
            f"{request.method} {request.url.path} - "
            f"Status: {response.status_code} - "
            f"Duration: {process_time:.3f}s"
        )
        return response


def setup_middlewares(app: FastAPI) -> None:
    """
    Настройка middleware для приложения.
    """
    # CORS middleware уже добавлен в main.py
    # Добавляем logging middleware
    app.add_middleware(LoggingMiddleware)