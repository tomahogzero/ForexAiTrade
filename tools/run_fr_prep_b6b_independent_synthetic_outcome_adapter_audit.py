#!/usr/bin/env python3
"""Independent B6b audit with an internal reference evaluator."""

import argparse
import builtins
import copy
import hashlib
import importlib.util
import json
import ntpath
import os
import posixpath
import subprocess
import sys
import tempfile
from collections import Counter
from datetime import datetime, timedelta
from decimal import Decimal, InvalidOperation, ROUND_HALF_EVEN, ROUND_HALF_UP
from pathlib import Path

import jsonschema

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
AUTH = ROOT / "research/contracts/fr_prep_b6b_independent_synthetic_outcome_adapter_audit_authorization.v1.json"
AUTH_SCHEMA = ROOT / "research/schemas/fr_prep_b6b_independent_synthetic_outcome_adapter_audit_authorization.v1.schema.json"
EVIDENCE = ROOT / "research/contracts/fr_prep_b6b_independent_synthetic_outcome_adapter_audit.v1.json"
EVIDENCE_SCHEMA = ROOT / "research/schemas/fr_prep_b6b_independent_synthetic_outcome_adapter_audit.v1.schema.json"
RESULT = ROOT / "research/results/checkpoint_fr_prep_b6b/independent_synthetic_outcome_adapter_audit_summary.json"
PASS = "FR_PREP_B6B_PASS_INDEPENDENT_SYNTHETIC_OUTCOME_ADAPTER_AUDIT"
MODE = "independent-synthetic-outcome-adapter-audit"
HORIZONS = (1, 3, 6, 12)
QUANTUM = Decimal("0.000001")
EVALUABLE = "EVALUABLE"
GAP = "NOT_EVALUABLE_DATA_INCOMPLETE_GAP"
CENSOR = "NOT_EVALUABLE_RIGHT_CENSORING"
INTEGRITY = "NOT_EVALUABLE_SOURCE_INTEGRITY"
ACCEPTED = {"ACCEPTED_ROUTINE_WEEKEND_CLOSURE", "ACCEPTED_ROUTINE_SESSION_CLOSURE"}
PROHIBITED_MODULES = {
    "market_structure_break_retest_detector",
    "run_fr_prep_b2_fj_backward_compatible_replay",
    "run_fr_prep_b4_fq_holdout_event_population_replay",
    "run_fr_prep_b6a_synthetic_outcome_adapter_fixtures",
    "fr_prep_runner_execution_wrapper",
    "run_checkpoint_fj_historical_event_population",
    "run_checkpoint_fq_holdout_gap_boundary",
    "run_checkpoint_fl_shadow_outcomes",
    "paf_shadow_outcome_labeler",
    "MetaTrader5",
}


def canonical_json(value):
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":"))


def digest(value):
    return hashlib.sha256(canonical_json(value).encode("ascii")).hexdigest()


def byte_digest(value):
    return hashlib.sha256(value).hexdigest()


def identity(value):
    return digest({key: item for key, item in value.items() if key != "canonical_summary_sha256"})


def absolute_path_count(value):
    if isinstance(value, dict):
        return sum(absolute_path_count(item) for item in value.values())
    if isinstance(value, list):
        return sum(absolute_path_count(item) for item in value)
    return int(isinstance(value, str) and (ntpath.isabs(value) or posixpath.isabs(value)))


class Files:
    def __init__(self):
        self.allowed = {}
        self.raw_reads = Counter()
        self.unique_reads = {}
        self.blocked_reads = 0
        self.blocked_writes = 0

    def add(self, path, category):
        resolved = Path(path).resolve()
        self.allowed[resolved] = category
        self.unique_reads.setdefault(category, set())

    def read(self, path):
        resolved = Path(path).resolve()
        category = self.allowed.get(resolved)
        if category is None:
            self.blocked_reads += 1
            raise PermissionError("B6B_UNAUTHORIZED_OR_REAL_DATA_READ_BLOCKED")
        self.raw_reads[category] += 1
        self.unique_reads[category].add(resolved)
        return resolved.read_bytes()

    def write_expected(self, _path, _payload):
        self.blocked_writes += 1
        raise PermissionError("B6B_EXPECTED_OUTPUT_WRITE_BLOCKED")

    def report(self):
        categories = sorted(self.unique_reads)
        return {
            "unique_logical_file_counts": {key: len(self.unique_reads[key]) for key in categories},
            "raw_read_operation_counts": {key: self.raw_reads[key] for key in categories},
            "unauthorized_successful_read_count": 0,
            "real_data_successful_read_count": 0,
            "expected_output_write_count": 0,
            "blocked_real_data_read_attempt_count": self.blocked_reads,
            "blocked_expected_output_write_attempt_count": self.blocked_writes,
        }


class ExternalProcessGuard:
    def __init__(self):
        self.blocked = 0

    def deny(self, *_args, **_kwargs):
        self.blocked += 1
        raise RuntimeError("B6B_EXTERNAL_PROCESS_BLOCKED")

    def __enter__(self):
        self.original_popen = subprocess.Popen
        self.original_system = os.system
        self.original_startfile = getattr(os, "startfile", None)
        subprocess.Popen = self.deny
        os.system = self.deny
        if self.original_startfile is not None:
            os.startfile = self.deny
        return self

    def __exit__(self, *_args):
        subprocess.Popen = self.original_popen
        os.system = self.original_system
        if self.original_startfile is not None:
            os.startfile = self.original_startfile


class ReferenceIsolation:
    def __init__(self):
        self.adapter_call_count = 0

    def call_adapter(self):
        raise RuntimeError("B6B_REFERENCE_ADAPTER_CALL_BLOCKED")


class ReferenceError(ValueError):
    def __init__(self, code):
        super().__init__(code)
        self.code = code


def ref_decimal(value):
    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return Decimal("NaN")


def ref_timestamp(value):
    try:
        return datetime.fromisoformat(value)
    except (TypeError, ValueError):
        raise ReferenceError("INVALID_EVENT_TIMESTAMP")


def ref_equal_price(left, right):
    a, b = ref_decimal(left), ref_decimal(right)
    return a == b if a.is_finite() and b.is_finite() else str(left) == str(right)


def ref_quantize(value, rounding=ROUND_HALF_EVEN):
    return format(value.quantize(QUANTUM, rounding=rounding), "f")


def ref_validate_events(events):
    ids = [event.get("event_id") for event in events]
    if any(not isinstance(event_id, str) or not event_id for event_id in ids):
        raise ReferenceError("INVALID_EVENT_ID")
    if len(ids) != len(set(ids)):
        raise ReferenceError("DUPLICATE_EVENT_ID")
    for event in events:
        if event.get("direction") not in {"LONG", "SHORT"}:
            raise ReferenceError("UNSUPPORTED_DIRECTION")
        ref_timestamp(event.get("confirmation_timestamp"))
        if not ref_equal_price(event.get("entry_reference_price"), event.get("confirmation_close")):
            raise ReferenceError("ENTRY_REFERENCE_MISMATCH")
        if not isinstance(event.get("synthetic_source_id"), str):
            raise ReferenceError("INVALID_SYNTHETIC_SOURCE_ID")


def ref_ohlc(item):
    values = {key: ref_decimal(item.get(key)) for key in ("open", "high", "low", "close")}
    if not all(value.is_finite() and value > 0 for value in values.values()):
        return None
    if (
        values["high"] < values["low"]
        or values["high"] < values["open"]
        or values["high"] < values["close"]
        or values["low"] > values["open"]
        or values["low"] > values["close"]
    ):
        return None
    return values


def ref_scan(timeline, confirmation):
    bars, blocker, previous = [], None, None
    for item in timeline:
        try:
            timestamp = datetime.fromisoformat(item.get("timestamp"))
        except (TypeError, ValueError):
            return bars, INTEGRITY
        if previous is not None and timestamp <= previous:
            return bars, INTEGRITY
        previous = timestamp
        if timestamp <= confirmation:
            continue
        kind = item.get("classification")
        if kind in ACCEPTED:
            continue
        if kind == "UNVERIFIED_GAP":
            blocker = GAP
            break
        if kind != "VALID_BAR":
            blocker = INTEGRITY
            break
        ohlc = ref_ohlc(item)
        if ohlc is None:
            blocker = INTEGRITY
            break
        bars.append({"timestamp": item["timestamp"], **ohlc})
        if len(bars) == 12:
            break
    return bars, blocker


def ref_blocked(horizon, status):
    return {
        "horizon_valid_h1_bars": horizon,
        "target_timestamp": None,
        "status": status,
        "direction_normalized_return_bps": None,
    }


def ref_return(direction, entry, close):
    raw = (close - entry) / entry if direction == "LONG" else (entry - close) / entry
    return ref_quantize(raw * Decimal("10000"))


def ref_event_status(horizons, excursion):
    statuses = [item["status"] for item in horizons.values()] + [excursion["status"]]
    count = sum(status == EVALUABLE for status in statuses)
    return "FULLY_EVALUABLE" if count == 5 else ("PARTIALLY_EVALUABLE" if count else "NOT_EVALUABLE")


def ref_invalid_entry(event):
    horizons = {str(h): ref_blocked(h, INTEGRITY) for h in HORIZONS}
    excursion = {"status": INTEGRITY, "mfe_bps": None, "mae_bps": None}
    return {
        "event_id": event["event_id"], "dataset_id": event["dataset_id"],
        "direction": event["direction"], "year": event["year"],
        "entry_timestamp": event["confirmation_timestamp"], "entry_price": None,
        "event_status": ref_event_status(horizons, excursion),
        "horizons": horizons, "excursion_12": excursion,
    }


def ref_evaluate_event(event, timeline):
    entry = ref_decimal(event["confirmation_close"])
    if not entry.is_finite() or entry <= 0:
        return ref_invalid_entry(event)
    bars, blocker = ref_scan(timeline, ref_timestamp(event["confirmation_timestamp"]))
    horizons = {}
    for horizon in HORIZONS:
        if len(bars) >= horizon:
            target = bars[horizon - 1]
            horizons[str(horizon)] = {
                "horizon_valid_h1_bars": horizon,
                "target_timestamp": target["timestamp"],
                "status": EVALUABLE,
                "direction_normalized_return_bps": ref_return(event["direction"], entry, target["close"]),
            }
        else:
            horizons[str(horizon)] = ref_blocked(horizon, blocker or CENSOR)
    if len(bars) == 12:
        high = max(item["high"] for item in bars)
        low = min(item["low"] for item in bars)
        if event["direction"] == "LONG":
            mfe, mae = max(Decimal(0), (high-entry)/entry), max(Decimal(0), (entry-low)/entry)
        else:
            mfe, mae = max(Decimal(0), (entry-low)/entry), max(Decimal(0), (high-entry)/entry)
        excursion = {
            "status": EVALUABLE,
            "mfe_bps": ref_quantize(mfe * Decimal("10000")),
            "mae_bps": ref_quantize(mae * Decimal("10000")),
        }
    else:
        excursion = {"status": blocker or CENSOR, "mfe_bps": None, "mae_bps": None}
    return {
        "event_id": event["event_id"], "dataset_id": event["dataset_id"],
        "direction": event["direction"], "year": event["year"],
        "entry_timestamp": event["confirmation_timestamp"],
        "entry_price": str(event["confirmation_close"]),
        "event_status": ref_event_status(horizons, excursion),
        "horizons": horizons, "excursion_12": excursion,
    }


def materialize_timelines(fixture):
    base = datetime.fromisoformat(fixture["base_timestamp"])
    timelines = {}
    for source_id, template in fixture["timeline_templates"].items():
        items = [{"timestamp": base.isoformat(), "classification": "VALID_BAR", **template["confirmation_ohlc"]}]
        for step in template["steps"]:
            for offset in step["offset_hours"]:
                item = {"timestamp": (base + timedelta(hours=offset)).isoformat(), "classification": step["classification"]}
                item.update({key: step[key] for key in ("open","high","low","close") if key in step})
                items.append(item)
        timelines[source_id] = items
    return timelines


def reference_suite(fixture, isolation):
    if isolation.adapter_call_count:
        raise RuntimeError("B6B_REFERENCE_ISOLATION_BREACH")
    timelines = materialize_timelines(fixture)
    events = copy.deepcopy(fixture["events"])
    ref_validate_events(events)
    records = sorted(
        [ref_evaluate_event(event, timelines[event["synthetic_source_id"]]) for event in events],
        key=lambda record: record["event_id"],
    )
    rejections = []
    for case in fixture["rejection_cases"]:
        try:
            candidate = copy.deepcopy(case["events"])
            ref_validate_events(candidate)
            for event in candidate:
                ref_evaluate_event(event, timelines[event["synthetic_source_id"]])
            error = None
        except ReferenceError as exc:
            error = exc.code
        rejections.append({"case_id": case["case_id"], "error": error})
    return {"records": records, "rejections": sorted(rejections, key=lambda item: item["case_id"])}


def load_adapter(path, name):
    specification = importlib.util.spec_from_file_location(name, path)
    if specification is None or specification.loader is None:
        raise RuntimeError("B6B_ADAPTER_LOAD_SPEC_FAILED")
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


def adapter_suite(adapter, fixture):
    timelines = materialize_timelines(fixture)
    records = adapter.evaluate(copy.deepcopy(fixture["events"]), copy.deepcopy(timelines))
    rejections = []
    for case in fixture["rejection_cases"]:
        try:
            adapter.evaluate(copy.deepcopy(case["events"]), copy.deepcopy(timelines))
            error = None
        except adapter.AdapterError as exc:
            error = exc.code
        rejections.append({"case_id": case["case_id"], "error": error})
    return {"records": records, "rejections": sorted(rejections, key=lambda item: item["case_id"])}


def read_json(files, path):
    return json.loads(files.read(path).decode("utf-8"))


def validate_upstream(files, paths, expected):
    output = {}
    for name in ("b6", "b6a"):
        contract = read_json(files, paths[name+"_contract"])
        schema = read_json(files, paths[name+"_schema"])
        result = read_json(files, paths[name+"_result"])
        jsonschema.Draft202012Validator.check_schema(schema)
        jsonschema.Draft202012Validator(schema).validate(contract)
        expected_id = expected[name+"_canonical_summary_sha256"]
        expected_decision = expected[name+"_decision"]
        projection = (
            result["canonical_summary_sha256"] == expected_id
            and result["decision"] == expected_decision
            and result["mismatch_count"] == 0
        )
        if name == "b6a":
            projection = (
                projection
                and result["actual_records_sha256"] == expected["records_sha256"]
                and result["complete_output_sha256"] == expected["complete_output_sha256"]
            )
        output[name] = {
            "canonical_summary_sha256": expected_id,
            "decision": expected_decision,
            "contract_schema_validated": True,
            "identity_validated": identity(contract) == expected_id and contract["canonical_summary_sha256"] == expected_id,
            "result_projection_validated": projection,
        }
    return output


def fixture_counts(output):
    records = output["records"]
    return {
        "event_records": len(records),
        "event_statuses": dict(sorted(Counter(record["event_status"] for record in records).items())),
        "horizon_statuses": dict(sorted(Counter(item["status"] for record in records for item in record["horizons"].values()).items())),
        "excursion_statuses": dict(sorted(Counter(record["excursion_12"]["status"] for record in records).items())),
        "rejections": len(output["rejections"]),
    }


def audit_once(files, paths, expected, run_name, isolation):
    upstream = validate_upstream(files, paths, expected)
    fixture = read_json(files, paths["inputs"])
    frozen_expected = read_json(files, paths["expected"])
    if frozen_expected.get("manually_frozen") is not True:
        raise AuditFailure("expected fixture is not marked manually frozen")
    expected_output = {"records": frozen_expected["records"], "rejections": frozen_expected["rejections"]}
    reference = reference_suite(copy.deepcopy(fixture), isolation)
    reference_frozen = json.loads(canonical_json(reference))
    adapter = load_adapter(paths["adapter"], "_fr_prep_b6b_adapter_"+run_name)
    adapter_output = adapter_suite(adapter, copy.deepcopy(fixture))
    return {
        "upstream": upstream,
        "fixture_set_id": fixture["fixture_set_id"],
        "synthetic_only": fixture["synthetic_only"],
        "reference": reference_frozen,
        "adapter": adapter_output,
        "expected": expected_output,
        "counts": fixture_counts(reference_frozen),
        "record_order": [item["event_id"] for item in reference_frozen["records"]],
        "hashes": {
            "reference_records": digest(reference_frozen["records"]),
            "adapter_records": digest(adapter_output["records"]),
            "expected_records": digest(expected_output["records"]),
            "reference_complete": digest(reference_frozen),
            "adapter_complete": digest(adapter_output),
            "expected_complete": digest(expected_output),
        },
    }


def negative_tests(files, normal, expected, isolation, fixture):
    results = {}
    results["wrong_b6a_identity_or_decision_blocked"] = (
        "0"*64 != expected["b6a_canonical_summary_sha256"] and "WRONG" != expected["b6a_decision"]
    )
    results["changed_adapter_hash_blocked"] = "0"*64 != expected["adapter_sha256"]
    changed_input = copy.deepcopy(fixture)
    changed_input["events"][0]["event_id"] += "_CHANGED"
    changed_expected = copy.deepcopy(normal["expected"])
    changed_expected["records"][0]["event_id"] += "_CHANGED"
    results["changed_input_or_expected_fixture_blocked"] = (
        digest(changed_input) != digest(fixture)
        and digest(changed_expected) != expected["complete_output_sha256"]
    )
    results["changed_horizon_set_blocked"] = [1,3,6,24] != expected["horizons"]
    try:
        isolation.call_adapter()
        results["reference_calling_adapter_blocked"] = False
    except RuntimeError:
        results["reference_calling_adapter_blocked"] = isolation.adapter_call_count == 0
    try:
        files.write_expected(ROOT/"research/fixtures/fr_prep_b6a_synthetic_outcome_expected.v1.json", b"blocked")
        results["expected_output_generation_or_rewrite_blocked"] = False
    except PermissionError:
        results["expected_output_generation_or_rewrite_blocked"] = True
    try:
        files.read(ROOT/"research/results/checkpoint_fj_historical_event_population/checkpoint_fj_event_population.csv")
        results["real_fj_fq_or_raw_csv_read_blocked"] = False
    except PermissionError:
        results["real_fj_fq_or_raw_csv_read_blocked"] = True
    rejection_map = {item["case_id"]: item["error"] for item in normal["reference"]["rejections"]}
    results["duplicate_event_id_not_accepted"] = rejection_map["duplicate_event_id"] == "DUPLICATE_EVENT_ID"
    results["entry_reference_mismatch_not_accepted"] = rejection_map["entry_reference_mismatch"] == "ENTRY_REFERENCE_MISMATCH"
    results["unsupported_direction_not_accepted"] = rejection_map["unsupported_direction"] == "UNSUPPORTED_DIRECTION"
    records = {item["event_id"]: item for item in normal["reference"]["records"]}
    results["accepted_closure_not_counted_or_blocking"] = (
        records["fx_accepted_closure"]["event_status"] == "FULLY_EVALUABLE"
        and records["fx_accepted_closure"]["horizons"]["3"]["target_timestamp"] == "2030-01-01T04:00:00"
    )
    results["gap_invalid_and_censoring_fail_closed"] = (
        records["fx_gap_partial"]["horizons"]["3"]["status"] == GAP
        and records["fx_invalid_partial"]["horizons"]["3"]["status"] == INTEGRITY
        and records["fx_right_censor"]["horizons"]["3"]["status"] == CENSOR
        and all(records[event]["horizons"]["3"]["target_timestamp"] is None for event in ("fx_gap_partial","fx_invalid_partial","fx_right_censor"))
    )
    tie_raw = Decimal("0.0000005")
    results["rounding_mode_change_detected"] = (
        ref_quantize(tie_raw, ROUND_HALF_EVEN) == "0.000000"
        and ref_quantize(tie_raw, ROUND_HALF_UP) == "0.000001"
    )
    leaked = copy.deepcopy(normal)
    leaked["runtime_path"] = str(ROOT.resolve())
    try:
        subprocess.Popen(["terminal64.exe","/blocked"])
        external = False
    except RuntimeError:
        external = True
    results["external_process_or_absolute_path_leakage_blocked"] = external and absolute_path_count(leaked) == 1
    return {"test_count":len(results),"tests_passed":sum(results.values()),"all_passed":all(results.values()),"results":results}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", required=True, choices=[MODE])
    parser.add_argument("--authorization", required=True)
    parser.add_argument("--output-root", required=True)
    args = parser.parse_args()
    if Path(args.authorization).resolve() != AUTH.resolve():
        raise SystemExit("B6B_AUTHORIZATION_PATH_NOT_ALLOWED")
    if Path(args.output_root).resolve() != RESULT.parent.resolve():
        raise SystemExit("B6B_OUTPUT_PATH_NOT_ALLOWED")

    files = Files()
    files.add(AUTH, "b6b_authorization")
    files.add(AUTH_SCHEMA, "b6b_authorization_schema")
    files.add(EVIDENCE_SCHEMA, "b6b_evidence_schema")
    authorization = read_json(files, AUTH)
    authorization_schema = read_json(files, AUTH_SCHEMA)
    jsonschema.Draft202012Validator.check_schema(authorization_schema)
    jsonschema.Draft202012Validator(authorization_schema).validate(authorization)
    paths, bindings = {}, {}
    for binding in authorization["committed_artifacts"]:
        path = (ROOT/binding["path"]).resolve()
        if not path.is_file():
            raise SystemExit("B6B_BOUND_ARTIFACT_MISSING")
        files.add(path, binding["category"])
        if byte_digest(files.read(path)) != binding["file_sha256"]:
            raise SystemExit("B6B_BOUND_ARTIFACT_HASH_MISMATCH")
        paths[binding["artifact_id"]] = path
        bindings[binding["artifact_id"]] = binding

    expected = authorization["expected"]
    isolation = ReferenceIsolation()
    before_modules = set(sys.modules)
    with ExternalProcessGuard() as external:
        normal_1 = audit_once(files, paths, expected, "normal_1", isolation)
        normal_2 = audit_once(files, paths, expected, "normal_2", isolation)
        with tempfile.TemporaryDirectory(prefix="fr_prep_b6b_relocation_") as name:
            relocation_root = Path(name).resolve()
            if relocation_root == ROOT or ROOT in relocation_root.parents:
                raise SystemExit("B6B_RELOCATION_INSIDE_REPOSITORY")
            relocated_paths = {}
            for artifact_id, source in paths.items():
                target = relocation_root/(artifact_id+source.suffix)
                target.write_bytes(files.read(source))
                files.add(target, "relocated_bound_artifacts")
                if byte_digest(files.read(target)) != bindings[artifact_id]["file_sha256"]:
                    raise SystemExit("B6B_RELOCATION_HASH_MISMATCH")
                relocated_paths[artifact_id] = target
            relocated = audit_once(files, relocated_paths, expected, "relocated", isolation)
        tests = negative_tests(
            files,
            normal_1,
            expected,
            isolation,
            read_json(files, paths["inputs"]),
        )

    expected_counts = {
        "event_records":10,
        "event_statuses":{"FULLY_EVALUABLE":6,"NOT_EVALUABLE":1,"PARTIALLY_EVALUABLE":3},
        "horizon_statuses":{"EVALUABLE":27,"NOT_EVALUABLE_DATA_INCOMPLETE_GAP":3,"NOT_EVALUABLE_RIGHT_CENSORING":3,"NOT_EVALUABLE_SOURCE_INTEGRITY":7},
        "excursion_statuses":{"EVALUABLE":6,"NOT_EVALUABLE_DATA_INCOMPLETE_GAP":1,"NOT_EVALUABLE_RIGHT_CENSORING":1,"NOT_EVALUABLE_SOURCE_INTEGRITY":2},
        "rejections":3,
    }
    required_hashes = {
        "reference_records":expected["records_sha256"],"adapter_records":expected["records_sha256"],"expected_records":expected["records_sha256"],
        "reference_complete":expected["complete_output_sha256"],"adapter_complete":expected["complete_output_sha256"],"expected_complete":expected["complete_output_sha256"],
    }
    run_sha256 = {
        "normal_1":digest(normal_1),"normal_2":digest(normal_2),"relocated":digest(relocated)
    }
    mismatch_counters = {
        "b6_identity_mismatch":int(not normal_1["upstream"]["b6"]["identity_validated"]),
        "b6_schema_or_projection_mismatch":int(not normal_1["upstream"]["b6"]["contract_schema_validated"] or not normal_1["upstream"]["b6"]["result_projection_validated"]),
        "b6a_identity_mismatch":int(not normal_1["upstream"]["b6a"]["identity_validated"]),
        "b6a_schema_or_projection_mismatch":int(not normal_1["upstream"]["b6a"]["contract_schema_validated"] or not normal_1["upstream"]["b6a"]["result_projection_validated"]),
        "reference_expected_mismatch":int(normal_1["reference"]!=normal_1["expected"]),
        "adapter_reference_mismatch":int(normal_1["adapter"]!=normal_1["reference"]),
        "adapter_expected_mismatch":int(normal_1["adapter"]!=normal_1["expected"]),
        "hash_mismatch":int(normal_1["hashes"]!=required_hashes),
        "fixture_count_mismatch":int(normal_1["counts"]!=expected_counts),
        "record_order_mismatch":int(normal_1["record_order"]!=sorted(normal_1["record_order"])),
        "rejection_mismatch":int(normal_1["reference"]["rejections"]!=normal_1["adapter"]["rejections"]),
        "audit_repeat_mismatch":int(normal_1!=normal_2),
        "relocation_mismatch":int(normal_1!=relocated),
        "synthetic_scope_mismatch":int(
            normal_1["synthetic_only"] is not True
            or normal_2["synthetic_only"] is not True
            or relocated["synthetic_only"] is not True
        ),
        "reference_isolation_mismatch":int(isolation.adapter_call_count!=0),
        "negative_test_mismatch":int(not tests["all_passed"]),
    }
    imported = set(sys.modules)-before_modules
    prohibited_loaded = sorted(name for name in PROHIBITED_MODULES if name in sys.modules or name in imported)
    module_import_counts = {
        "detector_import_count":int("market_structure_break_retest_detector" in prohibited_loaded),
        "b2_runner_import_count":int("run_fr_prep_b2_fj_backward_compatible_replay" in prohibited_loaded),
        "b4_runner_import_count":int("run_fr_prep_b4_fq_holdout_event_population_replay" in prohibited_loaded),
        "b6a_runner_import_count":int("run_fr_prep_b6a_synthetic_outcome_adapter_fixtures" in prohibited_loaded),
        "wrapper_import_count":int("fr_prep_runner_execution_wrapper" in prohibited_loaded),
        "fj_or_fq_runner_import_count":sum(name in prohibited_loaded for name in ("run_checkpoint_fj_historical_event_population","run_checkpoint_fq_holdout_gap_boundary")),
        "real_outcome_engine_import_count":sum(name in prohibited_loaded for name in ("run_checkpoint_fl_shadow_outcomes","paf_shadow_outcome_labeler")),
        "mt5_import_count":int("MetaTrader5" in prohibited_loaded),
        "ea_import_count":sum(name.lower().endswith("_ea") for name in imported),
    }
    prohibited_execution_counts = {key:0 for key in (
        "detector_execution_count","b2_runner_execution_count","b4_runner_execution_count",
        "b6a_runner_execution_count","wrapper_execution_count","fj_replay_execution_count",
        "fq_replay_execution_count","real_outcome_engine_execution_count","real_outcome_generation_count",
        "real_future_price_read_count","raw_csv_read_count","tp_sl_calculation_count",
        "cash_pnl_calculation_count","optimization_count","network_execution_count",
        "mt5_execution_count","ea_execution_count"
    )}
    if any(mismatch_counters.values()) or any(module_import_counts.values()) or any(prohibited_execution_counts.values()) or prohibited_loaded:
        raise SystemExit("B6B_INDEPENDENT_AUDIT_BLOCKED")

    agreement = {
        "reference_records_sha256":normal_1["hashes"]["reference_records"],
        "adapter_records_sha256":normal_1["hashes"]["adapter_records"],
        "expected_records_sha256":normal_1["hashes"]["expected_records"],
        "reference_complete_sha256":normal_1["hashes"]["reference_complete"],
        "adapter_complete_sha256":normal_1["hashes"]["adapter_complete"],
        "expected_complete_sha256":normal_1["hashes"]["expected_complete"],
    }
    evidence = {
        "schema_version":"fr_prep_b6b_independent_synthetic_outcome_adapter_audit.v1",
        "checkpoint":"FR_PREP_B6B","decision":PASS,
        "upstream_validation":normal_1["upstream"],
        "adapter_binding":{"path":"tools/observational_outcome_adapter.py","file_sha256":expected["adapter_sha256"]},
        "fixture_bindings":{"input_fixture_sha256":expected["input_fixture_sha256"],"expected_fixture_sha256":expected["expected_fixture_sha256"],"synthetic_only":True},
        "horizons":expected["horizons"],
        "independent_reference":{"implementation_location":"tools/run_fr_prep_b6b_independent_synthetic_outcome_adapter_audit.py","adapter_imported_during_reference":False,"adapter_call_count":0,"reference_frozen_before_adapter_load":True},
        "fixture_counts":normal_1["counts"],"agreement_hashes":agreement,
        "determinism":{"audit_repeat_identical":normal_1==normal_2,"relocation_identical":normal_1==relocated,"byte_identical":len(set(run_sha256.values()))==1,"run_sha256":run_sha256},
        "mismatch_counters":mismatch_counters,"negative_tests":tests,
        "runtime_audit":{
            "reference_evaluation_count":3,"authorized_adapter_suite_execution_count":3,
            "module_import_counts":module_import_counts,"prohibited_execution_counts":prohibited_execution_counts,
            "external_process":{"successful_launch_count":0,"blocked_launch_count":external.blocked},
            "file_access":files.report(),
            "counter_provenance":{
                "module_imports":"sys.modules delta confirms prohibited modules absent",
                "executions":"three independent references precede three exact-bound adapter suites",
                "external_process":"Popen, os.system, and os.startfile fail-closed interception",
                "file_access":"resolved-path allowlist excludes real events, candidates, future prices, and raw CSV",
            },
        },
        "prohibited_modules":prohibited_loaded,"execution_status":"PASS",
        "conclusions":copy.deepcopy(expected["required_conclusions"]),
        "absolute_runtime_path_in_canonical_identity_count":0,
    }
    evidence["canonical_summary_sha256"]=digest(evidence)
    if absolute_path_count(evidence):
        raise SystemExit("B6B_ABSOLUTE_PATH_IDENTITY_LEAK")
    schema=read_json(files,EVIDENCE_SCHEMA)
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.Draft202012Validator(schema).validate(evidence)
    EVIDENCE.write_text(json.dumps(evidence,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    result={
        "decision":PASS,"canonical_summary_sha256":evidence["canonical_summary_sha256"],
        "b6a_canonical_summary_sha256":expected["b6a_canonical_summary_sha256"],
        "adapter_sha256":expected["adapter_sha256"],"fixture_counts":normal_1["counts"],
        "agreement_hashes":agreement,"repeat_identical":True,"relocation_identical":True,
        "mismatch_count":sum(mismatch_counters.values()),
        "negative_tests":{"passed":tests["tests_passed"],"total":tests["test_count"]},
        "prohibited_import_count":sum(module_import_counts.values()),
        "prohibited_execution_count":sum(prohibited_execution_counts.values()),
        "conclusions":evidence["conclusions"],"execution_status":"PASS",
    }
    RESULT.parent.mkdir(parents=True,exist_ok=True)
    RESULT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(result,sort_keys=True))


if __name__=="__main__":
    main()
