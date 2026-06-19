# 🚀 CERES Locker Rental API

Backend API сервис для системы онлайн-аренды ячеек в постоматах через мобильное приложение.

## 📌 Описание

Система позволяет пользователям находить ближайшие постоматы, выбирать свободные ячейки, активировать их с оплатой, использовать, а затем завершать аренду с автоматическим расчётом стоимости и списанием средств.

## ⚙️ Стек технологий

* **FastAPI** - асинхронный веб-фреймворк
* **PostgreSQL** - реляционная база данных
* **SQLAlchemy 2.0** - асинхронный ORM
* **Alembic** - миграции базы данных
* **Pydantic v2** - валидация данных
* **Uvicorn** - ASGI сервер
* **Docker & Docker Compose** - контейнеризация

## 📦 Сущности системы

1. **Пользователь (User)** - регистрация и управление профилем
2. **Постомат (LockerStation)** - информация о местоположении и статусе
3. **Ячейка (LockerCell)** - характеристики, статус, цена
4. **Аренда (Rental)** - жизненный цикл аренды
5. **Способ оплаты (PaymentMethod)** - привязанные карты пользователя
6. **Платеж (Payment)** - история транзакций
7. **Событие ячейки (CellEvent)** - логирование действий с ячейками
8. **Событие оборудования (HardwareEvent)** - обработка аппаратных событий

## 🚀 Быстрый старт

### 1. Клонирование репозитория

```bash
git clone <repository-url>
cd ceres
```

### 2. Настройка окружения

Создайте файл `.env` на основе `.env.example`:

```bash
cp .env.example .env
```

Отредактируйте `.env` при необходимости.

### 3. Запуск базы данных

```bash
docker compose up -d
```

### 4. Установка зависимостей

Рекомендуется использовать виртуальное окружение:

```bash
python -m venv .venv
# Для Windows:
.venv\Scripts\activate
# Для Linux/Mac:
source .venv/bin/activate

pip install -r requirements.txt
```

### 5. Тестирование конфигурации (опционально)

```bash
python test_config.py
```

### 6. Применение миграций

```bash
alembic upgrade head
```

### 7. Запуск сервера разработки

```bash
uvicorn app.main:app --reload
```

Сервер будет доступен по адресу: [http://localhost:8000](http://localhost:8000)

### 8. Запуск тестов при запущенных через docker-compose контейнерах

```bash
cd tests
pytest -v --asyncio-mode=auto
```

## ⚡ Быстрый старт с SQLite (без Docker)

Для быстрого локального тестирования можно использовать SQLite:

1. Убедитесь, что в `.env` установлено `DATABASE_TYPE=sqlite`
2. Установите зависимости: `pip install -r requirements.txt`
3. Запустите тестовый скрипт: `python test_config.py`
4. Запустите сервер: `uvicorn app.main:app --reload`

## 📖 Документация API

После запуска сервера доступны:

* **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
* **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## 📁 Структура проекта

```
ceres/
├── alembic/              # Миграции базы данных
├── app/                  # Основной код приложения
│   ├── api/              # API endpoints
│   │   ├── users.py
│   │   ├── locker_stations.py
│   │   ├── locker_cells.py
│   │   ├── rentals.py
│   │   ├── payment_methods.py
│   │   ├── payments.py
│   │   ├── cell_events.py
│   │   └── hardware_events.py
│   ├── db/               # Работа с базой данных
│   │   ├── database.py   # Настройка подключения
│   │   └── crud.py       # Базовые CRUD операции
│   ├── models/           # SQLAlchemy модели
│   ├── schemas/          # Pydantic схемы
│   ├── config.py         # Конфигурация приложения
│   ├── logger.py         # Настройка логирования
│   ├── middlewares.py    # HTTP middleware
│   ├── utils.py          # Вспомогательные функции
│   └── main.py           # Точка входа
├── docker-compose.yaml   # Конфигурация Docker
├── Dockerfile            # Docker образ приложения
├── requirements.txt      # Зависимости Python
├── alembic.ini           # Конфигурация Alembic
└── README.md             # Документация
```

## 🔄 Жизненные циклы

### Ячейка (CellStatus)

```
AVAILABLE → RESERVED → ACTIVE → PAYMENT → AVAILABLE
```

* **AVAILABLE** - ячейка свободна
* **RESERVED** - пользователь выбрал ячейку, но ещё не активировал
* **ACTIVE** - ячейка открыта, пользователь кладёт вещи
* **PAYMENT** - пользователь закрыл дверь, система начинает расчёт
* **BLOCKED** - пользователь не оплатил, заблокирован до погашения долга
* **OFFLINE** - техническая неисправность

### Аренда (RentalStatus)

```
CREATED → ACTIVE → WAITING_CLOSE → PAYMENT → COMPLETED
```

* **CREATED** - пользователь выбрал ячейку, но ещё не оплатил
* **ACTIVE** - ячейка открыта, начат отсчёт времени
* **WAITING_CLOSE** - пользователь завершил использование, но не закрыл дверь
* **PAYMENT** - дверь закрыта, система запускает оплату
* **COMPLETED** - оплата прошла успешно, аренда завершена
* **CANCELLED** - пользователь отменил аренду до активации
* **OVERDUE** - не оплачено, начислен долг, блокировка

## 📋 Основные API endpoints

### Пользователи (`/api/v1/users`)
* `GET /` - список пользователей
* `POST /` - создание пользователя
* `GET /{user_id}` - информация о пользователе
* `PUT /{user_id}` - обновление пользователя
* `DELETE /{user_id}` - удаление пользователя

### Постоматы (`/api/v1/locker-stations`)
* `GET /` - список постоматов
* `POST /` - создание постомата
* `GET /{station_id}` - информация о постомате
* `PUT /{station_id}` - обновление постомата
* `DELETE /{station_id}` - удаление постомата

### Ячейки (`/api/v1/locker-cells`)
* `GET /` - список ячеек (с фильтрацией по station_id)
* `POST /` - создание ячейки
* `GET /{cell_id}` - информация о ячейке
* `PUT /{cell_id}` - обновление ячейки
* `DELETE /{cell_id}` - удаление ячейки

### Аренды (`/api/v1/rentals`)
* `GET /` - список аренд (с фильтрацией)
* `POST /` - создание аренды
* `GET /{rental_id}` - информация об аренде
* `PUT /{rental_id}` - обновление аренды
* `POST /{rental_id}/start` - начать аренду (открыть ячейку)
* `POST /{rental_id}/close` - закрыть аренду (пользователь закрыл дверь)

### Способы оплаты (`/api/v1/payment-methods`)
* `GET /` - список способов оплаты
* `POST /` - создание способа оплаты
* `GET /{method_id}` - информация о способе оплаты
* `PUT /{method_id}` - обновление способа оплаты
* `DELETE /{method_id}` - удаление способа оплаты

### Платежи (`/api/v1/payments`)
* `GET /` - список платежей
* `POST /` - создание платежа
* `GET /{payment_id}` - информация о платеже
* `PUT /{payment_id}` - обновление платежа
* `DELETE /{payment_id}` - удаление платежа

## 🐳 Docker развертывание

### Сборка и запуск

```bash
docker compose up --build
```

### Остановка

```bash
docker compose down
```

### Просмотр логов

**Grafana + Loki** (рекомендуется):

1. Запустите стек: `docker compose up -d`
2. Откройте Grafana: [http://localhost:3000](http://localhost:3000) (admin / пароль из `GRAFANA_ADMIN_PASSWORD`)
3. **Explore** → datasource **Loki** → запрос `{service="backend"}`
4. Или дашборд **CERES Logs** в папке CERES

Примеры LogQL:

* `{service="backend"} |= "http_request"` — HTTP-запросы API
* `{service="backend"} |~ "ERROR|WARNING"` — ошибки и предупреждения
* `{service="db"}` — логи PostgreSQL

Включите `JSON_LOGS=true` в `.env` для структурированных логов (по умолчанию в docker-compose).

**Терминал** (fallback):

```bash
docker compose logs -f backend
```

## 📊 Миграции базы данных

### Создание новой миграции

```bash
alembic revision --autogenerate -m "Описание изменений"
```

### Применение миграций

```bash
alembic upgrade head
```

### Откат миграции

```bash
alembic downgrade -1
```

## 🧪 Тестирование

*Для тестирования будут добавлены позже*

## 🤝 Вклад в проект

1. Форкните репозиторий
2. Создайте ветку для новой функции (`git checkout -b feature/amazing-feature`)
3. Зафиксируйте изменения (`git commit -m 'Add some amazing feature'`)
4. Отправьте в ветку (`git push origin feature/amazing-feature`)
5. Откройте Pull Request

## 📄 Лицензия

Этот проект лицензирован под MIT License - см. файл LICENSE для деталей.

## 📞 Контакты

*Проект разработан в рамках учебного/тестового задания*

---
**Примечание**: Это MVP версия системы. В будущем планируется добавление аутентификации, нотификаций, интеграции с платежными системами и аппаратным обеспечением.