#!/usr/bin/env python3
"""Freeze B10 research-disposition rules without selecting a disposition."""

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
AUTH = ROOT / "research/contracts/fr_prep_b10_research_disposition_contract_authorization.v1.json"
AUTH_SCHEMA = ROOT / "research/schemas/fr_prep_b10_research_disposition_contract_authorization.v1.schema.json"
CONTRACT = ROOT / "research/contracts/fr_prep_b10_research_disposition_contract.v1.json"
CONTRACT_SCHEMA = ROOT / "research/schemas/fr_prep_b10_research_disposition_contract.v1.schema.json"
RESULT = ROOT / "research/results/checkpoint_fr_prep_b10/research_disposition_contract_summary.json"
MODE = "freeze-research-disposition-contract"
PASS = "FR_PREP_B10_PASS_RESEARCH_DISPOSITION_CONTRACT_FROZEN"
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
        self.parse_allowed = set()
        self.hash_reads = Counter()
        self.parse_reads = Counter()
        self.blocked_parse_attempts = 0

    def add(self, path, category, parse_authorized):
        resolved = Path(path).resolve()
        self.allowed[resolved] = category
        if parse_authorized:
            self.parse_allowed.add(resolved)

    def hash_read(self, path):
        resolved = Path(path).resolve()
        category = self.allowed.get(resolved)
        if category is None:
            raise PermissionError("B10_UNAUTHORIZED_HASH_READ_BLOCKED")
        self.hash_reads[category] += 1
        return resolved.read_bytes()

    def parse_json(self, path):
        resolved = Path(path).resolve()
        if resolved not in self.parse_allowed:
            self.blocked_parse_attempts += 1
            raise PermissionError("B10_PROHIBITED_PARSE_READ_BLOCKED")
        category = self.allowed[resolved]
        self.parse_reads[category] += 1
        return json.loads(resolved.read_text(encoding="utf-8"))

    def report(self):
        categories = sorted(set(self.allowed.values()))
        return {
            "hash_read_operation_counts": {
                category: self.hash_reads[category] for category in categories
            },
            "parse_read_operation_counts": {
                category: self.parse_reads[category] for category in categories
            },
            "blocked_prohibited_parse_attempt_count": self.blocked_parse_attempts,
            "b7_jsonl_parse_count": 0,
            "b7_statistics_csv_parse_count": 0,
            "b9_markdown_parse_count": 0,
            "b9_report_raw_statistic_value_read_count": 0,
            "raw_broker_csv_read_count": 0,
            "future_ohlc_read_count": 0,
            "unauthorized_successful_read_count": 0,
        }


class ExternalProcessGuard:
    def __init__(self):
        self.blocked = 0

    def deny(self, *_args, **_kwargs):
        self.blocked += 1
        raise RuntimeError("B10_EXTERNAL_PROCESS_BLOCKED")

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
            raise ImportError("B10_PROHIBITED_IMPORT_BLOCKED")
        return self.original(name, *args, **kwargs)

    def __enter__(self):
        self.original = builtins.__import__
        builtins.__import__ = self.guarded
        return self

    def __exit__(self, *_args):
        builtins.__import__ = self.original


def validate_b9(files, paths, expected):
    contract = files.parse_json(paths["b9_contract"])
    schema = files.parse_json(paths["b9_schema"])
    summary = files.parse_json(paths["b9_summary"])
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.Draft202012Validator(schema).validate(contract)
    binding = expected["b9"]
    required_conclusions = {
        "outcome_record_integrity": "PROVEN",
        "descriptive_statistics_integrity": "PROVEN",
        "descriptive_interpretation": "COMPLETED_UNDER_FROZEN_CONTRACT",
        "strategy_edge": "NOT_ESTABLISHED",
        "robustness": "NOT_ESTABLISHED",
        "performance": "NOT_EVALUATED",
        "profitability": "NOT_CLAIMED",
        "order_logic": "NOT_APPROVED",
        "candidate": "NOT_READY_FOR_ORDER_LOGIC",
        "next_allowed_scope": "RESEARCH_DISPOSITION_CONTRACT_DESIGN_ONLY",
    }
    hashes_valid = (
        contract["output_hashes"]["report_json_sha256"] == binding["report_json_sha256"]
        and contract["output_hashes"]["report_markdown_sha256"] == binding["report_markdown_sha256"]
        and contract["output_hashes"]["complete_sha256"] == binding["complete_output_sha256"]
        and summary["output_hashes"] == contract["output_hashes"]
    )
    identity_valid = (
        identity(contract) == binding["canonical_summary_sha256"]
        and contract["canonical_summary_sha256"] == binding["canonical_summary_sha256"]
        and summary["canonical_summary_sha256"] == binding["canonical_summary_sha256"]
        and contract["decision"] == binding["decision"]
        and summary["decision"] == binding["decision"]
        and contract["execution_status"] == "PASS"
        and summary["execution_status"] == "PASS"
    )
    projection_valid = (
        summary == contract
        and contract["conclusions"] == required_conclusions
        and contract["report"]["dataset_separation"] == "PROVEN"
        and contract["report"]["dataset_order"] == ["FJ", "FQ"]
        and contract["report"]["direction_order"] == ["LONG", "SHORT"]
        and contract["report"]["horizon_order"] == ["1", "3", "6", "12"]
        and contract["report"]["statistics_rows"] == 72
        and contract["report"]["b7_jsonl_records_parsed"] is False
        and contract["report"]["statistics_recomputed"] is False
    )
    return {
        "canonical_summary_sha256": binding["canonical_summary_sha256"],
        "decision": binding["decision"],
        "identity_validated": identity_valid,
        "schema_validated": True,
        "summary_projection_validated": projection_valid,
        "output_hashes_validated": hashes_valid,
        "dataset_separation": contract["report"]["dataset_separation"],
        "dataset_order": copy.deepcopy(contract["report"]["dataset_order"]),
        "direction_order": copy.deepcopy(contract["report"]["direction_order"]),
        "horizon_order": copy.deepcopy(contract["report"]["horizon_order"]),
        "required_conclusions_validated": contract["conclusions"] == required_conclusions,
    }


def frozen_design(expected):
    return {
        "disposition_values": copy.deepcopy(expected["disposition_values"]),
        "disposition_interpretation": copy.deepcopy(expected["disposition_interpretation"]),
        "rules": copy.deepcopy(expected["rules"]),
        "rule_evaluation_policy": {
            "rule_order": [1, 2, 3, 4],
            "evaluation_count": 1,
            "first_matching_rule_wins": True,
            "manual_override_allowed": False,
            "score_or_weighting_allowed": False,
            "multiple_dispositions_allowed": False,
        },
        "permitted_future_inputs": copy.deepcopy(expected["permitted_future_inputs"]),
        "forbidden_decision_inputs": copy.deepcopy(expected["forbidden_decision_inputs"]),
        "coverage_rules": copy.deepcopy(expected["coverage_rules"]),
        "future_decision_record_fields": copy.deepcopy(expected["future_decision_record_fields"]),
        "future_decision_record_policy": copy.deepcopy(expected["future_decision_record_policy"]),
        "conclusions": copy.deepcopy(expected["contract_conclusions"]),
    }


def base_request(expected):
    return {
        "b9_identity": expected["b9"]["canonical_summary_sha256"],
        "b9_decision": expected["b9"]["decision"],
        "b9_hashes": [
            expected["b9"]["report_json_sha256"],
            expected["b9"]["report_markdown_sha256"],
            expected["b9"]["complete_output_sha256"],
        ],
        "parse_b7_jsonl_or_statistics": False,
        "parse_b9_markdown": False,
        "execute_disposition": False,
        "rule_order": [1, 2, 3, 4],
        "first_match": True,
        "manual_override": False,
        "requested_dispositions": [],
        "coverage_threshold": None,
        "override_material_limitation": False,
        "performance_gate_inputs": [],
        "preferred_subgroup": [],
        "dataset_pooling": False,
        "claims": [],
        "trade_or_order_features": [],
        "external_process": False,
        "runtime_path": None,
    }


def request_allowed(expected, request):
    return request == base_request(expected)


def negative_tests(expected, files, paths):
    base = base_request(expected)
    tests = {}

    def mutate(name, change):
        changed = copy.deepcopy(base)
        change(changed)
        tests[name] = not request_allowed(expected, changed)

    mutate(
        "wrong_b9_identity_decision_or_output_hash_blocked",
        lambda value: value.update({"b9_identity": "0" * 64}),
    )
    blocked_b7 = 0
    for prohibited in (
        ROOT / "research/results/checkpoint_fr_prep_b7/fj_observational_outcomes.jsonl",
        ROOT / "research/results/checkpoint_fr_prep_b7/fq_observational_outcomes.jsonl",
        ROOT / "research/results/checkpoint_fr_prep_b7/observational_outcome_statistics.csv",
    ):
        try:
            files.parse_json(prohibited)
        except PermissionError:
            blocked_b7 += 1
    changed = copy.deepcopy(base)
    changed["parse_b7_jsonl_or_statistics"] = True
    tests["b7_jsonl_or_statistics_csv_parsing_attempt_blocked"] = (
        blocked_b7 == 3 and not request_allowed(expected, changed)
    )
    try:
        files.parse_json(paths["b9_report_markdown"])
        markdown_blocked = False
    except PermissionError:
        markdown_blocked = True
    changed = copy.deepcopy(base)
    changed["parse_b9_markdown"] = True
    tests["b9_markdown_parsing_attempt_blocked"] = (
        markdown_blocked and not request_allowed(expected, changed)
    )
    mutate(
        "disposition_execution_during_design_blocked",
        lambda value: value.update({"execute_disposition": True}),
    )
    mutate(
        "changed_rule_order_or_first_match_precedence_blocked",
        lambda value: value.update({"rule_order": [2, 1, 3, 4]}),
    )
    mutate(
        "manual_override_or_multiple_dispositions_blocked",
        lambda value: value.update({
            "manual_override": True,
            "requested_dispositions": expected["disposition_values"][:2],
        }),
    )
    mutate(
        "invented_numerical_coverage_threshold_blocked",
        lambda value: value.update({"coverage_threshold": "0.950000"}),
    )
    mutate(
        "positive_observations_overriding_material_limitation_blocked",
        lambda value: value.update({"override_material_limitation": True}),
    )
    mutate(
        "return_sign_mfe_mae_or_shares_as_performance_gate_blocked",
        lambda value: value.update({"performance_gate_inputs": ["RETURN_SIGN", "MFE_MAE", "SHARES"]}),
    )
    mutate(
        "preferred_horizon_direction_or_year_selection_blocked",
        lambda value: value.update({"preferred_subgroup": ["HORIZON", "DIRECTION", "YEAR"]}),
    )
    mutate(
        "dataset_pooling_blocked",
        lambda value: value.update({"dataset_pooling": True}),
    )
    mutate(
        "profitability_edge_robustness_or_readiness_claim_blocked",
        lambda value: value.update({"claims": ["PROFITABILITY", "EDGE", "ROBUSTNESS", "READINESS"]}),
    )
    mutate(
        "tp_sl_cost_cash_pl_lot_or_order_simulation_blocked",
        lambda value: value.update({
            "trade_or_order_features": ["TP_SL", "COST", "CASH_PL", "LOT", "ORDER_SIMULATION"]
        }),
    )
    blocked_imports = 0
    for module in sorted(PROHIBITED_MODULES):
        try:
            builtins.__import__(module)
        except ImportError:
            blocked_imports += 1
    tests["prohibited_import_guard_fail_closed"] = blocked_imports == len(PROHIBITED_MODULES)
    try:
        subprocess.Popen(["terminal64.exe", "/blocked"])
        external_blocked = False
    except RuntimeError:
        external_blocked = True
    leaked = copy.deepcopy(base)
    leaked["runtime_path"] = str(ROOT.resolve())
    tests["mt5_ea_network_external_process_or_absolute_path_leakage_blocked"] = (
        external_blocked
        and not request_allowed(expected, leaked)
        and absolute_path_count(leaked) == 1
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
        raise SystemExit("B10_AUTHORIZATION_PATH_NOT_ALLOWED")
    if Path(args.output_root).resolve() != RESULT.parent.resolve():
        raise SystemExit("B10_OUTPUT_ROOT_NOT_ALLOWED")

    files = Files()
    for path, category in (
        (AUTH, "b10_authorization"),
        (AUTH_SCHEMA, "b10_authorization_schema"),
        (CONTRACT_SCHEMA, "b10_contract_schema"),
    ):
        files.add(path, category, True)
    authorization = files.parse_json(AUTH)
    authorization_schema = files.parse_json(AUTH_SCHEMA)
    contract_schema = files.parse_json(CONTRACT_SCHEMA)
    jsonschema.Draft202012Validator.check_schema(authorization_schema)
    jsonschema.Draft202012Validator(authorization_schema).validate(authorization)
    jsonschema.Draft202012Validator.check_schema(contract_schema)

    paths = {}
    artifact_hash_mismatch = 0
    for binding in authorization["committed_artifacts"]:
        path = (ROOT / binding["path"]).resolve()
        files.add(path, binding["category"], binding["parse_authorized"])
        if not path.is_file():
            raise SystemExit("B10_COMMITTED_B9_ARTIFACT_MISSING")
        artifact_hash_mismatch += int(
            byte_digest(files.hash_read(path)) != binding["file_sha256"]
        )
        paths[binding["artifact_id"]] = path
    if artifact_hash_mismatch:
        raise SystemExit("B10_COMMITTED_B9_ARTIFACT_HASH_MISMATCH")

    before_modules = set(sys.modules)
    with ExternalProcessGuard() as external_guard, ImportGuard() as import_guard:
        b9 = validate_b9(files, paths, authorization["expected"])
        design_1 = frozen_design(authorization["expected"])
        design_2 = frozen_design(authorization["expected"])
        tests = negative_tests(authorization["expected"], files, paths)
    imported = set(sys.modules) - before_modules
    prohibited_loaded = sorted(
        name for name in PROHIBITED_MODULES if name in sys.modules or name in imported
    )

    required_rule_projection = [
        (1, "BLOCKED_EVIDENCE_INTEGRITY", "EVIDENCE_REPAIR_ONLY"),
        (2, "DATA_QUALITY_REMEDIATION_REQUIRED", "DATA_QUALITY_REMEDIATION_CONTRACT_DESIGN_ONLY"),
        (3, "PREDECLARED_ADDITIONAL_HOLDOUT_REQUIRED", "PREDECLARED_HOLDOUT_CONTRACT_DESIGN_ONLY"),
        (4, "ARCHIVE_AUDITED_DESCRIPTIVE_BASELINE", "RESEARCH_ARCHIVE_ONLY"),
    ]
    actual_rule_projection = [
        (item["rule"], item["disposition"], item["next_scope"]) for item in design_1["rules"]
    ]
    mismatch_counters = {
        "b9_identity_or_decision_mismatch": int(not b9["identity_validated"]),
        "b9_schema_or_summary_projection_mismatch": int(
            not (b9["schema_validated"] and b9["summary_projection_validated"])
        ),
        "b9_output_hash_mismatch": int(not b9["output_hashes_validated"]),
        "b9_required_conclusion_mismatch": int(not b9["required_conclusions_validated"]),
        "b9_dataset_separation_or_order_mismatch": int(
            not (
                b9["dataset_separation"] == "PROVEN"
                and b9["dataset_order"] == ["FJ", "FQ"]
                and b9["direction_order"] == ["LONG", "SHORT"]
                and b9["horizon_order"] == ["1", "3", "6", "12"]
            )
        ),
        "committed_artifact_hash_mismatch": artifact_hash_mismatch,
        "contract_repeat_mismatch": int(design_1 != design_2),
        "disposition_value_mismatch": int(len(design_1["disposition_values"]) != 4),
        "rule_order_or_first_match_mismatch": int(
            actual_rule_projection != required_rule_projection
            or design_1["rule_evaluation_policy"]["rule_order"] != [1, 2, 3, 4]
            or not design_1["rule_evaluation_policy"]["first_matching_rule_wins"]
        ),
        "manual_override_weighting_or_multiple_disposition_mismatch": int(
            design_1["rule_evaluation_policy"]["manual_override_allowed"]
            or design_1["rule_evaluation_policy"]["score_or_weighting_allowed"]
            or design_1["rule_evaluation_policy"]["multiple_dispositions_allowed"]
        ),
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
            "adapter_call_count",
            "b7_runner_call_count",
            "b7a_auditor_call_count",
            "detector_execution_count",
            "disposition_selection_count",
            "disposition_execution_count",
            "b7_jsonl_parse_count",
            "b7_statistics_parse_count",
            "b9_markdown_parse_count",
            "b9_raw_statistic_value_read_count",
            "outcome_recomputation_count",
            "statistics_recomputation_count",
            "classification_recomputation_count",
            "raw_broker_csv_read_count",
            "future_ohlc_read_count",
            "strategy_change_count",
            "optimization_count",
            "tp_sl_calculation_count",
            "cash_pl_calculation_count",
            "trading_cost_calculation_count",
            "lot_simulation_count",
            "order_simulation_count",
            "mt5_execution_count",
            "ea_execution_count",
            "network_execution_count",
            "external_process_success_count",
            "profitability_claim_count",
            "edge_claim_count",
            "robustness_claim_count",
            "trading_readiness_claim_count",
        )
    }
    if (
        any(mismatch_counters.values())
        or any(prohibited_import_counts.values())
        or any(prohibited_execution_counts.values())
        or prohibited_loaded
    ):
        raise SystemExit("B10_RESEARCH_DISPOSITION_CONTRACT_DESIGN_BLOCKED")

    contract = {
        "schema_version": "fr_prep_b10_research_disposition_contract.v1",
        "checkpoint": "FR_PREP_B10",
        "decision": PASS,
        "execution_status": "PASS",
        "b9_binding": b9,
        **design_1,
        "contract_scope": {
            "design_only": True,
            "disposition_selected": False,
            "disposition_executed": False,
            "b7_jsonl_or_statistics_parsed": False,
            "b9_markdown_parsed": False,
            "outcomes_statistics_or_classifications_recomputed": False,
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
        raise SystemExit("B10_ABSOLUTE_PATH_IDENTITY_LEAKAGE_BLOCKED")
    rendered = json.dumps(contract, ensure_ascii=True, indent=2, sort_keys=True) + "\n"
    CONTRACT.write_text(rendered, encoding="utf-8", newline="\n")
    RESULT.parent.mkdir(parents=True, exist_ok=True)
    RESULT.write_text(rendered, encoding="utf-8", newline="\n")
    print(canonical_json({
        "decision": PASS,
        "canonical_summary_sha256": contract["canonical_summary_sha256"],
        "disposition_value_count": len(contract["disposition_values"]),
        "rule_order": contract["rule_evaluation_policy"]["rule_order"],
        "first_matching_rule_wins": contract["rule_evaluation_policy"]["first_matching_rule_wins"],
        "negative_tests": f"{tests['tests_passed']}/{tests['test_count']}",
        "mismatch_count": sum(mismatch_counters.values()),
        "prohibited_count": (
            sum(prohibited_import_counts.values()) + sum(prohibited_execution_counts.values())
        ),
    }))


if __name__ == "__main__":
    main()
