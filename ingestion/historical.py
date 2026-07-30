import pandas as pd
from utils.logger import get_logger

logger = get_logger("Ingest.Historical")

def fetch_historical(locations):
    logger.info("Fetching Historical Flood data (Mocking API endpoint)...")
    data = []
    for _, _, loc_id in locations:
        data.append({
            'Location_ID': loc_id,
            'Historical_Rainfall_mm': 120.5,
            'Flood_Frequency': 'Medium'
        })
    return pd.DataFrame(data)
