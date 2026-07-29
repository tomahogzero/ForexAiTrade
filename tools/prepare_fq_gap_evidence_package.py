#!/usr/bin/env python3
"""Offline packager for future FQ gap evidence; it never adjudicates gaps."""

import argparse
import hashlib
import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUEST = ROOT / "research/results/checkpoint_fr_prep_b11a/fq_gap_evidence_request_manifest.json"
REQUEST_SHA256 = "b3e2cd4b1b075884491a9134bea78e453459bde690d946973613082ce780a7ae"
STAGING = ROOT / "research/evidence/fq_gap_remediation_intake"
PRIMARY_TYPES = {
    "BROKER_SERVER_SESSION_SCHEDULE",
    "SAME_BROKER_SERVER_LOWER_TIMEFRAME_OR_TICK_EXPORT",
    "INDEPENDENT_SAME_BROKER_SERVER_H1_EXPORT",
    "OFFICIAL_MARKET_OR_BROKER_HOLIDAY_NOTICE",
}
CORROBORATIVE_TYPES = {
    "TERMINAL_SCREENSHOTS", "OPERATOR_NOTES",
    "RECURRING_TIMESTAMP_PATTERNS_IN_EXISTING_FQ_INVENTORY",
    "GENERIC_MARKET_HOUR_WEBSITES", "OTHER_BROKER_DATA",
    "NEARBY_DATES_OR_NEIGHBORING_SYMBOLS",
}
FROZEN_SOURCE_NAMES = {
    "GOLD#_H1_202001020900_202012311800.csv",
    "GOLD#_H1_202101040100_202112311800.csv",
    "GOLD#_H1_202201030100_202212302300.csv",
}
SENSITIVE = re.compile(r"(?i)(password|passwd|credential|secret|token|api[_ -]?key|login[_ -]?id|account[_ -]?(number|id)|\\baccount\\b)")


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def safe_text(label, value):
    if SENSITIVE.search(value):
        raise ValueError(f"sensitive metadata rejected: {label}")
    return value


def safe_relative(path_text):
    path = Path(path_text)
    if path.is_absolute() or ".." in path.parts:
        raise ValueError("artifact must be a repository-relative path without traversal")
    resolved = (ROOT / path).resolve()
    try:
        resolved.relative_to(ROOT.resolve())
    except ValueError as exc:
        raise ValueError("artifact resolves outside repository") from exc
    if resolved.is_symlink() or any(parent.is_symlink() for parent in resolved.parents if parent != ROOT.parent):
        raise ValueError("symlinks are rejected")
    if not resolved.is_file():
        raise ValueError("artifact does not exist")
    return path.as_posix(), resolved


def frozen_target_ids():
    raw = REQUEST.read_bytes()
    if sha256_bytes(raw) != REQUEST_SHA256:
        raise ValueError("frozen target manifest hash mismatch")
    doc = json.loads(raw)
    ids = [row["gap_id"] for row in doc["intake_targets"]]
    if len(ids) != 625 or len(set(ids)) != 625:
        raise ValueError("frozen target set invalid")
    return set(ids)


def requested_gap_ids(single_ids, gap_id_file):
    ids = list(single_ids)
    if gap_id_file:
        relative, resolved = safe_relative(gap_id_file)
        del relative
        ids.extend(line.strip() for line in resolved.read_text(encoding="utf-8").splitlines() if line.strip())
    if not ids:
        raise ValueError("at least one --gap-id or --gap-id-file is required")
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate gap ID rejected")
    unknown = sorted(set(ids) - frozen_target_ids())
    if unknown:
        raise ValueError("unknown gap ID rejected: " + ",".join(unknown))
    return sorted(ids)


def build_parser():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--package-id", required=True)
    parser.add_argument("--evidence-type", required=True)
    parser.add_argument("--evidence-role", required=True, choices=["PRIMARY", "CORROBORATIVE_ONLY"])
    parser.add_argument("--broker", required=True)
    parser.add_argument("--server", required=True)
    parser.add_argument("--symbol", required=True)
    parser.add_argument("--time-basis", required=True)
    parser.add_argument("--timezone-or-unknown", required=True)
    parser.add_argument("--effective-start", required=True)
    parser.add_argument("--effective-end", required=True)
    parser.add_argument("--gap-id", action="append", default=[])
    parser.add_argument("--gap-id-file")
    parser.add_argument("--source-organization", required=True)
    parser.add_argument("--operator-notes", default="")
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,79}", args.package_id):
        raise ValueError("invalid package ID")
    all_types = PRIMARY_TYPES | CORROBORATIVE_TYPES
    if args.evidence_type not in all_types:
        raise ValueError("invalid evidence type")
    expected_role = "PRIMARY" if args.evidence_type in PRIMARY_TYPES else "CORROBORATIVE_ONLY"
    if args.evidence_role != expected_role:
        raise ValueError("evidence type/role mismatch")
    artifact_relative, artifact = safe_relative(args.artifact)
    del artifact_relative
    if artifact.name in FROZEN_SOURCE_NAMES:
        raise ValueError("frozen FQ source CSV cannot be independent evidence")
    for label in ("broker", "server", "symbol", "source_organization", "operator_notes"):
        safe_text(label, getattr(args, label))
    gaps = requested_gap_ids(args.gap_id, args.gap_id_file)
    package_dir = STAGING / args.package_id
    if package_dir.exists():
        raise ValueError("package ID already exists")
    package_dir.mkdir(parents=True, exist_ok=False)
    destination = package_dir / artifact.name
    shutil.copyfile(artifact, destination)
    metadata = {
        "schema_version": "fq_gap_evidence_package.v1",
        "evidence_package_id": args.package_id,
        "gap_id_or_explicit_gap_id_set": gaps,
        "evidence_type": args.evidence_type,
        "evidence_role": args.evidence_role,
        "source_organization": args.source_organization,
        "broker": args.broker, "server": args.server, "symbol": args.symbol,
        "time_basis": args.time_basis,
        "timezone_or_unknown": args.timezone_or_unknown,
        "effective_start": args.effective_start, "effective_end": args.effective_end,
        "captured_at": datetime.now(timezone.utc).isoformat(),
        "artifact_path": destination.relative_to(ROOT).as_posix(),
        "artifact_sha256": sha256_bytes(destination.read_bytes()),
        "source_metadata": {"packaging_mode": "OFFLINE_OPERATOR_CAPTURE"},
        "supports_status": [], "conflicts_with_status": [],
        "operator_notes": args.operator_notes,
        "validation_status": "PACKAGE_REGISTERED_UNAUDITED",
    }
    descriptor = package_dir / "evidence_package.json"
    descriptor.write_text(json.dumps(metadata, ensure_ascii=True, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(descriptor.relative_to(ROOT).as_posix())


if __name__ == "__main__":
    main()
