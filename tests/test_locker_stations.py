class TestLockerStations:
    async def test_list_empty(self, client):
        resp = await client.get("/api/v1/locker-stations/")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    async def test_create_station(self, client):
        payload = {
            "title": "Новая станция",
            "address": "ул. Новая, 10",
            "latitude": 55.5,
            "longitude": 37.5,
        }
        resp = await client.post("/api/v1/locker-stations/", json=payload)
        assert resp.status_code == 201
        data = resp.json()
        assert data["title"] == payload["title"]
        assert "id" in data
        assert data["total_cells"] is None
        assert data["occupied_cells"] is None
        assert data["free_cells"] is None

    async def test_get_station_counts(self, client, station_id, cell_id):
        resp = await client.get(f"/api/v1/locker-stations/{station_id}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_cells"] == 1
        assert data["occupied_cells"] == 0
        assert data["free_cells"] == 1

    async def test_get_station_counts_occupied(self, client, station_id, unique_phone):
        cell1 = await client.post("/api/v1/locker-cells/", json={
            "station_id": station_id, "number": 1, "size": "SMALL", "hourly_price": 50,
        })
        cell1_id = cell1.json()["id"]
        cell2 = await client.post("/api/v1/locker-cells/", json={
            "station_id": station_id, "number": 2, "size": "MEDIUM", "hourly_price": 80,
        })
        cell2_id = cell2.json()["id"]
        user = await client.post("/api/v1/users/", json={
            "phone": unique_phone, "full_name": "User",
        })
        user_id = user.json()["id"]
        rental = await client.post("/api/v1/rentals/", json={
            "user_id": user_id, "cell_id": cell1_id, "price_per_hour": 50,
        })
        rental_id = rental.json()["id"]
        await client.post(f"/api/v1/rentals/{rental_id}/start")
        resp = await client.get(f"/api/v1/locker-stations/{station_id}")
        data = resp.json()
        assert data["total_cells"] == 2
        assert data["occupied_cells"] == 1
        assert data["free_cells"] == 1

    async def test_list_aggregates(self, client):
        s1 = await client.post("/api/v1/locker-stations/", json={
            "title": "S1", "address": "A1", "latitude": 55.0, "longitude": 37.0,
        })
        s1_id = s1.json()["id"]
        s2 = await client.post("/api/v1/locker-stations/", json={
            "title": "S2", "address": "A2", "latitude": 55.1, "longitude": 37.1,
        })
        s2_id = s2.json()["id"]
        await client.post("/api/v1/locker-cells/", json={
            "station_id": s1_id, "number": 1, "size": "SMALL", "hourly_price": 50,
        })
        await client.post("/api/v1/locker-cells/", json={
            "station_id": s2_id, "number": 1, "size": "SMALL", "hourly_price": 50,
        })
        await client.post("/api/v1/locker-cells/", json={
            "station_id": s2_id, "number": 2, "size": "MEDIUM", "hourly_price": 80,
        })
        resp = await client.get("/api/v1/locker-stations/")
        data = resp.json()
        for s in data:
            if s["id"] == s1_id:
                assert s["total_cells"] == 1
                assert s["free_cells"] == 1
            elif s["id"] == s2_id:
                assert s["total_cells"] == 2
                assert s["free_cells"] == 2

    async def test_get_station_not_found(self, client):
        resp = await client.get("/api/v1/locker-stations/00000000-0000-0000-0000-000000000000")
        assert resp.status_code == 404
