# Checkpoint DS-Prep: Post-DR Artifact Review Template

วันที่: 2026-07-09

## สถานะ

Checkpoint DS-Prep เป็น documentation-only post-run review template สำหรับใช้หลัง Future Checkpoint DR เท่านั้น หาก DR ได้รับ exact approval และถูกรันจริงภายหลัง

DS-Prep ไม่รัน MT5 ไม่รัน Strategy Tester ไม่อ่าน artifact ใหม่จาก DR เพราะ DR ยังไม่ได้ถูกรัน ไม่แก้ EA/MQL5 ไม่แก้ preset ไม่ optimize ไม่เพิ่ม lot/risk ไม่เพิ่ม order logic ไม่ทำ demo/live forward test และไม่อ้าง profitability

Future DR ยัง `BLOCKED` จนกว่าผู้ใช้จะให้ exact approval phrase ตาม Checkpoint DQ

PAF / Price Action Fibo ยังคงเป็น diagnostic-only และยังคงสถานะ:

`NOT_READY_FOR_ORDER_LOGIC`

## จุดประสงค์ของ DS-Prep

DQ เตรียม approval package สำหรับ Future DR แล้ว DS-Prep เตรียม post-run review template เพื่อให้หลังจาก DR ถูกรันจริงภายหลัง การ review ไม่หลุด guardrail และไม่รีบสรุปเป็น rule/order logic

DS-Prep ไม่ใช่ DS result

DS-Prep ไม่อนุมัติ:

- Future DR execution
- rule candidate
- order logic
- market orders
- pending orders
- position modification
- optimization
- demo/live forward test
- profitability claim

## Baseline ก่อน Future DR

ค่าปัจจุบันหลัง Checkpoint DN/DQ:

| Metric | Current |
|---|---:|
| Diagnostic windows | 18 |
| Diagnostic rows | 1589 |
| Possible setup rows | 451 |
| Total usable direction rows | 290 |
| Total usable direction gate | 300 |
| Shortfall | 10 |
| Fibo Pullback rows | 277 |
| Fibo usable first-touch rows | 210 |
| Fibo direction gap rows | 67 |
| Fibo SELL rows | 164 |
| Fibo BUY rows | 46 |
| Fibo DIRECTION_UNKNOWN rows | 67 |

Current gates:

- window count >= `12`: `PASS`
- Fibo usable first-touch rows >= `150`: `PASS`
- total usable direction rows >= `300`: `FAIL`
- low-window weakness: `FAIL_HISTORICAL_WEAKNESS_REMAINS`
- rule-candidate gate: `FAIL`
- order-logic gate: `FAIL`

## Required DS Inputs หลัง Future DR

ถ้า Future DR ถูกอนุมัติและถูกรันจริง DS ต้องใช้ artifacts ต่อไปนี้:

- DR research matrix used for execution
- DR runner log
- DR per-window MT5 reports
- DR parsed execution summary
- DR PAF diagnostics presence check
- DR forbidden action marker scan
- DR baseline fallback marker scan
- combined CV + CY + DB + DI + DM + DR summary
- optional row-level Fibo slice if available from committed artifacts

ถ้า input เหล่านี้ไม่ครบ DS ต้องจัด classification เป็น blocked/review-incomplete ไม่ใช่ pass

## DS Execution Safety Review

DS ต้องแยก execution status ออกจาก strategy performance:

| Check | PASS Requirement |
|---|---|
| all approved DR windows executed | all DR windows present |
| report artifacts | found for every DR window |
| parser status | parsed without fatal error |
| total trades | exactly `0` for every DR window |
| PAF diagnostics | found for every DR window |
| forbidden action markers | `0` |
| baseline fallback markers | `0` |
| symbol | approved broker-specific `GOLD#` |
| timeframe | H1 |
| process safety | runner only stops its own spawned PID |

ถ้า report ถูกต้องแต่ strategy performance แพ้หรือไม่น่าสนใจ ยังถือว่า execution review ได้ ห้ามใช้คำว่า profitable/live-ready

## DS Coverage Review

DS ต้องคำนวณ combined CV + CY + DB + DI + DM + DR:

| Gate | Requirement | Meaning |
|---|---:|---|
| total usable direction rows | >= 300 | minimum rule-candidate discussion gate |
| Fibo usable first-touch rows | remains >= 150 | Fibo-specific coverage remains adequate |
| weak windows | no repeated/consecutive low-window weakness | stability gate |
| total trades | 0 | diagnostic-only safety |

ถ้า total usable direction rows ยังต่ำกว่า `300`, DS ต้องตัดสินเป็น:

`TOTAL_USABLE_DIRECTION_GATE_FAIL`

ถ้า rows >= `300` แต่ weak-window weakness ยัง fail, DS ต้องตัดสินเป็น:

`LOW_WINDOW_WEAKNESS_GATE_FAIL`

## DS Direction Distribution Review

DS ต้อง review Fibo BUY/SELL distribution หลัง DR โดยไม่อนุมัติ bias อัตโนมัติ

ต้องรายงาน:

- Fibo SELL rows
- Fibo BUY rows
- Fibo DIRECTION_UNKNOWN rows
- SELL share of usable Fibo
- BUY share of usable Fibo
- whether DR reduced or increased SELL skew
- whether BUY sample remains too small

Forbidden interpretations:

- ห้ามสรุปว่า SELL ดีกว่า BUY
- ห้ามสรุปว่า BUY ดีกว่า SELL
- ห้ามแปลง direction distribution เป็น entry bias
- ห้ามเพิ่ม filter หรือ order rule จาก distribution อย่างเดียว

## DS Gap Attribution Review

DS ต้อง review Fibo direction gaps หลัง DR:

- `PRICE_BETWEEN_EMAS`
- `TREND_ALIGNMENT_CONFLICT`
- any new gap reason if present

ต้องแยก:

- gap count
- share of Fibo gaps
- whether gap share improved or worsened
- whether gap rows remain material

Forbidden interpretations:

- ห้าม force direction ให้ gap rows
- ห้ามใช้ gap reason เป็น trading filter โดยยังไม่มี rule-candidate approval
- ห้ามตีความ gap reduction เป็น profitability evidence

## DS Classification Set

DS ควรใช้ classification เหล่านี้:

| Classification | Meaning |
|---|---|
| `DS_REVIEW_COMPLETE` | review package complete |
| `DR_EXECUTION_STATUS_PASS` | execution artifacts valid and no-trade safety passed |
| `DR_EXECUTION_STATUS_FAIL` | execution artifacts invalid or safety failed |
| `DR_REVIEW_INCOMPLETE` | required artifact missing |
| `TOTAL_USABLE_DIRECTION_GATE_PASS` | combined usable direction >= 300 |
| `TOTAL_USABLE_DIRECTION_GATE_FAIL` | combined usable direction < 300 |
| `LOW_WINDOW_WEAKNESS_GATE_PASS` | no repeated/consecutive weak-window issue |
| `LOW_WINDOW_WEAKNESS_GATE_FAIL` | weak-window issue remains |
| `BUY_SELL_DISTRIBUTION_REVIEWED_NOT_APPROVED` | distribution reviewed but not a bias |
| `FIBO_GAPS_REVIEWED_STILL_MATERIAL` | gaps remain material |
| `RULE_CANDIDATE_REVIEW_ALLOWED_NEXT` | all pre-rule gates pass, next checkpoint may discuss rule candidate |
| `RULE_CANDIDATE_GATE_FAIL` | at least one pre-rule gate fails |
| `ORDER_LOGIC_NOT_APPROVED` | no order logic allowed |

## DS Decision Matrix

| Execution Safety | Coverage Gate | Weak-Window Gate | Distribution/Gaps | DS Decision |
|---|---|---|---|---|
| FAIL | any | any | any | `DR_EXECUTION_STATUS_FAIL`, stop |
| PASS | FAIL | any | any | `RULE_CANDIDATE_GATE_FAIL` |
| PASS | PASS | FAIL | any | `RULE_CANDIDATE_GATE_FAIL` |
| PASS | PASS | PASS | not reviewed | `RULE_CANDIDATE_GATE_FAIL` |
| PASS | PASS | PASS | reviewed, still diagnostic | `RULE_CANDIDATE_REVIEW_ALLOWED_NEXT` |

`RULE_CANDIDATE_REVIEW_ALLOWED_NEXT` ไม่ใช่ order logic approval

ถ้าถึงจุดนี้ได้ checkpoint ถัดไปควรเป็น rule-candidate review plan เท่านั้น ไม่ใช่ EA implementation

## Required DS Output

DS result ต้องสร้าง:

- Thai checkpoint document under `docs/`
- AI status refresh
- summary of execution status
- combined post-DR counts
- gate table
- verdict list
- no-profitability statement
- next safe step

DS result PR ต้องไม่ include:

- `.ex5`
- `.pyc`
- `__pycache__/`
- `.zip`
- `.git/`
- `.agents/`
- `mt5_artifacts/`
- machine-specific config

## Decision

Checkpoint DS-Prep อนุมัติ template เท่านั้น:

- Future DR execution remains blocked
- DS result remains impossible until DR artifacts exist
- Rule candidate remains blocked today
- Order logic remains blocked today
- Demo/live remains blocked
- Optimization remains blocked
- Profitability claim remains prohibited

## Verdicts

- `DS_PREP_REVIEW_TEMPLATE_COMPLETE`
- `DOCUMENTATION_ONLY`
- `NO_MT5_RUN`
- `NO_STRATEGY_TESTER_RUN`
- `NO_DR_ARTIFACTS_REVIEWED`
- `FUTURE_DR_EXECUTION_STILL_BLOCKED`
- `DS_RESULT_BLOCKED_UNTIL_DR_ARTIFACTS_EXIST`
- `NO_EA_OR_PRESET_CHANGE`
- `NO_OPTIMIZATION_APPROVED`
- `NO_ORDER_LOGIC_APPROVED`
- `NO_DEMO_LIVE_FORWARD_TEST`
- `NO_PROFITABILITY_CLAIM`
- `PAF_NOT_READY_FOR_ORDER_LOGIC`

## Progress Estimate

- Research infrastructure readiness: `96%`
- PAF diagnostic pipeline readiness: `91%`
- PAF diagnostic interpretation readiness: `83%`
- Fibo Pullback interpretation readiness: `84%`
- PAF rule-candidate readiness: `63%`
- PAF order-logic readiness: `0%`
- Demo/live readiness: `0%`
