import requests
from utils.logger import get_logger

logger = get_logger("Geocoder")

def geocode_place(place_name):
    """Uses Open-Meteo Geocoding API to convert a place name to Lat/Lon"""
    logger.info(f"Geocoding location: {place_name}...")
    url = f"https://geocoding-api.open-meteo.com/v1/search?name={place_name}&count=1&language=en&format=json"
    
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            if 'results' in data and len(data['results']) > 0:
                result = data['results'][0]
                lat = result.get('latitude')
                lon = result.get('longitude')
                logger.info(f"Found Coordinates for {place_name}: {lat}, {lon}")
                return lat, lon
            else:
                logger.warning(f"Could not find coordinates for '{place_name}'. Using default.")
    except Exception as e:
        logger.error(f"Geocoding API failed: {e}")
        
    # Default fallback (Guwahati) if it fails
    logger.warning("Falling back to default coordinates (26.15, 91.75)")
    return 26.15, 91.75
