from typing import Optional
import requests
from fastapi import HTTPException


def get_station_data_from_ghcn(station_id: str, start_year: Optional[str], end_year: Optional[str]) -> dict:
    """
    Lädt GHCN-Daily-Daten (TMIN und TMAX) vom NOAA-Server für die gegebene station_id,
    aggregiert sie nach Jahr und Jahreszeit und gibt eine Struktur zurück,
    die Mittelwerte (min/max) enthält. Beispielausgabe:

    {
      "station_id": "USW00094846",
      "data": [
        {
          "year": 2000,
          "annual": {"min": -7.6, "max": 31.6},
          "spring": {"min": 4.9, "max": 14.3},
          "summer": {"min": 21.6, "max": 32.3},
          "autumn": {"min": 8.4, "max": 16.3},
          "winter": {"min": -8.9, "max": 6.9}
        },
        ...
      ]
    }
    """
    # 1) Station-File herunterladen
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

    # 2) Start- und Endjahr in int konvertieren (falls angegeben)
    sy = int(start_year) if start_year else 0
    ey = int(end_year) if end_year else 9999

    # 3) Aggregator: year_data[year]["annual"|"spring"|"summer"|"autumn"|"winter"]["tmin_vals"/"tmax_vals"]
    year_data = {}

    # Hilfsfunktion: initialisiert die Struktur für ein bestimmtes Jahr (falls nicht vorhanden)
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
        Für den Winter wird Dezember dem folgenden Jahr zugeordnet.

        Beispiel:
          - Für Dezember 2024 liefert die Funktion ("winter", 2025).
          - Für Januar/Februar 2025 liefert sie ("winter", 2025).
        """
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

    # 4) Zeilenweise durch das GHCN-Daily-Format
    for line in lines:
        # Minimale Zeilenlänge prüfen
        if len(line) < 269:
            continue

        # Aus dem fixed-width-Format: Jahr, Monat und Element
        original_year = int(line[11:15])  # z.B. "2001"
        month = int(line[15:17])  # z.B. "05"
        element = line[17:21]  # "TMAX", "TMIN", ...

        # Nur, wenn es sich um TMIN oder TMAX handelt
        if element not in ["TMIN", "TMAX"]:
            continue

        # Ermitteln von Jahreszeit und effektivem Jahr
        season, effective_year = get_seasons(original_year, month)

        # Nur, wenn das effektive Jahr im geforderten Bereich liegt
        if not (sy <= effective_year <= ey):
            continue

        # Jahresstruktur für das effektive Jahr sicherstellen
        ensure_year_structure(effective_year)

        # In GHCN-Daily: ab Spalte 21 folgen 31 Blöcke à 8 Zeichen (Tage 1..31)
        for day_idx in range(31):
            offset = 21 + day_idx * 8
            chunk = line[offset:offset + 8]

            # chunk[0:5] -> Wert, chunk[5] -> Qualität, chunk[6:8] -> Flags
            val_str = chunk[0:5].strip()
            if val_str == "-9999" or not val_str:
                # Fehlender Wert
                continue

            try:
                # TMIN/TMAX werden in 1/10 °C gespeichert
                val = int(val_str) / 10.0
            except ValueError:
                # Falls irgendein ungültiger Wert in val_str steht
                continue

            # Wert in die jeweiligen Aggregatoren werfen
            if element == "TMIN":
                year_data[effective_year]["annual"]["tmin_vals"].append(val)
                year_data[effective_year][season]["tmin_vals"].append(val)
            elif element == "TMAX":
                year_data[effective_year]["annual"]["tmax_vals"].append(val)
                year_data[effective_year][season]["tmax_vals"].append(val)

    # 5) Aus year_data ein Array von Dicts bauen (sortiert nach Jahr)
    output_data = []
    all_years = sorted(year_data.keys())

    # Hilfsfunktion, um min-/max-Werte schön aus tmin_vals/tmax_vals zu holen
    def calc_min_max(vals: dict) -> dict:
        """
        vals: z.B. {"tmin_vals": [...], "tmax_vals": [...]}
        Liefert z.B. {"min": -7.6, "max": 31.6} (oder None, wenn keine Daten)
        """

        if vals["tmin_vals"]:
            min_val = round(sum(vals["tmin_vals"]) / len(vals["tmin_vals"]), 1)
        else:
            min_val = None

        if vals["tmax_vals"]:
            max_val = round(sum(vals["tmax_vals"]) / len(vals["tmax_vals"]), 1)
        else:
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

    # Gebe einen 404-Error zurück, wenn es tatsächlich keine Temperaturdaten
    # für die Station im angegebenen Zeitraum gibt
    if not output_data:
        raise HTTPException(status_code=404, detail={
            "station_id": station_id,
            "error": "Not Found",
            "message" : "There is no station data in this period available",
        })

    # 6) Finale Rückgabe im gewünschten Format
    return {
        "station_id": station_id,
        "data": output_data
    }