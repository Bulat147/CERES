# 🚀 FastAPI Backend Project

## 📌 Описание

Backend API сервис, реализованный на FastAPI.
Использует PostgreSQL, SQLAlchemy и Alembic для работы с базой данных.

---

## ⚙️ Стек технологий

* FastAPI
* PostgreSQL
* SQLAlchemy
* Alembic
* Docker

---

## 🚀 Запуск проекта

### 1. Поднять базу данных

```bash
docker compose up -d
```

### 2. Создать виртуальное окружение

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Установить зависимости

```bash
pip install -r requirements.txt
```

### 4. Применить миграции

```bash
alembic upgrade head
```

### 5. Запустить сервер

```bash
uvicorn app.main:app --reload
```

---

## 📁 Структура проекта

```
app/
├── api/                # Роуты (контроллеры)
│   └── users.py
│
├── core/               # Конфигурация и инфраструктура
│   ├── config.py
│   └── database.py
│
├── dependencies/       # Dependency Injection
│   ├── db.py
│   └── services.py
│
├── dto                 # Pydantic схемы (DTO)
│   └──user_dto.py
│
├── models/             # ORM модели (SQLAlchemy)
│   └── user_model.py
│
├── repositories/       # Работа с БД
│   └── user_repository.py
│
├── services/           # Бизнес-логика
│   └── user_service.py
│
└── main.py             # Точка входа

alembic/                # Миграции базы данных

docker/                 # Работа с docker

requirements.txt        # Зависимости проекта
```

---

## 📖 Документация API

Swagger UI доступен по эндпоинту (после запуска):

```
GET /docs
```
