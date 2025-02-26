from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from src import load_station_data, Station, get_station_data_from_ghcn
from src import fetch_stations_query
from typing import List, Optional

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
    count: int = Query(...),
    startYear: Optional[int] = Query(None),
    endYear: Optional[int] = Query(None)
):
    """
    Beispiel:
      GET /stations-query?latitude=52.52&longitude=13.405&radius=50&count=5&startYear=1980&endYear=2020
    """
    filtered_stations = ALL_STATIONS
    if startYear is not None or endYear is not None:
        filtered = []
        for st in ALL_STATIONS:
            inv_start = st.get("inventory_start_year")
            inv_end = st.get("inventory_end_year")
            if startYear is not None:
                if inv_start is None or inv_start > startYear:
                    continue
            if endYear is not None:
                if inv_end is None or inv_end < endYear:
                    continue
            filtered.append(st)
        filtered_stations = filtered

    return fetch_stations_query(latitude, longitude, radius, count, filtered_stations)

@app.get("/station/data")
def fetch_station_data(
    stationId: str = Query(...),
    startYear: Optional[str] = Query(None),
    endYear: Optional[str] = Query(None)
):
    """
    GET-Endpoint:
    Beispiel:
      GET /station/data?stationId=USW00094846&startYear=2000&endYear=2020
    """
    # Ermittle anhand der ALL_STATIONS den Latitude-Wert der Station
    latitude = None
    for st in ALL_STATIONS:
        if st["id"] == stationId:
            latitude = st["latitude"]
            break

    data = get_station_data_from_ghcn(
        station_id=stationId,
        start_year=startYear,
        end_year=endYear,
        latitude=latitude
    )
    return data



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
