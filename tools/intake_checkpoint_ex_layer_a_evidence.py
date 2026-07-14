#!/usr/bin/env python3
"""Fail-closed offline intake for user-supplied Checkpoint EX Layer A evidence."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from datetime import datetime
from pathlib import Path

from intake_yearly_xm_gap_evidence import GAP_TIME_FORMAT, load_raw


PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def parse_notes(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        if ":" not in line or line.lstrip().startswith("#"):
            continue
        key, value = line.split(":", 1)
        values[key.strip()] = value.strip()
    return values


def expected_screenshot_name(index: int, gap: dict[str, str]) -> str:
    previous = datetime.strptime(gap["prev_time"], GAP_TIME_FORMAT).strftime("%Y%m%d_%H%M")
    following = datetime.strptime(gap["next_time"], GAP_TIME_FORMAT).strftime("%Y%m%d_%H%M")
    return f"gap_{index:02d}_{previous}_{following}_GOLD_HASH_H1.png"


def png_valid(path: Path) -> bool:
    with path.open("rb") as handle:
        return handle.read(len(PNG_SIGNATURE)) == PNG_SIGNATURE


def main() -> int:
    parser = argparse.ArgumentParser(description="Offline Checkpoint EX Layer A evidence intake.")
    parser.add_argument("--raw-csv", action="append", required=True)
    parser.add_argument("--gaps-csv", required=True)
    parser.add_argument("--screenshots-dir", required=True)
    parser.add_argument("--notes", required=True)
    parser.add_argument("--results-root", required=True)
    args = parser.parse_args()

    if len(args.raw_csv) != 3:
        raise SystemExit("Exactly three 2023-2025 raw CSV files are required")
    screenshots_dir = Path(args.screenshots_dir)
    notes_path = Path(args.notes)
    if not screenshots_dir.is_dir() or not notes_path.is_file():
        raise SystemExit("screenshots directory or notes file is missing")

    combined: dict[datetime, Path] = {}
    files: list[dict[str, object]] = []
    for raw in args.raw_csv:
        bars, file_summary = load_raw(Path(raw))
        overlap = set(combined).intersection(bars)
        if overlap:
            raise SystemExit(f"duplicate timestamps across yearly CSV files: {len(overlap)}")
        combined.update(bars)
        files.append(file_summary)

    with Path(args.gaps_csv).open(encoding="utf-8-sig", newline="") as handle:
        gaps = list(csv.DictReader(handle))
    if len(gaps) != 28:
        raise SystemExit(f"frozen gap count must be 28, got {len(gaps)}")

    notes = parse_notes(notes_path)
    note_checks = {
        "symbol": notes.get("symbol") == "GOLD#",
        "timeframe": notes.get("timeframe") == "H1",
        "terminal_path": bool(notes.get("mt5_terminal_path")),
        "terminal_build": bool(notes.get("mt5_build")) and "UNKNOWN" not in notes.get("mt5_build", "").upper(),
        "xm_server": bool(notes.get("xm_server")) and "UNKNOWN" not in notes.get("xm_server", "").upper(),
        "chart_time_basis": notes.get("chart_time_basis", "").startswith("XM MT5 server chart time"),
        "history_refresh_user_attested": notes.get("history_refresh", "").upper() == "YES",
        "raw_files_unmodified_user_attested": notes.get("raw_files_modified", "").upper() == "NO",
        "screenshot_visual_content_user_attested": notes.get("screenshot_visual_content_user_attested", "").upper() == "YES",
        "timezone_dst_exact_source_attached": notes.get("server_timezone_dst", "").upper() not in {"", "UNKNOWN"},
    }

    all_times = sorted(combined)
    rows: list[dict[str, object]] = []
    confirmed = 0
    png_pass = 0
    for index, gap in enumerate(gaps, start=1):
        previous = datetime.strptime(gap["prev_time"], GAP_TIME_FORMAT)
        following = datetime.strptime(gap["next_time"], GAP_TIME_FORMAT)
        expected_delta = float(gap["delta_hours"])
        interior_count = sum(1 for time in all_times if previous < time < following)
        csv_confirmed = (
            previous in combined
            and following in combined
            and (following - previous).total_seconds() / 3600.0 == expected_delta
            and interior_count == 0
        )
        confirmed += int(csv_confirmed)
        filename = expected_screenshot_name(index, gap)
        screenshot = screenshots_dir / filename
        signature_valid = screenshot.is_file() and png_valid(screenshot)
        png_pass += int(signature_valid)
        rows.append({
            "gap_id": f"gap_{index:02d}",
            "prev_time": gap["prev_time"],
            "next_time": gap["next_time"],
            "delta_hours": gap["delta_hours"],
            "csv_gap_confirmed": str(csv_confirmed).lower(),
            "interior_h1_bars": interior_count,
            "screenshot_file": filename,
            "screenshot_present": str(screenshot.is_file()).lower(),
            "screenshot_png_signature_valid": str(signature_valid).lower(),
            "screenshot_sha256": sha256(screenshot) if signature_valid else "",
            "layer_a_status": "PRESENT_PENDING_EXACT_TIMEZONE_AND_VISUAL_REVIEW" if csv_confirmed and signature_valid else "INCOMPLETE",
            "layer_b_status": "MISSING",
            "acceptance_state": "CONTEXT_ONLY",
        })

    results = Path(args.results_root)
    results.mkdir(parents=True, exist_ok=True)
    with (results / "checkpoint_ex_layer_a_intake.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    summary = {
        "execution_status": "PASS" if confirmed == 28 and png_pass == 28 else "FAIL_INPUT_RECONCILIATION",
        "evidence_status": "INCOMPLETE",
        "frozen_gap_count": 28,
        "csv_confirmed_gaps": confirmed,
        "screenshot_name_and_png_signature_pass": png_pass,
        "notes_sha256": sha256(notes_path),
        "yearly_files": files,
        "note_checks": note_checks,
        "layer_a_complete": 0,
        "layer_b_complete": 0,
        "exact_broker_evidence_complete": 0,
        "acceptance_state": "CONTEXT_ONLY",
        "blockers": ["exact_timezone_dst_source_missing", "screenshot_visual_content_not_independently_verified", "layer_b_exact_xm_schedule_or_session_source_missing"],
        "policy_change_approved": False,
        "mt5_opened": False,
        "strategy_performance_status": "NOT_EVALUATED",
        "order_logic_status": "NOT_APPROVED",
        "paf_status": "NOT_READY_FOR_ORDER_LOGIC",
        "profitability_claim": False,
    }
    (results / "checkpoint_ex_layer_a_intake_summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    lines = ["# Checkpoint EX Layer A Evidence Intake", ""]
    lines.extend(f"- {key}: `{value}`" for key, value in summary.items())
    lines.append("")
    (results / "checkpoint_ex_layer_a_intake_summary.md").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0 if summary["execution_status"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
