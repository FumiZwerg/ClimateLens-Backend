from fastapi import Query
from . import get_stations_in_radius, Station

def fetch_stations_query(
    latitude: float = Query(...),
    longitude: float = Query(...),
    radius: float = Query(...),
    count: int = Query(...),
        all_stations=None
):
    """
    Beispiel:
      GET /stations-query?latitude=52.52&longitude=13.405&radius=50&count=5
    """
    if all_stations is None:
        all_stations = []
    if not all_stations:
        return []

    stations = get_stations_in_radius(all_stations, latitude, longitude, radius, count)
    return stations