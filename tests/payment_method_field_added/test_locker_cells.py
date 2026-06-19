class TestLockerCells:
    async def test_hourly_price_is_float(self, auth_client, station_id):
        resp = await auth_client.post("/api/v1/locker-cells/", json={
            "station_id": station_id, "number": 1, "size": "SMALL", "hourly_price": 60.00,
        })
        cell_id = resp.json()["id"]
        resp = await auth_client.get(f"/api/v1/locker-cells/{cell_id}")
        data = resp.json()
        assert isinstance(data["hourly_price"], float), f"Expected float, got {type(data['hourly_price'])}"
        assert data["hourly_price"] == 60.0

    async def test_title_field(self, auth_client, station_id):
        title = "Моя тестовая ячейка"
        resp = await auth_client.post("/api/v1/locker-cells/", json={
            "station_id": station_id, "number": 2, "title": title,
            "size": "LARGE", "hourly_price": 100.00,
        })
        data = resp.json()
        assert data["title"] == title

    async def test_title_default_empty(self, auth_client, station_id):
        resp = await auth_client.post("/api/v1/locker-cells/", json={
            "station_id": station_id, "number": 3, "size": "SMALL", "hourly_price": 50.00,
        })
        data = resp.json()
        assert isinstance(data["title"], str)

    async def test_filter_by_station_id(self, auth_client):
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
            "station_id": s1_id, "number": 2, "size": "MEDIUM", "hourly_price": 80,
        })
        await auth_client.post("/api/v1/locker-cells/", json={
            "station_id": s2_id, "number": 1, "size": "LARGE", "hourly_price": 120,
        })
        resp = await auth_client.get(f"/api/v1/locker-cells/?station_id={s1_id}")
        data = resp.json()
        assert len(data) == 2
        for cell in data:
            assert cell["station_id"] == s1_id
        resp = await auth_client.get(f"/api/v1/locker-cells/?station_id={s2_id}")
        assert len(resp.json()) == 1

    async def test_status_field_values(self, auth_client, station_id):
        resp = await auth_client.post("/api/v1/locker-cells/", json={
            "station_id": station_id, "number": 10, "size": "SMALL", "hourly_price": 50.00,
        })
        data = resp.json()
        assert data["status"] == "AVAILABLE"

    async def test_station_id_present_in_response(self, auth_client, station_id):
        resp = await auth_client.post("/api/v1/locker-cells/", json={
            "station_id": station_id, "number": 5, "size": "MEDIUM", "hourly_price": 75.00,
        })
        data = resp.json()
        assert data["station_id"] == station_id

    async def test_create_cell_no_station_404(self, auth_client):
        resp = await auth_client.post("/api/v1/locker-cells/", json={
            "station_id": "00000000-0000-0000-0000-000000000000",
            "number": 1, "size": "SMALL", "hourly_price": 50.00,
        })
        assert resp.status_code == 404

    async def test_get_cell_not_found(self, auth_client):
        resp = await auth_client.get("/api/v1/locker-cells/00000000-0000-0000-0000-000000000000")
        assert resp.status_code == 404
