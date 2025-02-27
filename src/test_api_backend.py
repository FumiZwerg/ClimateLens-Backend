import requests

BASE_URL = "http://localhost:8000"  

# =============================
# API-Tests für die Endpunkte
# =============================

def test_api_fetch_stations_query():
    response = requests.get(f"{BASE_URL}/stations-query?latitude=52.166&longitude=20.967&radius=10&count=5")
    assert response.status_code == 200, f"Fehler: {response.status_code} {response.text}"
    json_data = response.json()
    assert isinstance(json_data, list), "Antwort sollte eine Liste sein"
    assert any(station["id"] == "PLM00012375" for station in json_data), "PLM00012375 sollte in der Antwort enthalten sein"

def test_api_get_station_data():
    response = requests.get(f"{BASE_URL}/station/data?stationId=PLM00012375&startYear=2000&endYear=2010")
    assert response.status_code == 200, f"Fehler: {response.status_code} {response.text}"
    json_data = response.json()
    assert "data" in json_data, "Antwort sollte 'data' enthalten"
    assert isinstance(json_data["data"], list), "Daten sollten eine Liste sein"

def test_api_get_station_data_south():
    response = requests.get(f"{BASE_URL}/station/data?stationId=ZI000067775&startYear=2000&endYear=2010")
    assert response.status_code == 200, f"Fehler: {response.status_code} {response.text}"
    json_data = response.json()
    assert "data" in json_data, "Antwort sollte 'data' enthalten"
    assert isinstance(json_data["data"], list), "Daten sollten eine Liste sein"
    
def test_api_invalid_station():
    response = requests.get(f"{BASE_URL}/station/data?stationId=INVALID_ID&startYear=2000&endYear=2010")
    assert response.status_code == 404, "Sollte 404 für ungültige Station zurückgeben"

