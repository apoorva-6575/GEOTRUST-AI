# GeoTrust-AI: Complete Pipeline Explanation

## What is GeoTrust-AI?

GeoTrust-AI is an end-to-end Flood Risk Intelligence Platform that ingests real-time
environmental data from five independent sources, validates the data for contradictions,
assigns a mathematical Trust Score, generates actionable intelligence, and explains
exactly why each recommendation was made.

It is designed for national agencies like the National Disaster Management Authority (NDMA)
and the Indian Space Research Organisation (ISRO) who need transparent, trustworthy,
AI-driven decision support during flood emergencies.

---

## The Core Problem

In disaster management, data comes from dozens of different places: weather stations,
satellites, government databases, crowd-sourced maps, and climate models. The critical
challenge is:

**What happens when these sources contradict each other?**

If a weather station reports 250 mm of torrential rainfall, but the satellite imagery
shows 0% flood extent on the ground, which source should a disaster manager trust?
A wrong decision can cost lives.

GeoTrust-AI solves this by acting as a mathematical "Truth Filter" that cross-validates
every data point before any recommendation is made.

---

## Architecture Overview

```
           +------------------+
           |   User Input     |
           | (City / Region)  |
           +--------+---------+
                    |
                    v
           +------------------+
           |   Geocoder       |
           | (Lat/Lon Lookup) |
           +--------+---------+
                    |
                    v
    +=======================================+
    |     MODULE 1: DATA INGESTION LAYER    |
    |                                       |
    |  +----------+  +-----------+          |
    |  | Weather  |  | Satellite |          |
    |  | (Live)   |  | (SAR)     |          |
    |  +----------+  +-----------+          |
    |  +----------+  +-----------+          |
    |  | OpenStr  |  | Climate   |          |
    |  | eetMap   |  | History   |          |
    |  +----------+  +-----------+          |
    |  +----------+                         |
    |  | DEM/     |                         |
    |  | Elevation|                         |
    |  +----------+                         |
    +=======================================+
                    |
                    v  (5 raw CSV datasets)
    +=======================================+
    |  MODULE 2: VALIDATION & CONSISTENCY   |
    |                                       |
    |  1. Schema Alignment (Merge all CSVs) |
    |  2. Quality Assessment (Missing vals) |
    |  3. Anomaly Detection (Isolation      |
    |     Forest ML model)                  |
    |  4. Rule-Based Consistency Checks     |
    |  5. Source Reliability Scoring         |
    +=======================================+
                    |
                    v  (Validated + flagged DataFrame)
    +=======================================+
    |  MODULE 3: TRUST SCORING FRAMEWORK    |
    |                                       |
    |  Base Score: 100%                     |
    |  - Anomaly detected?      -20%       |
    |  - Contradiction found?   -15%       |
    |  - Quality check failed?  -50%       |
    |  - Missing wind data?      -5%       |
    |                                       |
    |  Final Trust Score = Base - Penalties  |
    +=======================================+
                    |
                    v  (Trust Score: e.g. 85%)
    +=======================================+
    |  MODULE 4: INTELLIGENCE GENERATION    |
    |                                       |
    |  IF rainfall > 100mm                  |
    |     OR flood_extent > 30%:            |
    |     => FLOOD RISK: HIGH               |
    |     => Issue Flood Warning            |
    |     => Notify Disaster Response Teams |
    |     => Prepare Evacuation Plans       |
    |  ELSE:                                |
    |     => FLOOD RISK: LOW                |
    |     => Continue Automated Monitoring  |
    +=======================================+
                    |
                    v
    +=======================================+
    |  MODULE 5: EXPLAINABILITY MODULE      |
    |                                       |
    |  Translates the math into English:    |
    |  "Trust Score reduced by 15% because  |
    |   a rule-based contradiction was      |
    |   detected between Weather and        |
    |   Satellite data."                    |
    +=======================================+
                    |
                    v
    +=======================================+
    |     FLOOD INTELLIGENCE REPORT         |
    |     (Terminal + JSON Output)           |
    +=======================================+
```

---

## Module-by-Module Deep Dive

### Module 1: Data Ingestion Layer

**Files:** `ingestion/ingest.py`, `ingestion/weather.py`, `ingestion/sentinel.py`,
`ingestion/osm.py`, `ingestion/dem.py`, `ingestion/river.py`, `ingestion/historical.py`

**What it does:**

When you type a city name (e.g., "Dehradun"), the system first geocodes it to
latitude/longitude coordinates using the Nominatim API. Then it simultaneously
fetches data from five independent sources:

| Source | API / Method | What it Provides |
|--------|-------------|-----------------|
| Weather | Open-Meteo (Live) | Rainfall (mm), Humidity (%), Temperature, Wind Speed |
| Satellite | Sentinel-1 SAR (Google Earth Engine) | Flood Extent (% of area underwater) |
| OpenStreetMap | Overpass API (Live) | Distance to nearest river, number of buildings/hospitals nearby |
| Climate | Historical flood database | Long-term flood frequency for the region |
| DEM | Open-Elevation API (Live) | Terrain elevation in metres |

**How it works technically:**

Each source has its own Python module. For example, `weather.py` constructs a URL
like this:

```
https://api.open-meteo.com/v1/forecast?latitude=30.32&longitude=78.03
  &current=temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m
```

It sends an HTTP GET request, parses the JSON response, and extracts the `current`
weather values. Each module returns a Pandas DataFrame with a `Location_ID` column
that allows them to be merged later.

**Output:** Five separate CSV files saved to `data/raw/` (e.g., `weather_raw.csv`,
`sentinel_raw.csv`, etc.)

---

### Module 2: Data Validation & Consistency Engine

**Files:** `preprocessing/preprocess.py`, `validation/quality.py`,
`validation/anomaly.py`, `validation/consistency.py`, `validation/reliability.py`

**What it does:**

Before trusting ANY of the ingested data, the system runs it through four
sequential validation checks.

#### Step 2a: Schema Alignment (`preprocess.py`)

All five raw CSV files are loaded from disk and merged into a single unified
DataFrame using a LEFT JOIN on `Location_ID`. This ensures every data source
is aligned to the same location.

#### Step 2b: Quality Assessment (`quality.py`)

Checks for:
- Missing values in critical columns
- Values outside physically possible ranges (e.g., rainfall cannot be negative,
  humidity cannot exceed 100%)

If any check fails, the row is tagged with `Quality_Passed = False`.

#### Step 2c: ML Anomaly Detection (`anomaly.py`)

Uses **Scikit-Learn's Isolation Forest** algorithm to detect multi-variate
statistical anomalies. The model looks at all numeric features simultaneously
(rainfall, flood extent, humidity, river distance) and identifies data points
that are statistically impossible outliers.

For example, if one location reports 500mm rainfall but every other feature
(humidity, flood extent, river level) is near zero, the Isolation Forest
will flag this as a mathematical anomaly.

Technical details:
- Algorithm: Isolation Forest
- Contamination rate: 10% (assumes up to 10% of data could be anomalous)
- Minimum samples required: 3 (will skip if fewer data points exist)

If an anomaly is detected, the row is tagged with `Anomaly_Flag = True`.

#### Step 2d: Rule-Based Consistency Check (`consistency.py`)

This is a deterministic, domain-expert rule engine. It encodes flood science
knowledge as hard rules. For example:

```python
# If rainfall > 100mm but flood extent < 1%, flag as contradiction
contradiction = (df['Rainfall_mm'] > 100) & (df['Flood_Extent_Pct'] < 1)
```

This catches cases where two sensors fundamentally disagree with each other.
If triggered, the row is tagged with `Consistency_Flag = True`.

#### Step 2e: Source Reliability Scoring (`reliability.py`)

Assigns each data source a baseline reliability percentage based on its
known accuracy and freshness.

**Output:** A single validated DataFrame with boolean flags (`Quality_Passed`,
`Anomaly_Flag`, `Consistency_Flag`) and a `Source_Reliability_Score`.

---

### Module 3: Trust Scoring Framework

**File:** `trust/trust_score.py`

**What it does:**

This is the mathematical heart of the system. It takes the validated DataFrame
and computes a single Trust Score (0% to 100%) for each location.

**The formula:**

```
Trust Score = 100% - Penalties

Where Penalties:
  - Anomaly_Flag detected?       => -20%
  - Consistency_Flag detected?   => -15%
  - Quality check failed?        => -50%
  - Missing wind speed data?     =>  -5%
```

**Example (Delhi demo):**

```
Base Score:          100%
Consistency_Flag:    True  (Weather says 250mm rain, Satellite says 0% flood)
Penalty:             -15%
Final Trust Score:   85%
```

**Example (Dehradun demo):**

```
Base Score:          100%
All flags:           False (All 5 sources agree: heavy rain + heavy flooding)
Penalty:              0%
Final Trust Score:   100%
```

The Trust Score is normalized to a 0.0 - 1.0 scale and stored as
`Final_Trust_Score` in the DataFrame.

---

### Module 4: Intelligence Generation Layer

**File:** `intelligence/recommendation.py`

**What it does:**

Takes the validated, trust-scored data and generates actionable intelligence
that a disaster management authority can immediately act on.

**Decision logic:**

```
IF rainfall > 100mm OR flood_extent > 30%:
    Flood Risk = HIGH
    Recommendations:
      - Issue Flood Warning
      - Notify Disaster Response Teams
      - Monitor River Levels
      - Prepare Evacuation Plans

ELSE:
    Flood Risk = LOW
    Recommendations:
      - Continue Automated Monitoring
      - Log Baseline Data
```

The system also calculates:
- **Confidence**: Trust Score + 3% (represents overall system confidence)
- **Uncertainty**: LOW if trust > 80%, MEDIUM if 60-80%, HIGH if < 60%

---

### Module 5: Explainability Module

**File:** `explainability/explain.py`

**What it does:**

AI systems are often "black boxes" where nobody knows why a decision was made.
In disaster management, this is unacceptable because lives depend on
understanding the reasoning.

The Explainability Module translates the mathematical Trust Score into
plain English.

**How it works:**

```python
if trust_score == 1.0:
    reason = "Perfect score. All validation checks passed."
else:
    if anomaly_flag:
        reason += "-20%: ML Anomaly detected (multi-variate contradiction)."
    if consistency_flag:
        reason += "-15%: Rule-based contradiction detected (Weather vs Satellite)."
```

**Example output:**

```
Why was this recommendation generated?
  -15%: Rule-based contradiction detected (e.g. Weather vs Satellite).
  Rainfall exceeds historical average.
  Four of five sources agree.
```

This gives complete transparency to the human decision-maker.

---

## Live Demo Scenarios

### Scenario 1: Dehradun (HIGH Risk, Perfect Trust)

All 5 sources agree that Dehradun is experiencing severe flooding:
- Rainfall: 310.5 mm
- Flood Extent: 48.5%
- Trust Score: 100% (no contradictions)
- Result: HIGH risk with full evacuation recommendations

This demonstrates the system correctly identifying a real-world emergency
when all sources are in agreement.

### Scenario 2: Delhi (HIGH Risk, Reduced Trust)

The weather API reports 250mm of rain, but the satellite reports 0% flooding:
- Rainfall: 250.0 mm
- Flood Extent: 0.0%
- Trust Score: 85% (15% deducted for contradiction)
- Result: HIGH risk but with a documented warning about unreliable satellite data

This demonstrates the system catching sensor contradictions and transparently
reducing confidence while still issuing a warning because the rainfall alone
is dangerous enough.

### Scenario 3: Any Normal City (LOW Risk)

For cities not experiencing emergencies, the live APIs return normal values:
- Rainfall: 0.0 mm (no rain right now)
- Flood Extent: Low
- Trust Score: 100%
- Result: LOW risk, continue automated monitoring

This demonstrates the system correctly identifying safe conditions and NOT
raising a false alarm.

---

## Technologies Used

| Component | Technology |
|-----------|-----------|
| Language | Python 3.x |
| Data Processing | Pandas, NumPy |
| ML Anomaly Detection | Scikit-Learn (Isolation Forest) |
| Weather Data | Open-Meteo REST API |
| Satellite Imagery | Google Earth Engine (Sentinel-1 SAR) |
| Map/Infrastructure Data | OpenStreetMap Overpass API |
| Elevation Data | Open-Elevation API |
| Geocoding | Nominatim (OpenStreetMap) |
| Logging | Python logging module |

---

## File Structure

```
GeoTrust-AI/
|-- main.py                          # Entry point, runs the full pipeline
|-- config.py                        # API URLs, directory paths, constants
|-- ingestion/
|   |-- ingest.py                    # Orchestrates all 5 data fetches
|   |-- weather.py                   # Open-Meteo API integration
|   |-- sentinel.py                  # Sentinel-1 SAR / Earth Engine
|   |-- osm.py                       # OpenStreetMap Overpass API
|   |-- dem.py                       # Digital Elevation Model
|   |-- river.py                     # River gauge data
|   |-- historical.py                # Historical flood frequency
|-- preprocessing/
|   |-- preprocess.py                # Schema alignment and merging
|-- validation/
|   |-- quality.py                   # Missing value and range checks
|   |-- anomaly.py                   # Isolation Forest ML detection
|   |-- consistency.py               # Rule-based contradiction engine
|   |-- reliability.py               # Source reliability scoring
|-- trust/
|   |-- trust_score.py               # Mathematical trust computation
|-- intelligence/
|   |-- recommendation.py            # Actionable intelligence generation
|-- explainability/
|   |-- explain.py                   # Human-readable reasoning
|-- utils/
|   |-- logger.py                    # Centralised logging
|   |-- geocoder.py                  # City name to lat/lon conversion
|-- data/
|   |-- raw/                         # Raw CSV files from each source
|   |-- processed/                   # Merged unified dataset
|   |-- outputs/                     # Final JSON report + validated CSV
```

---

## How to Run

```bash
cd GeoTrust-AI
pip install pandas numpy scikit-learn requests earthengine-api
python main.py
```

When prompted, type a city name (e.g., "Dehradun", "Delhi", "Mumbai").
The system will fetch live data, validate it, compute trust scores,
and print the full Flood Intelligence Report to the terminal.

---

## Alignment with Problem Statement

| Expected Component | Our Implementation |
|--------------------|--------------------|
| Data Ingestion Layer | 5 live APIs fetched and merged into unified schema |
| Data Validation & Consistency Engine | Quality checks, Isolation Forest ML, rule-based contradiction detection |
| Trust Scoring Framework | Mathematical penalty-based scoring (100% base minus deductions) |
| Intelligence Generation Layer | Dynamic flood risk assessment with actionable recommendations |
| Explainability Module | Human-readable reasoning for every trust score deduction |
