class TestPayments:
    async def test_create_payment_with_payment_method_id(self, client, user_id, cell_id, payment_method_id):
        rental = await client.post("/api/v1/rentals/", json={
            "user_id": user_id, "cell_id": cell_id, "price_per_hour": 60.00,
        })
        rental_id = rental.json()["id"]
        resp = await client.post("/api/v1/payments/", json={
            "rental_id": rental_id,
            "user_id": user_id,
            "amount": 120.00,
            "payment_method_id": payment_method_id,
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["payment_method_id"] == payment_method_id
        assert data["amount"] == 120.0

    async def test_create_payment_without_payment_method_id(self, client, user_id, cell_id):
        rental = await client.post("/api/v1/rentals/", json={
            "user_id": user_id, "cell_id": cell_id, "price_per_hour": 60.00,
        })
        rental_id = rental.json()["id"]
        resp = await client.post("/api/v1/payments/", json={
            "rental_id": rental_id,
            "user_id": user_id,
            "amount": 60.00,
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["payment_method_id"] is None

    async def test_amount_is_float(self, client, user_id, cell_id):
        rental = await client.post("/api/v1/rentals/", json={
            "user_id": user_id, "cell_id": cell_id, "price_per_hour": 60.00,
        })
        rental_id = rental.json()["id"]
        resp = await client.post("/api/v1/payments/", json={
            "rental_id": rental_id, "user_id": user_id, "amount": 100.50,
        })
        payment_id = resp.json()["id"]
        resp = await client.get(f"/api/v1/payments/{payment_id}")
        data = resp.json()
        assert isinstance(data["amount"], float), f"Expected float, got {type(data['amount'])}"

    async def test_filter_by_rental_id(self, client, user_id, cell_id):
        rental = await client.post("/api/v1/rentals/", json={
            "user_id": user_id, "cell_id": cell_id, "price_per_hour": 60.00,
        })
        rental_id = rental.json()["id"]
        await client.post("/api/v1/payments/", json={
            "rental_id": rental_id, "user_id": user_id, "amount": 50.00,
        })
        resp = await client.get(f"/api/v1/payments/?rental_id={rental_id}")
        data = resp.json()
        assert len(data) >= 1
        for p in data:
            assert p["rental_id"] == rental_id

    async def test_filter_by_status(self, client, user_id, cell_id):
        rental = await client.post("/api/v1/rentals/", json={
            "user_id": user_id, "cell_id": cell_id, "price_per_hour": 60.00,
        })
        rental_id = rental.json()["id"]
        await client.post("/api/v1/payments/", json={
            "rental_id": rental_id, "user_id": user_id, "amount": 50.00,
        })
        resp = await client.get("/api/v1/payments/?status=PENDING")
        data = resp.json()
        assert len(data) >= 1
        for p in data:
            assert p["status"] == "PENDING"

    async def test_payment_not_found(self, client):
        resp = await client.get("/api/v1/payments/00000000-0000-0000-0000-000000000000")
        assert resp.status_code == 404
