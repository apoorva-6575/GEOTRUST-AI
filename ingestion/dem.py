import requests
import pandas as pd
from config import OPEN_METEO_API
from utils.logger import get_logger

logger = get_logger("Ingest.DEM")

def fetch_elevation(locations):
    logger.info("Fetching DEM elevation data...")
    dem_data = []
    for lat, lon, loc_id in locations:
        url = f"{OPEN_METEO_API}?latitude={lat}&longitude={lon}&elevation=nan&current=temperature_2m"
        try:
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                dem_data.append({
                    'Location_ID': loc_id,
                    'Elevation_m': resp.json().get('elevation', 0)
                })
        except Exception as e:
            logger.error(f"Failed to fetch DEM for {loc_id}: {e}")
    return pd.DataFrame(dem_data)
