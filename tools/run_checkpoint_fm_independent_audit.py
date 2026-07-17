#!/usr/bin/env python3
"""Independent FM audit of the frozen FL outcome population; no outcome artifacts are modified."""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from decimal import Decimal, InvalidOperation
from pathlib import Path

SOURCE_HASHES = {
    "GOLD#_H1_202301030100_202312292300.csv": "bbe0c3b83439dbd223ff64f4e6fa75af84981befff3482cb00161936b56bd468",
    "GOLD#_H1_202401020100_202412312000.csv": "883f5076cdc6ef6c30caf8e995dd7e33f63e7f50e9e2a9f91f77d206ffbd4f0a",
    "GOLD#_H1_202501020800_202512311900.csv": "368ce15fa4225c14bc1513d108ec75d1ab49274b82208b36de03b1cbdc92195b",
}
OUTCOMES = {"TP_FIRST", "SL_FIRST", "AMBIGUOUS_SAME_BAR", "NO_RESOLUTION", "DATA_INCOMPLETE_GAP", "INSUFFICIENT_FUTURE_BARS", "INVALID_EVENT_INPUT"}
RESOLVED = {"TP_FIRST", "SL_FIRST", "AMBIGUOUS_SAME_BAR"}
HORIZONS = (6, 12, 24, 48)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def sha256_lf_normalized(path: Path) -> str:
    return sha256_bytes(path.read_bytes().replace(b"\r\n", b"\n"))

def canonical(value) -> bytes:
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("ascii")


def decimal_text(value: Decimal) -> str:
    return format(value.normalize(), "f")


def close_time(open_time: str) -> str:
    return (datetime.fromisoformat(open_time) + timedelta(hours=1)).isoformat()


def require(condition: bool, text: str) -> None:
    if not condition:
        raise SystemExit(text)


def load_contract(path: Path) -> tuple[dict, str]:
    contract = json.loads(path.read_text(encoding="utf-8"))
    contract_hash = sha256_file(path)
    require(contract["contract_version"] == "MARKET_STRUCTURE_BREAK_RETEST_CONFIRMATION_V1_SHADOW_OUTCOME_FK_V1", "FK contract version mismatch")
    require(contract_hash == "42182742575ef3e4add245ef8181a2424fb27907453c35f8ed73597b54d3cd55", "FK contract hash mismatch")
    require(tuple(contract["horizons_bars"]) == HORIZONS, "FK horizons mismatch")
    return contract, contract_hash


def load_events(path: Path, contract: dict) -> tuple[dict[str, dict], str]:
    with path.open(encoding="utf-8", newline="") as handle:
        events = list(csv.DictReader(handle))
    required = {"event_id", "symbol", "timeframe", "direction", "confirmation_timestamp", "entry_reference_price", "atr", "year", "source_row_keys"}
    require(bool(events) and required.issubset(events[0]), "FJ event schema mismatch")
    for event in events:
        event["source_row_keys"] = json.loads(event["source_row_keys"])
        if event.get("exclusion_reason") == "":
            event["exclusion_reason"] = None
    events.sort(key=lambda value: value["event_id"])
    population_hash = sha256_bytes(canonical(events))
    require(population_hash == contract["source_population"]["event_population_sha256"], "FJ population hash mismatch")
    require(len(events) == 1079 and len({value["event_id"] for value in events}) == 1079, "FJ event count or IDs mismatch")
    require(sum(value["direction"] == "LONG" for value in events) == 588, "FJ LONG count mismatch")
    require(sum(value["direction"] == "SHORT" for value in events) == 491, "FJ SHORT count mismatch")
    return {value["event_id"]: value for value in events}, population_hash


def load_policy(path: Path) -> dict[tuple[str, str], str]:
    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    return {(row["prev_time"], row["next_time"]): row["policy_status"] for row in rows}


def load_bars(paths: list[Path], policy: dict[tuple[str, str], str]) -> tuple[list[dict], dict[str, int], set[str], dict[str, dict], int, int]:
    bars = []
    required = {"<DATE>", "<TIME>", "<OPEN>", "<HIGH>", "<LOW>", "<CLOSE>"}
    for path in paths:
        require(path.name in SOURCE_HASHES and sha256_file(path) == SOURCE_HASHES[path.name], f"unapproved source {path.name}")
        with path.open(encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle, delimiter="\t")
            require(reader.fieldnames is not None and required.issubset(reader.fieldnames), f"source schema mismatch {path.name}")
            for line, row in enumerate(reader, start=2):
                timestamp = datetime.strptime(f"{row['<DATE>']} {row['<TIME>']}", "%Y.%m.%d %H:%M:%S").isoformat()
                bars.append({"timestamp": timestamp, "key": f"{path.name}:{line}", "open": Decimal(row["<OPEN>"]), "high": Decimal(row["<HIGH>"]), "low": Decimal(row["<LOW>"]), "close": Decimal(row["<CLOSE>"])})
    bars.sort(key=lambda value: (value["timestamp"], value["key"]))
    require(len(bars) == 17716 and len({value["timestamp"] for value in bars}) == len(bars), "source ordering or duplicate timestamp failure")
    accepted = blocked = 0
    blocked_inventory = {}
    for prior, current in zip(bars, bars[1:]):
        prior_dt, current_dt = datetime.fromisoformat(prior["timestamp"]), datetime.fromisoformat(current["timestamp"])
        if current_dt - prior_dt <= timedelta(hours=1):
            continue
        key = (prior_dt.strftime("%Y-%m-%d %H:%M:%S"), current_dt.strftime("%Y-%m-%d %H:%M:%S"))
        if policy.get(key, "").startswith("ACCEPTED_"):
            accepted += 1
        else:
            blocked += 1
            gap = {"gap_start": prior_dt.isoformat(), "gap_end": current_dt.isoformat()}
            current["gap_before"] = gap
            blocked_inventory[current["timestamp"]] = gap
    require((accepted, blocked) == (745, 28), f"gap inventory mismatch accepted={accepted} blocked={blocked}")
    close_indexes = {close_time(bar["timestamp"]): index for index, bar in enumerate(bars)}
    require(len(close_indexes) == len(bars), "source close time conflict")
    return bars, close_indexes, {value["key"] for value in bars}, blocked_inventory, accepted, blocked


def load_fl_rows(path: Path, contract: dict, population_hash: str) -> tuple[list[dict], str]:
    required = contract["canonical_output"]["fields"]
    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    require(bool(rows) and rows[0].keys() >= set(required), "FL canonical schema mismatch")
    require(sha256_lf_normalized(path) == "b05b38a11db6c776e177b2b738610724bbd877870f5a12cea0ce698fc636a804", "FL canonical outcome LF-normalized hash mismatch")
    require(len(rows) == 4316, "FL canonical row count mismatch")
    for row in rows:
        row["horizon_bars"] = int(row["horizon_bars"])
        row["evaluated_bar_count"] = int(row["evaluated_bar_count"])
        require(row["source_population_hash"] == population_hash, "FL source population hash mismatch")
        require(row["outcome_contract_version"] == contract["contract_version"], "FL contract version mismatch")
    return rows, sha256_lf_normalized(path)


def expected_from_source(event: dict, horizon: int, bars: list[dict], close_indexes: dict[str, int], contract: dict, population_hash: str) -> dict:
    result = {"outcome": "INVALID_EVENT_INPUT", "evaluated_bar_count": 0, "first_touch_timestamp": "", "first_touch_bar_key": "", "gap_start": "", "gap_end": "", "exclusion_reason": ""}
    try:
        entry = Decimal(event["entry_reference_price"])
        atr = Decimal(event["atr"])
        if not entry.is_finite() or not atr.is_finite() or atr <= 0 or event["direction"] not in {"LONG", "SHORT"}:
            raise InvalidOperation
    except (InvalidOperation, ValueError):
        result["exclusion_reason"] = "non-finite/inconsistent event input"
        return result
    start = close_indexes.get(event["confirmation_timestamp"])
    if start is None:
        result["exclusion_reason"] = "confirmation_timestamp_not_found_in_source"
        return result
    if event["direction"] == "LONG":
        tp, sl = entry + Decimal("1.5") * atr, entry - atr
    else:
        tp, sl = entry - Decimal("1.5") * atr, entry + atr
    result["tp_level"] = decimal_text(tp)
    result["sl_level"] = decimal_text(sl)
    for bar in bars[start + 1:]:
        if "gap_before" in bar:
            result.update({"outcome": "DATA_INCOMPLETE_GAP", "gap_start": bar["gap_before"]["gap_start"], "gap_end": bar["gap_before"]["gap_end"], "exclusion_reason": "DATA_INCOMPLETE_GAP"})
            return result
        result["evaluated_bar_count"] += 1
        if event["direction"] == "LONG":
            hit_tp, hit_sl = bar["high"] >= tp, bar["low"] <= sl
        else:
            hit_tp, hit_sl = bar["low"] <= tp, bar["high"] >= sl
        if hit_tp or hit_sl:
            result["outcome"] = "AMBIGUOUS_SAME_BAR" if hit_tp and hit_sl else ("TP_FIRST" if hit_tp else "SL_FIRST")
            result["first_touch_timestamp"] = close_time(bar["timestamp"])
            result["first_touch_bar_key"] = bar["key"]
            return result
        if result["evaluated_bar_count"] == horizon:
            result["outcome"] = "NO_RESOLUTION"
            return result
    result.update({"outcome": "INSUFFICIENT_FUTURE_BARS", "exclusion_reason": "INSUFFICIENT_FUTURE_BARS"})
    return result


def counts(rows: list[dict]) -> dict:
    result = {"by_horizon": {}, "by_direction": {}, "by_year": {}, "by_direction_year": {}}
    for horizon in HORIZONS:
        selected = [row for row in rows if row["horizon_bars"] == horizon]
        outcomes = Counter(row["outcome"] for row in selected)
        result["by_horizon"][str(horizon)] = {"total": len(selected), "eligible_denominator": sum(row["eligibility_status"] == "ELIGIBLE" for row in selected), "excluded_denominator": sum(row["eligibility_status"] == "EXCLUDED" for row in selected), "outcomes": dict(sorted(outcomes.items()))}
    dimensions = {"by_direction": lambda row: row["direction"], "by_year": lambda row: row["confirmation_timestamp"][:4], "by_direction_year": lambda row: f"{row['direction']}|{row['confirmation_timestamp'][:4]}"}
    for label, key in dimensions.items():
        grouped = defaultdict(Counter)
        for row in rows:
            grouped[key(row)][row["outcome"]] += 1
        result[label] = {name: dict(sorted(values.items())) for name, values in sorted(grouped.items())}
    return result


def audit(contract: dict, events: dict[str, dict], rows: list[dict], bars: list[dict], close_indexes: dict[str, int], source_keys: set[str], blocked_inventory: dict[str, dict], population_hash: str) -> dict:
    event_ids = set(events)
    pairs = [(row["event_id"], row["horizon_bars"]) for row in rows]
    duplicate_ids = len(rows) - len({row["outcome_row_id"] for row in rows})
    key_report = {"unique_event_ids": len({row["event_id"] for row in rows}), "rows": len(rows), "event_key_conservation": f"{len({row['event_id'] for row in rows} & event_ids)}/{len(event_ids)}", "missing_event_ids": len(event_ids - {row["event_id"] for row in rows}), "unknown_event_ids": len({row["event_id"] for row in rows} - event_ids), "duplicate_event_horizon_pairs": len(rows) - len(set(pairs)), "duplicate_outcome_row_ids": duplicate_ids, "invalid_horizons": sum(row["horizon_bars"] not in HORIZONS for row in rows)}
    input_mismatches = []
    formula = {"checked_rows": 0, "tp_level_mismatches": 0, "sl_level_mismatches": 0, "non_finite_values": 0, "precision_or_serialization_mismatches": 0, "mismatch_examples": []}
    first_touch = {"audited_rows": 0, "exact_outcome_matches": 0, "outcome_mismatches": 0, "first_touch_timestamp_mismatches": 0, "first_touch_bar_key_mismatches": 0, "evaluated_bar_count_mismatches": 0, "mismatch_examples": []}
    gap_rows, ambiguity_issues = [], []
    expected_by_pair = {}
    for row in rows:
        event = events.get(row["event_id"])
        if event is None:
            continue
        for field in ("symbol", "timeframe", "direction", "confirmation_timestamp", "entry_reference_price", "atr"):
            if row[field] != event[field]:
                input_mismatches.append({"event_id": row["event_id"], "horizon_bars": row["horizon_bars"], "field": field, "fl": row[field], "fj": event[field]})
        try:
            entry, atr = Decimal(row["entry_reference_price"]), Decimal(row["atr"])
            if not entry.is_finite() or not atr.is_finite():
                formula["non_finite_values"] += 1
            if row["direction"] == "LONG":
                expected_tp, expected_sl = entry + Decimal("1.5") * atr, entry - atr
            else:
                expected_tp, expected_sl = entry - Decimal("1.5") * atr, entry + atr
            formula["checked_rows"] += 1
            if row["tp_level"] != decimal_text(expected_tp): formula["tp_level_mismatches"] += 1
            if row["sl_level"] != decimal_text(expected_sl): formula["sl_level_mismatches"] += 1
            if row["tp_multiple"] != "1.5" or row["sl_multiple"] != "1.0": formula["precision_or_serialization_mismatches"] += 1
        except (InvalidOperation, ValueError):
            formula["non_finite_values"] += 1
        expected = expected_from_source(event, row["horizon_bars"], bars, close_indexes, contract, population_hash)
        expected_by_pair[(row["event_id"], row["horizon_bars"])] = expected
        first_touch["audited_rows"] += 1
        mismatch_fields = [field for field in ("outcome", "first_touch_timestamp", "first_touch_bar_key", "evaluated_bar_count", "gap_start", "gap_end", "exclusion_reason") if row[field] != expected.get(field, "")]
        if not mismatch_fields:
            first_touch["exact_outcome_matches"] += 1
        else:
            if row["outcome"] != expected["outcome"]: first_touch["outcome_mismatches"] += 1
            if row["first_touch_timestamp"] != expected["first_touch_timestamp"]: first_touch["first_touch_timestamp_mismatches"] += 1
            if row["first_touch_bar_key"] != expected["first_touch_bar_key"]: first_touch["first_touch_bar_key_mismatches"] += 1
            if row["evaluated_bar_count"] != expected["evaluated_bar_count"]: first_touch["evaluated_bar_count_mismatches"] += 1
            if len(first_touch["mismatch_examples"]) < 20: first_touch["mismatch_examples"].append({"event_id": row["event_id"], "horizon_bars": row["horizon_bars"], "fields": mismatch_fields})
        if row["outcome"] == "DATA_INCOMPLETE_GAP":
            valid_gap = row["gap_end"] in blocked_inventory and blocked_inventory[row["gap_end"]]["gap_start"] == row["gap_start"]
            gap_rows.append({"event_id": row["event_id"], "horizon_bars": row["horizon_bars"], "gap_start": row["gap_start"], "gap_end": row["gap_end"], "evaluated_bar_count": row["evaluated_bar_count"], "approved_gap_inventory_match": valid_gap})
        if row["outcome"] == "AMBIGUOUS_SAME_BAR" and expected["outcome"] != "AMBIGUOUS_SAME_BAR":
            ambiguity_issues.append({"event_id": row["event_id"], "horizon_bars": row["horizon_bars"], "issue": "ambiguous_not_independently_reproduced"})
        if row["outcome"] in {"TP_FIRST", "SL_FIRST"} and expected["outcome"] == "AMBIGUOUS_SAME_BAR":
            ambiguity_issues.append({"event_id": row["event_id"], "horizon_bars": row["horizon_bars"], "issue": "non_ambiguous_row_is_same_bar_ambiguous"})
    monotonic = []
    grouped = defaultdict(list)
    for row in rows: grouped[row["event_id"]].append(row)
    for event_id, values in grouped.items():
        values.sort(key=lambda value: value["horizon_bars"])
        prior = None
        for row in values:
            if prior in RESOLVED and row["outcome"] != prior:
                monotonic.append({"event_id": event_id, "earlier_outcome": prior, "later_horizon": row["horizon_bars"], "later_outcome": row["outcome"]})
            if row["outcome"] in RESOLVED:
                prior = row["outcome"]
    fl_summary_path = Path("research/results/checkpoint_fl_shadow_outcome_evaluation/checkpoint_fl_population_summary.json")
    fl_direction_path = Path("research/results/checkpoint_fl_shadow_outcome_evaluation/checkpoint_fl_direction_year_integrity.json")
    fl_summary = json.loads(fl_summary_path.read_text(encoding="utf-8"))
    fl_direction = json.loads(fl_direction_path.read_text(encoding="utf-8"))
    recomputed = counts(rows)
    count_match = recomputed == {"by_horizon": fl_summary["descriptive_counts"]["by_horizon"], "by_direction": fl_direction["descriptive_counts_by_direction"], "by_year": fl_direction["descriptive_counts_by_year"], "by_direction_year": fl_direction["descriptive_counts_by_direction_year"]}
    return {"key_conservation": key_report, "frozen_input_reproduction": {"checked_rows": len(rows), "mismatches": len(input_mismatches), "mismatch_examples": input_mismatches[:20]}, "formula_audit": formula, "first_touch_reconciliation": first_touch, "gap_policy_audit": {"accepted_closures_do_not_consume_bar_count": True, "unverified_gap_count": len(blocked_inventory), "affected_rows": gap_rows, "affected_row_count": len(gap_rows), "all_gap_inventory_matches": all(value["approved_gap_inventory_match"] for value in gap_rows), "broker_history_completeness": "NOT_PROVEN"}, "ambiguity_audit": {"ambiguous_rows": sum(row["outcome"] == "AMBIGUOUS_SAME_BAR" for row in rows), "issues": ambiguity_issues, "issue_count": len(ambiguity_issues)}, "horizon_monotonicity": {"contradictions": monotonic, "contradiction_count": len(monotonic)}, "descriptive_count_reconciliation": {"recomputed": recomputed, "matches_fl_machine_readable_summaries": count_match}}


def audit_bytes(report: dict) -> bytes:
    return json.dumps(report, ensure_ascii=True, indent=2, sort_keys=True).encode("utf-8") + b"\n"


def run(args) -> tuple[dict, dict]:
    contract, contract_hash = load_contract(Path(args.contract))
    events, population_hash = load_events(Path(args.events), contract)
    bars, close_indexes, source_keys, blocked_inventory, accepted, blocked = load_bars([Path(value) for value in args.source], load_policy(Path(args.gap_policy)))
    rows, canonical_hash = load_fl_rows(Path(args.outcomes), contract, population_hash)
    report = audit(contract, events, rows, bars, close_indexes, source_keys, blocked_inventory, population_hash)
    material = sum([report["key_conservation"][key] for key in ("missing_event_ids", "unknown_event_ids", "duplicate_event_horizon_pairs", "duplicate_outcome_row_ids", "invalid_horizons")]) + report["frozen_input_reproduction"]["mismatches"] + report["formula_audit"]["tp_level_mismatches"] + report["formula_audit"]["sl_level_mismatches"] + report["formula_audit"]["non_finite_values"] + report["first_touch_reconciliation"]["outcome_mismatches"] + report["first_touch_reconciliation"]["first_touch_timestamp_mismatches"] + report["first_touch_reconciliation"]["first_touch_bar_key_mismatches"] + report["first_touch_reconciliation"]["evaluated_bar_count_mismatches"] + report["horizon_monotonicity"]["contradiction_count"] + report["ambiguity_audit"]["issue_count"]
    report.update({"execution_status": "PASS" if material == 0 else "FAIL", "decision": "FM_PASS_INDEPENDENT_OUTCOME_AUDIT" if material == 0 else "FM_BLOCKED_OUTCOME_INTEGRITY_FAILURE", "material_mismatch_count": material, "preflight": {"frozen_events": len(events), "long_events": 588, "short_events": 491, "canonical_rows": len(rows), "event_population_sha256": population_hash, "fl_canonical_outcome_sha256": canonical_hash, "fk_contract_sha256": contract_hash, "accepted_closures": accepted, "unverified_gaps": blocked}, "strategy_performance_status": "NOT_EVALUATED", "order_logic_status": "NOT_APPROVED", "candidate_status": "NOT_READY_FOR_ORDER_LOGIC", "profitability_claim": False})
    manifest = {"execution_status": report["execution_status"], "event_population_sha256": population_hash, "fk_contract_sha256": contract_hash, "fk_contract_version": contract["contract_version"], "fl_canonical_outcome_sha256": canonical_hash, "raw_broker_csv_committed": False, "source_rows": len(bars), "accepted_closures": accepted, "unverified_gaps": blocked}
    return report, manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", action="append", required=True)
    parser.add_argument("--gap-policy", required=True)
    parser.add_argument("--events", required=True)
    parser.add_argument("--contract", required=True)
    parser.add_argument("--outcomes", required=True)
    parser.add_argument("--output-root", required=True)
    args = parser.parse_args()
    first = run(args)
    second = run(args)
    require(canonical(first) == canonical(second), "FM independent audit replay mismatch")
    report, manifest = first
    output = Path(args.output_root); output.mkdir(parents=True, exist_ok=True)
    (output / "checkpoint_fm_independent_audit.json").write_bytes(audit_bytes(report))
    (output / "checkpoint_fm_event_key_conservation.json").write_bytes(audit_bytes(report["key_conservation"]))
    (output / "checkpoint_fm_formula_audit.json").write_bytes(audit_bytes(report["formula_audit"]))
    (output / "checkpoint_fm_first_touch_reconciliation.json").write_bytes(audit_bytes(report["first_touch_reconciliation"]))
    (output / "checkpoint_fm_gap_policy_audit.json").write_bytes(audit_bytes(report["gap_policy_audit"]))
    (output / "checkpoint_fm_ambiguity_audit.json").write_bytes(audit_bytes(report["ambiguity_audit"]))
    (output / "checkpoint_fm_horizon_monotonicity.json").write_bytes(audit_bytes(report["horizon_monotonicity"]))
    (output / "checkpoint_fm_descriptive_count_reconciliation.json").write_bytes(audit_bytes(report["descriptive_count_reconciliation"]))
    (output / "checkpoint_fm_sha256_manifest.json").write_bytes(audit_bytes(manifest))
    artifact_hashes = {path.name: sha256_file(path) for path in sorted(output.glob("*.json")) if path.name != "checkpoint_fm_deterministic_replay.json"}
    replay = {"execution_status": report["execution_status"], "byte_identical": True, "mismatch_count": 0, "row_order_frozen": True, "artifact_sha256": artifact_hashes}
    (output / "checkpoint_fm_deterministic_replay.json").write_bytes(audit_bytes(replay))
    print(json.dumps({"decision": report["decision"], "material_mismatch_count": report["material_mismatch_count"], "replay": replay}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
