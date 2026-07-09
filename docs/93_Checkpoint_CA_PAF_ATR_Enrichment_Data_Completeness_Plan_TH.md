# Checkpoint CA: PAF ATR Enrichment / Data Completeness Plan

Checkpoint CA เป็นแผนเติมข้อมูล ATR และตรวจ data completeness หลังจาก Checkpoint BZ รัน offline joiner แล้วพบว่า first-touch labels ยังเป็น `DATA_MISSING`

รอบนี้เป็น documentation / planning only:

- ไม่รัน MT5
- ไม่รัน Strategy Tester
- ไม่แก้ EA/source code
- ไม่แก้ preset
- ไม่แก้ production validator
- ไม่รัน joiner
- ไม่คำนวณ outcome ใหม่
- ไม่ optimize
- ไม่เพิ่ม lot/risk
- ไม่สรุป profitability

## ปัญหาจาก Checkpoint BZ

Checkpoint BZ รัน offline joiner สำเร็จ:

- Shadow rows: `33`
- Joined rows: `19`
- Direction missing rows: `14`
- MFE/MAE context: available

แต่ first-touch labels ยังไม่พร้อม:

- Horizon 6/12/24/48 labels: `DATA_MISSING`
- Reason: `atr is missing or invalid`

ดังนั้น BZ ยังใช้ตีความ TP-first / SL-first หรือ R-multiple ไม่ได้

## Root Cause

ไฟล์ shadow outcomes/enriched output ไม่มีค่า ATR ต่อ event row

Joiner ต้องใช้ ATR เพื่อคำนวณ hypothetical TP/SL:

- TP = entry +/- ATR * TP multiplier
- SL = entry +/- ATR * SL multiplier

ถ้า ATR หาย ระบบต้อง label เป็น `DATA_MISSING` แทนการเดา ซึ่งเป็นพฤติกรรมที่ถูกต้องและปลอดภัย

## ATR Enrichment Options

### Option A: ใช้ ATR ที่ EA log ไว้แล้ว ถ้ามี

ข้อดี:

- ตรงกับสิ่งที่ EA เห็นตอน diagnostic event
- ลดความต่างจาก runtime context

ข้อจำกัด:

- ต้องตรวจว่า EA mirror log มี ATR ต่อ event หรือไม่
- ถ้าไม่มี ต้องแก้ logging ใน checkpoint อื่นก่อน ไม่ใช่เดาค่าใน CA

### Option B: คำนวณ ATR offline จาก H1 bars

ข้อดี:

- ทำซ้ำได้จาก CSV เดิม
- ไม่ต้องรัน MT5
- เหมาะกับ offline diagnostics

ข้อกำหนด:

- ต้องระบุ ATR period ชัดเจน เช่น 14
- ต้องระบุสูตร True Range / ATR smoothing ชัดเจน
- ต้องใช้เฉพาะ bars ที่เกิดก่อนหรือถึง event time ตาม rule ที่ review แล้ว
- ห้ามใช้ future bars ในการคำนวณ ATR ของ event
- ต้องบันทึกว่าเป็น `offline_computed_atr` ไม่ใช่ runtime EA ATR

### Option C: เพิ่ม EA diagnostic logging ในอนาคต

ข้อดี:

- ทำให้ future diagnostics สมบูรณ์ขึ้น

ข้อจำกัด:

- เป็น source/MQL5 change ต้องมี checkpoint แยก
- ต้อง compile และ guardrail review
- ไม่ควรทำก่อนกำหนด offline method ชัดเจน

## Recommended Approach

สำหรับขั้นถัดไป แนะนำ:

1. ทำ Checkpoint CB เป็น offline ATR enrichment tool approval package
2. ใช้ Option B ก่อน: คำนวณ ATR offline จาก normalized `GOLD#` H1 bars
3. ระบุ ATR period เป็นค่าคงที่เพื่อ diagnostic เท่านั้น เช่น `14`
4. เพิ่มคอลัมน์ ATR เข้า shadow/enriched rows โดยใช้ชื่อเช่น `offline_atr_14`
5. ยังไม่เปลี่ยน EA/source code
6. ยังไม่ optimize ATR period
7. หลัง ATR enrichment ค่อยทำ checkpoint ถัดไปเพื่อ rerun joiner/first-touch labels

## Data Completeness Gates

ก่อนตีความ outcome ต้องผ่าน:

- event row มี direction ที่ใช้ได้
- event row มี entry reference price
- event row มี ATR ที่ valid
- event time match กับ bar time
- future bars มีพอสำหรับ horizon ที่ต้องการ
- gap policy dry-run ยังเป็น `PASS`
- ไม่มี unknown irregular gaps

ถ้า gate ใดไม่ผ่าน ต้องคง label เป็น `DATA_MISSING`

## สิ่งที่ยังห้ามทำ

- ห้ามตีความ BZ เป็นผลกำไร
- ห้ามนับ TP/SL outcome จาก rows ที่ ATR missing
- ห้าม optimize ATR period เพื่อให้ผลดูดี
- ห้ามเพิ่ม lot/risk
- ห้ามเริ่ม demo/live
- ห้ามใช้ offline ATR เป็น runtime EA ATR โดยไม่ระบุ limitation

## Decision

- `ATR_ENRICHMENT_PLAN_CREATED`
- `BZ_LIMITATION_CONFIRMED`
- `FIRST_TOUCH_LABELS_STILL_BLOCKED`
- `OFFLINE_ATR_OPTION_RECOMMENDED`
- `NO_ATR_OPTIMIZATION_APPROVED`
- `JOINER_NOT_RERUN`
- `MT5_NOT_RUN`
- `STRATEGY_TESTER_NOT_RUN`
- `EA_SOURCE_NOT_CHANGED`
- `PRESETS_NOT_CHANGED`
- `NO_PROFITABILITY_CLAIM`

## Next Safe Step

Checkpoint CB ควรเป็น approval package สำหรับ offline ATR enrichment tool/run:

- ไม่รัน MT5
- ไม่รัน Strategy Tester
- ไม่แก้ EA/source code
- ใช้ normalized H1 bars จาก BZ
- คำนวณ ATR แบบ offline เท่านั้น
- output เป็น enriched diagnostic artifact
- ยังไม่ตีความ profitability
