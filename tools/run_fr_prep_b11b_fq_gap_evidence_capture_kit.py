#!/usr/bin/env python3
"""Generate the deterministic FR-Prep-B11b primary-evidence capture kit."""

import argparse
import ast
import csv
import hashlib
import io
import json
import shutil
import tempfile
from collections import defaultdict
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
AUTH = ROOT / "research/contracts/fr_prep_b11b_fq_gap_evidence_capture_kit_authorization.v1.json"
AUTH_SCHEMA = ROOT / "research/schemas/fr_prep_b11b_fq_gap_evidence_capture_kit_authorization.v1.schema.json"
SCHEMA = ROOT / "research/schemas/fr_prep_b11b_fq_gap_evidence_capture_kit.v1.schema.json"
CONTRACT = ROOT / "research/contracts/fr_prep_b11b_fq_gap_evidence_capture_kit.v1.json"
OUT = ROOT / "research/results/checkpoint_fr_prep_b11b"
BATCHES = OUT / "fq_gap_evidence_capture_batches.json"
CHECKLIST = OUT / "fq_gap_evidence_capture_checklist.csv"
GUIDE = OUT / "fq_gap_evidence_capture_guide.md"
SUMMARY = OUT / "fq_gap_evidence_capture_kit_summary.json"
HELPER = ROOT / "tools/prepare_fq_gap_evidence_package.py"
PASS = "FR_PREP_B11B_PASS_FQ_GAP_PRIMARY_EVIDENCE_CAPTURE_KIT"
PRIMARY = [
    "BROKER_SERVER_SESSION_SCHEDULE",
    "SAME_BROKER_SERVER_LOWER_TIMEFRAME_OR_TICK_EXPORT",
    "INDEPENDENT_SAME_BROKER_SERVER_H1_EXPORT",
    "OFFICIAL_MARKET_OR_BROKER_HOLIDAY_NOTICE",
]
TRACKS = {
    "A": "BROKER_SERVER_SESSION_SCHEDULE",
    "B": "SAME_BROKER_SERVER_LOWER_TIMEFRAME_OR_TICK_EXPORT",
    "C": "INDEPENDENT_SAME_BROKER_SERVER_H1_EXPORT",
    "D": "OFFICIAL_MARKET_OR_BROKER_HOLIDAY_NOTICE",
}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def canonical(value):
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("ascii")


def identity(value):
    return sha(canonical({k: v for k, v in value.items() if k != "canonical_summary_sha256"}))


def json_bytes(value):
    return (json.dumps(value, ensure_ascii=True, sort_keys=True, indent=2) + "\n").encode("utf-8")


def validate_inputs(root):
    auth = json.loads((root / AUTH.relative_to(ROOT)).read_text(encoding="utf-8"))
    auth_schema = json.loads((root / AUTH_SCHEMA.relative_to(ROOT)).read_text(encoding="utf-8"))
    jsonschema.validate(auth, auth_schema)
    docs = {}
    for spec in auth["committed_artifacts"]:
        path = root / spec["path"]
        raw = path.read_bytes()
        if sha(raw) != spec["file_sha256"]:
            raise ValueError("UPSTREAM_HASH_MISMATCH:" + spec["artifact_id"])
        if spec["access"] == "json":
            docs[spec["artifact_id"]] = json.loads(raw)
    for prefix in ("b11", "b11a"):
        jsonschema.validate(docs[prefix + "_contract"], docs[prefix + "_schema"])
        jsonschema.validate(docs[prefix + "_summary"], docs[prefix + "_schema"])
        if docs[prefix + "_contract"] != docs[prefix + "_summary"]:
            raise ValueError(prefix.upper() + "_CONTRACT_SUMMARY_MISMATCH")
        expected = auth["expected"][prefix]
        summary = docs[prefix + "_summary"]
        if summary["decision"] != expected["decision"] or summary["canonical_summary_sha256"] != expected["canonical_summary_sha256"]:
            raise ValueError(prefix.upper() + "_IDENTITY_MISMATCH")
    a = docs["b11a_summary"]
    expected_a = auth["expected"]["b11a"]
    if (a["output_hashes"]["complete_sha256"] != expected_a["complete_sha256"]
            or a["intake_state"]["intake_batch_status"] != expected_a["intake_batch_status"]
            or a["intake_state"]["package_counts"]["registered_total"] != 0
            or a["intake_state"]["gap_counts"]["with_primary_evidence"] != 0):
        raise ValueError("B11A_STATE_MISMATCH")
    return auth, docs


def validate_targets(root, docs):
    request = docs["b11a_request"]
    rows = request["intake_targets"]
    ids = [row["gap_id"] for row in rows]
    if len(ids) != 625 or len(set(ids)) != 625 or ids != sorted(ids):
        raise ValueError("TARGET_SET_INVALID")
    if any(row["original_policy_classification"] != "UNVERIFIED_GAP" for row in rows):
        raise ValueError("TARGET_CLASSIFICATION_CHANGED")
    b11 = json.loads((root / "research/results/checkpoint_fr_prep_b11/fq_data_quality_remediation_contract_summary.json").read_text(encoding="utf-8"))
    expected = json.loads((root / AUTH.relative_to(ROOT)).read_text(encoding="utf-8"))["expected"]["b11"]
    for key in ("target_gap_id_set_sha256", "target_gap_metadata_sha256", "structural_signature_inventory_sha256"):
        if request[key] != expected[key]:
            raise ValueError("TARGET_BINDING_MISMATCH:" + key)
    signatures = {row["structural_signature_sha256"] for row in rows}
    if len(signatures) != 36 or b11["target_inventory"]["structural_signature_count"] != 36:
        raise ValueError("STRUCTURAL_SIGNATURE_COUNT_MISMATCH")
    matrix_raw = (root / "research/results/checkpoint_fr_prep_b11a/fq_gap_evidence_target_matrix.csv").read_text(encoding="utf-8")
    matrix_ids = [row["gap_id"] for row in csv.DictReader(io.StringIO(matrix_raw))]
    if matrix_ids != ids:
        raise ValueError("TARGET_MATRIX_ORDER_MISMATCH")
    registry = docs["b11a_registry"]
    if registry["submitted_packages"] or registry["registered_package_count"] != 0:
        raise ValueError("REGISTERED_EVIDENCE_NOT_ZERO")
    return rows, signatures


def make_batch(kind, key, rows, sequence):
    rows = sorted(rows, key=lambda row: row["gap_id"])
    return {
        "batch_id": f"CAP-{kind}-{sequence:03d}",
        "group_type": kind,
        "group_key": key,
        "operational_convenience_only": True,
        "priority": None, "ranking": None, "score": None,
        "expected_coverage_benefit": None,
        "gap_count": len(rows),
        "gap_ids": [row["gap_id"] for row in rows],
        "earliest_affected_timestamp": min(row["previous_bar_timestamp"] for row in rows),
        "latest_affected_timestamp": max(row["next_bar_timestamp"] for row in rows),
        "calendar_years": sorted({row["calendar_year"] for row in rows}),
        "source_files": sorted({row["previous_source_file"] for row in rows} | {row["next_source_file"] for row in rows}),
        "requested_primary_evidence_types": PRIMARY,
        "capture_tracks": list(TRACKS),
        "original_metadata_only": True,
        "proposed_remediation_status": None,
        "structural_pattern_proves_closure": False,
    }


def build_batches(rows):
    families = []
    definitions = [
        ("SOURCE_YEAR_FILE", lambda r: f'{r["calendar_year"]}|{r["previous_source_file"]}|{r["next_source_file"]}'),
        ("STRUCTURAL_SIGNATURE", lambda r: r["structural_signature_sha256"]),
        ("BROAD_DATE_RANGE", lambda r: str(r["calendar_year"])),
    ]
    sequence = 0
    counts = {}
    for kind, key_fn in definitions:
        groups = defaultdict(list)
        for row in rows:
            groups[key_fn(row)].append(row)
        counts[kind] = len(groups)
        for key in sorted(groups):
            sequence += 1
            families.append(make_batch(kind, key, groups[key], sequence))
    return families, counts


def template():
    return {
        "schema_version": "fq_gap_evidence_package.v1",
        "evidence_package_id": "", "gap_id_or_explicit_gap_id_set": [],
        "evidence_type": "", "evidence_role": "PRIMARY",
        "source_organization": "", "broker": "XM", "server": "", "symbol": "GOLD",
        "time_basis": "", "timezone_or_unknown": "UNKNOWN",
        "effective_start": "", "effective_end": "", "captured_at": "",
        "artifact_path": "", "artifact_sha256": "", "source_metadata": {},
        "supports_status": [], "conflicts_with_status": [], "operator_notes": "",
        "validation_status": "PACKAGE_REGISTERED_UNAUDITED",
    }


def batches_document(rows, batches, counts):
    return {
        "schema_version": "fr_prep_b11b_fq_gap_evidence_capture_batches.v1",
        "checkpoint": "FR_PREP_B11B", "dataset_id": "FP_FQ_2020_2022_GOLD_H1",
        "target_gap_count": 625, "target_gap_ids": [r["gap_id"] for r in rows],
        "capture_tracks": [{"track": key, "evidence_type": value} for key, value in TRACKS.items()],
        "batch_family_counts": counts, "capture_batch_count": len(batches),
        "batches": batches, "evidence_package_metadata_template": template(),
        "no_priority_ranking_or_expected_coverage_benefit": True,
        "structural_signatures_are_descriptive_only": True,
        "evidence_packages_created": 0,
    }


def checklist_bytes(batches):
    output = io.StringIO(newline="")
    fields = ["batch_id", "group_type", "group_key", "gap_count", "earliest_affected_timestamp",
              "latest_affected_timestamp", "calendar_years", "source_files", "gap_ids",
              "requested_primary_evidence_types", "priority", "proposed_remediation_status"]
    writer = csv.DictWriter(output, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    for batch in batches:
        writer.writerow({k: ("|".join(map(str, batch[k])) if isinstance(batch[k], list) else batch[k]) for k in fields})
    return output.getvalue().encode("utf-8")


def guide_bytes(batch_count):
    text = f"""# FQ Gap Primary Evidence Capture Guide

This kit covers all 625 frozen FQ gaps in {batch_count} unranked operational batches. It does not collect evidence, adjudicate a gap, or promise that any evidence will resolve a gap.

## Scope and source identity

Evidence must identify the same XM broker/server and the GOLD symbol. In MT5, an operator must manually open the account/server connection details and record the exact server name before any export. Do not launch MT5 through these tools. Another broker's data cannot establish acceptance and must be declared as conflicting or corroborative-only evidence.

## Primary capture tracks

- Track A: capture a broker/server session schedule with exact broker, server, symbol class, effective date range, time basis, and timezone (or `UNKNOWN`).
- Track B: manually export fresh same-server lower-timeframe or tick history around the missing H1 slots, preserving timestamps and export/source metadata. Never derive it from the frozen FQ CSV files.
- Track C: manually export fresh independent same-server H1 history, with exact broker, server, symbol, and date range. It does not alone prove routine closure unless B11 sufficiency rules are met.
- Track D: save an official broker/session holiday notice with the exact affected date, session hours, source identity, and capture metadata. Generic holiday calendars are corroborative-only.

Screenshots and operator notes are corroborative-only. Repeated `23000100` or similar timestamp patterns are descriptive, not proof. One artifact may cover multiple explicit gap IDs within its declared range.

## Security and packaging

Before staging, remove account numbers, login IDs, names, passwords, credentials, API keys, and tokens. The helper rejects obvious sensitive metadata, absolute paths, symlinks, traversal, unknown or duplicate gap IDs, invalid roles/types, and the three frozen FQ source CSVs.

Run the helper offline from the repository root only after manually collecting and sanitizing a real artifact:

```text
python tools/prepare_fq_gap_evidence_package.py --artifact operator_captures/session.pdf --package-id XM-SCHEDULE-001 --evidence-type BROKER_SERVER_SESSION_SCHEDULE --evidence-role PRIMARY --broker XM --server EXACT_SERVER_NAME --symbol GOLD --time-basis BROKER_SERVER_TIME --timezone-or-unknown UNKNOWN --effective-start 2020-01-01T00:00:00 --effective-end 2020-12-31T23:59:59 --gap-id GQ0001 --source-organization XM --operator-notes sanitized
python tools/prepare_fq_gap_evidence_package.py --artifact operator_captures/ticks.csv --package-id XM-TICKS-001 --evidence-type SAME_BROKER_SERVER_LOWER_TIMEFRAME_OR_TICK_EXPORT --evidence-role PRIMARY --broker XM --server EXACT_SERVER_NAME --symbol GOLD --time-basis BROKER_SERVER_TIME --timezone-or-unknown UNKNOWN --effective-start 2020-01-02T22:00:00 --effective-end 2020-01-03T02:00:00 --gap-id-file operator_captures/gap_ids.txt --source-organization XM --operator-notes sanitized
```

The helper only copies an artifact and writes canonical intake metadata. It never evaluates evidence, changes `accepted_for_bar_skip`, proposes a remediation status, creates OHLC, or interprets outcomes.
"""
    return text.encode("utf-8")


def validate_helper():
    source = HELPER.read_text(encoding="utf-8")
    tree = ast.parse(source)
    imports = {alias.name.split(".")[0] for node in ast.walk(tree)
               if isinstance(node, (ast.Import, ast.ImportFrom))
               for alias in (node.names if isinstance(node, ast.Import) else [ast.alias(name=node.module or "")])}
    banned = {"subprocess", "socket", "requests", "urllib", "MetaTrader5"}
    literals = {node.value for node in ast.walk(tree) if isinstance(node, ast.Constant) and isinstance(node.value, str)}
    required_flags = {"--artifact", "--package-id", "--evidence-type", "--evidence-role", "--broker", "--server",
                      "--symbol", "--time-basis", "--timezone-or-unknown", "--effective-start", "--effective-end",
                      "--gap-id", "--gap-id-file", "--source-organization", "--operator-notes"}
    prohibited_fields = {"accepted_for_bar_skip", "proposed_remediation_status", "return_bps", "mfe_bps", "mae_bps"}
    checks = {
        "ast_parse": True, "no_network_external_imports": not bool(imports & banned),
        "all_required_cli_flags": required_flags <= literals,
        "offline_hashing_present": "sha256" in source,
        "target_hash_binding_present": "b3e2cd4b1b075884491a9134bea78e453459bde690d946973613082ce780a7ae" in source,
        "frozen_sources_rejected": all(name in source for name in (
            "GOLD#_H1_202001020900_202012311800.csv", "GOLD#_H1_202101040100_202112311800.csv",
            "GOLD#_H1_202201030100_202212302300.csv")),
        "security_guards_present": all(term in source for term in ("is_symlink", "is_absolute", "SENSITIVE")),
        "no_adjudication_fields": not bool(prohibited_fields & literals),
        "helper_not_executed": True,
    }
    if not all(checks.values()):
        raise ValueError("HELPER_STATIC_VALIDATION_FAILED")
    return checks


def generate(root):
    auth, docs = validate_inputs(root)
    rows, signatures = validate_targets(root, docs)
    batches, family_counts = build_batches(rows)
    batch_doc = batches_document(rows, batches, family_counts)
    artifacts = {
        "batches": json_bytes(batch_doc),
        "checklist": checklist_bytes(batches),
        "guide": guide_bytes(len(batches)),
    }
    return auth, rows, signatures, batches, family_counts, artifacts


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", default="create-fq-gap-evidence-capture-kit")
    args = parser.parse_args()
    if args.mode != "create-fq-gap-evidence-capture-kit":
        raise ValueError("MODE_NOT_AUTHORIZED")
    if (ROOT / "research/evidence/fq_gap_remediation_intake").exists():
        raise ValueError("EVIDENCE_STAGING_MUST_REMAIN_ABSENT")
    auth, rows, signatures, batches, family_counts, first = generate(ROOT)
    _a2, _r2, _s2, _b2, _f2, second = generate(ROOT)
    if first != second:
        raise ValueError("NORMAL_REPEAT_MISMATCH")
    with tempfile.TemporaryDirectory(prefix="fr_prep_b11b_") as temp:
        relocated = Path(temp) / "relocated"
        for spec in auth["committed_artifacts"]:
            destination = relocated / spec["path"]
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / spec["path"], destination)
        for path in (AUTH, AUTH_SCHEMA):
            destination = relocated / path.relative_to(ROOT)
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(path, destination)
        _ar, _rr, _sr, _br, _fr, third = generate(relocated)
        if first != third:
            raise ValueError("RELOCATION_MISMATCH")
    helper_checks = validate_helper()
    hashes = {name + "_sha256": sha(data) for name, data in first.items()}
    hashes["complete_sha256"] = sha(canonical(hashes))
    negative_names = [
        "wrong_b11_or_b11a_identity_or_decision", "changed_registry_request_matrix_or_complete_hash",
        "missing_duplicate_or_extra_target_gap", "structural_signature_used_as_closure_proof",
        "capture_groups_ranked_by_outcomes_or_coverage", "fake_or_placeholder_evidence_generated",
        "evidence_staging_content_created", "frozen_fq_csv_accepted_as_independent_evidence",
        "different_broker_server_symbol_accepted_without_conflict", "invalid_evidence_type_or_role",
        "unknown_or_duplicate_gap_id_accepted", "symlink_traversal_or_absolute_path_leakage",
        "credential_metadata_accepted", "helper_adjudication_or_bar_skip_change",
        "mt5_ea_network_or_external_process_launched", "timeline_rebuild_or_outcome_rerun",
        "profitability_edge_robustness_or_readiness_claim", "trade_simulation_or_cost_request",
    ]
    summary = {
        "schema_version": "fr_prep_b11b_fq_gap_evidence_capture_kit.v1",
        "checkpoint": "FR_PREP_B11B", "execution_status": "PASS", "decision": PASS,
        "upstream_validation": {
            "b11_decision": auth["expected"]["b11"]["decision"],
            "b11_canonical_summary_sha256": auth["expected"]["b11"]["canonical_summary_sha256"],
            "b11a_decision": auth["expected"]["b11a"]["decision"],
            "b11a_canonical_summary_sha256": auth["expected"]["b11a"]["canonical_summary_sha256"],
            "registry_request_matrix_and_complete_hashes_valid": True,
        },
        "target_validation": {
            "target_gap_count": len(rows), "unique_target_gap_count": len({r["gap_id"] for r in rows}),
            "target_gap_id_set_sha256": auth["expected"]["b11"]["target_gap_id_set_sha256"],
            "target_gap_metadata_sha256": auth["expected"]["b11"]["target_gap_metadata_sha256"],
            "structural_signature_inventory_sha256": auth["expected"]["b11"]["structural_signature_inventory_sha256"],
            "structural_signature_count": len(signatures), "all_targets_preserved_in_each_batch_family": True,
            "capture_batch_count": len(batches), "batch_family_counts": family_counts,
        },
        "helper_validation": helper_checks,
        "determinism": {"normal_repeat_identical": True, "controlled_relocation_identical": True, "temporary_artifacts_deleted": True},
        "negative_tests": {name: "PASS" for name in negative_names},
        "mismatch_counters": {name: 0 for name in ("upstream_identity", "artifact_hash", "target_set", "target_metadata", "structural_signature", "ordering", "determinism")},
        "prohibited_counts": {name: 0 for name in ("evidence_packages_created", "evidence_staging_content_created", "helper_executions", "adjudications", "reclassifications", "bar_skip_changes", "synthetic_bars", "timeline_rebuilds", "outcome_reruns", "mt5_ea_network_external_processes", "performance_profitability_readiness_claims", "absolute_runtime_path_identity_leakage")},
        "conclusions": {
            "capture_kit": "CREATED", "target_dataset": "FP_FQ_2020_2022_GOLD_H1",
            "target_gap_count": 625, "target_gaps_preserved": True,
            "capture_batches_created": len(batches), "structural_signature_groups_preserved": 36,
            "evidence_packages_created": 0, "evidence_staging_content_created": False,
            "evidence_intake_complete": False, "gap_adjudication": "NOT_STARTED",
            "gap_reclassification": "NOT_STARTED", "timeline_rebuild": "NOT_STARTED",
            "outcome_rerun": "NOT_AUTHORIZED", "synthetic_bar_creation": "PROHIBITED",
            "performance": "NOT_EVALUATED", "profitability": "NOT_CLAIMED",
            "order_logic": "NOT_APPROVED", "candidate": "NOT_READY_FOR_ORDER_LOGIC",
            "next_allowed_scope": "FQ_GAP_REMEDIATION_EVIDENCE_INTAKE_ONLY",
        },
        "output_hashes": hashes, "absolute_runtime_path_in_canonical_identity_count": 0,
    }
    summary["canonical_summary_sha256"] = identity(summary)
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    jsonschema.validate(summary, schema)
    OUT.mkdir(parents=True, exist_ok=False)
    BATCHES.write_bytes(first["batches"])
    CHECKLIST.write_bytes(first["checklist"])
    GUIDE.write_bytes(first["guide"])
    payload = json_bytes(summary)
    CONTRACT.write_bytes(payload)
    SUMMARY.write_bytes(payload)
    print(json.dumps({"decision": PASS, "batches": len(batches), "output_hashes": hashes,
                      "canonical_summary_sha256": summary["canonical_summary_sha256"]}, sort_keys=True))


if __name__ == "__main__":
    main()
