import pandas as pd
import numpy as np

def standardize_units(datasets):
    print("[Schema Mapping] Standardizing units across datasets...")
    
    # 1. Weather: Convert Rainfall (inches) to (mm)
    weather = datasets['weather'].copy()
    weather['Rainfall_mm'] = weather['Rainfall_in'] * 25.4
    weather = weather.drop(columns=['Rainfall_in'])
    
    # Weather: Convert Temp (F) to (C)
    weather['Temp_C'] = (weather['Temp_F'] - 32) * 5.0/9.0
    weather['Temp_C'] = weather['Temp_C'].round(2)
    weather = weather.drop(columns=['Temp_F'])
    
    # 2. OSM: Convert River Distance (km) to (m)
    osm = datasets['osm'].copy()
    osm['River_Distance_m'] = osm['River_Distance_km'] * 1000
    osm = osm.drop(columns=['River_Distance_km'])
    
    # 3. Satellite: Rename Lat/Lon to match standard schema
    sat = datasets['sat'].copy()
    sat = sat.rename(columns={'Lat': 'Latitude', 'Lon': 'Longitude'})
    
    datasets['weather'] = weather
    datasets['osm'] = osm
    datasets['sat'] = sat
    
    return datasets

def merge_datasets(datasets):
    print("[Schema Mapping] Merging 5 datasets into unified schema...")
    
    # Base is EO dataset
    unified_df = datasets['eo'].copy()
    
    # Merge Satellite
    # We drop lat/lon from sat to avoid duplicates since we join on Location_ID
    sat_merge = datasets['sat'].drop(columns=['Latitude', 'Longitude'])
    unified_df = unified_df.merge(sat_merge, on='Location_ID', how='left')
    
    # Merge OSM
    unified_df = unified_df.merge(datasets['osm'], on='Location_ID', how='left')
    
    # Merge Weather
    unified_df = unified_df.merge(datasets['weather'], on='Location_ID', how='left')
    
    # Merge Climate
    unified_df = unified_df.merge(datasets['climate'], on='Location_ID', how='left')
    
    # Standardize schema column names
    final_cols = [
        'Location_ID', 'Latitude', 'Longitude', 
        'Rainfall_mm', 'Humidity_pct', 'Temp_C', 'Wind_Speed_kmh',
        'Flood_Extent_Pct', 'Surface_Water_Coverage', 'Water_Expansion_Index',
        'Flood_Detected', 'Water_Pixels', 'Cloud_Cover',
        'River_Distance_m', 'Nearby_Villages', 'Nearby_Roads', 'Nearby_Hospitals',
        'Historical_Rainfall_mm', 'Flood_Frequency', 'Seasonal_Risk_Level',
        'timestamp', 'Sat_Time', 'Update_Time' # Source timestamps
    ]
    
    return unified_df[final_cols]

def process_schema(datasets):
    standardized = standardize_units(datasets)
    unified = merge_datasets(standardized)
    print(f"[Schema Mapping] Generated unified dataset with {unified.shape[0]} rows and {unified.shape[1]} columns.")
    return unified
