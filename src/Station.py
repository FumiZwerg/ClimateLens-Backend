from pydantic import BaseModel

class Station(BaseModel):
    """
    Antwortmodell, das wir für Endpoint "/stations-query" verwenden.
    """
    id: str
    name: str
    latitude: float
    longitude: float
    distance: float