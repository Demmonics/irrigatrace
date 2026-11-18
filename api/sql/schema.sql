PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS users (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  role TEXT NOT NULL CHECK (role IN ('SUPERVISOR','ADMIN','AUDITOR'))
);

CREATE TABLE IF NOT EXISTS farm_plots (
  id TEXT PRIMARY KEY,
  code TEXT UNIQUE NOT NULL,
  name TEXT NOT NULL,
  area_ha REAL NOT NULL CHECK (area_ha > 0),
  soil_type TEXT NOT NULL,
  crop TEXT NOT NULL DEFAULT 'sugarcane',
  variety TEXT,
  planting_date TEXT NOT NULL,
  irrigation_method TEXT NOT NULL,
  application_rate_mm_h REAL NOT NULL CHECK (application_rate_mm_h > 0),
  geojson TEXT
);

CREATE TABLE IF NOT EXISTS sensor_readings (
  id TEXT PRIMARY KEY,
  plot_id TEXT NOT NULL REFERENCES farm_plots(id),
  ts TEXT NOT NULL,
  soil_moisture_pct REAL NOT NULL CHECK (soil_moisture_pct BETWEEN 0 AND 100),
  temperature_c REAL NOT NULL,
  source TEXT NOT NULL CHECK (source IN ('SIMULATED','MANUAL')),
  quality_flag TEXT NOT NULL DEFAULT 'OK' CHECK (quality_flag IN ('OK','SUSPECT','MISSING_FILLED'))
);

CREATE TABLE IF NOT EXISTS weather_snapshots (
  id TEXT PRIMARY KEY,
  plot_id TEXT NOT NULL REFERENCES farm_plots(id),
  captured_at TEXT NOT NULL,
  rain_probability_pct REAL NOT NULL CHECK (rain_probability_pct BETWEEN 0 AND 100),
  forecast_rain_mm REAL NOT NULL DEFAULT 0,
  horizon_h INTEGER NOT NULL DEFAULT 48,
  source TEXT NOT NULL CHECK (source IN ('SIMULATED','MANUAL'))
);

CREATE TABLE IF NOT EXISTS irrigation_decisions (
  id TEXT PRIMARY KEY,
  plot_id TEXT NOT NULL REFERENCES farm_plots(id),
  created_at TEXT NOT NULL,
  ruleset_version TEXT NOT NULL,
  recommended_action TEXT NOT NULL CHECK (recommended_action IN ('IRRIGATE','WAIT','DEFER_RAIN')),
  recommended_duration_h REAL NOT NULL CHECK (recommended_duration_h >= 0),
  confidence REAL NOT NULL CHECK (confidence BETWEEN 0 AND 1),
  status TEXT NOT NULL            -- PROJECTION of events; the only mutable column
);

CREATE TABLE IF NOT EXISTS decision_snapshots (
  decision_id TEXT PRIMARY KEY REFERENCES irrigation_decisions(id),
  sensor_reading_id TEXT NOT NULL,
  weather_snapshot_id TEXT NOT NULL,
  inputs_json TEXT NOT NULL,           -- EngineInputs incl. crop_stage, days_since_last_irrigation
  ruleset_json TEXT NOT NULL,          -- full copy of ruleset used
  engine_version TEXT NOT NULL,
  engine_code_sha256 TEXT NOT NULL,
  snapshot_sha256 TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS decision_explanations (
  id TEXT PRIMARY KEY,
  decision_id TEXT NOT NULL REFERENCES irrigation_decisions(id),
  kind TEXT NOT NULL CHECK (kind IN ('DETERMINISTIC','LLM_NARRATIVE','TRANSLATION','COMPARISON_SUMMARY')),
  language TEXT NOT NULL DEFAULT 'en',
  content_json TEXT NOT NULL,
  provenance_json TEXT NOT NULL,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS human_reviews (
  id TEXT PRIMARY KEY,
  decision_id TEXT NOT NULL REFERENCES irrigation_decisions(id),
  reviewer_id TEXT NOT NULL REFERENCES users(id),
  action TEXT NOT NULL CHECK (action IN ('APPROVE','MODIFY','REJECT')),
  reason_code TEXT,
  reason_text TEXT,
  final_action TEXT NOT NULL CHECK (final_action IN ('IRRIGATE','WAIT','DEFER_RAIN')),
  final_duration_h REAL NOT NULL CHECK (final_duration_h >= 0),
  created_at TEXT NOT NULL,
  CHECK (action = 'APPROVE' OR (reason_code IS NOT NULL AND length(trim(coalesce(reason_text,''))) > 0))
);

CREATE TABLE IF NOT EXISTS decision_events (
  seq INTEGER PRIMARY KEY AUTOINCREMENT,
  decision_id TEXT NOT NULL REFERENCES irrigation_decisions(id),
  event_type TEXT NOT NULL,
  actor_id TEXT NOT NULL,
  actor_role TEXT NOT NULL,
  occurred_at TEXT NOT NULL,
  payload_json TEXT NOT NULL,
  prev_hash TEXT NOT NULL,
  event_hash TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_events_decision ON decision_events(decision_id, seq);

CREATE TABLE IF NOT EXISTS outcome_records (
  id TEXT PRIMARY KEY,
  decision_id TEXT NOT NULL REFERENCES irrigation_decisions(id),
  recorded_by TEXT NOT NULL REFERENCES users(id),
  recorded_at TEXT NOT NULL,
  actual_duration_h REAL,
  soil_moisture_after_pct REAL,
  actual_rainfall_mm REAL,
  water_stress_observed INTEGER CHECK (water_stress_observed IN (0,1)),
  crop_health_note TEXT,
  notes TEXT
);
