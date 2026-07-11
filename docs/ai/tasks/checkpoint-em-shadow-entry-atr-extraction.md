# Checkpoint EM Shadow Entry/ATR Extraction

Date: 2026-07-11

Decision: `SHADOW_ENTRY_ATR_EXACT_EXTRACTION_PASS`.

The offline extractor used only the three original DZ runs and exact-joined authoritative `ea_mirror.log` values to the committed EH eligible population by `run_id + case_id + event_time`, with classification and direction provenance checks.

- EH eligible rows: `1600`
- exact matches: `1600`
- source logs: `156`
- missing/duplicate/unmatched/conflicting/invalid rows: `0`
- execution status: `PASS`
- strategy performance: `NOT_EVALUATED`
- MT5/Strategy Tester: `NOT_RUN`
- EA, presets, optimization, and order logic: `UNCHANGED/NOT_RUN/NOT_APPROVED`
- profitability claim: `false`

Checkpoint EN GOLD# H1 bars export remains blocked until separate user approval. PAF remains `NOT_READY_FOR_ORDER_LOGIC`.
