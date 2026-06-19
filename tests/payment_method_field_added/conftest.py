import json
import uuid
import base64

import pytest_asyncio
from httpx import AsyncClient


BASE_URL = "http://localhost:8000"
# BASE_URL = "http://85.209.9.46:8000"


@pytest_asyncio.fixture
async def client():
    async with AsyncClient(base_url=BASE_URL, trust_env=False) as ac:
        yield ac


@pytest_asyncio.fixture
async def unique_phone():
    return f"+7{uuid.uuid4().hex[:10]}"


@pytest_asyncio.fixture
async def token(client, unique_phone):
    resp = await client.post("/api/v1/auth/register", json={
        "phone": unique_phone,
        "full_name": "Тестовый пользователь",
        "password": "testpass123",
    })
    assert resp.status_code == 200
    return resp.json()["access_token"]


@pytest_asyncio.fixture
async def auth_client(client, token):
    client.headers.update({"Authorization": f"Bearer {token}"})
    return client


@pytest_asyncio.fixture
async def user_id(token):
    payload_b64 = token.split(".")[1]
    payload_b64 += "=" * (4 - len(payload_b64) % 4)
    payload = json.loads(base64.urlsafe_b64decode(payload_b64))
    return payload["sub"]


@pytest_asyncio.fixture
async def station_id(auth_client):
    payload = {
        "title": "Тестовая станция",
        "address": "ул. Тестовая, 1",
        "latitude": 55.0,
        "longitude": 37.0,
    }
    resp = await auth_client.post("/api/v1/locker-stations/", json=payload)
    assert resp.status_code == 201
    return resp.json()["id"]


@pytest_asyncio.fixture
async def cell_id(auth_client, station_id):
    payload = {
        "station_id": station_id,
        "number": 1,
        "title": "Ячейка A1",
        "size": "SMALL",
        "hourly_price": 60.00,
    }
    resp = await auth_client.post("/api/v1/locker-cells/", json=payload)
    assert resp.status_code == 201
    return resp.json()["id"]


@pytest_asyncio.fixture
async def payment_method_id(auth_client, user_id):
    payload = {
        "user_id": user_id,
        "provider": "YooKassa",
        "masked_pan": "**** **** **** 1234",
        "is_verified": True,
    }
    resp = await auth_client.post("/api/v1/payment-methods/", json=payload)
    assert resp.status_code == 201
    return resp.json()["id"]
