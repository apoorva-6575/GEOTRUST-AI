import pandas as pd
from sklearn.ensemble import IsolationForest
from utils.logger import get_logger

logger = get_logger("Validation.Anomaly")

def detect_anomalies(df):
    logger.info("Running Isolation Forest for multi-variate contradiction detection...")
    features = ['Rainfall_mm', 'Flood_Extent_Pct', 'River_Distance_m', 'Humidity_pct']
    # Filter features that actually exist in df
    features = [f for f in features if f in df.columns]
    
    if len(features) < 2 or len(df.dropna(subset=features)) < 3:
        logger.warning("Not enough data to run ML anomaly detection.")
        return df

    ml_df = df[features].fillna(0)
    clf = IsolationForest(contamination=0.1, random_state=42)
    preds = clf.fit_predict(ml_df)
    
    df['Anomaly_Flag'] = (preds == -1)
    if df['Anomaly_Flag'].any():
        logger.warning(f"Detected {df['Anomaly_Flag'].sum()} contradictory records via ML.")
    
    return df
