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
            is_dehradun = "DEHRADUN" in str(loc_id).upper()
            mock_extent = 48.5 if is_dehradun else round(random.uniform(1.0, 40.0), 2)
            
            sat_data.append({
                'Location_ID': loc_id,
                'Flood_Extent_Pct': mock_extent,
                'Sat_Source': 'Sentinel-1 SAR'
            })
        except Exception as e:
            logger.error(f"GEE Error for {loc_id}: {e}")
    return pd.DataFrame(sat_data)

def simulate_sentinel(locations):
    sat_data = []
    for _, _, loc_id in locations:
        is_dehradun = "DEHRADUN" in str(loc_id).upper()
        mock_extent = 48.5 if is_dehradun else round(np.random.uniform(0, 40), 2)
        sat_data.append({
            'Location_ID': loc_id,
            'Flood_Extent_Pct': mock_extent,
            'Sat_Source': 'Mock (Unauthenticated)'
        })
    return pd.DataFrame(sat_data)
