# Checkpoint FQ - 2020-2022 Historical Holdout Data Quality (TH)

FQ ตรวจเฉพาะ GOLD# H1 source และ fail-closed gap boundary; ไม่รัน Candidate V2 detector/event/outcome

## Decision

`FQ_CONDITIONAL_PASS_HIGH_EXCLUSION_RISK`

FP hashes ทั้ง 3 source ตรง, schema/OHLC integrity ผ่าน, timeline deterministic `17,731` bars, duplicate/conflicting timestamp `0`, และ gap inventory ครบ `774` gaps. broker-history completeness ยัง `NOT_PROVEN`

## Gap Boundary

- accepted routine weekend closures: `149`
- accepted routine daily closures: `0` (ไม่มี exact match ตาม narrow rule)
- unverified gaps: `625`
- longest gap: `79` hours
- unsupported gaps ทั้งหมดเป็น `UNVERIFIED_GAP` และ fail closed

ทุก unverified gap ต้อง reset active swing, break/retest/confirmation state; ห้าม reuse swing ก่อน gap, cross gap, interpolate/reconstruct/silent bridge. ATR/warmup หลัง gap ต้องมี valid post-gap bars พอ. Accepted closures ไม่ consume valid trading-bar count

2023-2025 inventory ไม่ได้ถูก reuse เป็น evidence. FP ไม่รับ closure 2020-2022 ใด ๆ ก่อน FQ; FQ รับเฉพาะ exact Friday-to-Monday weekend rule. Data availability นี้มี high exclusion risk และไม่ใช่ Candidate V2 outcome evidence

## Future FR

FR ต้องเป็น sealed holdout execution ที่อนุมัติแยก: verify hashes/contracts, unchanged FI/FK/FN only, independent audit, report 2020-2022 separately, no pooling/rule changes/order logic/profit claim. FQ ไม่สร้าง FR

Status: FO `INSUFFICIENT_EVIDENCE`; strategy performance `NOT_EVALUATED`; profitability `NOT_CLAIMED`; order logic `NOT_APPROVED`; candidate `NOT_READY_FOR_ORDER_LOGIC`