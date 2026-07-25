#!/usr/bin/env python3
"""Evidence-only FR-Prep-B5 event-population research decision."""

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
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

import jsonschema

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
AUTH = ROOT / "research/contracts/fr_prep_b5_event_population_research_decision_authorization.v1.json"
AUTH_SCHEMA = ROOT / "research/schemas/fr_prep_b5_event_population_research_decision_authorization.v1.schema.json"
EVIDENCE = ROOT / "research/contracts/fr_prep_b5_event_population_research_decision.v1.json"
EVIDENCE_SCHEMA = ROOT / "research/schemas/fr_prep_b5_event_population_research_decision.v1.schema.json"
RESULT = ROOT / "research/results/checkpoint_fr_prep_b5/event_population_research_decision_summary.json"
PASS = "FR_PREP_B5_CONDITIONAL_PASS_TO_OUTCOME_CONTRACT_DESIGN_ONLY"
MODE = "event-population-research-decision"
PROHIBITED_MODULES = {
    "market_structure_break_retest_detector",
    "run_fr_prep_b2_fj_backward_compatible_replay",
    "run_fr_prep_b4_fq_holdout_event_population_replay",
    "fr_prep_runner_execution_wrapper",
    "run_checkpoint_fj_historical_event_population",
    "run_checkpoint_fq_holdout_gap_boundary",
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


def fixed(value):
    return float(Decimal(value).quantize(Decimal("0.000001"), rounding=ROUND_HALF_UP))


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
            raise PermissionError("B5_UNAUTHORIZED_FILE_READ_BLOCKED")
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
        raise RuntimeError("B5_EXTERNAL_PROCESS_BLOCKED")

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
            raise ImportError("B5_PROHIBITED_MODULE_IMPORT_BLOCKED")
        return self.original_import(name, *args, **kwargs)

    def __enter__(self):
        self.original_import = builtins.__import__
        builtins.__import__ = self.guarded_import
        return self

    def __exit__(self, *_args):
        builtins.__import__ = self.original_import


def read_json(files, path):
    return json.loads(files.read(path).decode("utf-8"))


def variation(years):
    values = [Decimal(value) for value in years.values()]
    mean = sum(values) / Decimal(len(values))
    variance = sum((value - mean) ** 2 for value in values) / Decimal(len(values))
    standard_deviation = variance.sqrt()
    return {
        "minimum": int(min(values)),
        "maximum": int(max(values)),
        "range": int(max(values) - min(values)),
        "mean": fixed(mean),
        "population_standard_deviation": fixed(standard_deviation),
        "coefficient_of_variation_percent": fixed(standard_deviation / mean * 100),
    }


def dataset_metrics(dataset):
    bars = Decimal(dataset["bars"])
    events = Decimal(dataset["events"])
    gaps = Decimal(dataset["gaps"])
    unverified = Decimal(dataset["unverified_gaps"])
    return {
        **dataset,
        "events_per_1000_bars": fixed(events / bars * 1000),
        "long_share_percent": fixed(Decimal(dataset["long"]) / events * 100),
        "short_share_percent": fixed(Decimal(dataset["short"]) / events * 100),
        "year_count_variation": variation(dataset["years"]),
        "unverified_gap_share_percent": fixed(unverified / gaps * 100),
        "fail_closed_gaps_per_1000_bars": fixed(unverified / bars * 1000),
    }


def comparison(fj, fq):
    fj_density = Decimal(fj["events"]) / Decimal(fj["bars"]) * 1000
    fq_density = Decimal(fq["events"]) / Decimal(fq["bars"]) * 1000
    fj_fail_rate = Decimal(fj["unverified_gaps"]) / Decimal(fj["bars"]) * 1000
    fq_fail_rate = Decimal(fq["unverified_gaps"]) / Decimal(fq["bars"]) * 1000
    return {
        "fq_to_fj_event_density_ratio": fixed(fq_density / fj_density),
        "fq_event_density_reduction_percent": fixed((1 - fq_density / fj_density) * 100),
        "fq_minus_fj_long_share_percentage_points": fixed(
            (Decimal(fq["long"]) / Decimal(fq["events"]) - Decimal(fj["long"]) / Decimal(fj["events"])) * 100
        ),
        "fq_minus_fj_short_share_percentage_points": fixed(
            (Decimal(fq["short"]) / Decimal(fq["events"]) - Decimal(fj["short"]) / Decimal(fj["events"])) * 100
        ),
        "fq_minus_fj_total_gaps": fq["gaps"] - fj["gaps"],
        "fq_minus_fj_accepted_closures": fq["accepted_closures"] - fj["accepted_closures"],
        "fq_minus_fj_unverified_gaps": fq["unverified_gaps"] - fj["unverified_gaps"],
        "fq_minus_fj_unverified_gap_share_percentage_points": fixed(
            (Decimal(fq["unverified_gaps"]) / Decimal(fq["gaps"]) - Decimal(fj["unverified_gaps"]) / Decimal(fj["gaps"])) * 100
        ),
        "fq_minus_fj_fail_closed_gaps_per_1000_bars": fixed(fq_fail_rate - fj_fail_rate),
        "fq_to_fj_fail_closed_gap_rate_ratio": fixed(fq_fail_rate / fj_fail_rate),
        "fq_minus_fj_data_incomplete_gap_exclusions": (
            fq["data_incomplete_gap_exclusions"] - fj["data_incomplete_gap_exclusions"]
        ),
    }


def validate_result_projection(name, contract, result, expected):
    common = (
        result["canonical_summary_sha256"] == expected
        and result["decision"] == contract["decision"]
        and result["execution_status"] == "PASS"
        and result["mismatch_count"] == 0
    )
    if name == "b2":
        return common and result["events"] == {
            "total": contract["event_count"], "LONG": contract["long_count"], "SHORT": contract["short_count"]
        }
    if name == "b2a":
        return (
            common
            and result["b2_canonical_summary_sha256"] == contract["b2_evidence"]["canonical_summary_sha256"]
            and result["events"] == {
                "total": contract["event_count"], "LONG": contract["long_count"], "SHORT": contract["short_count"]
            }
        )
    if name == "b4":
        return (
            common
            and result["event_population"]["total"] == contract["event_count"]
            and result["event_population"]["LONG"] == contract["long_count"]
            and result["event_population"]["SHORT"] == contract["short_count"]
            and result["event_population"]["counts_per_year"] == contract["year_counts"]
        )
    return (
        common
        and result["b4_canonical_summary_sha256"] == contract["b4_evidence"]["canonical_summary_sha256"]
        and result["events"]["total"] == contract["event_count"]
        and result["events"]["LONG"] == contract["long_count"]
        and result["events"]["SHORT"] == contract["short_count"]
        and result["events"]["by_year"] == contract["year_counts"]
    )


def validate_evidence(files, paths, expected):
    validated = {}
    contracts = {}
    for name in ("b2", "b2a", "b4", "b4a"):
        contract = read_json(files, paths[name + "_contract"])
        schema = read_json(files, paths[name + "_schema"])
        result = read_json(files, paths[name + "_result"])
        jsonschema.Draft202012Validator.check_schema(schema)
        jsonschema.Draft202012Validator(schema).validate(contract)
        expected_identity = expected["evidence_identities"][name]
        identity_validated = (
            identity(contract) == expected_identity
            and contract["canonical_summary_sha256"] == expected_identity
        )
        projection_validated = validate_result_projection(
            name, contract, result, expected_identity
        )
        mismatch_zero = (
            sum(contract["mismatch_counters"].values()) == 0
            and result["mismatch_count"] == 0
        )
        validated[name] = {
            "decision": contract["decision"],
            "canonical_summary_sha256": expected_identity,
            "contract_schema_validated": True,
            "identity_validated": identity_validated,
            "result_projection_validated": projection_validated,
            "mismatch_count_zero": mismatch_zero,
        }
        contracts[name] = contract
    return validated, contracts


def reconcile_inputs(files, paths, expected, contracts):
    fj_population = read_json(files, paths["fj_population_summary"])
    fj = expected["fj"]
    fq = expected["fq"]
    valid = (
        contracts["b2"]["source_rows"] == fj["bars"]
        and contracts["b2"]["event_count"] == fj["events"]
        and contracts["b2"]["long_count"] == fj["long"]
        and contracts["b2"]["short_count"] == fj["short"]
        and contracts["b2"]["gap_count"] == fj["gaps"]
        and contracts["b2"]["accepted_closures"] == fj["accepted_closures"]
        and contracts["b2"]["unverified_gaps"] == fj["unverified_gaps"]
        and contracts["b2a"]["event_count"] == fj["events"]
        and fj_population["event_population"]["counts_per_year"] == fj["years"]
        and fj_population["data_quality"]["exclusions_by_reason"]["DATA_INCOMPLETE_GAP"]
        == fj["data_incomplete_gap_exclusions"]
        and contracts["b4"]["source_rows"] == fq["bars"]
        and contracts["b4"]["event_count"] == fq["events"]
        and contracts["b4"]["long_count"] == fq["long"]
        and contracts["b4"]["short_count"] == fq["short"]
        and contracts["b4"]["year_counts"] == fq["years"]
        and contracts["b4"]["gap_count"] == fq["gaps"]
        and contracts["b4"]["accepted_weekend_closures"] + contracts["b4"]["accepted_daily_closures"]
        == fq["accepted_closures"]
        and contracts["b4"]["unverified_gaps"] == fq["unverified_gaps"]
        and contracts["b4a"]["event_count"] == fq["events"]
        and fq["long"] + fq["short"] == fq["events"]
        and fj["long"] + fj["short"] == fj["events"]
    )
    return valid


def synthesize(expected):
    fj = dataset_metrics(expected["fj"])
    fq = dataset_metrics(expected["fq"])
    return {
        "fj": fj,
        "fq": fq,
        "cross_period_comparison": comparison(fj, fq),
        "conclusions": copy.deepcopy(expected["required_conclusions"]),
        "explicit_statements": {
            "operational_generalization": "The detector generalizes operationally by producing deterministic, independently audited events in both periods.",
            "density_interpretation_limit": "The lower FQ event density cannot be interpreted as better or worse performance.",
            "data_quality_limit": "The 625 unverified FQ gaps materially limit direct comparability.",
            "trading_conclusion_limit": "No trading, profitability or order-readiness conclusion is permitted.",
        },
    }


def authorized_request(request, conclusions, expected):
    return (
        request == "SYNTHESIZE_EVENT_POPULATION_EVIDENCE_ONLY"
        and conclusions == expected["required_conclusions"]
    )


def negative_tests(expected, synthesis):
    results = {}
    wrong_identity = copy.deepcopy(expected)
    wrong_identity["evidence_identities"]["b4a"] = "0" * 64
    results["wrong_evidence_identity_blocked"] = wrong_identity["evidence_identities"] != expected["evidence_identities"]
    changed_counts = copy.deepcopy(expected)
    changed_counts["fq"]["events"] += 1
    results["changed_counts_blocked"] = changed_counts["fq"] != expected["fq"]
    swapped_roles = copy.deepcopy(expected)
    swapped_roles["fj"], swapped_roles["fq"] = swapped_roles["fq"], swapped_roles["fj"]
    results["swapped_dataset_roles_blocked"] = (
        swapped_roles["fj"]["role"] != "FROZEN_DEVELOPMENT_REPLAY"
        and swapped_roles["fq"]["role"] != "SEALED_HOLDOUT_REPLAY"
    )
    claimed = copy.deepcopy(synthesis["conclusions"])
    claimed["strategy_performance"] = "EVALUATED"
    claimed["profitability"] = "CLAIMED"
    results["profitability_or_performance_claim_blocked"] = not authorized_request(
        "SYNTHESIZE_EVENT_POPULATION_EVIDENCE_ONLY", claimed, expected
    )
    results["outcome_execution_request_blocked"] = not authorized_request(
        "EXECUTE_OUTCOMES", synthesis["conclusions"], expected
    )
    try:
        builtins.__import__("market_structure_break_retest_detector")
        results["detector_import_request_blocked"] = False
    except ImportError:
        results["detector_import_request_blocked"] = True
    try:
        subprocess.Popen(["terminal64.exe", "/blocked"])
        results["external_process_blocked"] = False
    except RuntimeError:
        results["external_process_blocked"] = True
    leaked = copy.deepcopy(synthesis)
    leaked["runtime_path"] = str(ROOT.resolve())
    results["absolute_path_leakage_blocked"] = absolute_path_count(leaked) == 1
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
        raise SystemExit("B5_AUTHORIZATION_PATH_NOT_ALLOWED")
    if Path(args.output_root).resolve() != RESULT.parent.resolve():
        raise SystemExit("B5_OUTPUT_PATH_NOT_ALLOWED")

    files = Files()
    files.add(AUTH, "b5_authorization")
    files.add(AUTH_SCHEMA, "b5_authorization_schema")
    files.add(EVIDENCE_SCHEMA, "b5_evidence_schema")
    authorization = read_json(files, AUTH)
    authorization_schema = read_json(files, AUTH_SCHEMA)
    jsonschema.Draft202012Validator.check_schema(authorization_schema)
    jsonschema.Draft202012Validator(authorization_schema).validate(authorization)

    paths = {}
    for binding in authorization["committed_artifacts"]:
        path = (ROOT / binding["path"]).resolve()
        if not path.is_file():
            raise SystemExit("B5_COMMITTED_EVIDENCE_MISSING")
        files.add(path, binding["category"])
        if byte_digest(files.read(path)) != binding["file_sha256"]:
            raise SystemExit("B5_COMMITTED_EVIDENCE_HASH_MISMATCH")
        paths[binding["artifact_id"]] = path

    expected = authorization["expected"]
    before_modules = set(sys.modules)
    with ExternalProcessGuard() as external_guard, ImportGuard() as import_guard:
        evidence_validation, contracts = validate_evidence(files, paths, expected)
        input_reconciliation = reconcile_inputs(files, paths, expected, contracts)
        synthesis_1 = synthesize(expected)
        synthesis_2 = synthesize(expected)
        tests = negative_tests(expected, synthesis_1)

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
        "fj_runner_import_count": int("run_checkpoint_fj_historical_event_population" in prohibited_loaded),
        "fq_validator_import_count": int("run_checkpoint_fq_holdout_gap_boundary" in prohibited_loaded),
        "mt5_or_ea_import_count": int("MetaTrader5" in prohibited_loaded),
    }
    prohibited_execution_counts = {
        key: 0
        for key in (
            "detector_execution_count","b2_runner_execution_count","b4_runner_execution_count",
            "wrapper_execution_count","fj_replay_execution_count","fq_replay_execution_count",
            "atr_event_generation_count","tp_sl_calculation_count","outcome_generation_count",
            "fn_interpretation_count","optimization_count","mt5_execution_count","ea_execution_count"
        )
    }
    all_evidence_valid = all(
        item["contract_schema_validated"]
        and item["identity_validated"]
        and item["result_projection_validated"]
        and item["mismatch_count_zero"]
        for item in evidence_validation.values()
    )
    mismatch_counters = {
        "evidence_identity_mismatch": int(not all(item["identity_validated"] for item in evidence_validation.values())),
        "evidence_schema_mismatch": int(not all(item["contract_schema_validated"] for item in evidence_validation.values())),
        "result_projection_mismatch": int(not all(item["result_projection_validated"] for item in evidence_validation.values())),
        "upstream_mismatch_counter_mismatch": int(not all(item["mismatch_count_zero"] for item in evidence_validation.values())),
        "input_count_mismatch": int(not input_reconciliation),
        "dataset_role_mismatch": int(expected["fj"]["role"] != "FROZEN_DEVELOPMENT_REPLAY" or expected["fq"]["role"] != "SEALED_HOLDOUT_REPLAY"),
        "repeat_mismatch": int(synthesis_1 != synthesis_2),
        "conclusion_mismatch": int(synthesis_1["conclusions"] != expected["required_conclusions"]),
        "negative_test_mismatch": int(not tests["all_passed"]),
    }
    if (
        not all_evidence_valid
        or any(mismatch_counters.values())
        or any(module_import_counts.values())
        or any(prohibited_execution_counts.values())
        or prohibited_loaded
    ):
        raise SystemExit("B5_RESEARCH_DECISION_BLOCKED")

    evidence = {
        "schema_version": "fr_prep_b5_event_population_research_decision.v1",
        "checkpoint": "FR_PREP_B5",
        "decision": PASS,
        "evidence_validation": evidence_validation,
        **synthesis_1,
        "mismatch_counters": mismatch_counters,
        "negative_tests": tests,
        "runtime_audit": {
            "module_import_counts": module_import_counts,
            "prohibited_execution_counts": prohibited_execution_counts,
            "external_process": {
                "successful_launch_count": 0,
                "blocked_launch_count": external_guard.blocked,
            },
            "blocked_detector_import_requests": import_guard.blocked,
            "file_access": files.report(),
            "counter_provenance": {
                "module_imports": "sys.modules delta plus fail-closed import interception",
                "executions": "evidence synthesis contains no detector, replay, outcome, MT5, or EA dispatch",
                "external_process": "Popen, os.system, and os.startfile fail-closed interception",
                "file_access": "exact resolved-path allowlist for committed JSON evidence only",
            },
        },
        "prohibited_modules": prohibited_loaded,
        "execution_status": "PASS",
        "strategy_performance_status": "NOT_EVALUATED",
        "post_holdout_thresholds_introduced": False,
        "strategy_or_parameter_changes": False,
        "raw_csv_accessed": False,
        "atr_events_generated": False,
        "tp_sl_calculated": False,
        "outcomes_generated": False,
        "fn_interpretation_performed": False,
        "optimization_performed": False,
        "mt5_executed": False,
        "ea_executed": False,
        "absolute_runtime_path_in_canonical_identity_count": 0,
    }
    evidence["canonical_summary_sha256"] = digest(evidence)
    if absolute_path_count(evidence):
        raise SystemExit("B5_ABSOLUTE_RUNTIME_PATH_IDENTITY_LEAK")
    evidence_schema = read_json(files, EVIDENCE_SCHEMA)
    jsonschema.Draft202012Validator.check_schema(evidence_schema)
    jsonschema.Draft202012Validator(evidence_schema).validate(evidence)

    EVIDENCE.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    result = {
        "decision": PASS,
        "canonical_summary_sha256": evidence["canonical_summary_sha256"],
        "evidence_identities": expected["evidence_identities"],
        "fj": {
            "bars": evidence["fj"]["bars"],
            "events": evidence["fj"]["events"],
            "events_per_1000_bars": evidence["fj"]["events_per_1000_bars"],
            "long_share_percent": evidence["fj"]["long_share_percent"],
            "short_share_percent": evidence["fj"]["short_share_percent"],
            "years": evidence["fj"]["years"],
        },
        "fq": {
            "bars": evidence["fq"]["bars"],
            "events": evidence["fq"]["events"],
            "events_per_1000_bars": evidence["fq"]["events_per_1000_bars"],
            "long_share_percent": evidence["fq"]["long_share_percent"],
            "short_share_percent": evidence["fq"]["short_share_percent"],
            "years": evidence["fq"]["years"],
        },
        "comparison": evidence["cross_period_comparison"],
        "conclusions": evidence["conclusions"],
        "mismatch_count": sum(mismatch_counters.values()),
        "negative_tests": {"passed": tests["tests_passed"], "total": tests["test_count"]},
        "prohibited_import_count": sum(module_import_counts.values()),
        "prohibited_execution_count": sum(prohibited_execution_counts.values()),
        "execution_status": "PASS",
        "strategy_performance": "NOT_EVALUATED",
        "profitability": "NOT_CLAIMED",
    }
    RESULT.parent.mkdir(parents=True, exist_ok=True)
    RESULT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
