# Checkpoint CM: PAF Direction Context Diagnostics Implementation Approval

Checkpoint CM เป็น approval package สำหรับ checkpoint ถัดไปเท่านั้น

รอบนี้ยังไม่ implement:

- ไม่รัน MT5
- ไม่รัน Strategy Tester
- ไม่แก้ EA/source code
- ไม่แก้ presets
- ไม่เพิ่ม order logic
- ไม่เพิ่ม market order
- ไม่เพิ่ม pending order
- ไม่เพิ่ม position modification
- ไม่ optimize
- ไม่เพิ่ม lot/risk
- ไม่สรุป profitability
- ไม่อนุมัติ demo/live

## Context

Checkpoint CK พบว่า `DIRECTION_MISSING` มี `14` จาก `33` rows

Root cause:

- `FIBO_PULLBACK_EMA_DIRECTION_CONTEXT_MISSING`: `10` rows
- `ZONE_REJECTION_CANDLE_DIRECTION_CONTEXT_MISSING`: `4` rows

Checkpoint CL ได้กำหนด field specification สำหรับ direction context แล้ว แต่ยังไม่ได้อนุมัติ implementation

## Purpose of Future Checkpoint CN

Checkpoint CN ที่จะทำถัดไปได้ ต้องเป็น diagnostics-only implementation เท่านั้น

เป้าหมาย:

- เพิ่ม log/diagnostic fields เพื่อให้ parser เห็น direction context ชัดขึ้น
- ลด `DIRECTION_MISSING` ใน offline pipeline
- ยังไม่เปลี่ยน trading behavior
- ยังไม่เปิด order path ใหม่

## Approved Scope for Future CN

อนุญาตเฉพาะงานเหล่านี้ใน checkpoint ถัดไป:

1. เพิ่ม diagnostics-only field output ใน PAF logging path
2. เพิ่มหรือปรับ parser ให้รองรับ field จาก Checkpoint CL
3. เพิ่ม audit/report ที่แสดง before/after direction completeness
4. Compile EA ถ้า MQL5 source ถูกแก้
5. รันเฉพาะ offline parser/tooling ที่ไม่ใช้ MT5

## Explicitly Not Approved

ห้ามทำใน checkpoint ถัดไป:

- ห้ามเปิด market order
- ห้ามวาง pending order
- ห้าม modify position
- ห้ามเปลี่ยน entry/exit behavior
- ห้ามใช้ field ใหม่เป็น signal
- ห้าม optimize parameter
- ห้ามเพิ่ม lot/risk
- ห้ามรัน MT5 เว้นแต่มี approval checkpoint แยก
- ห้าม claim profitability
- ห้าม demo/live forward test

## Required Effective Fields

Future implementation should produce these common fields when possible:

- `paf_candidate_direction`
- `paf_direction_source`
- `paf_direction_confidence`
- `paf_direction_reason`
- `paf_direction_is_usable_for_first_touch`

For Fibo Pullback:

- `paf_trend_context`
- `paf_pullback_side`
- `paf_ema_fast_value`
- `paf_ema_slow_value`
- `paf_ema_fast_slope`
- `paf_ema_slow_slope`
- `paf_fibo_zone_level`

For Zone Rejection:

- `paf_zone_side`
- `paf_rejection_side`
- `paf_candle_body_direction`
- `paf_wick_side`
- `paf_rejection_strength`

For Break Retest:

- `paf_break_direction`
- `paf_retest_side`
- `paf_break_level`

## Required Validation Rules

Implementation must enforce:

1. If `paf_candidate_direction = DIRECTION_UNKNOWN`, then `paf_direction_reason` must be present
2. If `paf_direction_is_usable_for_first_touch = false`, row must not be counted as relabel-ready
3. Direction must not be inferred from `classification` alone
4. Conflicting context must be marked as `DIRECTION_CONFLICT`
5. Parser must preserve old behavior if new fields are absent
6. Parser must not silently fill missing direction

## Required Guardrail Checks in CN

Checkpoint CN must include proof/checks:

- grep/check summary confirms no new `Buy`, `Sell`, `OrderSend`, pending-order, or `PositionModify` path was added
- no presets changed unless explicitly approved
- no default live trading enablement
- no risk/lot increase
- compile log with `0 errors, 0 warnings` if MQL5 changed
- artifact audit excludes `.ex5`, `.pyc`, `__pycache__`, `.zip`, `.agents`

## Required Outputs in CN

If CN proceeds, it must create:

- Thai checkpoint doc under `docs/`
- updated AI task record under `docs/ai/tasks/`
- GPT request or self-review note
- before/after direction completeness summary
- parser compatibility report
- guardrail grep/check summary
- compile log if EA/source changed

## Stop Conditions

Stop and do not proceed if:

- implementation requires order logic changes
- implementation requires pending orders
- implementation requires position modification
- implementation needs MT5 execution without separate approval
- source/preset drift is detected and not documented
- compile fails and cannot be fixed without changing trading behavior
- new fields are ambiguous enough that parser would need to guess direction

## Decision

`DIAGNOSTICS_ONLY_IMPLEMENTATION_APPROVAL_PACKAGE_CREATED`

`IMPLEMENTATION_NOT_DONE_IN_THIS_CHECKPOINT`

`ORDER_LOGIC_NOT_APPROVED`

`MT5_NOT_APPROVED`

`NOT_READY_FOR_ORDER_LOGIC`

## Guardrail Confirmation

- `MT5_NOT_RUN`
- `STRATEGY_TESTER_NOT_RUN`
- `EA_SOURCE_NOT_CHANGED`
- `PRESETS_NOT_CHANGED`
- `ORDER_LOGIC_NOT_APPROVED`
- `OPTIMIZATION_NOT_PERFORMED`
- `LOT_RISK_NOT_INCREASED`
- `PROFITABILITY_NOT_CLAIMED`
- `DEMO_LIVE_NOT_APPROVED`

