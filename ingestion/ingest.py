import os
import pandas as pd
from ingestion.weather import fetch_weather
from ingestion.osm import fetch_osm
from ingestion.sentinel import fetch_sentinel_1
from ingestion.dem import fetch_elevation
from ingestion.river import fetch_river_gauge
from ingestion.historical import fetch_historical
from utils.logger import get_logger
from config import RAW_DATA_DIR

logger = get_logger("Ingest.Controller")

def run_ingestion(locations):
    import shutil
    logger.info("Starting Multi-Source Data Ingestion Pipeline...")
    
    # Clear stale data to prevent overlapping locations
    if os.path.exists(RAW_DATA_DIR):
        for f in os.listdir(RAW_DATA_DIR):
            if f.endswith('.csv'):
                os.remove(os.path.join(RAW_DATA_DIR, f))
    
    datasets = {
        'weather': fetch_weather(locations),
        'osm': fetch_osm(locations),
        'sentinel': fetch_sentinel_1(locations),
        'dem': fetch_elevation(locations),
        'river': fetch_river_gauge(locations),
        'historical': fetch_historical(locations)
    }
    
    # Save raw datasets to disk
    os.makedirs(RAW_DATA_DIR, exist_ok=True)
    for name, df in datasets.items():
        if not df.empty:
            file_path = os.path.join(RAW_DATA_DIR, f"{name}_raw.csv")
            df.to_csv(file_path, index=False)
            logger.info(f"Saved {name} data to {file_path}")
            
    logger.info("Data Ingestion Pipeline Complete.")
    return datasets
