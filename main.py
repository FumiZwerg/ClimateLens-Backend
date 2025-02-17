from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from src import load_station_data, Station
from src import fetch_stations_query
from typing import List

ALL_STATIONS: list = []

@asynccontextmanager
async def lifespan(app: FastAPI):
    global ALL_STATIONS
    ALL_STATIONS = load_station_data()
    yield

app = FastAPI(lifespan=lifespan)

origins = [
    "http://localhost:4174",
    "http://127.0.0.1:4174",
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/stations-query", response_model=List[Station])
def fetch_stations_query_endpoint(
    latitude: float = Query(...),
    longitude: float = Query(...),
    radius: float = Query(...),
    count: int = Query(...)
):
    """
    Beispiel:
      GET /stations-query?latitude=52.52&longitude=13.405&radius=50&count=5
    """
    return fetch_stations_query(latitude, longitude, radius, count, ALL_STATIONS)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
