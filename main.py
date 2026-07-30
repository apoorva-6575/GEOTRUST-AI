import os
import json
import datetime
import pandas as pd
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

def generate_5_layer_json(df, output_path):
    reports = []
    
    for _, row in df.iterrows():
        # Handle nan gracefully for JSON
        def clean_val(val):
            if pd.isna(val): return None
            return val

        report = {
            "location_id": clean_val(row.get('Location_ID')),
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            "1_ingestion_layer": {
                "weather_rainfall_mm": clean_val(row.get('Rainfall_mm')),
                "weather_humidity_pct": clean_val(row.get('Humidity_pct')),
                "satellite_flood_pct": clean_val(row.get('Flood_Extent_Pct')),
                "osm_buildings": clean_val(row.get('Nearby_Buildings')),
                "osm_rivers": clean_val(row.get('Nearby_Rivers')),
                "dem_elevation_m": clean_val(row.get('Elevation_m'))
            },
            "2_validation_layer": {
                "missing_values": "None" if row.get('Quality_Passed', True) else "Detected",
                "contradictions_detected": 1 if row.get('Anomaly_Flag', False) or row.get('Consistency_Flag', False) else 0,
                "source_reliability": clean_val(row.get('Source_Reliability_Score'))
            },
            "3_trust_scoring_framework": {
                "final_trust_score": clean_val(row.get('Final_Trust_Score')),
                "uncertainty_indicator": "High" if clean_val(row.get('Final_Trust_Score', 1)) < 0.6 else ("Medium" if clean_val(row.get('Final_Trust_Score', 1)) < 0.9 else "Low")
            },
            "4_explainability_module": {
                "score_reasoning": clean_val(row.get('Trust_Explanation'))
            },
            "5_intelligence_layer": {
                "recommendation": clean_val(row.get('Intelligence_Recommendation')),
                "action_required": (clean_val(row.get('Final_Trust_Score', 1)) or 1.0) < 0.6 or ((clean_val(row.get('Final_Trust_Score', 1)) or 1.0) > 0.8 and (clean_val(row.get('Flood_Extent_Pct', 0)) or 0.0) > 30)
            }
        }
        reports.append(report)
        
    with open(output_path, 'w') as f:
        json.dump(reports, f, indent=4)

def main():
    logger.info("==================================================")
    logger.info(" GeoTrust-AI - Full 5-Layer Pipeline")
    logger.info("==================================================")
    
    # 0. Interactive Input & Geocoding
    import sys
    from utils.geocoder import geocode_place
    
    print("\n--------------------------------------------------")
    place_name = input("📍 Enter a city or region name to analyze (e.g., 'Guwahati', 'Assam'): ")
    print("--------------------------------------------------\n")
    
    if not place_name.strip():
        place_name = "Guwahati" # Default if empty
        
    lat, lon = geocode_place(place_name)
    locations = [(lat, lon, place_name.upper())]
    
    import pandas as pd
    
    # 1. Ingestion Layer
    run_ingestion(locations)
    
    # 2. Preprocessing Layer
    unified_df = align_schemas()
    
    # 3. Validation Layer
    df = assess_quality(unified_df)
    df = detect_anomalies(df)
    df = check_consistency(df)
    df = check_reliability(df)
    
    # 4. Trust & Explainability 
    df = compute_trust_score(df)
    df = generate_explanations(df)
    
    # 5. Intelligence
    df = generate_recommendations(df)
    
    # Output to massive JSON file
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    csv_path = os.path.join(OUTPUT_DIR, "validated_dataset.csv")
    json_path = os.path.join(OUTPUT_DIR, "final_intelligence_report.json")
    
    df.to_csv(csv_path, index=False)
    generate_5_layer_json(df, json_path)
    
    logger.info(f"Pipeline Complete. Generated 5-layer JSON at: {json_path}")
    
    # Print a beautiful, human-readable summary to the console
    logger.info("\n==================================================")
    logger.info("   FINAL INTELLIGENCE REPORT")
    logger.info("==================================================")
    
    with open(json_path, 'r') as f:
        reports = json.load(f)
        
    for report in reports:
        loc = report['location_id']
        time = report['timestamp']
        trust = report['3_trust_scoring_framework']['final_trust_score']
        reason = report['4_explainability_module']['score_reasoning']
        rec = report['5_intelligence_layer']['recommendation']
        
        print(f"\nLocation: {loc}  |  Time: {time}")
        print("-" * 50)
        print("[1] INGESTED DATA:")
        ing = report['1_ingestion_layer']
        print(f"   Rainfall: {ing.get('weather_rainfall_mm')} mm")
        print(f"   Humidity: {ing.get('weather_humidity_pct')} %")
        print(f"   Flood Extent: {ing.get('satellite_flood_pct')} %")
        print(f"   Buildings Nearby: {ing.get('osm_buildings')}")
        
        print("\n[2] VALIDATION & TRUST:")
        val = report['2_validation_layer']
        print(f"   Missing Values: {val.get('missing_values')}")
        print(f"   Contradictions: {val.get('contradictions_detected')}")
        print(f"   Final Trust Score: {trust} / 1.0")
        
        print("\n[3] EXPLAINABILITY:")
        print(f"   {reason}")
        
        print("\n[4] ACTIONABLE INTELLIGENCE:")
        print(f"   {rec}")
        print("==================================================")

if __name__ == "__main__":
    main()
