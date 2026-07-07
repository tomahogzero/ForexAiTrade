# Checkpoint AZ: PAF Lookahead Offline Tool

วันที่จัดทำ: 2026-07-07

## สถานะ

Checkpoint AZ เพิ่มเครื่องมือ Python สำหรับ join Price Action / Fibo diagnostic shadow rows กับ OHLC lookahead bar CSV แบบ offline เท่านั้น

ไม่มีการแก้ EA/MQL5, ไม่มีการแก้ presets, ไม่มีการรัน MT5, ไม่มีการรัน Strategy Tester, ไม่มี optimization, ไม่มีการเพิ่ม lot/risk และไม่มี profitability claim

## เหตุผล

Checkpoint AX ยืนยันว่า diagnostic fields ออกครบ แต่ shadow outcome ยังติด `BLOCKED_BY_MISSING_LOOKAHEAD_DATA`

Checkpoint AY กำหนดแผนให้ใช้ bar-series artifact แบบ offline เพื่อลดความเสี่ยง future leak ใน EA decision path

Checkpoint AZ จึงเพิ่ม tool ที่รับ bar CSV ภายนอก แล้ว join กับ shadow outcome rows โดยไม่ยุ่งกับ EA runtime

## ไฟล์ที่เพิ่ม

- `tools/paf_lookahead_joiner.py`
- `docs/65_Checkpoint_AZ_PAF_Lookahead_Offline_Tool_TH.md`
- `docs/ai/tasks/checkpoint-az-paf-lookahead-offline-tool.md`

## วิธีใช้

ตัวอย่าง:

```powershell
python tools\paf_lookahead_joiner.py `
  --shadow-outcomes research\results\paf_shadow_outcomes_all_cases.csv `
  --bars-csv path\to\paf_lookahead_bars.csv `
  --results-root research\results `
  --horizons 6,12,24,48
```

## รูปแบบ bar CSV ที่ต้องการ

ต้องมี column:

- `time`
- `open`
- `high`
- `low`
- `close`

ยอมรับชื่อแบบตัวพิมพ์ใหญ่ด้วย เช่น `Time`, `Open`, `High`, `Low`, `Close`

เวลารองรับรูปแบบ:

- `YYYY.MM.DD HH:MM:SS`
- `YYYY-MM-DD HH:MM:SS`
- `YYYY.MM.DD HH:MM`
- `YYYY-MM-DD HH:MM`

## Output

tool สร้าง:

- `research/results/paf_shadow_outcomes_enriched.csv`
- `research/results/paf_lookahead_join_summary.json`
- `research/results/paf_lookahead_join_summary.md`

## หลักการคำนวณ

tool ใช้ `event_time` จาก diagnostic row เพื่อ match กับ bar timestamp แบบ exact match

future bars เริ่มจาก bar หลัง event bar เท่านั้น เพื่อหลีกเลี่ยง same-bar ambiguity ของ diagnostic bar

สำหรับ direction:

- `BUY_CONTEXT`: MFE = future high - entry, MAE = entry - future low
- `SELL_CONTEXT`: MFE = entry - future low, MAE = future high - entry

สำหรับ hypothetical TP/SL:

- default TP = `1.5 * ATR`
- default SL = `1.0 * ATR`
- ใช้เพื่อ label offline เท่านั้น ไม่ใช่ order rule

ถ้า TP และ SL ถูกแตะใน future bar เดียวกัน ให้ label เป็น:

- `AMBIGUOUS_SAME_BAR`

## Guardrails

- tool ไม่รัน MT5
- tool ไม่เปิด market order
- tool ไม่เปิด pending order
- tool ไม่ modify position
- tool ไม่แก้ strategy logic
- tool ไม่ optimize
- tool ไม่เพิ่ม lot/risk
- output ไม่ใช่ proof of profitability
- lookahead data ต้องไม่ถูกใช้ใน EA decision path

## Limitations

- OHLC bar ไม่สามารถยืนยันลำดับ tick ภายในแท่งได้
- exact timestamp match อาจ fail หาก timezone หรือ bar timestamp ไม่ตรงกับ EA log
- หากไม่มี ATR หรือ direction จะคงสถานะ `DATA_MISSING` หรือ `DIRECTION_MISSING`
- sample size ต่ำยังเสี่ยงต่อการสรุปผิด

## Decision

- `OFFLINE_LOOKAHEAD_JOINER_ADDED`
- `ORDER_PATH_STILL_BLOCKED`
- `NO_MT5_RUN`
- `NO_OPTIMIZATION_APPROVED`
- `NO_PROFITABILITY_CLAIM`

## Next Safe Step

Checkpoint BA ควรเป็น approval package หรือ manual artifact checklist สำหรับสร้าง `paf_lookahead_bars.csv` จากแหล่งข้อมูลที่ตรวจสอบได้ แล้วค่อยรัน tool นี้กับข้อมูลจริง

ยังไม่ควร implement market orders หรือ pending orders
