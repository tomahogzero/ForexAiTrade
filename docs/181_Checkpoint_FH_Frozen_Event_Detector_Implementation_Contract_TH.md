# Checkpoint FH: Frozen Event Detector Implementation Contract

วันที่: 2026-07-15

## วัตถุประสงค์และขอบเขต

FH freeze พฤติกรรม implementation แบบ deterministic สำหรับ historical detector ของ `MARKET_STRUCTURE_BREAK_RETEST_CONFIRMATION_V1` ก่อนการสร้าง full historical event population. แหล่งกติกาเดียวคือ FF และ FG; FH ไม่เปลี่ยน swing width, retest window, confirmation หรือ hypothesis ใดๆ และไม่ generate events/outcomes.

ทุก input bar ต้องเป็น GOLD# H1 source row ที่ valid, เรียงตาม `(bar_open_timestamp, source_row_key)` แบบ ascending. `bar_close_timestamp` คือเวลาปิดของ source H1 bar และเป็นเวลา decision; source-row timestamp/key ดิบต้องเก็บไว้เสมอ. H1 bar ที่ต่อเนื่อง valid เท่านั้นจึงเป็นหนึ่ง trading-bar count; ห้ามใช้ elapsed wall-clock hours เป็น counter.

## Frozen State Machine

### STATE 1 - SEEK_CONFIRMED_SWING

เมื่อ bar `i` ปิด ให้ตรวจ center bar `i-2` ด้วย FF strict 2-left/2-right rule. ต้องมี left 2 และ right 2 valid sequential bars; equality ไม่เป็น swing.

- `swing_timestamp`: source timestamp ของ center bar
- `swing_confirmation_timestamp`: close timestamp ของ bar `i`
- `swing_price`: center high สำหรับ `SWING_HIGH`, center low สำหรับ `SWING_LOW`
- `swing_type`: `SWING_HIGH` หรือ `SWING_LOW`

ลำดับภายใน close ของ bar `i` ถูก freeze เป็น: validate continuity -> confirm swing `i-2` -> update active swing state -> evaluate break ด้วย close ของ bar `i`. ดังนั้น swing ใช้ได้เฉพาะเมื่อ right-side 2 bars ปิดแล้ว และไม่ใช้ future bar.

### STATE 2 - SEEK_BREAK

เก็บ active confirmed swing ล่าสุดแยกตาม type. LONG ใช้เฉพาะ most recent `SWING_HIGH`; SHORT ใช้เฉพาะ most recent `SWING_LOW` ที่ confirmation timestamp ไม่เกิน break decision timestamp.

- LONG break: `close > swing_price`
- SHORT break: `close < swing_price`
- wick-only ไม่ใช่ break เพราะไม่มี close ผ่าน level

เมื่อเกิด break ให้ freeze record: direction, broken swing timestamp, swing confirmation timestamp, swing price, break timestamp, break close และ source-row keys ของ swing confirmation/break. Break ถูก anchor กับ swing เดิมตลอด lifecycle และ swing ใหม่ห้ามแก้ย้อนหลัง.

### STATE 3 - SEEK_RETEST

เริ่ม retest search จาก **next valid H1 bar after break**. Break candle นับเป็น bar 0 และห้ามเป็น retest candle. Window คือ valid H1 trading bars ลำดับที่ 1 ถึง 12 หลัง break เท่านั้น; accepted daily/weekend closure ข้ามได้ตาม existing data policy โดยไม่สร้าง bar, แต่ unverified timestamp gap ใน sequence ที่ต้องใช้ต้อง terminal เป็น `DATA_INCOMPLETE_GAP` พร้อม gap timestamp และ current detector state.

- LONG retest: `bar.low <= broken_swing_price`
- SHORT retest: `bar.high >= broken_swing_price`
- retest touch/cross ต้องเป็น exact broken swing price; ไม่มี tolerance band

multiple retest touches ก่อน confirmation เป็นของ break candidate เดิม. หลัง valid bar 12 ปิดโดยไม่มี retest ให้ `RETEST_NOT_FOUND_WITHIN_12_BARS`.

### STATE 4 - SEEK_CONFIRMATION

หลังมี retest valid แล้ว ตรวจทุก valid sequential bar ที่เหลือใน window เดิม; confirmation ต้องเกิดหลัง retest และภายใน post-break bars 1..12.

- LONG: `close > open` และ `close > previous valid candle high`
- SHORT: `close < open` และ `close < previous valid candle low`

confirmation failure ใน bar หนึ่งไม่สร้าง break ใหม่; candidate เดิมตรวจต่อถึง bar 12. หากหมด window โดยไม่มี confirmation ให้ `CONFIRMATION_NOT_FOUND_WITHIN_12_BARS`. เมื่อผ่าน ให้ entry reference เป็น confirmation close เพื่อ diagnostic เท่านั้น ไม่ใช่ order instruction. `confirmation_timestamp` และ event timestamp คือ confirmation candle close timestamp ซึ่งเป็นเวลาแรกที่ข้อมูลครบ.

## Candidate, Replacement, Duplicate และ Tie-breaking

- identifier state ใช้ deterministic source fields เท่านั้น; ไม่มี random UUID.
- มี open candidate ได้สูงสุดหนึ่งตัวต่อ `(direction, break_id)`. Candidate LONG และ SHORT แยก lane; event หนึ่งไม่สามารถเป็นทั้งสอง direction หรือใช้ break state เดียวร่วมกันได้.
- break เดิม emit event ได้สูงสุดหนึ่งครั้ง; หลัง `EVENT_EMITTED` หรือ terminal status จะ close.
- break close ใหม่ใน direction เดิมขณะ candidate เดิมยัง open ไม่สร้าง candidate ใหม่และบันทึก `DUPLICATE_SUPPRESSED`; candidate เดิมยัง anchor เดิม.
- candidate ใหม่ต้องเป็น valid close-based break ของ subsequently eligible confirmed swing หลัง candidate เดิม close. failed confirmation ไม่เปิด break ใหม่.
- swing ใหม่แทน active swing เดิมได้หลัง confirmation timestamp เท่านั้น และกระทบเฉพาะ break ที่ยังไม่ถูก record.
- tie-break: process bars by `(bar_open_timestamp, source_row_key)` ascending; confirm `SWING_HIGH` ก่อน `SWING_LOW` หาก malformed identical source ordering ทำให้ทั้งคู่ eligible; evaluate LONG before SHORT only for deterministic logging. Strict inequalities normallyทำให้ simultaneous conflict ไม่เกิด. Existing open candidate ไม่ถูก reassigned.

## Gap, History และ Terminal Status

ห้าม interpolate, infer, reconstruct หรือ silent bridge. Any unverified gap ใน required swing five-bar sequence, break/retest/confirmation sequence, previous-valid confirmation reference หรือ ATR prerequisite ต้อง fail closed, เก็บ gap timestamp และ state, แล้วใช้ `DATA_INCOMPLETE_GAP`. broker-history completeness remains `NOT_PROVEN`.

Terminal status meanings:

| Status | Meaning |
|---|---|
| `EVENT_EMITTED` | confirmation ผ่านและ schema ครบ |
| `NO_BREAK` | confirmed swing observation จบโดยไม่มี qualifying close break |
| `RETEST_NOT_FOUND_WITHIN_12_BARS` | valid bars 1..12 ไม่มี exact-level retest |
| `CONFIRMATION_NOT_FOUND_WITHIN_12_BARS` | มี retest แต่ไม่มี confirmation ใน window |
| `DATA_INCOMPLETE_GAP` | required sequence มี unverified gap/invalid continuity |
| `INSUFFICIENT_LEFT_HISTORY` | ไม่มี bars ก่อน swing หรือ ATR prerequisite ครบ |
| `INSUFFICIENT_RIGHT_HISTORY` | ไม่มี right-side two completed bars สำหรับ swing |
| `ATR_UNAVAILABLE` | pattern ผ่านแต่ approved ATR จาก prior completed bars ไม่พร้อม |
| `DUPLICATE_SUPPRESSED` | attempted duplicate ของ open/closed break ถูก suppress |

## Deterministic Identifiers

ใช้ canonical source fields ที่ UTF-8, pipe-delimited, timestamp ISO-8601 และ decimal price canonical string; `SHA-256` lower-case hex ของข้อความนั้นเป็น key. ห้าม random UUID.

- `swing_id = sha256(symbol|timeframe|swing_type|swing_timestamp|swing_price|source_row_key_center)`
- `break_id = sha256(symbol|timeframe|direction|swing_id|break_timestamp|break_close|source_row_key_break)`
- `candidate_id = sha256(break_id|retest_window=12|retest_start=next_valid_bar)`
- `event_id = sha256(symbol|timeframe|direction|swing_timestamp|break_timestamp|confirmation_timestamp|break_id)`

`source_row_keys` is an ordered immutable list: left/right swing rows, swing center, break, retest, previous-valid confirmation reference, confirmation, and ATR input rows. Equality of IDs requires exact equality of these frozen source fields.

## Frozen Future Event Schema

| Field |
|---|
| event_id |
| symbol |
| timeframe |
| direction |
| swing_type |
| swing_timestamp |
| swing_confirmation_timestamp |
| swing_price |
| break_timestamp |
| break_close |
| retest_timestamp |
| retest_price_reference |
| confirmation_timestamp |
| confirmation_open |
| confirmation_high |
| confirmation_low |
| confirmation_close |
| entry_reference_price |
| atr |
| year |
| source_row_keys |
| data_quality_status |
| exclusion_reason |

`atr` uses existing approved `offline_atr_14` definition from prior completed H1 bars only. `year` derives from confirmation timestamp. Non-emitted terminal records may retain null future-event fields but must retain identifiers, source keys, data quality status and exclusion reason.

## Deterministic Pseudocode

```text
for each source bar in canonical valid order:
  validate row and continuity; mark affected state DATA_INCOMPLETE_GAP on unverified gap
  if i lacks two left bars: record INSUFFICIENT_LEFT_HISTORY where applicable
  if i has center i-2 and five valid sequential bars:
    confirm strict swing(s) for i-2 at current bar close
    update only active swing state not already anchored by a break
  else if right-side bars cannot exist: record INSUFFICIENT_RIGHT_HISTORY at stream end

  for direction in LONG, SHORT order:
    if no open candidate and current close is qualifying break of most-recent confirmed matching swing:
      create immutable break/candidate state; retest counter starts at next valid bar
    if open candidate:
      count only next valid bars after its break
      if gap touches required sequence: terminal DATA_INCOMPLETE_GAP
      else if bar 1..12 touches exact level: retain first valid retest timestamp
      if after retained retest current bar passes frozen confirmation: compute prior-bar ATR; emit or ATR_UNAVAILABLE
      if bar 12 closes without retest: RETEST_NOT_FOUND_WITHIN_12_BARS
      if bar 12 closes after retest without confirmation: CONFIRMATION_NOT_FOUND_WITHIN_12_BARS
```

## Look-ahead Prevention Checklist

- center swing never usable before the second right-side bar close
- break reads only confirmed swing state available at its decision timestamp
- retest starts on next valid bar; confirmation is after retest
- no future bar changes recorded swing, break, candidate, or emitted event
- prior valid candle only supplies confirmation reference
- ATR consumes only completed bars strictly before event bar
- gaps never create inferred bars or implicit continuity
- IDs and source keys preserve replayable provenance

## Fixture Expectations (reuse FG cases)

| FG fixture | FH expected behavior |
|---|---|
| valid LONG sequence | one `EVENT_EMITTED` LONG only after next-bar retest and valid confirmation |
| valid SHORT sequence | one `EVENT_EMITTED` SHORT only after next-bar retest and valid confirmation |
| wick-only false break | no break; no event |
| swing not yet confirmed | cannot enter SEEK_BREAK |
| retest after 12-bar window | `RETEST_NOT_FOUND_WITHIN_12_BARS` |
| confirmation failure | `CONFIRMATION_NOT_FOUND_WITHIN_12_BARS` after valid retest/window expiry |
| gap inside required sequence | `DATA_INCOMPLETE_GAP`, retain gap timestamp/state |
| duplicate candidate sequence | one candidate/event maximum; later attempt `DUPLICATE_SUPPRESSED` |

## Exact Scope for Future FI (not created)

FI may, only with separate approval, implement the frozen detector and run deterministic fixture tests. FI must not run the full historical population unless separately and explicitly approved after fixture validation. FI may not calculate TP/SL outcomes, alter FF/FH definitions, optimize, change EA/MQL5/presets, use MT5/Strategy Tester, create order logic, or do demo/live testing.

## Status

- strategy performance: `NOT_EVALUATED`
- order logic: `NOT_APPROVED`
- candidate: `NOT_READY_FOR_ORDER_LOGIC`
- profitability: `NOT_CLAIMED`

No profitability, trading-edge, or executable-trading conclusion is authorized.