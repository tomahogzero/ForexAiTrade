# Checkpoint H: Controlled Exit Variant Research

เอกสารนี้สรุป Checkpoint H ซึ่งเป็นการวิจัย exit variant แบบควบคุมล่วงหน้า ไม่ใช่ optimization และไม่ใช่การอนุมัติ candidate สำหรับ demo/live

## เป้าหมาย

Checkpoint G พบว่า MT5 close comment คำว่า `SL` มีความกำกวม เพราะ SL บางส่วนเป็นการปิดแบบ trailing profit ไม่ใช่ initial stop loss ที่ขาดทุนจริง ดังนั้น Checkpoint H จึงทดสอบ exit variant จำนวนเล็กและกำหนดไว้ล่วงหน้า เพื่อดูว่า trailing behavior ปัจจุบันช่วยหรือทำร้าย baseline อย่างไร

## สิ่งที่เปลี่ยนด้านความปลอดภัย

ค่า default ของ telemetry ถูกเปลี่ยนให้ปลอดภัยขึ้น:

- `InpEnableExitTelemetry=false`
- `InpLogPositionModifyEvents=false`

research preset ยังสามารถเปิด telemetry ได้เมื่ออยู่ใน Strategy Tester

มี input เพิ่ม:

- `InpExitTelemetryMinModifyStepPoints=0`

ถ้าค่าเป็น `0` จะ log MODIFY เหมือนเดิม ถ้ามากกว่า `0` จะ log MODIFY เฉพาะเมื่อ SL/TP เปลี่ยนเกินจำนวน points ที่กำหนดจาก modify event ล่าสุดของ position นั้น การตั้งค่านี้มีผลต่อ logging เท่านั้น ไม่เปลี่ยนการส่งคำสั่ง `PositionModify`

## Variants ที่ทดสอบ

ทดสอบเฉพาะ EURUSD H1 deposit 10000:

| Variant | ความหมาย |
|---|---|
| baseline | trailing เดิม `InpUseTrailingStop=true`, `InpTrailingAtrMultiplier=1.5` |
| no_trailing | ปิด trailing stop |
| trailing_tighter | trailing แคบขึ้น `InpTrailingAtrMultiplier=1.0` |
| trailing_looser | trailing หลวมขึ้น `InpTrailingAtrMultiplier=2.0` |

ทุก variant เป็น pre-registered research variant ไม่ใช่การค้นหาค่าที่ดีที่สุด

## Run ที่ใช้

RunId: `run_20260621_205032`

Phases:

- train: 2023-01-01 ถึง 2024-12-31
- validation: 2025-01-01 ถึง 2025-12-31
- out_of_sample: 2026-01-01 ถึง 2026-06-18

## ผลสรุป

| Variant | Train | Validation | OOS | Classification |
|---|---:|---:|---:|---|
| baseline | -40.96 | 61.38 | 41.03 | BASELINE_REFERENCE |
| no_trailing | -22.85 | -1.57 | 72.84 | INSUFFICIENT_TRADES |
| trailing_tighter | -45.63 | -49.31 | 9.06 | REJECT_FOR_NOW |
| trailing_looser | -47.75 | 12.51 | 97.33 | INSUFFICIENT_TRADES |

ข้อสังเกต:

- baseline ยังเป็น reference เพราะ validation และ OOS เป็นบวก แต่ train ยังติดลบและยังไม่ใช่ final candidate
- no_trailing มี OOS ดี แต่ validation ติดลบและ trade count ต่ำมาก จึงยังใช้แทน baseline ไม่ได้
- trailing_tighter เพิ่ม trade count แต่ validation ติดลบ จึง reject for now
- trailing_looser ดูน่าสนใจใน OOS แต่ validation มี trade count ต่ำ จึงยังเป็นหลักฐานไม่พอ

## วิธีอ่าน Baseline vs Variants

อย่าเลือก variant จาก OOS ที่ดูดีที่สุด เพราะ OOS ใช้เป็น diagnostic check ไม่ใช่สนาม optimize ถ้า variant ทำกำไรจาก trade จำนวนน้อยมาก มีโอกาสสูงที่ผลจะไม่ stable

สิ่งที่ควรดูพร้อมกัน:

- validation และ OOS ต้องเป็นบวกทั้งคู่
- trade count ต้องพอสมควรทั้ง validation และ OOS
- drawdown ต้องไม่แย่กว่า baseline อย่างมีนัยสำคัญ
- initial SL loss ต้องไม่เพิ่มขึ้นมาก
- train ต้องไม่แย่ลงแบบอันตรายเมื่อเทียบ baseline
- ผลต้องไม่มาจาก trade ใหญ่เพียง 1-2 ไม้

## Recommendation

ผลลัพธ์ Checkpoint H:

`KEEP_BASELINE_NO_CHANGE`

ความหมายคือยังไม่ควรเปลี่ยน exit behavior จาก baseline ตอนนี้ แต่ควรเก็บข้อมูล exit/session/regime เพิ่มก่อนทำวิจัยรอบถัดไป

## ทำไมยังไม่ใช่ Optimization

รอบนี้ทดสอบเพียง 4 variants ที่กำหนดไว้ล่วงหน้า ไม่ได้ sweep parameter, ไม่ได้เลือกค่าที่กำไรสูงสุด, และไม่ได้ใช้ OOS เพื่อปรับค่ากลยุทธ์ จึงเป็น controlled research ไม่ใช่ optimization

## ทำไมยังไม่อนุญาต Demo Forward

ยังไม่มี final candidate เพราะ:

- baseline train ยังติดลบ
- variants บางตัวมี trade count ต่ำ
- OOS เป็น diagnostic evidence เท่านั้น
- ยังต้องตรวจ session/regime/spread/slippage และความกระจุกตัวของ drawdown เพิ่ม

ดังนั้นยังไม่ควรเริ่ม demo forward test จาก Checkpoint H เพียงอย่างเดียว
