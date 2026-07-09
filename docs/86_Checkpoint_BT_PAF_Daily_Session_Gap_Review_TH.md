# Checkpoint BT: PAF Gold H1 Daily Session Gap Review

Checkpoint BT เป็นการรีวิว daily broker-session gap ของ `GOLD#` H1 หลังจาก Checkpoint BS ทำ dry-run แล้วได้ผล `REVIEW_REQUIRED`

รอบนี้เป็น documentation / review-only:

- ไม่รัน MT5
- ไม่รัน Strategy Tester
- ไม่แก้ EA/source code
- ไม่แก้ preset
- ไม่แก้ production validator
- ไม่รัน joiner
- ไม่ optimize
- ไม่เพิ่ม lot/risk
- ไม่สรุป profitability

## บริบท

Checkpoint BS dry-run พบ:

- Gap ทั้งหมด: `6`
- Weekend closure accepted: `1`
- Daily broker-session gap ที่ยังต้อง review: `5`
- Joiner status: `blocked_by_gap_policy`

Daily gaps ที่ต้อง review:

| Previous time | Next time | Delta hours | Status |
|---|---|---:|---|
| 2026-03-02 23:00:00 | 2026-03-03 01:00:00 | 2.0 | `REVIEW_REQUIRED_DAILY_BROKER_SESSION_GAP` |
| 2026-03-03 23:00:00 | 2026-03-04 01:00:00 | 2.0 | `REVIEW_REQUIRED_DAILY_BROKER_SESSION_GAP` |
| 2026-03-04 23:00:00 | 2026-03-05 01:00:00 | 2.0 | `REVIEW_REQUIRED_DAILY_BROKER_SESSION_GAP` |
| 2026-03-05 23:00:00 | 2026-03-06 01:00:00 | 2.0 | `REVIEW_REQUIRED_DAILY_BROKER_SESSION_GAP` |
| 2026-03-09 22:00:00 | 2026-03-10 00:00:00 | 2.0 | `REVIEW_REQUIRED_DAILY_BROKER_SESSION_GAP` |

## Review Result

BT ยังไม่ approve daily broker-session gap rule

เหตุผล:

- ยังไม่มีหลักฐานจาก MT5 chart/export เพิ่มเติมว่า `GOLD#` H1 ไม่มี bar ในช่วง gap จริง
- ยังไม่มีหลักฐานจาก broker/session spec ว่าช่วง `22:00/23:00 -> 00:00/01:00` เป็น session break ปกติ
- ยังไม่ได้ตรวจหลายสัปดาห์หรือหลายเดือนว่ารูปแบบ gap นี้เกิดซ้ำอย่างสม่ำเสมอ
- ถ้า approve เร็วเกินไป อาจทำให้ lookahead/shadow outcome ใช้ข้อมูลไม่ครบและบิดเบือนผลวิจัย

## Approval Criteria สำหรับอนาคต

ก่อนอนุญาต daily broker-session gap rule ต้องมีอย่างน้อย:

1. Manual MT5 chart/export evidence

   - เปิด `GOLD#` H1 ใน MT5
   - ตรวจว่าช่วงเวลาที่หายไม่มี bar จริงใน chart
   - export หรือ screenshot แสดงช่วงก่อนและหลัง gap

2. Pattern consistency evidence

   - ตรวจมากกว่า 1 สัปดาห์
   - ถ้าเป็นไปได้ ตรวจ 1-3 เดือน
   - gap ควรเกิดในช่วงเวลาเดิมหรือใกล้เคียงกันอย่างสม่ำเสมอ

3. Symbol/timeframe scope

   - rule ต้องใช้เฉพาะ `GOLD#` H1
   - ห้ามนำ rule นี้ไปใช้กับ EURUSD, USDJPY#, หรือ symbol/timeframe อื่นโดยอัตโนมัติ

4. Unknown gap remains blocker

   - gap ที่ไม่ตรงเวลา session ที่อนุมัติ ต้อง block
   - gap ที่ยาวผิดปกติในวันทำการ ต้อง block
   - gap ที่เกิดช่วงมี signal/event ต้อง review เพิ่ม

5. Dry-run must pass before joiner

   - policy dry-run ต้องได้ verdict `PASS`
   - `joiner_status` ต้องเป็น `allowed_by_gap_policy`
   - ต้องไม่มี `REVIEW_REQUIRED_*` หรือ `BLOCKED_*`

## Decision

- `DAILY_SESSION_GAP_REVIEW_DONE`
- `DAILY_SESSION_GAP_NOT_APPROVED_YET`
- `ADDITIONAL_EVIDENCE_REQUIRED`
- `JOINER_STILL_BLOCKED`
- `VALIDATOR_PRODUCTION_NOT_CHANGED`
- `POLICY_DRAFT_NOT_PROMOTED`
- `MT5_NOT_RUN`
- `STRATEGY_TESTER_NOT_RUN`
- `EA_SOURCE_NOT_CHANGED`
- `PRESETS_NOT_CHANGED`
- `NO_OPTIMIZATION_APPROVED`
- `NO_PROFITABILITY_CLAIM`

## Next Safe Step

Checkpoint BU ควรเป็น evidence collection guide หรือ manual export checklist สำหรับ `GOLD#` H1 session gaps:

- ระบุวิธี export/จับภาพช่วง gap จาก MT5
- ระบุช่วงวันที่ที่ต้องตรวจ
- ไม่รัน Strategy Tester
- ไม่รัน joiner
- ไม่ approve daily gap จนกว่าหลักฐานจะครบ

หากผู้ใช้ต้องการเร็วขึ้น ให้ใช้แนวทาง “manual evidence first” ไม่ใช่การ bypass validator
