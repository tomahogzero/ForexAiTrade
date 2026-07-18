# Checkpoint FR-Prep-A0 — Adapter Implementation Inventory and Frozen Interface Design

วันที่: 2026-07-18

สถานะ: `FR_PREP_A0_DESIGN_ONLY`

## ขอบเขต

เอกสารนี้เป็น inventory และ frozen interface design เท่านั้น ไม่มี adapter implementation, runner refactor, fixture creation/execution, detector execution, event/outcome, holdout preflight, TP/SL, gap reclassification, optimization, MT5/Strategy Tester, EA/order logic หรือ demo/live.

ฐานงาน: `33660ec7f703fe3f58d5fb40722bc4b5adb7974e` บน branch `agent/fr-prep-generic-adapter`.

## ข้อค้นพบหลัก

1. FJ รับ source path จาก CLI แต่อนุมัติด้วย `EXPECTED_SHA256` ที่ผูก filename/hash ของปี 2023–2025 เท่านั้น.
2. FJ ไม่ assert row count และ declared date range โดยตรง; hash pin ล็อก bytes ทางอ้อม แต่ generic manifest ต้องตรวจ rows/range/boundary อย่างชัดเจน.
3. FJ อ่าน EO CSV columns `prev_time,next_time,delta_hours,missing_h1_bars_estimate,prev_weekday,next_weekday,classification,policy_status` และ lookup ด้วย `next_time`.
4. FQ gap inventory ใช้ JSON fields `previous_bar_timestamp,next_bar_timestamp,policy_classification,accepted_for_trading_bar_skip,fail_closed_required` จึงเข้า FJ โดยตรงไม่ได้.
5. FJ ยอมรับทุกค่าที่ขึ้นต้น `ACCEPTED_`; adapter ต้องใช้ exact allowlist และให้ unknown/missing/contradictory entry fail closed.
6. FQ commit เพียง canonical timeline summary/hash ไม่ได้ commit canonical OHLC bars; adapter ต้อง rebuild จาก manifest-validated sources แล้วตรวจ hash ก่อน execution boundary.
7. FP/FJ/FQ artifacts มี absolute Windows development paths; logical source identity ต้องแยกจาก runtime locator.
8. FI detector รับ caller-provided canonical bars อยู่แล้ว จึงไม่ต้องแก้ detector core.

## Exact code and artifact map

| File | Function/location | Current responsibility | Hard-coded assumption | Minimal change | Risk |
|---|---|---|---|---|---|
| `tools/run_checkpoint_fj_historical_event_population.py` | `REQUIRED`, `EXPECTED_SHA256` lines 10–15 | raw schema/source allowlist | exact 2023–2025 basenames and hashes | A1 manifest descriptors; retain MT5 format profile | HIGH |
| same | `read_policy` lines 33–35 | EO CSV lookup | `next_time` key; duplicate overwrites; no domain check | A2 normalized EO/FQ parser; reject duplicates | HIGH |
| same | `read_sources` lines 38–85 | parse, hash, merge, detect/mark gaps | filename allowlist; no rows/range assertion; EO columns; prefix acceptance; fixed 745/28 | A1 source validation plus A2 gap adapter | HIGH |
| same | `normalize_terminals` lines 88–97 | project gap details | FJ keys `gap_start/gap_end` only | B project normalized gap back to legacy fields | MEDIUM |
| same | `validate` lines 100–116 | event integrity | frozen FI event schema/source keys | retain semantics; pass adapter key set | LOW |
| same | `generate` lines 119–132 | orchestration/summary/manifest | hard-coded `GOLD#`,`H1`, 28-gap text, EO path and FJ provenance | B descriptor-driven metadata with legacy mode | HIGH |
| same | `main` lines 144–169 | CLI/replay/artifact write | individual sources, EO policy, FJ names | B add descriptor input and preflight gate; preserve legacy CLI | HIGH |
| `tools/market_structure_break_retest_detector.py` | entire file; `detect` line 75 | frozen FI state machine | defaults `GOLD#`,`H1`; consumes `gap_before` | byte-for-byte unchanged; pass explicit metadata/bars | CRITICAL/FROZEN |
| `tools/run_checkpoint_fi_detector_fixtures.py` | entire file | FI fixture/golden validation | FI-only fixture contract | byte-for-byte unchanged; new adapter tests elsewhere | CRITICAL/FROZEN |
| `checkpoint_fj_source_manifest.json` | committed manifest | FJ provenance | absolute paths, 3 exact files/counts/ranges/hashes, EO path | A3 legacy golden reference only | MEDIUM |
| `checkpoint_fp_new_evidence_boundary_contract.json` | `source_bar_coverage`, `source_files` | FP holdout declaration | absolute paths; `rows`; fixed boundary/symbol/timeframe | A1 import mapping, no FP mutation | MEDIUM |
| `checkpoint_fp_source_provenance.json` | `sources` | compact FP manifest | field names differ; no format descriptor | A1 normalize to one descriptor schema | MEDIUM |
| `tools/run_checkpoint_fq_holdout_gap_boundary.py` | `ROOT`,`CONTRACT` lines 8–9 | FQ artifact locations | fixed development paths | leave unchanged; consume committed outputs | LOW |
| same | source loop lines 15–38 | source/OHLC/canonical bars | FP path fields; hard-coded symbol/timeframe; no explicit declared rows/range comparison | A1 generic explicit validation; FQ remains reference | HIGH |
| same | gap loop lines 39–49 | derive FQ inventory | H1 rules and FQ classification names | A2 consumes frozen inventory; no derivation/reclassification | HIGH |
| same | summary/timeline lines 50–58 | year stats/hash/decision | years 2020–2022, fixed artifacts/decision | A1 generic timeline expectations; no FQ decision change | MEDIUM |
| `checkpoint_fq_source_integrity.json` | `timeline`,`yearly_files` | timeline/source integrity | absolute paths; `parsed_rows`; summary/hash only | A1 map metadata and rebuild/hash bars | HIGH |
| `checkpoint_fq_gap_inventory.json` | array entries | frozen 774 gaps | FQ JSON schema; 149 accepted/625 unverified | A2 exact normalization and flag consistency | HIGH |
| `checkpoint_eo_gap_policy_review/gap_policy_dry_run.csv` | CSV artifact | FJ legacy gap policy | 8 EO columns; 773 rows; EO classes | A2 legacy profile/exact allowlist | HIGH |

## Minimal generic interfaces

Machine-readable draft: `docs/ai/tasks/checkpoint-fr-prep-a0-adapter-interface-draft.json`.

1. **Historical source manifest** — dataset ID, explicit symbol/timeframe, frozen boundary, ordered source descriptors, expected aggregate rows/range/duplicates/canonical hash, `NOT_PROVEN` completeness และ raw CSV not committed.
2. **Source-file descriptor** — stable source ID/basename, runtime-only locator, SHA-256, optional bytes, exact rows, first/last timestamps, duplicate count และ MT5 TSV format. ห้ามอนุมาน symbol/year จาก filename.
3. **Canonical timeline input** — metadata และ bars เรียง `(timestamp,source_row_key)` มี OHLC กับ optional normalized `gap_before/gap_details`; unique, resolvable, no interpolation/synthetic bars และ hash ตรง manifest/FQ.
4. **Gap-policy entry** — timestamp pair, original classification, normalized `ACCEPTED_CLOSURE|UNVERIFIED_GAP`, acceptance/fail-closed booleans, evidence/source schema. Unknown/missing/duplicate/contradictory ต้อง fail closed.
5. **Dataset execution descriptor** — manifest path, gap path/schema/hash, explicit output root, frozen detector/FI hashes, execution mode และ preflight evidence; `SEALED_HOLDOUT` ต้อง refuse ก่อน detector เมื่อ preflight ไม่ใช่ `PASS`.

Exact accepted EO values: `ACCEPTED_DAILY_BROKER_SESSION_GAP`, `ACCEPTED_WEEKEND_MARKET_CLOSURE`. Exact accepted FQ values: `ACCEPTED_ROUTINE_DAILY_SESSION_CLOSURE`, `ACCEPTED_ROUTINE_WEEKEND_CLOSURE`. EO blocked คือ `BLOCKED_UNCLASSIFIED_GAP`; FQ unverified คือ `UNVERIFIED_GAP`.

## Detector-core byte-for-byte freeze

ไฟล์ต่อไปนี้ต้องไม่เปลี่ยนแม้แต่ byte ใน FR-Prep-A1 ถึง B:

- `tools/market_structure_break_retest_detector.py`
- `tools/run_checkpoint_fi_detector_fixtures.py`
- `tests/fixtures/checkpoint_fi_detector_cases.json`
- `tests/fixtures/checkpoint_fi_detector_inputs.json`
- `tests/fixtures/checkpoint_fi_detector_expected.json`

FI result artifacts เป็น hash references และห้าม regenerate ระหว่าง adapter preparation.

## Future fixture inventory

| Micro-step | Fixtures to create later (none created in A0) | Assertion |
|---|---|---|
| A1 | `manifest_minimal_valid`, `manifest_fp_mapping`, `manifest_fj_mapping` | schema parses; FP/FJ fields map exactly |
| A1 | `manifest_missing_hash`, `hash_mismatch`, `row_count_mismatch`, `timestamp_range_mismatch` | fail source validation before detector |
| A1 | `duplicate_source_or_timestamp`, `runtime_path_relocation` | duplicates fail; relocation preserves identity |
| A2 | `gap_eo_accepted_daily`, `gap_eo_accepted_weekend`, `gap_eo_blocked` | exact EO values normalize correctly |
| A2 | `gap_fq_accepted_weekend`, `gap_fq_unverified` | FQ flags/classes agree; unverified marks next bar |
| A2 | `gap_unknown_accepted_prefix`, `gap_contradictory_flags`, `gap_duplicate_pair`, `gap_missing_pair` | never prefix-accept; reject/fail closed |
| A3 | `adapter_canonical_order`, `source_row_key_golden`, `runtime_path_invariance` | stable canonical bytes/keys |
| A3 | `adapter_eo_legacy_golden`, `adapter_fq_holdout_golden`, `adapter_replay_manifest` | adapter-only output/hash and two runs byte-identical; no detector |
| B | `fj_legacy_cli_compatibility` | legacy FJ invocation/artifact semantics remain compatible |
| B | `sealed_holdout_preflight_not_run`, `preflight_hash_mismatch`, `preflight_pass` | refuse before detector unless approved PASS evidence matches |

## Incremental plan

### FR-Prep-A1 — manifest schema and source validation

เพิ่ม adapter module ใหม่; parse manifest/descriptor; ตรวจ schema/hash/bytes/rows/range/boundary/OHLC/order/duplicates; รองรับ FP/FJ mapping และ relocated runtime paths. รันเฉพาะ synthetic A1 source-validation fixtures. ไม่อ่าน gap policy และไม่เรียก detector.

### FR-Prep-A2 — gap-policy adapter and gap fixtures

แปลง EO CSV/FQ JSON เป็น normalized gap entries ด้วย exact allowlists; duplicate/contradiction reject, missing/unknown fail closed; annotate next bar โดยไม่ reclassify หรือ infer closure. รันเฉพาะ gap adapter fixtures.

### FR-Prep-A3 — deterministic adapter replay and golden artifacts

freeze canonical serialization, source-row keys, path invariance และ adapter-only replay; compare EO legacy/FQ metadata and hashes. ไม่มี FJ replay หรือ detector/event/outcome.

### FR-Prep-B — FJ backward-compatible runner integration and holdout preflight guard

integrate descriptor ที่ orchestration boundary โดยรักษา legacy CLI/output, assert frozen detector/FI hashes และ fail-before-detector เมื่อ sealed holdout preflight ไม่ผ่าน. การ execute holdout จริงยังต้อง approval แยก.

## Validation boundary

A0 อนุญาตเฉพาะ documentation reference checks, JSON parse, `git diff --check`, staged-file review และ prohibited-artifact checks. ห้าม invoke FI fixture harness, FJ/FQ runners, evaluator หรือ artifact generation workflow ใด ๆ.

Semantic risks: detector/FI files = CRITICAL/FROZEN; source integrity, canonical hash, classification, fail-closed, symbol/timeframe, preflight = HIGH; provenance/summary projection = MEDIUM; non-semantic CLI plumbing = LOW.

## References

- `AGENTS.md`; `docs/ai/current-status.md`
- `docs/182_Checkpoint_FI_Deterministic_Detector_Implementation_and_Fixture_Validation_TH.md`
- `docs/183_Checkpoint_FJ_Frozen_Historical_Event_Population_Generation_TH.md`
- `docs/189_Checkpoint_FP_New_Evidence_Boundary_and_Holdout_Eligibility_TH.md`
- `docs/190_Checkpoint_FQ_Historical_Holdout_Data_Quality_TH.md`
- matching FI/FJ/FP/FQ documents under `docs/ai/tasks/`
- `tools/run_checkpoint_fj_historical_event_population.py`
- `tools/market_structure_break_retest_detector.py`
- `tools/run_checkpoint_fq_holdout_gap_boundary.py`
- `research/contracts/checkpoint_fp_new_evidence_boundary_contract.json`
- `research/results/checkpoint_fp_evidence_boundary/checkpoint_fp_source_provenance.json`
- `research/results/checkpoint_fj_historical_event_population/checkpoint_fj_source_manifest.json`
- `research/results/checkpoint_fq_holdout_gap_boundary/checkpoint_fq_source_integrity.json`
- `research/results/checkpoint_fq_holdout_gap_boundary/checkpoint_fq_gap_inventory.json`
- `research/results/checkpoint_eo_gap_policy_review/gap_policy_dry_run.csv`

## Status

- execution status: `PASS` สำหรับ documentation/code-location analysis เท่านั้น
- strategy performance: `NOT_EVALUATED`
- profitability: `NOT_CLAIMED`
- order logic: `NOT_APPROVED`
- candidate: `NOT_READY_FOR_ORDER_LOGIC`
- detector/events/outcomes/holdout preflight: `NOT_RUN`
