CREATE TRIGGER IF NOT EXISTS events_no_update BEFORE UPDATE ON decision_events BEGIN SELECT RAISE(ABORT,'decision_events is append-only'); END;
CREATE TRIGGER IF NOT EXISTS events_no_delete BEFORE DELETE ON decision_events BEGIN SELECT RAISE(ABORT,'decision_events is append-only'); END;
CREATE TRIGGER IF NOT EXISTS snap_no_update  BEFORE UPDATE ON decision_snapshots BEGIN SELECT RAISE(ABORT,'snapshots are immutable'); END;
CREATE TRIGGER IF NOT EXISTS snap_no_delete  BEFORE DELETE ON decision_snapshots BEGIN SELECT RAISE(ABORT,'snapshots are immutable'); END;
CREATE TRIGGER IF NOT EXISTS rev_no_update   BEFORE UPDATE ON human_reviews BEGIN SELECT RAISE(ABORT,'reviews are immutable'); END;
CREATE TRIGGER IF NOT EXISTS rev_no_delete   BEFORE DELETE ON human_reviews BEGIN SELECT RAISE(ABORT,'reviews are immutable'); END;
CREATE TRIGGER IF NOT EXISTS expl_no_update  BEFORE UPDATE ON decision_explanations BEGIN SELECT RAISE(ABORT,'explanations are immutable'); END;
CREATE TRIGGER IF NOT EXISTS dec_core_immutable BEFORE UPDATE OF id, plot_id, created_at, ruleset_version, recommended_action, recommended_duration_h, confidence
  ON irrigation_decisions BEGIN SELECT RAISE(ABORT,'original recommendation is immutable'); END;
CREATE TRIGGER IF NOT EXISTS dec_no_delete BEFORE DELETE ON irrigation_decisions BEGIN SELECT RAISE(ABORT,'decisions cannot be deleted'); END;
