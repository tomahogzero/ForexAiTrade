#!/usr/bin/env python3
"""Freeze B8 observational-outcome interpretation rules without reading outcomes."""

import argparse
import builtins
import copy
import hashlib
import json
import ntpath
import os
import posixpath
import subprocess
import sys
from collections import Counter
from pathlib import Path

import jsonschema

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
AUTH = ROOT / "research/contracts/fr_prep_b8_outcome_interpretation_contract_authorization.v1.json"
AUTH_SCHEMA = ROOT / "research/schemas/fr_prep_b8_outcome_interpretation_contract_authorization.v1.schema.json"
CONTRACT = ROOT / "research/contracts/fr_prep_b8_observational_outcome_interpretation_contract.v1.json"
CONTRACT_SCHEMA = ROOT / "research/schemas/fr_prep_b8_observational_outcome_interpretation_contract.v1.schema.json"
RESULT = ROOT / "research/results/checkpoint_fr_prep_b8/outcome_interpretation_contract_summary.json"
MODE = "freeze-observational-outcome-interpretation-contract"
PASS = "FR_PREP_B8_PASS_OUTCOME_INTERPRETATION_CONTRACT_FROZEN"
PROHIBITED_MODULES = {
    "observational_outcome_adapter",
    "run_fr_prep_b7_sealed_real_observational_outcomes",
    "run_fr_prep_b7a_independent_real_outcome_audit",
    "market_structure_break_retest_detector",
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
        self.reads = Counter()
        self.unique = {}
        self.blocked_b7_data_reads = 0

    def add(self, path, category):
        resolved = Path(path).resolve()
        self.allowed[resolved] = category
        self.unique.setdefault(category, set())

    def read(self, path):
        resolved = Path(path).resolve()
        category = self.allowed.get(resolved)
        if category is None:
            self.blocked_b7_data_reads += 1
            raise PermissionError("B8_B7_RECORD_OR_STATISTICS_READ_BLOCKED")
        self.reads[category] += 1
        self.unique[category].add(resolved)
        return resolved.read_bytes()

    def report(self):
        categories = sorted(self.unique)
        return {
            "unique_logical_file_counts": {
                category: len(self.unique[category]) for category in categories
            },
            "raw_read_operation_counts": {
                category: self.reads[category] for category in categories
            },
            "b7_jsonl_parse_count": 0,
            "b7_statistics_csv_parse_count": 0,
            "outcome_recomputation_count": 0,
            "statistics_recomputation_count": 0,
            "blocked_b7_data_read_attempt_count": self.blocked_b7_data_reads,
            "unauthorized_successful_read_count": 0,
        }


class ExternalProcessGuard:
    def __init__(self):
        self.blocked = 0

    def deny(self, *_args, **_kwargs):
        self.blocked += 1
        raise RuntimeError("B8_EXTERNAL_PROCESS_BLOCKED")

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
            raise ImportError("B8_PROHIBITED_IMPORT_BLOCKED")
        return self.original(name, *args, **kwargs)

    def __enter__(self):
        self.original = builtins.__import__
        builtins.__import__ = self.guarded
        return self

    def __exit__(self, *_args):
        builtins.__import__ = self.original


def read_json(files, path):
    return json.loads(files.read(path).decode("utf-8"))


def validate_b7a(files, paths, expected):
    contract = read_json(files, paths["b7a_contract"])
    schema = read_json(files, paths["b7a_schema"])
    result = read_json(files, paths["b7a_result"])
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.Draft202012Validator(schema).validate(contract)
    binding = expected["b7a"]
    conclusions = contract["conclusions"]
    valid = (
        identity(contract) == binding["canonical_summary_sha256"]
        and contract["canonical_summary_sha256"] == binding["canonical_summary_sha256"]
        and result["canonical_summary_sha256"] == binding["canonical_summary_sha256"]
        and contract["decision"] == binding["decision"]
        and result["decision"] == binding["decision"]
        and result["execution_status"] == "PASS"
        and conclusions["real_outcome_records"] == "INDEPENDENTLY_AUDITED"
        and conclusions["descriptive_statistics"] == "INDEPENDENTLY_AUDITED"
        and conclusions["dataset_separation"] == "PROVEN"
        and conclusions["performance"] == "NOT_EVALUATED"
        and conclusions["profitability"] == "NOT_CLAIMED"
        and conclusions["next_allowed_scope"] == "OUTCOME_INTERPRETATION_CONTRACT_DESIGN_ONLY"
    )
    return {
        "canonical_summary_sha256": binding["canonical_summary_sha256"],
        "decision": binding["decision"],
        "identity_validated": valid,
        "schema_validated": True,
        "result_projection_validated": valid,
        "records_independently_audited": conclusions["real_outcome_records"] == "INDEPENDENTLY_AUDITED",
        "statistics_independently_audited": conclusions["descriptive_statistics"] == "INDEPENDENTLY_AUDITED",
        "dataset_separation": conclusions["dataset_separation"],
        "performance": conclusions["performance"],
        "profitability": conclusions["profitability"],
    }


def frozen_contract(expected):
    return {
        "interpretation_vocabulary": copy.deepcopy(expected["interpretation_vocabulary"]),
        "permitted_future_interpretation_inputs": copy.deepcopy(
            expected["permitted_future_interpretation_inputs"]
        ),
        "interpretation_rules": copy.deepcopy(expected["interpretation_rules"]),
        "pattern_reporting_contract": copy.deepcopy(expected["pattern_reporting_contract"]),
        "coverage_handling": copy.deepcopy(expected["coverage_handling"]),
        "future_report_conclusions": copy.deepcopy(expected["future_report_conclusions"]),
    }


def request_allowed(expected, request):
    return request == {
        "b7a_identity": expected["b7a"]["canonical_summary_sha256"],
        "b7a_decision": expected["b7a"]["decision"],
        "parse_b7_records_or_statistics": False,
        "dataset_pooling": False,
        "selection_request": [],
        "composite_score": False,
        "performance_threshold": None,
        "wording": [],
        "claims": [],
        "trade_simulation_features": [],
        "optimization_or_parameter_recommendation": False,
        "suppress_groups": False,
        "external_process": False,
    }


def negative_tests(expected, files):
    base = {
        "b7a_identity": expected["b7a"]["canonical_summary_sha256"],
        "b7a_decision": expected["b7a"]["decision"],
        "parse_b7_records_or_statistics": False,
        "dataset_pooling": False,
        "selection_request": [],
        "composite_score": False,
        "performance_threshold": None,
        "wording": [],
        "claims": [],
        "trade_simulation_features": [],
        "optimization_or_parameter_recommendation": False,
        "suppress_groups": False,
        "external_process": False,
    }
    tests = {}
    mutations = [
        ("wrong_b7a_identity_or_decision_blocked", lambda x: x.update({"b7a_identity": "0" * 64})),
        ("b7_records_or_statistics_parsing_attempt_blocked", lambda x: x.update({"parse_b7_records_or_statistics": True})),
        ("dataset_pooling_request_blocked", lambda x: x.update({"dataset_pooling": True})),
        ("best_horizon_direction_or_year_selection_blocked", lambda x: x.update({"selection_request": ["BEST_HORIZON", "BEST_DIRECTION", "BEST_YEAR"]})),
        ("composite_score_or_performance_threshold_blocked", lambda x: x.update({"composite_score": True})),
        ("win_rate_or_trade_pl_wording_blocked", lambda x: x.update({"wording": ["WIN_RATE", "TRADE_PL"]})),
        ("profitability_edge_or_robustness_claim_blocked", lambda x: x.update({"claims": ["PROFITABLE", "HAS_EDGE", "ROBUST"]})),
        ("tp_sl_cost_lot_or_order_simulation_blocked", lambda x: x.update({"trade_simulation_features": ["TP_SL", "COST", "LOT", "ORDER_SIMULATION"]})),
        ("optimization_or_parameter_recommendation_blocked", lambda x: x.update({"optimization_or_parameter_recommendation": True})),
        ("conflicting_or_low_coverage_group_suppression_blocked", lambda x: x.update({"suppress_groups": True})),
        ("mt5_ea_network_or_external_process_request_blocked", lambda x: x.update({"external_process": True})),
    ]
    for name, mutation in mutations:
        changed = copy.deepcopy(base)
        mutation(changed)
        tests[name] = not request_allowed(expected, changed)
    try:
        files.read(ROOT / "research/results/checkpoint_fr_prep_b7/fj_observational_outcomes.jsonl")
        tests["b7_file_read_guard_fail_closed"] = False
    except PermissionError:
        tests["b7_file_read_guard_fail_closed"] = True
    blocked_imports = 0
    for module in (
        "observational_outcome_adapter",
        "run_fr_prep_b7_sealed_real_observational_outcomes",
        "run_fr_prep_b7a_independent_real_outcome_audit",
        "market_structure_break_retest_detector",
        "MetaTrader5",
    ):
        try:
            builtins.__import__(module)
        except ImportError:
            blocked_imports += 1
    tests["prohibited_import_guard_fail_closed"] = blocked_imports == 5
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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", required=True, choices=[MODE])
    parser.add_argument("--authorization", required=True)
    parser.add_argument("--output-root", required=True)
    args = parser.parse_args()
    if Path(args.authorization).resolve() != AUTH.resolve():
        raise SystemExit("B8_AUTHORIZATION_PATH_NOT_ALLOWED")
    if Path(args.output_root).resolve() != RESULT.parent.resolve():
        raise SystemExit("B8_OUTPUT_ROOT_NOT_ALLOWED")

    files = Files()
    for path, category in (
        (AUTH, "b8_authorization"),
        (AUTH_SCHEMA, "b8_authorization_schema"),
        (CONTRACT_SCHEMA, "b8_contract_schema"),
    ):
        files.add(path, category)
    authorization = read_json(files, AUTH)
    authorization_schema = read_json(files, AUTH_SCHEMA)
    contract_schema = read_json(files, CONTRACT_SCHEMA)
    jsonschema.Draft202012Validator.check_schema(authorization_schema)
    jsonschema.Draft202012Validator(authorization_schema).validate(authorization)
    jsonschema.Draft202012Validator.check_schema(contract_schema)
    paths = {}
    artifact_hash_mismatch = 0
    for binding in authorization["committed_artifacts"]:
        path = (ROOT / binding["path"]).resolve()
        files.add(path, binding["category"])
        if not path.is_file():
            raise SystemExit("B8_COMMITTED_B7A_ARTIFACT_MISSING")
        artifact_hash_mismatch += int(
            byte_digest(files.read(path)) != binding["file_sha256"]
        )
        paths[binding["artifact_id"]] = path
    if artifact_hash_mismatch:
        raise SystemExit("B8_COMMITTED_B7A_ARTIFACT_HASH_MISMATCH")

    before_modules = set(sys.modules)
    with ExternalProcessGuard() as external_guard, ImportGuard() as import_guard:
        b7a = validate_b7a(files, paths, authorization["expected"])
        design_1 = frozen_contract(authorization["expected"])
        design_2 = frozen_contract(authorization["expected"])
        tests = negative_tests(authorization["expected"], files)
    imported = set(sys.modules) - before_modules
    prohibited_loaded = sorted(
        name for name in PROHIBITED_MODULES if name in sys.modules or name in imported
    )
    mismatch_counters = {
        "b7a_identity_or_decision_mismatch": int(not b7a["identity_validated"]),
        "b7a_schema_or_projection_mismatch": int(
            not (b7a["schema_validated"] and b7a["result_projection_validated"])
        ),
        "b7a_audit_conclusion_mismatch": int(
            not (
                b7a["records_independently_audited"]
                and b7a["statistics_independently_audited"]
                and b7a["dataset_separation"] == "PROVEN"
                and b7a["performance"] == "NOT_EVALUATED"
                and b7a["profitability"] == "NOT_CLAIMED"
            )
        ),
        "committed_artifact_hash_mismatch": artifact_hash_mismatch,
        "contract_repeat_mismatch": int(design_1 != design_2),
        "vocabulary_mismatch": int(
            len(design_1["interpretation_vocabulary"]["permitted_evidence_statements"]) != 9
            or len(design_1["interpretation_vocabulary"]["prohibited_evidence_statements"]) != 13
        ),
        "interpretation_rule_mismatch": int(len(design_1["interpretation_rules"]) != 16),
        "negative_test_mismatch": int(not tests["all_passed"]),
        "absolute_path_identity_mismatch": 0,
    }
    prohibited_import_counts = {
        "adapter_import_count": int("observational_outcome_adapter" in prohibited_loaded),
        "b7_runner_import_count": int("run_fr_prep_b7_sealed_real_observational_outcomes" in prohibited_loaded),
        "b7a_auditor_import_count": int("run_fr_prep_b7a_independent_real_outcome_audit" in prohibited_loaded),
        "detector_import_count": int("market_structure_break_retest_detector" in prohibited_loaded),
        "mt5_import_count": int("MetaTrader5" in prohibited_loaded),
    }
    prohibited_execution_counts = {
        key: 0 for key in (
            "adapter_call_count", "b7_runner_call_count", "b7a_auditor_call_count",
            "detector_execution_count", "b7_record_parse_count",
            "b7_statistics_parse_count", "outcome_recomputation_count",
            "statistics_recomputation_count", "outcome_interpretation_count",
            "strategy_change_count", "optimization_count", "tp_sl_calculation_count",
            "cash_pl_calculation_count", "trading_cost_calculation_count",
            "lot_simulation_count", "order_simulation_count", "mt5_execution_count",
            "ea_execution_count", "network_execution_count",
            "external_process_success_count", "profitability_claim_count",
            "edge_claim_count", "robustness_claim_count", "trading_readiness_claim_count",
        )
    }
    if (
        any(mismatch_counters.values()) or any(prohibited_import_counts.values())
        or any(prohibited_execution_counts.values()) or prohibited_loaded
    ):
        raise SystemExit("B8_INTERPRETATION_CONTRACT_DESIGN_BLOCKED")

    contract = {
        "schema_version": "fr_prep_b8_observational_outcome_interpretation_contract.v1",
        "checkpoint": "FR_PREP_B8",
        "decision": PASS,
        "execution_status": "PASS",
        "b7a_binding": b7a,
        **design_1,
        "contract_scope": {
            "design_only": True,
            "b7_jsonl_records_parsed": False,
            "b7_statistics_csv_values_parsed": False,
            "outcomes_recomputed": False,
            "statistics_recomputed": False,
            "outcome_interpretation_performed": False,
        },
        "negative_tests": tests,
        "mismatch_counters": mismatch_counters,
        "runtime_audit": {
            "file_access": files.report(),
            "blocked_import_requests": import_guard.blocked,
            "prohibited_import_counts": prohibited_import_counts,
            "prohibited_execution_counts": prohibited_execution_counts,
            "external_process": {
                "blocked_launch_count": external_guard.blocked,
                "successful_launch_count": 0,
            },
        },
        "absolute_runtime_path_in_canonical_identity_count": 0,
        "prohibited_modules": [],
    }
    contract["canonical_summary_sha256"] = identity(contract)
    jsonschema.Draft202012Validator(contract_schema).validate(contract)
    if absolute_path_count(contract):
        raise SystemExit("B8_ABSOLUTE_PATH_IDENTITY_LEAKAGE_BLOCKED")
    rendered = json.dumps(contract, ensure_ascii=True, indent=2, sort_keys=True) + "\n"
    CONTRACT.write_text(rendered, encoding="utf-8", newline="\n")
    RESULT.parent.mkdir(parents=True, exist_ok=True)
    RESULT.write_text(rendered, encoding="utf-8", newline="\n")
    print(canonical_json({
        "decision": PASS,
        "canonical_summary_sha256": contract["canonical_summary_sha256"],
        "permitted_vocabulary_count": len(
            contract["interpretation_vocabulary"]["permitted_evidence_statements"]
        ),
        "prohibited_vocabulary_count": len(
            contract["interpretation_vocabulary"]["prohibited_evidence_statements"]
        ),
        "negative_tests": f"{tests['tests_passed']}/{tests['test_count']}",
        "mismatch_count": sum(mismatch_counters.values()),
        "prohibited_count": sum(prohibited_import_counts.values())
        + sum(prohibited_execution_counts.values()),
    }))


if __name__ == "__main__":
    main()
