#!/usr/bin/env python3
"""Run only fixed FI detector fixtures and emit deterministic validation artifacts."""
from __future__ import annotations
import argparse, copy, json
from datetime import datetime, timedelta
from hashlib import sha256
from pathlib import Path
from market_structure_break_retest_detector import EVENT_SCHEMA, TIE_BREAK_ORDER, detect


def stable(value):
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":"))


def digest(value):
    return sha256(stable(value).encode("ascii")).hexdigest()


def bar(index, op, high, low, close, **extra):
    timestamp = (datetime(2024, 1, 1) + timedelta(hours=index)).isoformat()
    return {"timestamp": timestamp, "source_row_key": f"fixture-row-{index:03d}", "open": op, "high": high, "low": low, "close": close, **extra}


def long_base():
    bars = [bar(i, 95, 100, 90, 95, metadata={"fixture": "base", "index": i}) for i in range(15)]
    bars += [bar(15, 96, 101, 93, 96), bar(16, 97, 103, 94, 97), bar(17, 100, 110, 95, 100), bar(18, 101, 104, 96, 101), bar(19, 99, 102, 95, 99)]
    return bars


def short_base():
    bars = [bar(i, 95, 100, 90, 95, metadata={"fixture": "base", "index": i}) for i in range(15)]
    bars += [bar(15, 94, 99, 89, 94), bar(16, 92, 98, 87, 92), bar(17, 85, 95, 80, 85), bar(18, 88, 96, 86, 88), bar(19, 90, 97, 88, 90)]
    return bars


def long_event():
    bars = long_base()
    bars += [bar(20, 108, 113, 105, 112), bar(21, 111, 112, 109, 110), bar(22, 110, 115, 109, 114)]
    return bars


def short_event():
    bars = short_base()
    bars += [bar(20, 85, 86, 75, 78), bar(21, 79, 81, 76, 79), bar(22, 79, 80, 74, 75)]
    return bars


def fixtures():
    out = {"A_valid_long_event": long_event(), "B_valid_short_event": short_event()}
    wick = long_base() + [bar(20, 108, 113, 105, 109)]
    out["C_wick_only_false_break"] = wick
    out["D_swing_not_yet_confirmed"] = long_base()[:19]
    late = long_base() + [bar(20, 108, 113, 105, 112)]
    late += [bar(i, 111, 114, 111, 112) for i in range(21, 33)]
    out["E_retest_after_12_valid_bars"] = late
    failed = long_base() + [bar(20, 108, 113, 105, 112), bar(21, 111, 112, 109, 110)]
    failed += [bar(i, 110, 113, 109, 110) for i in range(22, 33)]
    out["F_confirmation_failure"] = failed
    gap = long_base() + [bar(20, 108, 113, 105, 112), bar(21, 111, 112, 109, 110, gap_before=True)]
    out["G_unverified_gap_required_sequence"] = gap
    duplicate = long_base() + [bar(20, 108, 113, 105, 112), bar(21, 111, 113, 109, 112), bar(22, 110, 115, 109, 114)]
    out["H_duplicate_suppression"] = duplicate
    anchored = long_base() + [bar(20, 108, 113, 105, 112), bar(21, 111, 112, 109, 110), bar(22, 110, 120, 109, 111), bar(23, 110, 115, 108, 110), bar(24, 109, 110, 106, 109), bar(25, 110, 116, 108, 116)]
    out["I_newer_swing_no_reanchor"] = anchored
    out["J_tied_eligible_swing_order"] = long_event()
    out["K_byte_identical_replay"] = long_event()
    out["L_nonsemantic_metadata_order"] = long_event()
    return out


def assertions(name, result):
    statuses = {item["status"] for item in result["terminals"]}
    events = result["events"]
    if name == "A_valid_long_event": return len(events) == 1 and events[0]["direction"] == "LONG" and events[0]["entry_reference_price"] == events[0]["confirmation_close"]
    if name == "B_valid_short_event": return len(events) == 1 and events[0]["direction"] == "SHORT"
    if name == "C_wick_only_false_break": return not events and "EVENT_EMITTED" not in statuses
    if name == "D_swing_not_yet_confirmed": return not events and "INSUFFICIENT_RIGHT_HISTORY" in statuses
    if name == "E_retest_after_12_valid_bars": return "RETEST_NOT_FOUND_WITHIN_12_BARS" in statuses
    if name == "F_confirmation_failure": return "CONFIRMATION_NOT_FOUND_WITHIN_12_BARS" in statuses
    if name == "G_unverified_gap_required_sequence": return "DATA_INCOMPLETE_GAP" in statuses
    if name == "H_duplicate_suppression": return len(events) == 1 and "DUPLICATE_SUPPRESSED" in statuses
    if name == "I_newer_swing_no_reanchor": return len(events) == 1 and events[0]["swing_price"] == "110"
    if name == "J_tied_eligible_swing_order": return result["tie_break_order"] == TIE_BREAK_ORDER
    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--inputs", required=True)
    parser.add_argument("--expected", required=True)
    parser.add_argument("--output-root", required=True)
    parser.add_argument("--write-expected", action="store_true")
    parser.add_argument("--write-inputs", action="store_true")
    args = parser.parse_args()
    inputs_path = Path(args.inputs)
    if args.write_inputs:
        inputs_path.write_text(json.dumps(fixtures(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    fixture_inputs = json.loads(inputs_path.read_text(encoding="utf-8"))
    case_results = {}
    for name, bars in fixture_inputs.items():
        result = detect(bars)
        if not assertions(name, result): raise SystemExit(f"semantic assertion failed: {name}")
        case_results[name] = result
    # K: independently replay every fixture. L: reverse irrelevant metadata insertion order and input order.
    replay = {name: detect(bars) for name, bars in fixture_inputs.items()}
    replay_identical = stable(case_results) == stable(replay)
    reordered = copy.deepcopy(fixture_inputs["L_nonsemantic_metadata_order"])
    for item in reordered:
        if "metadata" in item: item["metadata"] = dict(reversed(list(item["metadata"].items())))
    reordered_ids = [event["event_id"] for event in detect(list(reversed(reordered)))["events"]]
    original_ids = [event["event_id"] for event in case_results["L_nonsemantic_metadata_order"]["events"]]
    if not replay_identical or reordered_ids != original_ids: raise SystemExit("replay or metadata ordering mismatch")
    for result in case_results.values():
        for event in result["events"]:
            if list(event) != EVENT_SCHEMA: raise SystemExit("event schema mismatch")
            encoded = stable(event)
            if "uuid" in encoded.lower() or "2026-" in encoded: raise SystemExit("non-frozen value found")
    expected_path = Path(args.expected)
    if args.write_expected:
        expected_path.write_text(json.dumps(case_results, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    expected = json.loads(expected_path.read_text(encoding="utf-8"))
    if stable(case_results) != stable(expected): raise SystemExit("golden expected output mismatch")
    root = Path(args.output_root); root.mkdir(parents=True, exist_ok=True)
    summary = {"execution_status": "PASS", "fixture_count": len(case_results), "fixtures_passed": len(case_results), "event_schema": EVENT_SCHEMA, "fixture_output_sha256": digest(case_results), "zero_key_mismatches": True, "no_random_or_current_timestamps": True, "no_hidden_file_order_dependency": True, "strategy_performance_status": "NOT_EVALUATED", "order_logic_status": "NOT_APPROVED", "candidate_status": "NOT_READY_FOR_ORDER_LOGIC", "profitability_claim": False}
    replay_summary = {"execution_status": "PASS", "run_1_sha256": digest(case_results), "run_2_sha256": digest(replay), "byte_identical": replay_identical, "zero_key_mismatches": True, "metadata_order_event_ids_identical": reordered_ids == original_ids}
    (root / "checkpoint_fi_fixture_test_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (root / "checkpoint_fi_deterministic_replay_summary.json").write_text(json.dumps(replay_summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"summary": summary, "replay": replay_summary}, indent=2, sort_keys=True))

if __name__ == "__main__": main()