import pandas as pd
from utils.logger import get_logger

logger = get_logger("Ingest.River")

def fetch_river_gauge(locations):
    logger.info("Fetching River Gauge Data (CWC / USGS Mock)...")
    data = []
    for _, _, loc_id in locations:
        data.append({
            'Location_ID': loc_id,
            'River_Water_Level_m': 45.2,
            'Danger_Level_m': 48.0
        })
    return pd.DataFrame(data)
