# 05 — Data Model

SQLite, WAL mode, foreign keys ON. Timestamps are ISO-8601 UTC strings. IDs: decisions `IRR-2026-018` style (`IRR-{year}-{seq:03d}`), others ULIDs.

## DDL (`api/sql/schema.sql`)
```sql
PRAGMA foreign_keys = ON;

CREATE TABLE users (
  id TEXT PRIMARY KEY, name TEXT NOT NULL,
  role TEXT NOT NULL CHECK (role IN ('SUPERVISOR','ADMIN','AUDITOR'))
);

CREATE TABLE farm_plots (
  id TEXT PRIMARY KEY, code TEXT UNIQUE NOT NULL, name TEXT NOT NULL,
  area_ha REAL NOT NULL CHECK (area_ha > 0),
  soil_type TEXT NOT NULL, crop TEXT NOT NULL DEFAULT 'sugarcane', variety TEXT,
  planting_date TEXT NOT NULL, irrigation_method TEXT NOT NULL,
  application_rate_mm_h REAL NOT NULL CHECK (application_rate_mm_h > 0),
  geojson TEXT
);

CREATE TABLE sensor_readings (
  id TEXT PRIMARY KEY, plot_id TEXT NOT NULL REFERENCES farm_plots(id),
  ts TEXT NOT NULL, soil_moisture_pct REAL NOT NULL CHECK (soil_moisture_pct BETWEEN 0 AND 100),
  temperature_c REAL NOT NULL, source TEXT NOT NULL CHECK (source IN ('SIMULATED','MANUAL')),
  quality_flag TEXT NOT NULL DEFAULT 'OK' CHECK (quality_flag IN ('OK','SUSPECT','MISSING_FILLED'))
);

CREATE TABLE weather_snapshots (
  id TEXT PRIMARY KEY, plot_id TEXT NOT NULL REFERENCES farm_plots(id),
  captured_at TEXT NOT NULL, rain_probability_pct REAL NOT NULL CHECK (rain_probability_pct BETWEEN 0 AND 100),
  forecast_rain_mm REAL NOT NULL DEFAULT 0, horizon_h INTEGER NOT NULL DEFAULT 48,
  source TEXT NOT NULL CHECK (source IN ('SIMULATED','MANUAL'))
);

CREATE TABLE irrigation_decisions (
  id TEXT PRIMARY KEY, plot_id TEXT NOT NULL REFERENCES farm_plots(id),
  created_at TEXT NOT NULL, ruleset_version TEXT NOT NULL,
  recommended_action TEXT NOT NULL CHECK (recommended_action IN ('IRRIGATE','WAIT','DEFER_RAIN')),
  recommended_duration_h REAL NOT NULL CHECK (recommended_duration_h >= 0),
  confidence REAL NOT NULL CHECK (confidence BETWEEN 0 AND 1),
  status TEXT NOT NULL            -- PROJECTION of events; the only mutable column
);

CREATE TABLE decision_snapshots (
  decision_id TEXT PRIMARY KEY REFERENCES irrigation_decisions(id),
  sensor_reading_id TEXT NOT NULL, weather_snapshot_id TEXT NOT NULL,
  inputs_json TEXT NOT NULL,           -- EngineInputs incl. crop_stage, days_since_last_irrigation
  ruleset_json TEXT NOT NULL,          -- full copy of ruleset used
  engine_version TEXT NOT NULL, engine_code_sha256 TEXT NOT NULL,
  snapshot_sha256 TEXT NOT NULL
);

CREATE TABLE decision_explanations (
  id TEXT PRIMARY KEY, decision_id TEXT NOT NULL REFERENCES irrigation_decisions(id),
  kind TEXT NOT NULL CHECK (kind IN ('DETERMINISTIC','LLM_NARRATIVE','TRANSLATION','COMPARISON_SUMMARY')),
  language TEXT NOT NULL DEFAULT 'en', content_json TEXT NOT NULL, provenance_json TEXT NOT NULL,
  created_at TEXT NOT NULL
);

CREATE TABLE human_reviews (
  id TEXT PRIMARY KEY, decision_id TEXT NOT NULL REFERENCES irrigation_decisions(id),
  reviewer_id TEXT NOT NULL REFERENCES users(id),
  action TEXT NOT NULL CHECK (action IN ('APPROVE','MODIFY','REJECT')),
  reason_code TEXT, reason_text TEXT,
  final_action TEXT NOT NULL CHECK (final_action IN ('IRRIGATE','WAIT','DEFER_RAIN')),
  final_duration_h REAL NOT NULL CHECK (final_duration_h >= 0),
  created_at TEXT NOT NULL,
  CHECK (action = 'APPROVE' OR (reason_code IS NOT NULL AND length(trim(coalesce(reason_text,''))) > 0))
);

CREATE TABLE decision_events (
  seq INTEGER PRIMARY KEY AUTOINCREMENT,
  decision_id TEXT NOT NULL REFERENCES irrigation_decisions(id),
  event_type TEXT NOT NULL, actor_id TEXT NOT NULL, actor_role TEXT NOT NULL,
  occurred_at TEXT NOT NULL, payload_json TEXT NOT NULL,
  prev_hash TEXT NOT NULL, event_hash TEXT NOT NULL
);
CREATE INDEX idx_events_decision ON decision_events(decision_id, seq);

CREATE TABLE outcome_records (
  id TEXT PRIMARY KEY, decision_id TEXT NOT NULL REFERENCES irrigation_decisions(id),
  recorded_by TEXT NOT NULL REFERENCES users(id), recorded_at TEXT NOT NULL,
  actual_duration_h REAL, soil_moisture_after_pct REAL, actual_rainfall_mm REAL,
  water_stress_observed INTEGER CHECK (water_stress_observed IN (0,1)),
  crop_health_note TEXT, notes TEXT
);
```

## Append-only triggers (`api/sql/triggers.sql`)
```sql
CREATE TRIGGER events_no_update BEFORE UPDATE ON decision_events BEGIN SELECT RAISE(ABORT,'decision_events is append-only'); END;
CREATE TRIGGER events_no_delete BEFORE DELETE ON decision_events BEGIN SELECT RAISE(ABORT,'decision_events is append-only'); END;
CREATE TRIGGER snap_no_update  BEFORE UPDATE ON decision_snapshots BEGIN SELECT RAISE(ABORT,'snapshots are immutable'); END;
CREATE TRIGGER snap_no_delete  BEFORE DELETE ON decision_snapshots BEGIN SELECT RAISE(ABORT,'snapshots are immutable'); END;
CREATE TRIGGER rev_no_update   BEFORE UPDATE ON human_reviews BEGIN SELECT RAISE(ABORT,'reviews are immutable'); END;
CREATE TRIGGER rev_no_delete   BEFORE DELETE ON human_reviews BEGIN SELECT RAISE(ABORT,'reviews are immutable'); END;
CREATE TRIGGER expl_no_update  BEFORE UPDATE ON decision_explanations BEGIN SELECT RAISE(ABORT,'explanations are immutable'); END;
CREATE TRIGGER dec_core_immutable BEFORE UPDATE OF id, plot_id, created_at, ruleset_version, recommended_action, recommended_duration_h, confidence
  ON irrigation_decisions BEGIN SELECT RAISE(ABORT,'original recommendation is immutable'); END;
CREATE TRIGGER dec_no_delete BEFORE DELETE ON irrigation_decisions BEGIN SELECT RAISE(ABORT,'decisions cannot be deleted'); END;
```
Only `irrigation_decisions.status` may be updated (projection cache). `outcome_records` are insert-only by application convention; corrections are new rows (latest wins in the view, all kept).

## Hash chain
```
GENESIS      = sha256("GENESIS:" + decision_id)
event_hash_n = sha256( canonical_json({decision_id, seq_in_chain, event_type, actor_id, actor_role, occurred_at, payload}) + prev_hash_n )
prev_hash_1  = GENESIS ; prev_hash_n = event_hash_{n-1}
```
`canonical_json` = sorted keys, separators `(",",":")`, UTF-8, floats rendered with `repr`. `IntegrityService.verify(decision_id)` recomputes the chain, checks snapshot hash, checks `status` equals the projection of events, and returns `{valid, broken_at_seq?, reason?}`. A "Tamper test" button is **not** exposed in UI; tamper testing lives in tests (they disable triggers on a temp DB copy and assert verification fails).

## Event types and payloads
| Event | Payload essentials |
|---|---|
| `SENSOR_RECEIVED` | reading id, moisture, temp, source, quality |
| `WEATHER_CAPTURED` | snapshot id, rain prob, rain mm, horizon, source |
| `RECOMMENDATION_GENERATED` | action, duration_h, confidence, ruleset_version, engine_version |
| `EXPLANATION_ATTACHED` | explanation id (deterministic) |
| `NARRATIVE_ATTACHED` | explanation id, provenance summary |
| `REVIEW_OPENED` | reviewer |
| `REVIEW_APPROVED` / `REVIEW_MODIFIED` / `REVIEW_REJECTED` | review id, reason code/text, final action/duration |
| `DECISION_FINALIZED` | final action/duration, source (AI or human) |
| `ACTION_RECORDED` | actual duration, executed_at |
| `OUTCOME_RECORDED` | outcome record id |
| `REPRODUCTION_CHECKED` | match bool, diffs |

Event timestamps in the replay are **real recorded times**. The seed script must create realistic, ordered timestamps (the doc's example: 09:41:58 → 10:05:47) by writing events with explicit `occurred_at` through the same recorder (clock injected).

## Reason codes
`LOCAL_FIELD_CONDITIONS, RECENT_RAIN_OBSERVED, PUMP_OR_POWER_CONSTRAINT, WATER_AVAILABILITY, SENSOR_DOUBT, CROP_OBSERVATION, OTHER`

## Status values
`GENERATED, PENDING_REVIEW, APPROVED, MODIFIED, REJECTED, FINALIZED, ACTION_RECORDED, OUTCOME_RECORDED`. Dashboard "Modified" and "Pending" chips derive from review action + status.
