import logging
import sys
from typing import Optional

from loguru import logger


class InterceptHandler(logging.Handler):
    """
    Перехват логов стандартного logging и перенаправление в loguru.
    """

    def emit(self, record):
        # Получаем соответствующий уровень loguru
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Находим caller для корректного отображения
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def setup_logging(
        level: Optional[str] = None,
        json_logs: Optional[bool] = None,
        intercept_handlers: Optional[list] = None,
) -> None:
    """
    Настройка логирования для приложения.
    Args:
        level: Уровень логирования (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            Если None, используется значение из настроек
        json_logs: Форматировать логи в JSON (полезно для production)
            Если None, используется значение из настроек
        intercept_handlers: Список handlers для перехвата (по умолчанию все)
    """
    from app.config import settings

    if level is None:
        level = "DEBUG" if settings.DEBUG else settings.LOG_LEVEL
    if json_logs is None:
        json_logs = settings.JSON_LOGS
    if intercept_handlers is None:
        intercept_handlers = ["uvicorn", "uvicorn.access", "fastapi"]

    # Удаляем все handlers у loguru и добавляем свой
    logger.remove()
    if json_logs:
        logger.add(
            sys.stdout,
            level=level,
            serialize=True,
            backtrace=True,
            diagnose=True,
        )
    else:
        logger.add(
            sys.stdout,
            format=(
                "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
                "<level>{level: <8}</level> | "
                "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
                "<level>{message}</level>"
            ),
            level=level,
            backtrace=True,
            diagnose=True,
        )

    # Перехватываем логи стандартного logging
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

    for handler in intercept_handlers:
        logging.getLogger(handler).handlers = [InterceptHandler()]

    # При JSON-логах middleware уже пишет http_request — access-лог uvicorn дублирует
    if json_logs:
        logging.getLogger("uvicorn.access").setLevel(logging.WARNING)

    # Устанавливаем уровень логирования для SQLAlchemy
    logging.getLogger("sqlalchemy.engine").setLevel(
        logging.WARNING if level != "DEBUG" else logging.INFO
    )


# Создаем глобальный логгер
log = logger