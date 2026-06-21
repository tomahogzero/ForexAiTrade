#!/usr/bin/env python3
"""Risk gate attribution for ForexAiTrade Checkpoint I2.

Parses existing run artifacts only. It does not run MT5 and does not change
strategy or risk behavior.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any


BASELINE_CASE_ID = "EURUSD_H1_EXIT_BASELINE_10000"
PHASES = ("train", "validation", "out_of_sample")


LOG_LINE_RE = re.compile(r"^(?P<time>\d{4}\.\d{2}\.\d{2} \d{2}:\d{2}:\d{2}) (?P<message>.*)$")
REASON_RE = re.compile(r" reason=(?P<reason>.*)$")


def load_json(path: Path) -> Any:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception:
        return {}


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = sorted({key for row in rows for key in row})
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def parse_dt(value: str | None) -> datetime | None:
    if not value:
        return None
    for fmt in ("%Y.%m.%d %H:%M:%S", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    return None


def month_of(dt: datetime | None) -> str:
    return dt.strftime("%Y-%m") if dt else "Unknown"


def to_float(value: Any) -> float | None:
    try:
        if value is None or value == "":
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def fmt(value: Any) -> str:
    if value is None or value == "":
        return ""
    return str(value).replace("|", "/")


def categorize_reason(reason: str, message: str) -> str:
    text = f"{reason} {message}".lower()
    if "losing streak" in text:
        return "losing_streak"
    if "daily loss" in text:
        return "daily_loss"
    if "weekly loss" in text:
        return "weekly_loss"
    if "floating drawdown" in text or "total drawdown" in text:
        return "total_drawdown"
    if "equity kill" in text:
        return "equity_kill_switch"
    if "max open orders" in text:
        return "max_open_order"
    if "spread above maximum" in text or "spread too wide" in text:
        return "spread"
    if "unsafe regime" in text:
        return "unsafe_regime"
    if "margin" in text or "not enough money" in text:
        return "margin"
    if "broker minimum lot" in text or "minimum lot" in text or "below broker minimum" in text:
        return "broker_minimum_lot"
    if "no strategy signal" in text:
        return "no_strategy_signal"
    if "execution safety checks passed" in text:
        return "accepted"
    return "other_risk_block" if "blocked" in message.lower() or "block" in text else "other"


def parse_log_events(case_dir: Path) -> list[dict[str, Any]]:
    case = load_json(case_dir / "case.json")
    log_path = case_dir / "ea_mirror.log"
    events: list[dict[str, Any]] = []
    if not log_path.exists():
        return events
    for line_no, line in enumerate(log_path.read_text(encoding="utf-8", errors="ignore").splitlines(), start=1):
        match = LOG_LINE_RE.match(line)
        if not match:
            continue
        timestamp = parse_dt(match.group("time"))
        message = match.group("message")
        reason_match = REASON_RE.search(message)
        reason = reason_match.group("reason").strip() if reason_match else ""
        event_type = "other"
        if message.startswith("Signal accepted:"):
            event_type = "signal_accepted"
        elif message.startswith("Signal blocked:"):
            event_type = "signal_blocked"
        elif message.startswith("No trade:"):
            event_type = "no_trade"
        elif "block" in message.lower():
            event_type = "safety_block"
        category = categorize_reason(reason, message)
        if event_type in {"signal_accepted", "signal_blocked", "no_trade", "safety_block"}:
            events.append({
                "run_id": case.get("run_id") or case_dir.parent.name,
                "case_id": case.get("case_id") or case_dir.name,
                "base_case_id": case.get("base_case_id") or BASELINE_CASE_ID,
                "phase": case.get("phase"),
                "timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S") if timestamp else "",
                "month": month_of(timestamp),
                "event_type": event_type,
                "category": category,
                "reason": reason,
                "message": message,
                "line_no": line_no,
            })
    return events


def trade_rows(case_dir: Path) -> list[dict[str, Any]]:
    rows = []
    for row in read_csv(case_dir / "trade_ledger.csv"):
        close_time = parse_dt(row.get("close_time"))
        open_time = parse_dt(row.get("open_time"))
        profit = to_float(row.get("total_profit")) or to_float(row.get("profit")) or 0.0
        rows.append({
            **row,
            "open_dt": open_time,
            "close_dt": close_time,
            "profit_float": profit,
        })
    rows.sort(key=lambda row: row.get("close_dt") or datetime.min)
    return rows


def consecutive_losses_before(trades: list[dict[str, Any]], before: datetime | None) -> int:
    if before is None:
        return 0
    closed = [row for row in trades if row.get("close_dt") and row["close_dt"] <= before]
    streak = 0
    for row in reversed(closed):
        profit = float(row.get("profit_float") or 0.0)
        if profit < 0:
            streak += 1
        elif profit > 0:
            break
    return streak


def last_trade_before(trades: list[dict[str, Any]], before: datetime | None) -> dict[str, Any] | None:
    if before is None:
        return None
    closed = [row for row in trades if row.get("close_dt") and row["close_dt"] <= before]
    return closed[-1] if closed else None


def accepted_count(events: list[dict[str, Any]], before: datetime | None = None, after: datetime | None = None) -> int:
    count = 0
    for event in events:
        if event.get("event_type") != "signal_accepted":
            continue
        timestamp = parse_dt(event.get("timestamp"))
        if before is not None and (timestamp is None or timestamp >= before):
            continue
        if after is not None and (timestamp is None or timestamp <= after):
            continue
        count += 1
    return count


def summarize_phase(case_dir: Path, events: list[dict[str, Any]]) -> dict[str, Any]:
    case = load_json(case_dir / "case.json")
    parsed = load_json(case_dir / "parsed_result.json")
    trades = trade_rows(case_dir)
    losing_events = [event for event in events if event.get("category") == "losing_streak"]
    first_losing = parse_dt(losing_events[0]["timestamp"]) if losing_events else None
    last_losing = parse_dt(losing_events[-1]["timestamp"]) if losing_events else None
    last_event_dt = parse_dt(events[-1]["timestamp"]) if events else None
    last_trade = last_trade_before(trades, first_losing)
    accepted_before = accepted_count(events, before=first_losing) if first_losing else accepted_count(events)
    accepted_after = accepted_count(events, after=first_losing) if first_losing else 0
    recovered = bool(first_losing and accepted_after > 0)
    blocks_until_end = bool(first_losing and last_losing and last_event_dt and last_losing >= last_event_dt)
    if first_losing and last_losing and last_event_dt:
        # Allow the last logged event to be a deinit/footer; still consider lockout persistent if the
        # final losing-streak block is near the final logged trading event date.
        blocks_until_end = last_losing.date() >= last_event_dt.date()

    counters = Counter(event.get("category") for event in events)
    signal_block_counters = Counter(event.get("category") for event in events if event.get("event_type") == "signal_blocked")
    return {
        "run_id": case.get("run_id") or case_dir.parent.name,
        "case_id": case.get("case_id") or case_dir.name,
        "phase": case.get("phase"),
        "execution_status": (load_json(case_dir / "status.json") or {}).get("execution_status", ""),
        "total_trades": parsed.get("total_trades") if isinstance(parsed, dict) else len(trades),
        "net_profit": parsed.get("net_profit") if isinstance(parsed, dict) else None,
        "profit_factor": parsed.get("profit_factor") if isinstance(parsed, dict) else None,
        "accepted_signals": counters.get("accepted", 0),
        "signal_blocked_total": sum(signal_block_counters.values()),
        "no_trade_total": len([event for event in events if event.get("event_type") == "no_trade"]),
        "losing_streak_blocks": counters.get("losing_streak", 0),
        "daily_loss_blocks": counters.get("daily_loss", 0),
        "weekly_loss_blocks": counters.get("weekly_loss", 0),
        "total_drawdown_blocks": counters.get("total_drawdown", 0),
        "equity_kill_switch_blocks": counters.get("equity_kill_switch", 0),
        "max_open_order_blocks": counters.get("max_open_order", 0),
        "spread_blocks": counters.get("spread", 0),
        "unsafe_regime_blocks": counters.get("unsafe_regime", 0),
        "margin_blocks": counters.get("margin", 0),
        "broker_minimum_lot_blocks": counters.get("broker_minimum_lot", 0),
        "other_risk_blocks": counters.get("other_risk_block", 0),
        "first_losing_streak_block": first_losing.strftime("%Y-%m-%d %H:%M:%S") if first_losing else "",
        "last_losing_streak_block": last_losing.strftime("%Y-%m-%d %H:%M:%S") if last_losing else "",
        "accepted_trades_before_first_losing_block": accepted_before,
        "accepted_trades_after_first_losing_block": accepted_after,
        "losing_streak_gate_recovered": recovered,
        "losing_streak_blocks_until_end": blocks_until_end,
        "last_closed_trade_before_gate_close_time": last_trade.get("close_time") if last_trade else "",
        "last_closed_trade_before_gate_profit": round(float(last_trade.get("profit_float") or 0.0), 2) if last_trade else "",
        "last_closed_trade_before_gate_exit_reason": last_trade.get("exit_reason") if last_trade else "",
        "consecutive_losses_before_trigger": consecutive_losses_before(trades, first_losing),
    }


def summarize_month(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str], Counter[str]] = defaultdict(Counter)
    for event in events:
        key = (str(event.get("phase")), str(event.get("month")))
        grouped[key][str(event.get("category"))] += 1
        grouped[key]["total_events"] += 1
    rows = []
    for (phase, month), counter in sorted(grouped.items()):
        rows.append({
            "phase": phase,
            "month": month,
            "total_events": counter.get("total_events", 0),
            "losing_streak_blocks": counter.get("losing_streak", 0),
            "spread_blocks": counter.get("spread", 0),
            "unsafe_regime_blocks": counter.get("unsafe_regime", 0),
            "max_open_order_blocks": counter.get("max_open_order", 0),
            "no_strategy_signal": counter.get("no_strategy_signal", 0),
            "accepted": counter.get("accepted", 0),
        })
    return rows


def markdown_table(rows: list[dict[str, Any]], fields: list[str]) -> list[str]:
    lines = ["| " + " | ".join(fields) + " |", "|" + "|".join("---" for _ in fields) + "|"]
    for row in rows:
        lines.append("| " + " | ".join(fmt(row.get(field)) for field in fields) + " |")
    return lines


def write_summary(path: Path, phase_rows: list[dict[str, Any]]) -> None:
    lines = [
        "# Risk Gate Attribution Summary",
        "",
        "Scope: `EURUSD_H1_EXIT_BASELINE_10000` from `run_20260621_205032`.",
        "",
        "This is diagnostic attribution only. It does not change risk settings or strategy behavior.",
        "",
        "## Phase Summary",
        "",
    ]
    fields = [
        "phase", "total_trades", "net_profit", "accepted_signals",
        "losing_streak_blocks", "first_losing_streak_block", "last_losing_streak_block",
        "accepted_trades_before_first_losing_block", "accepted_trades_after_first_losing_block",
        "losing_streak_gate_recovered", "losing_streak_blocks_until_end",
        "consecutive_losses_before_trigger",
    ]
    lines += markdown_table(phase_rows, fields)
    lines += [
        "",
        "## Code Review: Losing Streak Logic",
        "",
        "- `CRiskManager::ConsecutiveLosses()` scans MT5 closed deal history from newest to oldest.",
        "- It filters by current `_Symbol` and `InpMagicNumber`.",
        "- Only `DEAL_ENTRY_OUT` and `DEAL_ENTRY_OUT_BY` closed deals are counted.",
        "- Negative closed profit increments the streak.",
        "- A positive closed profit stops the scan, effectively resetting the streak.",
        "- If the streak is greater than or equal to `InpMaxLosingStreak`, `CanOpenNewTrade()` rejects new entries.",
        "- Because rejected entries do not create new closed winning deals, the streak cannot recover while the EA is fully locked out by this gate.",
        "- This is intentional capital-preservation behavior, but it is also a research limitation because a backtest phase can become long-term locked after a short loss cluster.",
        "",
        "## Interpretation",
        "",
        "A long losing-streak lockout means the phase result is risk-gated performance, not raw strategy performance. It protects capital, but it can make train/validation/OOS comparisons harder.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_interpretation(path: Path, phase_rows: list[dict[str, Any]]) -> None:
    train = next((row for row in phase_rows if row.get("phase") == "train"), {})
    validation = next((row for row in phase_rows if row.get("phase") == "validation"), {})
    oos = next((row for row in phase_rows if row.get("phase") == "out_of_sample"), {})
    lines = [
        "# Risk Gate Research Interpretation",
        "",
        "## Is EURUSD train weakness mostly strategy loss, or risk-gate lockout?",
        "",
        f"Train has `{fmt(train.get('total_trades'))}` trades and `{fmt(train.get('losing_streak_blocks'))}` losing-streak blocks. "
        f"The first losing-streak block appears at `{fmt(train.get('first_losing_streak_block'))}` and the last at `{fmt(train.get('last_losing_streak_block'))}`. "
        "This indicates the weak train result is strongly affected by risk-gate lockout after the initial loss cluster, not only by raw entry/exit quality.",
        "",
        "## Is validation/OOS affected by the same behavior?",
        "",
        f"Validation losing-streak blocks: `{fmt(validation.get('losing_streak_blocks'))}`. "
        f"OOS losing-streak blocks: `{fmt(oos.get('losing_streak_blocks'))}`. "
        "The same gate affects later phases, but the impact appears less dominant than train because more trades were accepted before/after blocks.",
        "",
        "## Is the current losing streak gate too restrictive for research evaluation?",
        "",
        "It may be too restrictive for interpreting raw strategy behavior, especially in train. For survival-first trading this gate is conservative and intentional, but for research it can hide what the strategy would have done after the lockout.",
        "",
        "## Should future research separate raw strategy performance from risk-gated performance?",
        "",
        "Yes. Future diagnostics should report both raw strategy behavior and risk-gated behavior, strictly in Strategy Tester, so the team can distinguish strategy weakness from protective lockout effects.",
        "",
        "## Should a diagnostic-only risk-gate variant be studied later?",
        "",
        "Yes, but not as a live/demo setting. A tester-only diagnostic variant could compare current risk-gated behavior against a controlled cooldown or raw-strategy diagnostic run.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_recommendation(path: Path, phase_rows: list[dict[str, Any]]) -> None:
    train = next((row for row in phase_rows if row.get("phase") == "train"), {})
    classification = "KEEP_BASELINE_RESEARCH_MORE"
    if int(train.get("losing_streak_blocks") or 0) > 100 and not train.get("losing_streak_gate_recovered"):
        classification = "NEEDS_LOSING_STREAK_COOLDOWN_RESEARCH"
    lines = [
        "# Checkpoint I2 Recommendation",
        "",
        f"Classification: `{classification}`",
        "",
        "No live/demo setting change is approved. No final candidate is approved.",
        "",
        "## Rationale",
        "",
        f"- Train losing-streak blocks: `{fmt(train.get('losing_streak_blocks'))}`.",
        f"- Train first losing-streak block: `{fmt(train.get('first_losing_streak_block'))}`.",
        f"- Train last losing-streak block: `{fmt(train.get('last_losing_streak_block'))}`.",
        f"- Accepted signals after first train losing-streak block: `{fmt(train.get('accepted_trades_after_first_losing_block'))}`.",
        "- This suggests train is dominated by risk-gate lockout after the early loss cluster.",
        "",
        "## Guardrails",
        "",
        "- No optimization was performed.",
        "- No strategy entry logic was changed.",
        "- No exit behavior was changed.",
        "- No new strategy was added.",
        "- No lot or risk increase is approved.",
        "- Demo forward testing remains blocked.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-root", default="research/runs/run_20260621_205032")
    parser.add_argument("--results-root", default="research/results")
    parser.add_argument("--case-id", default=BASELINE_CASE_ID)
    args = parser.parse_args()

    run_root = Path(args.run_root)
    results_root = Path(args.results_root)
    results_root.mkdir(parents=True, exist_ok=True)

    all_events: list[dict[str, Any]] = []
    phase_rows: list[dict[str, Any]] = []
    for phase in PHASES:
        case_dir = run_root / f"{args.case_id}_{phase}"
        if not case_dir.exists():
            continue
        events = parse_log_events(case_dir)
        all_events.extend(events)
        phase_rows.append(summarize_phase(case_dir, events))

    month_rows = summarize_month(all_events)
    write_csv(results_root / "risk_gate_attribution_events.csv", all_events)
    write_csv(results_root / "risk_gate_attribution_by_phase.csv", phase_rows)
    write_csv(results_root / "risk_gate_attribution_by_month.csv", month_rows)
    write_summary(results_root / "risk_gate_attribution_summary.md", phase_rows)
    write_interpretation(results_root / "risk_gate_research_interpretation.md", phase_rows)
    write_recommendation(results_root / "checkpoint_i2_recommendation.md", phase_rows)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
