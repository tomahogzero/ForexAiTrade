# Checkpoint DK: Diagnostic Review and Coverage Plan

วันที่: 2026-07-09

## สถานะ

Checkpoint DK เป็น documentation-only plan หลัง Checkpoint DJ

ไม่มีการรัน MT5 ไม่มีการรัน Strategy Tester ไม่มีการแก้ EA/MQL5 ไม่มีการแก้ preset ไม่มีการ optimize ไม่มีการเพิ่ม lot/risk ไม่มีการเพิ่ม order logic ไม่มี demo/live forward test และไม่มีการอ้าง profitability

PAF / Price Action Fibo ยังเป็น diagnostic-only และยังคงสถานะ:

`NOT_READY_FOR_ORDER_LOGIC`

## Input จาก Checkpoint DJ

Checkpoint DK ใช้ผลที่ commit แล้วจาก Checkpoint DJ เท่านั้น:

- `docs/128_Checkpoint_DJ_DI_Artifact_Review_TH.md`
- `docs/ai/current-status.md`
- `research/results/checkpoint_dj_di_artifact_review.json`

Combined CV + CY + DB + DI หลัง DJ:

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

Gate ที่ผ่านแล้ว:

- diagnostic windows >= `12`: `PASS`
- Fibo usable first-touch rows >= `150`: `PASS`
- no-trade diagnostic safety from DI: `PASS`

Gate ที่ยังไม่ผ่าน:

- total usable direction rows >= `300`: `FAIL` เพราะมี `249`
- low-window weakness: `FAIL`
- rule-candidate gate: `FAIL`
- order-logic gate: `FAIL`

## ปัญหาหลักที่ DK ต้องวางแผน

หลัง DI/DJ ข้อมูล Fibo ดีขึ้นมาก แต่ยังมีช่องว่างสำคัญ 4 จุด:

1. total usable direction rows ยังขาดอย่างน้อย `51` rows เพื่อผ่าน gate `300`
2. low-window weakness ยังมีอยู่ โดยเฉพาะ `CY-W3`, `DB-W1`, และ `DI-W3`
3. Fibo SELL-heavy distribution ยังเป็น diagnostic imbalance เท่านั้น ไม่ใช่ bias ที่อนุมัติแล้ว
4. Fibo gap reasons ยังมีนัยสำคัญ โดยเฉพาะ `PRICE_BETWEEN_EMAS` และ `TREND_ALIGNMENT_CONFLICT`

## แผนที่ DK อนุมัติให้ทำต่อได้แบบไม่ต้องรัน MT5

DK แนะนำให้ทำ Checkpoint DL เป็น artifact-only deep review ก่อน:

- review low-window weakness จาก artifact เดิม
- แยก window ที่มี Fibo usable rows ต่ำกว่า `5`
- review SELL-heavy distribution ต่อ window
- review BUY sample ที่ยังน้อย
- review gap attribution แยก `PRICE_BETWEEN_EMAS` และ `TREND_ALIGNMENT_CONFLICT`
- ไม่สร้าง buy/sell rule
- ไม่สรุปว่า distribution ใดดีกว่า
- ไม่เพิ่ม filter
- ไม่แตะ EA/MQL5 หรือ preset
- ไม่รัน MT5 หรือ Strategy Tester

Checkpoint DL ควรตอบให้ได้ว่า weak windows เป็นปัญหา data coverage, market regime, diagnostic labeling, หรือแค่ sample noise โดยยังไม่แปลงเป็น order rule

## Future Diagnostic-Only Coverage Option

ถ้าหลัง DL ยังต้องเพิ่ม coverage เพื่อดัน total usable direction rows จาก `249` ให้เกิน `300`, DK กำหนด future Checkpoint DM เป็น diagnostic-only Strategy Tester run เท่านั้น

Future DM ต้องยังเป็น:

- Strategy Tester only
- `GOLD#` H1 broker-specific symbol
- no optimization
- no demo/live forward test
- no EA/MQL5 changes
- no preset changes
- no order logic
- no lot/risk increase
- total trades must remain `0`
- official AK runner/parser workflow only
- execution status must remain separate from strategy performance
- losing or unattractive reports, if valid and no-trade, are still execution-status reviewable

### Target Windows สำหรับ Future DM

DK เสนอ 3 fully closed weekly windows หลัง DI:

| Window | From | To | Purpose |
|---|---|---|---|
| DM-W1 | 2026-06-14 | 2026-06-21 | continue after DI-W7 |
| DM-W2 | 2026-06-21 | 2026-06-28 | increase coverage |
| DM-W3 | 2026-06-28 | 2026-07-05 | increase coverage before current date |

เป้าหมายเชิง diagnostic:

- เพิ่ม diagnostic windows จาก `15` เป็น `18`
- เพิ่ม total usable direction rows จาก `249` ไปให้เกิน `300` ถ้าข้อมูลจริงเพียงพอ
- เพิ่ม Fibo usable first-touch rows จาก `184` ไปให้มั่นคงกว่า `150`
- ตรวจว่า weak-window pattern ยังเกิดซ้ำหรือไม่

นี่ไม่ใช่ optimization และไม่ใช่ profitability test

## Exact Approval Phrase สำหรับ Future DM

Future DM ยัง blocked จนกว่าผู้ใช้จะให้ approval phrase นี้แบบตรงตัว:

`Approved to execute Checkpoint DM diagnostic-only GOLD# H1 PAF/Fibo usable-direction coverage expansion with Strategy Tester only, no optimization, no demo/live forward test, no EA or preset changes, no order logic, total trades must remain 0, using windows 2026-06-14 to 2026-06-21, 2026-06-21 to 2026-06-28, and 2026-06-28 to 2026-07-05 with the official AK runner/parser workflow.`

ถ้า phrase ไม่ตรง หรือขอเพิ่ม/ลด window ต้องทำ approval package ใหม่ก่อน

## Required Artifacts ถ้า Future DM ได้รับอนุมัติ

DM ต้องสร้างหรือยืนยัน artifacts ต่อไปนี้:

- research matrix สำหรับ DM เท่านั้น
- runner stdout/stderr หรือ batch log
- per-window MT5 report artifacts
- parsed per-window execution status
- parsed `total_trades`
- PAF diagnostics presence check
- forbidden action marker count
- baseline fallback marker count
- combined CV + CY + DB + DI + DM summary
- Thai checkpoint document under `docs/`
- AI status refresh

DM PR ต้องไม่ include:

- `.ex5`
- `.pyc`
- `__pycache__/`
- `.zip`
- `.git/`
- `.agents/`
- `mt5_artifacts/`
- machine-specific terminal config

## Stop Conditions สำหรับ Future DM

ถ้าเกิดข้อใดข้อหนึ่ง ต้องหยุดและรายงานเป็น blocked/fail-safe:

- window ใดมี `total_trades > 0`
- MT5 report missing
- parser อ่าน report ไม่ได้
- PAF diagnostics missing
- forbidden action marker count > `0`
- baseline fallback marker count > `0`
- symbol ไม่ใช่ runtime broker symbol ที่อนุมัติ
- runner ต้องหยุด process ที่ไม่ได้ spawn เอง
- ต้องแก้ EA/MQL5 หรือ preset เพื่อให้รันผ่าน
- ต้อง optimize parameter
- ต้องเพิ่ม lot/risk
- artifact path ไม่ชัดเจนหรือปนกับ run อื่น

ถ้า execution status PASS แต่ coverage ยังไม่ถึง gate ให้บันทึกเป็น valid diagnostic evidence ไม่ใช่ความล้มเหลวของ execution

## Review Gate หลัง Future DM

ถึงแม้ Future DM จะผ่าน no-trade execution safety, ยังห้ามเปิด rule-candidate discussion ทันที

ต้องมี Checkpoint DN artifact-only review ก่อน โดย DN ต้อง review:

- total usable direction rows >= `300`
- low-window weakness ว่ายัง fail หรือไม่
- Fibo BUY/SELL distribution โดยไม่อนุมัติ bias อัตโนมัติ
- Fibo gap attribution
- execution-status safety
- no profitability claim

เฉพาะถ้า DN ผ่านทุก gate จึงค่อยวางแผน rule-candidate review ใน checkpoint ถัดไปได้ แต่ยังไม่ใช่ order logic

## Decision

Checkpoint DK อนุมัติแผนเท่านั้น:

- Checkpoint DL artifact-only deep review: allowed as docs/artifact review, no MT5
- Future Checkpoint DM diagnostic-only run: blocked until exact approval phrase
- Rule candidate: not approved
- Order logic: not approved
- Demo/live: not approved
- Optimization: not approved
- Profitability claim: prohibited

## Verdicts

- `DK_PLAN_COMPLETE`
- `DOCUMENTATION_ONLY`
- `NO_MT5_RUN`
- `NO_STRATEGY_TESTER_RUN`
- `NO_EA_OR_PRESET_CHANGE`
- `NO_OPTIMIZATION_APPROVED`
- `NO_ORDER_LOGIC_APPROVED`
- `FUTURE_DM_BLOCKED_UNTIL_EXACT_APPROVAL`
- `TOTAL_USABLE_DIRECTION_GATE_STILL_FAIL`
- `LOW_WINDOW_WEAKNESS_GATE_STILL_FAIL`
- `RULE_CANDIDATE_GATE_FAIL`
- `ORDER_LOGIC_NOT_APPROVED`
- `NO_PROFITABILITY_CLAIM`
- `PAF_NOT_READY_FOR_ORDER_LOGIC`

## Progress Estimate

- Research infrastructure readiness: `94%`
- PAF diagnostic pipeline readiness: `89%`
- PAF diagnostic interpretation readiness: `74%`
- Fibo Pullback interpretation readiness: `74%`
- PAF rule-candidate readiness: `52%`
- PAF order-logic readiness: `0%`
- Demo/live readiness: `0%`

