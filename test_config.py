#!/usr/bin/env python3
"""
Тестовый скрипт для проверки конфигурации приложения.
Запуск: python test_config.py
"""

import asyncio
import sys
import os

# Добавляем текущую директорию в путь Python
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


async def test_config():
    """Тестирование конфигурации приложения."""
    print("🔧 Тестирование конфигурации приложения...")
    
    try:
        from app.config import settings
        print(f"✅ Конфигурация загружена успешно")
        print(f"   PROJECT_NAME: {settings.PROJECT_NAME}")
        print(f"   DATABASE_TYPE: {settings.DATABASE_TYPE}")
        print(f"   DATABASE_URL: {settings.DATABASE_URL}")
        print(f"   DEBUG: {settings.DEBUG}")
    except Exception as e:
        print(f"❌ Ошибка загрузки конфигурации: {e}")
        return False
    
    return True


async def test_database_connection():
    """Тестирование подключения к базе данных."""
    print("\n🔌 Тестирование подключения к базе данных...")
    
    try:
        from app.db.database import engine
        from sqlalchemy import text
        
        async with engine.connect() as conn:
            # Простой запрос для проверки подключения
            result = await conn.execute(text("SELECT 1"))
            value = result.scalar()
            
            if value == 1:
                print(f"✅ Подключение к базе данных успешно")
                print(f"   Движок: {engine.url}")
                return True
            else:
                print(f"❌ Неожиданный результат запроса: {value}")
                return False
                
    except Exception as e:
        print(f"❌ Ошибка подключения к базе данных: {e}")
        return False


async def test_models_import():
    """Тестирование импорта моделей."""
    print("\n📦 Тестирование импорта моделей...")
    
    models = [
        "app.models.user.User",
        "app.models.locker_station.LockerStation",
        "app.models.locker_cell.LockerCell",
        "app.models.rental.Rental",
        "app.models.payment_method.PaymentMethod",
        "app.models.payment.Payment",
        "app.models.cell_event.CellEvent",
        "app.models.hardware_event.HardwareEvent",
    ]
    
    all_ok = True
    for model_path in models:
        try:
            module_name, class_name = model_path.rsplit('.', 1)
            module = __import__(module_name, fromlist=[class_name])
            cls = getattr(module, class_name)
            print(f"✅ {class_name}")
        except Exception as e:
            print(f"❌ {class_name}: {e}")
            all_ok = False
    
    return all_ok


async def main():
    """Основная функция тестирования."""
    print("🚀 Запуск тестов конфигурации CERES API\n")
    
    tests = [
        test_config(),
        test_database_connection(),
        test_models_import(),
    ]
    
    results = await asyncio.gather(*tests)
    
    print("\n" + "="*50)
    print("📊 Результаты тестирования:")
    print(f"   Конфигурация: {'✅' if results[0] else '❌'}")
    print(f"   База данных: {'✅' if results[1] else '❌'}")
    print(f"   Модели: {'✅' if results[2] else '❌'}")
    
    all_passed = all(results)
    if all_passed:
        print("\n🎉 Все тесты пройдены успешно!")
        print("Приложение готово к запуску.")
        print("\nЗапустите сервер командой:")
        print("   uvicorn app.main:app --reload")
    else:
        print("\n⚠️  Некоторые тесты не прошли.")
        print("Проверьте конфигурацию и зависимости.")
    
    return all_passed


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)