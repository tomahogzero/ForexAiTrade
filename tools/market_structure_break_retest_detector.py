#!/usr/bin/env python3
"""Deterministic FH detector. Fixture-only use; no historical dataset runner."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal
from hashlib import sha256
from typing import Any

TERMINAL_STATUSES = {
    "EVENT_EMITTED", "NO_BREAK", "RETEST_NOT_FOUND_WITHIN_12_BARS",
    "CONFIRMATION_NOT_FOUND_WITHIN_12_BARS", "DATA_INCOMPLETE_GAP",
    "INSUFFICIENT_LEFT_HISTORY", "INSUFFICIENT_RIGHT_HISTORY",
    "ATR_UNAVAILABLE", "DUPLICATE_SUPPRESSED",
}
EVENT_SCHEMA = [
    "event_id", "symbol", "timeframe", "direction", "swing_type",
    "swing_timestamp", "swing_confirmation_timestamp", "swing_price",
    "break_timestamp", "break_close", "retest_timestamp", "retest_price_reference",
    "confirmation_timestamp", "confirmation_open", "confirmation_high",
    "confirmation_low", "confirmation_close", "entry_reference_price", "atr", "year",
    "source_row_keys", "data_quality_status", "exclusion_reason",
]
TIE_BREAK_ORDER = ["SWING_HIGH", "SWING_LOW", "LONG", "SHORT"]


def _decimal(value: Any) -> str:
    return format(Decimal(str(value)).normalize(), "f")


def _key(*parts: Any) -> str:
    return sha256("|".join(str(part) for part in parts).encode("utf-8")).hexdigest()


def _close_timestamp(bar: dict[str, Any]) -> str:
    return (datetime.fromisoformat(bar["timestamp"]) + timedelta(hours=1)).isoformat()


def _valid(bar: dict[str, Any]) -> bool:
    required = {"timestamp", "source_row_key", "open", "high", "low", "close"}
    if not required.issubset(bar) or not bar.get("valid", True):
        return False
    return Decimal(str(bar["high"])) >= Decimal(str(bar["low"]))


def _atr(bars: list[dict[str, Any]], event_index: int) -> str | None:
    # Approved simple-average true range from completed bars strictly before event bar.
    if event_index < 15:
        return None
    prior = bars[event_index - 14:event_index]
    if len(prior) != 14 or not all(_valid(bar) and not bar.get("gap_before") for bar in prior):
        return None
    tr_values: list[Decimal] = []
    for index, bar in enumerate(prior, start=event_index - 14):
        high, low = Decimal(str(bar["high"])), Decimal(str(bar["low"]))
        previous_close = Decimal(str(bars[index - 1]["close"]))
        tr_values.append(max(high - low, abs(high - previous_close), abs(low - previous_close)))
    return _decimal(sum(tr_values) / Decimal("14"))


def _terminal(result: dict[str, Any], status: str, *, state: str, **details: Any) -> None:
    if status not in TERMINAL_STATUSES:
        raise ValueError(f"unknown status {status}")
    result["terminals"].append({"status": status, "state": state, **details})


def _swing(bars: list[dict[str, Any]], center: int, kind: str) -> bool:
    values = ("high", "high") if kind == "SWING_HIGH" else ("low", "low")
    center_value = Decimal(str(bars[center][values[0]]))
    neighbors = [Decimal(str(bars[index][values[1]])) for index in (center - 2, center - 1, center + 1, center + 2)]
    return center_value > max(neighbors) if kind == "SWING_HIGH" else center_value < min(neighbors)


def detect(source_bars: list[dict[str, Any]], *, symbol: str = "GOLD#", timeframe: str = "H1") -> dict[str, Any]:
    """Run frozen FH state machine over caller-provided bars; never reads files."""
    bars = sorted((dict(bar) for bar in source_bars), key=lambda bar: (bar.get("timestamp", ""), bar.get("source_row_key", "")))
    result: dict[str, Any] = {"events": [], "terminals": [], "swing_audit": [], "tie_break_order": TIE_BREAK_ORDER}
    active: dict[str, dict[str, Any] | None] = {"SWING_HIGH": None, "SWING_LOW": None}
    candidates: dict[str, dict[str, Any] | None] = {"LONG": None, "SHORT": None}
    closed_swing: dict[str, str | None] = {"LONG": None, "SHORT": None}

    for i, bar in enumerate(bars):
        if not _valid(bar) or bar.get("gap_before"):
            for direction, candidate in list(candidates.items()):
                if candidate:
                    _terminal(result, "DATA_INCOMPLETE_GAP", state=candidate["state"], candidate_id=candidate["candidate_id"], gap_timestamp=bar.get("timestamp"))
                    candidates[direction] = None
                    closed_swing[direction] = candidate["swing_id"]
            continue

        # Existing candidates observe this bar before any new break may be created on it.
        for direction in ("LONG", "SHORT"):
            candidate = candidates[direction]
            if not candidate or i <= candidate["break_index"]:
                continue
            candidate["bars_after_break"] += 1
            level = Decimal(candidate["swing_price"])
            touched = Decimal(str(bar["low"])) <= level if direction == "LONG" else Decimal(str(bar["high"])) >= level
            if candidate["retest_index"] is None and touched:
                candidate["retest_index"] = i
                candidate["retest_timestamp"] = _close_timestamp(bar)
            elif candidate["retest_index"] is not None and i > candidate["retest_index"]:
                previous = bars[i - 1]
                confirmed = (Decimal(str(bar["close"])) > Decimal(str(bar["open"])) and Decimal(str(bar["close"])) > Decimal(str(previous["high"]))) if direction == "LONG" else (Decimal(str(bar["close"])) < Decimal(str(bar["open"])) and Decimal(str(bar["close"])) < Decimal(str(previous["low"])))
                if confirmed:
                    atr = _atr(bars, i)
                    if atr is None:
                        _terminal(result, "ATR_UNAVAILABLE", state="SEEK_CONFIRMATION", candidate_id=candidate["candidate_id"])
                    else:
                        event = {
                            "symbol": symbol, "timeframe": timeframe, "direction": direction,
                            "swing_type": candidate["swing_type"], "swing_timestamp": candidate["swing_timestamp"],
                            "swing_confirmation_timestamp": candidate["swing_confirmation_timestamp"], "swing_price": candidate["swing_price"],
                            "break_timestamp": candidate["break_timestamp"], "break_close": candidate["break_close"],
                            "retest_timestamp": candidate["retest_timestamp"], "retest_price_reference": candidate["swing_price"],
                            "confirmation_timestamp": _close_timestamp(bar), "confirmation_open": _decimal(bar["open"]),
                            "confirmation_high": _decimal(bar["high"]), "confirmation_low": _decimal(bar["low"]),
                            "confirmation_close": _decimal(bar["close"]), "entry_reference_price": _decimal(bar["close"]),
                            "atr": atr, "year": _close_timestamp(bar)[:4],
                            "source_row_keys": candidate["source_row_keys"] + [previous["source_row_key"], bar["source_row_key"]],
                            "data_quality_status": "VALID", "exclusion_reason": None,
                        }
                        event["event_id"] = _key(symbol, timeframe, direction, candidate["swing_timestamp"], candidate["break_timestamp"], event["confirmation_timestamp"], candidate["break_id"])
                        result["events"].append({field: event[field] for field in EVENT_SCHEMA})
                        _terminal(result, "EVENT_EMITTED", state="SEEK_CONFIRMATION", event_id=event["event_id"], candidate_id=candidate["candidate_id"])
                    closed_swing[direction] = candidate["swing_id"]
                    candidates[direction] = None
                    continue
            if candidates[direction] and candidate["bars_after_break"] == 12:
                status = "RETEST_NOT_FOUND_WITHIN_12_BARS" if candidate["retest_index"] is None else "CONFIRMATION_NOT_FOUND_WITHIN_12_BARS"
                _terminal(result, status, state=candidate["state"], candidate_id=candidate["candidate_id"])
                closed_swing[direction] = candidate["swing_id"]
                candidates[direction] = None

        if i >= 4:
            window = bars[i - 4:i + 1]
            if all(_valid(candidate) and not candidate.get("gap_before") for candidate in window):
                center = i - 2
                for kind in ("SWING_HIGH", "SWING_LOW"):
                    if _swing(bars, center, kind):
                        price = _decimal(bars[center]["high"] if kind == "SWING_HIGH" else bars[center]["low"])
                        swing = {"swing_type": kind, "swing_timestamp": bars[center]["timestamp"], "swing_confirmation_timestamp": _close_timestamp(bar), "swing_price": price, "source_row_key_center": bars[center]["source_row_key"]}
                        swing["swing_id"] = _key(symbol, timeframe, kind, swing["swing_timestamp"], price, swing["source_row_key_center"])
                        active[kind] = swing
                        result["swing_audit"].append(swing)
        elif i < 2:
            _terminal(result, "INSUFFICIENT_LEFT_HISTORY", state="SEEK_CONFIRMED_SWING", bar_timestamp=bar["timestamp"])

        for direction, swing_kind in (("LONG", "SWING_HIGH"), ("SHORT", "SWING_LOW")):
            swing = active[swing_kind]
            candidate = candidates[direction]
            if swing is None:
                continue
            close = Decimal(str(bar["close"]))
            qualifies = close > Decimal(swing["swing_price"]) if direction == "LONG" else close < Decimal(swing["swing_price"])
            if candidate and qualifies and not candidate.get("duplicate_logged"):
                _terminal(result, "DUPLICATE_SUPPRESSED", state=candidate["state"], candidate_id=candidate["candidate_id"], duplicate_timestamp=_close_timestamp(bar))
                candidate["duplicate_logged"] = True
            if candidate or not qualifies or closed_swing[direction] == swing["swing_id"]:
                continue
            break_timestamp = _close_timestamp(bar)
            break_close = _decimal(bar["close"])
            break_id = _key(symbol, timeframe, direction, swing["swing_id"], break_timestamp, break_close, bar["source_row_key"])
            candidates[direction] = {
                **swing, "direction": direction, "break_id": break_id,
                "candidate_id": _key(break_id, "retest_window=12", "retest_start=next_valid_bar"),
                "break_index": i, "break_timestamp": break_timestamp, "break_close": break_close,
                "bars_after_break": 0, "retest_index": None, "retest_timestamp": None,
                "state": "SEEK_RETEST", "duplicate_logged": False,
                "source_row_keys": [swing["source_row_key_center"], bar["source_row_key"]],
            }

    for center in range(max(0, len(bars) - 2), len(bars)):
        _terminal(result, "INSUFFICIENT_RIGHT_HISTORY", state="SEEK_CONFIRMED_SWING", bar_timestamp=bars[center]["timestamp"])
    for direction, candidate in candidates.items():
        if candidate:
            _terminal(result, "INSUFFICIENT_RIGHT_HISTORY", state=candidate["state"], candidate_id=candidate["candidate_id"])
    for kind, swing in active.items():
        if swing and all(swing["swing_id"] != item.get("swing_id") for item in candidates.values() if item):
            _terminal(result, "NO_BREAK", state="SEEK_BREAK", swing_id=swing["swing_id"])
    result["events"].sort(key=lambda event: event["event_id"])
    result["terminals"].sort(key=lambda item: (item["status"], str(item)))
    return result