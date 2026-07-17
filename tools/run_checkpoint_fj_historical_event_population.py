#!/usr/bin/env python3
"""FJ frozen historical event-population runner. No TP/SL or trade execution."""
from __future__ import annotations
import argparse, csv, hashlib, json, math
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from market_structure_break_retest_detector import EVENT_SCHEMA, detect

REQUIRED = ("<DATE>", "<TIME>", "<OPEN>", "<HIGH>", "<LOW>", "<CLOSE>")
EXPECTED_SHA256 = {
    "GOLD#_H1_202301030100_202312292300.csv": "bbe0c3b83439dbd223ff64f4e6fa75af84981befff3482cb00161936b56bd468",
    "GOLD#_H1_202401020100_202412312000.csv": "883f5076cdc6ef6c30caf8e995dd7e33f63e7f50e9e2a9f91f77d206ffbd4f0a",
    "GOLD#_H1_202501020800_202512311900.csv": "368ce15fa4225c14bc1513d108ec75d1ab49274b82208b36de03b1cbdc92195b",
}

def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical(value) -> bytes:
    return json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode("ascii")


def digest(value) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def read_policy(path: Path) -> dict[str, dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return {row["next_time"]: row for row in csv.DictReader(handle)}


def read_sources(paths: list[Path], policy: dict[str, dict[str, str]]):
    bars, provenance = [], []
    for path in paths:
        if path.name not in EXPECTED_SHA256:
            raise SystemExit(f"unapproved source filename: {path.name}")
        with path.open(encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle, delimiter="\t")
            if reader.fieldnames is None or not set(REQUIRED).issubset(reader.fieldnames):
                raise SystemExit(f"schema mismatch: {path}")
            rows = list(reader)
        if not rows:
            raise SystemExit(f"empty source: {path}")
        timestamps = []
        for index, row in enumerate(rows, start=2):
            stamp = datetime.strptime(f"{row['<DATE>']} {row['<TIME>']}", "%Y.%m.%d %H:%M:%S")
            timestamps.append(stamp)
            bars.append({"timestamp": stamp.isoformat(), "source_row_key": f"{path.name}:{index}", "open": row["<OPEN>"], "high": row["<HIGH>"], "low": row["<LOW>"], "close": row["<CLOSE>"]})
        source_hash = sha256_path(path)
        if source_hash != EXPECTED_SHA256[path.name]:
            raise SystemExit(f"source SHA-256 mismatch: {path.name}")
        provenance.append({"path": str(path.resolve()), "file": path.name, "size_bytes": path.stat().st_size, "sha256": source_hash, "row_count": len(rows), "first_timestamp": timestamps[0].isoformat(sep=" "), "last_timestamp": timestamps[-1].isoformat(sep=" ")})
    bars.sort(key=lambda bar: (bar["timestamp"], bar["source_row_key"]))
    timestamp_counts = Counter(bar["timestamp"] for bar in bars)
    duplicates = sorted(timestamp for timestamp, count in timestamp_counts.items() if count > 1)
    if duplicates:
        raise SystemExit(f"duplicate source timestamps: {len(duplicates)}")
    gaps, accepted, blocked = [], 0, 0
    for previous, current in zip(bars, bars[1:]):
        previous_time = datetime.fromisoformat(previous["timestamp"])
        current_time = datetime.fromisoformat(current["timestamp"])
        if (current_time - previous_time).total_seconds() <= 3600:
            continue
        policy_row = policy.get(current_time.strftime("%Y-%m-%d %H:%M:%S"))
        if policy_row is None or policy_row["prev_time"] != previous_time.strftime("%Y-%m-%d %H:%M:%S"):
            classification = "BLOCKED_UNCLASSIFIED_GAP"
        else:
            classification = policy_row["policy_status"]
        gap = {"gap_start": previous_time.isoformat(sep=" "), "gap_end": current_time.isoformat(sep=" "), "classification": classification}
        gaps.append(gap)
        if classification.startswith("ACCEPTED_"):
            accepted += 1
        else:
            blocked += 1
            current["gap_before"] = True
            current["gap_details"] = gap
    if accepted != 745 or blocked != 28:
        raise SystemExit(f"frozen gap policy mismatch: accepted={accepted} blocked={blocked}")
    return bars, provenance, gaps, accepted, blocked


def normalize_terminals(terminals, bars):
    gap_by_end = {bar["timestamp"]: bar.get("gap_details") for bar in bars if bar.get("gap_details")}
    output = []
    for item in terminals:
        row = {"status": item["status"], "state": item["state"], "candidate_id": item.get("candidate_id"), "event_id": item.get("event_id"), "swing_id": item.get("swing_id"), "duplicate_timestamp": item.get("duplicate_timestamp"), "gap_timestamp": item.get("gap_timestamp"), "gap_start": None, "gap_end": None, "direction": None, "affected_break_or_swing_id": item.get("candidate_id") or item.get("swing_id"), "exclusion_reason": None if item["status"] == "EVENT_EMITTED" else item["status"]}
        details = gap_by_end.get(item.get("gap_timestamp"))
        if details:
            row["gap_start"], row["gap_end"] = details["gap_start"], details["gap_end"]
        output.append(row)
    return sorted(output, key=lambda row: tuple("" if value is None else str(value) for value in row.values()))


def validate(events, terminals, source_keys):
    ids = [event["event_id"] for event in events]
    if len(ids) != len(set(ids)):
        raise SystemExit("duplicate event_id")
    semantic = [(event["direction"], event["swing_timestamp"], event["break_timestamp"], event["confirmation_timestamp"]) for event in events]
    if len(semantic) != len(set(semantic)):
        raise SystemExit("duplicate semantic event")
    for event in events:
        if list(event) != EVENT_SCHEMA or event["direction"] not in {"LONG", "SHORT"}:
            raise SystemExit("event schema/direction failure")
        if not (event["swing_timestamp"] <= event["swing_confirmation_timestamp"] < event["break_timestamp"] < event["retest_timestamp"] <= event["confirmation_timestamp"]):
            raise SystemExit("event timestamp ordering failure")
        if event["entry_reference_price"] != event["confirmation_close"] or not math.isfinite(float(event["atr"])):
            raise SystemExit("entry/ATR integrity failure")
        if any(key not in source_keys for key in event["source_row_keys"]):
            raise SystemExit("unresolved source_row_key")
    return {"unique_event_ids": len(ids), "duplicate_semantic_events": 0, "unresolved_source_row_keys": 0}


def generate(paths, policy_path):
    policy = read_policy(policy_path)
    bars, provenance, gaps, accepted, blocked = read_sources(paths, policy)
    result = detect(bars, symbol="GOLD#", timeframe="H1")
    events = result["events"]
    terminals = normalize_terminals(result["terminals"], bars)
    integrity = validate(events, terminals, {bar["source_row_key"] for bar in bars})
    status_counts = Counter(item["status"] for item in terminals)
    years = Counter(event["year"] for event in events)
    direction_years = {direction: dict(sorted(Counter(event["year"] for event in events if event["direction"] == direction).items())) for direction in ("LONG", "SHORT")}
    exclusions = [item for item in terminals if item["status"] != "EVENT_EMITTED"]
    summary = {"execution_status": "PASS", "decision": "FJ_PASS_POPULATION_GENERATED" if events else "FJ_BLOCKED_ZERO_EVENT_POPULATION", "symbol": "GOLD#", "timeframe": "H1", "source_rows": len(bars), "source_first_timestamp": bars[0]["timestamp"], "source_last_timestamp": bars[-1]["timestamp"], "duplicate_source_timestamps": 0, "detected_gap_count": len(gaps), "accepted_closures": accepted, "unverified_gaps": blocked, "broker_history_completeness": "NOT_PROVEN", "event_population": {"total_EVENT_EMITTED": len(events), "LONG": sum(event["direction"] == "LONG" for event in events), "SHORT": sum(event["direction"] == "SHORT" for event in events), "counts_per_year": dict(sorted(years.items())), "counts_per_direction_year": direction_years, "first_event_timestamp": min((event["confirmation_timestamp"] for event in events), default=None), "last_event_timestamp": max((event["confirmation_timestamp"] for event in events), default=None)}, "terminal_status_counts": dict(sorted(status_counts.items())), "data_quality": {"exclusions_by_reason": dict(sorted(Counter(item["exclusion_reason"] for item in exclusions).items())), "exclusions_by_year": dict(sorted(Counter((item.get("gap_end") or item.get("gap_timestamp"))[:4] if (item.get("gap_end") or item.get("gap_timestamp")) else "UNKNOWN" for item in exclusions).items())), "exclusions_by_detector_state": dict(sorted(Counter(item["state"] for item in exclusions).items())), "event_coverage_limitations": ["broker-history completeness NOT_PROVEN", "28 unverified gaps remain fail-closed", "accepted daily/weekend closures reused from frozen EO/EU policy"]}, "integrity": integrity, "strategy_performance_status": "NOT_EVALUATED", "order_logic_status": "NOT_APPROVED", "candidate_status": "NOT_READY_FOR_ORDER_LOGIC", "profitability_claim": False}
    manifest = {"execution_status": "PASS", "detector_path": "tools/market_structure_break_retest_detector.py", "detector_sha256": sha256_path(Path(__file__).with_name("market_structure_break_retest_detector.py")), "detector_commit_provenance": "f13108b49dfccd26bb2a08ca5d791c034239abee", "fi_fixture_output_sha256": "0b13abedc4f71f5be160b18830de69537438351ba13ec4cf2671616bf9db6abc", "sources": provenance, "gap_policy": "research/results/checkpoint_eo_gap_policy_review/gap_policy_dry_run.csv", "raw_broker_csv_committed": False}
    return events, terminals, summary, manifest


def write_csv(path, rows, fields):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            normalized = {field: json.dumps(row[field], separators=(",", ":")) if field == "source_row_keys" else row.get(field) for field in fields}
            writer.writerow(normalized)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", action="append", required=True)
    parser.add_argument("--gap-policy", required=True)
    parser.add_argument("--output-root", required=True)
    args = parser.parse_args()
    paths = [Path(value) for value in args.source]
    first = generate(paths, Path(args.gap_policy))
    second = generate(paths, Path(args.gap_policy))
    first_bytes = canonical(first)
    second_bytes = canonical(second)
    if first_bytes != second_bytes:
        raise SystemExit("deterministic replay mismatch")
    events, terminals, summary, manifest = first
    root = Path(args.output_root); root.mkdir(parents=True, exist_ok=True)
    write_csv(root / "checkpoint_fj_event_population.csv", events, EVENT_SCHEMA)
    terminal_fields = ["status", "state", "candidate_id", "event_id", "swing_id", "duplicate_timestamp", "gap_timestamp", "gap_start", "gap_end", "direction", "affected_break_or_swing_id", "exclusion_reason"]
    write_csv(root / "checkpoint_fj_candidate_status.csv", terminals, terminal_fields)
    replay = {"execution_status": "PASS", "byte_identical": True, "mismatch_count": 0, "event_population_sha256": digest(events), "exclusion_population_sha256": digest([item for item in terminals if item["status"] != "EVENT_EMITTED"]), "terminal_status_summary_sha256": digest(summary["terminal_status_counts"]), "population_summary_sha256": digest(summary), "event_ids_and_row_order_match": True}
    (root / "checkpoint_fj_population_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (root / "checkpoint_fj_source_manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (root / "checkpoint_fj_deterministic_replay.json").write_text(json.dumps(replay, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"summary": summary, "replay": replay}, indent=2, sort_keys=True))

if __name__ == "__main__":
    main()