# Checkpoint FK: Frozen Shadow Outcome Contract

วันที่: 2026-07-17

## วัตถุประสงค์

FK freeze กติกา diagnostic shadow outcome สำหรับ FJ population ที่ freeze แล้วเท่านั้น และไม่ calculate outcome. ไม่มีการอ่าน/inspect future outcome distribution, ไม่มีการแก้ detector/population และไม่มี executable order.

## Frozen Population

- source checkpoint: `FJ`
- GOLD# H1 2023-2025: `1,079` events; LONG `588`; SHORT `491`
- FJ event population SHA-256: `db59643834e06acbfebb66026634f4f561fb9b07131fdca1513e3585cd51c74b`
- broker-history completeness: `NOT_PROVEN`; unverified gaps remain fail-closed

## Entry and Levels

entry คือ frozen `entry_reference_price` ที่ confirmation close และ entry timestamp คือ `confirmation_timestamp`; diagnostic only. Evaluation starts at the next valid H1 trading bar. Confirmation bar ห้ามใช้ resolve TP/SL.

| Direction | TP | SL |
|---|---|---|
| LONG | entry + (1.5 x ATR) | entry - (1.0 x ATR) |
| SHORT | entry - (1.5 x ATR) | entry + (1.0 x ATR) |

ATR ใช้ field `atr` จาก FJ event row เท่านั้น; ห้าม recalculate ATR และห้ามเปลี่ยน multiples.

## Horizons and First Touch

H6/H12/H24/H48 คือ 6/12/24/48 valid post-entry H1 trading bars ตามลำดับ, not wall-clock hours. LONG: TP `high >= TP`, SL `low <= SL`; SHORT: TP `low <= TP`, SL `high >= SL`.

ถ้า TP และ SL ถูกแตะใน H1 bar เดียวกัน ให้ `AMBIGUOUS_SAME_BAR`; ห้าม infer intrabar order ด้วย open/close หรือข้อมูลอื่น.

## Outcome, Gap and Horizon Rules

Outcome domain ที่ exclusive ต่อ event/horizon คือ `TP_FIRST`, `SL_FIRST`, `AMBIGUOUS_SAME_BAR`, `NO_RESOLUTION`, `DATA_INCOMPLETE_GAP`, `INSUFFICIENT_FUTURE_BARS`, `INVALID_EVENT_INPUT`.

- outcome ที่ resolve ก่อน unverified gap คง valid
- หากยังไม่ resolve และ gap ตัด remaining required sequence: `DATA_INCOMPLETE_GAP`, record exact gap start/end
- accepted daily/weekend closure ตาม policy เดิมไม่ consume bar count; ห้าม bridge/interpolate/reconstruct
- source end ก่อน horizon complete และยังไม่ resolve: `INSUFFICIENT_FUTURE_BARS`
- invalid/missing/non-finite/inconsistent frozen input: `INVALID_EVENT_INPUT`

Horizon independent แต่ monotonic: resolved TP/SL ไม่เปลี่ยนใน horizon ที่ยาวกว่า, ambiguous คง ambiguous, and gap cannot overwrite an outcome resolved before it. `NO_RESOLUTION` อาจ resolve ใน longer complete horizon เท่านั้น.

## Canonical Output and Integrity

Canonical output เป็น one row per event/horizon: expected `1,079 x 4 = 4,316` rows. Schema และ stable ID อยู่ใน `research/contracts/checkpoint_fk_shadow_outcome_contract.json`.

`outcome_row_id = sha256(event_id|horizon_bars|outcome_contract_version)`; no UUID or runtime timestamp. Future runner must validate event conservation `1079/1079`, four rows/event, unique event/horizon, frozen source hash, level formula, direction/horizon domains, explicit exclusion reasons, monotonic consistency และ byte-identical replay.

## Contract Artifacts

- machine contract: `research/contracts/checkpoint_fk_shadow_outcome_contract.json`
- classification/gap decision table: `research/contracts/checkpoint_fk_outcome_truth_table.md`

## Future Checkpoint FL (not created)

FL may only implement or execute this exact contract against frozen FJ population, create all 4,316 event/horizon rows, report counts and data-quality exclusions, and validate deterministic replay. FL must not interpret performance, select subgroups, optimize, or create order logic.

## Status

- strategy performance: `NOT_EVALUATED`
- order logic: `NOT_APPROVED`
- candidate: `NOT_READY_FOR_ORDER_LOGIC`
- profitability: `NOT_CLAIMED`

FK contains no TP/SL result, profitability calculation, or trading-edge claim.