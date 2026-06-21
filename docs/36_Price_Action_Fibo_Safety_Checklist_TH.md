# Price Action / Fibo Safety Checklist

เอกสารนี้เป็น checklist สำหรับ strategy implementation ในอนาคตเท่านั้น ยังไม่อนุญาตให้ demo/live

## Symbol Profile

- ต้องเลือก symbol profile อย่างชัดเจนก่อน research run
- EURUSD settings ห้าม reuse อัตโนมัติบน symbol อื่น
- Other forex pairs ต้องมี validation แยกตาม symbol
- Gold risk-budget review ต้องเสร็จก่อน Gold research run
- Broker minimum lot ต้องไม่ override risk budget

## Order Limits

- กำหนด maximum pending orders ต่อ symbol
- กำหนด maximum open orders ต่อ symbol
- กำหนด maximum total orders รวม pending + open
- ห้ามเปิด order เพิ่มไม่จำกัดเมื่อราคาไปผิดทาง
- ห้าม recovery lot multiplication

## Exposure Limits

- จำกัด total lot exposure ต่อ symbol
- จำกัด total risk money ต่อ setup
- จำกัด total risk money ต่อวัน/สัปดาห์ตาม RiskManager
- ห้ามเพิ่ม lot หลัง loss
- ห้าม force min lot ถ้า risk budget ไม่พอ

## Zone Safety

- กำหนด maximum zone depth
- zone height ต้องวัดจาก ATR/points
- zone ต้องมี expiry
- setup ต้อง invalidate เมื่อราคา close ทะลุ invalidation level
- ห้ามถือ zone แบบไม่มี stop loss

## Stop Loss Requirement

- market order ต้องมี SL
- pending order ต้องมี SL
- SL ต้องผ่าน stops level/freeze level
- SL distance ต้องใช้ RiskManager คำนวณ lot
- ห้าม no-stop-loss recovery

## Pending Order Management

- pending order ต้องมี expiration
- cancel pending order เมื่อ setup invalidate
- cancel pending order เมื่อ spread สูงเกิน limit
- cancel pending order เมื่อ regime unsafe
- cancel pending order เมื่อมี order/position เกิน limit
- log cancel reason ทุกครั้ง

## Spread / Execution Filters

- ใช้ max spread filter
- ตรวจ symbol metadata จริงจาก broker
- ตรวจ tick size, tick value, point, contract size
- ตรวจ margin ก่อนส่ง order
- ตรวจ stops level/freeze level

## Session / News / Volatility

- พิจารณา session filter เป็น diagnostic ก่อนใช้จริง
- ระวังช่วง rollover หรือ liquidity ต่ำ
- ระวังข่าว/high-volatility event
- ห้ามใช้ high volatility เพื่อเพิ่ม lot หรือไล่ราคา

## Risk Controls

ต้องไม่ bypass:

- InpLiveTradingEnabled
- InpDemoSafeMode
- InpRequireStrategyTester
- max daily loss
- max weekly loss
- max drawdown
- equity kill switch
- max losing streak
- max open orders

## Diagnostics Required

ก่อนพิจารณา strategy ต้องมี:

- setup count
- accepted/rejected count
- pending fill/cancel count
- invalidation reason
- SL/TP distance
- actual risk money
- drawdown by phase
- Calmar ratio
- annualized return
- trade count

## Explicit Prohibitions

- martingale
- unlimited grid
- hidden loss holding
- closing only winners while keeping losers
- adding indefinitely into drawdown
- increasing risk to meet annual target

## Final Rule

Price Action/Fibo strategy จะเริ่มได้เฉพาะใน Strategy Tester research branch เท่านั้น

ไม่มี live/demo approval จาก checklist นี้ และไม่มี profitability claim
