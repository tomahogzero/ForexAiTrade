# Checkpoint CD: PAF Offline First-Touch Relabel Approval Package

Checkpoint CD เป็น approval package สำหรับรอบถัดไปที่จะนำ `offline_atr_14` จาก Checkpoint CC ไปใช้ relabel first-touch outcome แบบ offline

รอบนี้เป็นเอกสาร/แผนอนุมัติเท่านั้น:

- ไม่รัน MT5
- ไม่รัน Strategy Tester
- ไม่แก้ EA/source code
- ไม่แก้ presets
- ไม่แก้ production validator
- ไม่รัน relabel จริง
- ไม่คำนวณ R-multiple จริง
- ไม่ optimize ATR period, TP multiple, SL multiple, horizon หรือ parameter ใด ๆ
- ไม่เพิ่ม lot/risk
- ไม่สรุป profitability

## เหตุผล

Checkpoint CC เติม ATR แบบ offline สำเร็จ:

- Bars read: `230`
- Event rows: `33`
- Events with valid `offline_atr_14`: `17`
- Events missing ATR: `2`
- Direction-missing rows: `14`
- Unknown irregular gaps: `0`

ข้อมูลพร้อมขึ้น แต่ยังไม่ควรตีความ outcome ทันทีโดยไม่มี approval package เพราะ first-touch relabeling สามารถทำให้ดูเหมือนมี TP/SL result ได้ ทั้งที่ยังเป็นเพียง shadow diagnostic ไม่ใช่ order จริง

## ขอบเขตที่ขออนุมัติสำหรับรอบถัดไป

Checkpoint ถัดไปหลัง CD สามารถทำได้เฉพาะ offline first-touch relabeling:

1. อ่าน `paf_shadow_outcomes_atr_enriched.csv` จาก Checkpoint CC
2. อ่าน `paf_lookahead_bars.csv` จาก Checkpoint BZ
3. ใช้ `offline_atr_14` เท่านั้น
4. relabel first-touch สำหรับ horizons เดิม: `6`, `12`, `24`, `48`
5. ใช้ TP/SL multiples เดิมจาก BZ diagnostic run:
   - TP ATR multiple: `1.5`
   - SL ATR multiple: `1.0`
6. แยก rows ที่พร้อมประเมินออกจาก rows ที่ยัง `DATA_MISSING`
7. รายงาน same-bar ambiguity อย่างอนุรักษ์นิยม

Checkpoint ถัดไปยังไม่ควร:

- เปลี่ยน strategy logic
- เพิ่ม market order
- เพิ่ม pending order
- เพิ่ม position modification
- ใช้ผล relabel เพื่อ optimize parameters
- ตัดสินว่า strategy ผ่าน/ไม่ผ่านจากกำไร
- สรุปว่าสามารถเทรดจริงได้

## Input Files ที่อนุญาต

ใช้ไฟล์ offline ที่มีอยู่เท่านั้น:

- `research/results/checkpoint_cc_offline_atr_enrichment/paf_shadow_outcomes_atr_enriched.csv`
- `research/results/checkpoint_bz_offline_joiner_run/paf_lookahead_bars.csv`
- `research/results/checkpoint_cc_offline_atr_enrichment/offline_atr_enrichment_summary.json`

ถ้าไฟล์ใดหายหรือ schema ไม่ตรง ต้องหยุดและรายงานเป็น `INPUT_MISSING` หรือ `SCHEMA_MISMATCH`

## Relabel Rules ที่อนุญาต

ใช้เฉพาะ rows ที่ผ่านเงื่อนไข:

- `offline_atr_status = ATR_READY`
- `offline_atr_14 > 0`
- `direction` เป็น `BUY_CONTEXT` หรือ `SELL_CONTEXT`
- `entry_reference_price` มีค่า valid
- `event_time` match กับ bar time
- future bars มีพอสำหรับ horizon ที่ประเมิน

rows ต่อไปนี้ต้องยังคง `DATA_MISSING` หรือ classification จำกัด:

- `DIRECTION_MISSING`
- `ATR_MISSING`
- entry missing
- event time missing/mismatch
- future bars ไม่พอ

## Outcome Labels ที่อนุญาต

สำหรับแต่ละ horizon อนุญาต label:

- `TP_FIRST`
- `SL_FIRST`
- `NO_RESOLUTION`
- `AMBIGUOUS_SAME_BAR`
- `DATA_MISSING`
- `DIRECTION_MISSING`

ถ้า TP และ SL ถูกแตะในแท่ง OHLC เดียวกัน ต้อง label เป็น `AMBIGUOUS_SAME_BAR` ห้ามเดาว่า TP หรือ SL มาก่อน เพราะ OHLC bar ไม่รู้ลำดับ tick ภายในแท่ง

## Guardrails

Checkpoint ถัดไปต้องยืนยัน:

- MT5 run: `NO`
- Strategy Tester run: `NO`
- EA/source changed: `NO`
- presets changed: `NO`
- order action generated: `NO`
- optimization: `NO`
- profitability claim: `NO`

## Output Artifacts ที่ควรสร้างในรอบถัดไป

เสนอ output folder:

- `research/results/checkpoint_ce_paf_first_touch_relabel/`

เสนอไฟล์:

- `paf_shadow_outcomes_first_touch_relabel.csv`
- `first_touch_relabel_summary.json`
- `first_touch_relabel_summary.md`
- `first_touch_relabel_by_horizon.csv`
- `first_touch_relabel_guardrail_summary.md`

## Stop Conditions

ต้องหยุดทันทีถ้า:

- input file หาย
- schema ไม่ตรง
- `offline_atr_14` ไม่มีในไฟล์ CC
- พบการใช้ ATR column อื่นโดยไม่ได้รับอนุมัติ
- TP/SL multiples ถูกเปลี่ยนจาก `1.5` / `1.0`
- horizons ถูกเปลี่ยนจาก `6,12,24,48`
- tool พยายามรัน MT5 หรือ Strategy Tester
- tool พยายามอ่าน/แก้ EA source หรือ presets
- tool พยายามเปิด order หรือสร้าง pending order
- output สื่อว่าเป็นกำไรหรือคำแนะนำเทรดจริง

## สิ่งที่ยังไม่อนุมัติ

Checkpoint CD ไม่อนุมัติ:

- การ optimize parameter ใด ๆ
- การทำ strategy selection
- การเลือก candidate สำหรับ demo/live
- การเพิ่ม order logic
- การเพิ่ม pending order
- การใช้ `GOLD#` เป็นระบบเทรดจริง
- การสรุป monthly return
- การเพิ่ม lot/risk

## Decision

- `FIRST_TOUCH_RELABEL_APPROVAL_PACKAGE_CREATED`
- `OFFLINE_ATR_14_REQUIRED`
- `ATR_READY_ROWS_ONLY_FOR_RELABEL`
- `DIRECTION_MISSING_STAYS_BLOCKED`
- `ATR_MISSING_STAYS_DATA_MISSING`
- `SAME_BAR_AMBIGUITY_REQUIRED`
- `NO_OPTIMIZATION_APPROVED`
- `MT5_NOT_RUN`
- `STRATEGY_TESTER_NOT_RUN`
- `EA_SOURCE_NOT_CHANGED`
- `PRESETS_NOT_CHANGED`
- `NO_PROFITABILITY_CLAIM`

## Next Safe Step

ถ้า Checkpoint CD ผ่าน review ขั้นถัดไปควรเป็น:

`Checkpoint CE: PAF Offline First-Touch Relabel Tool and Dry Run`

Checkpoint CE ควรทำเฉพาะ offline relabel จากไฟล์ Checkpoint CC และ BZ เท่านั้น ยังไม่ควรสรุปความสามารถทำกำไรหรือความพร้อมเทรดจริง
