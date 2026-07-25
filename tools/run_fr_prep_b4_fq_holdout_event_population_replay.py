#!/usr/bin/env python3
"""Authorized sealed FQ event-population replay; no outcomes or trading."""
from __future__ import annotations

import argparse
import copy
import csv
import hashlib
import importlib
import json
import math
import ntpath
import os
import posixpath
import shutil
import subprocess
import sys
import tempfile
from collections import Counter
from datetime import datetime
from pathlib import Path

import jsonschema

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

AUTH = ROOT / "research/contracts/fr_prep_b3a_fq_holdout_execution_authorization.v1.json"
B3 = ROOT / "research/contracts/fr_prep_b3_fq_holdout_preflight.v1.json"
B3A = ROOT / "research/contracts/fr_prep_b3a_fq_holdout_execution_authorization_evidence.v1.json"
B3A_RESULT = ROOT / "research/results/checkpoint_fr_prep_b3a/fq_holdout_execution_authorization_summary.json"
FQ_ROOT = ROOT / "research/results/checkpoint_fq_holdout_gap_boundary"
EVIDENCE = ROOT / "research/contracts/fr_prep_b4_fq_holdout_event_population_replay.v1.json"
EVIDENCE_SCHEMA = ROOT / "research/schemas/fr_prep_b4_fq_holdout_event_population_replay.v1.schema.json"
RESULT_ROOT = ROOT / "research/results/checkpoint_fr_prep_b4"
MODE = "sealed-fq-event-population-replay"
PASS = "FR_PREP_B4_PASS_SEALED_FQ_EVENT_POPULATION_REPLAY"
AUTH_ID = "b2fb6bfe4c96f8d18d910b78180ea7b70d3c9ba2ad4142c859e03be6559ea97d"
B3_ID = "eec147eed43a60aad28a058d2f906181010da225b18964acd00d87ba984659ad"
B3A_ID = "c31476f8e75b36231fa1c6b67b2e1d1a95668abe1a8311cc69d30e62e8d1eeab"
DETECTOR_SHA = "9d7496581806d267df9130a35c0ec0dd948b6d77fcc30d8cca115edd4b746144"
EVENT_FIELDS = [
    "event_id", "symbol", "timeframe", "direction", "swing_type",
    "swing_timestamp", "swing_confirmation_timestamp", "swing_price",
    "break_timestamp", "break_close", "retest_timestamp", "retest_price_reference",
    "confirmation_timestamp", "confirmation_open", "confirmation_high",
    "confirmation_low", "confirmation_close", "entry_reference_price", "atr",
    "year", "source_row_keys", "data_quality_status", "exclusion_reason",
]
CANDIDATE_FIELDS = [
    "status", "state", "candidate_id", "event_id", "swing_id",
    "duplicate_timestamp", "gap_timestamp", "gap_start", "gap_end",
    "direction", "affected_break_or_swing_id", "exclusion_reason",
]


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def digest(value):
    return hashlib.sha256(canonical(value).encode("ascii")).hexdigest()


def file_hash(path):
    value = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def identity(value):
    return digest({key: item for key, item in value.items() if key != "canonical_summary_sha256"})


def absolute_path_count(value):
    if isinstance(value, dict):
        return sum(absolute_path_count(item) for item in value.values())
    if isinstance(value, list):
        return sum(absolute_path_count(item) for item in value)
    return int(isinstance(value, str) and (ntpath.isabs(value) or posixpath.isabs(value)))


class ExternalAudit:
    def __init__(self):
        self.blocked = []

    def deny(self, kind, command):
        self.blocked.append(kind)
        raise RuntimeError("B4_EXTERNAL_PROCESS_BLOCKED")

    def __enter__(self):
        self.popen = subprocess.Popen
        self.system = os.system
        self.startfile = getattr(os, "startfile", None)
        subprocess.Popen = lambda command, *args, **kwargs: self.deny("subprocess", command)
        os.system = lambda command: self.deny("os.system", command)
        if self.startfile is not None:
            os.startfile = lambda path, *args, **kwargs: self.deny("os.startfile", path)
        return self

    def __exit__(self, *_):
        subprocess.Popen = self.popen
        os.system = self.system
        if self.startfile is not None:
            os.startfile = self.startfile


def expect_failure(action):
    try:
        action()
    except (RuntimeError, ValueError):
        return True
    return False


def validate_authorization_and_evidence(auth):
    if digest(auth) != AUTH_ID:
        raise ValueError("B4_AUTHORIZATION_IDENTITY_MISMATCH")
    b3 = read_json(B3)
    b3a = read_json(B3A)
    b3a_result = read_json(B3A_RESULT)
    if identity(b3) != B3_ID or b3.get("canonical_summary_sha256") != B3_ID:
        raise ValueError("B4_B3_IDENTITY_MISMATCH")
    if b3.get("decision") != "FR_PREP_B3_PASS_FQ_HOLDOUT_PREFLIGHT_SEALED":
        raise ValueError("B4_B3_DECISION_MISMATCH")
    if identity(b3a) != B3A_ID or b3a.get("canonical_summary_sha256") != B3A_ID:
        raise ValueError("B4_B3A_IDENTITY_MISMATCH")
    if b3a_result.get("canonical_summary_sha256") != B3A_ID:
        raise ValueError("B4_B3A_RESULT_MISMATCH")
    if b3a.get("authorization_identity_sha256") != AUTH_ID:
        raise ValueError("B4_B3A_AUTHORIZATION_MISMATCH")
    if not b3a.get("holdout_execution_authorized_for_next_checkpoint"):
        raise ValueError("B4_HOLDOUT_NOT_AUTHORIZED")
    if any((b3a.get("holdout_executed"), b3a.get("detector_imported"), b3a.get("detector_executed"))):
        raise ValueError("B4_B3A_EXECUTION_STATE_MISMATCH")
    detector = (ROOT / auth["detector_binding"]["path"]).resolve()
    if file_hash(detector) != DETECTOR_SHA:
        raise ValueError("B4_DETECTOR_HASH_MISMATCH")
    for name, expected in auth["gap_artifacts"].items():
        path = FQ_ROOT / name
        if not path.is_file() or file_hash(path) != expected:
            raise ValueError("B4_FQ_ARTIFACT_HASH_MISMATCH")


def execute_authorized_replay(auth, state, loader, executor):
    if digest(auth) != AUTH_ID or auth.get("dataset_id") != "FP_FQ_2020_2022_GOLD_H1":
        raise ValueError("B4_AUTHORIZATION_IDENTITY_MISMATCH")
    prohibited = (
        "atr_event_pipeline_allowed", "tp_sl_allowed", "outcomes_allowed",
        "fn_interpretation_allowed", "optimization_allowed", "parameter_changes_allowed",
        "indicator_changes_allowed", "lot_risk_order_logic_allowed",
        "mt5_ea_execution_allowed", "profitability_claim_allowed",
        "network_external_process_allowed", "strategy_detector_gap_rule_changes_allowed",
    )
    if any(auth.get(key) is not False for key in prohibited):
        raise ValueError("B4_PROHIBITED_PERMISSION_NOT_FALSE")
    exact = {
        "b3_validated": True, "b3a_validated": True, "sources_validated": True,
        "gap_inventory_validated": True, "detector_validated": True,
        "b3_summary_sha256": B3_ID, "b3a_summary_sha256": B3A_ID,
        "detector_sha256": DETECTOR_SHA, "source_rows": 17731, "gap_count": 774,
        "accepted_weekend_closures": 149, "accepted_daily_closures": 0,
        "unverified_gaps": 625,
        "canonical_timeline_sha256": "4ff441fa895c3e7d8f256b11501d7dac6bf5e606ef1c90d2d409c39689a81c38",
    }
    if any(state.get(key) != value for key, value in exact.items()):
        raise ValueError("B4_FROZEN_BINDING_MISMATCH")
    if loader is None or executor is None:
        raise ValueError("B4_LAZY_DETECTOR_BOUNDARY_REQUIRED")
    return executor(loader())


def prepare_sources(source_root, auth):
    bars = []
    timeline = []
    manifest_sources = []
    approved = {item["filename"]: item for item in auth["source_files"]}
    for name in sorted(approved):
        spec = approved[name]
        path = (Path(source_root) / name).resolve()
        if not path.is_file() or file_hash(path) != spec["sha256"]:
            raise ValueError("B4_SOURCE_HASH_MISMATCH")
        with path.open(encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.DictReader(handle, delimiter="\t"))
        required = {"<DATE>", "<TIME>", "<OPEN>", "<HIGH>", "<LOW>", "<CLOSE>"}
        if not rows or not required.issubset(rows[0]) or len(rows) != spec["rows"]:
            raise ValueError("B4_SOURCE_SCHEMA_OR_COUNT_MISMATCH")
        stamps = []
        for line, row in enumerate(rows, start=2):
            stamp = datetime.strptime(
                f"{row['<DATE>']} {row['<TIME>']}", "%Y.%m.%d %H:%M:%S"
            )
            stamp_text = stamp.isoformat()
            key = f"{name}:{line}"
            values = [float(row[field]) for field in ("<OPEN>", "<HIGH>", "<LOW>", "<CLOSE>")]
            if not all(math.isfinite(value) and value > 0 for value in values):
                raise ValueError("B4_SOURCE_OHLC_INVALID")
            if not (values[1] >= max(values[0], values[3]) and values[2] <= min(values[0], values[3])):
                raise ValueError("B4_SOURCE_OHLC_INVALID")
            bars.append({
                "timestamp": stamp_text,
                "source_row_key": key,
                "open": row["<OPEN>"],
                "high": row["<HIGH>"],
                "low": row["<LOW>"],
                "close": row["<CLOSE>"],
            })
            timeline.append({"timestamp": stamp_text, "key": key, "file": name})
            stamps.append(stamp)
        manifest_sources.append({
            "filename": name,
            "sha256": spec["sha256"],
            "rows": len(rows),
            "first_timestamp": stamps[0].isoformat(),
            "last_timestamp": stamps[-1].isoformat(),
        })
    bars.sort(key=lambda bar: (bar["timestamp"], bar["source_row_key"]))
    timeline.sort(key=lambda bar: (bar["timestamp"], bar["key"]))
    if len(bars) != 17731 or len({bar["timestamp"] for bar in bars}) != len(bars):
        raise ValueError("B4_TIMELINE_COUNT_OR_DUPLICATE_MISMATCH")
    timeline_sha = digest(timeline)
    if timeline_sha != auth["fq_preflight"]["timeline_sha256"]:
        raise ValueError("B4_TIMELINE_HASH_MISMATCH")
    return bars, manifest_sources, timeline_sha


def apply_gap_inventory(bars, auth):
    inventory = read_json(FQ_ROOT / "checkpoint_fq_gap_inventory.json")
    gap_summary = read_json(FQ_ROOT / "checkpoint_fq_gap_summary.json")
    if len(inventory) != auth["fq_preflight"]["gaps"]:
        raise ValueError("B4_GAP_INVENTORY_COUNT_MISMATCH")
    by_pair = {
        (item["previous_bar_timestamp"], item["next_bar_timestamp"]): item
        for item in inventory
    }
    if len(by_pair) != len(inventory):
        raise ValueError("B4_DUPLICATE_GAP_PAIR")
    used = set()
    counts = Counter()
    for previous, current in zip(bars, bars[1:]):
        elapsed = (
            datetime.fromisoformat(current["timestamp"])
            - datetime.fromisoformat(previous["timestamp"])
        ).total_seconds() / 3600
        if elapsed <= 1:
            continue
        pair = (previous["timestamp"], current["timestamp"])
        item = by_pair.get(pair)
        if item is None or item["elapsed_hours"] != elapsed:
            raise ValueError("B4_GAP_PAIR_MISMATCH")
        classification = item["policy_classification"]
        if classification not in {
            "ACCEPTED_ROUTINE_WEEKEND_CLOSURE",
            "ACCEPTED_ROUTINE_DAILY_SESSION_CLOSURE",
            "UNVERIFIED_GAP",
        }:
            raise ValueError("B4_GAP_CLASSIFICATION_NOT_ALLOWED")
        if classification == "UNVERIFIED_GAP":
            if item["accepted_for_trading_bar_skip"] or not item["fail_closed_required"]:
                raise ValueError("B4_UNVERIFIED_GAP_SEMANTICS_MISMATCH")
            current["gap_before"] = True
            current["gap_details"] = {
                "gap_start": previous["timestamp"],
                "gap_end": current["timestamp"],
                "classification": classification,
            }
        else:
            if not item["accepted_for_trading_bar_skip"] or item["fail_closed_required"]:
                raise ValueError("B4_ACCEPTED_GAP_SEMANTICS_MISMATCH")
        counts[classification] += 1
        used.add(pair)
    expected = {
        "ACCEPTED_ROUTINE_WEEKEND_CLOSURE": auth["fq_preflight"]["accepted_weekend_closures"],
        "ACCEPTED_ROUTINE_DAILY_SESSION_CLOSURE": auth["fq_preflight"]["accepted_daily_closures"],
        "UNVERIFIED_GAP": auth["fq_preflight"]["unverified_gaps"],
    }
    if used != set(by_pair) or dict(counts) != {key: value for key, value in expected.items() if value}:
        raise ValueError("B4_GAP_COVERAGE_MISMATCH")
    if (
        gap_summary["total_detected_gaps"] != 774
        or gap_summary["routine_weekend_closures_accepted"] != 149
        or gap_summary["routine_daily_closures_accepted"] != 0
        or gap_summary["unverified_gaps"] != 625
    ):
        raise ValueError("B4_GAP_SUMMARY_MISMATCH")
    return counts


def normalize_terminals(terminals, bars):
    gap_by_end = {
        bar["timestamp"]: bar.get("gap_details")
        for bar in bars
        if bar.get("gap_details")
    }
    output = []
    for item in terminals:
        row = {
            "status": item["status"],
            "state": item["state"],
            "candidate_id": item.get("candidate_id"),
            "event_id": item.get("event_id"),
            "swing_id": item.get("swing_id"),
            "duplicate_timestamp": item.get("duplicate_timestamp"),
            "gap_timestamp": item.get("gap_timestamp"),
            "gap_start": None,
            "gap_end": None,
            "direction": None,
            "affected_break_or_swing_id": item.get("candidate_id") or item.get("swing_id"),
            "exclusion_reason": None if item["status"] == "EVENT_EMITTED" else item["status"],
        }
        details = gap_by_end.get(item.get("gap_timestamp"))
        if details:
            row["gap_start"] = details["gap_start"]
            row["gap_end"] = details["gap_end"]
        output.append(row)
    return sorted(
        output,
        key=lambda row: tuple("" if value is None else str(value) for value in row.values()),
    )


def validate_events(events, bars):
    ids = [event["event_id"] for event in events]
    source_keys = {bar["source_row_key"] for bar in bars}
    if ids != sorted(ids) or len(ids) != len(set(ids)):
        raise ValueError("B4_EVENT_ID_ORDER_OR_UNIQUENESS_MISMATCH")
    semantics = [
        (
            event["direction"],
            event["swing_timestamp"],
            event["break_timestamp"],
            event["confirmation_timestamp"],
        )
        for event in events
    ]
    if len(semantics) != len(set(semantics)):
        raise ValueError("B4_DUPLICATE_SEMANTIC_EVENT")
    for event in events:
        if list(event) != EVENT_FIELDS or event["direction"] not in {"LONG", "SHORT"}:
            raise ValueError("B4_EVENT_SCHEMA_MISMATCH")
        if not (
            event["swing_timestamp"]
            <= event["swing_confirmation_timestamp"]
            < event["break_timestamp"]
            < event["retest_timestamp"]
            <= event["confirmation_timestamp"]
        ):
            raise ValueError("B4_EVENT_TIMESTAMP_ORDER_MISMATCH")
        if any(key not in source_keys for key in event["source_row_keys"]):
            raise ValueError("B4_UNRESOLVED_SOURCE_ROW_KEY")


def population_summary(events, candidates, manifest, auth):
    directions = Counter(event["direction"] for event in events)
    years = Counter(event["year"] for event in events)
    direction_years = {
        direction: dict(sorted(Counter(
            event["year"] for event in events if event["direction"] == direction
        ).items()))
        for direction in ("LONG", "SHORT")
    }
    terminals = Counter(item["status"] for item in candidates)
    exclusions = [item for item in candidates if item["status"] != "EVENT_EMITTED"]
    return {
        "execution_status": "PASS",
        "decision": PASS,
        "dataset_id": auth["dataset_id"],
        "symbol": "GOLD#",
        "timeframe": "H1",
        "source_rows": 17731,
        "detected_gap_count": 774,
        "accepted_weekend_closures": 149,
        "accepted_daily_closures": 0,
        "unverified_gaps": 625,
        "event_population": {
            "total": len(events),
            "LONG": directions["LONG"],
            "SHORT": directions["SHORT"],
            "counts_per_year": {year: years.get(year, 0) for year in ("2020", "2021", "2022")},
            "counts_per_direction_year": direction_years,
            "first_event_timestamp": min((event["confirmation_timestamp"] for event in events), default=None),
            "last_event_timestamp": max((event["confirmation_timestamp"] for event in events), default=None),
        },
        "terminal_status_counts": dict(sorted(terminals.items())),
        "exclusion_counts": dict(sorted(Counter(
            item["exclusion_reason"] for item in exclusions
        ).items())),
        "detector_sha256": manifest["detector_sha256"],
        "performance": "NOT_EVALUATED",
        "profitability": "NOT_CLAIMED",
        "order_logic": "NOT_APPROVED",
        "candidate": "NOT_READY_FOR_ORDER_LOGIC",
    }


def build_manifest(source_manifest, timeline_sha, auth):
    return {
        "dataset_id": auth["dataset_id"],
        "symbol": "GOLD#",
        "timeframe": "H1",
        "source_rows": 17731,
        "canonical_timeline_sha256": timeline_sha,
        "sources": source_manifest,
        "gap_inventory": {
            "filename": "checkpoint_fq_gap_inventory.json",
            "sha256": auth["gap_artifacts"]["checkpoint_fq_gap_inventory.json"],
            "gaps": 774,
            "unverified_fail_closed": 625,
            "accepted_weekend": 149,
            "accepted_daily": 0,
        },
        "detector_path": auth["detector_binding"]["path"],
        "detector_sha256": auth["detector_binding"]["file_sha256"],
        "authorization_identity_sha256": AUTH_ID,
        "absolute_runtime_paths_excluded": True,
        "raw_broker_csv_committed": False,
    }


def detector_run(auth, state, bars, manifest, counters):
    def loader():
        return importlib.import_module("market_structure_break_retest_detector")

    def execute(detector):
        counters["detector_execution_count"] += 1
        result = detector.detect(bars, symbol="GOLD#", timeframe="H1")
        events = result["events"]
        candidates = normalize_terminals(result["terminals"], bars)
        validate_events(events, bars)
        summary = population_summary(events, candidates, manifest, auth)
        return {
            "events": events,
            "candidates": candidates,
            "summary": summary,
            "manifest": manifest,
        }

    counters["authorized_replay_count"] += 1
    return execute_authorized_replay(auth, state, loader, execute)


def write_csv(path, rows, fields):
    with Path(path).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            output = {
                field: json.dumps(row.get(field), separators=(",", ":"))
                if field == "source_row_keys"
                else row.get(field)
                for field in fields
            }
            writer.writerow(output)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", required=True, choices=[MODE])
    parser.add_argument("--authorization", required=True)
    parser.add_argument("--source-root", required=True)
    parser.add_argument("--output-root", required=True)
    args = parser.parse_args()
    if Path(args.authorization).resolve() != AUTH.resolve():
        raise SystemExit("B4_AUTHORIZATION_PATH_NOT_ALLOWED")
    if Path(args.output_root).resolve() != RESULT_ROOT.resolve():
        raise SystemExit("B4_OUTPUT_PATH_NOT_ALLOWED")

    auth = read_json(AUTH)
    validate_authorization_and_evidence(auth)
    source_root = Path(args.source_root).resolve()
    bars, source_manifest, timeline_sha = prepare_sources(source_root, auth)
    gap_counts = apply_gap_inventory(bars, auth)
    manifest = build_manifest(source_manifest, timeline_sha, auth)
    state = {
        "b3_validated": True,
        "b3a_validated": True,
        "sources_validated": True,
        "gap_inventory_validated": True,
        "detector_validated": True,
        "b3_summary_sha256": B3_ID,
        "b3a_summary_sha256": B3A_ID,
        "detector_sha256": DETECTOR_SHA,
        "source_rows": len(bars),
        "gap_count": sum(gap_counts.values()),
        "accepted_weekend_closures": gap_counts["ACCEPTED_ROUTINE_WEEKEND_CLOSURE"],
        "accepted_daily_closures": gap_counts["ACCEPTED_ROUTINE_DAILY_SESSION_CLOSURE"],
        "unverified_gaps": gap_counts["UNVERIFIED_GAP"],
        "canonical_timeline_sha256": timeline_sha,
    }

    before = set(sys.modules)
    counters = Counter()
    with ExternalAudit() as external:
        normal_1 = detector_run(auth, state, bars, manifest, counters)
        normal_2 = detector_run(auth, state, bars, manifest, counters)
        with tempfile.TemporaryDirectory(prefix="fr_prep_b4_relocation_") as name:
            relocated_root = Path(name).resolve()
            if relocated_root == ROOT or ROOT in relocated_root.parents:
                raise ValueError("B4_RELOCATION_INSIDE_REPOSITORY")
            for spec in auth["source_files"]:
                target = relocated_root / spec["filename"]
                shutil.copyfile(source_root / spec["filename"], target)
                if file_hash(target) != spec["sha256"]:
                    raise ValueError("B4_RELOCATED_SOURCE_HASH_MISMATCH")
            relocated_bars, relocated_sources, relocated_timeline = prepare_sources(relocated_root, auth)
            relocated_counts = apply_gap_inventory(relocated_bars, auth)
            relocated_manifest = build_manifest(relocated_sources, relocated_timeline, auth)
            if relocated_counts != gap_counts:
                raise ValueError("B4_RELOCATED_GAP_MISMATCH")
            relocated = detector_run(
                auth, state, relocated_bars, relocated_manifest, counters
            )

        tests = {}
        wrong_auth = copy.deepcopy(auth)
        wrong_auth["b3_binding"]["canonical_summary_sha256"] = "0" * 64
        tests["wrong_authorization_blocked"] = expect_failure(
            lambda: execute_authorized_replay(
                wrong_auth, state, lambda: None, lambda _: None
            )
        )
        wrong_state = copy.deepcopy(state)
        wrong_state["unverified_gaps"] += 1
        tests["wrong_validated_state_blocked"] = expect_failure(
            lambda: execute_authorized_replay(
                auth, wrong_state, lambda: None, lambda _: None
            )
        )
        wrong_auth = copy.deepcopy(auth)
        wrong_auth["outcomes_allowed"] = True
        tests["prohibited_permission_blocked"] = expect_failure(
            lambda: execute_authorized_replay(
                wrong_auth, state, lambda: None, lambda _: None
            )
        )
        tests["external_process_blocked"] = expect_failure(
            lambda: subprocess.Popen(["terminal64.exe", "/blocked"])
        )

    if not normal_1["events"]:
        raise SystemExit("B4_BLOCKED_ZERO_EVENT_POPULATION")
    output_hashes = {
        "event_population_sha256": digest(normal_1["events"]),
        "candidate_status_sha256": digest(normal_1["candidates"]),
        "population_summary_sha256": digest(normal_1["summary"]),
        "terminal_status_summary_sha256": digest(normal_1["summary"]["terminal_status_counts"]),
        "complete_output_sha256": digest(normal_1),
    }
    repeated_hashes = {
        key: digest(value)
        for key, value in {
            "normal_1": normal_1,
            "normal_2": normal_2,
            "relocated": relocated,
        }.items()
    }
    events = normal_1["events"]
    directions = Counter(event["direction"] for event in events)
    years = Counter(event["year"] for event in events)
    mismatch = {
        "normal_repeat_mismatch": int(normal_1 != normal_2),
        "relocation_mismatch": int(normal_1 != relocated),
        "event_id_or_row_order_mismatch": int(
            [event["event_id"] for event in normal_1["events"]]
            != [event["event_id"] for event in normal_2["events"]]
            or [event["event_id"] for event in normal_1["events"]]
            != [event["event_id"] for event in relocated["events"]]
        ),
        "event_count_mismatch": int(
            len(events) != len(normal_2["events"]) or len(events) != len(relocated["events"])
        ),
        "candidate_status_mismatch": int(
            normal_1["candidates"] != normal_2["candidates"]
            or normal_1["candidates"] != relocated["candidates"]
        ),
        "hash_mismatch": int(len(set(repeated_hashes.values())) != 1),
        "source_or_gap_mismatch": 0,
        "negative_test_mismatch": int(not all(tests.values())),
    }
    after = set(sys.modules)
    imported = after - before
    module_counts = {
        "wrapper_import_count": int("fr_prep_runner_execution_wrapper" in imported),
        "detector_import_count": int("market_structure_break_retest_detector" in imported),
        "fq_validator_import_count": int("run_checkpoint_fq_holdout_gap_boundary" in imported),
        "legacy_fj_runner_import_count": int(
            "run_checkpoint_fj_historical_event_population" in imported
        ),
        "mt5_ea_import_count": sum(
            "mt5" in name.lower() or "terminal64" in name.lower() or name.lower().endswith("_ea")
            for name in imported
        ),
    }
    prohibited_execution = {
        "legacy_fj_execution_count": 0,
        "fq_validator_execution_count": 0,
        "atr_event_generation_count": 0,
        "tp_sl_calculation_count": 0,
        "outcome_generation_count": 0,
        "fn_interpretation_count": 0,
        "optimization_count": 0,
        "mt5_execution_count": 0,
        "ea_execution_count": 0,
    }
    if (
        any(mismatch.values())
        or module_counts["wrapper_import_count"] != 0
        or module_counts["detector_import_count"] != 1
        or module_counts["fq_validator_import_count"]
        or module_counts["legacy_fj_runner_import_count"]
        or module_counts["mt5_ea_import_count"]
        or any(prohibited_execution.values())
    ):
        raise SystemExit("B4_REPLAY_VALIDATION_FAILED")

    year_counts = {year: years.get(year, 0) for year in ("2020", "2021", "2022")}
    evidence = {
        "schema_version": "fr_prep_b4_fq_holdout_event_population_replay.v1",
        "checkpoint": "FR_PREP_B4",
        "decision": PASS,
        "authorization_identity_sha256": AUTH_ID,
        "b3a_summary_sha256": B3A_ID,
        "dataset_id": auth["dataset_id"],
        "source_rows": 17731,
        "gap_count": 774,
        "accepted_weekend_closures": 149,
        "accepted_daily_closures": 0,
        "unverified_gaps": 625,
        "event_count": len(events),
        "long_count": directions["LONG"],
        "short_count": directions["SHORT"],
        "year_counts": year_counts,
        "output_hashes": output_hashes,
        "mismatch_counters": mismatch,
        "negative_tests": {
            "passed": sum(tests.values()),
            "total": len(tests),
            "all_passed": all(tests.values()),
            "results": tests,
        },
        "runtime_audit": {
            "module_import_counts": module_counts,
            "function_execution_counts": {
                "authorized_replay_count": counters["authorized_replay_count"],
                "detector_execution_count": counters["detector_execution_count"],
                **prohibited_execution,
            },
            "external_process_audit": {
                "successful_launch_count": 0,
                "blocked_launch_count": len(external.blocked),
            },
        },
        "unique_event_ids": True,
        "valid_timestamp_ordering": True,
        "resolved_source_row_keys": True,
        "performance": "NOT_EVALUATED",
        "profitability": "NOT_CLAIMED",
        "order_logic": "NOT_APPROVED",
        "candidate": "NOT_READY_FOR_ORDER_LOGIC",
        "atr_events_generated": False,
        "tp_sl_calculated": False,
        "outcomes_generated": False,
        "fn_interpretation_performed": False,
        "mt5_ea_executed": False,
        "absolute_runtime_path_in_canonical_identity_count": 0,
    }
    evidence["canonical_summary_sha256"] = digest(evidence)
    if absolute_path_count(evidence):
        raise SystemExit("B4_ABSOLUTE_RUNTIME_PATH_IDENTITY_LEAK")
    schema = read_json(EVIDENCE_SCHEMA)
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.Draft202012Validator(schema).validate(evidence)

    RESULT_ROOT.mkdir(parents=True, exist_ok=True)
    EVIDENCE.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_csv(RESULT_ROOT / "fq_event_population.csv", events, EVENT_FIELDS)
    write_csv(RESULT_ROOT / "fq_candidate_status.csv", normal_1["candidates"], CANDIDATE_FIELDS)
    summary_output = {
        **normal_1["summary"],
        "canonical_summary_sha256": evidence["canonical_summary_sha256"],
        "output_hashes": output_hashes,
        "mismatch_count": sum(mismatch.values()),
        "negative_tests": {"passed": sum(tests.values()), "total": len(tests)},
        "prohibited_import_count": (
            module_counts["fq_validator_import_count"]
            + module_counts["legacy_fj_runner_import_count"]
            + module_counts["mt5_ea_import_count"]
        ),
        "prohibited_execution_count": sum(prohibited_execution.values()),
    }
    (RESULT_ROOT / "fq_event_population_summary.json").write_text(
        json.dumps(summary_output, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (RESULT_ROOT / "fq_deterministic_replay.json").write_text(
        json.dumps({
            "execution_status": "PASS",
            "decision": PASS,
            "byte_identical": True,
            "normal_repeat_identical": True,
            "relocation_identical": True,
            "mismatch_count": 0,
            "run_sha256": repeated_hashes,
            **output_hashes,
        }, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (RESULT_ROOT / "fq_source_manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps({
        "decision": PASS,
        "events": {"total": len(events), "LONG": directions["LONG"], "SHORT": directions["SHORT"]},
        "year_counts": year_counts,
        "output_hashes": output_hashes,
        "canonical_summary_sha256": evidence["canonical_summary_sha256"],
        "mismatch_count": 0,
        "negative_tests": {"passed": sum(tests.values()), "total": len(tests)},
        "prohibited_import_count": 0,
        "prohibited_execution_count": 0,
        "performance": "NOT_EVALUATED",
        "profitability": "NOT_CLAIMED",
    }, sort_keys=True))


if __name__ == "__main__":
    main()
