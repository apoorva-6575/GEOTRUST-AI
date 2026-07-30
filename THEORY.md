# GeoTrust-AI: Architectural & Theoretical Foundation

GeoTrust-AI is an enterprise-grade multi-source flood intelligence module. Its core objective is to ingest heterogeneous data from Earth Observation, Meteorological, and Ground Infrastructure sources, standardize them, and evaluate their trustworthiness before generating actionable intelligence.

This document outlines the underlying theories and logic driving the platform.

---

## 1. The Ingestion Layer

The module pulls live data across 5 distinct domains:
1. **Meteorological (Open-Meteo / ERA5)**: Provides current rainfall, temperature, and wind.
2. **Infrastructure (OpenStreetMap / Overpass)**: Provides proximity to rivers and structural density (buildings).
3. **Earth Observation (Sentinel-1 / GEE)**: Provides Synthetic Aperture Radar (SAR) backscatter data.
4. **Topographical (Copernicus DEM)**: Provides elevation (Digital Elevation Model).
5. **Historical/River Gauge (Mocked)**: Provides contextual ground truth.

**Theoretical Approach:**
The ingestion layer standardizes geospatial joins. Every incoming record is mapped to a unique `Location_ID` derived from its spatial bounding box (Latitude, Longitude) to ensure all data across the 5 sources refers to the exact same physical space.

---

## 2. The Validation & Consistency Engine

Data collected during a crisis is often noisy, delayed, or outright wrong. The Validation Engine uses a multi-tiered approach to detect bad data.

### 2.1 Rule-Based Validation (Quality & Consistency)
- **Range Checks**: Absolute physical limits. (e.g., Humidity cannot exceed 100%. River distance cannot be negative).
- **Logical Cross-Checks**: Simple heuristic contradictions. (e.g., if Rainfall > 100mm, but Flood Extent == 0%, this triggers a consistency flag).

### 2.2 ML Anomaly Detection (Isolation Forest)
GeoTrust-AI employs an **Isolation Forest** (an unsupervised machine learning algorithm) to detect multi-variate anomalies.

**How it works:**
The algorithm recursively generates random partitions across the feature space (Rainfall, Flood Extent, River Distance, Humidity). 
- *Normal records* require many partitions to be isolated.
- *Anomalous records* (where the relationship between variables is contradictory, e.g., low rain + high elevation + massive flood extent) are isolated very quickly (few partitions).
If a record falls into the top 10% of isolation speed (`contamination=0.1`), it is flagged as an Anomaly.

---

## 3. Trust Scoring Framework

The Trust Score mathematically represents the reliability of a given record. It uses a **Weighted Penalty System** on a scale of `0.0` to `1.0`.

**The Algorithm:**
1. Base Score = `100.0`
2. **ML Anomaly Penalty**: `-20.0` (If Isolation Forest flags the record)
3. **Consistency Penalty**: `-15.0` (If rule-based logic fails)
4. **Critical Quality Penalty**: `-50.0` (If physics are violated, e.g., Humidity > 100%)
5. **Missing Data Penalty**: `-5.0` (For missing non-essential data like Wind Speed)

*Final Trust Score = Max(0, Base - Penalties) / 100*

---

## 4. Explainability & Intelligence

### Explainability (`explain.py`)
AI decisions must be transparent. The explainability module acts as a heuristic surrogate model. Instead of a black-box trust score, it concatenates human-readable strings explaining exactly *which* penalties were applied (e.g., `"-20%: ML Anomaly detected (multi-variate contradiction)"`).

### Actionable Intelligence (`recommendation.py`)
The final layer converts data into action using a decision matrix:
- **CRITICAL**: Trust > 0.8 AND Flood Extent > 30% -> `Immediate Evacuation Recommended.`
- **WARNING**: Trust > 0.8 AND Rainfall > 100mm -> `High flood risk due to severe rainfall.`
- **ACTION**: Trust < 0.5 -> `Deploy ground truth teams. Data reliability is too low.`
- **INFO**: Everything else -> `Normal conditions.`
