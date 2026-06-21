# Checkpoint B: Result Aggregation And Single Case Research

วันที่: 2026-06-20

เอกสารนี้อธิบาย Checkpoint B สำหรับ ForexAiTrade โดยเน้นการจัดผลลัพธ์ให้สะอาด และการรัน research แบบควบคุมเพียง 1 case ผ่าน 3 ช่วงเวลาเท่านั้น

## ข้อจำกัดของ Checkpoint นี้

- ไม่ optimize parameters
- ไม่เพิ่ม MicroTrend
- ไม่แก้ strategy entry/exit logic เพื่อไล่กำไร
- ไม่ claim profitability
- ไม่รัน full matrix
- ไม่ปิดหรือ kill MT5 terminal ที่ runner ไม่ได้เปิดเอง

## ทำไมต้องแยก old debug runs

ก่อนหน้าเคยมี debug runs ที่สถานะเป็น `NO_REPORT` เพราะ MT5 ยังไม่ export report ตาม path ที่ runner คาดไว้ในช่วงทดสอบ reliability

ถ้าเอา debug failed runs เหล่านี้ไปปนในตารางผลหลัก จะทำให้การอ่านผลล่าสุดสับสน เพราะ:

- execution failure เก่าไม่ใช่ผล strategy
- `NO_REPORT` ไม่ได้แปลว่า strategy แพ้หรือชนะ
- run ล่าสุดที่ผ่านแล้วควรถูกอ่านแยกจาก infrastructure failure

ดังนั้น `tools/generate_research_summary.py` ถูกปรับให้:

- เลือก run เฉพาะด้วย `--run-id`
- เลือก run ล่าสุดที่สำเร็จด้วย `--latest-run`
- ค่า default ไม่ปน old failed debug runs ในตารางหลัก
- ย้าย old failed debug runs ไป section `Debug / Infrastructure Failed Runs`

## วิธี generate summary เฉพาะ RunId

ตัวอย่าง:

```powershell
python tools\generate_research_summary.py `
  --runs-root research\runs `
  --results-root research\results `
  --run-id run_20260619_221606
```

ไฟล์หลัก:

```text
research/results/research_summary.md
```

หากต้องการให้ summary ไปอยู่ในโฟลเดอร์ run:

```powershell
python tools\generate_research_summary.py `
  --runs-root research\runs `
  --results-root research\results `
  --run-id <RunId> `
  --summary-output research\runs\<RunId>\research_summary_for_run.md
```

## วิธีรันหนึ่ง case ผ่าน train / validation / out-of-sample

ใช้ runner แบบระบุ case เดียว:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\run_mt5_research_batch.ps1 `
  -CaseId EURUSD_H1_10000 `
  -Phases train,validation,out_of_sample `
  -TerminalExe "C:\Program Files\XM Global MT5\terminal64.exe" `
  -TerminalDataFolder "C:\Users\tomah\AppData\Roaming\MetaQuotes\Terminal\BB16F565FAAA6B23A20C26C49416FF05" `
  -TesterRootFolder "C:\Users\tomah\AppData\Roaming\MetaQuotes\Tester\BB16F565FAAA6B23A20C26C49416FF05" `
  -CaseTimeoutMinutes 10 `
  -RetryCount 0 `
  -OutputRoot research\runs
```

คำสั่งนี้จะรันเฉพาะ:

- `EURUSD_H1_10000_train`
- `EURUSD_H1_10000_validation`
- `EURUSD_H1_10000_out_of_sample`

และไม่รัน full matrix

## Output Structure

เมื่อรันสำเร็จ จะได้:

```text
research/runs/<RunId>/
  EURUSD_H1_10000_train/
  EURUSD_H1_10000_validation/
  EURUSD_H1_10000_out_of_sample/
  run_status.json
  research_summary_for_run.md
```

แต่ละ case folder ควรมี:

- `case.json`
- `generated_tester.ini`
- `effective_preset.set`
- `process_info.json`
- `runner.log`
- `tester_log_excerpt.log`
- `ea_mirror.log` ถ้ามี
- `mt5_report.htm`
- `parsed_result.json`
- `status.json`

## วิธีอ่านผล

อ่าน `research_summary_for_run.md` ก่อน เพื่อดู:

- execution status ของแต่ละ phase
- net profit, profit factor, drawdown, trades
- classification
- candidate ranking
- debug/infrastructure failure แยกต่างหาก

จากนั้นค่อยดู `parsed_result.json` ในแต่ละ case folder หากต้องการรายละเอียดเชิง metric

## Scoring Rule สำหรับ Checkpoint B

ห้ามอนุมัติ candidate จาก train อย่างเดียว

Classification:

- `RESEARCH_CANDIDATE` เกิดได้เฉพาะเมื่อ validation และ out_of_sample เป็นบวกและผ่าน gates ทั้งคู่
- train ที่กำไรแต่ validation/out-of-sample ยังไม่ผ่าน จะเป็น `TRAIN_ONLY_PROFIT`
- report ที่ขาดทุนแต่ parse ได้ยังคงเป็น execution `PASS` เพราะ execution status ไม่ใช่ verdict ว่ากลยุทธ์ดี
- infrastructure failure เช่น `NO_REPORT` จะไม่ถูกนำไปปนกับตารางผลหลักของ run ล่าสุด

## ทำไมสิ่งนี้ไม่ใช่ optimization

Checkpoint B รัน case เดียวและ parameter ชุดเดิม เพื่อทดสอบ:

- runner ทำงานครบ 3 period ได้
- result aggregation สะอาด
- report parser แยก timeframe/period ได้
- scoring ไม่ approve จาก train อย่างเดียว

ไม่มีการ search parameter, ไม่มีการเลือกค่าที่กำไรสูงสุด, และไม่มีการปรับ strategy logic

## ทำไมสิ่งนี้ไม่ใช่ proof of future profitability

Backtest เป็นเพียงข้อมูลวิจัยจากอดีต ผลที่ดีในอดีตไม่ได้รับประกันผลในอนาคต

ก่อนพิจารณาใช้งานจริง ต้องมีอย่างน้อย:

- validation ที่ไม่ overfit
- out-of-sample ที่ผ่าน
- demo forward test
- slippage/spread realism
- risk review
- broker-specific symbol and contract checks

