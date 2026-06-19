class TestPaymentMethods:
    async def test_create_payment_method(self, auth_client, user_id):
        resp = await auth_client.post("/api/v1/payment-methods/", json={
            "user_id": user_id,
            "provider": "YooKassa",
            "masked_pan": "**** **** **** 1234",
            "is_verified": True,
        })
        assert resp.status_code == 201
        data = resp.json()
        assert "id" in data
        assert data["provider"] == "YooKassa"
        assert data["masked_pan"] == "**** **** **** 1234"
        assert data["is_verified"] is True
        assert data["user_id"] == user_id

    async def test_get_payment_method_by_id(self, auth_client, user_id):
        resp = await auth_client.post("/api/v1/payment-methods/", json={
            "user_id": user_id, "provider": "Sberbank",
            "masked_pan": "**** **** **** 5678", "is_verified": False,
        })
        method_id = resp.json()["id"]
        resp = await auth_client.get(f"/api/v1/payment-methods/{method_id}")
        data = resp.json()
        assert data["masked_pan"] == "**** **** **** 5678"
        assert data["provider"] == "Sberbank"

    async def test_filter_by_user_id(self, auth_client, user_id):
        await auth_client.post("/api/v1/payment-methods/", json={
            "user_id": user_id, "provider": "YooKassa",
            "masked_pan": "**** **** **** 1111", "is_verified": True,
        })
        resp = await auth_client.get(f"/api/v1/payment-methods/?user_id={user_id}")
        data = resp.json()
        assert len(data) >= 1
        for m in data:
            assert m["user_id"] == user_id

    async def test_create_payment_method_no_user_404(self, auth_client):
        resp = await auth_client.post("/api/v1/payment-methods/", json={
            "user_id": "00000000-0000-0000-0000-000000000000",
            "provider": "YooKassa",
            "masked_pan": "**** **** **** 0000",
            "is_verified": False,
        })
        assert resp.status_code == 404

    async def test_update_payment_method(self, auth_client, user_id):
        resp = await auth_client.post("/api/v1/payment-methods/", json={
            "user_id": user_id, "provider": "YooKassa",
            "masked_pan": "**** **** **** 2222", "is_verified": False,
        })
        method_id = resp.json()["id"]
        resp = await auth_client.put(f"/api/v1/payment-methods/{method_id}", json={"is_verified": True})
        assert resp.status_code == 200
        assert resp.json()["is_verified"] is True
