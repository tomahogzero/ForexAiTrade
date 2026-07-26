#!/usr/bin/env python3
"""Freeze the FR-Prep-B6 observational outcome contract without evaluating outcomes."""

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
AUTH = ROOT / "research/contracts/fr_prep_b6_outcome_contract_design_authorization.v1.json"
AUTH_SCHEMA = ROOT / "research/schemas/fr_prep_b6_outcome_contract_design_authorization.v1.schema.json"
CONTRACT = ROOT / "research/contracts/fr_prep_b6_observational_outcome_contract.v1.json"
CONTRACT_SCHEMA = ROOT / "research/schemas/fr_prep_b6_observational_outcome_contract.v1.schema.json"
RESULT = ROOT / "research/results/checkpoint_fr_prep_b6/outcome_contract_design_summary.json"
PASS = "FR_PREP_B6_PASS_OBSERVATIONAL_OUTCOME_CONTRACT_FROZEN"
MODE = "freeze-observational-outcome-contract"
PROHIBITED_MODULES = {
    "market_structure_break_retest_detector",
    "run_fr_prep_b2_fj_backward_compatible_replay",
    "run_fr_prep_b4_fq_holdout_event_population_replay",
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

    def add(self, path, category):
        resolved = Path(path).resolve()
        self.allowed[resolved] = category
        self.unique_reads.setdefault(category, set())

    def read(self, path):
        resolved = Path(path).resolve()
        category = self.allowed.get(resolved)
        if category is None:
            raise PermissionError("B6_UNAUTHORIZED_FILE_READ_BLOCKED")
        self.raw_reads[category] += 1
        self.unique_reads[category].add(resolved)
        return resolved.read_bytes()

    def report(self):
        categories = sorted(self.unique_reads)
        return {
            "unique_logical_file_counts": {
                category: len(self.unique_reads[category]) for category in categories
            },
            "raw_read_operation_counts": {
                category: self.raw_reads[category] for category in categories
            },
            "unauthorized_successful_read_count": 0,
        }


class ExternalProcessGuard:
    def __init__(self):
        self.blocked = 0

    def deny(self, *_args, **_kwargs):
        self.blocked += 1
        raise RuntimeError("B6_EXTERNAL_PROCESS_BLOCKED")

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


class ImportGuard:
    def __init__(self):
        self.blocked = 0

    def guarded_import(self, name, *args, **kwargs):
        if name.split(".", 1)[0] in PROHIBITED_MODULES:
            self.blocked += 1
            raise ImportError("B6_PROHIBITED_IMPORT_BLOCKED")
        return self.original_import(name, *args, **kwargs)

    def __enter__(self):
        self.original_import = builtins.__import__
        builtins.__import__ = self.guarded_import
        return self

    def __exit__(self, *_args):
        builtins.__import__ = self.original_import


def read_json(files, path):
    return json.loads(files.read(path).decode("utf-8"))


def validate_b5(files, paths, expected):
    contract = read_json(files, paths["b5_contract"])
    schema = read_json(files, paths["b5_schema"])
    result = read_json(files, paths["b5_result"])
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.Draft202012Validator(schema).validate(contract)
    binding = expected["b5"]
    identity_valid = (
        identity(contract) == binding["canonical_summary_sha256"]
        and contract["canonical_summary_sha256"] == binding["canonical_summary_sha256"]
    )
    projection_valid = (
        result["canonical_summary_sha256"] == binding["canonical_summary_sha256"]
        and result["decision"] == binding["decision"]
        and result["execution_status"] == "PASS"
        and result["mismatch_count"] == 0
        and result["fj"]["events"] == binding["fj_events"]
        and result["fq"]["events"] == binding["fq_events"]
        and result["conclusions"]["data_quality_comparability"] == binding["data_quality_comparability"]
        and result["strategy_performance"] == binding["performance"]
        and result["profitability"] == binding["profitability"]
    )
    count_valid = (
        contract["fj"]["events"] == binding["fj_events"]
        and contract["fq"]["events"] == binding["fq_events"]
    )
    conclusion_valid = (
        contract["decision"] == binding["decision"]
        and contract["conclusions"]["data_quality_comparability"] == binding["data_quality_comparability"]
        and contract["conclusions"]["strategy_performance"] == binding["performance"]
        and contract["conclusions"]["profitability"] == binding["profitability"]
        and contract["conclusions"]["next_allowed_scope"] == "OUTCOME_CONTRACT_DESIGN_ONLY"
    )
    return {
        "canonical_summary_sha256": binding["canonical_summary_sha256"],
        "decision": binding["decision"],
        "fj_events": binding["fj_events"],
        "fq_events": binding["fq_events"],
        "data_quality_comparability": binding["data_quality_comparability"],
        "performance": binding["performance"],
        "profitability": binding["profitability"],
        "contract_schema_validated": True,
        "identity_validated": identity_valid,
        "result_projection_validated": projection_valid,
        "count_validated": count_valid,
        "conclusion_validated": conclusion_valid,
    }


def frozen_design(expected):
    return {
        "event_entry_contract": {
            "immutable_join_key": "event_id",
            "entry_timestamp_field": "confirmation_timestamp",
            "entry_price_field": "confirmation_close",
            "entry_reference_equality": "entry_reference_price == confirmation_close",
            "evaluation_independence": "EACH_EVENT_EVALUATED_INDEPENDENTLY",
            "position_simulation": False,
        },
        "horizon_contract": {
            "target_valid_h1_bars_after_confirmation": copy.deepcopy(expected["horizons"]),
            "timeframe": "H1",
            "valid_bar_selection": "STRICTLY_AFTER_CONFIRMATION_IN_CHRONOLOGICAL_SOURCE_ORDER",
            "immutable_after_checkpoint": True,
            "descriptive_observations_not_trade_exits": True,
        },
        "direction_normalized_return": {
            "future_price_field": "future_close",
            "long_formula_bps": "((future_close - entry_price) / entry_price) * 10000",
            "short_formula_bps": "((entry_price - future_close) / entry_price) * 10000",
            "basis_point_multiplier": "10000",
            "unit": "BASIS_POINTS",
        },
        "excursion_contract": {
            "future_window": "FIRST_12_VALID_H1_BARS_AFTER_CONFIRMATION",
            "window_high_field": "future_high",
            "window_low_field": "future_low",
            "long_mfe_formula_bps": "max(0, (max_future_high - entry_price) / entry_price) * 10000",
            "long_mae_formula_bps": "max(0, (entry_price - min_future_low) / entry_price) * 10000",
            "short_mfe_formula_bps": "max(0, (entry_price - min_future_low) / entry_price) * 10000",
            "short_mae_formula_bps": "max(0, (max_future_high - entry_price) / entry_price) * 10000",
            "non_negative": True,
            "non_negative_policy": "MAX_WITH_ZERO_BEFORE_BPS_QUANTIZATION",
            "basis_point_multiplier": "10000",
            "unit": "BASIS_POINTS",
        },
        "evaluability_contract": {
            "fail_closed_statuses": {
                "unverified_gap_crossed_before_target_horizon": "NOT_EVALUABLE_DATA_INCOMPLETE_GAP",
                "insufficient_future_valid_h1_bars": "NOT_EVALUABLE_RIGHT_CENSORING",
                "invalid_or_nonfinite_ohlc": "NOT_EVALUABLE_SOURCE_INTEGRITY",
            },
            "accepted_weekend_or_session_closure_effect": "DOES_NOT_INVALIDATE_AND_DOES_NOT_COUNT_AS_A_VALID_BAR",
            "unverified_gap_crossing_interval": "ENTRY_TIMESTAMP_EXCLUSIVE_TO_TARGET_BAR_TIMESTAMP_INCLUSIVE",
            "horizon_status_resolution": "SCAN_CHRONOLOGICALLY_AFTER_CONFIRMATION; FIRST_UNVERIFIED_GAP_OR_INVALID_OHLC_BLOCKS; IF_NO_BLOCKER_AND_TOO_FEW_VALID_BARS_USE_RIGHT_CENSORING",
            "invalid_entry_source_status": "NOT_EVALUABLE_SOURCE_INTEGRITY",
            "horizon_evaluable_status": "EVALUABLE",
            "event_status_values": ["FULLY_EVALUABLE", "PARTIALLY_EVALUABLE", "NOT_EVALUABLE"],
            "all_events_retained": True,
        },
        "output_record_contract": {
            "one_record_per_input_event": True,
            "immutable_event_join_key": "event_id",
            "event_level_status_required": True,
            "horizon_result_keys": ["1", "3", "6", "12"],
            "horizon_result_fields": [
                "horizon_valid_h1_bars", "target_timestamp", "status",
                "direction_normalized_return_bps",
            ],
            "excursion_12_fields": ["status", "mfe_bps", "mae_bps"],
            "status_fields_never_null": True,
        },
        "aggregation_contract": {
            "dataset_pooling_allowed": False,
            "group_dimensions": ["dataset_id", "direction", "year", "horizon_valid_h1_bars"],
            "report_counts": ["total_events", "evaluable_events"],
            "evaluation_coverage_formula": "evaluable_events / total_events",
            "descriptive_statistics": [
                "mean_bps", "median_bps", "p25_bps", "p75_bps",
                "positive_share", "zero_share", "negative_share",
            ],
            "statistics_input": "EVALUABLE_QUANTIZED_BASIS_POINT_VALUES_ONLY",
            "quantile_method": "R7_LINEAR_INTERPOLATION",
            "share_classification": "QUANTIZED_BPS_GREATER_THAN_EQUAL_TO_LESS_THAN_ZERO",
            "performance_pass_fail_threshold": None,
            "hypothesis_selection_after_outcomes_allowed": False,
            "year_dimension": "YEAR_OF_CONFIRMATION_TIMESTAMP",
        },
        "numeric_and_canonical_policy": {
            "arithmetic": "DECIMAL_FROM_SOURCE_STRINGS",
            "basis_point_quantization_decimal_places": 6,
            "basis_point_quantum": "0.000001",
            "rounding": "ROUND_HALF_EVEN",
            "canonical_json": {
                "ensure_ascii": True,
                "sort_keys": True,
                "separators": [",", ":"],
            },
            "absolute_runtime_paths_excluded": True,
        },
        "explicit_exclusions": [
            "SPREAD", "COMMISSION", "SWAP", "SLIPPAGE", "CASH_PNL",
            "LOT_SIZING", "ACCOUNT_BALANCE", "TP_SL", "ORDER_SIMULATION",
            "OVERLAPPING_POSITION_RULES", "PROFITABILITY_CONCLUSION",
            "TRADING_READINESS_CONCLUSION",
        ],
        "conclusions": copy.deepcopy(expected["required_conclusions"]),
    }


def request_allowed(expected, b5_identity, b5_decision, horizons, requested_features, threshold, execute):
    return (
        b5_identity == expected["b5"]["canonical_summary_sha256"]
        and b5_decision == expected["b5"]["decision"]
        and horizons == expected["horizons"]
        and not requested_features
        and threshold is None
        and execute is False
    )


def negative_tests(expected, design):
    results = {}
    results["wrong_b5_identity_or_decision_blocked"] = not request_allowed(
        expected, "0" * 64, "WRONG", expected["horizons"], [], None, False
    )
    results["changed_horizon_set_blocked"] = not request_allowed(
        expected, expected["b5"]["canonical_summary_sha256"], expected["b5"]["decision"],
        [1, 3, 6, 24], [], None, False
    )
    results["tp_sl_or_cash_pnl_request_blocked"] = not request_allowed(
        expected, expected["b5"]["canonical_summary_sha256"], expected["b5"]["decision"],
        expected["horizons"], ["TP_SL", "CASH_PNL"], None, False
    )
    results["performance_threshold_request_blocked"] = not request_allowed(
        expected, expected["b5"]["canonical_summary_sha256"], expected["b5"]["decision"],
        expected["horizons"], [], "POSITIVE_RETURN_THRESHOLD", False
    )
    results["outcome_execution_attempt_blocked"] = not request_allowed(
        expected, expected["b5"]["canonical_summary_sha256"], expected["b5"]["decision"],
        expected["horizons"], [], None, True
    )
    blocked_imports = 0
    for module_name in (
        "market_structure_break_retest_detector",
        "run_fr_prep_b4_fq_holdout_event_population_replay",
    ):
        try:
            builtins.__import__(module_name)
        except ImportError:
            blocked_imports += 1
    results["detector_or_runner_import_request_blocked"] = blocked_imports == 2
    leaked = copy.deepcopy(design)
    leaked["runtime_path"] = str(ROOT.resolve())
    results["absolute_path_identity_leakage_blocked"] = absolute_path_count(leaked) == 1
    try:
        subprocess.Popen(["terminal64.exe", "/blocked"])
        results["external_process_attempt_blocked"] = False
    except RuntimeError:
        results["external_process_attempt_blocked"] = True
    return {
        "test_count": len(results),
        "tests_passed": sum(results.values()),
        "all_passed": all(results.values()),
        "results": results,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", required=True, choices=[MODE])
    parser.add_argument("--authorization", required=True)
    parser.add_argument("--output-root", required=True)
    args = parser.parse_args()
    if Path(args.authorization).resolve() != AUTH.resolve():
        raise SystemExit("B6_AUTHORIZATION_PATH_NOT_ALLOWED")
    if Path(args.output_root).resolve() != RESULT.parent.resolve():
        raise SystemExit("B6_OUTPUT_PATH_NOT_ALLOWED")

    files = Files()
    files.add(AUTH, "b6_authorization")
    files.add(AUTH_SCHEMA, "b6_authorization_schema")
    files.add(CONTRACT_SCHEMA, "b6_contract_schema")
    authorization = read_json(files, AUTH)
    authorization_schema = read_json(files, AUTH_SCHEMA)
    jsonschema.Draft202012Validator.check_schema(authorization_schema)
    jsonschema.Draft202012Validator(authorization_schema).validate(authorization)

    paths = {}
    for binding in authorization["committed_artifacts"]:
        path = (ROOT / binding["path"]).resolve()
        if not path.is_file():
            raise SystemExit("B6_COMMITTED_B5_EVIDENCE_MISSING")
        files.add(path, binding["category"])
        if byte_digest(files.read(path)) != binding["file_sha256"]:
            raise SystemExit("B6_COMMITTED_B5_EVIDENCE_HASH_MISMATCH")
        paths[binding["artifact_id"]] = path

    expected = authorization["expected"]
    before_modules = set(sys.modules)
    with ExternalProcessGuard() as external_guard, ImportGuard() as import_guard:
        b5 = validate_b5(files, paths, expected)
        design_1 = frozen_design(expected)
        design_2 = frozen_design(expected)
        tests = negative_tests(expected, design_1)

    imported_modules = set(sys.modules) - before_modules
    prohibited_loaded = sorted(
        name for name in PROHIBITED_MODULES
        if name in sys.modules or name in imported_modules
    )
    module_import_counts = {
        "detector_import_count": int("market_structure_break_retest_detector" in prohibited_loaded),
        "b2_runner_import_count": int("run_fr_prep_b2_fj_backward_compatible_replay" in prohibited_loaded),
        "b4_runner_import_count": int("run_fr_prep_b4_fq_holdout_event_population_replay" in prohibited_loaded),
        "wrapper_import_count": int("fr_prep_runner_execution_wrapper" in prohibited_loaded),
        "fj_or_fq_runner_import_count": sum(name in prohibited_loaded for name in (
            "run_checkpoint_fj_historical_event_population", "run_checkpoint_fq_holdout_gap_boundary"
        )),
        "outcome_engine_import_count": sum(name in prohibited_loaded for name in (
            "run_checkpoint_fl_shadow_outcomes", "paf_shadow_outcome_labeler"
        )),
        "mt5_import_count": int("MetaTrader5" in prohibited_loaded),
        "ea_import_count": sum(name.lower().endswith("_ea") for name in imported_modules),
    }
    prohibited_execution_counts = {
        key: 0
        for key in (
            "detector_execution_count","b2_runner_execution_count","b4_runner_execution_count",
            "wrapper_execution_count","fj_replay_execution_count","fq_replay_execution_count",
            "outcome_engine_execution_count","outcome_generation_count","future_price_read_count",
            "atr_event_generation_count","tp_sl_calculation_count","fn_interpretation_count",
            "optimization_count","network_execution_count","mt5_execution_count","ea_execution_count"
        )
    }
    mismatch_counters = {
        "b5_identity_mismatch": int(not b5["identity_validated"]),
        "b5_schema_mismatch": int(not b5["contract_schema_validated"]),
        "b5_result_projection_mismatch": int(not b5["result_projection_validated"]),
        "b5_count_mismatch": int(not b5["count_validated"]),
        "b5_conclusion_mismatch": int(not b5["conclusion_validated"]),
        "contract_repeat_mismatch": int(design_1 != design_2),
        "frozen_horizon_mismatch": int(design_1["horizon_contract"]["target_valid_h1_bars_after_confirmation"] != [1, 3, 6, 12]),
        "negative_test_mismatch": int(not tests["all_passed"]),
    }
    if (
        any(mismatch_counters.values())
        or any(module_import_counts.values())
        or any(prohibited_execution_counts.values())
        or prohibited_loaded
    ):
        raise SystemExit("B6_OUTCOME_CONTRACT_DESIGN_BLOCKED")

    contract = {
        "schema_version": "fr_prep_b6_observational_outcome_contract.v1",
        "checkpoint": "FR_PREP_B6",
        "decision": PASS,
        "b5_binding": {
            "canonical_summary_sha256": b5["canonical_summary_sha256"],
            "decision": b5["decision"],
            "fj_events": b5["fj_events"],
            "fq_events": b5["fq_events"],
            "data_quality_comparability": b5["data_quality_comparability"],
            "performance": b5["performance"],
            "profitability": b5["profitability"],
            "contract_schema_validated": b5["contract_schema_validated"],
            "identity_validated": b5["identity_validated"],
            "result_projection_validated": b5["result_projection_validated"],
        },
        **design_1,
        "mismatch_counters": mismatch_counters,
        "negative_tests": tests,
        "runtime_audit": {
            "module_import_counts": module_import_counts,
            "prohibited_execution_counts": prohibited_execution_counts,
            "external_process": {
                "successful_launch_count": 0,
                "blocked_launch_count": external_guard.blocked,
            },
            "blocked_import_requests": import_guard.blocked,
            "file_access": files.report(),
            "counter_provenance": {
                "module_imports": "sys.modules delta plus fail-closed import interception",
                "executions": "contract design contains no outcome, future-price, replay, detector, MT5, or EA dispatch",
                "external_process": "Popen, os.system, and os.startfile fail-closed interception",
                "file_access": "exact resolved-path allowlist for committed B5 JSON evidence only",
            },
        },
        "prohibited_modules": prohibited_loaded,
        "execution_status": "PASS",
        "future_prices_inspected": False,
        "outcome_records_generated": False,
        "outcome_execution_count": 0,
        "performance_threshold": None,
        "raw_csv_accessed": False,
        "atr_events_generated": False,
        "tp_sl_calculated": False,
        "fn_interpretation_performed": False,
        "optimization_performed": False,
        "strategy_or_indicator_changes": False,
        "mt5_executed": False,
        "ea_executed": False,
        "absolute_runtime_path_in_canonical_identity_count": 0,
    }
    contract["canonical_summary_sha256"] = digest(contract)
    if absolute_path_count(contract):
        raise SystemExit("B6_ABSOLUTE_RUNTIME_PATH_IDENTITY_LEAK")
    contract_schema = read_json(files, CONTRACT_SCHEMA)
    jsonschema.Draft202012Validator.check_schema(contract_schema)
    jsonschema.Draft202012Validator(contract_schema).validate(contract)

    CONTRACT.write_text(json.dumps(contract, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    result = {
        "decision": PASS,
        "canonical_summary_sha256": contract["canonical_summary_sha256"],
        "b5_canonical_summary_sha256": b5["canonical_summary_sha256"],
        "horizons_valid_h1_bars": design_1["horizon_contract"]["target_valid_h1_bars_after_confirmation"],
        "fail_closed_statuses": design_1["evaluability_contract"]["fail_closed_statuses"],
        "accepted_closures_invalidate": False,
        "numeric_policy": expected["numeric_policy"],
        "conclusions": design_1["conclusions"],
        "mismatch_count": sum(mismatch_counters.values()),
        "negative_tests": {"passed": tests["tests_passed"], "total": tests["test_count"]},
        "prohibited_import_count": sum(module_import_counts.values()),
        "prohibited_execution_count": sum(prohibited_execution_counts.values()),
        "future_prices_inspected": False,
        "outcome_records_generated": False,
        "execution_status": "PASS",
    }
    RESULT.parent.mkdir(parents=True, exist_ok=True)
    RESULT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
