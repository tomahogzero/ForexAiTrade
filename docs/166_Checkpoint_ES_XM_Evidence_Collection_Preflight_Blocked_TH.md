# Checkpoint ES: XM Fresh Evidence Collection Preflight Blocked

วันที่: 2026-07-12

## Approved Scope

ES ได้รับอนุมัติให้เก็บ fresh `GOLD#` H1 evidence ตาม EQ contract เท่านั้น โดยห้าม Strategy Tester, order, EA/preset change, policy/validator change, joiner และ shadow backtest

## Preflight Finding

พบ XM MT5 instance ที่กำลังทำงานอยู่ก่อน ES:

- executable: `C:\Program Files\XM Global MT5\terminal64.exe`
- PID: `16380`
- title: `168886591 - XMGlobal-MT5 2: Demo Account - Hedge - XM Global Limited - [GOLD#,H1]`
- terminal build: `5.0.0.5833`

PID นี้ไม่ได้เริ่มโดย ES ดังนั้นห้าม kill, restart หรือควบคุมผ่าน workflow อัตโนมัติ ตาม project guardrails

ใน session นี้ไม่มี desktop/MT5 UI automation และไม่พบ existing non-UI exporter ที่เก็บ fresh History/Symbol Bars request, per-gap screenshot และ EQ provenance manifest ได้ จึงไม่สามารถสร้าง EQ layer A ด้วยวิธีที่ตรวจสอบได้โดยไม่แตะ terminal ของผู้ใช้

## Decision

Decision: `ES_BLOCKED_UNOWNED_MT5_PROCESS_AND_NO_SAFE_EXPORT_INTERFACE`

- fresh evidence collection: `NOT_RUN`
- MT5 process started by ES: `0`
- Strategy Tester: `NOT_RUN`
- policy/validator: `UNCHANGED_NOT_BYPASSED`
- joiner/shadow backtest: `NOT_RUN`
- strategy performance: `NOT_EVALUATED`
- profitability claim: `NOT_ALLOWED`
- PAF: `NOT_READY_FOR_ORDER_LOGIC`

Shadow readiness remains `40%`.

## Required Next Direction

ต้องเลือกอย่างใดอย่างหนึ่งก่อน ES จะดำเนินต่อ:

1. ผู้ใช้ export `GOLD#` H1 evidence ตาม EQ contract ด้วยตนเองและให้ paths/manifest มาเพื่อ offline intake
2. ผู้ใช้ปิด terminal ที่มีอยู่ แล้วอนุมัติให้ ES เริ่ม MT5 instance ของตนเอง พร้อมวิธี export ที่ควบคุมได้
3. ผู้ใช้อนุมัติให้ attach/control terminal PID `16380` อย่างชัดเจน ซึ่งยังต้องมี UI automation/export interface ที่ใช้งานได้

ห้ามถือว่าหลักฐานเดิมหรือ CSV ระยะยาวแทน fresh EQ layer A ได้
