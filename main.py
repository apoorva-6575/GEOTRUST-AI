import os
from config import TEST_LOCATIONS, OUTPUT_DIR
from ingestion.ingest import run_ingestion
from preprocessing.preprocess import align_schemas
from validation.quality import assess_quality
from validation.anomaly import detect_anomalies
from validation.consistency import check_consistency
from validation.reliability import check_reliability
from trust.trust_score import compute_trust_score
from explainability.explain import generate_explanations
from intelligence.recommendation import generate_recommendations
from utils.logger import get_logger

logger = get_logger("GeoTrust-AI.Main")

def main():
    logger.info("==================================================")
    logger.info(" GeoTrust-AI - Modular Data Engineering Pipeline")
    logger.info("==================================================")
    
    # 1. Ingestion Layer (Saves to data/raw/)
    run_ingestion(TEST_LOCATIONS)
    
    # 2. Preprocessing Layer (Reads from data/raw/, saves to data/processed/)
    unified_df = align_schemas()
    
    # 3. Validation Layer (Operates on Processed Data)
    df = assess_quality(unified_df)
    df = detect_anomalies(df)
    df = check_consistency(df)
    df = check_reliability(df)
    
    # 4. Trust & Explainability 
    df = compute_trust_score(df)
    df = generate_explanations(df)
    
    # 5. Intelligence / Recommendations
    df = generate_recommendations(df)
    
    # 6. Output
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    output_path = os.path.join(OUTPUT_DIR, "validated_dataset.csv")
    df.to_csv(output_path, index=False)
    logger.info(f"Pipeline Complete. Validated dataset saved to {output_path}")
    
    # Print a quick summary of the intelligence to the console
    logger.info("\n--- Executive Summary ---")
    for _, row in df.iterrows():
        logger.info(f"[{row['Location_ID']}] Score: {row['Final_Trust_Score']} -> {row['Intelligence_Recommendation']}")
    logger.info("==================================================")

if __name__ == "__main__":
    main()
