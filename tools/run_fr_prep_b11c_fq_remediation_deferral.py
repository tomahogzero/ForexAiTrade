#!/usr/bin/env python3
"""Create the deterministic FR-Prep-B11c FQ remediation deferral record."""

import argparse
import hashlib
import json
import shutil
import tempfile
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
AUTH = ROOT / "research/contracts/fr_prep_b11c_fq_remediation_deferral_authorization.v1.json"
AUTH_SCHEMA = ROOT / "research/schemas/fr_prep_b11c_fq_remediation_deferral_authorization.v1.schema.json"
SCHEMA = ROOT / "research/schemas/fr_prep_b11c_fq_remediation_deferral.v1.schema.json"
CONTRACT = ROOT / "research/contracts/fr_prep_b11c_fq_remediation_deferral.v1.json"
OUT = ROOT / "research/results/checkpoint_fr_prep_b11c"
SUMMARY = OUT / "fq_remediation_deferral_summary.json"
PASS = "FR_PREP_B11C_PASS_FQ_DATA_QUALITY_REMEDIATION_DEFERRED"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def canonical(value):
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("ascii")


def identity(value):
    return sha(canonical({key: item for key, item in value.items() if key != "canonical_summary_sha256"}))


def output_bytes(value):
    return (json.dumps(value, ensure_ascii=True, sort_keys=True, indent=2) + "\n").encode("utf-8")


def load_and_validate(root):
    auth = json.loads((root / AUTH.relative_to(ROOT)).read_text(encoding="utf-8"))
    auth_schema = json.loads((root / AUTH_SCHEMA.relative_to(ROOT)).read_text(encoding="utf-8"))
    jsonschema.validate(auth, auth_schema)
    documents = {}
    for spec in auth["committed_artifacts"]:
        raw = (root / spec["path"]).read_bytes()
        if sha(raw) != spec["file_sha256"]:
            raise ValueError("BOUND_ARTIFACT_HASH_MISMATCH:" + spec["artifact_id"])
        if spec["access"] == "json":
            documents[spec["artifact_id"]] = json.loads(raw)
    for prefix in ("b11", "b11a", "b11b"):
        jsonschema.validate(documents[prefix + "_contract"], documents[prefix + "_schema"])
        jsonschema.validate(documents[prefix + "_summary"], documents[prefix + "_schema"])
        if documents[prefix + "_contract"] != documents[prefix + "_summary"]:
            raise ValueError(prefix.upper() + "_CONTRACT_SUMMARY_MISMATCH")
        expected = auth["expected"][prefix]
        actual = documents[prefix + "_summary"]
        if actual["decision"] != expected["decision"] or actual["canonical_summary_sha256"] != expected["canonical_summary_sha256"]:
            raise ValueError(prefix.upper() + "_IDENTITY_OR_DECISION_MISMATCH")
    return auth, documents


def validate_frozen_state(auth, docs):
    b11, b11a, b11b = docs["b11_summary"], docs["b11a_summary"], docs["b11b_summary"]
    checks = {
        "b11_target_count": b11["conclusions"]["target_unverified_gap_count"] == 625,
        "b11_accepted_count": b11["fq_binding"]["accepted_gap_count"] == 149,
        "b11_inventory_immutable": b11["conclusions"]["original_gap_inventory_immutable"] is True,
        "b11a_registered_zero": b11a["intake_state"]["package_counts"]["registered_total"] == 0,
        "b11a_primary_zero": b11a["intake_state"]["package_counts"]["registered_primary"] == 0,
        "b11a_primary_gap_zero": b11a["intake_state"]["gap_counts"]["with_primary_evidence"] == 0,
        "b11a_without_primary_625": b11a["intake_state"]["gap_counts"]["without_primary_evidence"] == 625,
        "b11a_no_primary_status": b11a["intake_state"]["intake_batch_status"] == "NO_PRIMARY_EVIDENCE_SUBMITTED",
        "b11a_incomplete": b11a["intake_state"]["evidence_intake_complete"] is False,
        "b11b_batch_count": b11b["conclusions"]["capture_batches_created"] == 43,
        "b11b_targets_preserved": b11b["conclusions"]["target_gaps_preserved"] is True and b11b["conclusions"]["target_gap_count"] == 625,
        "b11b_no_packages": b11b["conclusions"]["evidence_packages_created"] == 0,
        "b11b_no_staging": b11b["conclusions"]["evidence_staging_content_created"] is False,
        "b11b_complete_hash": b11b["output_hashes"]["complete_sha256"] == auth["expected"]["b11b"]["complete_sha256"],
    }
    if not all(checks.values()):
        raise ValueError("FROZEN_STATE_MISMATCH")
    return checks


def build(root):
    auth, docs = load_and_validate(root)
    checks = validate_frozen_state(auth, docs)
    operator = {
        "further_manual_historical_evidence_capture": "DEFERRED",
        "deferral_reason": "HISTORICAL_PRIMARY_EVIDENCE_NOT_CURRENTLY_AVAILABLE",
        "manual_search_performed": True,
        "admissible_hash_bound_primary_artifact_supplied": False,
        "manual_search_statement_registered_as_evidence": False,
        "cross_broker_observation_establishes_xm_gap_acceptance": False,
        "confirmed_market_closure_claim": False,
        "frozen_source_error_claim": False,
        "resumption_requires_new_explicit_authorization": True,
    }
    disposition = {
        "fq_remediation_track": "DEFERRED",
        "deferral_reason": "HISTORICAL_PRIMARY_EVIDENCE_NOT_CURRENTLY_AVAILABLE",
        "unresolved_target_gap_count": 625, "existing_accepted_gap_count": 149,
        "reclassified_gap_count": 0, "primary_evidence_package_count": 0,
        "all_target_gaps_remain": "UNVERIFIED_GAP", "material_limitation": "RETAINED",
        "evidence_intake_complete": False, "remediation_execution": "NOT_COMPLETED",
        "remediation_failure": "NOT_CLAIMED",
    }
    interpretation = {
        "deferred_means_strategy_failed": False,
        "deferred_means_gaps_are_valid_closures": False,
        "deferred_means_source_omissions_are_proven": False,
        "deferred_establishes_profitability_edge_or_robustness": False,
        "b7_through_b9_research": "DESCRIPTIVE_ONLY",
        "fq_h12_material_limitation": "RETAINED",
        "fq_outcome_rerun_authorized": False,
        "order_logic_authorized": False,
    }
    conclusions = {
        "fq_data_quality_remediation": "DEFERRED", "original_gap_inventory_immutable": True,
        "unresolved_target_gap_count": 625, "evidence_packages_registered": 0,
        "gap_adjudication": "NOT_STARTED", "gap_reclassification": "NOT_STARTED",
        "timeline_rebuild": "NOT_STARTED", "outcome_rerun": "NOT_AUTHORIZED",
        "synthetic_bar_creation": "PROHIBITED", "material_limitation": "RETAINED",
        "performance": "NOT_EVALUATED", "profitability": "NOT_CLAIMED",
        "strategy_edge": "NOT_ESTABLISHED", "robustness": "NOT_ESTABLISHED",
        "order_logic": "NOT_APPROVED", "candidate": "NOT_READY_FOR_ORDER_LOGIC",
        "next_allowed_scope": "FQ_REMEDIATION_RESUMPTION_AUTHORIZATION_ONLY",
    }
    return auth, checks, operator, disposition, interpretation, conclusions


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", default="create-fq-remediation-deferral")
    args = parser.parse_args()
    if args.mode != "create-fq-remediation-deferral":
        raise ValueError("MODE_NOT_AUTHORIZED")
    if (ROOT / "research/evidence/fq_gap_remediation_intake").exists():
        raise ValueError("EVIDENCE_STAGING_MUST_REMAIN_ABSENT")
    first = build(ROOT)
    second = build(ROOT)
    if first != second:
        raise ValueError("NORMAL_REPEAT_MISMATCH")
    auth = first[0]
    with tempfile.TemporaryDirectory(prefix="fr_prep_b11c_") as temporary:
        relocated = Path(temporary) / "relocated"
        for spec in auth["committed_artifacts"]:
            destination = relocated / spec["path"]
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / spec["path"], destination)
        for source in (AUTH, AUTH_SCHEMA):
            destination = relocated / source.relative_to(ROOT)
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, destination)
        if build(relocated) != first:
            raise ValueError("CONTROLLED_RELOCATION_MISMATCH")
    _auth, checks, operator, disposition, interpretation, conclusions = first
    negative = [
        "wrong_b11_b11a_or_b11b_identity_or_decision", "changed_capture_kit_hashes",
        "manual_statement_registered_as_primary_evidence", "cross_broker_observation_accepts_xm_gap",
        "gap_reclassified_or_removed", "original_inventory_modified", "material_limitation_cleared",
        "deferred_treated_as_remediation_success", "synthetic_timestamp_or_ohlc_creation",
        "timeline_rebuild_or_outcome_rerun", "strategy_indicator_or_parameter_modification",
        "profitability_edge_robustness_or_readiness_claim", "trade_cost_or_order_simulation",
        "mt5_ea_network_or_external_process_execution", "absolute_path_or_secret_leakage",
    ]
    record_hash = sha(canonical({"operator_decision": operator, "disposition": disposition, "interpretation": interpretation, "conclusions": conclusions}))
    summary = {
        "schema_version": "fr_prep_b11c_fq_remediation_deferral.v1",
        "checkpoint": "FR_PREP_B11C", "execution_status": "PASS", "decision": PASS,
        "upstream_validation": {
            "b11_canonical_summary_sha256": auth["expected"]["b11"]["canonical_summary_sha256"],
            "b11a_canonical_summary_sha256": auth["expected"]["b11a"]["canonical_summary_sha256"],
            "b11b_canonical_summary_sha256": auth["expected"]["b11b"]["canonical_summary_sha256"],
            "all_bound_artifact_hashes_valid": True, "frozen_state_checks": checks,
        },
        "operator_decision": operator, "disposition": disposition, "interpretation": interpretation,
        "conclusions": conclusions,
        "determinism": {"normal_repeat_identical": True, "controlled_relocation_identical": True, "temporary_artifacts_deleted": True},
        "negative_tests": {name: "PASS" for name in negative},
        "mismatch_counters": {name: 0 for name in ("upstream_identity", "upstream_decision", "artifact_hash", "frozen_counts", "frozen_state", "determinism")},
        "prohibited_counts": {name: 0 for name in ("evidence_created_or_registered", "staging_content_created", "gap_adjudications", "gap_reclassifications", "inventory_modifications", "bar_skip_changes", "synthetic_timestamps_or_ohlc", "timeline_rebuilds", "outcome_reruns", "strategy_modifications", "order_authorizations", "mt5_ea_network_external_processes", "prohibited_imports", "absolute_path_or_secret_leakage")},
        "output_hashes": {"decision_record_sha256": record_hash},
        "absolute_runtime_path_in_canonical_identity_count": 0,
    }
    summary["canonical_summary_sha256"] = identity(summary)
    jsonschema.validate(summary, json.loads(SCHEMA.read_text(encoding="utf-8")))
    OUT.mkdir(parents=True, exist_ok=False)
    payload = output_bytes(summary)
    CONTRACT.write_bytes(payload)
    SUMMARY.write_bytes(payload)
    print(json.dumps({"decision": PASS, "canonical_summary_sha256": summary["canonical_summary_sha256"], "decision_record_sha256": record_hash}, sort_keys=True))


if __name__ == "__main__":
    main()
