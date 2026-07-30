import requests
import pandas as pd
from config import OPEN_METEO_API
from utils.logger import get_logger

logger = get_logger("Ingest.Weather")

def fetch_weather(locations):
    logger.info("Fetching real-time weather data from Open-Meteo...")
    weather_data = []
    for lat, lon, loc_id in locations:
        url = f"{OPEN_METEO_API}?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m&timezone=auto"
        try:
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                current = resp.json().get('current', {})
                weather_data.append({
                    'Location_ID': loc_id,
                    'Temp_C': current.get('temperature_2m'),
                    'Humidity_pct': current.get('relative_humidity_2m'),
                    'Rainfall_mm': current.get('precipitation'),
                    'Wind_Speed_kmh': current.get('wind_speed_10m')
                })
        except Exception as e:
            logger.error(f"Failed to fetch weather for {loc_id}: {e}")
    return pd.DataFrame(weather_data)
