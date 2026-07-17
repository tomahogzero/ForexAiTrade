# Checkpoint FJ: Frozen Historical Event Population Generation

วันที่: 2026-07-17

## ขอบเขต

FJ execute detector ที่ FI merge (`f13108b49dfccd26bb2a08ca5d791c034239abee`) กับ approved GOLD# H1 yearly CSV เฉพาะปี 2023-2025 เพื่อ generate frozen event population และตรวจ integrity. ไม่มี TP/SL, outcome, subgroup, performance interpretation, optimization, MT5/Strategy Tester, EA/preset หรือ order logic.

## Preflight และ Source Provenance

FI fixtures ผ่าน `12/12` และ golden fixture hash ยังคง `0b13abedc4f71f5be160b18830de69537438351ba13ec4cf2671616bf9db6abc`. Detector SHA-256 คือ `9d7496581806d267df9130a35c0ec0dd948b6d77fcc30d8cca115edd4b746144`.

แหล่งข้อมูล raw ไม่ถูก commit; manifest ที่ commit บันทึก absolute paths, bytes, row counts, date ranges และ SHA-256 ของ:

- `GOLD#_H1_202301030100_202312292300.csv`: 5,894 rows
- `GOLD#_H1_202401020100_202412312000.csv`: 5,928 rows
- `GOLD#_H1_202501020800_202512311900.csv`: 5,894 rows

รวม `17,716` bars, coverage `2023-01-03T01:00:00` ถึง `2025-12-31T19:00:00`. Schema, chronological ordering และ duplicate source timestamp ผ่าน (`0`). Wrapper assert source hashes และ frozen EO policy exactly `745` accepted closures / `28` unverified gaps; mismatch จะ stop.

## Frozen Gap Handling

ใช้ accepted daily/weekend closures จาก EO/EU policy โดยไม่สร้าง bar. Unverified gaps `28` ยังคง `BLOCKED_UNCLASSIFIED_GAP`, set fail-closed only at their next source bar, และไม่มี interpolation/inference/bridge. Candidate ที่ sequence ถูกแตะ gap ได้ `DATA_INCOMPLETE_GAP` (`13` records). broker-history completeness remains `NOT_PROVEN`.

## Proven Defect Correction

FJ regression proved that FI retained a confirmed swing across an unverified gap and could later emit an event from that pre-gap swing after enough post-gap ATR history. This violated FH/FJ fail-closed sequence integrity. The only implementation change resets active swing state when `gap_before` is unverified; it does not alter swing width, break/retest/confirmation, IDs, ATR, or any parameter. The existing 12 fixture cases still pass; their canonical terminal-output golden hash is rebaselined to `0b13abedc4f71f5be160b18830de69537438351ba13ec4cf2671616bf9db6abc` because the gap fixture now carries the corrected fail-closed state behavior.
## Event Population

Decision: `FJ_PASS_POPULATION_GENERATED`.

- `EVENT_EMITTED`: `1,079`
- LONG: `588`; SHORT: `491`
- 2023: `352` (LONG 176, SHORT 176)
- 2024: `376` (LONG 216, SHORT 160)
- 2025: `351` (LONG 196, SHORT 155)
- first event: `2023-01-05T14:00:00`; last event: `2025-12-31T11:00:00`
- event IDs unique: `1,079`; duplicate semantic events: `0`; unresolved source-row keys: `0`

ไม่มี sample-size threshold ถูกสร้างขึ้นใหม่; FJ รายงาน count จริงเท่านั้น และผลนี้ไม่ใช่ performance evidence.

## Terminal and Data Quality

Terminal counts: `EVENT_EMITTED=1078`, `NO_BREAK=2`, `RETEST_NOT_FOUND_WITHIN_12_BARS=267`, `CONFIRMATION_NOT_FOUND_WITHIN_12_BARS=174`, `DATA_INCOMPLETE_GAP=13`, `INSUFFICIENT_LEFT_HISTORY=2`, `INSUFFICIENT_RIGHT_HISTORY=3`, `ATR_UNAVAILABLE=16`, `DUPLICATE_SUPPRESSED=1130`.

Candidate-status artifact records terminal status/state, candidate/event/swing identifiers where available, gap start/end for gap terminals, and explicit exclusion reason. The frozen FI terminal record does not retain a terminal timestamp for every non-gap/non-duplicate exclusion; data-quality year report therefore records those as `UNKNOWN`, rather than inferring a year.

## Integrity and Replay

- event timestamp order, event=confirmation timestamp, entry reference=confirmation close, finite ATR, direction domain, source-key resolution, unique IDs และ one-event-per-break checks: `PASS`
- replay byte-identical: `true`; mismatch count: `0`
- event population SHA-256: `db59643834e06acbfebb66026634f4f561fb9b07131fdca1513e3585cd51c74b`
- exclusion population SHA-256: `1a150cfc3ae0f338e0f43710187c9bc6363e32dd453fd85a9e5f4a231e4952ed`
- terminal summary SHA-256: `b9edb4f6455d4742e9e77f1d3b23b920c145cc1b3eee3d53eed9d1b05235b1ef`
- population summary SHA-256: `5a45eb6e58b7b38764c6ecbf51fbf6e8472c702b8ebe28c97bee9beafcfba408`

## Deliverables

- `research/results/checkpoint_fj_historical_event_population/checkpoint_fj_event_population.csv`
- `research/results/checkpoint_fj_historical_event_population/checkpoint_fj_candidate_status.csv`
- `research/results/checkpoint_fj_historical_event_population/checkpoint_fj_population_summary.json`
- `research/results/checkpoint_fj_historical_event_population/checkpoint_fj_deterministic_replay.json`
- `research/results/checkpoint_fj_historical_event_population/checkpoint_fj_source_manifest.json`

## Future Checkpoint FK (not created)

FK may only define the shadow-outcome contract for this frozen FJ population: eligibility, TP/SL references, horizons, ambiguity and gap handling. FK must not calculate outcomes in the same checkpoint and may not change FF/FH/FI/FJ rules, create order logic, or claim profitability.

## Status

- execution status: `PASS`
- strategy performance: `NOT_EVALUATED`
- order logic: `NOT_APPROVED`
- candidate: `NOT_READY_FOR_ORDER_LOGIC`
- profitability: `NOT_CLAIMED`