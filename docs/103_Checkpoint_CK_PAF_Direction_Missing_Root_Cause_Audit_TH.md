# Checkpoint CK: PAF Direction Missing Root-Cause Audit

Checkpoint CK ตรวจ root cause ของ `DIRECTION_MISSING` จากไฟล์ offline เท่านั้น

รอบนี้:

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

## สิ่งที่เพิ่ม

เพิ่มเครื่องมือ:

- `tools/paf_direction_missing_audit.py`

เครื่องมือนี้อ่าน:

- `research/results/checkpoint_ce_paf_first_touch_relabel/paf_shadow_outcomes_first_touch_relabel.csv`

แล้วสร้าง:

- `research/results/checkpoint_ck_paf_direction_missing_audit/direction_missing_summary.md`
- `research/results/checkpoint_ck_paf_direction_missing_audit/direction_missing_summary.json`
- `research/results/checkpoint_ck_paf_direction_missing_audit/direction_missing_rows.csv`
- `research/results/checkpoint_ck_paf_direction_missing_audit/direction_missing_root_cause_counts.csv`
- `research/results/checkpoint_ck_paf_direction_missing_audit/direction_missing_by_classification.csv`
- `research/results/checkpoint_ck_paf_direction_missing_audit/direction_missing_by_session.csv`
- `research/results/checkpoint_ck_paf_direction_missing_audit/direction_missing_guardrail_summary.md`

## Offline Audit Result

- Status: `PASS_OFFLINE_DIRECTION_MISSING_AUDIT`
- Classification: `DIRECTION_COMPLETENESS_FAIL`
- Rows read: `33`
- Direction-missing rows: `14` (`42.42%`)

## Root Cause

| Root cause | Rows | Share |
|---|---:|---:|
| `FIBO_PULLBACK_EMA_DIRECTION_CONTEXT_MISSING` | 10 | 71.43% |
| `ZONE_REJECTION_CANDLE_DIRECTION_CONTEXT_MISSING` | 4 | 28.57% |

## Direction Reason

| Direction reason | Rows |
|---|---:|
| `fibo_pullback_without_clear_ema_direction_context` | 10 |
| `zone_rejection_without_directional_candle_context` | 4 |

## By Classification

| Classification | Direction-missing rows |
|---|---:|
| `POSSIBLE_FIBO_PULLBACK` | 10 |
| `POSSIBLE_ZONE_REJECTION` | 4 |

## By Session

| Session | Direction-missing rows |
|---|---:|
| `LONDON` | 5 |
| `NEW_YORK` | 5 |
| `OTHER` | 3 |
| `OVERLAP` | 1 |

## Interpretation

`DIRECTION_MISSING` ไม่ได้เกิดจาก CSV field ว่างเฉย ๆ

แถวที่ขาด direction มี:

- `direction = DIRECTION_UNKNOWN`
- `direction_reason` ชัดเจน
- source file เป็น `ea_mirror.log`

ความหมาย:

- parser เห็น diagnostic event แล้ว
- แต่ diagnostic context ยังไม่พอให้แปลเป็น buy/sell direction
- ปัญหาหลักคือ Fibo Pullback ยังไม่มี EMA/candidate direction context ชัด
- ปัญหารองคือ Zone Rejection ยังไม่มี candle rejection direction context ชัด

## Why This Does Not Approve Order Logic

แม้จะรู้ root cause แล้ว แต่ยังไม่ควรเพิ่ม order logic เพราะ:

- direction missing ยังสูงกว่า gate มาก
- ยังไม่มี field ที่ยืนยัน candidate direction แบบตรวจสอบย้อนกลับได้
- ถ้าเดา direction จาก classification อาจสร้าง false signal
- ยังไม่มี proof ว่าการเติม direction จะทำให้ first-touch distribution ดีขึ้น

## Recommended Next Checkpoint

Checkpoint CL ควรเป็น diagnostics-only field specification / approval package:

- ระบุ field ที่ต้องการเพิ่มในอนาคตเพื่อให้ direction ชัดขึ้น
- แยก Fibo Pullback fields และ Zone Rejection fields
- ห้ามเพิ่ม market/pending order
- ห้ามเปลี่ยน entry/exit behavior
- ห้าม optimize
- ห้าม claim profitability
- ถ้าต้องแก้ EA/source ต้องทำใน checkpoint ถัดไปหลัง review แยก

Field ที่ควรพิจารณา:

สำหรับ Fibo Pullback:

- `paf_candidate_direction`
- `paf_direction_source`
- `paf_ema_fast`
- `paf_ema_slow`
- `paf_ema_slope`
- `paf_pullback_side`
- `paf_trend_context`

สำหรับ Zone Rejection:

- `paf_zone_side`
- `paf_rejection_side`
- `paf_candle_body_direction`
- `paf_wick_side`
- `paf_candidate_direction`
- `paf_direction_source`

ทั้งหมดนี้ต้องเป็น diagnostics-only ก่อน ห้ามใช้เป็น order logic ทันที

## Decision

`DIRECTION_COMPLETENESS_FAIL`

`DATA_COMPLETENESS_WORK_REQUIRED`

`ORDER_LOGIC_NOT_APPROVED`

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

