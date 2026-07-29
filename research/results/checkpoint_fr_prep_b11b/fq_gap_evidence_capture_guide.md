# FQ Gap Primary Evidence Capture Guide

This kit covers all 625 frozen FQ gaps in 43 unranked operational batches. It does not collect evidence, adjudicate a gap, or promise that any evidence will resolve a gap.

## Scope and source identity

Evidence must identify the same XM broker/server and the GOLD symbol. In MT5, an operator must manually open the account/server connection details and record the exact server name before any export. Do not launch MT5 through these tools. Another broker's data cannot establish acceptance and must be declared as conflicting or corroborative-only evidence.

## Primary capture tracks

- Track A: capture a broker/server session schedule with exact broker, server, symbol class, effective date range, time basis, and timezone (or `UNKNOWN`).
- Track B: manually export fresh same-server lower-timeframe or tick history around the missing H1 slots, preserving timestamps and export/source metadata. Never derive it from the frozen FQ CSV files.
- Track C: manually export fresh independent same-server H1 history, with exact broker, server, symbol, and date range. It does not alone prove routine closure unless B11 sufficiency rules are met.
- Track D: save an official broker/session holiday notice with the exact affected date, session hours, source identity, and capture metadata. Generic holiday calendars are corroborative-only.

Screenshots and operator notes are corroborative-only. Repeated `23000100` or similar timestamp patterns are descriptive, not proof. One artifact may cover multiple explicit gap IDs within its declared range.

## Security and packaging

Before staging, remove account numbers, login IDs, names, passwords, credentials, API keys, and tokens. The helper rejects obvious sensitive metadata, absolute paths, symlinks, traversal, unknown or duplicate gap IDs, invalid roles/types, and the three frozen FQ source CSVs.

Run the helper offline from the repository root only after manually collecting and sanitizing a real artifact:

```text
python tools/prepare_fq_gap_evidence_package.py --artifact operator_captures/session.pdf --package-id XM-SCHEDULE-001 --evidence-type BROKER_SERVER_SESSION_SCHEDULE --evidence-role PRIMARY --broker XM --server EXACT_SERVER_NAME --symbol GOLD --time-basis BROKER_SERVER_TIME --timezone-or-unknown UNKNOWN --effective-start 2020-01-01T00:00:00 --effective-end 2020-12-31T23:59:59 --gap-id GQ0001 --source-organization XM --operator-notes sanitized
python tools/prepare_fq_gap_evidence_package.py --artifact operator_captures/ticks.csv --package-id XM-TICKS-001 --evidence-type SAME_BROKER_SERVER_LOWER_TIMEFRAME_OR_TICK_EXPORT --evidence-role PRIMARY --broker XM --server EXACT_SERVER_NAME --symbol GOLD --time-basis BROKER_SERVER_TIME --timezone-or-unknown UNKNOWN --effective-start 2020-01-02T22:00:00 --effective-end 2020-01-03T02:00:00 --gap-id-file operator_captures/gap_ids.txt --source-organization XM --operator-notes sanitized
```

The helper only copies an artifact and writes canonical intake metadata. It never evaluates evidence, changes `accepted_for_bar_skip`, proposes a remediation status, creates OHLC, or interprets outcomes.
