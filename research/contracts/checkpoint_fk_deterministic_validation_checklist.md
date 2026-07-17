# Checkpoint FK Deterministic Validation Checklist

Future FL must pass every item before reporting its frozen outcome artifact:

- source population SHA-256 equals `db59643834e06acbfebb66026634f4f561fb9b07131fdca1513e3585cd51c74b`
- exactly 1,079 known FJ event IDs; exactly four rows per ID; total 4,316 rows
- unique `(event_id, horizon_bars)` and unique deterministic `outcome_row_id`
- horizon domain is exactly 6, 12, 24, 48
- entry and ATR exactly match frozen FJ fields; TP/SL formulas match direction and 1.5/1.0 multiples
- confirmation bar is never evaluated; valid-bar counting begins on next valid H1 bar
- all outcomes are in the frozen exclusive domain and all exclusions have explicit reasons
- unverified gap records exact start/end; resolved-before-gap results remain preserved
- longer horizon cannot contradict an earlier TP_FIRST, SL_FIRST, or AMBIGUOUS_SAME_BAR result
- source row keys and first-touch bar key resolve; no interpolation, reconstruction, or silent gap bridge
- no UUID, random value, or runtime timestamp in canonical outputs
- deterministic replay is byte-identical with zero event/key/row-order mismatches

This checklist is a contract only. It does not calculate an outcome.