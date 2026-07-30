import os

# Base paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
RAW_DATA_DIR = os.path.join(DATA_DIR, "raw")
PROCESSED_DATA_DIR = os.path.join(DATA_DIR, "processed")
OUTPUT_DIR = os.path.join(DATA_DIR, "outputs")

# API Endpoints
OPEN_METEO_API = "https://api.open-meteo.com/v1/forecast"
OVERPASS_API = "http://overpass-api.de/api/interpreter"

# Test Locations (Lat, Lon, ID)
TEST_LOCATIONS = [
    (26.15, 91.75, "LOC-001"), # Guwahati
    (25.60, 85.12, "LOC-002"), # Patna
    (22.57, 88.36, "LOC-003"), # Kolkata
]
