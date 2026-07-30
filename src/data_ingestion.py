import pandas as pd
import numpy as np
import datetime
import requests
import time
import ee

# Define some locations of interest for testing (e.g., flood-prone regions in India/Bangladesh)
# Lat, Lon
LOCATIONS = [
    (26.15, 91.75), # Guwahati, Assam (flood prone)
    (25.60, 85.12), # Patna, Bihar
    (22.57, 88.36), # Kolkata, West Bengal
    (28.70, 77.10), # Delhi
    (25.31, 83.00), # Varanasi
]

def generate_locations(num_records=5):
    locations = []
    for i in range(min(num_records, len(LOCATIONS))):
        lat, lon = LOCATIONS[i]
        locations.append({'Latitude': lat, 'Longitude': lon, 'Location_ID': f"LOC-{i:03d}"})
    return pd.DataFrame(locations)

def fetch_weather_and_climate(locations_df):
    """
    Source: Open-Meteo (Free API, no key required)
    Fetches Current Weather, Historical Precipitation, and Elevation (DEM).
    """
    print("[Ingestion] Fetching data from Open-Meteo API...")
    weather_data = []
    climate_data = []
    
    for _, row in locations_df.iterrows():
        lat, lon = row['Latitude'], row['Longitude']
        
        # Open-Meteo Endpoint
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m&elevation=nan&timezone=auto"
        
        try:
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                current = data.get('current', {})
                
                weather_data.append({
                    'Location_ID': row['Location_ID'],
                    'Temp_C': current.get('temperature_2m', np.nan),
                    'Humidity_pct': current.get('relative_humidity_2m', np.nan),
                    'Rainfall_mm': current.get('precipitation', np.nan),
                    'Wind_Speed_kmh': current.get('wind_speed_10m', np.nan)
                })
                
                # Mock historical/climate using elevation as a proxy for risk level for now
                elevation = data.get('elevation', 0)
                climate_data.append({
                    'Location_ID': row['Location_ID'],
                    'Elevation_m': elevation,
                    'Historical_Rainfall_mm': np.random.uniform(50, 200), # Placeholder for long-term historical API call
                    'Flood_Frequency': 'High' if elevation < 50 else 'Low',
                    'Seasonal_Risk_Level': 5 if elevation < 50 else 1,
                    'Update_Time': datetime.datetime.now().isoformat()
                })
            else:
                print(f"Failed to fetch weather for {lat}, {lon}")
        except Exception as e:
            print(f"Error calling Open-Meteo: {e}")
            
        time.sleep(1) # Respect rate limits
        
    return pd.DataFrame(weather_data), pd.DataFrame(climate_data)

def fetch_osm_data(locations_df):
    """
    Source: OpenStreetMap Overpass API (Free, no key required)
    Queries for nearby rivers and building counts within a 2km radius.
    """
    print("[Ingestion] Fetching data from Overpass API (OSM)...")
    osm_data = []
    
    overpass_url = "http://overpass-api.de/api/interpreter"
    
    for _, row in locations_df.iterrows():
        lat, lon = row['Latitude'], row['Longitude']
        radius = 2000 # meters
        
        # Overpass QL Query: Count buildings and find nearest waterway
        query = f"""
        [out:json];
        (
          way["waterway"="river"](around:{radius},{lat},{lon});
          way["building"](around:{radius},{lat},{lon});
        );
        out count;
        """
        
        try:
            resp = requests.post(overpass_url, data={'data': query}, timeout=20)
            if resp.status_code == 200:
                data = resp.json()
                elements = data.get('elements', [])
                
                buildings = 0
                rivers = 0
                if len(elements) > 0 and 'tags' in elements[0]:
                    tags = elements[0]['tags']
                    buildings = tags.get('buildings', 0)
                    rivers = tags.get('waterways', 1)
                
                osm_data.append({
                    'Location_ID': row['Location_ID'],
                    'Nearby_Buildings': int(buildings),
                    'Nearby_Rivers': int(rivers),
                    'River_Distance_m': np.random.uniform(50, radius) if rivers > 0 else -1 # Mock exact distance
                })
            else:
                print(f"Failed Overpass API for {lat}, {lon}. Code: {resp.status_code}")
                
        except Exception as e:
            print(f"Error calling Overpass API: {e}")
            
        time.sleep(2) # Overpass has strict rate limits
        
    return pd.DataFrame(osm_data)

def initialize_earth_engine():
    """Initializes Google Earth Engine. Authenticates if necessary."""
    try:
        ee.Initialize()
    except Exception as e:
        print("\n[WARNING] Google Earth Engine is not authenticated.")
        print("To authenticate, you must run the following command in your terminal:")
        print("    earthengine authenticate")
        print("Once authenticated, re-run this script.\n")
        # For now, we will just return False to mock the data if not authenticated
        return False
    return True

def fetch_satellite_data(locations_df):
    """
    Source: Google Earth Engine (Sentinel-1 SAR)
    Calculates water coverage using actual Copernicus Sentinel-1 GRD imagery.
    """
    print("[Ingestion] Fetching Earth Observation Data from Google Earth Engine (Sentinel-1)...")
    
    is_auth = initialize_earth_engine()
    sat_data = []
    
    for _, row in locations_df.iterrows():
        if is_auth:
            try:
                lat, lon = row['Latitude'], row['Longitude']
                point = ee.Geometry.Point([lon, lat])
                
                # Fetch Sentinel-1 image collection for the last 15 days
                end_date = datetime.datetime.now()
                start_date = end_date - datetime.timedelta(days=15)
                
                collection = ee.ImageCollection('COPERNICUS/S1_GRD') \
                    .filterBounds(point) \
                    .filterDate(start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')) \
                    .filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VV')) \
                    .filter(ee.Filter.eq('instrumentMode', 'IW'))
                
                # Try to get the latest image
                count = collection.size().getInfo()
                
                if count > 0:
                    image = collection.sort('system:time_start', False).first()
                    
                    # Simple thresholding for water detection on VV polarization (e.g., < -16 dB)
                    # This is a basic SAR water detection algorithm
                    vv = image.select('VV')
                    water_mask = vv.lt(-16)
                    
                    # Calculate percentage of water in a 5km radius
                    buffer = point.buffer(5000)
                    water_area = water_mask.multiply(ee.Image.pixelArea()).reduceRegion(
                        reducer=ee.Reducer.sum(),
                        geometry=buffer,
                        scale=30,
                        maxPixels=1e9
                    ).get('VV').getInfo()
                    
                    total_area = ee.Number(5000 * 5000 * 3.14159).getInfo()
                    water_coverage_pct = (water_area / total_area) * 100
                    
                    sat_data.append({
                        'Location_ID': row['Location_ID'],
                        'Flood_Extent_Pct': round(water_coverage_pct, 2),
                        'Sat_Source': 'Sentinel-1 (Live)'
                    })
                else:
                    print(f"No Sentinel-1 imagery available for {lat}, {lon} in the last 15 days.")
                    sat_data.append({
                        'Location_ID': row['Location_ID'],
                        'Flood_Extent_Pct': np.nan,
                        'Sat_Source': 'No Data'
                    })
            except Exception as e:
                print(f"GEE Error for {lat}, {lon}: {e}")
        else:
            # Fallback to simulated data if GEE is not authenticated yet
            sat_data.append({
                'Location_ID': row['Location_ID'],
                'Flood_Extent_Pct': round(np.random.uniform(0, 40), 2),
                'Sat_Source': 'Mock (Not Authenticated)'
            })
            
    return pd.DataFrame(sat_data)

def ingest_all_sources(num_records=5):
    print("[Ingestion Layer] Pulling live data from active APIs...")
    locs = generate_locations(num_records)
    
    weather_df, climate_df = fetch_weather_and_climate(locs)
    osm_df = fetch_osm_data(locs)
    sat_df = fetch_satellite_data(locs)
    
    # We will simulate the 'EO' dataset as a combination/placeholder since GEE provides our satellite data
    eo_df = pd.DataFrame({
        'Location_ID': locs['Location_ID'],
        'Surface_Water_Coverage': np.random.uniform(0, 80, len(locs))
    })
    
    datasets = {
        'eo': eo_df,
        'sat': sat_df,
        'osm': osm_df,
        'weather': weather_df,
        'climate': climate_df
    }
    print("[Ingestion Layer] Live API Data Collection Complete.")
    return datasets
