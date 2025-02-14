from src import Station, get_stations_in_radius
from src import load_station_data
from contextlib import asynccontextmanager
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List

ALL_STATIONS: list[Station] = []

@asynccontextmanager
async def lifespan(app: FastAPI):
    global ALL_STATIONS
    ALL_STATIONS = load_station_data()
    yield
app = FastAPI(lifespan=lifespan)

origins = [
    "http://localhost:4174",  # Erlaubt spezifischen Port für lokale Entwicklung
    "http://127.0.0.1:4174",
    "*"                       # Falls alle Domains erlaubt sein sollen (Entwicklung), aber unsicher für Produktion
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],      # Erlaubt alle HTTP-Methoden (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"], )    # Erlaubt alle Header


@app.get("/stations-query", response_model=List[Station])

def fetch_stations_query(
    latitude: float = Query(...),
    longitude: float = Query(...),
    radius: float = Query(...),
    count: int = Query(...)
):
    """
    Beispiel:
      GET /stations-query?latitude=52.52&longitude=13.405&radius=50&count=5
    """

    if not ALL_STATIONS:
        return []

    stations = get_stations_in_radius(ALL_STATIONS, latitude, longitude, radius, count)
    return stations


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)