class TestRentals:
    async def test_create_rental_with_payment_method_id(self, auth_client, user_id, cell_id, payment_method_id):
        resp = await auth_client.post("/api/v1/rentals/", json={
            "user_id": user_id,
            "cell_id": cell_id,
            "price_per_hour": 60.00,
            "payment_method_id": payment_method_id,
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["payment_method_id"] == payment_method_id
        assert data["status"] == "CREATED"

    async def test_create_rental_without_payment_method_id(self, auth_client, user_id, cell_id):
        resp = await auth_client.post("/api/v1/rentals/", json={
            "user_id": user_id,
            "cell_id": cell_id,
            "price_per_hour": 60.00,
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["payment_method_id"] is None

    async def test_price_per_hour_is_float(self, auth_client, user_id, cell_id):
        resp = await auth_client.post("/api/v1/rentals/", json={
            "user_id": user_id, "cell_id": cell_id, "price_per_hour": 60.00,
        })
        rental_id = resp.json()["id"]
        resp = await auth_client.get(f"/api/v1/rentals/{rental_id}")
        data = resp.json()
        assert isinstance(data["price_per_hour"], float), f"Expected float, got {type(data['price_per_hour'])}"

    async def test_final_amount_is_nullable_float(self, auth_client, user_id, cell_id):
        resp = await auth_client.post("/api/v1/rentals/", json={
            "user_id": user_id, "cell_id": cell_id, "price_per_hour": 60.00,
        })
        rental_id = resp.json()["id"]
        resp = await auth_client.get(f"/api/v1/rentals/{rental_id}")
        data = resp.json()
        assert data["final_amount"] is None

    async def test_start_rental(self, auth_client, user_id, cell_id):
        resp = await auth_client.post("/api/v1/rentals/", json={
            "user_id": user_id, "cell_id": cell_id, "price_per_hour": 60.00,
        })
        rental_id = resp.json()["id"]
        resp = await auth_client.post(f"/api/v1/rentals/{rental_id}/start")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ACTIVE"
        assert data["opened_at"] is not None
        assert data["started_at"] is not None
        resp = await auth_client.get(f"/api/v1/locker-cells/{cell_id}")
        assert resp.json()["status"] == "ACTIVE"

    async def test_close_rental(self, auth_client, user_id, cell_id):
        resp = await auth_client.post("/api/v1/rentals/", json={
            "user_id": user_id, "cell_id": cell_id, "price_per_hour": 60.00,
        })
        rental_id = resp.json()["id"]
        await auth_client.post(f"/api/v1/rentals/{rental_id}/start")
        resp = await auth_client.post(f"/api/v1/rentals/{rental_id}/close")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "WAITING_CLOSE"
        assert data["closed_at"] is not None
        resp = await auth_client.get(f"/api/v1/locker-cells/{cell_id}")
        assert resp.json()["status"] == "PAYMENT"

    async def test_start_rental_invalid_status(self, auth_client, user_id, cell_id):
        resp = await auth_client.post("/api/v1/rentals/", json={
            "user_id": user_id, "cell_id": cell_id, "price_per_hour": 60.00,
        })
        rental_id = resp.json()["id"]
        await auth_client.post(f"/api/v1/rentals/{rental_id}/start")
        resp = await auth_client.post(f"/api/v1/rentals/{rental_id}/start")
        assert resp.status_code == 400

    async def test_filter_by_user_id(self, auth_client, user_id, cell_id):
        await auth_client.post("/api/v1/rentals/", json={
            "user_id": user_id, "cell_id": cell_id, "price_per_hour": 60.00,
        })
        resp = await auth_client.get(f"/api/v1/rentals/?user_id={user_id}")
        data = resp.json()
        assert len(data) >= 1
        for r in data:
            assert r["user_id"] == user_id

    async def test_filter_by_status(self, auth_client, user_id, cell_id):
        await auth_client.post("/api/v1/rentals/", json={
            "user_id": user_id, "cell_id": cell_id, "price_per_hour": 60.00,
        })
        resp = await auth_client.get(f"/api/v1/rentals/?status=CREATED")
        data = resp.json()
        assert len(data) >= 1
        for r in data:
            assert r["status"] == "CREATED"

    async def test_rental_not_found(self, auth_client):
        resp = await auth_client.get("/api/v1/rentals/00000000-0000-0000-0000-000000000000")
        assert resp.status_code == 404

    async def test_delete_rental(self, auth_client, user_id, cell_id):
        resp = await auth_client.post("/api/v1/rentals/", json={
            "user_id": user_id, "cell_id": cell_id, "price_per_hour": 60.00,
        })
        rental_id = resp.json()["id"]
        resp = await auth_client.delete(f"/api/v1/rentals/{rental_id}")
        assert resp.status_code == 204
        resp = await auth_client.get(f"/api/v1/rentals/{rental_id}")
        assert resp.status_code == 404
