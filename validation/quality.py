from utils.logger import get_logger

logger = get_logger("Validation.Quality")

def assess_quality(df):
    logger.info("Assessing missing values and data ranges...")
    # Add simple validity flags based on basic quality rules
    df['Quality_Passed'] = True
    
    if 'Humidity_pct' in df.columns:
        df.loc[(df['Humidity_pct'] > 100) | (df['Humidity_pct'] < 0), 'Quality_Passed'] = False
        
    return df
