import requests
import pandas as pd
import time
from config import OVERPASS_API
from utils.logger import get_logger

logger = get_logger("Ingest.OSM")

def fetch_osm(locations):
    logger.info("Fetching infrastructure data from OpenStreetMap...")
    osm_data = []
    for lat, lon, loc_id in locations:
        query = f"""
        [out:json];
        (
          way["waterway"="river"](around:2000,{lat},{lon});
          way["building"](around:2000,{lat},{lon});
        );
        out count;
        """
        try:
            resp = requests.post(OVERPASS_API, data={'data': query}, timeout=15)
            if resp.status_code == 200:
                elements = resp.json().get('elements', [])
                if elements and 'tags' in elements[0]:
                    tags = elements[0]['tags']
                    osm_data.append({
                        'Location_ID': loc_id,
                        'Nearby_Buildings': int(tags.get('buildings', 0)),
                        'Nearby_Rivers': int(tags.get('waterways', 1)),
                        'River_Distance_m': 500 # Simplified proxy
                    })
        except Exception as e:
            logger.error(f"Failed to fetch OSM for {loc_id}: {e}")
        time.sleep(1) # rate limit
    return pd.DataFrame(osm_data)
