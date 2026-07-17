# Checkpoint FP - New Evidence Boundary and Holdout Eligibility Contract (TH)

วันที่: 2026-07-17

## Purpose

FO ได้ `INSUFFICIENT_EVIDENCE`; FP จึง freeze boundary สำหรับหลักฐานใหม่ของ candidate เดิมเท่านั้น. FP เป็น provenance/source-boundary definition: ไม่รัน detector, ไม่สร้าง events/outcomes, ไม่เปิด TP/SL distribution และไม่เปลี่ยน Candidate V2

## Provenance Audit

ตรวจ Git history, tracked documents/artifacts/task memory และ temporary worktrees ตั้งแต่ Candidate V2 เริ่มใน FF.

- raw GOLD# H1 2020–2022 มีอยู่จริง แต่ raw-bar existence ไม่ใช่ contamination
- history ของ Candidate V2 มีเฉพาะ FF–FO chain; ไม่มี history reference ถึง 2020 source file
- tracked Candidate V2 x 2020/2021/2022 paths: `0`; tracked TP_FIRST/SL_FIRST x 2020/2021/2022 paths: `0`
- temporary candidate-era worktrees ที่ตรวจ: `11`; contamination path hits: `0`
- ไม่พบ repository evidence ว่า Candidate V2 events/outcomes ช่วง 2020–2022 เคยถูก generated, inspected, summarized หรือใช้ปรับ rule/FO decision

ผลนี้ไม่พิสูจน์ว่าไม่มีมนุษย์เคยเห็น price bar รายตัว; คำถาม contamination ที่เกี่ยวข้องคือ Candidate V2 design/decision เคยได้รับอิทธิพลจาก Candidate V2 results ช่วงนี้หรือไม่

## Source Availability

Selected boundary: `2020-01-01T00:00:00` ถึง `2022-12-31T23:59:59`, GOLD# H1

| File | Rows | First bar | Last bar | SHA-256 |
|---|---:|---|---|---|
| 2020 | 5912 | 2020-01-02 09:00 | 2020-12-31 18:00 | `7864a86a...efccc` |
| 2021 | 5902 | 2021-01-04 01:00 | 2021-12-31 18:00 | `3aa00fbe...fd2a5` |
| 2022 | 5917 | 2022-01-03 01:00 | 2022-12-30 23:00 | `dc619371...2213a` |

Total `17,731` rows. แต่ละไฟล์เรียงเวลาและไม่มี duplicate timestamp; cross-file duplicates `0`. CSV schema มี DATE/TIME/OHLC และ metadata. Raw broker CSV ไม่ถูก commit

## Decision

`FP_PASS_2020_2022_HISTORICAL_HOLDOUT_ELIGIBLE`

2020–2022 ผ่านเฉพาะ clean-holdout provenance boundary. ยังไม่ใช่ data-quality approval สำหรับการรัน detector/outcome

- broker-history completeness: `NOT_PROVEN`
- FP ไม่รับ closure ของ 2020–2022 ใด ๆ
- ห้าม assume 2023–2025 gap inventory ใช้ได้กับ period นี้
- future source validation ต้องสร้าง contract-compatible closure/gap inventory แยก; unverified gaps fail closed; ไม่มี interpolation/reconstruction/silent bridge

## Rules Frozen Unchanged

FF–FN rules ทั้งหมดคงเดิม: 2-left/2-right, close break, exact retest, 12 valid bars, confirmation/entry/ATR/1.5-1.0 ATR/H6-H48/H48-H24/FN metrics and Wilson/sample rules. H้ามเปลี่ยนเพราะ FO inconclusive

ห้าม optional stopping หรือปรับ boundary ตามผล. ห้าม pool 2020–2022 กับ 2023–2025 จนกว่าจะมี contract แยกที่อนุมัติก่อนเปิด 2020–2022 outcomes

## Future Scope

หากมี approval แยก checkpoint ถัดไปทำได้เพียง validate/freeze 2020–2022 bars และ fail-closed gap inventory; จากนั้นจึงใช้ FI/FK/FN ที่ไม่เปลี่ยนแปลง, integrity audit และรายงาน holdout แยก. ไม่มี follow-up อัตโนมัติ

- strategy performance: `NOT_EVALUATED`
- profitability: `NOT_CLAIMED`
- order logic: `NOT_APPROVED`
- candidate: `NOT_READY_FOR_ORDER_LOGIC`
- FO disposition: `INSUFFICIENT_EVIDENCE`