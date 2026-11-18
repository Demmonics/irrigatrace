/**
 * TypeScript API Types for IrrigaTrace
 * Generated and synchronized with openapi.json and domain models
 */

export type RecommendedAction = 'WAIT' | 'IRRIGATE' | 'SUPPRESS_RAIN' | 'REDUCE_DURATION';
export type ReviewAction = 'APPROVE' | 'MODIFY' | 'REJECT';
export type DecisionStatus = 'COLLECTED' | 'RECOMMENDED' | 'RECORDED' | 'AWAITING_REVIEW' | 'FINALIZED' | 'OUTCOME_RECORDED';
export type CropStage = 'GERMINATION' | 'TILLERING' | 'CANOPY_GROWTH' | 'YIELD_FORMATION' | 'RIPENING';

export type EventType =
  | 'DECISION_CREATED'
  | 'INPUTS_FROZEN'
  | 'AI_RECOMMENDED'
  | 'EXPLANATION_GENERATED'
  | 'REVIEW_REQUESTED'
  | 'REVIEW_APPROVED'
  | 'REVIEW_MODIFIED'
  | 'REVIEW_REJECTED'
  | 'OUTCOME_OBSERVED'
  | 'INTEGRITY_VERIFIED';

export interface FarmPlot {
  id: string;
  name: string;
  area_hectares: number;
  crop_type: string;
  soil_type: string;
  stage: CropStage;
  target_moisture_pct?: number;
  critical_moisture_pct?: number;
  created_at?: string;
}

export interface SensorReading {
  plot_id: string;
  timestamp: string;
  soil_moisture_pct: number;
  ambient_temp_c: number;
  humidity_pct: number;
  electrical_conductivity?: number;
}

export interface WeatherSnapshot {
  forecast_time: string;
  temp_max_c: number;
  temp_min_c: number;
  rain_probability_pct: number;
  expected_rain_mm: number;
  wind_speed_kmh?: number;
}

export interface Recommendation {
  action: RecommendedAction;
  recommended_duration_h: number;
  confidence: number;
  fired_rules: string[];
  factors: Record<string, number | string | boolean>;
}

export interface EngineInputs {
  plot: FarmPlot;
  sensor: SensorReading;
  weather: WeatherSnapshot;
  days_since_last_irrigation: number;
}

export interface DecisionSnapshot {
  id: string;
  decision_id: string;
  snapshot_time: string;
  inputs: EngineInputs;
  recommendation: Recommendation;
}

export interface HumanReview {
  id: string;
  decision_id: string;
  action: ReviewAction;
  final_duration_h: number;
  modified_by: string;
  reason_code: string;
  justification_notes?: string;
  reviewed_at: string;
}

export interface DecisionExplanation {
  decision_id: string;
  factors: Array<{
    name: string;
    value: string | number;
    impact: 'INCREASE' | 'DECREASE' | 'NEUTRAL';
    description: string;
  }>;
  narrative_summary: string;
  provenance: string;
  generated_at: string;
}

export interface DecisionEvent {
  id: string;
  decision_id: string;
  seq: number;
  seq_in_chain: number;
  event_type: EventType;
  actor_id: string;
  payload_json: string;
  prev_hash: string;
  this_hash: string;
  created_at: string;
}

export interface OutcomeRecord {
  id: string;
  decision_id: string;
  actual_duration_h: number;
  soil_moisture_after_pct: number;
  observed_rainfall_mm: number;
  water_stress_observed: boolean;
  notes?: string;
  recorded_at: string;
}

export interface IrrigationDecision {
  id: string;
  plot_id: string;
  status: DecisionStatus;
  created_at: string;
  snapshot: DecisionSnapshot;
  review?: HumanReview | null;
  explanation?: DecisionExplanation | null;
  outcome?: OutcomeRecord | null;
  events: DecisionEvent[];
}

export interface DecisionComparison {
  decision_a: IrrigationDecision;
  decision_b: IrrigationDecision;
  delta_inputs: Record<string, { a: any; b: any; delta?: any }>;
  delta_outputs: {
    action_changed: boolean;
    duration_delta_h: number;
    confidence_delta: number;
  };
  rule_diffs: {
    fired_in_both: string[];
    only_in_a: string[];
    only_in_b: string[];
  };
  flip_analysis: Array<{
    variable: string;
    value_a: any;
    value_b: any;
    flips_action: boolean;
    resulting_action: RecommendedAction;
    resulting_duration_h: number;
  }>;
  summary_text: string;
}

export interface IntegrityVerificationReport {
  decision_id: string;
  valid: boolean;
  event_count: number;
  genesis_hash: string;
  final_hash: string;
  broken_seq?: number | null;
  details?: string;
}

export interface KpiSummary {
  total_decisions: number;
  awaiting_review: number;
  modified_by_humans: number;
  outcomes_recorded: number;
  override_rate_pct: number;
}
