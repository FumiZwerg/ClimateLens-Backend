import requests
import csv

STATIONS_CSV_URL = "https://www1.ncdc.noaa.gov/pub/data/ghcn/daily/ghcnd-stations.csv"

def load_station_data() -> list | None:
    all_stations: list = []

    """
    Lädt die ghcnd-stations.csv herunter und speichert diese in ALL_STATIONS.
    Da die Datei keine Kopfzeile hat, greifen wir fest auf Spalte 0..8 zu.
    Aufbau der ghcnd-stations.csv:

      0 station_id
      1 latitude
      2 longitude
      3 elevation
      4 state
      5 name
      6 gsn_flag
      7 hcn_crn_flag
      8 wmo_id

    :return station_data[list]
    """

    try:
        print("Starte Download der Stationsliste...")
        r = requests.get(STATIONS_CSV_URL, timeout=30)
        r.raise_for_status()
    except requests.RequestException as e:
        print(f"Fehler beim Download der CSV: {e}")
        # Falls nicht verfügbar bleibt ALL_STATIONS leer
        return None

    lines = r.text.splitlines()
    reader = csv.reader(lines)

    # Zeilenweise durchgehen
    for row in reader:
        # Mindestens 6 Spalten sollten vorhanden sein (id, lat, lon, elevation, state, name)
        if len(row) < 6:
            continue

        station_id = row[0].strip()
        lat_str = row[1].strip()
        lon_str = row[2].strip()
        name_str = row[5].strip() if len(row) >= 6 else ""

        # Nur verarbeiten, wenn lat/lon valide sind
        if not lat_str or not lon_str:
            continue

        try:
            lat = float(lat_str)
            lon = float(lon_str)
        except ValueError:
            # Ungültige Koordinaten => überspringen
            continue

        station_obj = {
            "id": station_id,
            "name": name_str,
            "latitude": lat,
            "longitude": lon,
            "distance": 0.0
        }
        all_stations.append(station_obj)

    print(f"CSV-Download abgeschlossen. Anzahl geladener Stationen: {len(all_stations)}")

    return all_stations