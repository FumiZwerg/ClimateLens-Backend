from src import fetch_stations_query, get_stations_in_radius, get_station_data_from_ghcn
from src import load_station_data
from src.load_station_inventory import load_station_inventory

# =============================
# Tests für fetch_stations_query
# =============================

def test_fetch_stations_query():
    result = fetch_stations_query(52.166, 20.967, 10, 1, load_station_data())
    assert len(result) > 0, "Es sollten Stationsdaten aus dem Backend zurückkommen"
    assert any(station["id"] == "PLM00012375" for station in result), "PLM00012375 sollte in den API-Daten enthalten sein"

# =============================
# Tests für get_stations_in_radius
# =============================

def test_get_stations_in_radius():
    result = get_stations_in_radius(load_station_data(), 52.166, 20.967, 10, 2)
    assert len(result) > 0

# =============================
# Tests für get_station_data_from_ghcn
# =============================

def test_get_station_data_north():
    result = get_station_data_from_ghcn("PLM00012375", "2000", "2010", 52.166)
    assert "data" in result
    assert isinstance(result["data"], list)
    assert len(result["data"]) > 0

def test_get_station_data_south():
    result = get_station_data_from_ghcn("ZI000067775", "2000", "2010", -17.917)
    assert "data" in result
    assert isinstance(result["data"], list)
    assert len(result["data"]) > 0

# =============================
# Tests für load_station_data
# =============================

def test_load_station_data():
    result = load_station_data()
    assert len(result) > 0

def test_load_station_data_valid():
    result = load_station_data()
    assert len(result) > 0
    assert "id" in result[0]

def test_load_station_data_invalid():
    result = load_station_data()
    assert isinstance(result, list)

# =============================
# Tests für load_station_inventory
# =============================

def test_load_station_inventory():
    result = load_station_inventory()
    assert "PLM00012375" in result or "ZI000067775" in result
    if "PLM00012375" in result:
        assert result["PLM00012375"]["start_year"] <= 2000
        assert result["PLM00012375"]["end_year"] >= 2010
    if "ZI000067775" in result:
        assert result["ZI000067775"]["start_year"] <= 2000
        assert result["ZI000067775"]["end_year"] >= 2010

def test_load_station_inventory_invalid():
    result = load_station_inventory()
    assert isinstance(result, dict)

# =============================
# Test für leere Stationsliste
# =============================

def test_fetch_stations_query_empty():
    result = fetch_stations_query(52.166, 20.967, 10, 1, [])
    assert result == []