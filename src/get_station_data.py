from typing import Optional
import requests
from fastapi import HTTPException

def get_station_data_from_ghcn(station_id: str, start_year: Optional[str], end_year: Optional[str], latitude: Optional[float] = None) -> dict:
    """
    Lädt GHCN-Daily-Daten (TMIN und TMAX) vom NOAA-Server für die gegebene station_id,
    aggregiert sie nach Jahr und Jahreszeit und gibt eine Struktur zurück,
    die Mittelwerte (min/max) enthält.
    Für den "Annual"-Fall werden die Daten vom 01.01. bis 31.12. des Kalenderjahres berechnet.
    Es wird der Zeitraum (start_year/end_year) berücksichtigt sowie die unterschiedliche
    Jahreszeiten-Zuordnung für Nord- und Südhalbkugel (bei Übergabe von latitude).
    """
    ghcn_url = f"https://www1.ncdc.noaa.gov/pub/data/ghcn/daily/all/{station_id}.dly"
    try:
        r = requests.get(ghcn_url, timeout=30)
        r.raise_for_status()
    except requests.RequestException as e:
        print(f"Fehler beim Download von {ghcn_url}: {e}")
        raise HTTPException(status_code=404, detail={
            "station_id": station_id,
            "error": "Not Found",
            "message" : "There is no station data available",
        })

    lines = r.text.splitlines()

    sy = int(start_year) if start_year else 0
    ey = int(end_year) if end_year else 9999

    # Zwei separate Dictionaries: eins für die Annual-Aggregation (Kalenderjahr) und
    # eins für die saisonale Aggregation (effektives Jahr, ggf. verschoben)
    annual_data = {}    # Schlüssel: original_year
    seasonal_data = {}  # Schlüssel: effective_year

    def ensure_annual_structure(y: int):
        if y not in annual_data:
            annual_data[y] = {
                "tmin_vals": [],
                "tmax_vals": [],
            }

    def ensure_seasonal_structure(y: int):
        if y not in seasonal_data:
            seasonal_data[y] = {
                "spring": {"tmin_vals": [], "tmax_vals": []},
                "summer": {"tmin_vals": [], "tmax_vals": []},
                "autumn": {"tmin_vals": [], "tmax_vals": []},
                "winter": {"tmin_vals": [], "tmax_vals": []},
            }

    def get_seasons(year: int, month: int) -> tuple[str, int]:
        """
        Ermittelt die Jahreszeit und das effektive Jahr.
        Berücksichtigt dabei die Hemisphäre:
        - Südhalbkugel (latitude < 0):
            Dezember, Januar, Februar → summer
            März bis Mai → autumn
            Juni bis August → winter
            September bis November → spring
        - Nordhalbkugel (default):
            Dezember → winter (Zugehörigkeit zum Folgejahr)
            Januar, Februar → winter
            März bis Mai → spring
            Juni bis August → summer
            September bis November → autumn
        """
        if latitude is not None and latitude < 0:
            # Südhalbkugel
            if month in [12, 1, 2]:
                return "summer", year
            elif month in [3, 4, 5]:
                return "autumn", year
            elif month in [6, 7, 8]:
                return "winter", year
            else:
                return "spring", year
        else:
            # Nordhalbkugel (default)
            if month == 12:
                return "winter", year + 1
            elif month in [1, 2]:
                return "winter", year
            elif month in [3, 4, 5]:
                return "spring", year
            elif month in [6, 7, 8]:
                return "summer", year
            else:
                return "autumn", year

    def get_annual_year(year: int, month: int) -> int:
        """
        Bestimmt das Kalenderjahr für den "Annual"-Fall, unabhängig von der Jahreszeitenzuordnung.
        Für Annual wird immer das originale Jahr verwendet.
        """
        return year

    for line in lines:
        if len(line) < 269:
            continue

        original_year = int(line[11:15])
        month = int(line[15:17])
        element = line[17:21]

        if element not in ["TMIN", "TMAX"]:
            continue

        # Für Annual immer das originale Jahr; für Season die verschobene Zuordnung
        annual_year = get_annual_year(original_year, month)
        season, effective_year = get_seasons(original_year, month)

        # Prüfe, ob die Daten in den jeweiligen Bereich fallen
        annual_in_range = sy <= annual_year <= ey
        seasonal_in_range = sy <= effective_year <= ey

        for day_idx in range(31):
            offset = 21 + day_idx * 8
            chunk = line[offset:offset + 8]
            val_str = chunk[0:5].strip()
            if val_str == "-9999" or not val_str:
                continue

            try:
                val = int(val_str) / 10.0
            except ValueError:
                continue

            if annual_in_range:
                ensure_annual_structure(annual_year)
                if element == "TMIN":
                    annual_data[annual_year]["tmin_vals"].append(val)
                elif element == "TMAX":
                    annual_data[annual_year]["tmax_vals"].append(val)

            if seasonal_in_range:
                ensure_seasonal_structure(effective_year)
                if element == "TMIN":
                    seasonal_data[effective_year][season]["tmin_vals"].append(val)
                elif element == "TMAX":
                    seasonal_data[effective_year][season]["tmax_vals"].append(val)

    # Für jedes Jahr im betrachteten Zeitraum sicherstellen, dass auch Einträge existieren
    all_years = set(range(sy, ey + 1))
    for e in all_years:
        if e not in annual_data:
            annual_data[e] = {"tmin_vals": [None], "tmax_vals": [None]}
        if e not in seasonal_data:
            seasonal_data[e] = {
                "spring": {"tmin_vals": [None], "tmax_vals": [None]},
                "summer": {"tmin_vals": [None], "tmax_vals": [None]},
                "autumn": {"tmin_vals": [None], "tmax_vals": [None]},
                "winter": {"tmin_vals": [None], "tmax_vals": [None]},
            }

    def calc_min_max(vals: dict) -> dict:
        try:
            if vals["tmin_vals"]:
                min_val = round(sum(vals["tmin_vals"]) / len(vals["tmin_vals"]), 1)
            else:
                min_val = None
        except Exception:
            min_val = None

        try:
            if vals["tmax_vals"]:
                max_val = round(sum(vals["tmax_vals"]) / len(vals["tmax_vals"]), 1)
            else:
                max_val = None
        except Exception:
            max_val = None

        return {"min": min_val, "max": max_val}

    output_data = []
    for y in sorted(all_years):
        entry = {
            "year": y,
            "annual": calc_min_max(annual_data[y]),
            "spring": calc_min_max(seasonal_data[y]["spring"]),
            "summer": calc_min_max(seasonal_data[y]["summer"]),
            "autumn": calc_min_max(seasonal_data[y]["autumn"]),
            "winter": calc_min_max(seasonal_data[y]["winter"]),
        }
        output_data.append(entry)

    if not output_data:
        raise HTTPException(status_code=404, detail={
            "station_id": station_id,
            "error": "Not Found",
            "message" : "There is no station data in this period available",
        })

    return {
        "station_id": station_id,
        "data": output_data
    }
