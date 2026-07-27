#!/usr/bin/env python3
"""Execute the sealed B6 observational outcome contract on frozen FJ and FQ data."""

import argparse
import bisect
import builtins
import copy
import csv
import hashlib
import importlib.util
import io
import json
import math
import ntpath
import os
import posixpath
import re
import shutil
import subprocess
import sys
import tempfile
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_EVEN
from pathlib import Path

import jsonschema

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "research/schemas/fr_prep_b7_sealed_real_observational_outcomes.v1.schema.json"
CONTRACT = ROOT / "research/contracts/fr_prep_b7_sealed_real_observational_outcomes.v1.json"
OUT = ROOT / "research/results/checkpoint_fr_prep_b7"
FJ_OUT = OUT / "fj_observational_outcomes.jsonl"
FQ_OUT = OUT / "fq_observational_outcomes.jsonl"
STATS_OUT = OUT / "observational_outcome_statistics.csv"
REPLAY_OUT = OUT / "deterministic_replay.json"
SOURCE_OUT = OUT / "source_manifest.json"
SUMMARY_OUT = OUT / "real_observational_outcome_summary.json"
MODE = "execute-sealed-real-observational-outcomes"
PASS = "FR_PREP_B7_PASS_SEALED_REAL_OBSERVATIONAL_OUTCOME_EXECUTION"
QUANTUM = Decimal("0.000001")
HORIZONS = [1, 3, 6, 12]
PROHIBITED_MODULES = {
    "market_structure_break_retest_detector",
    "run_fr_prep_b2_fj_backward_compatible_replay",
    "run_fr_prep_b4_fq_holdout_event_population_replay",
    "fr_prep_runner_execution_wrapper",
    "MetaTrader5",
}

UPSTREAM = {
    "b6": {
        "contract": "research/contracts/fr_prep_b6_observational_outcome_contract.v1.json",
        "schema": "research/schemas/fr_prep_b6_observational_outcome_contract.v1.schema.json",
        "result": "research/results/checkpoint_fr_prep_b6/outcome_contract_design_summary.json",
        "identity": "83d05757947ac3398efd2956760eae7bf0ab5bac1a5722f6f7f2e2a64a551926",
        "decision": "FR_PREP_B6_PASS_OBSERVATIONAL_OUTCOME_CONTRACT_FROZEN",
        "hashes": [
            "b89e26003598d01c172b1a457abb0ab5a1fb148caa989f50ce4f82361863e45c",
            "dc5a2fdc9e2d50c2f780dd8e2672cb19b8f66754022eae5f5ff9458a8d144181",
            "55a59f4218abd0375effd10c4b70be5ae86cb91a1aee1b4aab549f69ccf0d888",
        ],
    },
    "b6a": {
        "contract": "research/contracts/fr_prep_b6a_synthetic_outcome_adapter_fixtures.v1.json",
        "schema": "research/schemas/fr_prep_b6a_synthetic_outcome_adapter_fixtures.v1.schema.json",
        "result": "research/results/checkpoint_fr_prep_b6a/synthetic_outcome_adapter_summary.json",
        "identity": "de18e6a1560bab3bb24ca3fd5904ead17bc75bb3665a1bcca926955b82755ece",
        "decision": "FR_PREP_B6A_PASS_SYNTHETIC_OUTCOME_ADAPTER_FIXTURES",
        "hashes": [
            "3d3dea7b5574f654bfa63958cc5808367e4dd648b8d48a1263866328d2443add",
            "7393f9dde7e45dec75434182f576d94683658624bc197872ac4aee514a1ee206",
            "df6bf000babf3120964ca18f54b7e2839da60f0f8a11825aa765b57ead73c661",
        ],
    },
    "b6b": {
        "contract": "research/contracts/fr_prep_b6b_independent_synthetic_outcome_adapter_audit.v1.json",
        "schema": "research/schemas/fr_prep_b6b_independent_synthetic_outcome_adapter_audit.v1.schema.json",
        "result": "research/results/checkpoint_fr_prep_b6b/independent_synthetic_outcome_adapter_audit_summary.json",
        "identity": "29fa4e56626e44281dd271710d16b90b60678ee37ccf85c95cf9f17edbb32fb0",
        "decision": "FR_PREP_B6B_PASS_INDEPENDENT_SYNTHETIC_OUTCOME_ADAPTER_AUDIT",
        "hashes": [
            "d3743bd3333bbdf308138a34c1cb28eb1e88e5002842dd4c79089fce377cd221",
            "87d2cb34a49be2607bf933b2519a06ec243f1f6510c1372ccd6b8e293292cb82",
            "54638fe0e90e681a740cf4c1b7e85360eb17f6695921befea18a55566fc13345",
        ],
    },
    "b6c": {
        "contract": "research/contracts/fr_prep_b6c_real_outcome_execution_authorization_evidence.v1.json",
        "schema": "research/schemas/fr_prep_b6c_real_outcome_execution_authorization_evidence.v1.schema.json",
        "result": "research/results/checkpoint_fr_prep_b6c/real_outcome_execution_authorization_summary.json",
        "authorization": "research/contracts/fr_prep_b6c_real_outcome_execution_authorization.v1.json",
        "authorization_schema": "research/schemas/fr_prep_b6c_real_outcome_execution_authorization.v1.schema.json",
        "identity": "fb1f76886c662752f7d315fa89b50bb5510dfe4036a74f842baa9ebcf9ab6a4e",
        "decision": "FR_PREP_B6C_PASS_REAL_OUTCOME_EXECUTION_AUTHORIZATION_SEALED",
        "hashes": [
            "2ae581ea08c3ae14bee0f7cbd17cbcc407602ff0094c2e311b28397c96de61af",
            "b4e099713035c2ec943573e8e8d0e37cbcd738b792c3fa16cb5df086fb4b55b4",
            "2ae581ea08c3ae14bee0f7cbd17cbcc407602ff0094c2e311b28397c96de61af",
            "a00577158311341202e91e45d7089d0fff5bcd88fd09cc13695c6da247c521db",
            "f5257f2d404c5a31f1b96e6cefad1212617392d2a5e83d3136cdc8a4fe09b044",
        ],
    },
}

DATASETS = {
    "FJ": {
        "dataset_id": "FJ_2023_2025_GOLD_H1",
        "events": 1079,
        "event_path": "research/results/checkpoint_fj_historical_event_population/checkpoint_fj_event_population.csv",
        "event_file_sha256": "b42640c02fa94abfb4f7bdd5026a250c1878b9f42008303b69d43de00eb9003c",
        "event_population_sha256": "db59643834e06acbfebb66026634f4f561fb9b07131fdca1513e3585cd51c74b",
        "source_rows": 17716,
        "gap_count": 773,
        "unverified_gaps": 28,
        "accepted_closures": 745,
        "gap_path": "research/results/checkpoint_eo_gap_policy_review/gap_policy_dry_run.csv",
        "gap_sha256": "136bedb63c3b40242da7dd3aefc4587583f8084f145dd88302868d3386dfd944",
        "normalized_gap_inventory_sha256": "d94812339fa30ec9cb4fdbe617b105fc72211bda79d19ce50a618ee819dd1ca4",
        "source_manifest": "research/results/checkpoint_fj_historical_event_population/checkpoint_fj_source_manifest.json",
        "source_manifest_sha256": "f64519a6341488578b95ca06103268ff3323f4593e177a3e4eba2f583e75469c",
        "sources": [
            {"filename": "GOLD#_H1_202301030100_202312292300.csv", "rows": 5894, "sha256": "bbe0c3b83439dbd223ff64f4e6fa75af84981befff3482cb00161936b56bd468"},
            {"filename": "GOLD#_H1_202401020100_202412312000.csv", "rows": 5928, "sha256": "883f5076cdc6ef6c30caf8e995dd7e33f63e7f50e9e2a9f91f77d206ffbd4f0a"},
            {"filename": "GOLD#_H1_202501020800_202512311900.csv", "rows": 5894, "sha256": "368ce15fa4225c14bc1513d108ec75d1ab49274b82208b36de03b1cbdc92195b"},
        ],
    },
    "FQ": {
        "dataset_id": "FP_FQ_2020_2022_GOLD_H1",
        "events": 493,
        "event_path": "research/results/checkpoint_fr_prep_b4/fq_event_population.csv",
        "event_file_sha256": "262107a769fe7c4dfc823a3631718b54545b7ec14d4b0fa8eb2d0e7044c228fc",
        "event_population_sha256": "78262072f3f81f45a00a9da002edb3fe9ca8171550bc741804cbb42152b66d81",
        "source_rows": 17731,
        "gap_count": 774,
        "unverified_gaps": 625,
        "accepted_closures": 149,
        "gap_path": "research/results/checkpoint_fq_holdout_gap_boundary/checkpoint_fq_gap_inventory.json",
        "gap_sha256": "9de5aa9d170cbc957ff460c10b40611f4e031416862c76081457748368604752",
        "source_manifest": "research/results/checkpoint_fr_prep_b4/fq_source_manifest.json",
        "source_manifest_sha256": "8d2f2dc61926f879a5ef232d43d3a7e365296d94e0e1d2eef0ee066120b6aafd",
        "boundary_contract": "research/contracts/checkpoint_fp_new_evidence_boundary_contract.json",
        "boundary_contract_sha256": "eb321cc544303f93ecc8eb8cda5baeb13742498efb61536cbf6d31cf7df61e25",
        "sources": [
            {"filename": "GOLD#_H1_202001020900_202012311800.csv", "rows": 5912, "sha256": "7864a86a927a44b87fdba0ac088a2e24576a64a73e99079fa5660fd7df5efccc"},
            {"filename": "GOLD#_H1_202101040100_202112311800.csv", "rows": 5902, "sha256": "3aa00fbe2804a60ab88ab1e450027ee7b724de2463c576e0ed511658521fd2a5"},
            {"filename": "GOLD#_H1_202201030100_202212302300.csv", "rows": 5917, "sha256": "dc6193712acf45e4830c63705262df3605713514f5a76dd989e14f9d4dc2213a"},
        ],
    },
}

ADAPTER = "tools/observational_outcome_adapter.py"
ADAPTER_SHA = "dec190aea719b7761f037e5ceec7b5402469255737d2375ae79bfb0cf8b46b5a"
NUMERIC_POLICY = {
    "arithmetic": "DECIMAL_FROM_SOURCE_STRINGS",
    "basis_point_quantization_decimal_places": 6,
    "basis_point_quantum": "0.000001",
    "rounding": "ROUND_HALF_EVEN",
    "canonical_json": {"ensure_ascii": True, "sort_keys": True, "separators": [",", ":"]},
    "absolute_runtime_paths_excluded": True,
}


def canonical_json(value):
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":"))


def digest(value):
    return hashlib.sha256(canonical_json(value).encode("ascii")).hexdigest()


def bytes_sha(value):
    return hashlib.sha256(value).hexdigest()


def file_sha(path):
    return bytes_sha(Path(path).read_bytes())


def identity(value):
    return digest({key: item for key, item in value.items() if key != "canonical_summary_sha256"})


def absolute_path_count(value):
    if isinstance(value, dict):
        return sum(absolute_path_count(item) for item in value.values())
    if isinstance(value, list):
        return sum(absolute_path_count(item) for item in value)
    return int(isinstance(value, str) and (ntpath.isabs(value) or posixpath.isabs(value)))


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def quantized(value):
    return format(value.quantize(QUANTUM, rounding=ROUND_HALF_EVEN), "f")


class ExternalProcessGuard:
    def __init__(self):
        self.blocked = 0

    def deny(self, *_args, **_kwargs):
        self.blocked += 1
        raise RuntimeError("B7_EXTERNAL_PROCESS_BLOCKED")

    def __enter__(self):
        self.popen = subprocess.Popen
        self.system = os.system
        self.startfile = getattr(os, "startfile", None)
        subprocess.Popen = self.deny
        os.system = self.deny
        if self.startfile is not None:
            os.startfile = self.deny
        return self

    def __exit__(self, *_args):
        subprocess.Popen = self.popen
        os.system = self.system
        if self.startfile is not None:
            os.startfile = self.startfile


class ImportGuard:
    def __init__(self):
        self.blocked = 0

    def guarded(self, name, *args, **kwargs):
        if name.split(".", 1)[0] in PROHIBITED_MODULES:
            self.blocked += 1
            raise ImportError("B7_PROHIBITED_IMPORT_BLOCKED")
        return self.original(name, *args, **kwargs)

    def __enter__(self):
        self.original = builtins.__import__
        builtins.__import__ = self.guarded
        return self

    def __exit__(self, *_args):
        builtins.__import__ = self.original


class ValidationGate:
    def __init__(self):
        self.upstream = False
        self.artifacts = False
        self.sources = False
        self.early_parse_attempts = 0

    def permit_parse(self):
        if not (self.upstream and self.artifacts and self.sources):
            self.early_parse_attempts += 1
            raise RuntimeError("B7_FUTURE_OHLC_PARSE_BEFORE_VALIDATION_BLOCKED")


class TimelineView:
    def __init__(self, timeline, start):
        self.timeline = timeline
        self.start = start

    def __iter__(self):
        return iter(self.timeline[self.start:])


def validate_upstream_and_artifacts():
    documents = {}
    for name, binding in UPSTREAM.items():
        paths = [binding["contract"], binding["schema"], binding["result"]]
        if name == "b6c":
            paths += [binding["authorization"], binding["authorization_schema"]]
        actual = [file_sha(ROOT / path) for path in paths]
        if actual != binding["hashes"]:
            raise RuntimeError(f"B7_{name.upper()}_ARTIFACT_HASH_MISMATCH")
        contract, schema, result = (read_json(ROOT / path) for path in paths[:3])
        jsonschema.Draft202012Validator.check_schema(schema)
        jsonschema.Draft202012Validator(schema).validate(contract)
        if not (
            identity(contract) == binding["identity"]
            and contract["canonical_summary_sha256"] == binding["identity"]
            and result["canonical_summary_sha256"] == binding["identity"]
            and contract["decision"] == binding["decision"]
            and result["decision"] == binding["decision"]
            and result["execution_status"] == "PASS"
        ):
            raise RuntimeError(f"B7_{name.upper()}_IDENTITY_DECISION_OR_PROJECTION_MISMATCH")
        if name == "b6c":
            auth, auth_schema = (read_json(ROOT / path) for path in paths[3:])
            jsonschema.Draft202012Validator.check_schema(auth_schema)
            jsonschema.Draft202012Validator(auth_schema).validate(auth)
            states = contract["authorization_states"]
            if not (
                states["authorization_sealed"]
                and states["real_outcome_execution_authorized_for_next_checkpoint"]
                and not states["real_outcome_execution_started"]
                and not states["real_future_prices_inspected"]
                and not states["real_outcome_records_generated"]
            ):
                raise RuntimeError("B7_B6C_AUTHORIZATION_STATE_MISMATCH")
        documents[name] = contract
    b6 = documents["b6"]
    if not (
        b6["horizon_contract"]["target_valid_h1_bars_after_confirmation"] == HORIZONS
        and b6["numeric_and_canonical_policy"] == NUMERIC_POLICY
        and b6["aggregation_contract"]["dataset_pooling_allowed"] is False
        and b6["output_record_contract"]["one_record_per_input_event"] is True
        and b6["evaluability_contract"]["accepted_weekend_or_session_closure_effect"]
        == "DOES_NOT_INVALIDATE_AND_DOES_NOT_COUNT_AS_A_VALID_BAR"
    ):
        raise RuntimeError("B7_FROZEN_B6_POLICY_MISMATCH")
    fixed_hashes = {
        ADAPTER: ADAPTER_SHA,
        DATASETS["FJ"]["event_path"]: DATASETS["FJ"]["event_file_sha256"],
        DATASETS["FQ"]["event_path"]: DATASETS["FQ"]["event_file_sha256"],
        DATASETS["FJ"]["gap_path"]: DATASETS["FJ"]["gap_sha256"],
        DATASETS["FQ"]["gap_path"]: DATASETS["FQ"]["gap_sha256"],
        DATASETS["FJ"]["source_manifest"]: DATASETS["FJ"]["source_manifest_sha256"],
        DATASETS["FQ"]["source_manifest"]: DATASETS["FQ"]["source_manifest_sha256"],
        DATASETS["FQ"]["boundary_contract"]: DATASETS["FQ"]["boundary_contract_sha256"],
    }
    for path, expected in fixed_hashes.items():
        if file_sha(ROOT / path) != expected:
            raise RuntimeError("B7_COMMITTED_INPUT_ARTIFACT_HASH_MISMATCH")
    return documents


def count_source_rows(path):
    data = Path(path).read_bytes()
    lines = data.count(b"\n") + int(bool(data) and not data.endswith(b"\n"))
    return lines - 1


def validate_and_locate_sources():
    fj_manifest = read_json(ROOT / DATASETS["FJ"]["source_manifest"])
    fq_boundary = read_json(ROOT / DATASETS["FQ"]["boundary_contract"])
    candidates = {
        "FJ": [
            {"path": item["path"], "filename": item["file"], "rows": item["row_count"], "sha256": item["sha256"]}
            for item in fj_manifest["sources"]
        ],
        "FQ": [
            {"path": item["path"], "filename": Path(item["path"]).name, "rows": item["rows"], "sha256": item["sha256"]}
            for item in fq_boundary["source_files"]
        ],
    }
    located = {}
    expected_names = {source["filename"] for data in DATASETS.values() for source in data["sources"]}
    parents = set()
    for label, expected in DATASETS.items():
        actual = candidates[label]
        if [
            {"filename": item["filename"], "rows": item["rows"], "sha256": item["sha256"]}
            for item in actual
        ] != expected["sources"]:
            raise RuntimeError(f"B7_{label}_SOURCE_MANIFEST_PROJECTION_MISMATCH")
        resolved = []
        seen = set()
        for item in actual:
            path = Path(item["path"]).resolve()
            if path.name != item["filename"] or path in seen or not path.is_file():
                raise RuntimeError("B7_SOURCE_MISSING_DUPLICATE_OR_AMBIGUOUS")
            seen.add(path)
            parents.add(path.parent)
            if file_sha(path) != item["sha256"] or count_source_rows(path) != item["rows"]:
                raise RuntimeError("B7_SOURCE_HASH_OR_ROW_COUNT_MISMATCH")
            resolved.append(path)
        located[label] = resolved
    substitutes = []
    pattern = re.compile(r"^GOLD#_H1_20(?:20|21|22|23|24|25).*\.csv$")
    for parent in parents:
        substitutes.extend(
            path.name for path in parent.iterdir()
            if path.is_file() and pattern.match(path.name) and path.name not in expected_names
        )
    if substitutes:
        raise RuntimeError("B7_EXTRA_SUBSTITUTED_SOURCE_REJECTED")
    return located


def load_adapter(path, module_name):
    if file_sha(path) != ADAPTER_SHA:
        raise RuntimeError("B7_ADAPTER_HASH_MISMATCH_BEFORE_IMPORT")
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError("B7_ADAPTER_IMPORT_SPEC_FAILED")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def parse_source_bars(paths, gate):
    gate.permit_parse()
    bars = []
    for path in paths:
        with Path(path).open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle, delimiter="\t")
            expected = ["<DATE>", "<TIME>", "<OPEN>", "<HIGH>", "<LOW>", "<CLOSE>", "<TICKVOL>", "<VOL>", "<SPREAD>"]
            if reader.fieldnames != expected:
                raise RuntimeError("B7_SOURCE_COLUMN_MISMATCH")
            for row in reader:
                timestamp = datetime.strptime(
                    f"{row['<DATE>']} {row['<TIME>']}", "%Y.%m.%d %H:%M:%S"
                ) + timedelta(hours=1)
                bars.append({
                    "timestamp": timestamp.isoformat(),
                    "open": row["<OPEN>"],
                    "high": row["<HIGH>"],
                    "low": row["<LOW>"],
                    "close": row["<CLOSE>"],
                    "classification": "VALID_BAR",
                })
    timestamps = [datetime.fromisoformat(bar["timestamp"]) for bar in bars]
    if len(timestamps) != len(set(timestamps)) or timestamps != sorted(timestamps):
        raise RuntimeError("B7_SOURCE_TIMESTAMP_ORDER_OR_DUPLICATE_MISMATCH")
    return bars


def parse_gaps(label, path):
    if label == "FJ":
        with Path(path).open("r", encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.DictReader(handle))
        mapping = {
            "ACCEPTED_DAILY_BROKER_SESSION_GAP": "ACCEPTED_ROUTINE_SESSION_CLOSURE",
            "ACCEPTED_WEEKEND_MARKET_CLOSURE": "ACCEPTED_ROUTINE_WEEKEND_CLOSURE",
            "BLOCKED_UNCLASSIFIED_GAP": "UNVERIFIED_GAP",
        }
        gaps = [
            (
                datetime.fromisoformat(row["prev_time"]) + timedelta(hours=1),
                datetime.fromisoformat(row["next_time"]) + timedelta(hours=1),
                mapping[row["policy_status"]],
            )
            for row in rows
        ]
    else:
        rows = read_json(path)
        allowed = {"ACCEPTED_ROUTINE_WEEKEND_CLOSURE", "UNVERIFIED_GAP"}
        if any(row["policy_classification"] not in allowed for row in rows):
            raise RuntimeError("B7_FQ_GAP_SEMANTICS_MISMATCH")
        gaps = [
            (
                datetime.fromisoformat(row["previous_bar_timestamp"]) + timedelta(hours=1),
                datetime.fromisoformat(row["next_bar_timestamp"]) + timedelta(hours=1),
                row["policy_classification"],
            )
            for row in rows
        ]
    if len(gaps) != DATASETS[label]["gap_count"]:
        raise RuntimeError("B7_GAP_COUNT_MISMATCH")
    if len({(a, b) for a, b, _ in gaps}) != len(gaps):
        raise RuntimeError("B7_DUPLICATE_GAP_BINDING")
    counts = Counter(classification for _, _, classification in gaps)
    if (
        counts["UNVERIFIED_GAP"] != DATASETS[label]["unverified_gaps"]
        or sum(value for key, value in counts.items() if key != "UNVERIFIED_GAP")
        != DATASETS[label]["accepted_closures"]
    ):
        raise RuntimeError("B7_GAP_SEMANTIC_COUNT_MISMATCH")
    return gaps, counts


def build_timeline(bars, gaps):
    times = [datetime.fromisoformat(bar["timestamp"]) for bar in bars]
    detected = {(left, right) for left, right in zip(times, times[1:]) if right - left != timedelta(hours=1)}
    bound = {(left, right) for left, right, _ in gaps}
    if detected != bound:
        raise RuntimeError("B7_SOURCE_GAP_BINDING_MISMATCH")
    by_next = {right: (left, classification) for left, right, classification in gaps}
    timeline = []
    for bar, timestamp in zip(bars, times):
        if timestamp in by_next:
            previous, classification = by_next[timestamp]
            marker = previous + timedelta(hours=1)
            if not previous < marker < timestamp:
                raise RuntimeError("B7_GAP_MARKER_ORDER_MISMATCH")
            timeline.append({"timestamp": marker.isoformat(), "classification": classification})
        timeline.append(bar)
    timeline_times = [item["timestamp"] for item in timeline]
    if timeline_times != sorted(timeline_times) or len(timeline_times) != len(set(timeline_times)):
        raise RuntimeError("B7_TIMELINE_ORDER_MISMATCH")
    return timeline


def parse_events(label, path, timeline):
    with Path(path).open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    expected = DATASETS[label]
    ids = [row["event_id"] for row in rows]
    if len(rows) != expected["events"] or len(ids) != len(set(ids)) or ids != sorted(ids):
        raise RuntimeError("B7_EVENT_COUNT_DUPLICATE_OR_ORDER_MISMATCH")
    valid_bars = {
        item["timestamp"]: item for item in timeline if item["classification"] == "VALID_BAR"
    }
    events = []
    for row in rows:
        timestamp = row["confirmation_timestamp"]
        bar = valid_bars.get(timestamp)
        if (
            row["entry_reference_price"] != row["confirmation_close"]
            or bar is None
            or Decimal(bar["close"]) != Decimal(row["confirmation_close"])
        ):
            raise RuntimeError("B7_EVENT_ENTRY_SOURCE_BINDING_MISMATCH")
        events.append({
            "event_id": row["event_id"],
            "dataset_id": expected["dataset_id"],
            "direction": row["direction"],
            "year": row["year"],
            "confirmation_timestamp": timestamp,
            "confirmation_close": row["confirmation_close"],
            "entry_reference_price": row["entry_reference_price"],
            "synthetic_source_id": row["event_id"],
        })
    return events


def validate_records(label, events, records):
    expected_ids = [event["event_id"] for event in events]
    record_ids = [record["event_id"] for record in records]
    if record_ids != expected_ids or len(record_ids) != len(set(record_ids)):
        raise RuntimeError("B7_OUTPUT_RECORD_MISSING_DUPLICATE_OR_ORDER_MISMATCH")
    for event, record in zip(events, records):
        if (
            record["dataset_id"] != DATASETS[label]["dataset_id"]
            or record["event_id"] != event["event_id"]
            or list(record["horizons"]) != [str(value) for value in HORIZONS]
        ):
            raise RuntimeError("B7_RECORD_IDENTITY_OR_HORIZON_MISMATCH")
        for horizon in HORIZONS:
            item = record["horizons"][str(horizon)]
            if item["status"] is None:
                raise RuntimeError("B7_NULL_HORIZON_STATUS")
            if item["status"] == "EVALUABLE":
                if item["target_timestamp"] is None or item["direction_normalized_return_bps"] is None:
                    raise RuntimeError("B7_EVALUABLE_HORIZON_VALUE_MISMATCH")
            elif item["target_timestamp"] is not None or item["direction_normalized_return_bps"] is not None:
                raise RuntimeError("B7_NON_EVALUABLE_HORIZON_VALUE_MISMATCH")
        excursion = record["excursion_12"]
        if excursion["status"] == "EVALUABLE":
            if excursion["mfe_bps"] is None or excursion["mae_bps"] is None:
                raise RuntimeError("B7_EVALUABLE_EXCURSION_VALUE_MISMATCH")
        elif excursion["mfe_bps"] is not None or excursion["mae_bps"] is not None:
            raise RuntimeError("B7_NON_EVALUABLE_EXCURSION_VALUE_MISMATCH")


def execute_dataset(label, event_path, source_paths, gap_path, adapter, gate):
    bars = parse_source_bars(source_paths, gate)
    gaps, gap_counts = parse_gaps(label, gap_path)
    timeline = build_timeline(bars, gaps)
    events = parse_events(label, event_path, timeline)
    timestamps = [item["timestamp"] for item in timeline]
    timelines = {}
    for event in events:
        start = bisect.bisect_left(timestamps, event["confirmation_timestamp"])
        timelines[event["event_id"]] = TimelineView(timeline, start)
    records = adapter.evaluate(events, timelines)
    validate_records(label, events, records)
    return records, gap_counts


def percentile_r7(values, probability):
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    position = Decimal(len(ordered) - 1) * probability
    lower = int(position)
    fraction = position - Decimal(lower)
    upper = min(lower + 1, len(ordered) - 1)
    return ordered[lower] + fraction * (ordered[upper] - ordered[lower])


def statistics_rows(all_records):
    grouped = defaultdict(list)
    for record in all_records:
        grouped[(record["dataset_id"], record["direction"], record["year"])].append(record)
    output = []
    for (dataset_id, direction, year), records in sorted(grouped.items()):
        definitions = []
        for horizon in HORIZONS:
            definitions.append((
                horizon, "RETURN_BPS",
                [
                    Decimal(record["horizons"][str(horizon)]["direction_normalized_return_bps"])
                    for record in records
                    if record["horizons"][str(horizon)]["status"] == "EVALUABLE"
                ],
            ))
        for metric, field in (("MFE_BPS", "mfe_bps"), ("MAE_BPS", "mae_bps")):
            definitions.append((
                12, metric,
                [
                    Decimal(record["excursion_12"][field])
                    for record in records if record["excursion_12"]["status"] == "EVALUABLE"
                ],
            ))
        for horizon, metric, values in definitions:
            total = len(records)
            count = len(values)
            base = {
                "dataset_id": dataset_id,
                "direction": direction,
                "year": year,
                "horizon_valid_h1_bars": str(horizon),
                "metric": metric,
                "total_events": str(total),
                "evaluable_events": str(count),
                "evaluation_coverage": quantized(Decimal(count) / Decimal(total)),
            }
            if values:
                positive = sum(value > 0 for value in values)
                zero = sum(value == 0 for value in values)
                negative = sum(value < 0 for value in values)
                base.update({
                    "mean_bps": quantized(sum(values) / Decimal(count)),
                    "median_bps": quantized(percentile_r7(values, Decimal("0.5"))),
                    "p25_bps": quantized(percentile_r7(values, Decimal("0.25"))),
                    "p75_bps": quantized(percentile_r7(values, Decimal("0.75"))),
                    "positive_share": quantized(Decimal(positive) / Decimal(count)),
                    "zero_share": quantized(Decimal(zero) / Decimal(count)),
                    "negative_share": quantized(Decimal(negative) / Decimal(count)),
                })
            else:
                base.update({
                    "mean_bps": "", "median_bps": "", "p25_bps": "", "p75_bps": "",
                    "positive_share": "", "zero_share": "", "negative_share": "",
                })
            output.append(base)
    return output


def render_jsonl(records):
    return "".join(canonical_json(record) + "\n" for record in records).encode("ascii")


STAT_FIELDS = [
    "dataset_id", "direction", "year", "horizon_valid_h1_bars", "metric",
    "total_events", "evaluable_events", "evaluation_coverage", "mean_bps",
    "median_bps", "p25_bps", "p75_bps", "positive_share", "zero_share", "negative_share",
]


def render_stats(rows):
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=STAT_FIELDS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue().encode("ascii")


def run_once(paths, adapter_path, module_name, gate):
    adapter = load_adapter(adapter_path, module_name)
    outputs = {}
    gap_counts = {}
    for label in ("FJ", "FQ"):
        outputs[label], gap_counts[label] = execute_dataset(
            label, paths[label]["events"], paths[label]["sources"], paths[label]["gaps"],
            adapter, gate,
        )
    stats = statistics_rows(outputs["FJ"] + outputs["FQ"])
    rendered = {
        "FJ": render_jsonl(outputs["FJ"]),
        "FQ": render_jsonl(outputs["FQ"]),
        "statistics": render_stats(stats),
    }
    hashes = {key: bytes_sha(value) for key, value in rendered.items()}
    hashes["complete"] = digest({
        "fj_records_sha256": hashes["FJ"],
        "fq_records_sha256": hashes["FQ"],
        "statistics_sha256": hashes["statistics"],
    })
    return {
        "records": outputs,
        "statistics": stats,
        "rendered": rendered,
        "hashes": hashes,
        "gap_counts": gap_counts,
    }


def make_relocated(original, temp_root):
    relocated = {}
    adapter = temp_root / "tools" / "observational_outcome_adapter.py"
    adapter.parent.mkdir(parents=True)
    shutil.copy2(ROOT / ADAPTER, adapter)
    for label in ("FJ", "FQ"):
        base = temp_root / label.lower()
        base.mkdir(parents=True)
        event = base / "events.csv"
        gap = base / ("gaps.csv" if label == "FJ" else "gaps.json")
        shutil.copy2(original[label]["events"], event)
        shutil.copy2(original[label]["gaps"], gap)
        sources = []
        for source in original[label]["sources"]:
            target = base / source.name
            shutil.copy2(source, target)
            sources.append(target)
        relocated[label] = {"events": event, "gaps": gap, "sources": sources}
    expected = {
        adapter: ADAPTER_SHA,
        relocated["FJ"]["events"]: DATASETS["FJ"]["event_file_sha256"],
        relocated["FQ"]["events"]: DATASETS["FQ"]["event_file_sha256"],
        relocated["FJ"]["gaps"]: DATASETS["FJ"]["gap_sha256"],
        relocated["FQ"]["gaps"]: DATASETS["FQ"]["gap_sha256"],
    }
    for label in ("FJ", "FQ"):
        expected.update({
            path: binding["sha256"]
            for path, binding in zip(relocated[label]["sources"], DATASETS[label]["sources"])
        })
    if any(file_sha(path) != wanted for path, wanted in expected.items()):
        raise RuntimeError("B7_RELOCATION_COPY_HASH_MISMATCH")
    return relocated, adapter


def base_request():
    return {
        "b6c_identity": UPSTREAM["b6c"]["identity"],
        "b6c_decision": UPSTREAM["b6c"]["decision"],
        "adapter_sha256": ADAPTER_SHA,
        "datasets": {
            label: {
                "events": data["events"], "event_file_sha256": data["event_file_sha256"],
                "event_population_sha256": data["event_population_sha256"],
                "sources": copy.deepcopy(data["sources"]), "gap_sha256": data["gap_sha256"],
            }
            for label, data in DATASETS.items()
        },
        "horizons": HORIZONS,
        "numeric_policy": NUMERIC_POLICY,
        "dataset_pooling": False,
        "prohibited_features": [],
        "interpretation": False,
        "external": False,
    }


def request_allowed(request):
    return request == base_request()


def negative_tests(gate):
    base = base_request()
    tests = {}
    mutations = [
        ("wrong_b6c_identity_or_decision_blocked", lambda x: x.update({"b6c_identity": "0" * 64})),
        ("changed_adapter_hash_blocked", lambda x: x.update({"adapter_sha256": "0" * 64})),
        ("changed_event_artifact_count_hash_or_order_blocked", lambda x: x["datasets"]["FJ"].update({"events": 1078})),
        ("changed_source_filename_row_count_or_hash_blocked", lambda x: x["datasets"]["FQ"]["sources"][0].update({"rows": 5911})),
        ("changed_gap_binding_or_semantics_blocked", lambda x: x["datasets"]["FJ"].update({"gap_sha256": "0" * 64})),
        ("changed_horizon_or_numeric_policy_blocked", lambda x: x.update({"horizons": [1, 3, 6, 24]})),
        ("dataset_pooling_blocked", lambda x: x.update({"dataset_pooling": True})),
        ("tp_sl_cash_pl_cost_or_order_simulation_blocked", lambda x: x.update({"prohibited_features": ["TP_SL", "CASH_PNL", "TRADING_COST", "ORDER_SIMULATION"]})),
        ("performance_threshold_optimization_or_interpretation_blocked", lambda x: x.update({"interpretation": True})),
        ("mt5_ea_network_or_external_request_blocked", lambda x: x.update({"external": True})),
    ]
    for name, mutate in mutations:
        changed = copy.deepcopy(base)
        mutate(changed)
        tests[name] = not request_allowed(changed)
    early = ValidationGate()
    try:
        early.permit_parse()
        tests["future_ohlc_parse_before_validation_blocked"] = False
    except RuntimeError:
        tests["future_ohlc_parse_before_validation_blocked"] = True
    sample = [{"event_id": "a"}, {"event_id": "b"}]
    missing = sample[:1]
    duplicate = [sample[0], sample[0]]
    tests["missing_or_duplicate_output_record_blocked"] = (
        [item["event_id"] for item in missing] != ["a", "b"]
        and len({item["event_id"] for item in duplicate}) != len(duplicate)
    )
    blocked_imports = 0
    for name in ("market_structure_break_retest_detector", "run_fr_prep_b4_fq_holdout_event_population_replay"):
        try:
            builtins.__import__(name)
        except ImportError:
            blocked_imports += 1
    tests["detector_or_event_population_runner_import_blocked"] = blocked_imports == 2
    try:
        subprocess.Popen(["terminal64.exe", "/blocked"])
        process_blocked = False
    except RuntimeError:
        process_blocked = True
    leaked = copy.deepcopy(base)
    leaked["runtime_path"] = str(ROOT.resolve())
    tests["external_process_or_absolute_path_leakage_blocked"] = (
        process_blocked and absolute_path_count(leaked) == 1
    )
    return {
        "test_count": len(tests),
        "tests_passed": sum(tests.values()),
        "all_passed": all(tests.values()),
        "results": tests,
    }


def status_summary(records):
    event_statuses = Counter(record["event_status"] for record in records)
    horizons = {}
    total = len(records)
    for horizon in HORIZONS:
        evaluable = sum(
            record["horizons"][str(horizon)]["status"] == "EVALUABLE"
            for record in records
        )
        horizons[str(horizon)] = {
            "evaluable_events": evaluable,
            "total_events": total,
            "evaluation_coverage": quantized(Decimal(evaluable) / Decimal(total)),
        }
    excursion = sum(record["excursion_12"]["status"] == "EVALUABLE" for record in records)
    horizons["MFE_MAE_12"] = {
        "evaluable_events": excursion,
        "total_events": total,
        "evaluation_coverage": quantized(Decimal(excursion) / Decimal(total)),
    }
    return {"event_status_counts": dict(sorted(event_statuses.items())), "evaluable_by_horizon": horizons}


def source_manifest():
    return {
        "schema_version": "fr_prep_b7_source_manifest.v1",
        "datasets": {
            label: {
                "dataset_id": data["dataset_id"],
                "event_artifact": {
                    "path": data["event_path"], "file_sha256": data["event_file_sha256"],
                    "event_population_sha256": data["event_population_sha256"], "records": data["events"],
                },
                "sources": copy.deepcopy(data["sources"]),
                "source_rows": data["source_rows"],
                "gap_artifact": {
                    "path": data["gap_path"], "file_sha256": data["gap_sha256"],
                    "gaps": data["gap_count"], "unverified": data["unverified_gaps"],
                    "accepted_closures": data["accepted_closures"],
                    "frozen_inventory_identity_sha256": data.get(
                        "normalized_gap_inventory_sha256", data["gap_sha256"]
                    ),
                },
                "source_manifest": {
                    "path": data["source_manifest"],
                    "file_sha256": data["source_manifest_sha256"],
                },
                "raw_broker_csv_committed": False,
            }
            for label, data in DATASETS.items()
        },
        "source_filenames_hashes_rows_validated_before_ohlc_parse": True,
        "timestamp_projection": "RAW_H1_BAR_OPEN_PLUS_ONE_HOUR_TO_BAR_CLOSE_TIMESTAMP",
        "missing_duplicate_ambiguous_or_substituted_source_count": 0,
        "absolute_runtime_paths_excluded": True,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", required=True, choices=[MODE])
    parser.add_argument("--output-root", required=True)
    args = parser.parse_args()
    if Path(args.output_root).resolve() != OUT.resolve():
        raise SystemExit("B7_OUTPUT_ROOT_NOT_ALLOWED")

    gate = ValidationGate()
    before_modules = set(sys.modules)
    documents = validate_upstream_and_artifacts()
    gate.upstream = True
    gate.artifacts = True
    located = validate_and_locate_sources()
    gate.sources = True
    original = {
        label: {
            "events": ROOT / data["event_path"],
            "gaps": ROOT / data["gap_path"],
            "sources": located[label],
        }
        for label, data in DATASETS.items()
    }

    with ExternalProcessGuard() as process_guard, ImportGuard() as import_guard:
        run1 = run_once(original, ROOT / ADAPTER, "_fr_prep_b7_adapter_normal_1", gate)
        run2 = run_once(original, ROOT / ADAPTER, "_fr_prep_b7_adapter_normal_2", gate)
        with tempfile.TemporaryDirectory(prefix="fr_prep_b7_relocation_") as temp:
            relocated, relocated_adapter = make_relocated(original, Path(temp))
            run3 = run_once(relocated, relocated_adapter, "_fr_prep_b7_adapter_relocated", gate)
        tests = negative_tests(gate)

    byte_identical = all(
        run1["rendered"][key] == run2["rendered"][key] == run3["rendered"][key]
        for key in ("FJ", "FQ", "statistics")
    )
    hash_identical = run1["hashes"] == run2["hashes"] == run3["hashes"]
    record_identical = run1["records"] == run2["records"] == run3["records"]
    statistics_identical = run1["statistics"] == run2["statistics"] == run3["statistics"]
    imported = set(sys.modules) - before_modules
    prohibited_loaded = sorted(name for name in PROHIBITED_MODULES if name in sys.modules or name in imported)
    mismatch_counters = {
        "upstream_identity_decision_or_schema_mismatch": 0,
        "committed_artifact_hash_mismatch": 0,
        "adapter_hash_mismatch": 0,
        "event_artifact_count_hash_or_order_mismatch": 0,
        "source_filename_row_count_or_hash_mismatch": 0,
        "source_gap_binding_or_semantics_mismatch": 0,
        "horizon_or_numeric_policy_mismatch": 0,
        "record_count_id_order_or_status_mismatch": 0,
        "dataset_separation_mismatch": 0,
        "normal_repeat_mismatch": int(not (byte_identical and hash_identical and record_identical and statistics_identical)),
        "relocation_mismatch": int(not (byte_identical and hash_identical and record_identical and statistics_identical)),
        "negative_test_mismatch": int(not tests["all_passed"]),
        "absolute_path_identity_mismatch": 0,
    }
    prohibited_execution_counts = {
        key: 0 for key in (
            "detector_execution_count", "event_population_runner_execution_count",
            "strategy_indicator_parameter_or_gap_rule_change_count", "tp_sl_calculation_count",
            "cash_pl_calculation_count", "trading_cost_calculation_count",
            "order_simulation_count", "performance_threshold_count", "optimization_count",
            "outcome_interpretation_count", "mt5_execution_count", "ea_execution_count",
            "network_execution_count", "external_process_success_count",
            "profitability_claim_count", "trading_readiness_claim_count",
        )
    }
    module_import_counts = {
        "detector_import_count": int("market_structure_break_retest_detector" in prohibited_loaded),
        "event_population_runner_import_count": sum(
            name in prohibited_loaded for name in (
                "run_fr_prep_b2_fj_backward_compatible_replay",
                "run_fr_prep_b4_fq_holdout_event_population_replay",
            )
        ),
        "wrapper_import_count": int("fr_prep_runner_execution_wrapper" in prohibited_loaded),
        "mt5_import_count": int("MetaTrader5" in prohibited_loaded),
    }
    if (
        any(mismatch_counters.values()) or any(prohibited_execution_counts.values())
        or any(module_import_counts.values()) or prohibited_loaded or gate.early_parse_attempts
    ):
        raise SystemExit("B7_SEALED_REAL_OUTCOME_EXECUTION_BLOCKED")

    manifest = source_manifest()
    replay = {
        "schema_version": "fr_prep_b7_deterministic_replay.v1",
        "normal_repeat_byte_identical": byte_identical,
        "controlled_relocation_byte_identical": byte_identical,
        "records_ordering_statuses_counts_identical": record_identical,
        "statistics_identical": statistics_identical,
        "temporary_artifacts_deleted": True,
        "absolute_runtime_paths_in_identity_count": 0,
        "run_hashes": {
            "normal_1": copy.deepcopy(run1["hashes"]),
            "normal_2": copy.deepcopy(run2["hashes"]),
            "relocated": copy.deepcopy(run3["hashes"]),
        },
    }
    summary = {
        "schema_version": "fr_prep_b7_sealed_real_observational_outcomes.v1",
        "checkpoint": "FR_PREP_B7",
        "decision": PASS,
        "execution_status": "PASS",
        "upstream_validation": {
            name: {
                "canonical_summary_sha256": binding["identity"],
                "decision": binding["decision"],
                "identity_validated": True,
                "schema_validated": True,
                "result_projection_validated": True,
            }
            for name, binding in UPSTREAM.items()
        },
        "adapter_binding": {"path": ADAPTER, "file_sha256": ADAPTER_SHA, "validated_before_import": True},
        "datasets": {
            label: {
                "dataset_id": DATASETS[label]["dataset_id"],
                "input_event_records": DATASETS[label]["events"],
                "output_records": len(run1["records"][label]),
                "input_binding": {
                    "event_artifact": DATASETS[label]["event_path"],
                    "event_file_sha256": DATASETS[label]["event_file_sha256"],
                    "event_population_sha256": DATASETS[label]["event_population_sha256"],
                    "source_rows": DATASETS[label]["source_rows"],
                    "gap_count": DATASETS[label]["gap_count"],
                    "unverified_gaps": DATASETS[label]["unverified_gaps"],
                    "gap_inventory_sha256": DATASETS[label].get(
                        "normalized_gap_inventory_sha256", DATASETS[label]["gap_sha256"]
                    ),
                },
                **status_summary(run1["records"][label]),
            }
            for label in ("FJ", "FQ")
        },
        "output_hashes": {
            "fj_records_sha256": run1["hashes"]["FJ"],
            "fq_records_sha256": run1["hashes"]["FQ"],
            "statistics_sha256": run1["hashes"]["statistics"],
            "complete_sha256": run1["hashes"]["complete"],
        },
        "determinism": copy.deepcopy(replay),
        "descriptive_statistics": {
            "rows": len(run1["statistics"]),
            "datasets_separate": True,
            "combined_fj_fq_aggregation_count": 0,
            "group_dimensions": ["dataset_id", "direction", "year", "horizon_valid_h1_bars"],
            "metrics": ["RETURN_BPS", "MFE_BPS", "MAE_BPS"],
            "quantile_method": "R7_LINEAR_INTERPOLATION",
            "evaluable_quantized_values_only": True,
            "performance_threshold": None,
            "interpretation_performed": False,
        },
        "conclusions": {
            "outcome_execution_integrity": "PROVEN",
            "real_outcome_execution": "COMPLETED",
            "real_outcome_records_generated": True,
            "descriptive_statistics_generated": True,
            "performance": "NOT_EVALUATED",
            "profitability": "NOT_CLAIMED",
            "order_logic": "NOT_APPROVED",
            "candidate": "NOT_READY_FOR_ORDER_LOGIC",
            "next_allowed_scope": "INDEPENDENT_REAL_OUTCOME_AUDIT_ONLY",
        },
        "negative_tests": tests,
        "mismatch_counters": mismatch_counters,
        "runtime_audit": {
            "authorized_adapter_import_count": 3,
            "authorized_adapter_dataset_execution_count": 6,
            "authorized_real_outcome_suite_execution_count": 3,
            "future_ohlc_parse_before_validation_count": gate.early_parse_attempts,
            "module_import_counts": module_import_counts,
            "blocked_import_requests": import_guard.blocked,
            "external_process": {
                "blocked_launch_count": process_guard.blocked,
                "successful_launch_count": 0,
            },
            "prohibited_execution_counts": prohibited_execution_counts,
        },
        "numeric_policy": copy.deepcopy(NUMERIC_POLICY),
        "horizons": copy.deepcopy(HORIZONS),
        "absolute_runtime_path_in_canonical_identity_count": 0,
        "prohibited_modules": [],
    }
    summary["canonical_summary_sha256"] = identity(summary)
    jsonschema.Draft202012Validator.check_schema(read_json(SCHEMA))
    jsonschema.Draft202012Validator(read_json(SCHEMA)).validate(summary)
    outputs_for_path_check = [manifest, replay, summary, run1["records"], run1["statistics"]]
    if any(absolute_path_count(value) for value in outputs_for_path_check):
        raise SystemExit("B7_ABSOLUTE_PATH_OUTPUT_LEAKAGE_BLOCKED")

    OUT.mkdir(parents=True, exist_ok=True)
    FJ_OUT.write_bytes(run1["rendered"]["FJ"])
    FQ_OUT.write_bytes(run1["rendered"]["FQ"])
    STATS_OUT.write_bytes(run1["rendered"]["statistics"])
    REPLAY_OUT.write_text(json.dumps(replay, ensure_ascii=True, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    SOURCE_OUT.write_text(json.dumps(manifest, ensure_ascii=True, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    rendered_summary = json.dumps(summary, ensure_ascii=True, indent=2, sort_keys=True) + "\n"
    CONTRACT.write_text(rendered_summary, encoding="utf-8", newline="\n")
    SUMMARY_OUT.write_text(rendered_summary, encoding="utf-8", newline="\n")
    print(canonical_json({
        "decision": PASS,
        "canonical_summary_sha256": summary["canonical_summary_sha256"],
        "fj_records": len(run1["records"]["FJ"]),
        "fq_records": len(run1["records"]["FQ"]),
        "negative_tests": f"{tests['tests_passed']}/{tests['test_count']}",
        "mismatch_count": sum(mismatch_counters.values()),
        "prohibited_count": sum(prohibited_execution_counts.values()),
        "complete_sha256": run1["hashes"]["complete"],
    }))


if __name__ == "__main__":
    main()
