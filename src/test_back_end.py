from pytest import fixture, raises
import requests
from fastapi import HTTPException
from unittest.mock import patch
from src import fetch_stations_query, get_stations_in_radius, get_station_data_from_ghcn
from src import load_station_data, load_station_inventory

# Erstellt Testdaten für die Stationen
@fixture
def test_stations():
    return [
        {"id": "S1", "name": "Station 1", "latitude": 52.52, "longitude": 13.405, "distance": 0.0},
        {"id": "S2", "name": "Station 2", "latitude": 52.5, "longitude": 13.4, "distance": 0.0},
    ]

# =============================
# Tests für fetch_stations_query
# =============================

# Testet die Funktion, die Stationen anhand der Entfernung filtert
@patch("src.get_stations_in_radius.get_stations_in_radius")
def test_fetch_stations_query(mock_get_stations, test_stations):
    mock_get_stations.return_value = test_stations[:1]  # Simuliert die Rückgabe einer Station
    result = fetch_stations_query(52.52, 13.405, 10, 1, test_stations)
    assert len(result) == 1  # Prüft, ob nur eine Station zurückgegeben wird
    assert result[0]["id"] == "S1"

# =============================
# Tests für get_stations_in_radius
# =============================

# Testet die Funktion, die Stationen innerhalb eines bestimmten Radius sucht
def test_get_stations_in_radius(test_stations):
    result = get_stations_in_radius(test_stations, 52.52, 13.405, 10, 2)
    assert len(result) == 2  # Überprüft, ob zwei Stationen gefunden werden


# =============================
# Tests für get_station_data_from_ghcn
# =============================

# Testet das Abrufen von Stationsdaten aus einer externen Quelle
@patch("requests.get")
def test_get_station_data_from_ghcn(mock_get):
    mock_get.return_value.status_code = 200
    mock_get.return_value.text = "S1 20200101 TMIN -50\nS1 20200101 TMAX 100"

    result = get_station_data_from_ghcn("S1", "2010", "2020", 52.52)

    assert "data" in result, "Antwort sollte 'data' enthalten"
    assert isinstance(result["data"], list), "Daten sollten eine Liste sein"
    assert len(result["data"]) > 0, "Die Liste sollte nicht leer sein"

@patch("requests.get")
def test_get_station_data_north_south(mock_get):
    mock_get.return_value.status_code = 200
    mock_get.return_value.text = "S1 20200101 TMIN -50\nS1 20200101 TMAX 100"

    result_north = get_station_data_from_ghcn("S1", "2010", "2020", 52.52)
    result_south = get_station_data_from_ghcn("S2", "2010", "2020", -33.86)

    assert "data" in result_north, "Antwort für Nordhalbkugel sollte 'data' enthalten"
    assert "data" in result_south, "Antwort für Südhalbkugel sollte 'data' enthalten"

@patch("requests.get")
def test_get_station_data_success(mock_get):
    mock_get.return_value.status_code = 200
    mock_get.return_value.text = "S1 20200101 TMIN -50\nS1 20200101 TMAX 100"

    result = get_station_data_from_ghcn("S1", "2010", "2020", 52.52)

    assert "data" in result, "Antwort sollte 'data' enthalten"
    assert isinstance(result["data"], list), "Daten sollten eine Liste sein"

@patch("requests.get")
def test_get_station_data_api_failure(mock_get):
    mock_get.side_effect = requests.exceptions.RequestException("API Error")

    with raises(HTTPException):
        get_station_data_from_ghcn("S1", "2010", "2020", 52.52)

# =============================
# Tests für load_station_data
# =============================


# Testet das Laden von Stationsdaten aus einer CSV-Datei
@patch("requests.get")
def test_load_station_data(mock_get):
    mock_get.return_value.status_code = 200
    mock_get.return_value.text = "S1,52.52,13.405,100,DE,Station 1\nS2,52.5,13.4,200,DE,Station 2"
    result = load_station_data()
    assert len(result) > 0  # Stellt sicher, dass mindestens eine Station geladen wird

@patch("requests.get")
def test_load_station_data_valid(mock_get):
    mock_get.return_value.status_code = 200
    mock_get.return_value.text = "S1,52.52,13.405,100,DE,Station 1\nS2,52.5,13.4,200,DE,Station 2"

    result = load_station_data()

    assert len(result) > 0, "Es sollten Stationen geladen werden"
    assert "id" in result[0], "Jede Station sollte eine 'id' haben"

@patch("requests.get")
def test_load_station_data_invalid(mock_get):
    mock_get.return_value.status_code = 200
    mock_get.return_value.text = ""

    result = load_station_data()

    assert result == [], "Sollte eine leere Liste zurückgeben"

# =============================
# Tests für load_station_inventory
# =============================

# Testet das Laden des Stationsinventars mit Jahresangaben
@patch("requests.get")
def test_load_station_inventory(mock_get):
    mock_get.return_value.status_code = 200
    mock_get.return_value.text = "S1 TMIN 2000 2020\nS1 TMAX 2000 2020"

    result = load_station_inventory()

    assert "S1" in result, "Die Stations-ID 'S1' sollte im Inventar enthalten sein"
    assert result["S1"]["start_year"] == 2000, "Das Startjahr sollte 2000 sein"
    assert result["S1"]["end_year"] == 2020, "Das Endjahr sollte 2020 sein"


# Testet das Verhalten, wenn keine Stationen vorhanden sind
def test_fetch_stations_query_empty():
    result = fetch_stations_query(52.52, 13.405, 10, 1, [])
    assert result == []  # Sollte eine leere Liste zurückgeben


@patch("requests.get")
def test_load_station_inventory_invalid(mock_get):
    mock_get.return_value.status_code = 200
    mock_get.return_value.text = ""

    result = load_station_inventory()

    assert result == {}, "Sollte ein leeres Dictionary zurückgeben"