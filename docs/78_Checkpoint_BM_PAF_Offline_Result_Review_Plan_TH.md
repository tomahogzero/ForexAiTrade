# Checkpoint BM: PAF Offline Result Review Plan

วันที่จัดทำ: 2026-07-08

## สถานะ

Checkpoint BM เป็นเอกสารกำหนดวิธีรีวิวผลลัพธ์หลังจากรัน offline PAF pipeline กับ CSV จริงในอนาคต

Checkpoint นี้ไม่รัน MT5, ไม่รัน Strategy Tester, ไม่รัน offline pipeline, ไม่แก้ EA/source code, ไม่แก้ presets, ไม่ optimize, ไม่เพิ่ม lot/risk และไม่ claim profitability

## เหตุผล

หลัง Checkpoint BJ/BK/BL-Prep เรามีเครื่องมือและกติกาเตรียมไฟล์ CSV แล้ว แต่ยังต้องมีกรอบอ่านผลลัพธ์ล่วงหน้า เพื่อกันไม่ให้ผล shadow outcome ถูกตีความเกินจริง

ผลจาก offline pipeline เป็นเพียงการวิเคราะห์ว่า setup ที่ถูก log แบบ diagnostic-only จะเจอ TP/SL shadow outcome อย่างไรภายในข้อมูล OHLC ที่ให้มา ไม่ใช่การพิสูจน์ว่าระบบทำกำไรได้จริง และไม่ใช่สัญญาณซื้อขาย

## Input ที่คาดว่าจะรีวิวในอนาคต

เมื่อ Checkpoint BL ถูกรันในอนาคต ควรมี artifact เช่น:

- `paf_offline_pipeline_runner_summary.json`
- `paf_offline_pipeline_runner_summary.md`
- `paf_bars_schema_normalization_summary.json` ถ้ามี raw CSV
- `paf_lookahead_bars_validation_summary.json`
- `paf_lookahead_bars_validation_summary.md`
- `paf_shadow_outcomes_enriched.csv`
- `paf_lookahead_join_summary.json`
- `paf_lookahead_join_summary.md`

## Review Questions

รีวิวต้องตอบคำถามเหล่านี้ก่อนคิดเรื่อง strategy:

1. CSV เป็น `GOLD#` H1 จริงหรือไม่
2. coverage พอถึง horizon 48 แท่ง H1 หรือไม่
3. diagnostic event timestamps match กับ bars ได้มากพอหรือไม่
4. มี missing events หรือ large gaps หรือไม่
5. possible setups ที่มี direction จริงมีจำนวนพอหรือไม่
6. outcome labels กระจายอย่างไร
7. ambiguous same-bar มีมากจนอ่านผลไม่ได้หรือไม่
8. ผลกระจุกใน session หรือช่วง spread สูงหรือไม่
9. ผลแตกต่างระหว่าง BUY_CONTEXT และ SELL_CONTEXT หรือไม่
10. ข้อมูลเป็น broker-comparable กับ XM MT5 หรือเป็น diagnostic-only เท่านั้น

## Quality Gates

ห้ามใช้ผล offline เป็นหลักฐานวิจัยเชิงกลยุทธ์ถ้า:

- validator ไม่ผ่าน
- coverage ไม่พอ
- event matching ต่ำ
- missing events สูง
- direction missing สูงจนเหลือ sample น้อย
- ambiguous same-bar สูงจน outcome ไม่ชัด
- bars source ไม่ใช่ XM MT5 และไม่ได้จัดเป็น non-broker-comparable
- CSV มีการแก้ OHLC ด้วยมือ
- ผลเกิดจาก sample น้อยมาก

## Suggested Classification

รีวิวในอนาคตควร classify เป็นหนึ่งในนี้:

- `OFFLINE_PIPELINE_PASS_REVIEWABLE`
- `VALIDATOR_FAIL_NEEDS_FIX`
- `COVERAGE_INSUFFICIENT`
- `EVENT_MATCH_INSUFFICIENT`
- `DIRECTION_CONTEXT_INSUFFICIENT`
- `AMBIGUITY_TOO_HIGH`
- `NON_BROKER_COMPARABLE_DIAGNOSTIC_ONLY`
- `SAMPLE_TOO_SMALL`
- `RESULT_INTERESTING_NEEDS_MORE_WINDOWS`
- `REJECT_ORDER_PATH_FOR_NOW`

ห้ามใช้ classification เหล่านี้:

- `PROFITABLE`
- `LIVE_READY`
- `DEMO_READY`
- `ORDER_APPROVED`
- `OPTIMIZATION_READY`

## Metrics To Review

อย่างน้อยควรดู:

- total diagnostic rows
- possible setup rows
- joined rows
- missing event count
- horizon coverage pass/fail
- outcome counts by horizon
- `TP_FIRST`
- `SL_FIRST`
- `NO_TOUCH`
- `AMBIGUOUS_SAME_BAR`
- `DIRECTION_MISSING`
- `DATA_MISSING`
- buy vs sell context
- result by session ถ้ามี
- result by spread bucket ถ้ามี
- result by classification label
- result by regime/unsafe reason ถ้ามี

## Interpretation Rules

- `TP_FIRST` ไม่เท่ากับเงินจริง เพราะไม่มี spread, slippage, execution, stops level, freeze level, margin, lot sizing หรือ order lifecycle
- `SL_FIRST` ไม่ได้แปลว่ากลยุทธ์แย่ทันที ต้องดู sample, regime, spread, และ ambiguity
- `NO_TOUCH` อาจหมายถึง TP/SL ไกลเกินไป หรือ horizon สั้นเกินไป
- `AMBIGUOUS_SAME_BAR` ต้องถือว่า conservative และห้ามใช้เป็น win
- ผลจาก 1 window ห้ามใช้สรุป strategy
- ผลจาก Gold ห้ามนำไปใช้กับ EURUSD หรือ symbol อื่นโดยตรง
- ผลนี้ยังไม่อนุญาต market order หรือ pending order

## Output Review Template

เมื่อมี Checkpoint BL result ในอนาคต ควรสรุปแบบนี้:

```text
RunId:
CSV path:
CSV source:
Symbol:
Timeframe:
Coverage:
Validator status:
Joined rows:
Missing events:
Outcome distribution:
Direction distribution:
Ambiguous same-bar count:
Main blocker:
Classification:
Order path status: BLOCKED
Profitability claim: NONE
Next step:
```

## Stop Conditions For Review

ต้องหยุดและไม่สรุปคุณภาพ strategy ถ้า:

- artifact ไม่ครบ
- runner summary ไม่มี
- validator summary ไม่มี
- enriched CSV ไม่มี
- outcome counts ไม่สอดคล้องกับ joined rows
- มีการรวมผลจาก synthetic fixture กับ real data โดยไม่แยก
- มีการใช้คำว่า profit, ready, live, approve order โดยไม่มี checkpoint เฉพาะ

## Guardrails

- ไม่รัน MT5
- ไม่รัน Strategy Tester
- ไม่รัน offline pipeline
- ไม่แก้ EA/source code
- ไม่แก้ presets
- ไม่ optimize
- ไม่เพิ่ม lot/risk
- ไม่ claim profitability
- ไม่อนุมัติ demo/live
- ไม่อนุมัติ order path

## Decision

- `OFFLINE_RESULT_REVIEW_PLAN_DEFINED`
- `REAL_CSV_PATH_STILL_REQUIRED`
- `OFFLINE_PIPELINE_NOT_RUN`
- `MT5_NOT_RUN`
- `STRATEGY_TESTER_NOT_RUN`
- `ORDER_PATH_STILL_BLOCKED`
- `NO_OPTIMIZATION_APPROVED`
- `NO_PROFITABILITY_CLAIM`

## Progress Estimate

- Research infrastructure readiness: `79%`
- PAF diagnostic readiness: `70%`
- PAF shadow-outcome readiness: `68%`
- Order implementation readiness: `0%`
- Demo/live readiness: `0%`

ขั้นตอนถัดไปที่มีผลจริงคือผู้ใช้ต้องส่ง absolute path ของ CSV จริง แล้วอนุมัติ Checkpoint BL เพื่อรัน offline pipeline
