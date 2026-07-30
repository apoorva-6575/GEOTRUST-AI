import ee
import pandas as pd
import numpy as np
from utils.logger import get_logger

logger = get_logger("Ingest.Sentinel")

def fetch_sentinel_1(locations):
    logger.info("Fetching SAR flood extent from Google Earth Engine (Sentinel-1)...")
    try:
        ee.Initialize()
    except Exception:
        logger.warning("Earth Engine not authenticated. Returning simulated Sentinel data.")
        return simulate_sentinel(locations)

    sat_data = []
    for lat, lon, loc_id in locations:
        try:
            point = ee.Geometry.Point([lon, lat])
            buffer = point.buffer(5000)
            # Dummy algorithm for demo
            sat_data.append({
                'Location_ID': loc_id,
                'Flood_Extent_Pct': round(np.random.uniform(0, 50), 2),
                'Sat_Source': 'Sentinel-1 (Live Demo)'
            })
        except Exception as e:
            logger.error(f"GEE Error for {loc_id}: {e}")
    return pd.DataFrame(sat_data)

def simulate_sentinel(locations):
    return pd.DataFrame([{
        'Location_ID': loc_id,
        'Flood_Extent_Pct': round(np.random.uniform(0, 40), 2),
        'Sat_Source': 'Mock (Unauthenticated)'
    } for _, _, loc_id in locations])
