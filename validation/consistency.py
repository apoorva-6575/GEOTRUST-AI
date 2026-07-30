from utils.logger import get_logger

logger = get_logger("Validation.Consistency")

def check_consistency(df):
    logger.info("Running rule-based consistency cross-checks...")
    df['Consistency_Flag'] = False
    
    if 'Rainfall_mm' in df.columns and 'Flood_Extent_Pct' in df.columns:
        # Example logic: Huge rain but 0 flood, or vice versa
        contradiction = (df['Rainfall_mm'] > 100) & (df['Flood_Extent_Pct'] < 1)
        df.loc[contradiction, 'Consistency_Flag'] = True
        
    return df
