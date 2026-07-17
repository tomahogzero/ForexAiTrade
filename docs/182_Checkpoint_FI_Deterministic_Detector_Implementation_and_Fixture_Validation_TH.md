# Checkpoint FI: Deterministic Detector Implementation and Fixture Validation

วันที่: 2026-07-17

## ขอบเขต

FI implement เฉพาะ frozen FH detector สำหรับ `MARKET_STRUCTURE_BREAK_RETEST_CONFIRMATION_V1` และ validate ด้วย deterministic fixtures ที่ commit อยู่ใน repository เท่านั้น. ไม่ได้อ่านหรือ run กับ GOLD# H1 historical dataset, ไม่ได้สร้าง production event population และไม่มี TP/SL outcome.

## Implementation

โมดูล `tools/market_structure_break_retest_detector.py` implement state machine ตาม FH:

- `SEEK_CONFIRMED_SWING`: strict 2-left/2-right, ใช้ swing หลัง right-side bars ปิด
- `SEEK_BREAK`: LONG close > confirmed swing high, SHORT close < confirmed swing low; wick-only reject
- `SEEK_RETEST`: เริ่ม next valid H1 bar หลัง break, break candle เป็น bar 0, exact level only และนับสูงสุด 12 valid trading bars
- `SEEK_CONFIRMATION`: หลัง retest เท่านั้น; LONG `close > open` และ `close > previous high`, SHORT `close < open` และ `close < previous low`

candidate ถูก anchor กับ swing/break เดิมตลอด lifecycle. Swing ใหม่ไม่ re-anchor candidate ที่เปิดอยู่. Gap/invalid continuity terminal เป็น `DATA_INCOMPLETE_GAP`; ไม่มี interpolation, reconstructed bar หรือ wall-clock retest counter.

IDs เป็น SHA-256 deterministic canonical source fields ตาม FH: `swing_id`, `break_id`, `candidate_id`, `event_id`. ไม่มี random UUID หรือ current timestamp. Event timestamp คือ confirmation candle close timestamp; entry reference คือ confirmation close เพื่อ diagnostic only.

## Fixture Inputs and Expected Outputs

- input fixture data: `tests/fixtures/checkpoint_fi_detector_inputs.json`
- fixture manifest: `tests/fixtures/checkpoint_fi_detector_cases.json`
- golden expected outputs: `tests/fixtures/checkpoint_fi_detector_expected.json`
- runner: `tools/run_checkpoint_fi_detector_fixtures.py`

Fixture tests A-L ครบ: valid LONG/SHORT, wick-only, swing not confirmed, retest after 12 bars, confirmation failure, gap, duplicate, newer swing no re-anchor, tie order, byte-identical replay และ non-semantic metadata/input order.

## Validation Result

- syntax/static check: `PASS` (`python -m py_compile`)
- fixture assertions: `12/12 PASS`
- exact event schema validation: `PASS`
- replay run 1/run 2 SHA-256: `0b13abedc4f71f5be160b18830de69537438351ba13ec4cf2671616bf9db6abc`
- byte-identical replay: `true`
- zero event-key mismatches: `true`
- reordered non-semantic metadata/input order preserves event IDs: `true`
- no random value/current timestamp in outputs: `true`
- no hidden dependency on fixture file ordering: `true`

Machine-readable outputs:

- `research/results/checkpoint_fi_detector_fixture_validation/checkpoint_fi_fixture_test_summary.json`
- `research/results/checkpoint_fi_detector_fixture_validation/checkpoint_fi_deterministic_replay_summary.json`

## Terminal Statuses

Implementation includes all FH terminal statuses: `EVENT_EMITTED`, `NO_BREAK`, `RETEST_NOT_FOUND_WITHIN_12_BARS`, `CONFIRMATION_NOT_FOUND_WITHIN_12_BARS`, `DATA_INCOMPLETE_GAP`, `INSUFFICIENT_LEFT_HISTORY`, `INSUFFICIENT_RIGHT_HISTORY`, `ATR_UNAVAILABLE` และ `DUPLICATE_SUPPRESSED`.

## Future Checkpoint FJ (not created)

FJ may only, with separate explicit approval, execute the FI-validated detector against the approved historical dataset; generate the frozen event population; and report coverage, exclusions and counts. FJ must not calculate TP/SL outcomes, tune rules, change FF/FH/FI, use MT5/Strategy Tester, modify EA/MQL5/presets, create order logic, or perform demo/live testing.

## Post-FI Fail-Closed Correction

During FJ, a deterministic regression demonstrated that an active swing could survive an unverified gap and later be reused. The implementation now clears active swing state at an unverified `gap_before`. This is a defect correction required by FH/FJ fail-closed policy, not a rule or parameter change. All 12 fixture cases still pass; the terminal-output golden hash is now `0b13abedc4f71f5be160b18830de69537438351ba13ec4cf2671616bf9db6abc`.
## Status

- execution status: `PASS`
- strategy performance: `NOT_EVALUATED`
- order logic: `NOT_APPROVED`
- candidate: `NOT_READY_FOR_ORDER_LOGIC`
- profitability: `NOT_CLAIMED`

FI provides implementation correctness against fixtures only. It makes no claim about historical frequency, profitability, trading edge or executable trading.