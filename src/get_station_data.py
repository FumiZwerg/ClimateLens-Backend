from typing import Optional
import requests
from fastapi import HTTPException

def get_station_data_from_ghcn(station_id: str, start_year: Optional[str], end_year: Optional[str], latitude: Optional[float] = None) -> dict:
    """
    Lädt GHCN-Daily-Daten (TMIN und TMAX) vom NOAA-Server für die gegebene station_id,
    aggregiert sie nach Jahr und Jahreszeit und gibt eine Struktur zurück,
    die Mittelwerte (min/max) enthält.
    Berücksichtigt dabei den Zeitraum (start_year/end_year) sowie die unterschiedliche
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
    tracked_years: set = set()

    year_data = {}

    def ensure_year_structure(y: int):
        if y not in year_data:
            year_data[y] = {
                "annual":  {"tmin_vals": [], "tmax_vals": []},
                "spring":  {"tmin_vals": [], "tmax_vals": []},
                "summer":  {"tmin_vals": [], "tmax_vals": []},
                "autumn":  {"tmin_vals": [], "tmax_vals": []},
                "winter":  {"tmin_vals": [], "tmax_vals": []},
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

    for line in lines:
        if len(line) < 269:
            continue

        original_year = int(line[11:15])
        month = int(line[15:17])
        element = line[17:21]
        tracked_years.add(original_year)

        if element not in ["TMIN", "TMAX"]:
            continue

        season, effective_year = get_seasons(original_year, month)
        if not (sy <= effective_year <= ey):
            continue

        ensure_year_structure(effective_year)

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

            if element == "TMIN":
                year_data[effective_year]["annual"]["tmin_vals"].append(val)
                year_data[effective_year][season]["tmin_vals"].append(val)
            elif element == "TMAX":
                year_data[effective_year]["annual"]["tmax_vals"].append(val)
                year_data[effective_year][season]["tmax_vals"].append(val)

    for e in range(sy, ey):
        if e not in tracked_years:
            ensure_year_structure(e)

            year_data[int(e)]["annual"]["tmin_vals"].append(None)
            year_data[int(e)]["spring"]["tmin_vals"].append(None)
            year_data[int(e)]["summer"]["tmin_vals"].append(None)
            year_data[int(e)]["autumn"]["tmin_vals"].append(None)
            year_data[int(e)]["winter"]["tmin_vals"].append(None)

            year_data[int(e)]["annual"]["tmax_vals"].append(None)
            year_data[int(e)]["spring"]["tmax_vals"].append(None)
            year_data[int(e)]["summer"]["tmax_vals"].append(None)
            year_data[int(e)]["autumn"]["tmax_vals"].append(None)
            year_data[int(e)]["winter"]["tmax_vals"].append(None)

    output_data = []
    all_years = sorted(year_data.keys())

    def calc_min_max(vals: dict) -> dict:
        try:
            if vals["tmin_vals"] and vals["tmin_vals"] is not None:
                min_val = round(sum(vals["tmin_vals"]) / len(vals["tmin_vals"]), 1)
            else:
                min_val = None
        except:
            min_val = None

        try:
            if vals["tmax_vals"] and vals["tmin_vals"] is not None:
                max_val = round(sum(vals["tmax_vals"]) / len(vals["tmax_vals"]), 1)
            else:
                max_val = None
        except:
            max_val = None

        return {"min": min_val, "max": max_val}

    for y in all_years:
        entry = {
            "year": y,
            "annual": calc_min_max(year_data[y]["annual"]),
            "spring": calc_min_max(year_data[y]["spring"]),
            "summer": calc_min_max(year_data[y]["summer"]),
            "autumn": calc_min_max(year_data[y]["autumn"]),
            "winter": calc_min_max(year_data[y]["winter"]),
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
