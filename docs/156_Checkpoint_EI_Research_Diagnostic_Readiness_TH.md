# Checkpoint EI: Research Diagnostic Readiness Decision

วันที่: 2026-07-11

## Evidence

- DZ long-horizon gate: `PASS`, 156 windows
- EF row artifact: 2,353 rows, reconciliation `PASS`
- EG verifier fixtures: `PASS 6/6`
- EH real artifact: 1,600 eligible, 753 rejected, conservation/invariants `PASS`
- existing 20-window gate: `FAIL_REPORTED_SEPARATELY`

## Decision

`PAF_FIBO_USABLE_DIRECTION_V1_APPROVED_FOR_OFFLINE_RESEARCH_DIAGNOSTICS_ONLY`

อนุญาตให้ใช้ candidate นี้เพื่อจัดหมวด committed/offline diagnostic rows และสร้างรายงาน research diagnostics เท่านั้น

ไม่อนุญาต:

- ฝังหรือเปิดใช้ใน EA/MQL5
- แปลง eligible เป็น BUY/SELL signal
- ส่ง market/pending order หรือ modify position
- เลือก entry/exit, TP/SL, lot หรือ risk
- optimize จาก return/profit/drawdown
- demo/live forward test
- profitability claim

## Gates

- offline diagnostic candidate: `APPROVED`
- EA implementation: `NOT_APPROVED`
- order logic: `FAIL_NOT_APPROVED`
- three-year stability: `PASS`
- historical 20-window: `FAIL_REPORTED_SEPARATELY`
- PAF order readiness: `NOT_READY_FOR_ORDER_LOGIC`

ขั้นถัดไปที่ปลอดภัยต้องเป็น checkpoint แยกเพื่อ preregister independent/offline diagnostic analyses; ห้ามขยาย approval โดยอัตโนมัติไปยัง trading behavior

## Progress

- Research infrastructure: `98%`
- PAF diagnostic pipeline: `98%`
- PAF diagnostic interpretation: `98%`
- Fibo Pullback interpretation: `98%`
- PAF diagnostic rule-candidate: `100%`
- PAF order-logic: `0%`
- Demo/live: `0%`
