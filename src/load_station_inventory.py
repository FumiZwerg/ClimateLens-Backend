import requests

INVENTORY_URL = "https://noaa-ghcn-pds.s3.amazonaws.com/ghcnd-inventory.txt"

def load_station_inventory() -> dict:
    """
    Lädt und parst die ghcnd-inventory.txt.
    Für jedes Station-Element (nur TMIN/TMAX) wird das früheste
    Startjahr und das späteste Endjahr ermittelt.
    Rückgabe: dict, das für jede station_id ein Dict mit "start_year" und "end_year" enthält.
    """
    inventory = {}
    try:
        print("Downloading station inventory...")
        r = requests.get(INVENTORY_URL, timeout=30)
        r.raise_for_status()
    except requests.RequestException as e:
        print(f"Error downloading inventory: {e}")
        return inventory

    lines = r.text.splitlines()
    for line in lines:
        # ghcnd-inventory.txt ist fixed-width formatiert:
        # station id: Spalte 0-11, Element: Spalte 11-15,
        # first year: Spalte 15-19, last year: Spalte 19-23
        station_id = line[0:11].strip()
        element = line[31:35].strip()
        first_year_str = line[36:40].strip()
        last_year_str = line[41:45].strip()
        if element not in ["TMIN", "TMAX"]:
            continue
        try:
            first_year = int(first_year_str)
            last_year = int(last_year_str)
        except ValueError:
            continue
        if station_id not in inventory:
            inventory[station_id] = {"start_year": first_year, "end_year": last_year}
        else:
            inventory[station_id]["start_year"] = min(inventory[station_id]["start_year"], first_year)
            inventory[station_id]["end_year"] = max(inventory[station_id]["end_year"], last_year)
    print("Inventory download complete.")
    return inventory