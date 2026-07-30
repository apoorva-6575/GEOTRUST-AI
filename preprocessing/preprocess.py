import os
import pandas as pd
from utils.logger import get_logger
import numpy as np
from config import RAW_DATA_DIR, PROCESSED_DATA_DIR

logger = get_logger("Preprocess")

def align_schemas():
    logger.info("Loading raw datasets from disk and aligning schemas...")
    
    # Load all available raw data from disk
    sources = ['weather', 'osm', 'sentinel', 'dem', 'river', 'historical']
    
    # Dynamically find all unique Location_IDs from raw data
    unique_locs = set()
    for name in sources:
        file_path = os.path.join(RAW_DATA_DIR, f"{name}_raw.csv")
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
            if 'Location_ID' in df.columns:
                unique_locs.update(df['Location_ID'].dropna().unique())
                
    if not unique_locs:
        # Fallback if somehow no data was ingested
        unique_locs = {"UNKNOWN_LOC"}
        
    base_df = pd.DataFrame({'Location_ID': list(unique_locs)})
    sources = ['weather', 'osm', 'sentinel', 'dem', 'river', 'historical']
    for name in sources:
        file_path = os.path.join(RAW_DATA_DIR, f"{name}_raw.csv")
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
            if not df.empty and 'Location_ID' in df.columns:
                base_df = base_df.merge(df, on='Location_ID', how='left')
                logger.info(f"Merged {name} into unified schema.")
            
    # Example preprocessing
    if 'Rainfall_mm' in base_df.columns:
        base_df['Rainfall_mm'] = base_df['Rainfall_mm'].fillna(0)
        
    base_df['CRS'] = 'EPSG:4326'
    
    # Save processed unified dataset
    os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)
    out_path = os.path.join(PROCESSED_DATA_DIR, "unified_processed.csv")
    base_df.to_csv(out_path, index=False)
    logger.info(f"Saved processed dataset to {out_path}")
    
    return base_df
