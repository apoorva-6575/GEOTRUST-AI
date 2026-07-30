import pandas as pd
from utils.logger import get_logger

logger = get_logger("Trust.Score")

def compute_trust_score(df):
    logger.info("Computing mathematical Trust Score based on validation flags...")
    
    # Base score is 100
    df['Trust_Score_Raw'] = 100.0
    
    for idx, row in df.iterrows():
        penalty = 0.0
        
        # ML Anomaly Penalty
        if row.get('Anomaly_Flag', False):
            penalty += 20.0
            
        # Consistency Penalty
        if row.get('Consistency_Flag', False):
            penalty += 15.0
            
        # Quality Penalty (e.g., bad ranges)
        if not row.get('Quality_Passed', True):
            penalty += 50.0
            
        # Missing non-critical data penalty
        if pd.isna(row.get('Wind_Speed_kmh', 0)):
            penalty += 5.0
            
        # Freshness/Reliability (Placeholder)
        # If Source_Reliability_Score exists, we could use it to scale the penalty
        
        final_raw = max(0.0, df.at[idx, 'Trust_Score_Raw'] - penalty)
        
        # Normalize to 0.0 - 1.0
        df.at[idx, 'Final_Trust_Score'] = round(final_raw / 100.0, 2)
        
    return df
