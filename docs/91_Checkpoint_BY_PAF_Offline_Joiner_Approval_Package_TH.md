# Checkpoint BY: PAF Offline Joiner Approval Package

Checkpoint BY เป็น approval package สำหรับการรัน offline PAF lookahead joiner ในอนาคต หลังจาก Checkpoint BX ทำ gap policy dry-run แล้วได้ผล `PASS`

รอบนี้เป็น documentation / approval-package only:

- ไม่รัน MT5
- ไม่รัน Strategy Tester
- ไม่แก้ EA/source code
- ไม่แก้ preset
- ไม่แก้ production validator
- ไม่รัน joiner
- ไม่ optimize
- ไม่เพิ่ม lot/risk
- ไม่สรุป profitability

## Background

Checkpoint BX result:

- Gap policy dry-run verdict: `PASS`
- Gap count: `9`
- Accepted gaps: `9`
- Blocking/review gaps: `0`
- Accepted daily broker-session gaps: `8`
- Accepted weekend market closure: `1`
- Dry-run joiner status: `allowed_by_gap_policy`

ข้อสำคัญ:

`allowed_by_gap_policy` ใน BX เป็นสถานะของ dry-run policy เท่านั้น ไม่ใช่ production validator approval และไม่ใช่ profitability proof

## Proposed Future Joiner Scope

รอบ future execution ต้องจำกัด scope ตามนี้:

- Symbol: `GOLD#`
- Timeframe: `H1`
- Mode: offline-only
- Input events: `research/results/paf_shadow_outcomes_all_cases.csv`
- Bars source: `GOLD#` H1 bars ที่ผ่าน evidence review และ gap policy dry-run
- Results root ที่เสนอ: `research/results/checkpoint_bz_offline_joiner_run/`
- No MT5
- No Strategy Tester
- No order execution
- No production validator change
- No optimization
- No profitability claim

## Required Preconditions Before Execution

ก่อนรัน joiner ใน checkpoint ถัดไป ต้องยืนยัน:

1. Checkpoint BX is merged.
2. Gap policy dry-run summary exists:

   `research/results/checkpoint_bx_gap_policy_dry_run/gap_policy_dry_run_summary.json`

3. Dry-run verdict is exactly:

   `PASS`

4. Blocking/review count is exactly:

   `0`

5. Unknown irregular gaps are not present in the evidence review.
6. `GOLD#` H1 bars are confirmed H1, not M1.
7. Shadow outcome CSV exists:

   `research/results/paf_shadow_outcomes_all_cases.csv`

8. Future execution output folder is clean or clearly timestamped.
9. No Strategy Tester/MT5 execution is included.

## Proposed Future Command Shape

Checkpoint BY does not execute this command. It records the intended command shape for a later explicit execution checkpoint.

If using an already-normalized bars CSV:

```powershell
python tools/paf_lookahead_joiner.py `
  --shadow-outcomes research/results/paf_shadow_outcomes_all_cases.csv `
  --bars-csv <NORMALIZED_GOLD_H1_BARS_CSV> `
  --results-root research/results/checkpoint_bz_offline_joiner_run `
  --horizons 6,12,24,48 `
  --tp-atr-multiple 1.5 `
  --sl-atr-multiple 1.0
```

ห้ามรัน command นี้ใน Checkpoint BY

## Stop Conditions

ต้องหยุดทันทีถ้า:

- gap policy dry-run verdict ไม่ใช่ `PASS`
- มี `BLOCKED_*` หรือ `REVIEW_REQUIRED_*`
- CSV ไม่ใช่ H1
- shadow outcome file หาย
- bars coverage ไม่ครอบคลุม event/horizon
- output folder ปนกับ run เก่าโดยไม่มี traceability
- มีการพยายามรัน MT5 หรือ Strategy Tester
- มีการพยายามแก้ production validator
- มีการตีความผลเป็นกำไรหรือความพร้อม live

## Required Future Outputs

ถ้า checkpoint ถัดไปได้รับ approval และรัน joiner จริง ต้องสร้าง:

- `paf_lookahead_joined.csv`
- `paf_lookahead_join_summary.json`
- `paf_lookahead_join_summary.md`
- `joiner_run_guardrail_summary.md`
- summary ว่าไม่มี MT5/Strategy Tester/order execution
- summary แยก data validity ออกจาก strategy performance

## Decision

- `OFFLINE_JOINER_APPROVAL_PACKAGE_CREATED`
- `JOINER_NOT_RUN`
- `FUTURE_JOINER_SCOPE_DEFINED`
- `BX_DRY_RUN_PASS_REQUIRED`
- `PRODUCTION_VALIDATOR_NOT_CHANGED`
- `MT5_NOT_RUN`
- `STRATEGY_TESTER_NOT_RUN`
- `EA_SOURCE_NOT_CHANGED`
- `PRESETS_NOT_CHANGED`
- `NO_OPTIMIZATION_APPROVED`
- `NO_PROFITABILITY_CLAIM`

## Next Safe Step

Checkpoint BZ ควรเป็น explicit offline joiner execution checkpoint เท่านั้น ถ้าได้รับ approval ชัดเจนจากผู้ใช้

Approval phrase ที่แนะนำ:

`Approved to execute Checkpoint BZ offline PAF joiner for GOLD# H1 using BX PASS gap policy and offline files only.`

หากไม่มี approval phrase นี้ ให้ยังไม่รัน joiner
