# Checkpoint CB: PAF Offline ATR Enrichment Approval Package

Checkpoint CB เป็น approval package สำหรับรอบถัดไปที่จะเติมค่า ATR แบบ offline ให้ข้อมูล Price Action / Fibo diagnostic ของ `GOLD#` H1

รอบนี้เป็นเอกสาร/แผนอนุมัติเท่านั้น:

- ไม่รัน MT5
- ไม่รัน Strategy Tester
- ไม่แก้ EA/source code
- ไม่แก้ presets
- ไม่แก้ production validator
- ไม่รัน joiner ซ้ำ
- ไม่คำนวณ first-touch outcome ใหม่
- ไม่ optimize ATR period หรือพารามิเตอร์ใด ๆ
- ไม่เพิ่ม lot/risk
- ไม่สรุป profitability

## เหตุผล

Checkpoint BZ ทำ offline joiner สำเร็จบางส่วน:

- Shadow rows: `33`
- Joined rows: `19`
- Direction missing rows: `14`
- MFE/MAE context: available

แต่ first-touch labels ยังเป็น `DATA_MISSING` เพราะ `atr is missing or invalid`

ดังนั้นก่อนจะประเมิน TP-first / SL-first / R-multiple ได้ ต้องเติม ATR ให้ event rows ด้วยวิธีที่ตรวจสอบได้และไม่ใช้ข้อมูลอนาคต

## ขอบเขตที่ขออนุมัติสำหรับรอบถัดไป

Checkpoint ถัดไปหลัง CB สามารถทำได้เฉพาะงาน offline ATR enrichment:

1. อ่าน normalized `GOLD#` H1 bars จากผลลัพธ์ BZ
2. อ่าน PAF shadow/enriched rows จากผลลัพธ์ BZ
3. คำนวณ ATR แบบ offline ด้วยสูตรที่กำหนดตายตัว
4. เติมคอลัมน์ ATR ให้ event rows
5. สร้าง artifact สรุปว่า event ใดมี ATR ใช้ได้ และ event ใดยัง `DATA_MISSING`

Checkpoint ถัดไปยังไม่ควร:

- เปลี่ยน logic entry/exit
- แก้ EA/source code
- แก้ presets
- รัน MT5
- รัน Strategy Tester
- optimize ATR period
- เลือก ATR period จากผลลัพธ์
- สรุปว่ากลยุทธ์กำไร
- เปิด market order / pending order / position modification

## Input Files ที่อนุญาต

ใช้ไฟล์ offline ที่มีอยู่เท่านั้น:

- `research/results/checkpoint_bz_offline_joiner_run/paf_lookahead_bars.csv`
- `research/results/checkpoint_bz_offline_joiner_run/paf_shadow_outcomes_enriched.csv`
- `research/results/checkpoint_bz_offline_joiner_run/paf_lookahead_join_summary.json`

ถ้าไฟล์ใดหายหรือ schema ไม่ตรง ต้องหยุดและรายงานเป็น `INPUT_MISSING` หรือ `SCHEMA_MISMATCH`

## ATR Method ที่อนุญาต

ใช้ ATR period คงที่:

- `ATR period = 14`

นี่เป็นค่า diagnostic default เพื่อให้ข้อมูลครบ ไม่ใช่ optimization

สูตรที่ต้องระบุใน tool/checkpoint ถัดไป:

- `true_range = max(high - low, abs(high - previous_close), abs(low - previous_close))`
- ATR ต้องคำนวณจาก bars ที่มีอยู่ก่อนหรือถึง event time เท่านั้น
- ห้ามใช้ future bars หลัง event time ในการคำนวณ ATR ของ event นั้น
- output column ต้องใช้ชื่อที่ชัดเจน เช่น `offline_atr_14`
- ต้องระบุชัดว่า `offline_atr_14` ไม่ใช่ runtime EA ATR

## Future Leakage Guard

สำหรับ event เวลา `T`:

- ATR ของ event นั้นใช้ได้เฉพาะข้อมูล H1 bars ที่ปิดก่อนหรือเท่ากับ `T`
- ห้ามใช้ high/low/close ของ bars หลัง `T`
- ถ้าจำนวน bars ก่อน `T` ไม่พอสำหรับ ATR period ต้องคงค่าเป็น missing
- missing ATR ต้องทำให้ outcome label ยังคงเป็น `DATA_MISSING`

## Data Completeness Gates

หลัง offline ATR enrichment ต้องรายงาน:

- total event rows
- rows with valid direction
- rows missing direction
- rows with valid entry price
- rows with valid `offline_atr_14`
- rows still missing ATR
- rows with enough future bars for each horizon
- rows still blocked from first-touch labeling

ห้ามตีความ outcome ถ้า gate ยังไม่ผ่าน

## Output Artifacts ที่ควรสร้างในรอบถัดไป

เสนอ output folder:

- `research/results/checkpoint_cc_offline_atr_enrichment/`

เสนอไฟล์:

- `paf_shadow_outcomes_atr_enriched.csv`
- `offline_atr_enrichment_summary.json`
- `offline_atr_enrichment_summary.md`
- `offline_atr_data_completeness.csv`
- `offline_atr_guardrail_summary.md`

## Stop Conditions

ต้องหยุดทันทีถ้า:

- input file หาย
- schema ไม่ตรง
- time format parse ไม่ได้
- H1 bars ไม่เรียงตามเวลา
- พบ unknown irregular gaps ที่ยังไม่ได้รับอนุมัติจาก BX policy
- event time จับคู่กับ bar ไม่ได้
- ATR period ถูกเปลี่ยนเพื่อให้ผลลัพธ์ดูดี
- tool พยายามรัน MT5 หรือ Strategy Tester
- tool พยายามอ่าน/แก้ EA source หรือ presets
- output สื่อว่าเป็นกำไรหรือคำแนะนำเทรดจริง

## สิ่งที่ยังไม่อนุมัติ

Checkpoint CB ไม่อนุมัติ:

- การ rerun first-touch joiner
- การตีความ TP-first / SL-first
- การเปรียบเทียบ profitability
- การเพิ่ม strategy logic
- การเพิ่ม pending order
- การเปิด demo/live forward test
- การเพิ่ม risk หรือ lot
- การใช้ `GOLD#` เป็นระบบเทรดจริง

## Decision

- `OFFLINE_ATR_ENRICHMENT_APPROVAL_PACKAGE_CREATED`
- `ATR_PERIOD_FIXED_FOR_DIAGNOSTIC_ONLY`
- `NO_ATR_OPTIMIZATION_APPROVED`
- `FUTURE_LEAKAGE_GUARD_REQUIRED`
- `FIRST_TOUCH_LABELS_STILL_BLOCKED`
- `JOINER_RERUN_NOT_APPROVED`
- `MT5_NOT_RUN`
- `STRATEGY_TESTER_NOT_RUN`
- `EA_SOURCE_NOT_CHANGED`
- `PRESETS_NOT_CHANGED`
- `NO_PROFITABILITY_CLAIM`

## Next Safe Step

ถ้า Checkpoint CB ผ่าน review ขั้นถัดไปควรเป็น Checkpoint CC:

`Checkpoint CC: Offline ATR Enrichment Tool and Dry Run`

Checkpoint CC ควรทำเฉพาะ offline ATR enrichment จากไฟล์ BZ ที่มีอยู่ แล้วสร้าง data completeness artifacts เท่านั้น ยังไม่ควรสรุปความสามารถทำกำไร
