# Checkpoint FR-Prep-A2b-1 — Negative Gap-Policy Contract Validation

วันที่: 2026-07-20

สถานะ: `FR_PREP_A2B1_NEGATIVE_GAP_CONTRACT_VALIDATION`

Decision: `FR_PREP_A2B1_PASS_NEGATIVE_GAP_CONTRACT_VALIDATION`

## ขอบเขต

A2b-1 เพิ่มเฉพาะ stable machine-readable failure codes และ synthetic negative fixtures สำหรับ manifest/artifact integrity, entry fields, timestamps/order, exact classification allowlist, FQ explicit booleans และ reset/prohibition/warmup semantics ไม่มี duplicate/count/canonical-inventory fixture, detector integration, FJ replay, holdout preflight, historical population, event/ATR-event, TP/SL หรือ outcome

## Frozen validation precedence

1. manifest path ต้องมีอยู่
2. manifest ต้อง decode เป็น JSON object
3. ตรวจ required manifest fields
4. ตรวจ `gap_policy_manifest.v1` และ frozen profile declarations
5. artifact path ต้อง resolve ก่อนตรวจ hash
6. artifact SHA-256 ต้องตรงก่อน parse entry
7. ตรวจ required non-classification entry fields
8. parse previous timestamp ก่อน next timestamp แล้วจึงตรวจ strict `previous < next`
9. ตรวจ classification presence ก่อน exact allowlist membership
10. generic semantics ตรวจ reset flags → event-crossing prohibition → post-gap warmup
11. FQ explicit accepted/fail-closed booleans ตรวจหลัง classification semantics ถูก resolve แล้ว

เมื่อ fixture มีหลายความผิดพลาด code จากลำดับแรกเท่านั้นเป็น canonical result. Registry ที่ `research/schemas/gap_policy_validation_codes.a2b1.json` ระบุ code, validation layer, meaning, precedence และ fixture proving the code ครบ 17 codes.

## Negative fixtures and replay

Synthetic negative fixtures `18/18 PASS`; unexpected pass `0`; wrong code `0`; unknown code `0`; mismatch `0`. Equal timestamp และ previous-later-than-next ใช้ code ร่วม `GAP_POLICY_TIMESTAMP_ORDER_INVALID`.

Run 1, run 2 และ golden SHA-256 เท่ากัน:

`e12d040363487ac48f972f86a976aacc72305940a08ce92c1d162544a89357a7`

Canonical failures มีเฉพาะ status, validation code, expected code และ `broker_history_completeness=NOT_PROVEN`; ไม่มี traceback, absolute path, runtime timestamp หรือ platform-dependent exception text.

## Frozen regressions

- A1a: `4/4 PASS`; SHA-256 `717da59654afbab1a983a5444d65739df5541b593d6d393fa3bc2a363f57261b`
- A1b-1: `9/9 PASS`; SHA-256 `97cf9cc363d58615fab7f1c50f7c8535498a62aaf39485810d3975863c37cbb8`
- A1b-2: `13/13 PASS`; SHA-256 `5bde1d04d27c67a089103c344ff17918a795d9dc14176fae6dffc58782b242a4`
- A2 positive: `8/8 PASS`; SHA-256 `7a6c6b95c1f1019be4f743906dfc633b26069f14a0df2e63236c121b33d7f6ff`
- existing A1 validation codes/precedence และ A2 positive golden ไม่เปลี่ยน

## Safety status

`broker_history_completeness=NOT_PROVEN`; strategy performance `NOT_EVALUATED`; profitability `NOT_CLAIMED`; order logic `NOT_APPROVED`; candidate `NOT_READY_FOR_ORDER_LOGIC`. Detector core, FI runner/fixtures, FJ runner และ FQ runner ต้อง byte-for-byte unchanged.

## Exact next step

FR-Prep-A2b-2 — Negative Gap-Policy Inventory Validation: duplicate gap IDs, duplicate source-record identities, duplicate timestamp pairs, expected entry-count mismatch, empty/invalid inventory shape, and normalized inventory identity/hash guards. No detector or historical execution.
