class TestLockerStations:
    async def test_list_empty(self, auth_client):
        resp = await auth_client.get("/api/v1/locker-stations/")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    async def test_create_station(self, auth_client):
        payload = {
            "title": "Новая станция",
            "address": "ул. Новая, 10",
            "latitude": 55.5,
            "longitude": 37.5,
        }
        resp = await auth_client.post("/api/v1/locker-stations/", json=payload)
        assert resp.status_code == 201
        data = resp.json()
        assert data["title"] == payload["title"]
        assert "id" in data
        assert data["total_cells"] is None
        assert data["occupied_cells"] is None
        assert data["free_cells"] is None

    async def test_get_station_counts(self, auth_client, station_id, cell_id):
        resp = await auth_client.get(f"/api/v1/locker-stations/{station_id}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_cells"] == 1
        assert data["occupied_cells"] == 0
        assert data["free_cells"] == 1

    async def test_get_station_counts_occupied(self, auth_client, station_id):
        import uuid
        user_phone = f"+7{uuid.uuid4().hex[:10]}"
        cell1 = await auth_client.post("/api/v1/locker-cells/", json={
            "station_id": station_id, "number": 1, "size": "SMALL", "hourly_price": 50,
        })
        cell1_id = cell1.json()["id"]
        cell2 = await auth_client.post("/api/v1/locker-cells/", json={
            "station_id": station_id, "number": 2, "size": "MEDIUM", "hourly_price": 80,
        })
        cell2_id = cell2.json()["id"]
        user = await auth_client.post("/api/v1/users/", json={
            "phone": user_phone, "full_name": "User", "password": "testpass123",
        })
        assert user.status_code == 201, f"User creation failed: {user.text}"
        user_id = user.json()["id"]
        rental = await auth_client.post("/api/v1/rentals/", json={
            "user_id": user_id, "cell_id": cell1_id, "price_per_hour": 50,
        })
        rental_id = rental.json()["id"]
        await auth_client.post(f"/api/v1/rentals/{rental_id}/start")
        resp = await auth_client.get(f"/api/v1/locker-stations/{station_id}")
        data = resp.json()
        assert data["total_cells"] == 2
        assert data["occupied_cells"] == 1
        assert data["free_cells"] == 1

    async def test_list_aggregates(self, auth_client):
        s1 = await auth_client.post("/api/v1/locker-stations/", json={
            "title": "S1", "address": "A1", "latitude": 55.0, "longitude": 37.0,
        })
        s1_id = s1.json()["id"]
        s2 = await auth_client.post("/api/v1/locker-stations/", json={
            "title": "S2", "address": "A2", "latitude": 55.1, "longitude": 37.1,
        })
        s2_id = s2.json()["id"]
        await auth_client.post("/api/v1/locker-cells/", json={
            "station_id": s1_id, "number": 1, "size": "SMALL", "hourly_price": 50,
        })
        await auth_client.post("/api/v1/locker-cells/", json={
            "station_id": s2_id, "number": 1, "size": "SMALL", "hourly_price": 50,
        })
        await auth_client.post("/api/v1/locker-cells/", json={
            "station_id": s2_id, "number": 2, "size": "MEDIUM", "hourly_price": 80,
        })
        resp = await auth_client.get("/api/v1/locker-stations/")
        data = resp.json()
        for s in data:
            if s["id"] == s1_id:
                assert s["total_cells"] == 1
                assert s["free_cells"] == 1
            elif s["id"] == s2_id:
                assert s["total_cells"] == 2
                assert s["free_cells"] == 2

    async def test_get_station_not_found(self, auth_client):
        resp = await auth_client.get("/api/v1/locker-stations/00000000-0000-0000-0000-000000000000")
        assert resp.status_code == 404
