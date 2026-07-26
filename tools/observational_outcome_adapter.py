#!/usr/bin/env python3
"""Frozen B6 observational outcome adapter; contains no file or process I/O."""

from datetime import datetime
from decimal import Decimal, InvalidOperation, ROUND_HALF_EVEN

HORIZONS = (1, 3, 6, 12)
QUANTUM = Decimal("0.000001")
GAP_STATUS = "NOT_EVALUABLE_DATA_INCOMPLETE_GAP"
CENSOR_STATUS = "NOT_EVALUABLE_RIGHT_CENSORING"
INTEGRITY_STATUS = "NOT_EVALUABLE_SOURCE_INTEGRITY"
EVALUABLE = "EVALUABLE"
ACCEPTED_CLOSURES = {
    "ACCEPTED_ROUTINE_WEEKEND_CLOSURE",
    "ACCEPTED_ROUTINE_SESSION_CLOSURE",
}


class AdapterError(ValueError):
    """Fail-closed input rejection with a stable error code."""

    def __init__(self, code):
        super().__init__(code)
        self.code = code


def _decimal(value):
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        return Decimal("NaN")


def _finite_positive(value):
    return value.is_finite() and value > 0


def _same_decimal_or_literal(left, right):
    left_decimal = _decimal(left)
    right_decimal = _decimal(right)
    if left_decimal.is_finite() and right_decimal.is_finite():
        return left_decimal == right_decimal
    return str(left) == str(right)


def _quantized_text(value):
    return format(value.quantize(QUANTUM, rounding=ROUND_HALF_EVEN), "f")


def _parse_timestamp(value):
    try:
        return datetime.fromisoformat(value)
    except (TypeError, ValueError):
        raise AdapterError("INVALID_EVENT_TIMESTAMP")


def _valid_ohlc(item):
    values = {key: _decimal(item.get(key)) for key in ("open", "high", "low", "close")}
    if not all(_finite_positive(value) for value in values.values()):
        return None
    if (
        values["high"] < values["low"]
        or values["high"] < values["open"]
        or values["high"] < values["close"]
        or values["low"] > values["open"]
        or values["low"] > values["close"]
    ):
        return None
    return values


def _validate_events(events):
    event_ids = [event.get("event_id") for event in events]
    if any(not isinstance(event_id, str) or not event_id for event_id in event_ids):
        raise AdapterError("INVALID_EVENT_ID")
    if len(event_ids) != len(set(event_ids)):
        raise AdapterError("DUPLICATE_EVENT_ID")
    for event in events:
        if event.get("direction") not in {"LONG", "SHORT"}:
            raise AdapterError("UNSUPPORTED_DIRECTION")
        _parse_timestamp(event.get("confirmation_timestamp"))
        if not _same_decimal_or_literal(
            event.get("entry_reference_price"), event.get("confirmation_close")
        ):
            raise AdapterError("ENTRY_REFERENCE_MISMATCH")
        if not isinstance(event.get("synthetic_source_id"), str):
            raise AdapterError("INVALID_SYNTHETIC_SOURCE_ID")


def _blocked_result(horizon, status):
    return {
        "horizon_valid_h1_bars": horizon,
        "target_timestamp": None,
        "status": status,
        "direction_normalized_return_bps": None,
    }


def _return_bps(direction, entry_price, future_close):
    if direction == "LONG":
        value = (future_close - entry_price) / entry_price * Decimal("10000")
    else:
        value = (entry_price - future_close) / entry_price * Decimal("10000")
    return _quantized_text(value)


def _scan_future(timeline, confirmation_timestamp):
    valid_bars = []
    blocker = None
    previous_timestamp = None
    for item in timeline:
        try:
            timestamp = datetime.fromisoformat(item.get("timestamp"))
        except (TypeError, ValueError):
            blocker = INTEGRITY_STATUS
            break
        if previous_timestamp is not None and timestamp <= previous_timestamp:
            blocker = INTEGRITY_STATUS
            break
        previous_timestamp = timestamp
        if timestamp <= confirmation_timestamp:
            continue
        classification = item.get("classification")
        if classification in ACCEPTED_CLOSURES:
            continue
        if classification == "UNVERIFIED_GAP":
            blocker = GAP_STATUS
            break
        if classification != "VALID_BAR":
            blocker = INTEGRITY_STATUS
            break
        ohlc = _valid_ohlc(item)
        if ohlc is None:
            blocker = INTEGRITY_STATUS
            break
        valid_bars.append({"timestamp": item["timestamp"], **ohlc})
        if len(valid_bars) == max(HORIZONS):
            break
    return valid_bars, blocker


def _event_status(horizons, excursion):
    statuses = [item["status"] for item in horizons.values()] + [excursion["status"]]
    evaluable_count = sum(status == EVALUABLE for status in statuses)
    if evaluable_count == len(statuses):
        return "FULLY_EVALUABLE"
    if evaluable_count:
        return "PARTIALLY_EVALUABLE"
    return "NOT_EVALUABLE"


def _invalid_entry_record(event):
    horizons = {
        str(horizon): _blocked_result(horizon, INTEGRITY_STATUS)
        for horizon in HORIZONS
    }
    excursion = {
        "status": INTEGRITY_STATUS,
        "mfe_bps": None,
        "mae_bps": None,
    }
    return {
        "event_id": event["event_id"],
        "dataset_id": event["dataset_id"],
        "direction": event["direction"],
        "year": event["year"],
        "entry_timestamp": event["confirmation_timestamp"],
        "entry_price": None,
        "event_status": _event_status(horizons, excursion),
        "horizons": horizons,
        "excursion_12": excursion,
    }


def _evaluate_event(event, timeline):
    entry_price = _decimal(event["confirmation_close"])
    if not _finite_positive(entry_price):
        return _invalid_entry_record(event)
    confirmation = _parse_timestamp(event["confirmation_timestamp"])
    valid_bars, blocker = _scan_future(timeline, confirmation)
    horizons = {}
    for horizon in HORIZONS:
        if len(valid_bars) >= horizon:
            target = valid_bars[horizon - 1]
            horizons[str(horizon)] = {
                "horizon_valid_h1_bars": horizon,
                "target_timestamp": target["timestamp"],
                "status": EVALUABLE,
                "direction_normalized_return_bps": _return_bps(
                    event["direction"], entry_price, target["close"]
                ),
            }
        else:
            horizons[str(horizon)] = _blocked_result(
                horizon, blocker or CENSOR_STATUS
            )
    if len(valid_bars) >= 12:
        future = valid_bars[:12]
        maximum_high = max(bar["high"] for bar in future)
        minimum_low = min(bar["low"] for bar in future)
        if event["direction"] == "LONG":
            mfe = max(Decimal("0"), (maximum_high - entry_price) / entry_price)
            mae = max(Decimal("0"), (entry_price - minimum_low) / entry_price)
        else:
            mfe = max(Decimal("0"), (entry_price - minimum_low) / entry_price)
            mae = max(Decimal("0"), (maximum_high - entry_price) / entry_price)
        excursion = {
            "status": EVALUABLE,
            "mfe_bps": _quantized_text(mfe * Decimal("10000")),
            "mae_bps": _quantized_text(mae * Decimal("10000")),
        }
    else:
        excursion = {
            "status": blocker or CENSOR_STATUS,
            "mfe_bps": None,
            "mae_bps": None,
        }
    return {
        "event_id": event["event_id"],
        "dataset_id": event["dataset_id"],
        "direction": event["direction"],
        "year": event["year"],
        "entry_timestamp": event["confirmation_timestamp"],
        "entry_price": str(event["confirmation_close"]),
        "event_status": _event_status(horizons, excursion),
        "horizons": horizons,
        "excursion_12": excursion,
    }


def evaluate(events, timelines):
    """Evaluate synthetic events against supplied synthetic timelines only."""

    _validate_events(events)
    records = []
    for event in events:
        source_id = event["synthetic_source_id"]
        if source_id not in timelines:
            raise AdapterError("MISSING_SYNTHETIC_TIMELINE")
        records.append(_evaluate_event(event, timelines[source_id]))
    return sorted(records, key=lambda record: record["event_id"])
