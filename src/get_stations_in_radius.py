import math
from typing import List
from src import Station


def get_stations_in_radius(all_stations: list[Station], lat: float, lon: float, radius_km: float, count: int) -> List[Station]:
    """
    Filtert ALL_STATIONS nach Stationen, die im Umkreis liegen,
    sortiert nach Distanz aufsteigend und schneidet auf 'count' zu.
    """
    results = []
    for st in all_stations:
        dist = haversine_distance(lat, lon, st["latitude"], st["longitude"])
        if dist <= radius_km:
            st_copy = st.copy()
            st_copy["distance"] = round(dist, 2)
            results.append(st_copy)

    results.sort(key=lambda s: s["distance"])
    return results[:count]


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Berechnet die Distanz (in km) zwischen zwei Koordinaten via Haversine-Formel.
    """
    R = 6371.0  # Erdradius in km
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    a = (math.sin(d_lat / 2) ** 2
         + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(d_lon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c
    return distance