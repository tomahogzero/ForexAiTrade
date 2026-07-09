# Checkpoint DL: Artifact-Only Deep Review

วันที่: 2026-07-09

## สถานะ

Checkpoint DL เป็น artifact-only deep review ตามแผน Checkpoint DK

ไม่มีการรัน MT5 ไม่มีการรัน Strategy Tester ไม่มีการแก้ EA/MQL5 ไม่มีการแก้ preset ไม่มีการ optimize ไม่มีการเพิ่ม lot/risk ไม่มีการเพิ่ม order logic ไม่มี demo/live forward test และไม่มีการอ้าง profitability

PAF / Price Action Fibo ยังเป็น diagnostic-only และยังคงสถานะ:

`NOT_READY_FOR_ORDER_LOGIC`

## Input Artifacts

DL ใช้ committed artifacts เท่านั้น:

- `research/results/checkpoint_df_fibo_pullback_row_level_slice.csv`
- `research/results/checkpoint_df_fibo_pullback_row_level_slice_summary.json`
- `research/results/checkpoint_di_diagnostic_coverage_summary.json`
- `research/results/checkpoint_dj_di_artifact_review.json`
- `docs/128_Checkpoint_DJ_DI_Artifact_Review_TH.md`
- `docs/129_Checkpoint_DK_Diagnostic_Review_And_Coverage_Plan_TH.md`

ข้อจำกัดสำคัญ:

- DF มี row-level Fibo slice สำหรับ CV + CY + DB รวม `8` windows
- DI มี committed summary-level artifact สำหรับ `7` windows
- DI ยังไม่มี committed row-level Fibo slice แยก BUY/SELL/gap reason ต่อ window
- ดังนั้น DL ไม่ตีความ DI per-window direction bias เกินหลักฐานที่มี

## Combined Coverage

หลังรวม CV + CY + DB + DI:

| Metric | Value |
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

## Low-Window Weakness Review

DL ใช้เกณฑ์ weak window แบบ conservative: Fibo usable first-touch rows ต่ำกว่า `5`

| Window | Source | Fibo rows | Fibo usable rows | Gap rows | Note |
|---|---|---:|---:|---:|---|
| CY-W3 | DF row-level | 4 | 2 | 2 | weak, consecutive before DB-W1 |
| DB-W1 | DF row-level | 6 | 2 | 4 | weak, consecutive after CY-W3 |
| DI-W3 | DI summary-level | 9 | 4 | 5 | weak in later expansion |

Weak-window share:

- weak Fibo rows: `19 / 242 = 7.9%`
- weak Fibo usable rows: `8 / 184 = 4.3%`

Interpretation ที่ปลอดภัย:

- weak windows ไม่ได้ dominate จำนวน Fibo usable rows ทั้งหมด
- แต่ weak windows เกิดซ้ำมากพอให้ stability gate ยัง fail
- `CY-W3` และ `DB-W1` เป็น consecutive weak pair จึงยังเป็นปัญหา coverage stability
- `DI-W3` เป็น weak window ใหม่หลัง coverage expansion
- ยังห้ามสรุปว่า weak windows เป็น market filter หรือ no-trade filter

## DF Row-Level Detail สำหรับ Weak Pair

จาก committed DF row-level CSV:

| Window | SELL usable | BUY usable | DIRECTION_UNKNOWN | PRICE_BETWEEN_EMAS | TREND_ALIGNMENT_CONFLICT |
|---|---:|---:|---:|---:|---:|
| CY-W3 | 2 | 0 | 2 | 2 | 0 |
| DB-W1 | 0 | 2 | 4 | 4 | 0 |

Interpretation:

- consecutive weak pair ไม่ได้เป็น SELL-only หรือ BUY-only pattern
- weak pair มี usable direction คนละด้าน: CY-W3 เป็น SELL usable, DB-W1 เป็น BUY usable
- gap ของ weak pair มาจาก `PRICE_BETWEEN_EMAS` ทั้งหมด
- จึงควรจัดเป็น coverage/stability limitation มากกว่าการอนุมัติ direction bias

## DF Row-Level Window Distribution

จาก DF row-level CSV สำหรับ CV + CY + DB:

| Window | Fibo rows | Usable | SELL | BUY | UNKNOWN | PRICE_BETWEEN_EMAS | TREND_ALIGNMENT_CONFLICT |
|---|---:|---:|---:|---:|---:|---:|---:|
| CV | 25 | 15 | 9 | 6 | 10 | 0 | 9 |
| CY-W1 | 20 | 15 | 11 | 4 | 5 | 2 | 3 |
| CY-W2 | 20 | 20 | 20 | 0 | 0 | 0 | 0 |
| CY-W3 | 4 | 2 | 2 | 0 | 2 | 2 | 0 |
| DB-W1 | 6 | 2 | 0 | 2 | 4 | 4 | 0 |
| DB-W2 | 19 | 10 | 0 | 10 | 9 | 9 | 0 |
| DB-W3 | 13 | 9 | 0 | 9 | 4 | 4 | 0 |
| DB-W4 | 21 | 12 | 11 | 0 | 9 | 6 | 3 |

DF row-level observation:

- SELL rows: `53`
- BUY rows: `32`
- DIRECTION_UNKNOWN rows: `43`
- DF usable SELL/BUY ratio: `53 / 32`
- DF direction balance is uneven but not one-sided enough to approve any bias
- BUY clusters in DB-W1 to DB-W3, while SELL clusters in CY-W2 and DB-W4
- This is regime/window distribution evidence only, not a trading rule

## DI Summary-Level Distribution

DI adds:

- Fibo Pullback rows: `114`
- Fibo usable first-touch rows: `99`
- Fibo direction gap rows: `15`
- Fibo SELL rows: `88`
- Fibo BUY rows: `11`
- Fibo DIRECTION_UNKNOWN rows: `15`

DI per-window Fibo usable rows:

| Window | From | To | Fibo rows | Fibo usable rows | Gap rows |
|---|---|---|---:|---:|---:|
| DI-W1 | 2026-04-26 | 2026-05-03 | 22 | 21 | 1 |
| DI-W2 | 2026-05-03 | 2026-05-10 | 22 | 19 | 3 |
| DI-W3 | 2026-05-10 | 2026-05-17 | 9 | 4 | 5 |
| DI-W4 | 2026-05-17 | 2026-05-24 | 22 | 19 | 3 |
| DI-W5 | 2026-05-24 | 2026-05-31 | 12 | 11 | 1 |
| DI-W6 | 2026-05-31 | 2026-06-07 | 21 | 19 | 2 |
| DI-W7 | 2026-06-07 | 2026-06-14 | 6 | 6 | 0 |

DI interpretation:

- DI materially improved Fibo usable coverage
- DI also made the combined dataset more SELL-heavy
- DI-W3 is the only DI weak window under the `<5` usable criterion
- DI-W7 has only `6` Fibo rows but all are usable, so it is a watch item, not a weak-window fail by current criterion
- DI does not provide committed row-level direction distribution per window, so no per-window SELL/BUY interpretation is approved from DI

## SELL-Heavy Distribution Review

Combined usable Fibo direction:

- SELL: `141`
- BUY: `43`
- usable total: `184`
- SELL share of usable Fibo: `76.6%`
- BUY share of usable Fibo: `23.4%`

Source split:

| Source | SELL | BUY | SELL share of usable |
|---|---:|---:|---:|
| DF row-level CV + CY + DB | 53 | 32 | 62.4% |
| DI summary-level | 88 | 11 | 88.9% |
| Combined | 141 | 43 | 76.6% |

Interpretation:

- DI is the main driver of the stronger SELL skew
- SELL-heavy distribution is now a diagnostic fact
- SELL-heavy distribution is not approved as a directional bias
- BUY sample remains small enough that any rule-candidate discussion would be premature
- Need either DI row-level review or additional coverage before treating direction distribution as stable

## Gap Attribution Review

Combined Fibo direction gaps:

| Gap reason | Count | Share of Fibo gaps |
|---|---:|---:|
| PRICE_BETWEEN_EMAS | 40 | 69.0% |
| TREND_ALIGNMENT_CONFLICT | 18 | 31.0% |

Source split:

| Source | PRICE_BETWEEN_EMAS | TREND_ALIGNMENT_CONFLICT |
|---|---:|---:|
| DF row-level CV + CY + DB | 28 | 15 |
| DI summary-level | 12 | 3 |
| Combined | 40 | 18 |

Interpretation:

- `PRICE_BETWEEN_EMAS` remains the dominant gap reason
- DI increased the relative share of `PRICE_BETWEEN_EMAS` among gap rows
- `TREND_ALIGNMENT_CONFLICT` remains material but secondary
- gap rows must not be forced into BUY/SELL
- gap reasons are diagnostic blockers, not entry filters approved for trading

## Rule-Candidate Readiness

DL does not approve a rule candidate because:

- total usable direction rows are `249`, below the `300` gate
- low-window weakness still fails
- DI per-window row-level direction distribution is not committed
- BUY sample is still small
- SELL-heavy distribution has not been validated as stable
- gap attribution remains material
- no shadow outcome edge review is approved here

## Decision

Checkpoint DL completes the artifact-only deep review.

Allowed after DL:

- Continue documentation-only review
- Provide exact DM approval phrase if the user wants future diagnostic-only Strategy Tester coverage expansion

Still not allowed:

- rule candidate
- order logic
- market orders
- pending orders
- position modification
- optimization
- lot/risk increase
- demo/live forward test
- profitability claim

## Verdicts

- `DL_ARTIFACT_DEEP_REVIEW_COMPLETE`
- `NO_MT5_RUN`
- `NO_STRATEGY_TESTER_RUN`
- `NO_EA_OR_PRESET_CHANGE`
- `LOW_WINDOW_WEAKNESS_REVIEWED_STILL_FAIL`
- `SELL_HEAVY_DISTRIBUTION_REVIEWED_NOT_APPROVED`
- `BUY_SAMPLE_STILL_SMALL`
- `FIBO_GAPS_REVIEWED_STILL_MATERIAL`
- `TOTAL_USABLE_DIRECTION_GATE_FAIL`
- `RULE_CANDIDATE_GATE_FAIL`
- `ORDER_LOGIC_NOT_APPROVED`
- `NO_OPTIMIZATION_PERFORMED`
- `NO_PROFITABILITY_CLAIM`
- `PAF_NOT_READY_FOR_ORDER_LOGIC`

## Progress Estimate

- Research infrastructure readiness: `94%`
- PAF diagnostic pipeline readiness: `89%`
- PAF diagnostic interpretation readiness: `77%`
- Fibo Pullback interpretation readiness: `78%`
- PAF rule-candidate readiness: `55%`
- PAF order-logic readiness: `0%`
- Demo/live readiness: `0%`
