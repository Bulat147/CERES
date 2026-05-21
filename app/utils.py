import uuid
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Optional, Union

from geopy.distance import geodesic


def generate_uuid() -> str:
    """
    Генерация UUID строки.
    """
    return str(uuid.uuid4())


def calculate_distance(
    lat1: float, lon1: float, lat2: float, lon2: float
) -> float:
    """
    Расчет расстояния между двумя точками в километрах.
    Использует формулу Хаверсина.
    """
    return geodesic((lat1, lon1), (lat2, lon2)).kilometers


def calculate_rental_cost(
    started_at: datetime,
    ended_at: datetime,
    price_per_hour: Decimal,
    min_hours: int = 1,
) -> Decimal:
    """
    Расчет стоимости аренды.

    Args:
        started_at: Время начала аренды
        ended_at: Время окончания аренды
        price_per_hour: Цена за час
        min_hours: Минимальное количество часов (округление вверх)

    Returns:
        Итоговая стоимость
    """
    if not started_at or not ended_at:
        return Decimal("0")

    duration = ended_at - started_at
    hours = max(duration.total_seconds() / 3600, min_hours)
    # Округляем до целых часов вверх
    hours_rounded = int(hours) + (1 if hours % 1 > 0 else 0)
    return price_per_hour * Decimal(str(hours_rounded))


def validate_phone_number(phone: str) -> bool:
    """
    Простая валидация номера телефона.
    """
    # Убираем все нецифровые символы
    digits = ''.join(filter(str.isdigit, phone))
    # Проверяем длину (минимум 10 цифр для международного формата)
    return len(digits) >= 10


def mask_card_number(card_number: str) -> str:
    """
    Маскировка номера карты (последние 4 цифры).
    """
    if len(card_number) <= 4:
        return card_number
    return "**** " * 3 + card_number[-4:]


def format_datetime(dt: Optional[datetime]) -> Optional[str]:
    """
    Форматирование datetime в строку ISO 8601.
    """
    if dt is None:
        return None
    return dt.isoformat()


def parse_datetime(dt_str: str) -> Optional[datetime]:
    """
    Парсинг строки в datetime.
    """
    try:
        return datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
    except (ValueError, TypeError):
        return None


class GeoPoint:
    """
    Класс для работы с географическими координатами.
    """

    def __init__(self, latitude: float, longitude: float):
        self.latitude = latitude
        self.longitude = longitude

    def distance_to(self, other: 'GeoPoint') -> float:
        """
        Расчет расстояния до другой точки.
        """
        return calculate_distance(
            self.latitude, self.longitude,
            other.latitude, other.longitude
        )

    def to_dict(self) -> dict:
        return {
            "latitude": self.latitude,
            "longitude": self.longitude
        }