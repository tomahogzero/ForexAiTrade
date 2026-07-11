# Checkpoint EK: Shadow Input Readiness Audit

วันที่: 2026-07-11

ตรวจ committed artifacts เท่านั้นสำหรับ EJ shadow rules

## Findings

- EH eligible rows: `1600`
- EH/EF schema ไม่มี `entry_reference_price` และ ATR ต่อ event
- ไม่มี committed GOLD# H1 future OHLC ที่ join ครบ 48 bars สำหรับ DZ eligible events ทั้ง 1,600 แถว
- lookahead/first-touch artifacts เดิมเป็นชุดก่อนหน้าและ self-test/limited samples ห้ามนำมาแทน DZ population

## Decision

`SHADOW_BACKTEST_BLOCKED_REQUIRED_INPUTS_NOT_COMMITTED`

- entry coverage: `FAIL_MISSING`
- ATR coverage: `FAIL_MISSING`
- future OHLC coverage: `FAIL_MISSING`
- shadow backtest: `NOT_RUN`
- Strategy Tester trade backtest: `NOT_APPROVED`
- order logic: `FAIL_NOT_APPROVED`
- PAF: `NOT_READY_FOR_ORDER_LOGIC`

ห้าม infer entry/ATR จาก aggregate, ห้าม reuse bars ที่ไม่ตรง event และห้ามลด population หลังเห็นผล

ขั้นถัดไป: EL docs-only data-production contract/approval package สำหรับ extraction entry+ATR จาก DZ logs เดิม และ export/join GOLD# H1 bars ภายใต้ approval แยก

Progress: infrastructure/pipeline/diagnostic interpretation `98%`, diagnostic candidate `100%`, shadow backtest readiness `20%`, order logic/demo-live `0%`.
