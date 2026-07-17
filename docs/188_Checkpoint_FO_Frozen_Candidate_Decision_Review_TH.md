# Checkpoint FO - Frozen Candidate Decision Review (TH)

วันที่: 2026-07-17

## วัตถุประสงค์และขอบเขต

FO ใช้ FN post-outcome interpretation firewall กับ FL canonical rows ที่ FM audit ผ่านแล้วเท่านั้น. ไม่มีการ regenerate event/outcome, เปลี่ยน detector, threshold, denominator, metric, TP/SL หรือ sample rule

Frozen provenance: FJ `1079` events (LONG `588`, SHORT `491`), FK `1.5/1.0 ATR`, FL `4316` rows, FM `FM_PASS_INDEPENDENT_OUTCOME_AUDIT` / material mismatches `0`. broker-history completeness ยัง `NOT_PROVEN`; unverified gaps ยังคง fail-closed

## Full Population ก่อนเสมอ

| Horizon | Total | Eligible | Excluded | TP | SL | Ambiguous | No resolution | Gap | Unambiguous resolved | TP share | Wilson 95% CI |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| H6 | 1079 | 1074 | 5 | 319 | 471 | 21 | 263 | 5 | 790 | 0.4038 | [0.3701, 0.4384] |
| H12 | 1079 | 1071 | 8 | 402 | 573 | 22 | 74 | 8 | 975 | 0.4123 | [0.3818, 0.4435] |
| H24 | 1079 | 1071 | 8 | 435 | 611 | 22 | 3 | 8 | 1046 | 0.4159 | [0.3864, 0.4460] |
| H48 | 1079 | 1071 | 8 | 437 | 612 | 22 | 0 | 8 | 1049 | 0.4166 | [0.3871, 0.4467] |

`AMBIGUOUS_SAME_BAR` ไม่ถูกนับเป็น TP/SL และ `NO_RESOLUTION` ไม่เป็น win/loss. H6/H12 เป็น descriptive early-resolution เท่านั้น; ห้ามใช้ override H48

## H48 Primary และ H24 Consistency

H48 เป็น primary ตาม FN: sample full population ผ่าน (`1049 >= 500`) แต่ Wilson lower bound `0.3871` ไม่มากกว่า diagnostic reference `0.40`; interval คร่อม reference จึงไม่เข้า advance condition

H24 เป็น mandatory consistency: TP share `0.4159` มากกว่า `0.40`, denominator `1046`, และไม่มี H24/H48 material conflict ตาม definition ของ FN. H24 ไม่สามารถ override H48

ค่า `0.40` เป็น zero-cost mathematical diagnostic reference จาก frozen 1.5/1.0 ATR เท่านั้น ไม่ใช่ profitability threshold, expected return, edge claim หรือ authorization ให้สร้าง order logic

## Direction และ Year Consistency (H48)

| Population | Unambiguous resolved | TP share | Wilson 95% CI | Sample status |
|---|---:|---:|---|---|
| LONG | 575 | 0.4452 | [0.4051, 0.4861] | PASS |
| SHORT | 474 | 0.3819 | [0.3392, 0.4264] | PASS |
| 2023 | 339 | 0.4248 | [0.3733, 0.4780] | PASS |
| 2024 | 362 | 0.4171 | [0.3675, 0.4685] | PASS |
| 2025 | 348 | 0.4080 | [0.3577, 0.4604] | PASS |

direction intervals overlap and FN direction-material-contradiction is false. Year results do not satisfy FN year-material-contradiction. กลุ่มเหล่านี้เป็น consistency/limitation reporting เท่านั้น และไม่ override full population

## Direction x Year Limitations (H48)

| Cell | Unambiguous resolved | TP share | Status |
|---|---:|---:|---|
| LONG x 2023 | 170 | 0.4353 | PASS |
| LONG x 2024 | 210 | 0.4857 | PASS |
| LONG x 2025 | 195 | 0.4103 | PASS |
| SHORT x 2023 | 169 | 0.4142 | PASS |
| SHORT x 2024 | 152 | 0.3224 | PASS |
| SHORT x 2025 | 153 | 0.4052 | PASS |

ทุก cell ผ่าน minimum 75 แต่เป็น limitation table เท่านั้น: ไม่มี best subgroup, ไม่มีการ retain/filter subgroup เพื่อ candidate ปัจจุบัน

## FN Disposition Matrix

| Disposition | FN conditions met | Blocking conditions | Eligible |
|---|---|---|---|
| REJECT_CURRENT_CANDIDATE | No | H48 upper `0.4467 > 0.40`; H24/H48 ไม่ต่ำกว่า reference ทั้งคู่; ไม่มี material contradiction | No |
| INSUFFICIENT_EVIDENCE | Yes | None; H48 CI คร่อม `0.40` และ advance condition ไม่ครบ | Yes, selected |
| RESEARCH_MORE_WITH_NEW_HYPOTHESIS | No | ไม่มี specific frozen structural question ที่ไม่ใช่ post-hoc subgroup retention | No |
| ELIGIBLE_FOR_COST_AWARE_OFFLINE_DIAGNOSTIC_DESIGN | No | H48 lower `0.3871` ไม่มากกว่า `0.40` | No |

Evidence และ condition-level citations อยู่ใน `checkpoint_fo_disposition_condition_matrix.json`

## Final Disposition

`INSUFFICIENT_EVIDENCE`

หลักฐานสนับสนุน: FM integrity PASS, denominator ทุก full/direction/year group ผ่าน, H24/H48 ไม่ conflict, และไม่มี direction/year material contradiction

หลักฐานจำกัด: H48 Wilson 95% interval คร่อม diagnostic reference; broker completeness `NOT_PROVEN`; unverified gaps/exclusions; H1 OHLC แยก intrabar order ไม่ได้; ไม่มี spread, commission, slippage, swap, latency, position sizing หรือ unseen-data forward validation

ไม่มี monetary profit, expected return, annual/monthly return, profitability/win-rate claim หรือ trading-edge claim ใน FO

## อนาคต

ไม่มี follow-up อัตโนมัติ. ก่อน decision review อีกครั้งต้องมีหลักฐานใหม่ที่เป็น independent และ chronology-separated ภายใต้ frozen definitions เดิม พร้อม design ที่อนุมัติแยก; ห้าม rerun dataset เดิมหรือ repeat audit เดิม

- strategy performance: `NOT_EVALUATED`
- profitability: `NOT_CLAIMED`
- order logic: `NOT_APPROVED`
- candidate: `NOT_READY_FOR_ORDER_LOGIC`