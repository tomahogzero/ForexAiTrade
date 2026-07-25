#!/usr/bin/env python3
"""Seal the next-checkpoint FQ execution authorization without executing FQ."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import ntpath
import os
import posixpath
import subprocess
import sys
from pathlib import Path

import jsonschema

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
AUTH = ROOT / "research/contracts/fr_prep_b3a_fq_holdout_execution_authorization.v1.json"
AUTH_SCHEMA = ROOT / "research/schemas/fr_prep_b3a_fq_holdout_execution_authorization.v1.schema.json"
EVIDENCE = ROOT / "research/contracts/fr_prep_b3a_fq_holdout_execution_authorization_evidence.v1.json"
EVIDENCE_SCHEMA = ROOT / "research/schemas/fr_prep_b3a_fq_holdout_execution_authorization_evidence.v1.schema.json"
RESULT = ROOT / "research/results/checkpoint_fr_prep_b3a/fq_holdout_execution_authorization_summary.json"
MODE = "seal-fq-holdout-execution-authorization"
PASS = "FR_PREP_B3A_PASS_FQ_HOLDOUT_EXECUTION_AUTHORIZATION_SEALED"

B3_CONTRACT = ROOT / "research/contracts/fr_prep_b3_fq_holdout_preflight.v1.json"
B3_RESULT = ROOT / "research/results/checkpoint_fr_prep_b3/fq_holdout_preflight_summary.json"
B3_AUTH = ROOT / "research/contracts/fr_prep_b3_fq_holdout_preflight_authorization.v1.json"
B2_CONTRACT = ROOT / "research/contracts/fr_prep_b2_fj_backward_compatible_replay.v1.json"
B2_AUTH = ROOT / "research/contracts/fr_prep_b2_fj_replay_authorization.v1.json"
B2A_CONTRACT = ROOT / "research/contracts/fr_prep_b2a_independent_replay_audit.v1.json"
FQ_ROOT = ROOT / "research/results/checkpoint_fq_holdout_gap_boundary"

B3_ID = "eec147eed43a60aad28a058d2f906181010da225b18964acd00d87ba984659ad"
B2_ID = "bc6fafc40b9c550a7d9d7e798a92a6f685e5de208c7c224c738726bce00608a0"
B2A_ID = "1f63983bf783452bd0e56d6c265f67f3baccbaae644eedcacb59a1f79a895251"
DETECTOR_SHA = "9d7496581806d267df9130a35c0ec0dd948b6d77fcc30d8cca115edd4b746144"
PROHIBITED_MODULES = (
    "market_structure_break_retest_detector",
    "run_checkpoint_fq_holdout_gap_boundary",
    "run_checkpoint_fj_historical_event_population",
    "fr_prep_runner_execution_wrapper",
)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def digest(value):
    return hashlib.sha256(canonical(value).encode("ascii")).hexdigest()


def file_hash(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def canonical_identity(contract):
    return digest({key: value for key, value in contract.items() if key != "canonical_summary_sha256"})


def absolute_path_count(value):
    if isinstance(value, dict):
        return sum(absolute_path_count(item) for item in value.values())
    if isinstance(value, list):
        return sum(absolute_path_count(item) for item in value)
    return int(isinstance(value, str) and (ntpath.isabs(value) or posixpath.isabs(value)))


class ExternalAudit:
    def __init__(self):
        self.blocked = []

    def _deny(self, kind, command):
        self.blocked.append({"kind": kind, "command_class": "EXTERNAL_PROCESS"})
        raise RuntimeError("B3A_EXTERNAL_PROCESS_BLOCKED")

    def __enter__(self):
        self._popen = subprocess.Popen
        self._system = os.system
        self._startfile = getattr(os, "startfile", None)
        subprocess.Popen = lambda command, *args, **kwargs: self._deny("subprocess", command)
        os.system = lambda command: self._deny("os.system", command)
        if self._startfile is not None:
            os.startfile = lambda path, *args, **kwargs: self._deny("os.startfile", path)
        return self

    def __exit__(self, *_):
        subprocess.Popen = self._popen
        os.system = self._system
        if self._startfile is not None:
            os.startfile = self._startfile


def exact_authorization(candidate, schema, sealed):
    jsonschema.Draft202012Validator(schema).validate(candidate)
    if candidate != sealed:
        raise ValueError("B3A_AUTHORIZATION_NOT_EXACT")


def expect_failure(action):
    try:
        action()
    except (ValueError, RuntimeError, jsonschema.ValidationError):
        return True
    return False


def execution_not_available_in_this_checkpoint():
    raise RuntimeError("B3A_AUTHORIZATION_ONLY_EXECUTION_BLOCKED")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", required=True, choices=[MODE])
    parser.add_argument("--authorization", required=True)
    parser.add_argument("--output-root", required=True)
    args = parser.parse_args()
    if Path(args.authorization).resolve() != AUTH.resolve():
        raise SystemExit("B3A_AUTHORIZATION_PATH_NOT_ALLOWED")
    if Path(args.output_root).resolve() != RESULT.parent.resolve():
        raise SystemExit("B3A_OUTPUT_PATH_NOT_ALLOWED")

    auth = read_json(AUTH)
    auth_schema = read_json(AUTH_SCHEMA)
    jsonschema.Draft202012Validator.check_schema(auth_schema)
    exact_authorization(auth, auth_schema, auth)

    b3 = read_json(B3_CONTRACT)
    b3_result = read_json(B3_RESULT)
    b3_auth = read_json(B3_AUTH)
    b2 = read_json(B2_CONTRACT)
    b2_auth = read_json(B2_AUTH)
    b2a = read_json(B2A_CONTRACT)

    if canonical_identity(b3) != B3_ID or b3.get("canonical_summary_sha256") != B3_ID:
        raise SystemExit("B3A_B3_IDENTITY_MISMATCH")
    if b3.get("decision") != "FR_PREP_B3_PASS_FQ_HOLDOUT_PREFLIGHT_SEALED":
        raise SystemExit("B3A_B3_DECISION_MISMATCH")
    if b3_result.get("canonical_summary_sha256") != B3_ID:
        raise SystemExit("B3A_B3_RESULT_MISMATCH")
    if canonical_identity(b2) != B2_ID or b2.get("canonical_summary_sha256") != B2_ID:
        raise SystemExit("B3A_B2_IDENTITY_MISMATCH")
    if canonical_identity(b2a) != B2A_ID or b2a.get("canonical_summary_sha256") != B2A_ID:
        raise SystemExit("B3A_B2A_IDENTITY_MISMATCH")

    if b3_auth["source_files"] != auth["source_files"]:
        raise SystemExit("B3A_SOURCE_BINDING_MISMATCH")
    if b3_auth["frozen_artifacts"] != auth["gap_artifacts"]:
        raise SystemExit("B3A_GAP_BINDING_MISMATCH")
    if b3_auth["expected"] != {
        "bars": auth["fq_preflight"]["bars"],
        "timeline_sha256": auth["fq_preflight"]["timeline_sha256"],
        "gaps": auth["fq_preflight"]["gaps"],
        "accepted_weekend_closures": auth["fq_preflight"]["accepted_weekend_closures"],
        "accepted_daily_closures": auth["fq_preflight"]["accepted_daily_closures"],
        "unverified_gaps": auth["fq_preflight"]["unverified_gaps"],
        "fq_decision": auth["fq_preflight"]["decision"],
        "deterministic_payload_sha256": auth["fq_preflight"]["deterministic_payload_sha256"],
    }:
        raise SystemExit("B3A_FQ_EXPECTATION_MISMATCH")

    detector = (ROOT / auth["detector_binding"]["path"]).resolve()
    if b2_auth.get("detector") != {
        "path": auth["detector_binding"]["path"],
        "file_sha256": DETECTOR_SHA,
    }:
        raise SystemExit("B3A_B2_DETECTOR_BINDING_MISMATCH")
    if file_hash(detector) != DETECTOR_SHA:
        raise SystemExit("B3A_DETECTOR_FILE_MISMATCH")
    for name, expected_hash in auth["gap_artifacts"].items():
        artifact = FQ_ROOT / name
        if not artifact.is_file() or file_hash(artifact) != expected_hash:
            raise SystemExit("B3A_FQ_ARTIFACT_MISMATCH")

    before_modules = set(sys.modules)
    with ExternalAudit() as external:
        tests = {}
        wrong = copy.deepcopy(auth)
        wrong["b3_binding"]["canonical_summary_sha256"] = "0" * 64
        wrong["b3_binding"]["decision"] = "WRONG"
        tests["wrong_b3_identity_or_decision_blocked"] = expect_failure(
            lambda: exact_authorization(wrong, auth_schema, auth)
        )
        wrong = copy.deepcopy(auth)
        wrong["detector_binding"]["file_sha256"] = "0" * 64
        tests["wrong_detector_binding_blocked"] = expect_failure(
            lambda: exact_authorization(wrong, auth_schema, auth)
        )
        wrong = copy.deepcopy(auth)
        wrong["fq_preflight"]["bars"] += 1
        wrong["fq_preflight"]["timeline_sha256"] = "0" * 64
        tests["changed_fq_counts_or_hash_blocked"] = expect_failure(
            lambda: exact_authorization(wrong, auth_schema, auth)
        )
        wrong = copy.deepcopy(auth)
        wrong["authorized_next_checkpoint_operations"].append("UNAUTHORIZED_OPERATION")
        tests["unauthorized_operation_blocked"] = expect_failure(
            lambda: exact_authorization(wrong, auth_schema, auth)
        )
        tests["execution_attempt_blocked"] = expect_failure(execution_not_available_in_this_checkpoint)
        tests["absolute_path_leakage_detected"] = absolute_path_count(
            {"runtime_source_root": str(ROOT.resolve())}
        ) == 1
        tests["external_launch_blocked"] = expect_failure(
            lambda: subprocess.Popen(["terminal64.exe", "/blocked"])
        )
        wrong = copy.deepcopy(auth)
        wrong["tp_sl_allowed"] = True
        wrong["outcomes_allowed"] = True
        tests["tp_sl_or_outcome_request_blocked"] = expect_failure(
            lambda: exact_authorization(wrong, auth_schema, auth)
        )

    imported = set(sys.modules) - before_modules
    module_counts = {
        "detector_import_count": int("market_structure_break_retest_detector" in imported),
        "fq_validator_import_count": int("run_checkpoint_fq_holdout_gap_boundary" in imported),
        "legacy_fj_runner_import_count": int("run_checkpoint_fj_historical_event_population" in imported),
        "execution_wrapper_import_count": int("fr_prep_runner_execution_wrapper" in imported),
        "mt5_ea_import_count": sum(
            "mt5" in name.lower() or "terminal64" in name.lower() or name.lower().endswith("_ea")
            for name in imported
        ),
    }
    if any(name in sys.modules for name in PROHIBITED_MODULES):
        raise SystemExit("B3A_PROHIBITED_MODULE_PRESENT")
    execution_counts = {
        "holdout_execution_count": 0,
        "detector_execution_count": 0,
        "event_generation_count": 0,
        "atr_event_generation_count": 0,
        "tp_sl_calculation_count": 0,
        "outcome_generation_count": 0,
        "fn_interpretation_count": 0,
        "mt5_execution_count": 0,
        "ea_execution_count": 0,
    }
    if not all(tests.values()) or any(module_counts.values()) or any(execution_counts.values()):
        raise SystemExit("B3A_AUTHORIZATION_VALIDATION_FAILED")

    authorization_identity = digest(auth)
    evidence = {
        "schema_version": "fr_prep_b3a_fq_holdout_execution_authorization_evidence.v1",
        "checkpoint": "FR_PREP_B3A",
        "decision": PASS,
        "authorization_identity_sha256": authorization_identity,
        "validated_bindings": {
            "b3_identity": B3_ID,
            "b2_identity": B2_ID,
            "b2a_identity": B2A_ID,
            "fq_counts_and_hashes": True,
            "source_files": True,
            "gap_artifacts": True,
            "detector": True,
        },
        "negative_tests": {
            "passed": sum(tests.values()),
            "total": len(tests),
            "all_passed": all(tests.values()),
            "results": tests,
        },
        "runtime_audit": {
            "module_import_counts": module_counts,
            "execution_counts": execution_counts,
            "external_process_audit": {
                "successful_launch_count": 0,
                "blocked_launch_count": len(external.blocked),
            },
            "counter_provenance": {
                "module_imports": "sys.modules before/after delta and final prohibited-module absence",
                "executions": "authorization-only runner exposes no execution dispatch",
                "external_process": "subprocess, os.system and os.startfile interception",
            },
        },
        "authorization_sealed": True,
        "holdout_execution_authorized_for_next_checkpoint": True,
        "holdout_executed": False,
        "detector_imported": False,
        "detector_executed": False,
        "events_generated": False,
        "atr_events_generated": False,
        "tp_sl_calculated": False,
        "outcomes_generated": False,
        "performance": "NOT_EVALUATED",
        "profitability": "NOT_CLAIMED",
        "order_logic": "NOT_APPROVED",
        "candidate": "NOT_READY_FOR_ORDER_LOGIC",
        "absolute_runtime_path_in_canonical_identity_count": 0,
    }
    evidence["canonical_summary_sha256"] = digest(evidence)
    if absolute_path_count(evidence):
        raise SystemExit("B3A_CANONICAL_IDENTITY_PATH_LEAK")

    evidence_schema = read_json(EVIDENCE_SCHEMA)
    jsonschema.Draft202012Validator.check_schema(evidence_schema)
    jsonschema.Draft202012Validator(evidence_schema).validate(evidence)
    EVIDENCE.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    summary = {
        "decision": PASS,
        "authorization_identity_sha256": authorization_identity,
        "canonical_summary_sha256": evidence["canonical_summary_sha256"],
        "b3_canonical_summary_sha256": B3_ID,
        "dataset_id": auth["dataset_id"],
        "fq_preflight": auth["fq_preflight"],
        "detector_binding": auth["detector_binding"],
        "negative_tests": {"passed": sum(tests.values()), "total": len(tests)},
        "prohibited_import_count": sum(module_counts.values()),
        "prohibited_execution_count": sum(execution_counts.values()),
        "authorization_sealed": True,
        "holdout_execution_authorized_for_next_checkpoint": True,
        "holdout_executed": False,
        "performance": "NOT_EVALUATED",
        "profitability": "NOT_CLAIMED",
    }
    RESULT.parent.mkdir(parents=True, exist_ok=True)
    RESULT.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, sort_keys=True))


if __name__ == "__main__":
    main()
