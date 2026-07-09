# Checkpoint DM-Prep: Diagnostic Run Readiness

วันที่: 2026-07-09

## สถานะ

Checkpoint DM-Prep เป็น documentation-only readiness package สำหรับ Future Checkpoint DM

ไม่มีการรัน MT5 ไม่มีการรัน Strategy Tester ไม่มีการสร้างหรือแก้ research matrix สำหรับ execution จริง ไม่มีการแก้ EA/MQL5 ไม่มีการแก้ preset ไม่มีการ optimize ไม่มีการเพิ่ม lot/risk ไม่มีการเพิ่ม order logic ไม่มี demo/live forward test และไม่มีการอ้าง profitability

Future Checkpoint DM ยัง `BLOCKED` จนกว่าผู้ใช้จะให้ exact approval phrase จาก Checkpoint DK แบบตรงตัว

PAF / Price Action Fibo ยังเป็น diagnostic-only และยังคงสถานะ:

`NOT_READY_FOR_ORDER_LOGIC`

## เหตุผลของ DM-Prep

หลัง Checkpoint DL:

- Fibo usable first-touch gate ผ่านแล้ว
- window count gate ผ่านแล้ว
- total usable direction rows ยัง `249 / 300`
- low-window weakness ยัง fail
- SELL-heavy distribution ยังไม่ใช่ approved bias
- BUY sample ยังเล็ก
- gap attribution ยัง material

ดังนั้น DM-Prep มีหน้าที่ลดความเสี่ยงก่อน future diagnostic-only run โดยนิยาม checklist และ artifact contract ล่วงหน้าเท่านั้น

## Future DM Scope ที่ยัง Blocked

Future DM ถ้าได้รับอนุมัติภายหลัง ต้องเป็น diagnostic-only Strategy Tester run:

| Field | Required |
|---|---|
| Symbol | `GOLD#` broker-specific runtime symbol |
| Timeframe | `H1` |
| Runner/parser | official AK workflow only |
| Optimization | prohibited |
| Demo/live forward test | prohibited |
| EA/MQL5 changes | prohibited |
| Preset changes | prohibited |
| Order logic | prohibited |
| Lot/risk increase | prohibited |
| Expected total trades | exactly `0` |

Target windows from Checkpoint DK:

| Window | From | To |
|---|---|---|
| DM-W1 | 2026-06-14 | 2026-06-21 |
| DM-W2 | 2026-06-21 | 2026-06-28 |
| DM-W3 | 2026-06-28 | 2026-07-05 |

## Exact Approval Phrase

DM-Prep ไม่อนุมัติ execution เอง

Future DM ยังต้องรอ phrase นี้แบบตรงตัว:

`Approved to execute Checkpoint DM diagnostic-only GOLD# H1 PAF/Fibo usable-direction coverage expansion with Strategy Tester only, no optimization, no demo/live forward test, no EA or preset changes, no order logic, total trades must remain 0, using windows 2026-06-14 to 2026-06-21, 2026-06-21 to 2026-06-28, and 2026-06-28 to 2026-07-05 with the official AK runner/parser workflow.`

ข้อความทั่วไป เช่น "ต่อเลย", "รันได้", หรือ "เพิ่ม PR" ไม่ถือเป็น approval phrase สำหรับ DM

## Pre-Run Checklist ถ้า Future DM ได้รับอนุมัติ

ก่อนเริ่ม Future DM ต้องตรวจ:

1. branch/worktree ต้องสร้างจาก latest `origin/main`
2. working tree ต้องสะอาดหรือแยก isolated worktree
3. approval phrase ต้องตรงตัว
4. ไม่มี EA/MQL5 หรือ preset changes ใน scope
5. runner ต้องเป็น official AK workflow
6. terminal path และ data folder ต้องชัดเจน
7. target symbol ต้องเป็น `GOLD#` ตาม broker-specific scope
8. timeframe ต้องเป็น H1
9. windows ต้องตรงกับ DK/DM-Prep เท่านั้น
10. retry/timeout ต้องไม่เปลี่ยนเป็น optimization
11. total trades must remain `0`
12. artifact output root ต้องแยก run id ใหม่

ถ้าข้อใดไม่ผ่าน ต้องหยุดก่อนรัน

## Expected Research Matrix Contract

ถ้า Future DM ได้รับอนุมัติ matrix ควรมี 3 cases เท่านั้น:

- `dm_w1_20260614_20260621`
- `dm_w2_20260621_20260628`
- `dm_w3_20260628_20260705`

แต่ละ case ต้องล็อก:

- actual broker symbol: `GOLD#`
- timeframe: `PERIOD_H1`
- from/to dates ตามตาราง
- diagnostic-only PAF/Fibo scope
- no optimization
- no order execution intent

DM-Prep ไม่สร้าง matrix file ใน checkpoint นี้ เพื่อหลีกเลี่ยงการทำให้ execution ดูเหมือนได้รับอนุมัติแล้ว

## Required Artifact Contract

ถ้า Future DM ได้รับอนุมัติและรันจริง ต้องมี artifact summary ที่แยก execution status ออกจาก strategy performance:

| Artifact / Field | Required |
|---|---|
| RunId | required |
| per-window execution status | required |
| report artifact status | required |
| `total_trades` | required |
| PAF diagnostics found/missing | required |
| forbidden action marker count | required |
| baseline fallback marker count | required |
| spawned PID list | required |
| combined CV + CY + DB + DI + DM totals | required |
| gate decisions | required |
| Thai checkpoint document | required |
| AI status refresh | required |

Execution status rule:

- valid report + parser pass + no-trade safety pass = execution can be `PASS`
- this says nothing about profitability
- unattractive or losing performance must not be reported as execution failure if artifacts are valid

## Stop Conditions

Future DM must stop and report blocked/fail-safe if:

- approval phrase is absent or not exact
- target symbol differs from approved `GOLD#`
- timeframe differs from H1
- any window differs from approved DM windows
- any window has `total_trades > 0`
- MT5 report is missing
- parser cannot read report
- PAF diagnostics are missing
- forbidden action markers > `0`
- baseline fallback markers > `0`
- runner needs to kill a process it did not spawn
- EA/MQL5 changes become necessary
- preset changes become necessary
- optimization becomes necessary
- lot/risk change becomes necessary
- artifact paths are ambiguous

## Post-Run Review Gate

ถ้า Future DM รันจริงและผ่าน execution safety แล้ว ยังไม่อนุมัติ rule-candidate โดยอัตโนมัติ

ต้องมี Checkpoint DN artifact-only review ก่อน โดย DN ต้องตรวจ:

- total usable direction rows >= `300`
- weak-window status after DM
- Fibo BUY/SELL distribution after DM
- Fibo gap attribution after DM
- total trades remain `0`
- no forbidden markers
- no baseline fallback markers
- no profitability claim

## Decision

Checkpoint DM-Prep เป็น readiness package เท่านั้น:

- Future DM execution remains blocked
- No matrix file is created
- No terminal is spawned
- No Strategy Tester is run
- No source/preset changes are made
- No rule candidate is approved
- No order logic is approved

## Verdicts

- `DM_PREP_READINESS_PACKAGE_COMPLETE`
- `DOCUMENTATION_ONLY`
- `FUTURE_DM_EXECUTION_BLOCKED_UNTIL_EXACT_APPROVAL`
- `NO_MT5_RUN`
- `NO_STRATEGY_TESTER_RUN`
- `NO_RESEARCH_MATRIX_CREATED`
- `NO_EA_OR_PRESET_CHANGE`
- `NO_OPTIMIZATION_APPROVED`
- `NO_ORDER_LOGIC_APPROVED`
- `NO_DEMO_LIVE_FORWARD_TEST`
- `NO_PROFITABILITY_CLAIM`
- `PAF_NOT_READY_FOR_ORDER_LOGIC`

## Progress Estimate

- Research infrastructure readiness: `95%`
- PAF diagnostic pipeline readiness: `89%`
- PAF diagnostic interpretation readiness: `77%`
- Fibo Pullback interpretation readiness: `78%`
- PAF rule-candidate readiness: `55%`
- PAF order-logic readiness: `0%`
- Demo/live readiness: `0%`

