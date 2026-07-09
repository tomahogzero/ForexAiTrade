# Checkpoint DO: Future DM Approval Handoff

วันที่: 2026-07-09

## สถานะ

Checkpoint DO เป็น documentation-only approval handoff สำหรับ Future Checkpoint DM

ไม่มีการรัน MT5 ไม่มีการรัน Strategy Tester ไม่มีการสร้าง research matrix สำหรับ execution จริง ไม่มีการแก้ EA/MQL5 ไม่มีการแก้ preset ไม่มีการ optimize ไม่มีการเพิ่ม lot/risk ไม่มีการเพิ่ม order logic ไม่มี demo/live forward test และไม่มีการอ้าง profitability

Future DM ยัง `BLOCKED` จนกว่าผู้ใช้จะส่ง exact approval phrase แบบตรงตัว

PAF / Price Action Fibo ยังเป็น diagnostic-only และยังคงสถานะ:

`NOT_READY_FOR_ORDER_LOGIC`

## ทำไมต้องมี DO

หลัง Checkpoint DN-Prep ระบบพร้อมด้านเอกสารสำหรับ:

- pre-run readiness
- artifact contract
- stop conditions
- post-run review template

แต่ Future DM ยังไม่ได้รับอนุมัติให้รันจริง

DO จึงเป็น handoff package ที่บอกชัดเจนว่า ถ้าต้องการรัน DM ต้องส่ง phrase ไหน และถ้าไม่ส่ง phrase นั้น Codex ต้องหยุดที่ documentation readiness

## Current Baseline ก่อน DM

ค่าล่าสุดก่อน Future DM:

| Metric | Current |
|---|---:|
| Diagnostic windows | 15 |
| Diagnostic rows | 1299 |
| Possible setup rows | 384 |
| Total usable direction rows | 249 |
| Fibo Pullback rows | 242 |
| Fibo usable first-touch rows | 184 |
| Fibo direction gap rows | 58 |
| Fibo SELL rows | 141 |
| Fibo BUY rows | 43 |
| Fibo DIRECTION_UNKNOWN rows | 58 |

Gate status:

- window count >= `12`: `PASS`
- Fibo usable first-touch rows >= `150`: `PASS`
- total usable direction rows >= `300`: `FAIL`
- low-window weakness: `FAIL`
- rule-candidate gate: `FAIL`
- order-logic gate: `FAIL`

## Future DM ที่รออนุมัติ

Future DM ถ้าอนุมัติภายหลัง จะเป็น diagnostic-only Strategy Tester run:

| Window | From | To |
|---|---|---|
| DM-W1 | 2026-06-14 | 2026-06-21 |
| DM-W2 | 2026-06-21 | 2026-06-28 |
| DM-W3 | 2026-06-28 | 2026-07-05 |

Requirements:

- symbol: `GOLD#`
- timeframe: H1
- Strategy Tester only
- official AK runner/parser workflow only
- no optimization
- no demo/live forward test
- no EA/MQL5 changes
- no preset changes
- no order logic
- no lot/risk increase
- total trades must remain `0`

## Exact Approval Phrase

ถ้าผู้ใช้ต้องการให้ Codex รัน Future DM ให้ส่งข้อความนี้แบบตรงตัว:

`Approved to execute Checkpoint DM diagnostic-only GOLD# H1 PAF/Fibo usable-direction coverage expansion with Strategy Tester only, no optimization, no demo/live forward test, no EA or preset changes, no order logic, total trades must remain 0, using windows 2026-06-14 to 2026-06-21, 2026-06-21 to 2026-06-28, and 2026-06-28 to 2026-07-05 with the official AK runner/parser workflow.`

## ข้อความที่ไม่ถือเป็น Approval

ข้อความต่อไปนี้ไม่อนุมัติ Future DM:

- `ต่อเลย`
- `รันต่อ`
- `ทำต่อ`
- `เพิ่ม PR`
- `ทำ 5 PR`
- `auto merge ได้ก็ทำ`
- `go`
- `continue`
- ข้อความใด ๆ ที่ไม่ได้ระบุ scope, windows, no-trade, no optimization, no EA/preset changes, no order logic, และ official AK runner/parser workflow ครบถ้วน

ถ้ามีข้อความเหล่านี้ Codex ทำได้เฉพาะ docs-only work หรือหยุดถาม/รายงาน blocker

## What Happens After Exact Approval

ถ้าได้รับ exact approval phrase ภายหลัง ขั้นตอน Future DM ต้องเป็น:

1. fetch latest `origin/main`
2. create isolated clean worktree
3. create DM execution branch
4. create DM research matrix for 3 approved windows only
5. run official AK runner/parser workflow via Strategy Tester only
6. verify every window has `total_trades=0`
7. stop immediately if any stop condition triggers
8. create Thai checkpoint document under `docs/`
9. create committed summary under `research/results/`
10. open PR for DM execution artifacts

DM execution artifact PR must not be auto-merged by default because working rules exclude MT5 execution artifact PRs from default auto-merge

## Stop Conditions Reminder

Future DM must stop if:

- approval phrase is not exact
- symbol is not `GOLD#`
- timeframe is not H1
- any window differs from approved windows
- any report is missing
- parser fails
- PAF diagnostics are missing
- any window has `total_trades > 0`
- forbidden action marker count > `0`
- baseline fallback marker count > `0`
- runner would need to stop a process it did not spawn
- EA/MQL5 or preset changes become necessary
- optimization becomes necessary
- lot/risk change becomes necessary

## Post-DM Rule

Even if Future DM executes successfully:

- no rule candidate is automatically approved
- no order logic is approved
- no demo/live forward test is approved
- no profitability claim is allowed
- Checkpoint DN artifact-only review must happen before any rule-candidate discussion

## Decision

Checkpoint DO completes the approval handoff only:

- Future DM execution remains blocked
- Exact approval phrase is required
- No matrix is created
- No terminal is spawned
- No Strategy Tester is run
- Rule candidate remains blocked
- Order logic remains blocked

## Verdicts

- `DO_APPROVAL_HANDOFF_COMPLETE`
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
- PAF diagnostic pipeline readiness: `90%`
- PAF diagnostic interpretation readiness: `78%`
- Fibo Pullback interpretation readiness: `79%`
- PAF rule-candidate readiness: `56%`
- PAF order-logic readiness: `0%`
- Demo/live readiness: `0%`

