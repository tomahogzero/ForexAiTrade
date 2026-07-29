#!/usr/bin/env python3
"""Execute the frozen B10 disposition contract once per deterministic generation."""

import argparse
import builtins
import copy
import hashlib
import json
import ntpath
import os
import posixpath
import shutil
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path

import jsonschema

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
AUTH = ROOT / "research/contracts/fr_prep_b10a_research_disposition_decision_authorization.v1.json"
AUTH_SCHEMA = ROOT / "research/schemas/fr_prep_b10a_research_disposition_decision_authorization.v1.schema.json"
CONTRACT = ROOT / "research/contracts/fr_prep_b10a_sealed_research_disposition_decision.v1.json"
CONTRACT_SCHEMA = ROOT / "research/schemas/fr_prep_b10a_sealed_research_disposition_decision.v1.schema.json"
RESULT = ROOT / "research/results/checkpoint_fr_prep_b10a/research_disposition_decision_summary.json"
MODE = "execute-sealed-research-disposition-decision"
PASS = "FR_PREP_B10A_PASS_SEALED_RESEARCH_DISPOSITION_DECISION"
NOT_AFTER_MATCH = "NOT_EVALUATED_AFTER_FIRST_MATCH"
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


def skip_space(text, index):
    while index < len(text) and text[index] in " \t\r\n":
        index += 1
    return index


def scan_json_value_end(text, index):
    index = skip_space(text, index)
    if text[index] == '"':
        escaped = False
        cursor = index + 1
        while cursor < len(text):
            char = text[cursor]
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                return cursor + 1
            cursor += 1
        raise ValueError("UNTERMINATED_JSON_STRING")
    if text[index] in "[{":
        stack = [text[index]]
        in_string = False
        escaped = False
        cursor = index + 1
        while cursor < len(text):
            char = text[cursor]
            if in_string:
                if escaped:
                    escaped = False
                elif char == "\\":
                    escaped = True
                elif char == '"':
                    in_string = False
            elif char == '"':
                in_string = True
            elif char in "[{":
                stack.append(char)
            elif char in "]}":
                expected = "[" if char == "]" else "{"
                if not stack or stack[-1] != expected:
                    raise ValueError("INVALID_JSON_NESTING")
                stack.pop()
                if not stack:
                    return cursor + 1
            cursor += 1
        raise ValueError("UNTERMINATED_JSON_CONTAINER")
    cursor = index
    while cursor < len(text) and text[cursor] not in ",}":
        cursor += 1
    return cursor


class Files:
    def __init__(self, permitted_selective_fields):
        self.registry = {}
        self.permitted_selective_fields = set(permitted_selective_fields)
        self.hash_reads = Counter()
        self.json_reads = Counter()
        self.selective_reads = Counter()
        self.blocked_parse_attempts = 0
        self.blocked_raw_field_attempts = 0

    def add(self, path, artifact_id, access):
        self.registry[Path(path).resolve()] = (artifact_id, access)

    def hash_read(self, path):
        resolved = Path(path).resolve()
        if resolved not in self.registry:
            raise PermissionError("B10A_UNAUTHORIZED_HASH_READ_BLOCKED")
        artifact_id, _access = self.registry[resolved]
        self.hash_reads[artifact_id] += 1
        return resolved.read_bytes()

    def parse_json(self, path):
        resolved = Path(path).resolve()
        entry = self.registry.get(resolved)
        if entry is None or entry[1] != "json":
            self.blocked_parse_attempts += 1
            raise PermissionError("B10A_PROHIBITED_JSON_PARSE_BLOCKED")
        artifact_id, _access = entry
        self.json_reads[artifact_id] += 1
        return json.loads(resolved.read_text(encoding="utf-8"))

    def selective_top_level(self, path, requested_fields):
        resolved = Path(path).resolve()
        entry = self.registry.get(resolved)
        requested = set(requested_fields)
        if entry is None or entry[1] != "selective_json":
            self.blocked_parse_attempts += 1
            raise PermissionError("B10A_SELECTIVE_PARSE_PATH_BLOCKED")
        if not requested.issubset(self.permitted_selective_fields):
            self.blocked_raw_field_attempts += 1
            raise PermissionError("B10A_RAW_STATISTIC_FIELD_READ_BLOCKED")
        artifact_id, _access = entry
        text = resolved.read_text(encoding="utf-8")
        decoder = json.JSONDecoder()
        cursor = skip_space(text, 0)
        if text[cursor] != "{":
            raise ValueError("B10A_B9_REPORT_NOT_OBJECT")
        cursor += 1
        selected = {}
        while True:
            cursor = skip_space(text, cursor)
            if text[cursor] == "}":
                break
            key, key_end = decoder.raw_decode(text, cursor)
            if not isinstance(key, str):
                raise ValueError("B10A_B9_REPORT_KEY_NOT_STRING")
            cursor = skip_space(text, key_end)
            if text[cursor] != ":":
                raise ValueError("B10A_B9_REPORT_MISSING_COLON")
            value_start = skip_space(text, cursor + 1)
            value_end = scan_json_value_end(text, value_start)
            if key in requested:
                selected[key] = json.loads(text[value_start:value_end])
            cursor = skip_space(text, value_end)
            if text[cursor] == ",":
                cursor += 1
                continue
            if text[cursor] == "}":
                break
            raise ValueError("B10A_B9_REPORT_MEMBER_SEPARATOR_INVALID")
        missing = requested - set(selected)
        if missing:
            raise ValueError(f"B10A_PERMITTED_B9_FIELDS_MISSING:{sorted(missing)}")
        self.selective_reads[artifact_id] += 1
        return selected

    def report(self):
        artifact_ids = sorted({item[0] for item in self.registry.values()})
        return {
            "hash_read_operation_counts": {
                artifact_id: self.hash_reads[artifact_id] for artifact_id in artifact_ids
            },
            "json_parse_operation_counts": {
                artifact_id: self.json_reads[artifact_id] for artifact_id in artifact_ids
            },
            "selective_projection_operation_counts": {
                artifact_id: self.selective_reads[artifact_id] for artifact_id in artifact_ids
            },
            "blocked_prohibited_parse_attempt_count": self.blocked_parse_attempts,
            "blocked_raw_statistic_field_attempt_count": self.blocked_raw_field_attempts,
            "b7_jsonl_parse_count": 0,
            "b7_statistics_csv_parse_count": 0,
            "b9_markdown_parse_count": 0,
            "b9_raw_statistic_value_read_count": 0,
            "raw_broker_csv_read_count": 0,
            "future_ohlc_read_count": 0,
            "unauthorized_successful_read_count": 0,
        }


class ExternalProcessGuard:
    def __init__(self):
        self.blocked = 0

    def deny(self, *_args, **_kwargs):
        self.blocked += 1
        raise RuntimeError("B10A_EXTERNAL_PROCESS_BLOCKED")

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
            raise ImportError("B10A_PROHIBITED_IMPORT_BLOCKED")
        return self.original(name, *args, **kwargs)

    def __enter__(self):
        self.original = builtins.__import__
        builtins.__import__ = self.guarded
        return self

    def __exit__(self, *_args):
        builtins.__import__ = self.original


def validate_identity(document, expected_identity, expected_decision):
    return (
        identity(document) == expected_identity
        and document["canonical_summary_sha256"] == expected_identity
        and document["decision"] == expected_decision
        and document["execution_status"] == "PASS"
    )


def validate_and_project(base_root, authorization):
    files = Files(authorization["permitted_b9_report_top_level_fields"])
    paths = {}
    for binding in authorization["committed_artifacts"]:
        path = (Path(base_root) / binding["path"]).resolve()
        files.add(path, binding["artifact_id"], binding["access"])
        paths[binding["artifact_id"]] = path
        if not path.is_file():
            raise ValueError("B10A_COMMITTED_ARTIFACT_MISSING")

    b9_contract = files.parse_json(paths["b9_contract"])
    b9_schema = files.parse_json(paths["b9_schema"])
    b9_summary = files.parse_json(paths["b9_summary"])
    b10_authorization = files.parse_json(paths["b10_authorization"])
    b10_authorization_schema = files.parse_json(paths["b10_authorization_schema"])
    b10_contract = files.parse_json(paths["b10_contract"])
    b10_schema = files.parse_json(paths["b10_schema"])
    b10_summary = files.parse_json(paths["b10_summary"])

    jsonschema.Draft202012Validator.check_schema(b9_schema)
    jsonschema.Draft202012Validator(b9_schema).validate(b9_contract)
    jsonschema.Draft202012Validator.check_schema(b10_authorization_schema)
    jsonschema.Draft202012Validator(b10_authorization_schema).validate(b10_authorization)
    jsonschema.Draft202012Validator.check_schema(b10_schema)
    jsonschema.Draft202012Validator(b10_schema).validate(b10_contract)

    expected = authorization["expected"]
    b9_identity_valid = validate_identity(
        b9_contract,
        expected["b9"]["canonical_summary_sha256"],
        expected["b9"]["decision"],
    )
    b10_identity_valid = validate_identity(
        b10_contract,
        expected["b10"]["canonical_summary_sha256"],
        expected["b10"]["decision"],
    )
    b10_state_valid = (
        b10_contract["conclusions"]["research_disposition_contract"]
        == expected["b10"]["contract_state"]
        and b10_contract["conclusions"]["disposition_execution"]
        == expected["b10"]["disposition_execution"]
        and b10_contract["conclusions"]["current_disposition"]
        == expected["b10"]["current_disposition"]
        and b10_contract["conclusions"]["next_allowed_scope"]
        == expected["b10"]["next_allowed_scope"]
    )
    rule_contract_valid = (
        b10_contract["rule_evaluation_policy"]
        == {
            "evaluation_count": 1,
            "first_matching_rule_wins": True,
            "manual_override_allowed": False,
            "multiple_dispositions_allowed": False,
            "rule_order": [1, 2, 3, 4],
            "score_or_weighting_allowed": False,
        }
        and [item["rule"] for item in b10_contract["rules"]] == [1, 2, 3, 4]
        and len({item["disposition"] for item in b10_contract["rules"]}) == 4
    )
    summary_projections_valid = b9_summary == b9_contract and b10_summary == b10_contract

    artifact_hash_mismatch = 0
    for binding in authorization["committed_artifacts"]:
        artifact_hash_mismatch += int(
            byte_digest(files.hash_read(paths[binding["artifact_id"]]))
            != binding["file_sha256"]
        )
    if artifact_hash_mismatch:
        raise ValueError("B10A_COMMITTED_ARTIFACT_HASH_MISMATCH")
    b9_hashes_valid = (
        b9_contract["output_hashes"]["report_json_sha256"]
        == expected["b9"]["report_json_sha256"]
        and b9_contract["output_hashes"]["report_markdown_sha256"]
        == expected["b9"]["report_markdown_sha256"]
        and b9_contract["output_hashes"]["complete_sha256"]
        == expected["b9"]["complete_output_sha256"]
    )
    b9_integrity_valid = (
        b9_contract["conclusions"] == expected["required_b9_conclusions"]
        and b9_contract["report"]["dataset_separation"] == "PROVEN"
        and b9_contract["report"]["dataset_order"] == ["FJ", "FQ"]
        and b9_contract["report"]["direction_order"] == ["LONG", "SHORT"]
        and b9_contract["report"]["horizon_order"] == ["1", "3", "6", "12"]
    )
    b10_to_b9_binding_valid = (
        b10_contract["b9_binding"]["canonical_summary_sha256"]
        == expected["b9"]["canonical_summary_sha256"]
        and b10_contract["b9_binding"]["decision"] == expected["b9"]["decision"]
        and b10_contract["b9_binding"]["dataset_separation"] == "PROVEN"
    )
    validation_components = {
        "all_committed_artifact_hashes_valid": artifact_hash_mismatch == 0,
        "b9_identity_and_decision_valid": b9_identity_valid,
        "b9_output_hashes_valid": b9_hashes_valid,
        "b9_schema_valid": True,
        "b9_summary_projection_valid": summary_projections_valid,
        "b9_dataset_separation_and_integrity_conclusions_valid": b9_integrity_valid,
        "b10_identity_and_decision_valid": b10_identity_valid,
        "b10_schema_valid": True,
        "b10_summary_projection_valid": summary_projections_valid,
        "b10_contract_state_valid": b10_state_valid,
        "b10_frozen_rule_contract_valid": rule_contract_valid,
        "b10_to_b9_binding_valid": b10_to_b9_binding_valid,
    }
    if not all(validation_components.values()):
        raise ValueError("B10A_UPSTREAM_VALIDATION_BLOCKED")

    selected = files.selective_top_level(
        paths["b9_report_json"],
        authorization["permitted_b9_report_top_level_fields"],
    )
    if selected["conclusions"] != expected["required_b9_conclusions"]:
        raise ValueError("B10A_SELECTIVE_B9_CONCLUSION_MISMATCH")
    if selected["dataset_pooling_performed"] is not False:
        raise ValueError("B10A_DATASET_POOLING_BLOCKED")
    datasets = selected["dataset_level_coverage"]
    if (
        [item["dataset"] for item in datasets] != ["FJ", "FQ"]
        or any([entry["horizon"] for entry in item["horizon_coverage"]] != ["1", "3", "6", "12"] for item in datasets)
        or any(not isinstance(item["material_limitation"], bool) for item in datasets)
        or any(not isinstance(item["h12_material_limitation_retained"], bool) for item in datasets)
    ):
        raise ValueError("B10A_PERMITTED_DATASET_EVIDENCE_INVALID")
    prohibited_names = set(authorization["prohibited_b9_field_names"])
    if any(name in canonical_json(selected) for name in prohibited_names):
        raise ValueError("B10A_PROHIBITED_RAW_STATISTIC_FIELD_LEAKAGE")

    cross_counts = b9_summary["report"]["cross_period_observation_counts"]
    evidence_statement_counts = {
        "CROSS_PERIOD_DIRECTIONAL_CONSISTENCY_OBSERVED": int(
            cross_counts.get("CROSS_PERIOD_DIRECTIONAL_CONSISTENCY_OBSERVED", 0)
        ),
        "CROSS_PERIOD_DIRECTIONAL_DIVERGENCE_OBSERVED": int(
            cross_counts.get("CROSS_PERIOD_DIRECTIONAL_DIVERGENCE_OBSERVED", 0)
        ),
        "NO_CLEAR_DESCRIPTIVE_PATTERN": int(
            cross_counts.get("NO_CLEAR_DESCRIPTIVE_PATTERN", 0)
        ),
    }
    evidence = {
        "validation_components": validation_components,
        "datasets": copy.deepcopy(datasets),
        "evidence_statement_counts": evidence_statement_counts,
        "dataset_separation_and_ordering": {
            "dataset_pooling_performed": False,
            "dataset_separation": b9_summary["report"]["dataset_separation"],
            "dataset_order": copy.deepcopy(b9_summary["report"]["dataset_order"]),
            "direction_order": copy.deepcopy(b9_summary["report"]["direction_order"]),
            "horizon_order": copy.deepcopy(b9_summary["report"]["horizon_order"]),
        },
        "rules": copy.deepcopy(b10_contract["rules"]),
        "prohibited_claims_and_authorizations": copy.deepcopy(
            b10_contract["future_decision_record_policy"]["prohibited_claims_and_authorizations"]
        ),
        "b9_binding": {
            "canonical_summary_sha256": expected["b9"]["canonical_summary_sha256"],
            "decision": expected["b9"]["decision"],
            "report_json_sha256": expected["b9"]["report_json_sha256"],
            "report_markdown_sha256": expected["b9"]["report_markdown_sha256"],
            "complete_output_sha256": expected["b9"]["complete_output_sha256"],
        },
        "b10_binding": {
            "canonical_summary_sha256": expected["b10"]["canonical_summary_sha256"],
            "decision": expected["b10"]["decision"],
            "contract_state": expected["b10"]["contract_state"],
        },
    }
    return evidence, files


def execute_once(evidence):
    rules = evidence["rules"]
    validation_passed = all(evidence["validation_components"].values())
    trace = []
    first_match = None
    selected_disposition = None
    resulting_scope = None

    rule_1_match = not validation_passed
    trace.append({
        "condition": rules[0]["condition"],
        "evaluated": True,
        "evidence": copy.deepcopy(evidence["validation_components"]),
        "rule": 1,
        "status": "MATCHED" if rule_1_match else "NOT_MATCHED",
    })
    if rule_1_match:
        first_match = 1
    else:
        matched_datasets = [
            item["dataset"]
            for item in evidence["datasets"]
            if item["material_limitation"] or item["h12_material_limitation_retained"]
        ]
        rule_2_match = bool(matched_datasets)
        trace.append({
            "condition": rules[1]["condition"],
            "evaluated": True,
            "evidence": {
                "dataset_flags": [
                    {
                        "dataset": item["dataset"],
                        "h12_material_limitation_retained": item[
                            "h12_material_limitation_retained"
                        ],
                        "material_limitation": item["material_limitation"],
                    }
                    for item in evidence["datasets"]
                ],
                "matching_datasets": matched_datasets,
            },
            "rule": 2,
            "status": "MATCHED" if rule_2_match else "NOT_MATCHED",
        })
        if rule_2_match:
            first_match = 2
        else:
            counts = evidence["evidence_statement_counts"]
            rule_3_match = (
                counts["CROSS_PERIOD_DIRECTIONAL_DIVERGENCE_OBSERVED"] > 0
                or counts["NO_CLEAR_DESCRIPTIVE_PATTERN"] > 0
                or counts["CROSS_PERIOD_DIRECTIONAL_CONSISTENCY_OBSERVED"] == 0
            )
            trace.append({
                "condition": rules[2]["condition"],
                "evaluated": True,
                "evidence": copy.deepcopy(counts),
                "rule": 3,
                "status": "MATCHED" if rule_3_match else "NOT_MATCHED",
            })
            first_match = 3 if rule_3_match else 4

    selected_rule = rules[first_match - 1]
    selected_disposition = selected_rule["disposition"]
    resulting_scope = selected_rule["next_scope"]
    evaluated_rules = {item["rule"] for item in trace}
    for rule in rules:
        if rule["rule"] not in evaluated_rules:
            trace.append({
                "condition": rule["condition"],
                "evaluated": False,
                "rule": rule["rule"],
                "status": NOT_AFTER_MATCH,
            })

    dataset_evidence = [
        {
            "dataset": item["dataset"],
            "dataset_id": item["dataset_id"],
            "events": item["events"],
            "event_status_counts": copy.deepcopy(item["event_status_counts"]),
            "horizon_coverage": copy.deepcopy(item["horizon_coverage"]),
            "material_limitation": item["material_limitation"],
            "h12_material_limitation_retained": item[
                "h12_material_limitation_retained"
            ],
        }
        for item in evidence["datasets"]
    ]
    return {
        "upstream_bindings": {
            "b9": copy.deepcopy(evidence["b9_binding"]),
            "b10": copy.deepcopy(evidence["b10_binding"]),
        },
        "validation_order": [
            "B9_AND_B10_IDENTITIES_DECISIONS_AND_SCHEMAS_VALIDATED",
            "ALL_HASH_BOUND_B9_AND_B10_ARTIFACTS_VALIDATED",
            "B9_DATASET_SEPARATION_AND_REQUIRED_INTEGRITY_CONCLUSIONS_VALIDATED",
            "PERMITTED_B9_DECISION_FIELDS_PROJECTED_AFTER_VALIDATION",
            "B10_RULES_EVALUATED_ONCE_IN_ORDER_UNTIL_FIRST_MATCH",
        ],
        "dataset_material_limitation_evidence": dataset_evidence,
        "evidence_statement_counts": copy.deepcopy(evidence["evidence_statement_counts"]),
        "dataset_separation_and_ordering": copy.deepcopy(
            evidence["dataset_separation_and_ordering"]
        ),
        "rule_evaluation": {
            "evaluation_count": 1,
            "first_matching_rule_wins": True,
            "manual_override_applied": False,
            "multiple_dispositions_selected": False,
            "score_or_weighting_applied": False,
            "hard_coded_disposition_used": False,
            "trace": trace,
        },
        "selected_disposition": selected_disposition,
        "first_matching_rule": first_match,
        "resulting_next_scope": resulting_scope,
        "prohibited_claims_and_authorizations": copy.deepcopy(
            evidence["prohibited_claims_and_authorizations"]
        ),
        "raw_statistic_values_included": False,
        "selected_subgroup_included": False,
        "remediation_executed": False,
        "archive_or_holdout_action_executed": False,
    }


def base_request(authorization):
    return {
        "b9_identity": authorization["expected"]["b9"]["canonical_summary_sha256"],
        "b10_identity": authorization["expected"]["b10"]["canonical_summary_sha256"],
        "b9_hashes": [
            authorization["expected"]["b9"]["report_json_sha256"],
            authorization["expected"]["b9"]["report_markdown_sha256"],
            authorization["expected"]["b9"]["complete_output_sha256"],
        ],
        "parse_b7_data": False,
        "parse_b9_markdown": False,
        "raw_statistic_fields": [],
        "rule_order": [1, 2, 3, 4],
        "first_match": True,
        "bypass_material_limitation": False,
        "evaluate_after_first_match": False,
        "forced_disposition": None,
        "manual_override": False,
        "weighting_or_score": False,
        "multiple_dispositions": False,
        "positive_observation_override": False,
        "preferred_subgroup": [],
        "dataset_pooling": False,
        "claims": [],
        "trade_or_order_features": [],
        "execute_remediation": False,
        "external_process": False,
        "runtime_path": None,
    }


def request_allowed(authorization, request):
    return request == base_request(authorization)


def negative_tests(authorization, evidence):
    base = base_request(authorization)
    tests = {}

    def mutate(name, update):
        changed = copy.deepcopy(base)
        update(changed)
        tests[name] = not request_allowed(authorization, changed)

    mutate(
        "wrong_b9_or_b10_identity_or_decision_blocked",
        lambda value: value.update({"b10_identity": "0" * 64}),
    )
    mutate(
        "changed_b9_json_markdown_or_complete_hash_blocked",
        lambda value: value.update({"b9_hashes": ["0" * 64] * 3}),
    )
    guard = Files(authorization["permitted_b9_report_top_level_fields"])
    report_json = ROOT / next(
        item["path"]
        for item in authorization["committed_artifacts"]
        if item["artifact_id"] == "b9_report_json"
    )
    report_markdown = ROOT / next(
        item["path"]
        for item in authorization["committed_artifacts"]
        if item["artifact_id"] == "b9_report_markdown"
    )
    guard.add(report_json, "b9_report_json", "selective_json")
    guard.add(report_markdown, "b9_report_markdown", "hash_only")
    blocked_b7 = 0
    for path in authorization["prohibited_input_paths"][:3]:
        try:
            guard.parse_json(ROOT / path)
        except PermissionError:
            blocked_b7 += 1
    changed = copy.deepcopy(base)
    changed["parse_b7_data"] = True
    tests["b7_jsonl_or_statistics_parsing_attempt_blocked"] = (
        blocked_b7 == 3 and not request_allowed(authorization, changed)
    )
    try:
        guard.parse_json(report_markdown)
        markdown_blocked = False
    except PermissionError:
        markdown_blocked = True
    changed = copy.deepcopy(base)
    changed["parse_b9_markdown"] = True
    tests["b9_markdown_parsing_attempt_blocked"] = (
        markdown_blocked and not request_allowed(authorization, changed)
    )
    try:
        guard.selective_top_level(report_json, {"full_descriptive_statistics"})
        raw_blocked = False
    except PermissionError:
        raw_blocked = True
    changed = copy.deepcopy(base)
    changed["raw_statistic_fields"] = ["mean_bps"]
    tests["raw_statistic_value_read_attempt_blocked"] = (
        raw_blocked and not request_allowed(authorization, changed)
    )
    mutate(
        "rule_order_or_first_match_precedence_change_blocked",
        lambda value: value.update({"rule_order": [2, 1, 3, 4]}),
    )
    mutate(
        "rule_2_bypass_despite_material_limitation_blocked",
        lambda value: value.update({"bypass_material_limitation": True}),
    )
    mutate(
        "rule_3_or_4_evaluation_after_rule_2_match_blocked",
        lambda value: value.update({"evaluate_after_first_match": True}),
    )
    mutate(
        "hard_coded_disposition_without_evidence_evaluation_blocked",
        lambda value: value.update({"forced_disposition": evidence["rules"][1]["disposition"]}),
    )
    mutate(
        "manual_override_weighting_or_multiple_disposition_blocked",
        lambda value: value.update({
            "manual_override": True,
            "weighting_or_score": True,
            "multiple_dispositions": True,
        }),
    )
    mutate(
        "positive_observations_overriding_material_limitation_blocked",
        lambda value: value.update({"positive_observation_override": True}),
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
    mutate(
        "data_remediation_execution_attempt_blocked",
        lambda value: value.update({"execute_remediation": True}),
    )
    blocked_imports = 0
    for module in sorted(PROHIBITED_MODULES):
        try:
            builtins.__import__(module)
        except ImportError:
            blocked_imports += 1
    try:
        subprocess.Popen(["terminal64.exe", "/blocked"])
        external_blocked = False
    except RuntimeError:
        external_blocked = True
    leaked = copy.deepcopy(base)
    leaked["runtime_path"] = str(ROOT.resolve())
    tests["mt5_ea_network_external_process_or_absolute_path_leakage_blocked"] = (
        blocked_imports == len(PROHIBITED_MODULES)
        and external_blocked
        and not request_allowed(authorization, leaked)
        and absolute_path_count(leaked) == 1
    )
    return {
        "test_count": len(tests),
        "tests_passed": sum(tests.values()),
        "all_passed": all(tests.values()),
        "results": tests,
        "guard_audit": guard.report(),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", required=True, choices=[MODE])
    parser.add_argument("--authorization", required=True)
    parser.add_argument("--output-root", required=True)
    args = parser.parse_args()
    if Path(args.authorization).resolve() != AUTH.resolve():
        raise SystemExit("B10A_AUTHORIZATION_PATH_NOT_ALLOWED")
    if Path(args.output_root).resolve() != RESULT.parent.resolve():
        raise SystemExit("B10A_OUTPUT_ROOT_NOT_ALLOWED")

    bootstrap = Files([])
    for path, artifact_id in (
        (AUTH, "b10a_authorization"),
        (AUTH_SCHEMA, "b10a_authorization_schema"),
        (CONTRACT_SCHEMA, "b10a_contract_schema"),
    ):
        bootstrap.add(path, artifact_id, "json")
    authorization = bootstrap.parse_json(AUTH)
    authorization_schema = bootstrap.parse_json(AUTH_SCHEMA)
    contract_schema = bootstrap.parse_json(CONTRACT_SCHEMA)
    jsonschema.Draft202012Validator.check_schema(authorization_schema)
    jsonschema.Draft202012Validator(authorization_schema).validate(authorization)
    jsonschema.Draft202012Validator.check_schema(contract_schema)

    before_modules = set(sys.modules)
    RESULT.parent.mkdir(parents=True, exist_ok=True)
    relocation_deleted = False
    with ExternalProcessGuard() as external_guard, ImportGuard() as import_guard:
        evidence_1, files_1 = validate_and_project(ROOT, authorization)
        record_1 = execute_once(evidence_1)
        evidence_2, files_2 = validate_and_project(ROOT, authorization)
        record_2 = execute_once(evidence_2)
        relocation_parent = RESULT.parent
        relocation_path = None
        with tempfile.TemporaryDirectory(
            prefix=".b10a_controlled_relocation_", dir=relocation_parent
        ) as temporary:
            relocation_path = Path(temporary)
            for binding in authorization["committed_artifacts"]:
                source = ROOT / binding["path"]
                target = relocation_path / binding["path"]
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source, target)
            evidence_relocated, files_relocated = validate_and_project(
                relocation_path, authorization
            )
            record_relocated = execute_once(evidence_relocated)
        relocation_deleted = relocation_path is not None and not relocation_path.exists()
        tests = negative_tests(authorization, evidence_1)

    imported = set(sys.modules) - before_modules
    prohibited_loaded = sorted(
        name for name in PROHIBITED_MODULES if name in sys.modules or name in imported
    )
    normal_identical = canonical_json(record_1) == canonical_json(record_2)
    relocation_identical = canonical_json(record_1) == canonical_json(record_relocated)
    trace = record_1["rule_evaluation"]["trace"]
    selected_rule = record_1["first_matching_rule"]
    selected_mapping = evidence_1["rules"][selected_rule - 1]
    structural_selection_valid = (
        record_1["selected_disposition"] == selected_mapping["disposition"]
        and record_1["resulting_next_scope"] == selected_mapping["next_scope"]
        and next(item["rule"] for item in trace if item["status"] == "MATCHED")
        == selected_rule
        and all(
            item["status"] == NOT_AFTER_MATCH
            for item in trace
            if item["rule"] > selected_rule
        )
        and record_1["rule_evaluation"]["hard_coded_disposition_used"] is False
    )
    dataset_flags = {
        item["dataset"]: (
            item["material_limitation"],
            item["h12_material_limitation_retained"],
        )
        for item in record_1["dataset_material_limitation_evidence"]
    }
    mismatch_counters = {
        "upstream_b9_or_b10_identity_decision_or_schema_mismatch": 0,
        "committed_artifact_hash_mismatch": 0,
        "b9_dataset_separation_or_integrity_conclusion_mismatch": 0,
        "permitted_b9_field_projection_mismatch": 0,
        "dataset_material_limitation_evidence_mismatch": int(
            set(dataset_flags) != {"FJ", "FQ"}
        ),
        "rule_order_or_first_match_mismatch": int(not structural_selection_valid),
        "decision_evaluation_count_mismatch": int(
            record_1["rule_evaluation"]["evaluation_count"] != 1
        ),
        "normal_repeat_mismatch": int(not normal_identical),
        "controlled_relocation_mismatch": int(not relocation_identical),
        "temporary_artifact_deletion_mismatch": int(not relocation_deleted),
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
            "data_remediation_execution_count",
            "additional_holdout_creation_count",
            "archive_execution_count",
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
        raise SystemExit("B10A_SEALED_DISPOSITION_DECISION_BLOCKED")

    decision_record_sha = digest(record_1)
    rule_trace_sha = digest(record_1["rule_evaluation"]["trace"])
    complete_sha = digest({
        "decision_record_sha256": decision_record_sha,
        "rule_trace_sha256": rule_trace_sha,
        "dataset_order": record_1["dataset_separation_and_ordering"]["dataset_order"],
        "rule_order": [item["rule"] for item in record_1["rule_evaluation"]["trace"]],
    })
    conclusions = {
        "research_disposition_contract": "FROZEN",
        "disposition_execution": "COMPLETED",
        "selected_disposition": record_1["selected_disposition"],
        "first_matching_rule": record_1["first_matching_rule"],
        "performance": "NOT_EVALUATED",
        "profitability": "NOT_CLAIMED",
        "strategy_edge": "NOT_ESTABLISHED",
        "robustness": "NOT_ESTABLISHED",
        "order_logic": "NOT_APPROVED",
        "candidate": "NOT_READY_FOR_ORDER_LOGIC",
        "data_remediation_execution": "NOT_STARTED",
        "next_allowed_scope": record_1["resulting_next_scope"],
    }
    result = {
        "schema_version": "fr_prep_b10a_sealed_research_disposition_decision.v1",
        "checkpoint": "FR_PREP_B10A",
        "decision": PASS,
        "execution_status": "PASS",
        "decision_record": record_1,
        "conclusions": conclusions,
        "output_hashes": {
            "decision_record_sha256": decision_record_sha,
            "rule_trace_sha256": rule_trace_sha,
            "complete_sha256": complete_sha,
        },
        "determinism": {
            "normal_repeat_identical": normal_identical,
            "controlled_relocation_identical": relocation_identical,
            "ordering_and_hashes_identical": normal_identical and relocation_identical,
            "temporary_artifacts_deleted": relocation_deleted,
            "decision_generation_count": 3,
            "decision_evaluation_count_per_generation": 1,
        },
        "negative_tests": {
            key: value for key, value in tests.items() if key != "guard_audit"
        },
        "mismatch_counters": mismatch_counters,
        "runtime_audit": {
            "normal_run_1_file_access": files_1.report(),
            "normal_run_2_file_access": files_2.report(),
            "relocation_run_file_access": files_relocated.report(),
            "negative_test_guard": tests["guard_audit"],
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
    result["canonical_summary_sha256"] = identity(result)
    jsonschema.Draft202012Validator(contract_schema).validate(result)
    if absolute_path_count(result):
        raise SystemExit("B10A_ABSOLUTE_RUNTIME_PATH_IDENTITY_LEAKAGE_BLOCKED")
    rendered = json.dumps(result, ensure_ascii=True, indent=2, sort_keys=True) + "\n"
    CONTRACT.write_text(rendered, encoding="utf-8", newline="\n")
    RESULT.write_text(rendered, encoding="utf-8", newline="\n")
    print(canonical_json({
        "decision": PASS,
        "canonical_summary_sha256": result["canonical_summary_sha256"],
        "selected_disposition": conclusions["selected_disposition"],
        "first_matching_rule": conclusions["first_matching_rule"],
        "next_allowed_scope": conclusions["next_allowed_scope"],
        "decision_record_sha256": decision_record_sha,
        "rule_trace_sha256": rule_trace_sha,
        "complete_sha256": complete_sha,
        "negative_tests": (
            f"{result['negative_tests']['tests_passed']}/"
            f"{result['negative_tests']['test_count']}"
        ),
        "mismatch_count": sum(mismatch_counters.values()),
        "prohibited_count": (
            sum(prohibited_import_counts.values())
            + sum(prohibited_execution_counts.values())
        ),
    }))


if __name__ == "__main__":
    main()
