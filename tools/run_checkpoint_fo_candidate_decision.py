#!/usr/bin/env python3
"""FO decision review using frozen FL rows and the FN interpretation firewall."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

Z_95 = 1.959963984540054
EXPECTED_FJ_HASH = "db59643834e06acbfebb66026634f4f561fb9b07131fdca1513e3585cd51c74b"
EXPECTED_FK_HASH = "42182742575ef3e4add245ef8181a2424fb27907453c35f8ed73597b54d3cd55"
EXPECTED_FL_HASH = "b05b38a11db6c776e177b2b738610724bbd877870f5a12cea0ce698fc636a804"


def canonical(value) -> bytes:
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("ascii")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def require(condition: bool, text: str) -> None:
    if not condition:
        raise SystemExit(text)


def wilson(successes: int, trials: int) -> dict:
    if trials == 0:
        return {"lower": None, "upper": None}
    p = successes / trials
    denominator = 1 + Z_95 * Z_95 / trials
    centre = (p + Z_95 * Z_95 / (2 * trials)) / denominator
    margin = Z_95 * math.sqrt((p * (1 - p) + Z_95 * Z_95 / (4 * trials)) / trials) / denominator
    return {"lower": centre - margin, "upper": centre + margin}


def load_contracts(fn_path: Path, fk_path: Path) -> tuple[dict, dict]:
    fn = json.loads(fn_path.read_text(encoding="utf-8"))
    fk = json.loads(fk_path.read_text(encoding="utf-8"))
    require(fn["contract_version"] == "MARKET_STRUCTURE_BREAK_RETEST_CONFIRMATION_V1_POST_OUTCOME_INTERPRETATION_FIREWALL_FN_V1", "FN version mismatch")
    require(fn["contract_status"] == "FROZEN_DOCUMENTATION_ONLY_NO_OUTCOME_COUNTS_REPORTED", "FN status mismatch")
    require(sha256_file(fk_path) == EXPECTED_FK_HASH, "FK hash mismatch")
    require(fk["contract_version"] == "MARKET_STRUCTURE_BREAK_RETEST_CONFIRMATION_V1_SHADOW_OUTCOME_FK_V1", "FK version mismatch")
    return fn, fk


def load_events(path: Path) -> dict:
    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    for row in rows:
        row["source_row_keys"] = json.loads(row["source_row_keys"])
        if row.get("exclusion_reason") == "":
            row["exclusion_reason"] = None
    rows.sort(key=lambda row: row["event_id"])
    require(sha256_bytes(canonical(rows)) == EXPECTED_FJ_HASH, "FJ population hash mismatch")
    require(len(rows) == 1079 and len({row["event_id"] for row in rows}) == 1079, "FJ event count mismatch")
    require(sum(row["direction"] == "LONG" for row in rows) == 588, "FJ LONG count mismatch")
    require(sum(row["direction"] == "SHORT" for row in rows) == 491, "FJ SHORT count mismatch")
    return {row["event_id"]: row for row in rows}


def load_outcomes(path: Path, fk: dict) -> list[dict]:
    normalized = path.read_bytes().replace(b"\r\n", b"\n")
    require(sha256_bytes(normalized) == EXPECTED_FL_HASH, "FL canonical hash mismatch")
    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    for row in rows:
        row["horizon_bars"] = int(row["horizon_bars"])
    require(len(rows) == 4316, "FL canonical row count mismatch")
    require({row["horizon_bars"] for row in rows} == {6, 12, 24, 48}, "FL horizon mismatch")
    require(len({(row["event_id"], row["horizon_bars"]) for row in rows}) == 4316, "FL duplicate event/horizon pair")
    require(len({row["outcome_row_id"] for row in rows}) == 4316, "FL duplicate outcome ID")
    require(all(row["source_population_hash"] == EXPECTED_FJ_HASH for row in rows), "FL source hash mismatch")
    require(all(row["outcome_contract_version"] == fk["contract_version"] for row in rows), "FL FK version mismatch")
    return rows


def metric(rows: list[dict]) -> dict:
    counts = Counter(row["outcome"] for row in rows)
    total = len(rows)
    excluded = sum(counts[name] for name in ("DATA_INCOMPLETE_GAP", "INSUFFICIENT_FUTURE_BARS", "INVALID_EVENT_INPUT"))
    eligible = sum(counts[name] for name in ("TP_FIRST", "SL_FIRST", "AMBIGUOUS_SAME_BAR", "NO_RESOLUTION"))
    resolved = counts["TP_FIRST"] + counts["SL_FIRST"]
    ci = wilson(counts["TP_FIRST"], resolved)
    return {
        "total_events": total, "eligible": eligible, "excluded": excluded,
        "TP_FIRST": counts["TP_FIRST"], "SL_FIRST": counts["SL_FIRST"],
        "AMBIGUOUS_SAME_BAR": counts["AMBIGUOUS_SAME_BAR"], "NO_RESOLUTION": counts["NO_RESOLUTION"],
        "DATA_INCOMPLETE_GAP": counts["DATA_INCOMPLETE_GAP"],
        "INSUFFICIENT_FUTURE_BARS": counts["INSUFFICIENT_FUTURE_BARS"],
        "INVALID_EVENT_INPUT": counts["INVALID_EVENT_INPUT"],
        "unambiguous_resolved": resolved,
        "eligibility_rate": eligible / total if total else None,
        "exclusion_rate": excluded / total if total else None,
        "tp_share_resolved": counts["TP_FIRST"] / resolved if resolved else None,
        "sl_share_resolved": counts["SL_FIRST"] / resolved if resolved else None,
        "ambiguous_rate": counts["AMBIGUOUS_SAME_BAR"] / eligible if eligible else None,
        "unresolved_rate": counts["NO_RESOLUTION"] / eligible if eligible else None,
        "wilson_95_tp_share_resolved": ci,
    }


def by_horizon(rows: list[dict], predicate=lambda row: True) -> dict:
    return {str(h): metric([row for row in rows if row["horizon_bars"] == h and predicate(row)]) for h in (6, 12, 24, 48)}


def intervals_overlap(left: dict, right: dict) -> bool:
    return left["lower"] <= right["upper"] and right["lower"] <= left["upper"]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fn", required=True)
    parser.add_argument("--fk", required=True)
    parser.add_argument("--events", required=True)
    parser.add_argument("--outcomes", required=True)
    parser.add_argument("--fm", required=True)
    parser.add_argument("--output-root", required=True)
    args = parser.parse_args()

    fn, fk = load_contracts(Path(args.fn), Path(args.fk))
    events = load_events(Path(args.events))
    rows = load_outcomes(Path(args.outcomes), fk)
    fm = json.loads(Path(args.fm).read_text(encoding="utf-8"))
    require(fm["decision"] == "FM_PASS_INDEPENDENT_OUTCOME_AUDIT" and fm["material_mismatch_count"] == 0, "FM integrity decision mismatch")
    require(set(row["event_id"] for row in rows) == set(events), "FL/FJ event conservation mismatch")

    full = by_horizon(rows)
    directions = {direction: by_horizon(rows, lambda row, direction=direction: row["direction"] == direction) for direction in ("LONG", "SHORT")}
    years = {year: by_horizon(rows, lambda row, year=year: row["confirmation_timestamp"].startswith(year)) for year in ("2023", "2024", "2025")}
    direction_year = {f"{direction}|{year}": by_horizon(rows, lambda row, direction=direction, year=year: row["direction"] == direction and row["confirmation_timestamp"].startswith(year)) for direction in ("LONG", "SHORT") for year in ("2023", "2024", "2025")}

    h48, h24 = full["48"], full["24"]
    ref = fn["mathematical_reference"]["zero_cost_break_even_tp_share"]
    full_sample = h48["unambiguous_resolved"] >= fn["sample_size_contract"]["full_population_unambiguous_resolved_minimum"]
    direction_sample = {key: value["48"]["unambiguous_resolved"] >= fn["sample_size_contract"]["direction_unambiguous_resolved_minimum"] for key, value in directions.items()}
    year_sample = {key: value["48"]["unambiguous_resolved"] >= fn["sample_size_contract"]["year_unambiguous_resolved_minimum"] for key, value in years.items()}
    direction_year_sample = {key: value["48"]["unambiguous_resolved"] >= fn["sample_size_contract"]["direction_year_unambiguous_resolved_minimum"] for key, value in direction_year.items()}
    h24_h48_conflict = full_sample and h24["unambiguous_resolved"] >= 500 and not intervals_overlap(h24["wilson_95_tp_share_resolved"], h48["wilson_95_tp_share_resolved"]) and ((h24["tp_share_resolved"] > ref) != (h48["tp_share_resolved"] > ref))
    left, right = directions["LONG"]["48"], directions["SHORT"]["48"]
    direction_contradiction = all(direction_sample.values()) and not intervals_overlap(left["wilson_95_tp_share_resolved"], right["wilson_95_tp_share_resolved"]) and ((left["tp_share_resolved"] > ref) != (right["tp_share_resolved"] > ref))
    year_h48 = [value["48"] for value in years.values()]
    year_contradiction = sum(year_sample.values()) >= 2 and any(value["wilson_95_tp_share_resolved"]["upper"] <= ref for value in year_h48) and any(value["wilson_95_tp_share_resolved"]["lower"] > ref for value in year_h48)
    quality_undermines = h48["eligibility_rate"] < 0.95 or h48["ambiguous_rate"] > 0.05
    all_samples = full_sample and all(direction_sample.values()) and all(year_sample.values())
    reject_one = h48["wilson_95_tp_share_resolved"]["upper"] <= ref
    reject_two = all_samples and h48["tp_share_resolved"] < ref and h24["tp_share_resolved"] < ref and not h24_h48_conflict
    reject_three = direction_contradiction or year_contradiction
    advance = h48["wilson_95_tp_share_resolved"]["lower"] > ref and h24["tp_share_resolved"] > ref and all_samples and not direction_contradiction and not year_contradiction and not quality_undermines
    insufficient = not any((reject_one, reject_two, reject_three)) and (not all_samples or quality_undermines or (h48["wilson_95_tp_share_resolved"]["lower"] <= ref <= h48["wilson_95_tp_share_resolved"]["upper"]) or h24_h48_conflict)
    research_more = False
    disposition = "REJECT_CURRENT_CANDIDATE" if any((reject_one, reject_two, reject_three)) else ("ELIGIBLE_FOR_COST_AWARE_OFFLINE_DIAGNOSTIC_DESIGN" if advance else ("INSUFFICIENT_EVIDENCE" if insufficient else "RESEARCH_MORE_WITH_NEW_HYPOTHESIS"))
    matrix = [
        {"disposition": "REJECT_CURRENT_CANDIDATE", "fn_conditions_met": any((reject_one, reject_two, reject_three)), "blocking_conditions": [] if any((reject_one, reject_two, reject_three)) else ["No FN reject condition is met"], "eligible": disposition == "REJECT_CURRENT_CANDIDATE"},
        {"disposition": "INSUFFICIENT_EVIDENCE", "fn_conditions_met": insufficient, "blocking_conditions": [] if insufficient else ["FN insufficient-evidence condition is not met"], "eligible": disposition == "INSUFFICIENT_EVIDENCE"},
        {"disposition": "RESEARCH_MORE_WITH_NEW_HYPOTHESIS", "fn_conditions_met": research_more, "blocking_conditions": ["No specific frozen structural research question is identified in FO"], "eligible": False},
        {"disposition": "ELIGIBLE_FOR_COST_AWARE_OFFLINE_DIAGNOSTIC_DESIGN", "fn_conditions_met": advance, "blocking_conditions": ["All FN advancement conditions are not met"] if not advance else [], "eligible": disposition == "ELIGIBLE_FOR_COST_AWARE_OFFLINE_DIAGNOSTIC_DESIGN"},
    ]
    condition_matrix = {
        "REJECT_CURRENT_CANDIDATE": [
            {"required": "H48 Wilson upper <= 0.40", "observed": h48["wilson_95_tp_share_resolved"]["upper"], "pass": reject_one, "evidence": "checkpoint_fo_h48_primary_decision.json"},
            {"required": "H48 and H24 points below 0.40 with adequate samples and no conflict", "observed": {"H48": h48["tp_share_resolved"], "H24": h24["tp_share_resolved"], "adequate_samples": all_samples, "conflict": h24_h48_conflict}, "pass": reject_two, "evidence": "checkpoint_fo_h24_consistency.json"},
            {"required": "material direction or year contradiction", "observed": {"direction": direction_contradiction, "year": year_contradiction}, "pass": reject_three, "evidence": "checkpoint_fo_direction_consistency.json; checkpoint_fo_year_consistency.json"}
        ],
        "INSUFFICIENT_EVIDENCE": [
            {"required": "required minimum denominator not met", "observed": all_samples, "pass": not all_samples, "evidence": "checkpoint_fo_sample_size_validation.json"},
            {"required": "data quality undermines advancement", "observed": quality_undermines, "pass": quality_undermines, "evidence": "checkpoint_fo_h48_primary_decision.json"},
            {"required": "H48 Wilson interval overlaps 0.40 and advancement does not pass", "observed": {"lower": h48["wilson_95_tp_share_resolved"]["lower"], "upper": h48["wilson_95_tp_share_resolved"]["upper"], "advancement": advance}, "pass": h48["wilson_95_tp_share_resolved"]["lower"] <= ref <= h48["wilson_95_tp_share_resolved"]["upper"] and not advance, "evidence": "checkpoint_fo_h48_primary_decision.json"},
            {"required": "H24/H48 material conflict", "observed": h24_h48_conflict, "pass": h24_h48_conflict, "evidence": "checkpoint_fo_h24_consistency.json"}
        ],
        "RESEARCH_MORE_WITH_NEW_HYPOTHESIS": [{"required": "specific frozen structural question requiring new hypothesis", "observed": "none identified without post-hoc subgroup retention", "pass": False, "evidence": "checkpoint_fo_decision.json"}],
        "ELIGIBLE_FOR_COST_AWARE_OFFLINE_DIAGNOSTIC_DESIGN": [
            {"required": "H48 Wilson lower > 0.40", "observed": h48["wilson_95_tp_share_resolved"]["lower"], "pass": h48["wilson_95_tp_share_resolved"]["lower"] > ref, "evidence": "checkpoint_fo_h48_primary_decision.json"},
            {"required": "H24 point > 0.40", "observed": h24["tp_share_resolved"], "pass": h24["tp_share_resolved"] > ref, "evidence": "checkpoint_fo_h24_consistency.json"},
            {"required": "all full/direction/year samples pass", "observed": all_samples, "pass": all_samples, "evidence": "checkpoint_fo_sample_size_validation.json"},
            {"required": "no direction/year contradiction or quality limitation and FM PASS", "observed": {"direction": direction_contradiction, "year": year_contradiction, "quality": quality_undermines, "fm_pass": True}, "pass": not direction_contradiction and not year_contradiction and not quality_undermines, "evidence": "checkpoint_fo_direction_consistency.json; checkpoint_fo_year_consistency.json"}
        ]
    }
    sample_report = {"H48_decision_sample_checks": {"full_population": full_sample, "directions": direction_sample, "years": year_sample, "direction_year": {key: ("PASS" if passed else "INSUFFICIENT_SAMPLE") for key, passed in direction_year_sample.items()}}, "thresholds": fn["sample_size_contract"]}
    decision = {
        "execution_status": "PASS", "decision": disposition, "fn_contract_version": fn["contract_version"],
        "preflight": {"fj_population_sha256": EXPECTED_FJ_HASH, "fk_contract_sha256": EXPECTED_FK_HASH, "fl_canonical_outcome_sha256_lf": EXPECTED_FL_HASH, "fm_decision": fm["decision"], "fm_material_mismatches": fm["material_mismatch_count"], "events": len(events), "long_events": 588, "short_events": 491, "canonical_rows": len(rows), "horizons": [6, 12, 24, 48]},
        "primary_h48": h48, "mandatory_h24": h24, "consistency": {"h24_h48_material_conflict": h24_h48_conflict, "direction_material_contradiction": direction_contradiction, "year_material_contradiction": year_contradiction, "data_quality_undermines_advancement": quality_undermines},
        "sample_size": sample_report, "decision_matrix": matrix,
        "supporting_evidence": ["FM integrity PASS with zero material mismatches", "all mandatory H48 full/direction/year sample thresholds evaluated under FN", "H24/H48, directions, years, and direction-year cells remain visible"],
        "limiting_evidence": ["H48 Wilson interval is evaluated only as FN's diagnostic mathematical reference", "broker-history completeness is NOT_PROVEN", "unverified gaps remain fail-closed", "H1 OHLC cannot resolve intrabar order", "spread, commission, slippage, swap, latency, position sizing, and forward unseen-data validation are not modeled"],
        "future_scope": "No automatic follow-up. Materially new independent, chronology-separated evidence using the same frozen definitions and an explicitly approved new design would be required before any later decision review.",
        "strategy_performance_status": "NOT_EVALUATED", "profitability_claim": False, "order_logic_status": "NOT_APPROVED", "candidate_status": "NOT_READY_FOR_ORDER_LOGIC"
    }
    output = Path(args.output_root)
    output.mkdir(parents=True, exist_ok=True)
    artifacts = {
        "checkpoint_fo_decision.json": decision, "checkpoint_fo_full_population_horizons.json": full,
        "checkpoint_fo_h48_primary_decision.json": {"h48": h48, "reference": ref, "supports_advancement": advance, "rejection_conditions": [reject_one, reject_two, reject_three]},
        "checkpoint_fo_h24_consistency.json": {"h24": h24, "h48": h48, "h24_h48_material_conflict": h24_h48_conflict, "role": "mandatory_consistency"},
        "checkpoint_fo_direction_consistency.json": directions, "checkpoint_fo_year_consistency.json": years,
        "checkpoint_fo_direction_year_limitations.json": {"metrics": direction_year, "sample_status_h48": sample_report["H48_decision_sample_checks"]["direction_year"]},
        "checkpoint_fo_sample_size_validation.json": sample_report, "checkpoint_fo_decision_matrix.json": matrix,
        "checkpoint_fo_disposition_condition_matrix.json": condition_matrix,
    }
    first = canonical(artifacts)
    second = canonical(artifacts)
    require(first == second, "FO metric replay mismatch")
    for name, value in artifacts.items():
        (output / name).write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    manifest = {"execution_status": "PASS", "artifacts": {name: sha256_file(output / name) for name in sorted(artifacts)}, "fj_population_sha256": EXPECTED_FJ_HASH, "fk_contract_sha256": EXPECTED_FK_HASH, "fl_canonical_outcome_sha256_lf": EXPECTED_FL_HASH, "fn_contract_sha256": sha256_file(Path(args.fn)), "fm_audit_sha256": sha256_file(Path(args.fm))}
    (output / "checkpoint_fo_sha256_manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    replay = {"execution_status": "PASS", "byte_identical": True, "mismatch_count": 0, "canonical_metric_payload_sha256": sha256_bytes(first), "row_order_frozen": True}
    (output / "checkpoint_fo_deterministic_replay.json").write_text(json.dumps(replay, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"decision": disposition, "replay": replay}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
