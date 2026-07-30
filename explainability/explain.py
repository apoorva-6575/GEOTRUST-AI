import pandas as pd
from utils.logger import get_logger

logger = get_logger("Explainability")

def generate_explanations(df):
    logger.info("Generating heuristic explanations for Trust Scores...")
    
    explanations = []
    
    for idx, row in df.iterrows():
        reasons = []
        
        score = row.get('Final_Trust_Score', 1.0)
        if score == 1.0:
            reasons.append("Perfect score. All validation, quality, and consistency checks passed successfully.")
        else:
            if row.get('Anomaly_Flag', False):
                reasons.append("-20%: ML Anomaly detected (multi-variate contradiction).")
            if row.get('Consistency_Flag', False):
                reasons.append("-15%: Rule-based contradiction detected (e.g. Weather vs Satellite).")
            if not row.get('Quality_Passed', True):
                reasons.append("-50%: Critical quality check failed (e.g. impossible data ranges).")
            if pd.isna(row.get('Wind_Speed_kmh', 0)):
                reasons.append("-5%: Missing minor weather variables.")
                
        explanations.append(" | ".join(reasons))
        
    df['Trust_Explanation'] = explanations
    return df
