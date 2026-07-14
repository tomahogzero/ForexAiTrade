# Checkpoint FD: Preregistered Subgroup Interpretation

วันที่: 2026-07-15

FD รันเฉพาะ dimensions ที่ FC freeze: direction, year, fixed ATR regime และ horizons H6/H12/H24/H48 จาก EU artifact เดิม

- execution/event-key conservation: `PASS` / `1600`
- ATR fixed boundaries: P33 `4.4567`, P67 `7.02`
- available groups ทั้งหมดมี included sample `>=30`; ไม่มี `INSUFFICIENT_SAMPLE` ใน available dimensions
- setup subtype, diagnostic reason และ market session: `NOT_AVAILABLE`; ไม่ infer category
- ทุก group และ full population ถูก report ใน artifact

ผล counts/rates เป็น descriptive diagnostic hypotheses only ห้ามใช้เลือก best subgroup, direction, TP/SL, entry, หรือ order logic และห้ามสรุป trading edge/profitability

- strategy performance: `NOT_EVALUATED`
- profitability: `NOT_CLAIMED`
- order logic: `NOT_APPROVED`; PAF: `NOT_READY_FOR_ORDER_LOGIC`

ไม่มี MT5/Strategy Tester, EA/preset, optimization, parameter search, order/risk หรือ demo/live work

Decision: `FD_PREREGISTERED_SUBGROUPS_REPORTED_DIAGNOSTIC_ONLY`.
