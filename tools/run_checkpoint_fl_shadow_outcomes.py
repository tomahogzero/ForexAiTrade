#!/usr/bin/env python3
"""FL frozen shadow-outcome evaluator. Diagnostic labels only; no trade execution or P/L."""
from __future__ import annotations
import argparse, csv, hashlib, json, math
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from decimal import Decimal
from pathlib import Path

EXPECTED_SOURCE_HASHES = {
    "GOLD#_H1_202301030100_202312292300.csv": "bbe0c3b83439dbd223ff64f4e6fa75af84981befff3482cb00161936b56bd468",
    "GOLD#_H1_202401020100_202412312000.csv": "883f5076cdc6ef6c30caf8e995dd7e33f63e7f50e9e2a9f91f77d206ffbd4f0a",
    "GOLD#_H1_202501020800_202512311900.csv": "368ce15fa4225c14bc1513d108ec75d1ab49274b82208b36de03b1cbdc92195b",
}
REQUIRED_EVENT_FIELDS = {"event_id", "symbol", "timeframe", "direction", "confirmation_timestamp", "entry_reference_price", "atr", "year", "source_row_keys"}


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical(value) -> bytes:
    return json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode("ascii")


def decimal_text(value: Decimal) -> str:
    return format(value.normalize(), "f")


def close_timestamp(open_timestamp: str) -> str:
    return (datetime.fromisoformat(open_timestamp) + timedelta(hours=1)).isoformat()


def read_policy(path: Path) -> dict[str, dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return {row["next_time"]: row for row in csv.DictReader(handle)}


def read_bars(paths: list[Path], policy: dict[str, dict[str, str]]):
    bars, source_manifest = [], []
    required = {"<DATE>", "<TIME>", "<OPEN>", "<HIGH>", "<LOW>", "<CLOSE>"}
    for path in paths:
        expected = EXPECTED_SOURCE_HASHES.get(path.name)
        if expected is None or sha256_path(path) != expected:
            raise SystemExit(f"unapproved or changed raw source: {path.name}")
        with path.open(encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle, delimiter="\t")
            if reader.fieldnames is None or not required.issubset(reader.fieldnames):
                raise SystemExit(f"source schema mismatch: {path}")
            rows = list(reader)
        for line, row in enumerate(rows, start=2):
            timestamp = datetime.strptime(f"{row['<DATE>']} {row['<TIME>']}", "%Y.%m.%d %H:%M:%S").isoformat()
            bars.append({"timestamp": timestamp, "source_row_key": f"{path.name}:{line}", "open": Decimal(row["<OPEN>"]), "high": Decimal(row["<HIGH>"]), "low": Decimal(row["<LOW>"]), "close": Decimal(row["<CLOSE>"])})
        source_manifest.append({"file": path.name, "sha256": expected, "rows": len(rows)})
    bars.sort(key=lambda bar: (bar["timestamp"], bar["source_row_key"]))
    if len({bar["timestamp"] for bar in bars}) != len(bars):
        raise SystemExit("conflicting duplicate source timestamps")
    accepted = blocked = 0
    for previous, current in zip(bars, bars[1:]):
        previous_dt, current_dt = datetime.fromisoformat(previous["timestamp"]), datetime.fromisoformat(current["timestamp"])
        if current_dt - previous_dt <= timedelta(hours=1):
            continue
        policy_row = policy.get(current_dt.strftime("%Y-%m-%d %H:%M:%S"))
        classification = policy_row["policy_status"] if policy_row and policy_row["prev_time"] == previous_dt.strftime("%Y-%m-%d %H:%M:%S") else "BLOCKED_UNCLASSIFIED_GAP"
        if classification.startswith("ACCEPTED_"):
            accepted += 1
        else:
            blocked += 1
            current["blocked_gap_before"] = {"gap_start": previous_dt.isoformat(), "gap_end": current_dt.isoformat()}
    if accepted != 745 or blocked != 28:
        raise SystemExit(f"frozen gap policy mismatch accepted={accepted} blocked={blocked}")
    return bars, source_manifest, accepted, blocked


def read_events(path: Path, contract: dict):
    with path.open(encoding="utf-8", newline="") as handle:
        events = list(csv.DictReader(handle))
    if not events or not REQUIRED_EVENT_FIELDS.issubset(events[0]):
        raise SystemExit("FJ event schema mismatch")
    for event in events:
        event["source_row_keys"] = json.loads(event["source_row_keys"])
        if event.get("exclusion_reason") == "":
            event["exclusion_reason"] = None
    events.sort(key=lambda event: event["event_id"])
    source_hash = sha256_bytes(canonical(events))
    if source_hash != contract["source_population"]["event_population_sha256"]:
        raise SystemExit(f"FJ population SHA-256 mismatch: {source_hash}")
    if len(events) != 1079 or len({event["event_id"] for event in events}) != 1079:
        raise SystemExit("FJ event count or unique ID mismatch")
    if sum(event["direction"] == "LONG" for event in events) != 588 or sum(event["direction"] == "SHORT" for event in events) != 491:
        raise SystemExit("FJ direction count mismatch")
    return events, source_hash


def invalid_row(event, horizon, contract, source_hash, reason):
    return build_row(event, horizon, contract, source_hash, outcome="INVALID_EVENT_INPUT", evaluated=0, exclusion=reason)


def build_row(event, horizon, contract, source_hash, *, outcome, evaluated, tp=None, sl=None, touch_timestamp=None, touch_key=None, gap=None, exclusion=None):
    version = contract["contract_version"]
    event_id = event.get("event_id", "INVALID_EVENT")
    row = {
        "outcome_row_id": sha256_bytes(f"{event_id}|{horizon}|{version}".encode("utf-8")),
        "event_id": event_id, "symbol": event.get("symbol"), "timeframe": event.get("timeframe"), "direction": event.get("direction"),
        "confirmation_timestamp": event.get("confirmation_timestamp"), "entry_reference_price": event.get("entry_reference_price"), "atr": event.get("atr"),
        "tp_multiple": contract["levels"]["tp_multiple"], "sl_multiple": contract["levels"]["sl_multiple"],
        "tp_level": decimal_text(tp) if tp is not None else None, "sl_level": decimal_text(sl) if sl is not None else None,
        "horizon_bars": horizon, "evaluated_bar_count": evaluated, "first_touch_timestamp": touch_timestamp,
        "first_touch_bar_key": touch_key, "outcome": outcome, "gap_start": None if gap is None else gap["gap_start"],
        "gap_end": None if gap is None else gap["gap_end"], "eligibility_status": "ELIGIBLE" if outcome in {"TP_FIRST", "SL_FIRST", "AMBIGUOUS_SAME_BAR", "NO_RESOLUTION"} else "EXCLUDED",
        "exclusion_reason": exclusion, "source_population_hash": source_hash, "outcome_contract_version": version,
    }
    return row


def evaluate(event, horizon, bars, close_index, contract, source_hash):
    try:
        entry, atr = Decimal(event["entry_reference_price"]), Decimal(event["atr"])
        if not entry.is_finite() or not atr.is_finite() or atr <= 0 or event["direction"] not in {"LONG", "SHORT"}:
            raise ValueError("non-finite/inconsistent event input")
    except Exception as exc:
        return invalid_row(event, horizon, contract, source_hash, str(exc))
    index = close_index.get(event["confirmation_timestamp"])
    if index is None:
        return invalid_row(event, horizon, contract, source_hash, "confirmation_timestamp_not_found_in_source")
    if event["direction"] == "LONG":
        tp, sl = entry + Decimal("1.5") * atr, entry - atr
    else:
        tp, sl = entry - Decimal("1.5") * atr, entry + atr
    evaluated = 0
    for bar in bars[index + 1:]:
        gap = bar.get("blocked_gap_before")
        if gap:
            return build_row(event, horizon, contract, source_hash, outcome="DATA_INCOMPLETE_GAP", evaluated=evaluated, tp=tp, sl=sl, gap=gap, exclusion="DATA_INCOMPLETE_GAP")
        evaluated += 1
        if event["direction"] == "LONG":
            touches_tp, touches_sl = bar["high"] >= tp, bar["low"] <= sl
        else:
            touches_tp, touches_sl = bar["low"] <= tp, bar["high"] >= sl
        if touches_tp or touches_sl:
            outcome = "AMBIGUOUS_SAME_BAR" if touches_tp and touches_sl else ("TP_FIRST" if touches_tp else "SL_FIRST")
            return build_row(event, horizon, contract, source_hash, outcome=outcome, evaluated=evaluated, tp=tp, sl=sl, touch_timestamp=close_timestamp(bar["timestamp"]), touch_key=bar["source_row_key"])
        if evaluated == horizon:
            return build_row(event, horizon, contract, source_hash, outcome="NO_RESOLUTION", evaluated=evaluated, tp=tp, sl=sl)
    return build_row(event, horizon, contract, source_hash, outcome="INSUFFICIENT_FUTURE_BARS", evaluated=evaluated, tp=tp, sl=sl, exclusion="INSUFFICIENT_FUTURE_BARS")


def validate(rows, events, bars, contract, source_hash):
    expected = contract["canonical_output"]["expected_rows"]
    horizons = set(contract["horizons_bars"])
    event_ids = {event["event_id"] for event in events}
    if len(rows) != expected or len(rows) != len(events) * 4:
        raise SystemExit("canonical row count failure")
    pairs = [(row["event_id"], row["horizon_bars"]) for row in rows]
    if len(set(pairs)) != len(rows) or len({row["outcome_row_id"] for row in rows}) != len(rows):
        raise SystemExit("duplicate outcome pair/id")
    if {row["event_id"] for row in rows} != event_ids or any(row["horizon_bars"] not in horizons for row in rows):
        raise SystemExit("event conservation/horizon failure")
    source_keys = {bar["source_row_key"] for bar in bars}
    allowed = set(contract["outcomes"])
    for row in rows:
        if row["outcome"] not in allowed or row["source_population_hash"] != source_hash or row["outcome_contract_version"] != contract["contract_version"]:
            raise SystemExit("outcome/version/source hash failure")
        if row["first_touch_bar_key"] and row["first_touch_bar_key"] not in source_keys:
            raise SystemExit("unresolved first touch key")
        if row["eligibility_status"] == "EXCLUDED" and not row["exclusion_reason"]:
            raise SystemExit("missing exclusion reason")
    contradictions = []
    by_event = defaultdict(list)
    resolved = {"TP_FIRST", "SL_FIRST", "AMBIGUOUS_SAME_BAR"}
    for row in rows: by_event[row["event_id"]].append(row)
    for event_id, values in by_event.items():
        values.sort(key=lambda row: row["horizon_bars"])
        prior = None
        for row in values:
            if prior in resolved and row["outcome"] != prior:
                contradictions.append({"event_id": event_id, "earlier": prior, "later": row["outcome"], "horizon": row["horizon_bars"]})
            if row["outcome"] in resolved:
                prior = row["outcome"]
    if contradictions:
        raise SystemExit(f"monotonicity contradictions: {len(contradictions)}")
    return {"canonical_rows": len(rows), "event_key_conservation": f"{len(event_ids)}/{len(events)}", "duplicate_event_horizon_pairs": 0, "duplicate_outcome_row_ids": 0, "unknown_event_ids": 0, "unresolved_first_touch_keys": 0, "monotonicity_contradictions": 0}


def summaries(rows):
    result = {"by_horizon": {}, "by_direction": {}, "by_year": {}, "by_direction_year": {}}
    for horizon in (6, 12, 24, 48):
        selected = [row for row in rows if row["horizon_bars"] == horizon]
        counts = Counter(row["outcome"] for row in selected)
        result["by_horizon"][str(horizon)] = {"total": len(selected), "eligible_denominator": sum(row["eligibility_status"] == "ELIGIBLE" for row in selected), "excluded_denominator": sum(row["eligibility_status"] == "EXCLUDED" for row in selected), "outcomes": dict(sorted(counts.items()))}
    for dimension, key in (("by_direction", lambda row: row["direction"]), ("by_year", lambda row: row["confirmation_timestamp"][:4]), ("by_direction_year", lambda row: f"{row['direction']}|{row['confirmation_timestamp'][:4]}")):
        grouped = defaultdict(Counter)
        for row in rows: grouped[key(row)][row["outcome"]] += 1
        result[dimension] = {name: dict(sorted(counts.items())) for name, counts in sorted(grouped.items())}
    return result


def csv_bytes(rows, fields):
    import io
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    for row in rows: writer.writerow(row)
    return buffer.getvalue().encode("utf-8")


def run(paths, policy_path, event_path, contract_path):
    contract = json.loads(contract_path.read_text(encoding="utf-8"))
    if contract["contract_status"] != "FROZEN_NO_OUTCOMES_CALCULATED": raise SystemExit("unexpected FK contract status")
    events, source_hash = read_events(event_path, contract)
    bars, sources, accepted, blocked = read_bars(paths, read_policy(policy_path))
    close_index = {close_timestamp(bar["timestamp"]): index for index, bar in enumerate(bars)}
    if len(close_index) != len(bars): raise SystemExit("source close timestamp conflict")
    rows = [evaluate(event, horizon, bars, close_index, contract, source_hash) for event in events for horizon in contract["horizons_bars"]]
    rows.sort(key=lambda row: (row["event_id"], row["horizon_bars"]))
    integrity = validate(rows, events, bars, contract, source_hash)
    descriptive = summaries(rows)
    exclusions = [row for row in rows if row["eligibility_status"] == "EXCLUDED"]
    gap_exclusions = [row for row in exclusions if row["outcome"] == "DATA_INCOMPLETE_GAP"]
    summary = {"execution_status": "PASS", "decision": "FL_PASS_OUTCOME_POPULATION_GENERATED", "source_population_hash": source_hash, "contract_version": contract["contract_version"], "contract_sha256": sha256_path(contract_path), "source_rows": len(bars), "accepted_closures": accepted, "unverified_gaps": blocked, "broker_history_completeness": "NOT_PROVEN", "population": {"frozen_events": len(events), "canonical_rows": len(rows), "long_events": sum(event["direction"] == "LONG" for event in events), "short_events": sum(event["direction"] == "SHORT" for event in events)}, "descriptive_counts": descriptive, "integrity": integrity, "strategy_performance_status": "NOT_EVALUATED", "order_logic_status": "NOT_APPROVED", "candidate_status": "NOT_READY_FOR_ORDER_LOGIC", "profitability_claim": False}
    quality = {"execution_status": "PASS", "exclusions_by_outcome": dict(sorted(Counter(row["outcome"] for row in exclusions).items())), "gap_exclusions": len(gap_exclusions), "gap_records": [{"event_id": row["event_id"], "horizon_bars": row["horizon_bars"], "gap_start": row["gap_start"], "gap_end": row["gap_end"], "evaluated_bar_count": row["evaluated_bar_count"]} for row in gap_exclusions], "broker_history_completeness": "NOT_PROVEN"}
    consistency = {"execution_status": "PASS", "monotonicity_contradictions": 0, "rules": contract["integrity"]["monotonicity"]}
    manifest = {"execution_status": "PASS", "sources": sources, "event_population_sha256": source_hash, "fk_contract_sha256": sha256_path(contract_path), "fk_contract_version": contract["contract_version"], "raw_broker_csv_committed": False}
    integrity_report = {"execution_status": "PASS", "preflight": {"frozen_events": len(events), "long_events": sum(event["direction"] == "LONG" for event in events), "short_events": sum(event["direction"] == "SHORT" for event in events), "source_population_hash": source_hash, "contract_version": contract["contract_version"]}, "integrity": integrity}
    direction_year_integrity = {"execution_status": "PASS", "descriptive_counts_by_direction": descriptive["by_direction"], "descriptive_counts_by_year": descriptive["by_year"], "descriptive_counts_by_direction_year": descriptive["by_direction_year"]}
    return rows, summary, quality, consistency, manifest, integrity_report, direction_year_integrity


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", action="append", required=True); parser.add_argument("--gap-policy", required=True); parser.add_argument("--events", required=True); parser.add_argument("--contract", required=True); parser.add_argument("--output-root", required=True)
    args = parser.parse_args(); paths = [Path(value) for value in args.source]
    first = run(paths, Path(args.gap_policy), Path(args.events), Path(args.contract)); second = run(paths, Path(args.gap_policy), Path(args.events), Path(args.contract))
    if canonical(first) != canonical(second): raise SystemExit("deterministic replay mismatch")
    rows, summary, quality, consistency, manifest, integrity_report, direction_year_integrity = first; fields = json.loads(Path(args.contract).read_text(encoding="utf-8"))["canonical_output"]["fields"]
    output = Path(args.output_root); output.mkdir(parents=True, exist_ok=True)
    csv_output = csv_bytes(rows, fields); (output / "checkpoint_fl_canonical_outcomes.csv").write_bytes(csv_output)
    (output / "checkpoint_fl_population_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (output / "checkpoint_fl_data_quality.json").write_text(json.dumps(quality, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (output / "checkpoint_fl_horizon_consistency.json").write_text(json.dumps(consistency, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (output / "checkpoint_fl_integrity_report.json").write_text(json.dumps(integrity_report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (output / "checkpoint_fl_direction_year_integrity.json").write_text(json.dumps(direction_year_integrity, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (output / "checkpoint_fl_sha256_manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    replay = {"execution_status": "PASS", "byte_identical": True, "mismatch_count": 0, "canonical_outcome_csv_sha256": sha256_bytes(csv_output), "population_summary_sha256": sha256_bytes(canonical(summary)), "data_quality_exclusions_sha256": sha256_bytes(canonical(quality)), "integrity_report_sha256": sha256_bytes(canonical(integrity_report)), "row_order_frozen": True}
    (output / "checkpoint_fl_deterministic_replay.json").write_text(json.dumps(replay, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"summary": summary, "replay": replay}, indent=2, sort_keys=True))

if __name__ == "__main__": main()