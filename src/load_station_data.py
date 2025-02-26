import requests
import csv
from .load_station_inventory import load_station_inventory

STATIONS_CSV_URL = "https://www1.ncdc.noaa.gov/pub/data/ghcn/daily/ghcnd-stations.csv"

def load_station_data() -> list:
    all_stations: list = []
    try:
        print("Starte Download der Stationsliste...")
        r = requests.get(STATIONS_CSV_URL, timeout=30)
        r.raise_for_status()
    except requests.RequestException as e:
        print(f"Fehler beim Download der CSV: {e}")
        raise

    lines = r.text.splitlines()
    reader = csv.reader(lines)

    # Hole zusätzlich die Inventardaten
    inventory = load_station_inventory()

    for row in reader:
        # Es werden mindestens 6 Spalten benötigt: id, lat, lon, elevation, state, name
        if len(row) < 6:
            continue

        station_id = row[0].strip()
        lat_str = row[1].strip()
        lon_str = row[2].strip()
        name_str = row[5].strip()

        if not lat_str or not lon_str:
            continue

        try:
            lat = float(lat_str)
            lon = float(lon_str)
        except ValueError:
            continue

        # Füge Inventarinformationen hinzu, falls vorhanden
        inv = inventory.get(station_id, {})
        station_obj = {
            "id": station_id,
            "name": name_str,
            "latitude": lat,
            "longitude": lon,
            "distance": 0.0,
            "inventory_start_year": inv.get("start_year"),
            "inventory_end_year": inv.get("end_year")
        }
        all_stations.append(station_obj)

    print(f"CSV-Download abgeschlossen. Anzahl geladener Stationen: {len(all_stations)}")
    return all_stations
