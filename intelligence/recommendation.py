import pandas as pd
from utils.logger import get_logger

logger = get_logger("Intelligence.Recommendation")

def generate_recommendations(df):
    logger.info("Generating actionable intelligence and recommendations...")
    
    recs = []
    for idx, row in df.iterrows():
        trust = row.get('Final_Trust_Score', 0)
        rain = row.get('Rainfall_mm', 0)
        flood_pct = row.get('Flood_Extent_Pct', 0)
        
        # Handle NaNs for logical checks
        rain = 0 if pd.isna(rain) else rain
        flood_pct = 0 if pd.isna(flood_pct) else flood_pct
        
        if trust < 0.5:
            recs.append("ACTION: Deploy ground truth teams. Data reliability is too low to automate response.")
        elif trust >= 0.8 and flood_pct > 30:
            recs.append("CRITICAL: Immediate Evacuation Recommended. High confidence in severe flooding.")
        elif trust >= 0.8 and rain > 100:
            recs.append("WARNING: High flood risk due to severe rainfall. Monitor river gauges actively.")
        else:
            recs.append("INFO: Normal conditions. Continue automated monitoring.")
            
    df['Intelligence_Recommendation'] = recs
    return df
