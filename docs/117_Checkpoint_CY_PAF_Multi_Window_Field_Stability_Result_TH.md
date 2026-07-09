# Checkpoint CY: ผล Multi-Window PAF Field Presence และ Direction-Gap Stability

วันที่: 2026-07-09

## สถานะ

Checkpoint CY รันตาม approval phrase ที่ผู้ใช้ให้ไว้เท่านั้น

- RunId: `run_20260709_202415`
- Symbol: `GOLD#`
- Timeframe: `H1`
- Windows:
  - `2026-03-08` ถึง `2026-03-15`
  - `2026-03-15` ถึง `2026-03-22`
  - `2026-03-22` ถึง `2026-03-29`
- Strategy Tester only
- No optimization
- No market orders
- No pending orders
- No position modification
- No lot/risk increase
- No profitability interpretation

## Compile

ก่อนรันได้ติดตั้ง source ไปยัง MT5 data folder และ compile active EA

- Compile log: `docs/verification/compile_after_checkpoint_CY.log`
- Result: `0 errors, 0 warnings`

## Process Safety

Runner เปิดและควบคุมเฉพาะ MT5 process ที่ตัวเองเริ่ม:

- Window 1 PID: `11648`
- Window 2 PID: `25548`
- Window 3 PID: `41288`

แต่ละ window พบ report ก่อนปิด process และปิดเฉพาะ PID ที่ runner เปิดเอง

## Artifact Path

Artifact root:

`G:\AiServer\Codex\ForexAiTrade\mt5_artifacts\run_20260709_202415\`

Case folders:

- `GOLD_HASH_H1_PAF_FIELD_STABILITY_CY_cy_w1_20260308_20260315`
- `GOLD_HASH_H1_PAF_FIELD_STABILITY_CY_cy_w2_20260315_20260322`
- `GOLD_HASH_H1_PAF_FIELD_STABILITY_CY_cy_w3_20260322_20260329`

## Execution Summary

| Window | Period | Execution | Report | Trades | Diagnostics | Forbidden markers | Baseline fallback markers |
|---|---|---|---|---:|---:|---:|---:|
| W1 | `2026-03-08` to `2026-03-15` | `PASS` | `FOUND` | 0 | 74 | 0 | 0 |
| W2 | `2026-03-15` to `2026-03-22` | `PASS` | `FOUND` | 0 | 72 | 0 | 0 |
| W3 | `2026-03-22` to `2026-03-29` | `PASS` | `FOUND` | 0 | 31 | 0 | 0 |

ทุก window มี:

- `no_trade_confirmation=PASS_FROM_REPORT_AND_EA_LOGS`
- `baseline_fallback_confirmation=PASS_FROM_EA_LOGS`
- `total_trades=0`

## CT Field Presence

ทุก window พบ CT diagnostics-only fields ครบใน `ea_mirror.log`

ทุก window มี parser summary keys ครบ:

- `paf_direction_gap_bucket_counts`
- `paf_fibo_direction_gap_reason_counts`
- `paf_zone_direction_gap_reason_counts`

Verdict:

`FIELD_PRESENCE_CONFIRMED_ALL_WINDOWS`

## Classification Counts

| Window | NO_SETUP | POSSIBLE_FIBO_PULLBACK | POSSIBLE_ZONE_REJECTION | POSSIBLE_BREAK_RETEST |
|---|---:|---:|---:|---:|
| W1 | 46 | 20 | 6 | 2 |
| W2 | 47 | 20 | 2 | 3 |
| W3 | 26 | 4 | 0 | 1 |

## Direction-Gap Buckets

| Window | NO_SETUP_DIRECTION_NOT_REQUIRED | USABLE_DIRECTION | TREND_ALIGNMENT_CONFLICT | WICK_TOO_SMALL | PRICE_BETWEEN_EMAS |
|---|---:|---:|---:|---:|---:|
| W1 | 46 | 18 | 3 | 5 | 2 |
| W2 | 47 | 23 | 0 | 2 | 0 |
| W3 | 26 | 3 | 0 | 0 | 2 |

## Stability Interpretation

สิ่งที่ดี:

- Field presence เสถียรครบทุก window
- Parser ทำงานครบทุก window
- No-trade safety ผ่านทุก window
- ไม่พบ baseline fallback ทุก window

สิ่งที่ยังอ่อน:

- Window 3 มี diagnostic rows เพียง `31`
- Window 3 มี usable direction เพียง `3`
- Distribution ของ usable direction ระหว่าง W1/W2/W3 ยังไม่สม่ำเสมอ
- ยังไม่ถึง data gate เดิมที่ต้องการจำนวน relabel-ready rows มากพอสำหรับการคุย rule-candidate

ดังนั้น direction-gap stability ยังควรจัดเป็น:

`DIRECTION_GAP_STABILITY_INCONCLUSIVE_LOW_SAMPLE`

## Guardrail Result

Checkpoint CY ไม่พบ:

- market order
- pending order
- position modification
- `SIGNAL_BUY`
- `SIGNAL_SELL`
- baseline strategy fallback
- optimization
- lot/risk increase

## สิ่งที่ยังพิสูจน์ไม่ได้

Checkpoint CY ไม่ได้พิสูจน์:

- profitability
- entry quality
- exit quality
- drawdown safety
- demo/live readiness
- order-logic readiness

## Recommendation

PAF ยังต้องคงสถานะ:

`NOT_READY_FOR_ORDER_LOGIC`

ขั้นถัดไปที่ปลอดภัยควรเป็น Checkpoint CZ artifact review / data sufficiency decision:

- ใช้ artifact จาก CY เท่านั้น
- ไม่รัน MT5 ใหม่
- ตรวจว่ารวม CV + CY แล้วข้อมูลพอสำหรับ next diagnostic หรือยัง
- ถ้ายังไม่พอ ให้กำหนด data collection plan เพิ่ม
- ห้ามเพิ่ม order logic
- ห้าม optimize
- ห้าม claim profitability
