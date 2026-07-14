# Checkpoint FC: Research Interpretation Contract

วันที่: 2026-07-15

## Purpose

Freeze ขอบเขตการตีความ offline diagnostic ของ valid fail-closed shadow population เดิมเท่านั้น FC เป็นเอกสาร-only และไม่รัน subgroup analysis

## Frozen Population and Outputs

- ใช้เฉพาะ included event/horizon จาก EU/EZ; excluded `DATA_INCOMPLETE_GAP` ไม่มี outcome
- ต้องแสดง full-population result คู่กับทุก subgroup เสมอ
- outputs อนุญาต: population/included/excluded counts, exclusion rate, TP_FIRST/SL_FIRST/AMBIGUOUS_SAME_BAR/NO_RESOLUTION counts, descriptive rates พร้อม denominator, confidence limitations, minimum-sample warnings, consistency/inconsistency และกลุ่มที่ต้องการ evidence เพิ่ม

## Preregistered Dimensions

1. direction: `BUY`, `SELL`
2. setup subtype / diagnostic reason: ใช้เฉพาะ field ที่มีอยู่ใน EU outcome artifact; ห้ามสร้าง subtype ใหม่หลังเห็น outcome
3. period: calendar year `2023`, `2024`, `2025`
4. market session: ใช้ only pre-existing session field; ถ้าไม่มี field ให้ report `NOT_AVAILABLE`, ห้าม infer จาก outcome
5. ATR regime: fixed boundaries `LOW: atr < P33`, `MID: P33 <= atr <= P67`, `HIGH: atr > P67` โดย P33/P67 คำนวณครั้งเดียวจาก full eligible population ก่อน subgroup outcomes และห้ามปรับ
6. horizon: `6`, `12`, `24`, `48` bars
7. coverage/exclusion/sample size/result stability

## Minimum Sample and Anti-Overfitting Rules

- full-population: report ทุก horizon
- subgroup/horizon ที่ included `< 30`: `INSUFFICIENT_SAMPLE`; report counts only, no descriptive outcome rates
- subgroup/horizon ที่ included `>= 30`: descriptive rates allowed with denominators and limitation text only
- freeze categories before computation; no post-outcome categories, no discarded unfavorable groups, and report every preregistered group
- no selection of best subgroup; all findings are diagnostic hypotheses only

## Prohibited

ห้ามสรุป profitability/expected return/trading edge, TP/SL/entry tuning, parameter search/optimization, order logic, EA/MQL5/preset/lot-risk changes, Strategy Tester, demo/live, market/pending orders

## Next Exact Checkpoint

Checkpoint FD: artifact-only preregistered subgroup interpretation report. FD ต้องอ่าน merged EU/EZ artifacts เท่านั้น, run every frozen group, preserve event-key conservation/deterministic replay, and keep `NOT_EVALUATED/NOT_APPROVED/NOT_READY_FOR_ORDER_LOGIC`. FD ห้ามเปลี่ยน dimensions หรือ boundaries.

## Status

- strategy performance: `NOT_EVALUATED`
- order logic: `NOT_APPROVED`
- PAF: `NOT_READY_FOR_ORDER_LOGIC`
- profitability: `NOT_CLAIMED`

Decision: `FC_RESEARCH_INTERPRETATION_CONTRACT_FROZEN`.
