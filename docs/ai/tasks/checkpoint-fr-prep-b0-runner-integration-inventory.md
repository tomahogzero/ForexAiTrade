# Checkpoint FR-Prep-B0 — Runner Integration Inventory and Frozen Execution Boundary

## สถานะและขอบเขต

ผลการตัดสินใจ: `FR_PREP_B0_PASS_INTEGRATION_PLAN_READY`

เอกสารนี้เป็นการออกแบบและทำบัญชีตำแหน่งโค้ดเท่านั้น ไม่มีการแก้ runner/detector/adapter และไม่มีการรัน FI, FJ replay, FQ inventory, holdout preflight, event, ATR-event, TP/SL หรือ outcome

ฐานที่ตรวจ: `bbc0e5df0ce59663bb2a0ad074ed4fd61cc7de85` (PR #169 merged)

## ขอบเขตที่ต้องคงเดิม

ไฟล์ detector/FI ที่ frozen ในคำสั่งต้องไม่เปลี่ยน byte-for-byte ตลอด FR-Prep-B. จาก inventory นี้ `tools/run_checkpoint_fj_historical_event_population.py` สามารถคงเดิมได้: wrapper ใหม่จะไม่ import `generate()` หรือแก้ไฟล์ FJ แต่จะใช้ detector ที่ไม่เปลี่ยนเมื่อ authorization อนุญาตโดยชัดเจน

`dataset_execution_descriptor.v1` ที่ merged มีโหมด `ADAPTER_VALIDATION_ONLY` และห้าม detector/outcome อยู่แล้ว จึงไม่ขยายหรือเปลี่ยน schema นี้. B1 จะเพิ่ม authorization ของ wrapper แยกต่างหาก: `FJ_BACKWARD_COMPATIBLE_REPLAY_ONLY` หรือ `PREFLIGHT_ONLY`; authorization ต้อง bind descriptor identity, dataset binding, รุ่น detector, และ frozen replay contract ก่อน import detector.

## แผนที่ความรับผิดชอบของ FJ

| กลุ่ม | ไฟล์ / ฟังก์ชัน | หน้าที่ปัจจุบันและ hard-code | วิธีเชื่อมต่อขั้นต่ำ | เปลี่ยนไฟล์? | ความเสี่ยง | หลักฐาน regression |
|---|---|---|---|---|---|---|
| A | `tools/market_structure_break_retest_detector.py:detect` | semantic detector ที่ frozen | เรียกแบบเดิมจาก wrapper ที่ได้รับ authorization เท่านั้น | ไม่ | สูง | FI 12/12 และ FJ IDs/order byte-identical |
| B | `tools/run_checkpoint_fj_historical_event_population.py:canonical,digest,write_csv` | deterministic orchestration/serialization | คัดลอกเฉพาะ serialization contract ที่มี golden proof เข้า wrapper; ไม่แก้ FJ | ไม่ | ปานกลาง | population/replay SHA และ CSV ordering เดิม |
| C | `...fj...:EXPECTED_SHA256,read_sources` | ชื่อไฟล์ 2023–2025, hash, path provenance, row key จาก filename | wrapper validate `historical_source_manifest.v1` ก่อน แล้ว materialize row key แบบ FJ-compatible จาก descriptor `file_name:index` | ไม่ | สูง | hashes/17,716 bars/event IDs เท่ากัน |
| D | `...fj...:read_policy,read_sources` | EO CSV lookup by `next_time`, `startswith(ACCEPTED_)`, 745/28 | wrapper validate `gap_policy_manifest.v1` EO/FJ mapping และแปลง normalized semantics เป็น `gap_before` ตาม fail-closed contract โดย exact allowlist | ไม่ | สูง | 745 accepted, 28 fail-closed; no semantic drift |
| E | `...fj...:normalize_terminals,write_csv` | terminal normalization and sorted CSV ordering | new wrapper reuses byte-compatible field/order rules, verified against committed FJ golden outputs | ไม่ | ปานกลาง | canonical population and terminal hashes unchanged |
| F | `...fj...:read_sources,generate,validate` | frozen FJ counts, GOLD#/H1, integrity, summary decisions | wrapper has a named FJ replay profile with assertions only for 2023–2025; no generic count inference | ไม่ | สูง | 1,079 / LONG 588 / SHORT 491 / mismatch 0 |
| G | `...fj...:generate` | unconditional detector import/call in current runner | wrapper keeps detector import inside an execution-only function reached only after authorization; preflight module has no detector import | ไม่ | สูง | guard test import/execution count 0 for preflight |
| H | `...fj...:generate,main` | event/terminal/provenance artifacts | execution profile may emit only FJ replay artifacts; preflight profile emits only sealed report | ไม่ | สูง | preflight artifact scan zero for events/ATR/TP-SL/outcomes |

## Adapter and runner integration points

- `tools/historical_source_adapter.py:normalize_manifest,validate_manifest_data` validates generic/FP/FJ mapping, hashes, OHLC, chronology, boundaries, row counts, and canonical timeline before wrapper materialization. Its public canonical identity remains unchanged.
- `tools/gap_policy_adapter.py:validate_gap_policy_data` validates exact EO/FJ/FQ allowlists, duplicate rules, deterministic order, and fail-closed semantics. Wrapper consumes only normalized entries; it must not classify from filename or prefix.
- `tools/dataset_execution_descriptor_adapter.py:compose_dataset_execution_descriptor,validate_dataset_execution_descriptor,validate_adapter_only_invocation` remains the adapter validation boundary. The B1 authorization is a separate wrapper contract so A3b's frozen `ADAPTER_VALIDATION_ONLY` semantics are not weakened.
- `tools/run_checkpoint_fq_holdout_gap_boundary.py` is historic FQ evidence only. It must not be imported, invoked, or modified. B3 instead uses generic adapters against the FP manifest and frozen FQ inventory under `--preflight-only`.

## Execution boundary

1. Wrapper parses an explicit invocation authorization before importing detector code.
2. `PREFLIGHT_ONLY` permits only path/hash/schema/timeline/gap/descriptor/count reconciliation and a sealed preflight JSON report.
3. The preflight module/function contains no detector import and accepts no event, ATR-event, TP/SL, outcome, traversal, or FN action flag. Its guard records `detector_import_count=0` and `detector_execution_count=0`.
4. FJ replay needs a separate exact authorization profile bound to the validated descriptor, FI fixture hash, frozen detector hash, FJ dataset identity, and output contract; it is the only future route to detector import.

## Frozen future contracts

### B2 FJ 2023–2025 regression

- FI fixtures: `12/12 PASS`
- source bars: `17,716`; events: `1,079`; LONG: `588`; SHORT: `491`
- event IDs and row ordering identical; canonical population byte-identical; mismatch `0`
- source hashes, detector semantics, and EO/FJ gap semantics unchanged; no rule change

### B3 FP/FQ 2020–2022 preflight-only reconciliation

- bars: `17,731`; total gaps: `774`; accepted weekend closures: `149`; `UNVERIFIED_GAP`: `625`
- validate only frozen FP source paths/hashes/schema/timeline, frozen FQ inventory, adapter descriptor, and counts
- emit only a sealed preflight report. No detector import/execution, swings/breaks/retests/confirmations, events/ATR, TP/SL, outcome traversal, or FN interpretation

## Incremental plan

1. **FR-Prep-B1** — Implement the new wrapper, two explicit authorization modes, and synthetic guard fixtures. No real source or FQ inventory.
2. **FR-Prep-B2** — Run the separately authorized, backward-compatible FJ 2023–2025 replay and prove the frozen regression contract.
3. **FR-Prep-B3** — Run real FP/FQ `--preflight-only` validation with the sealed report and zero detector-import proof.
4. **Future sealed FR** — separately approve holdout detector, outcomes, independent audit, and FN disposition.

## Safety

`broker_history_completeness=NOT_PROVEN`; strategy performance `NOT_EVALUATED`; profitability `NOT_CLAIMED`; order logic `NOT_APPROVED`; candidate `NOT_READY_FOR_ORDER_LOGIC`.
