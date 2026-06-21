# ภาพรวมโปรเจกต์ ForexAiTrade

ForexAiTrade คือ Expert Advisor สำหรับ MetaTrader 5 และ research pipeline สำหรับการเทรดฟอเร็กซ์แบบปรับตัวตามสภาพตลาด เป้าหมายหลักคือการรักษาทุนก่อนเสมอ ทุกคำสั่งเทรดต้องผ่านทั้งตัวตรวจจับสภาพตลาดและระบบควบคุมความเสี่ยงก่อนส่งคำสั่ง

สถาปัตยกรรมของ EA แยกเป็นโมดูล:

- `ForexAiTrade.mq5` ควบคุม lifecycle, position management, regime selection และ trade execution
- `RiskManager.mqh` บังคับใช้ข้อจำกัดด้านความเสี่ยงทั้งระดับบัญชีและระดับออเดอร์
- `RegimeDetector.mqh` จำแนกสภาพตลาด
- `Strategies/` เก็บ logic ของ trend following, breakout และ mean reversion
- `tools/` เก็บ Python scripts สำหรับอ่านรายงาน MT5 ให้คะแนน robustness จัดอันดับ parameter sets และสร้างรายงานสรุป

ระบบไม่เปิด live trading เป็นค่าเริ่มต้น ค่า `InpLiveTradingEnabled=false` และ `InpDemoSafeMode=true` ถูกตั้งไว้เพื่อความปลอดภัยโดยตั้งใจ
