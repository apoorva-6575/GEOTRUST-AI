import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
import datetime

class ValidationEngine:
    def __init__(self, df):
        self.df = df.copy()
        self.validation_logs = []
        self.df['Is_Valid'] = True
        self.df['Validation_Flags'] = ""
        
        # Source quality tracking
        self.source_quality = {
            'EO': {'total': len(df), 'issues': 0},
            'Satellite': {'total': len(df), 'issues': 0},
            'OSM': {'total': len(df), 'issues': 0},
            'Weather': {'total': len(df), 'issues': 0},
            'Climate': {'total': len(df), 'issues': 0}
        }

    def log_issue(self, loc_id, issue_type, desc, source):
        self.validation_logs.append({
            'Location_ID': loc_id,
            'Type': issue_type,
            'Description': desc,
            'Source': source
        })
        self.source_quality[source]['issues'] += 1

    def flag_record(self, idx, flag_msg):
        self.df.at[idx, 'Is_Valid'] = False
        current_flags = self.df.at[idx, 'Validation_Flags']
        self.df.at[idx, 'Validation_Flags'] = current_flags + f"[{flag_msg}] "

    def check_missing_values(self):
        print("[Validation] Running Missing Value Checks...")
        for idx, row in self.df.iterrows():
            if pd.isna(row['Rainfall_mm']):
                self.log_issue(row['Location_ID'], 'Missing Value', 'Rainfall data unavailable', 'Weather')
                self.flag_record(idx, "Missing: Rainfall")
                
            if pd.isna(row['Flood_Extent_Pct']):
                self.log_issue(row['Location_ID'], 'Missing Value', 'Flood Extent missing', 'EO')
                self.flag_record(idx, "Missing: Flood Extent")

    def check_ranges(self):
        print("[Validation] Running Range Checks...")
        for idx, row in self.df.iterrows():
            # Humidity > 100
            if pd.notna(row['Humidity_pct']) and (row['Humidity_pct'] > 100 or row['Humidity_pct'] < 0):
                self.log_issue(row['Location_ID'], 'Invalid Range', f"Humidity reported at {row['Humidity_pct']}%", 'Weather')
                self.flag_record(idx, "Range: Humidity")
                
            # Flood Extent > 100
            if pd.notna(row['Flood_Extent_Pct']) and (row['Flood_Extent_Pct'] > 100 or row['Flood_Extent_Pct'] < 0):
                self.log_issue(row['Location_ID'], 'Invalid Range', f"Flood Extent at {row['Flood_Extent_Pct']}%", 'EO')
                self.flag_record(idx, "Range: Flood Extent")
                
            # River Distance < 0
            if pd.notna(row['River_Distance_m']) and row['River_Distance_m'] < 0:
                self.log_issue(row['Location_ID'], 'Invalid Range', f"River distance is negative: {row['River_Distance_m']}", 'OSM')
                self.flag_record(idx, "Range: River Distance")

    def check_freshness(self):
        print("[Validation] Running Freshness Checks...")
        now = datetime.datetime.now()
        for idx, row in self.df.iterrows():
            # Check climate update time
            if pd.notna(row['Update_Time']):
                record_time = datetime.datetime.fromisoformat(row['Update_Time'])
                days_old = (now - record_time).days
                if days_old > 180: # 6 months
                    self.log_issue(row['Location_ID'], 'Freshness Warning', f"Climate dataset timestamp is {days_old} days old.", 'Climate')
                    # We might not flag the record as totally invalid just for freshness, but log it.
                    self.df.at[idx, 'Validation_Flags'] += "[Stale Data] "

    def detect_contradictions_ml(self):
        print("[Validation] Running ML-based Contradiction Detection (Isolation Forest)...")
        # Features to check for logical consistency: 
        # e.g., high rainfall and close river distance usually correlates with high flood extent.
        
        # Prepare data for ML model
        ml_features = ['Rainfall_mm', 'Flood_Extent_Pct', 'River_Distance_m', 'Humidity_pct']
        
        # Drop NaNs for the ML model
        ml_df = self.df[ml_features].dropna()
        
        if len(ml_df) > 10: # Need enough data to fit the model
            # Fit Isolation Forest
            clf = IsolationForest(contamination=0.05, random_state=42)
            preds = clf.fit_predict(ml_df)
            
            anomaly_indices = ml_df[preds == -1].index
            
            for idx in anomaly_indices:
                loc_id = self.df.at[idx, 'Location_ID']
                self.log_issue(loc_id, 'Contradiction Detected', "ML Anomaly: Conflicting meteorological and observation signals", 'Multiple')
                self.flag_record(idx, "Contradiction (ML Anomaly)")

    def calculate_source_quality(self):
        scores = {}
        for source, stats in self.source_quality.items():
            if stats['total'] > 0:
                # 1 issue reduces score by some percentage. E.g. (Total - Issues)/Total
                # Cap at 0
                score = max(0, int(((stats['total'] - stats['issues']) / stats['total']) * 100))
                scores[source] = score
            else:
                scores[source] = 100
        return scores

    def run_all(self):
        self.check_missing_values()
        self.check_ranges()
        self.check_freshness()
        self.detect_contradictions_ml()
        
        scores = self.calculate_source_quality()
        
        print("\n--- Source Quality Scores ---")
        for k, v in scores.items():
            print(f"{k}: {v}%")
            
        return self.df, self.validation_logs, scores
