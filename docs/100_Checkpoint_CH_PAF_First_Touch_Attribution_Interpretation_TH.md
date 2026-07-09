# Checkpoint CH: PAF First-Touch Attribution Interpretation

Checkpoint CH เป็นเอกสารตีความผลจาก Checkpoint CG เท่านั้น

รอบนี้ไม่ทำสิ่งต่อไปนี้:

- ไม่รัน MT5
- ไม่รัน Strategy Tester
- ไม่แก้ EA/source code
- ไม่แก้ presets
- ไม่เพิ่ม order logic
- ไม่เพิ่ม market order
- ไม่เพิ่ม pending order
- ไม่ปรับ lot/risk
- ไม่ optimize
- ไม่สรุปว่าระบบทำกำไรได้

## Input ที่ใช้ตีความ

อ้างอิงผลจาก:

- `research/results/checkpoint_cg_first_touch_attribution/first_touch_attribution_summary.md`
- `research/results/checkpoint_cg_first_touch_attribution/first_touch_attribution_summary.json`
- `research/results/checkpoint_cg_first_touch_attribution/first_touch_attribution_by_dimension.csv`

ข้อมูลนี้มาจาก offline first-touch labels ของ Checkpoint CE ไม่ใช่ real trades และไม่ใช่ Strategy Tester backtest

## สถานะรวม

ผล CG:

- Status: `PASS_OFFLINE_FIRST_TOUCH_ATTRIBUTION`
- Rows read: `33`
- Relabel-ready rows: `17`
- Direction-missing rows: `14`
- Data-missing rows: `2`
- Classification: `NOT_READY_FOR_ORDER_LOGIC`

คำแปลเชิงวิจัย:

ระบบ offline pipeline เริ่มตอบคำถามได้แล้วว่า setup แต่ละกลุ่มไปแตะ TP หรือ SL ก่อนมากกว่ากัน แต่ปริมาณข้อมูลยังน้อยเกินกว่าจะใช้สร้างกฎเข้า order

## สิ่งที่เห็นชัดที่สุด

### 1. Fibo Pullback เป็นกลุ่มใหญ่สุด แต่ยังเอียงไปทาง SL_FIRST

`POSSIBLE_FIBO_PULLBACK` มี:

- Rows: `25`
- Relabel-ready rows: `15`
- Horizon 6: TP_FIRST `4`, SL_FIRST `9`
- Horizon 12/24/48: TP_FIRST `5`, SL_FIRST `10`

การตีความ:

- กลุ่มนี้เป็นกลุ่มหลักที่ต้องศึกษาต่อ
- แต่ผลตอนนี้เป็นสัญญาณเตือน ไม่ใช่สัญญาณเข้าเทรด
- ถ้าเปลี่ยนเป็น order logic ตอนนี้ มีความเสี่ยงสูงว่าจะสร้างกฎจาก setup ที่ยังแตะ SL ก่อนมากกว่า TP

### 2. Zone Rejection ยังสรุปไม่ได้

`POSSIBLE_ZONE_REJECTION` มี relabel-ready เพียง `2` rows

การตีความ:

- ถึงบาง horizon อาจดูดีกว่า Fibo Pullback แต่ sample เล็กเกินไป
- ห้ามเลือกเป็น strategy candidate จากข้อมูลชุดนี้
- ต้องการข้อมูลเพิ่มก่อนตีความ

### 3. Session ยังใช้เป็น filter ไม่ได้

จาก CG:

- `ASIA` และ `OVERLAP` มี SL_FIRST concentration ใน sample ปัจจุบัน
- `LONDON` และ `NEW_YORK` ดูไม่แย่เท่า แต่จำนวน relabel-ready ยังน้อย

การตีความ:

- ยังไม่ควรเพิ่ม session filter
- ยังไม่ควรสรุปว่า session ไหนดีหรือแย่จริง
- ใช้ได้เพียงเป็น diagnostic question สำหรับรอบถัดไป

คำถามที่ควรถามต่อ:

- ถ้าเก็บข้อมูลหลายเดือน ASIA/OVERLAP ยัง SL_FIRST dominant หรือไม่
- LONDON/NEW_YORK ดีขึ้นจริง หรือเป็นผลจาก sample เล็ก
- SL_FIRST เกิดจาก entry timing, zone width, stop distance, หรือ volatility ใน session นั้น

### 4. Spread และ Regime ยังแยกผลได้จำกัด

`NORMAL_SPREAD` และ `trend` ครอบคลุมข้อมูลส่วนใหญ่

การตีความ:

- ข้อมูลยังไม่หลากหลายพอจะแยกผลของ spread/regime
- ยังไม่ควรเปลี่ยน regime rule หรือ spread rule
- ต้องเก็บข้อมูลเพิ่มและต้องลด direction missing ก่อน

## Blockers ก่อนคิดเรื่อง order logic

### Blocker 1: Direction missing สูง

มี `DIRECTION_MISSING` จำนวน `14` จาก `33` rows

ผลกระทบ:

- first-touch label ใช้ประเมิน TP/SL ได้ไม่ครบ
- attribution บางกลุ่มอาจผิดน้ำหนัก
- ทำให้ sample ที่ใช้ตัดสินจริงเหลือเพียง `17` rows

สถานะ:

- ยังเป็น blocker หลัก
- ต้องแก้ผ่าน data/diagnostic completeness ก่อน order logic

### Blocker 2: Sample size เล็ก

Relabel-ready rows มีเพียง `17`

ผลกระทบ:

- สรุป session ไม่ได้
- สรุป setup class ไม่ได้
- สรุป spread/regime ไม่ได้
- เสี่ยง overfit สูงมากถ้าเริ่มปรับกฎ

สถานะ:

- ยังไม่ผ่านเกณฑ์สำหรับ strategy decision

### Blocker 3: SL_FIRST dominant ในกลุ่มหลัก

`POSSIBLE_FIBO_PULLBACK` ยัง SL_FIRST dominant ทุก horizon

ผลกระทบ:

- ยังไม่ควรสร้าง order จาก Fibo Pullback ตรง ๆ
- ต้องวิเคราะห์ว่า SL_FIRST มาจากอะไร ก่อนปรับ logic

คำถามที่ต้องตอบ:

- SL_FIRST เกิดเพราะ stop distance แคบไปหรือไม่
- TP distance ไกลเกินไปหรือไม่
- Entry เกิดเร็วเกินไปหรือช้าเกินไปหรือไม่
- zone classification กว้างหรือหยาบเกินไปหรือไม่
- direction extraction ขาดหายเพราะ log/CSV ไม่ครบหรือไม่

## Decision Matrix

| Topic | Current Finding | Decision |
|---|---|---|
| Fibo Pullback | กลุ่มใหญ่สุด แต่ SL_FIRST dominant | ศึกษาต่อเท่านั้น |
| Zone Rejection | sample เล็กมาก | สรุปไม่ได้ |
| Session | ASIA/OVERLAP ดูเสี่ยง แต่ sample เล็ก | ยังไม่ทำ filter |
| Spread | ส่วนใหญ่เป็น NORMAL_SPREAD | ยังแยกผลไม่ได้ |
| Regime | ส่วนใหญ่เป็น trend | ยังแยกผลไม่ได้ |
| Direction completeness | missing สูง | ต้องแก้ก่อน |
| Order logic | ยังไม่มีหลักฐานพอ | ไม่อนุมัติ |

## Recommendation

Checkpoint ถัดไปควรเป็นหนึ่งในสองแนวนี้:

1. Data completeness improvement plan
   - ลด `DIRECTION_MISSING`
   - เพิ่ม field ที่บอก direction / intended TP / intended SL ให้ชัด
   - ตรวจว่า offline CSV และ PAF diagnostics join กันครบหรือไม่

2. Multi-window offline sample expansion plan
   - ใช้ pipeline เดิมกับหลายช่วงเวลา
   - ยังไม่เพิ่ม order logic
   - เปรียบเทียบว่า Fibo Pullback ยัง SL_FIRST dominant ข้ามช่วงเวลาหรือไม่

ลำดับที่แนะนำ:

ให้ทำ data completeness ก่อน เพราะถ้าข้อมูล direction ยังหายเยอะ การขยาย sample อาจขยายข้อมูลที่ยังไม่สมบูรณ์ตามไปด้วย

## Final Classification

`NOT_READY_FOR_ORDER_LOGIC`

เหตุผล:

- relabel-ready sample มีเพียง `17`
- direction missing สูง
- Fibo Pullback ยัง SL_FIRST dominant
- session/spread/regime ยังแยกผลไม่ได้ชัด
- ยังไม่มีหลักฐานพอสำหรับ order, pending order, filter, หรือ parameter change

## Guardrail Confirmation

- `MT5_NOT_RUN`
- `STRATEGY_TESTER_NOT_RUN`
- `EA_SOURCE_NOT_CHANGED`
- `PRESETS_NOT_CHANGED`
- `ORDER_LOGIC_NOT_APPROVED`
- `OPTIMIZATION_NOT_APPROVED`
- `LOT_RISK_NOT_INCREASED`
- `PROFITABILITY_NOT_CLAIMED`
- `DEMO_LIVE_NOT_APPROVED`

