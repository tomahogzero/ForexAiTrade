# Checkpoint BS: PAF Gap Policy Dry-Run

Checkpoint BS เพิ่มเครื่องมือ dry-run สำหรับตรวจ gap policy ก่อนนำข้อมูล `GOLD#` H1 ไปใช้กับ offline joiner

รอบนี้ไม่ได้รัน MT5, ไม่ได้รัน Strategy Tester, ไม่ได้แก้ EA/source code, ไม่ได้แก้ preset, ไม่ได้แก้ validator เดิม, ไม่ได้รัน joiner, ไม่ได้ optimize และไม่ได้สรุปกำไร

## เป้าหมาย

หลังจาก Checkpoint BQ/BR พบว่า real `GOLD#` H1 CSV มี gap 6 จุด:

- weekend closure candidate 1 จุด
- daily broker-session/history gap 5 จุด

Checkpoint BS จึงเพิ่มเครื่องมือ dry-run เพื่อแยกว่า gap ไหน:

- accept ได้ตาม policy
- ยังต้อง review
- ต้อง block

เครื่องมือนี้ยังไม่ใช่การเปลี่ยน validator production และยังไม่อนุญาตให้ joiner ทำงานต่อ

## Files ที่เพิ่ม

- `tools/paf_gap_policy_dry_run.py`
- `research/policies/paf_gold_h1_gap_policy_draft.json`
- `research/results/checkpoint_bs_gap_policy_dry_run/gap_policy_dry_run.csv`
- `research/results/checkpoint_bs_gap_policy_dry_run/gap_policy_dry_run_summary.json`
- `research/results/checkpoint_bs_gap_policy_dry_run/gap_policy_dry_run_summary.md`

## Policy Draft

Policy draft สำหรับ `GOLD#` H1:

- weekend market closure: enabled เฉพาะ Friday -> Monday และ delta ไม่เกิน 72 ชั่วโมง
- daily broker-session gap: ยังไม่ enabled, เป็น `review_required`
- true missing data: ยังเป็น blocker

## Dry-Run Result

ผลการรัน dry-run:

- Verdict: `REVIEW_REQUIRED`
- Gap count: `6`
- Accepted count: `1`
- Blocking/review count: `5`
- Joiner status: `blocked_by_gap_policy`

Status counts:

| Policy status | Count |
|---|---:|
| `ACCEPTED_WEEKEND_MARKET_CLOSURE` | 1 |
| `REVIEW_REQUIRED_DAILY_BROKER_SESSION_GAP` | 5 |

## การตีความ

ผลนี้ดีในแง่ที่ระบบแยก weekend closure ออกจาก daily session gap ได้แล้ว แต่ยังไม่เพียงพอสำหรับการรัน joiner

daily session gaps ทั้ง 5 จุดยังต้อง review เพิ่ม เพราะถ้าอนุญาตผิด อาจทำให้ lookahead/shadow outcome ใช้ข้อมูลไม่ครบ และทำให้ผลวิจัยบิดเบือน

## Guardrails

- ไม่รัน MT5
- ไม่รัน Strategy Tester
- ไม่ส่ง market order
- ไม่ส่ง pending order
- ไม่ modify position
- ไม่แก้ EA/source code
- ไม่แก้ preset
- ไม่แก้ validator production
- ไม่รัน joiner
- ไม่ optimize
- ไม่เพิ่ม lot/risk
- ไม่สรุป profitability

## Decision

- `GAP_POLICY_DRY_RUN_TOOL_ADDED`
- `POLICY_DRAFT_ADDED`
- `DRY_RUN_EXECUTED_OFFLINE_ONLY`
- `VERDICT_REVIEW_REQUIRED`
- `WEEKEND_GAP_ACCEPTED_1`
- `DAILY_SESSION_GAPS_REVIEW_REQUIRED_5`
- `JOINER_STILL_BLOCKED`
- `VALIDATOR_PRODUCTION_NOT_CHANGED`
- `MT5_NOT_RUN`
- `STRATEGY_TESTER_NOT_RUN`
- `EA_SOURCE_NOT_CHANGED`
- `PRESETS_NOT_CHANGED`
- `NO_OPTIMIZATION_APPROVED`
- `NO_PROFITABILITY_CLAIM`

## Next Safe Step

Checkpoint BT ควรเป็น review/approval pack เพื่อพิจารณาว่า daily broker-session gaps ของ `GOLD#` H1 ควรถูกอนุญาตใน policy หรือไม่

ก่อนอนุญาตต้องมีหลักฐานว่า:

- gap 23:00 -> 01:00 หรือ 22:00 -> 00:00 เป็น session break ปกติของ broker
- rule ถูกจำกัดเฉพาะ `GOLD#` H1
- unknown gaps ยัง block เสมอ
- joiner จะรันเฉพาะเมื่อ dry-run verdict เป็น `PASS`
