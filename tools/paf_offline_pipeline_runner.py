#!/usr/bin/env python3
"""Run the offline PAF lookahead data pipeline.

Pipeline:
raw bars CSV -> optional schema normalization -> bars validation -> lookahead join.

This runner does not run MT5, does not run Strategy Tester, does not send
orders, and does not prove profitability. It only orchestrates existing
offline research tools with guardrail stop gates.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


def run_command(command: list[str], cwd: Path) -> dict[str, Any]:
    started = datetime.now()
    completed = subprocess.run(
        command,
        cwd=str(cwd),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    finished = datetime.now()
    return {
        "command": command,
        "returncode": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
        "started_at": started.isoformat(timespec="seconds"),
        "finished_at": finished.isoformat(timespec="seconds"),
    }


def write_markdown_summary(path: Path, summary: dict[str, Any]) -> None:
    lines = [
        "# PAF Offline Pipeline Runner Summary",
        "",
        "This is an offline research pipeline summary. It does not run MT5, does not send orders, and does not prove profitability.",
        "",
        "## Verdict",
        "",
        f"`{summary['verdict']}`",
        "",
        "## Inputs",
        "",
        f"- Raw CSV: `{summary.get('raw_csv', '')}`",
        f"- Bars CSV: `{summary.get('bars_csv', '')}`",
        f"- Shadow outcomes: `{summary['shadow_outcomes']}`",
        f"- Results root: `{summary['results_root']}`",
        f"- Symbol: `{summary['symbol']}`",
        f"- Timeframe: `{summary['timeframe']}`",
        f"- Horizon bars: `{summary['horizon_bars']}`",
        f"- Join horizons: `{summary['join_horizons']}`",
        "",
        "## Stage Results",
        "",
        "| Stage | Status | Return Code |",
        "|---|---|---:|",
    ]
    for stage in summary["stages"]:
        lines.append(f"| `{stage['name']}` | `{stage['status']}` | {stage['returncode']} |")

    lines += [
        "",
        "## Stop Reason",
        "",
        f"`{summary.get('stop_reason', '')}`",
        "",
        "## Guardrails",
        "",
        "- Offline pipeline only.",
        "- No MT5 run.",
        "- No Strategy Tester run.",
        "- No market orders or pending orders.",
        "- No position modification.",
        "- No optimization.",
        "- No lot/risk increase.",
        "- No profitability claim.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def append_stage(summary: dict[str, Any], name: str, result: dict[str, Any]) -> None:
    summary["stages"].append(
        {
            "name": name,
            "status": "PASS" if result["returncode"] == 0 else "FAIL",
            "returncode": result["returncode"],
            "stdout": result["stdout"],
            "stderr": result["stderr"],
            "command": result["command"],
        }
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Run offline PAF bars normalize/validate/join pipeline.")
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument("--raw-csv", help="Raw MT5-style bars CSV to normalize before validation.")
    input_group.add_argument("--bars-csv", help="Already normalized bars CSV with time,open,high,low,close.")
    parser.add_argument("--shadow-outcomes", required=True)
    parser.add_argument("--results-root", default="research/results/paf_offline_pipeline")
    parser.add_argument("--symbol", default="GOLD#")
    parser.add_argument("--timeframe", default="H1")
    parser.add_argument("--horizon-bars", type=int, default=48)
    parser.add_argument("--join-horizons", default="6,12,24,48")
    parser.add_argument("--tp-atr-multiple", type=float, default=1.5)
    parser.add_argument("--sl-atr-multiple", type=float, default=1.0)
    parser.add_argument("--non-broker-comparable", action="store_true")
    args = parser.parse_args()

    repo_root = Path.cwd()
    results_root = Path(args.results_root)
    results_root.mkdir(parents=True, exist_ok=True)

    normalized_bars = results_root / "paf_lookahead_bars.csv"
    bars_csv = Path(args.bars_csv) if args.bars_csv else normalized_bars
    summary: dict[str, Any] = {
        "verdict": "INCOMPLETE",
        "raw_csv": args.raw_csv or "",
        "bars_csv": str(bars_csv),
        "shadow_outcomes": args.shadow_outcomes,
        "results_root": str(results_root),
        "symbol": args.symbol,
        "timeframe": args.timeframe,
        "horizon_bars": args.horizon_bars,
        "join_horizons": args.join_horizons,
        "tp_atr_multiple": args.tp_atr_multiple,
        "sl_atr_multiple": args.sl_atr_multiple,
        "stages": [],
        "stop_reason": "",
        "guardrails": [
            "offline pipeline only",
            "no MT5 run",
            "no Strategy Tester run",
            "no orders",
            "no position modification",
            "no optimization",
            "no profitability claim",
        ],
    }

    if args.raw_csv:
        normalize_command = [
            sys.executable,
            "tools/paf_bars_schema_normalizer.py",
            "--raw-csv",
            args.raw_csv,
            "--output-csv",
            str(normalized_bars),
            "--results-root",
            str(results_root),
            "--source-symbol",
            args.symbol,
            "--source-timeframe",
            args.timeframe,
        ]
        if args.non_broker_comparable:
            normalize_command.append("--non-broker-comparable")
        normalize_result = run_command(normalize_command, repo_root)
        append_stage(summary, "normalize", normalize_result)
        if normalize_result["returncode"] != 0:
            summary["verdict"] = "FAIL"
            summary["stop_reason"] = "normalization failed; validator and joiner were not run"
            write_outputs(results_root, summary)
            return 2

    validate_command = [
        sys.executable,
        "tools/paf_lookahead_bars_validator.py",
        "--bars-csv",
        str(bars_csv),
        "--shadow-outcomes",
        args.shadow_outcomes,
        "--results-root",
        str(results_root),
        "--symbol",
        args.symbol,
        "--timeframe",
        args.timeframe,
        "--horizon-bars",
        str(args.horizon_bars),
    ]
    validate_result = run_command(validate_command, repo_root)
    append_stage(summary, "validate", validate_result)
    if validate_result["returncode"] != 0:
        summary["verdict"] = "FAIL"
        summary["stop_reason"] = "validation failed; joiner was not run"
        write_outputs(results_root, summary)
        return 2

    join_command = [
        sys.executable,
        "tools/paf_lookahead_joiner.py",
        "--shadow-outcomes",
        args.shadow_outcomes,
        "--bars-csv",
        str(bars_csv),
        "--results-root",
        str(results_root),
        "--horizons",
        args.join_horizons,
        "--tp-atr-multiple",
        str(args.tp_atr_multiple),
        "--sl-atr-multiple",
        str(args.sl_atr_multiple),
    ]
    join_result = run_command(join_command, repo_root)
    append_stage(summary, "join", join_result)
    if join_result["returncode"] != 0:
        summary["verdict"] = "FAIL"
        summary["stop_reason"] = "joiner failed"
        write_outputs(results_root, summary)
        return 2

    summary["verdict"] = "PASS"
    summary["stop_reason"] = ""
    write_outputs(results_root, summary)
    return 0


def write_outputs(results_root: Path, summary: dict[str, Any]) -> None:
    (results_root / "paf_offline_pipeline_runner_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    write_markdown_summary(results_root / "paf_offline_pipeline_runner_summary.md", summary)
    print(f"Offline pipeline verdict: {summary['verdict']}")
    if summary.get("stop_reason"):
        print(f"Stop reason: {summary['stop_reason']}")
    print(f"Summary: {results_root / 'paf_offline_pipeline_runner_summary.md'}")


if __name__ == "__main__":
    raise SystemExit(main())
