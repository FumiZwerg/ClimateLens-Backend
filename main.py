from src import Station
from contextlib import asynccontextmanager
from src import load_station_data
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

ALL_STATIONS: list[Station] = []

@asynccontextmanager
async def lifespan(app: FastAPI):
    load_station_data()
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)