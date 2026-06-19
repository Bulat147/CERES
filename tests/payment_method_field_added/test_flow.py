import json
import uuid
import base64


class TestFullLifecycle:
    """
    Интеграционный тест полного жизненного цикла:
    Station → Cell → User → PaymentMethod → Rental → Start → Close → Payment
    """

    async def test_full_flow(self, client, unique_phone):
        # 0. Регистрируем пользователя и получаем токен
        auth_resp = await client.post("/api/v1/auth/register", json={
            "phone": unique_phone, "full_name": "Flow User",
            "password": "testpass123",
        })
        assert auth_resp.status_code == 200
        token = auth_resp.json()["access_token"]
        client.headers.update({"Authorization": f"Bearer {token}"})

        payload_b64 = token.split(".")[1]
        payload_b64 += "=" * (4 - len(payload_b64) % 4)
        user_id = json.loads(base64.urlsafe_b64decode(payload_b64))["sub"]

        # 1. Создаём станцию
        s = await client.post("/api/v1/locker-stations/", json={
            "title": "Интеграционная станция",
            "address": "пр. Тестовый, 42",
            "latitude": 55.7558,
            "longitude": 37.6173,
        })
        assert s.status_code == 201
        station_id = s.json()["id"]

        # 2. Создаём несколько ячеек
        c1 = await client.post("/api/v1/locker-cells/", json={
            "station_id": station_id, "number": 1, "title": "Ячейка 1",
            "size": "SMALL", "hourly_price": 60.00,
        })
        assert c1.status_code == 201
        cell_id = c1.json()["id"]
        assert isinstance(c1.json()["hourly_price"], float)
        assert c1.json()["title"] == "Ячейка 1"

        await client.post("/api/v1/locker-cells/", json={
            "station_id": station_id, "number": 2, "size": "LARGE", "hourly_price": 120.00,
        })

        # 3. Проверяем агрегаты станции
        gs = await client.get(f"/api/v1/locker-stations/{station_id}")
        assert gs.json()["total_cells"] == 2
        assert gs.json()["free_cells"] == 2
        assert gs.json()["occupied_cells"] == 0

        # 4. Создаём способ оплаты
        pm = await client.post("/api/v1/payment-methods/", json={
            "user_id": user_id, "provider": "YooKassa",
            "masked_pan": "**** **** **** 9999", "is_verified": True,
        })
        assert pm.status_code == 201
        method_id = pm.json()["id"]

        # 5. Создаём аренду с payment_method_id
        r = await client.post("/api/v1/rentals/", json={
            "user_id": user_id, "cell_id": cell_id,
            "price_per_hour": 60.00, "payment_method_id": method_id,
        })
        assert r.status_code == 201
        rental_id = r.json()["id"]
        assert r.json()["payment_method_id"] == method_id
        assert r.json()["status"] == "CREATED"
        assert isinstance(r.json()["price_per_hour"], float)

        # 6. Проверяем GET rental
        gr = await client.get(f"/api/v1/rentals/{rental_id}")
        assert gr.json()["payment_method_id"] == method_id
        assert gr.json()["final_amount"] is None

        # 7. Начинаем аренду
        rs = await client.post(f"/api/v1/rentals/{rental_id}/start")
        assert rs.status_code == 200
        assert rs.json()["status"] == "ACTIVE"
        assert rs.json()["opened_at"] is not None

        # 8. Проверяем что ячейка занята
        gc = await client.get(f"/api/v1/locker-cells/{cell_id}")
        assert gc.json()["status"] == "ACTIVE"

        # 9. Проверяем что агрегаты изменились
        gs = await client.get(f"/api/v1/locker-stations/{station_id}")
        assert gs.json()["occupied_cells"] == 1
        assert gs.json()["free_cells"] == 1

        # 10. Закрываем аренду
        rc = await client.post(f"/api/v1/rentals/{rental_id}/close")
        assert rc.status_code == 200
        assert rc.json()["status"] == "WAITING_CLOSE"
        assert rc.json()["closed_at"] is not None

        # 11. Проверяем статус ячейки
        gc = await client.get(f"/api/v1/locker-cells/{cell_id}")
        assert gc.json()["status"] == "PAYMENT"

        # 12. Создаём платеж с payment_method_id
        p = await client.post("/api/v1/payments/", json={
            "rental_id": rental_id, "user_id": user_id,
            "amount": 60.00, "payment_method_id": method_id,
        })
        assert p.status_code == 201
        payment_id = p.json()["id"]
        assert p.json()["payment_method_id"] == method_id
        assert isinstance(p.json()["amount"], float)

        # 13. Проверяем GET payment
        gp = await client.get(f"/api/v1/payments/{payment_id}")
        assert gp.json()["payment_method_id"] == method_id
        assert gp.json()["status"] == "PENDING"
