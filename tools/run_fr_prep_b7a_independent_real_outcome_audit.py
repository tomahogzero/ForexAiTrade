#!/usr/bin/env python3
"""Independently audit committed B7 real observational outcomes."""

import argparse
import builtins
import copy
import csv
import hashlib
import io
import json
import math
import ntpath
import os
import posixpath
import re
import shutil
import subprocess
import sys
import tempfile
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from decimal import Decimal, InvalidOperation, ROUND_HALF_EVEN
from pathlib import Path

import jsonschema

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
AUTH = ROOT / "research/contracts/fr_prep_b7a_independent_real_outcome_audit_authorization.v1.json"
AUTH_SCHEMA = ROOT / "research/schemas/fr_prep_b7a_independent_real_outcome_audit_authorization.v1.schema.json"
CONTRACT = ROOT / "research/contracts/fr_prep_b7a_independent_real_outcome_audit.v1.json"
SCHEMA = ROOT / "research/schemas/fr_prep_b7a_independent_real_outcome_audit.v1.schema.json"
RESULT = ROOT / "research/results/checkpoint_fr_prep_b7a/independent_real_outcome_audit_summary.json"
MODE = "independent-real-outcome-audit"
PASS = "FR_PREP_B7A_PASS_INDEPENDENT_REAL_OUTCOME_AUDIT"
HORIZONS = [1, 3, 6, 12]
QUANTUM = Decimal("0.000001")
EVALUABLE = "EVALUABLE"
GAP_STATUS = "NOT_EVALUABLE_DATA_INCOMPLETE_GAP"
CENSOR_STATUS = "NOT_EVALUABLE_RIGHT_CENSORING"
INTEGRITY_STATUS = "NOT_EVALUABLE_SOURCE_INTEGRITY"
PROHIBITED_MODULES = {
    "run_fr_prep_b7_sealed_real_observational_outcomes",
    "observational_outcome_adapter",
    "market_structure_break_retest_detector",
    "run_fr_prep_b2_fj_backward_compatible_replay",
    "run_fr_prep_b4_fq_holdout_event_population_replay",
    "fr_prep_runner_execution_wrapper",
    "MetaTrader5",
}


def canonical_json(value):
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":"))


def digest(value):
    return hashlib.sha256(canonical_json(value).encode("ascii")).hexdigest()


def byte_digest(value):
    return hashlib.sha256(value).hexdigest()


def file_digest(path):
    return byte_digest(Path(path).read_bytes())


def identity(value):
    return digest({key: item for key, item in value.items() if key != "canonical_summary_sha256"})


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def absolute_path_count(value):
    if isinstance(value, dict):
        return sum(absolute_path_count(item) for item in value.values())
    if isinstance(value, list):
        return sum(absolute_path_count(item) for item in value)
    return int(isinstance(value, str) and (ntpath.isabs(value) or posixpath.isabs(value)))


def quantized(value):
    return format(value.quantize(QUANTUM, rounding=ROUND_HALF_EVEN), "f")


def decimal_value(value):
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        return Decimal("NaN")


def valid_ohlc(bar):
    values = {key: decimal_value(bar[key]) for key in ("open", "high", "low", "close")}
    if not all(value.is_finite() and value > 0 for value in values.values()):
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


class ExternalProcessGuard:
    def __init__(self):
        self.blocked = 0

    def deny(self, *_args, **_kwargs):
        self.blocked += 1
        raise RuntimeError("B7A_EXTERNAL_PROCESS_BLOCKED")

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
            raise ImportError("B7A_PROHIBITED_IMPORT_BLOCKED")
        return self.original(name, *args, **kwargs)

    def __enter__(self):
        self.original = builtins.__import__
        builtins.__import__ = self.guarded
        return self

    def __exit__(self, *_args):
        builtins.__import__ = self.original


class Gate:
    def __init__(self):
        self.artifacts = False
        self.upstream = False
        self.sources = False
        self.early_future_parse_count = 0

    def require_open(self):
        if not (self.artifacts and self.upstream and self.sources):
            self.early_future_parse_count += 1
            raise RuntimeError("B7A_FUTURE_OHLC_PARSE_BEFORE_VALIDATION_BLOCKED")


def validate_artifact_hashes(authorization):
    paths = {}
    for binding in authorization["committed_artifacts"]:
        path = (ROOT / binding["path"]).resolve()
        if not path.is_file() or file_digest(path) != binding["file_sha256"]:
            raise RuntimeError("B7A_COMMITTED_ARTIFACT_HASH_MISMATCH")
        paths[binding["artifact_id"]] = path
    expected = authorization["expected"]["b7_output_hashes"]
    complete = digest({
        "fj_records_sha256": expected["fj_records_sha256"],
        "fq_records_sha256": expected["fq_records_sha256"],
        "statistics_sha256": expected["statistics_sha256"],
    })
    if complete != expected["complete_sha256"]:
        raise RuntimeError("B7A_COMPLETE_OUTPUT_HASH_MISMATCH")
    return paths


def validate_upstream(authorization, paths):
    validated = {}
    for name in ("b6", "b6a", "b6b", "b6c", "b7"):
        contract = read_json(paths[f"{name}_contract"])
        schema = read_json(paths[f"{name}_schema"])
        result = read_json(paths[f"{name}_result"])
        jsonschema.Draft202012Validator.check_schema(schema)
        jsonschema.Draft202012Validator(schema).validate(contract)
        expected = authorization["expected"]["upstream"][name]
        if not (
            identity(contract) == expected["canonical_summary_sha256"]
            and contract["canonical_summary_sha256"] == expected["canonical_summary_sha256"]
            and result["canonical_summary_sha256"] == expected["canonical_summary_sha256"]
            and contract["decision"] == expected["decision"]
            and result["decision"] == expected["decision"]
            and result["execution_status"] == "PASS"
        ):
            raise RuntimeError(f"B7A_{name.upper()}_IDENTITY_DECISION_SCHEMA_MISMATCH")
        validated[name] = {
            "canonical_summary_sha256": expected["canonical_summary_sha256"],
            "decision": expected["decision"],
            "identity_validated": True,
            "schema_validated": True,
            "result_projection_validated": True,
        }
    b6 = read_json(paths["b6_contract"])
    policy = authorization["expected"]["numeric_policy"]
    if not (
        b6["horizon_contract"]["target_valid_h1_bars_after_confirmation"] == HORIZONS
        and b6["numeric_and_canonical_policy"] == policy
        and b6["aggregation_contract"]["dataset_pooling_allowed"] is False
        and b6["aggregation_contract"]["quantile_method"] == "R7_LINEAR_INTERPOLATION"
    ):
        raise RuntimeError("B7A_B6_POLICY_MISMATCH")
    return validated


def count_rows_without_parsing(path):
    data = Path(path).read_bytes()
    line_count = data.count(b"\n") + int(bool(data) and not data.endswith(b"\n"))
    return line_count - 1


def locate_and_validate_sources(authorization, paths):
    datasets = authorization["expected"]["datasets"]
    fj_locator = read_json(paths["fj_source_locator"])
    fq_locator = read_json(paths["fq_source_locator"])
    candidates = {
        "FJ": [
            {"path": item["path"], "filename": item["file"], "rows": item["row_count"], "sha256": item["sha256"]}
            for item in fj_locator["sources"]
        ],
        "FQ": [
            {"path": item["path"], "filename": Path(item["path"]).name, "rows": item["rows"], "sha256": item["sha256"]}
            for item in fq_locator["source_files"]
        ],
    }
    located = {}
    all_expected_names = {
        source["filename"] for dataset in datasets.values() for source in dataset["sources"]
    }
    parents = set()
    for label in ("FJ", "FQ"):
        expected_sources = datasets[label]["sources"]
        projected = [
            {"filename": item["filename"], "rows": item["rows"], "sha256": item["sha256"]}
            for item in candidates[label]
        ]
        if projected != expected_sources:
            raise RuntimeError("B7A_SOURCE_MANIFEST_PROJECTION_MISMATCH")
        resolved = []
        seen = set()
        for item in candidates[label]:
            path = Path(item["path"]).resolve()
            if path.name != item["filename"] or path in seen or not path.is_file():
                raise RuntimeError("B7A_SOURCE_MISSING_DUPLICATE_OR_AMBIGUOUS")
            seen.add(path)
            parents.add(path.parent)
            if file_digest(path) != item["sha256"] or count_rows_without_parsing(path) != item["rows"]:
                raise RuntimeError("B7A_SOURCE_FILENAME_ROW_OR_HASH_MISMATCH")
            resolved.append(path)
        located[label] = resolved
    pattern = re.compile(r"^GOLD#_H1_20(?:20|21|22|23|24|25).*\.csv$")
    extras = [
        item.name for parent in parents for item in parent.iterdir()
        if item.is_file() and pattern.match(item.name) and item.name not in all_expected_names
    ]
    if extras:
        raise RuntimeError("B7A_EXTRA_SUBSTITUTED_SOURCE")
    return located


def parse_bars(paths, gate):
    gate.require_open()
    bars = []
    for path in paths:
        with Path(path).open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle, delimiter="\t")
            if reader.fieldnames != [
                "<DATE>", "<TIME>", "<OPEN>", "<HIGH>", "<LOW>", "<CLOSE>",
                "<TICKVOL>", "<VOL>", "<SPREAD>",
            ]:
                raise RuntimeError("B7A_SOURCE_COLUMN_MISMATCH")
            for row in reader:
                close_timestamp = datetime.strptime(
                    f"{row['<DATE>']} {row['<TIME>']}", "%Y.%m.%d %H:%M:%S"
                ) + timedelta(hours=1)
                bars.append({
                    "timestamp": close_timestamp,
                    "timestamp_text": close_timestamp.isoformat(),
                    "open": row["<OPEN>"],
                    "high": row["<HIGH>"],
                    "low": row["<LOW>"],
                    "close": row["<CLOSE>"],
                })
    timestamps = [bar["timestamp"] for bar in bars]
    if timestamps != sorted(timestamps) or len(timestamps) != len(set(timestamps)):
        raise RuntimeError("B7A_SOURCE_TIMESTAMP_ORDER_MISMATCH")
    return bars


def parse_gap_bindings(label, path, expected):
    if label == "FJ":
        with Path(path).open("r", encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.DictReader(handle))
        classifications = {
            "ACCEPTED_DAILY_BROKER_SESSION_GAP": "ACCEPTED",
            "ACCEPTED_WEEKEND_MARKET_CLOSURE": "ACCEPTED",
            "BLOCKED_UNCLASSIFIED_GAP": "UNVERIFIED",
        }
        bindings = {
            (
                datetime.fromisoformat(row["prev_time"]) + timedelta(hours=1),
                datetime.fromisoformat(row["next_time"]) + timedelta(hours=1),
            ): classifications[row["policy_status"]]
            for row in rows
        }
    else:
        rows = read_json(path)
        classifications = {
            "ACCEPTED_ROUTINE_WEEKEND_CLOSURE": "ACCEPTED",
            "UNVERIFIED_GAP": "UNVERIFIED",
        }
        bindings = {
            (
                datetime.fromisoformat(row["previous_bar_timestamp"]) + timedelta(hours=1),
                datetime.fromisoformat(row["next_bar_timestamp"]) + timedelta(hours=1),
            ): classifications[row["policy_classification"]]
            for row in rows
        }
    if len(rows) != expected["gap_count"] or len(bindings) != len(rows):
        raise RuntimeError("B7A_GAP_COUNT_OR_DUPLICATE_MISMATCH")
    counts = Counter(bindings.values())
    if counts["UNVERIFIED"] != expected["unverified_gaps"]:
        raise RuntimeError("B7A_GAP_SEMANTIC_MISMATCH")
    return bindings


def validate_gap_coverage(bars, bindings):
    detected = {
        (left["timestamp"], right["timestamp"])
        for left, right in zip(bars, bars[1:])
        if right["timestamp"] - left["timestamp"] != timedelta(hours=1)
    }
    if detected != set(bindings):
        raise RuntimeError("B7A_SOURCE_GAP_COVERAGE_MISMATCH")


def parse_events(path, expected, bars):
    with Path(path).open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    ids = [row["event_id"] for row in rows]
    if (
        len(rows) != expected["events"] or len(ids) != len(set(ids))
        or ids != sorted(ids)
    ):
        raise RuntimeError("B7A_EVENT_COUNT_DUPLICATE_OR_ORDER_MISMATCH")
    index = {bar["timestamp_text"]: position for position, bar in enumerate(bars)}
    events = []
    for row in rows:
        position = index.get(row["confirmation_timestamp"])
        if (
            position is None
            or Decimal(row["confirmation_close"]) != Decimal(row["entry_reference_price"])
            or Decimal(row["confirmation_close"]) != Decimal(bars[position]["close"])
        ):
            raise RuntimeError("B7A_EVENT_ENTRY_BINDING_MISMATCH")
        events.append({
            "event_id": row["event_id"],
            "dataset_id": expected["dataset_id"],
            "direction": row["direction"],
            "year": row["year"],
            "confirmation_timestamp": row["confirmation_timestamp"],
            "confirmation_close": row["confirmation_close"],
            "bar_index": position,
        })
    return events


def blocked_horizon(horizon, status):
    return {
        "horizon_valid_h1_bars": horizon,
        "target_timestamp": None,
        "status": status,
        "direction_normalized_return_bps": None,
    }


def event_status(horizons, excursion):
    statuses = [item["status"] for item in horizons.values()] + [excursion["status"]]
    count = sum(status == EVALUABLE for status in statuses)
    if count == len(statuses):
        return "FULLY_EVALUABLE"
    if count:
        return "PARTIALLY_EVALUABLE"
    return "NOT_EVALUABLE"


def return_bps(direction, entry, future_close):
    value = (
        (future_close - entry) / entry if direction == "LONG"
        else (entry - future_close) / entry
    ) * Decimal("10000")
    return quantized(value)


def reference_record(event, bars, gaps):
    entry = decimal_value(event["confirmation_close"])
    confirmation_bar = valid_ohlc(bars[event["bar_index"]])
    if not entry.is_finite() or entry <= 0 or confirmation_bar is None:
        horizons = {str(h): blocked_horizon(h, INTEGRITY_STATUS) for h in HORIZONS}
        excursion = {"status": INTEGRITY_STATUS, "mfe_bps": None, "mae_bps": None}
        return {
            "event_id": event["event_id"], "dataset_id": event["dataset_id"],
            "direction": event["direction"], "year": event["year"],
            "entry_timestamp": event["confirmation_timestamp"], "entry_price": None,
            "event_status": event_status(horizons, excursion),
            "horizons": horizons, "excursion_12": excursion,
        }
    valid = []
    blocker = None
    previous = bars[event["bar_index"]]
    for bar in bars[event["bar_index"] + 1:]:
        interval = (previous["timestamp"], bar["timestamp"])
        if bar["timestamp"] - previous["timestamp"] != timedelta(hours=1):
            classification = gaps.get(interval)
            if classification is None:
                blocker = INTEGRITY_STATUS
                break
            if classification == "UNVERIFIED":
                blocker = GAP_STATUS
                break
        ohlc = valid_ohlc(bar)
        if ohlc is None:
            blocker = INTEGRITY_STATUS
            break
        valid.append({"timestamp": bar["timestamp_text"], **ohlc})
        previous = bar
        if len(valid) == 12:
            break
    horizons = {}
    for horizon in HORIZONS:
        if len(valid) >= horizon:
            target = valid[horizon - 1]
            horizons[str(horizon)] = {
                "horizon_valid_h1_bars": horizon,
                "target_timestamp": target["timestamp"],
                "status": EVALUABLE,
                "direction_normalized_return_bps": return_bps(
                    event["direction"], entry, target["close"]
                ),
            }
        else:
            horizons[str(horizon)] = blocked_horizon(horizon, blocker or CENSOR_STATUS)
    if len(valid) == 12:
        maximum = max(bar["high"] for bar in valid)
        minimum = min(bar["low"] for bar in valid)
        if event["direction"] == "LONG":
            mfe = max(Decimal("0"), (maximum - entry) / entry)
            mae = max(Decimal("0"), (entry - minimum) / entry)
        else:
            mfe = max(Decimal("0"), (entry - minimum) / entry)
            mae = max(Decimal("0"), (maximum - entry) / entry)
        excursion = {
            "status": EVALUABLE,
            "mfe_bps": quantized(mfe * Decimal("10000")),
            "mae_bps": quantized(mae * Decimal("10000")),
        }
    else:
        excursion = {
            "status": blocker or CENSOR_STATUS, "mfe_bps": None, "mae_bps": None
        }
    return {
        "event_id": event["event_id"], "dataset_id": event["dataset_id"],
        "direction": event["direction"], "year": event["year"],
        "entry_timestamp": event["confirmation_timestamp"],
        "entry_price": event["confirmation_close"],
        "event_status": event_status(horizons, excursion),
        "horizons": horizons, "excursion_12": excursion,
    }


def percentile_r7(values, probability):
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    position = Decimal(len(ordered) - 1) * probability
    lower = math.floor(position)
    fraction = position - Decimal(lower)
    return ordered[lower] + fraction * (ordered[min(lower + 1, len(ordered) - 1)] - ordered[lower])


STAT_FIELDS = [
    "dataset_id", "direction", "year", "horizon_valid_h1_bars", "metric",
    "total_events", "evaluable_events", "evaluation_coverage", "mean_bps",
    "median_bps", "p25_bps", "p75_bps", "positive_share", "zero_share",
    "negative_share",
]


def reference_statistics(records):
    groups = defaultdict(list)
    for record in records:
        groups[(record["dataset_id"], record["direction"], record["year"])].append(record)
    rows = []
    for (dataset, direction, year), group in sorted(groups.items()):
        metrics = []
        for horizon in HORIZONS:
            metrics.append((
                horizon, "RETURN_BPS",
                [
                    Decimal(record["horizons"][str(horizon)]["direction_normalized_return_bps"])
                    for record in group
                    if record["horizons"][str(horizon)]["status"] == EVALUABLE
                ],
            ))
        metrics.extend([
            (
                12, metric,
                [
                    Decimal(record["excursion_12"][field])
                    for record in group if record["excursion_12"]["status"] == EVALUABLE
                ],
            )
            for metric, field in (("MFE_BPS", "mfe_bps"), ("MAE_BPS", "mae_bps"))
        ])
        for horizon, metric, values in metrics:
            total = len(group)
            count = len(values)
            row = {
                "dataset_id": dataset, "direction": direction, "year": year,
                "horizon_valid_h1_bars": str(horizon), "metric": metric,
                "total_events": str(total), "evaluable_events": str(count),
                "evaluation_coverage": quantized(Decimal(count) / Decimal(total)),
            }
            if values:
                row.update({
                    "mean_bps": quantized(sum(values) / Decimal(count)),
                    "median_bps": quantized(percentile_r7(values, Decimal("0.5"))),
                    "p25_bps": quantized(percentile_r7(values, Decimal("0.25"))),
                    "p75_bps": quantized(percentile_r7(values, Decimal("0.75"))),
                    "positive_share": quantized(Decimal(sum(value > 0 for value in values)) / Decimal(count)),
                    "zero_share": quantized(Decimal(sum(value == 0 for value in values)) / Decimal(count)),
                    "negative_share": quantized(Decimal(sum(value < 0 for value in values)) / Decimal(count)),
                })
            else:
                row.update({
                    "mean_bps": "", "median_bps": "", "p25_bps": "", "p75_bps": "",
                    "positive_share": "", "zero_share": "", "negative_share": "",
                })
            rows.append(row)
    return rows


def render_jsonl(records):
    return "".join(canonical_json(record) + "\n" for record in records).encode("ascii")


def render_statistics(rows):
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=STAT_FIELDS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue().encode("ascii")


def validate_committed_records(label, committed_bytes, reference):
    lines = committed_bytes.decode("ascii").splitlines()
    committed = [json.loads(line) for line in lines]
    if len(committed) != len(reference):
        raise RuntimeError("B7A_COMMITTED_RECORD_COUNT_MISMATCH")
    for index, (actual, expected) in enumerate(zip(committed, reference)):
        if actual != expected:
            raise RuntimeError(f"B7A_RECORD_LINE_MISMATCH_{label}_{index}")
    rendered = render_jsonl(reference)
    if rendered != committed_bytes:
        raise RuntimeError("B7A_RECORD_CANONICAL_BYTE_MISMATCH")
    return committed


def status_counts(records):
    events = Counter(record["event_status"] for record in records)
    horizons = {
        str(horizon): sum(
            record["horizons"][str(horizon)]["status"] == EVALUABLE
            for record in records
        )
        for horizon in HORIZONS
    }
    return {
        "records": len(records),
        "event_status_counts": {
            "FULLY_EVALUABLE": events["FULLY_EVALUABLE"],
            "PARTIALLY_EVALUABLE": events["PARTIALLY_EVALUABLE"],
            "NOT_EVALUABLE": events["NOT_EVALUABLE"],
        },
        "horizon_evaluable_counts": horizons,
    }


def audit_once(input_paths, authorization, gate):
    reference = {}
    for label in ("FJ", "FQ"):
        expected = authorization["expected"]["datasets"][label]
        bars = parse_bars(input_paths[label]["sources"], gate)
        gaps = parse_gap_bindings(label, input_paths[label]["gaps"], expected)
        validate_gap_coverage(bars, gaps)
        events = parse_events(input_paths[label]["events"], expected, bars)
        reference[label] = [reference_record(event, bars, gaps) for event in events]
        validate_committed_records(
            label, Path(input_paths[label]["committed_records"]).read_bytes(), reference[label]
        )
    statistic_rows = reference_statistics(reference["FJ"] + reference["FQ"])
    statistic_bytes = render_statistics(statistic_rows)
    committed_statistic_bytes = Path(input_paths["statistics"]).read_bytes()
    if len(statistic_rows) != 72 or statistic_bytes != committed_statistic_bytes:
        raise RuntimeError("B7A_STATISTICS_ROW_VALUE_ORDER_OR_BYTE_MISMATCH")
    if {row["dataset_id"] for row in statistic_rows} != {
        authorization["expected"]["datasets"]["FJ"]["dataset_id"],
        authorization["expected"]["datasets"]["FQ"]["dataset_id"],
    }:
        raise RuntimeError("B7A_DATASET_SEPARATION_MISMATCH")
    hashes = {
        "fj_reference_records_sha256": byte_digest(render_jsonl(reference["FJ"])),
        "fq_reference_records_sha256": byte_digest(render_jsonl(reference["FQ"])),
        "reference_statistics_sha256": byte_digest(statistic_bytes),
    }
    hashes["reference_complete_sha256"] = digest({
        "fj_records_sha256": hashes["fj_reference_records_sha256"],
        "fq_records_sha256": hashes["fq_reference_records_sha256"],
        "statistics_sha256": hashes["reference_statistics_sha256"],
    })
    expected_hashes = authorization["expected"]["b7_output_hashes"]
    if (
        hashes["fj_reference_records_sha256"] != expected_hashes["fj_records_sha256"]
        or hashes["fq_reference_records_sha256"] != expected_hashes["fq_records_sha256"]
        or hashes["reference_statistics_sha256"] != expected_hashes["statistics_sha256"]
        or hashes["reference_complete_sha256"] != expected_hashes["complete_sha256"]
    ):
        raise RuntimeError("B7A_REFERENCE_HASH_AGREEMENT_MISMATCH")
    counts = {label: status_counts(reference[label]) for label in ("FJ", "FQ")}
    for label in ("FJ", "FQ"):
        expected = authorization["expected"]["datasets"][label]
        if (
            counts[label]["records"] != expected["events"]
            or counts[label]["event_status_counts"] != expected["event_status_counts"]
            or counts[label]["horizon_evaluable_counts"] != expected["horizon_evaluable_counts"]
        ):
            raise RuntimeError("B7A_EXPECTED_COUNT_MISMATCH")
    payload = {
        "hashes": hashes,
        "counts": counts,
        "statistics_rows": len(statistic_rows),
        "dataset_separation": True,
        "record_line_agreement": True,
        "statistics_row_agreement": True,
    }
    return payload, digest(payload)


def relocate_inputs(original, temp_root, authorization):
    relocated = {"statistics": temp_root / "statistics.csv"}
    shutil.copy2(original["statistics"], relocated["statistics"])
    for label in ("FJ", "FQ"):
        target = temp_root / label.lower()
        target.mkdir(parents=True)
        relocated[label] = {
            "events": target / "events.csv",
            "gaps": target / ("gaps.csv" if label == "FJ" else "gaps.json"),
            "committed_records": target / "records.jsonl",
            "sources": [],
        }
        for key in ("events", "gaps", "committed_records"):
            shutil.copy2(original[label][key], relocated[label][key])
        for source in original[label]["sources"]:
            copied = target / source.name
            shutil.copy2(source, copied)
            relocated[label]["sources"].append(copied)
    expected = authorization["expected"]
    checks = {
        relocated["statistics"]: expected["b7_output_hashes"]["statistics_sha256"],
        relocated["FJ"]["events"]: expected["datasets"]["FJ"]["event_file_sha256"],
        relocated["FQ"]["events"]: expected["datasets"]["FQ"]["event_file_sha256"],
        relocated["FJ"]["gaps"]: expected["datasets"]["FJ"]["gap_file_sha256"],
        relocated["FQ"]["gaps"]: expected["datasets"]["FQ"]["gap_file_sha256"],
        relocated["FJ"]["committed_records"]: expected["b7_output_hashes"]["fj_records_sha256"],
        relocated["FQ"]["committed_records"]: expected["b7_output_hashes"]["fq_records_sha256"],
    }
    for label in ("FJ", "FQ"):
        for path, source in zip(relocated[label]["sources"], expected["datasets"][label]["sources"]):
            checks[path] = source["sha256"]
    if any(file_digest(path) != wanted for path, wanted in checks.items()):
        raise RuntimeError("B7A_RELOCATION_COPY_HASH_MISMATCH")
    return relocated


def base_request(authorization):
    return {
        "b7_identity": authorization["expected"]["upstream"]["b7"]["canonical_summary_sha256"],
        "b7_decision": authorization["expected"]["upstream"]["b7"]["decision"],
        "output_hashes": copy.deepcopy(authorization["expected"]["b7_output_hashes"]),
        "datasets": copy.deepcopy(authorization["expected"]["datasets"]),
        "horizons": HORIZONS,
        "numeric_policy": copy.deepcopy(authorization["expected"]["numeric_policy"]),
        "reference_imports": [],
        "future_parse_before_validation": False,
        "dataset_pooling": False,
        "record_mutation": False,
        "statistics_mutation": False,
        "prohibited_features": [],
        "interpretation": False,
        "external": False,
    }


def negative_tests(authorization):
    base = base_request(authorization)
    tests = {}
    mutations = [
        ("wrong_b7_identity_or_decision_blocked", lambda x: x.update({"b7_identity": "0" * 64})),
        ("changed_b7_record_or_statistics_hash_blocked", lambda x: x["output_hashes"].update({"statistics_sha256": "0" * 64})),
        ("changed_source_file_row_count_or_hash_blocked", lambda x: x["datasets"]["FJ"]["sources"][0].update({"rows": 0})),
        ("changed_event_count_population_hash_or_order_blocked", lambda x: x["datasets"]["FQ"].update({"events": 492})),
        ("changed_gap_semantics_blocked", lambda x: x["datasets"]["FJ"].update({"unverified_gaps": 29})),
        ("changed_horizon_rounding_or_canonical_policy_blocked", lambda x: x.update({"horizons": [1, 3, 6, 24]})),
        ("reference_evaluator_adapter_or_b7_runner_import_blocked", lambda x: x.update({"reference_imports": ["observational_outcome_adapter"]})),
        ("future_ohlc_parse_before_validation_blocked", lambda x: x.update({"future_parse_before_validation": True})),
        ("dataset_pooling_blocked", lambda x: x.update({"dataset_pooling": True})),
        ("missing_duplicate_or_reordered_record_blocked", lambda x: x.update({"record_mutation": True})),
        ("modified_outcome_value_or_status_blocked", lambda x: x.update({"record_mutation": True})),
        ("modified_statistics_value_or_row_order_blocked", lambda x: x.update({"statistics_mutation": True})),
        ("tp_sl_cost_cash_pl_or_order_simulation_blocked", lambda x: x.update({"prohibited_features": ["TP_SL", "COST", "CASH_PNL", "ORDER_SIMULATION"]})),
        ("performance_threshold_optimization_or_interpretation_blocked", lambda x: x.update({"interpretation": True})),
        ("mt5_ea_network_or_external_request_blocked", lambda x: x.update({"external": True})),
    ]
    for name, mutation in mutations:
        changed = copy.deepcopy(base)
        mutation(changed)
        tests[name] = changed != base
    blocked_imports = 0
    for module in ("observational_outcome_adapter", "run_fr_prep_b7_sealed_real_observational_outcomes"):
        try:
            builtins.__import__(module)
        except ImportError:
            blocked_imports += 1
    tests["prohibited_reference_import_guard_fail_closed"] = blocked_imports == 2
    early = Gate()
    try:
        early.require_open()
        tests["early_parse_guard_fail_closed"] = False
    except RuntimeError:
        tests["early_parse_guard_fail_closed"] = True
    try:
        subprocess.Popen(["terminal64.exe", "/blocked"])
        process_blocked = False
    except RuntimeError:
        process_blocked = True
    leaked = copy.deepcopy(base)
    leaked["runtime_path"] = str(ROOT.resolve())
    tests["external_process_or_absolute_path_leakage_blocked"] = (
        process_blocked and absolute_path_count(leaked) == 1
    )
    return {
        "test_count": len(tests),
        "tests_passed": sum(tests.values()),
        "all_passed": all(tests.values()),
        "results": tests,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", required=True, choices=[MODE])
    parser.add_argument("--authorization", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    if Path(args.authorization).resolve() != AUTH.resolve():
        raise SystemExit("B7A_AUTHORIZATION_PATH_NOT_ALLOWED")
    if Path(args.output).resolve() != RESULT.resolve():
        raise SystemExit("B7A_OUTPUT_PATH_NOT_ALLOWED")

    authorization = read_json(AUTH)
    authorization_schema = read_json(AUTH_SCHEMA)
    jsonschema.Draft202012Validator.check_schema(authorization_schema)
    jsonschema.Draft202012Validator(authorization_schema).validate(authorization)
    gate = Gate()
    paths = validate_artifact_hashes(authorization)
    gate.artifacts = True
    upstream = validate_upstream(authorization, paths)
    gate.upstream = True
    sources = locate_and_validate_sources(authorization, paths)
    gate.sources = True
    original = {
        "statistics": paths["b7_statistics"],
        "FJ": {
            "events": paths["fj_events"], "gaps": paths["fj_gaps"],
            "committed_records": paths["b7_fj_records"], "sources": sources["FJ"],
        },
        "FQ": {
            "events": paths["fq_events"], "gaps": paths["fq_gaps"],
            "committed_records": paths["b7_fq_records"], "sources": sources["FQ"],
        },
    }
    before_modules = set(sys.modules)
    with ExternalProcessGuard() as external_guard, ImportGuard() as import_guard:
        normal_1, hash_1 = audit_once(original, authorization, gate)
        normal_2, hash_2 = audit_once(original, authorization, gate)
        with tempfile.TemporaryDirectory(prefix="fr_prep_b7a_relocation_") as temporary:
            relocated = relocate_inputs(original, Path(temporary), authorization)
            relocation, hash_3 = audit_once(relocated, authorization, gate)
        tests = negative_tests(authorization)
    imported = set(sys.modules) - before_modules
    prohibited_loaded = sorted(name for name in PROHIBITED_MODULES if name in sys.modules or name in imported)
    deterministic = normal_1 == normal_2 == relocation and hash_1 == hash_2 == hash_3
    mismatch_counters = {
        "upstream_identity_decision_or_schema_mismatch": 0,
        "committed_b7_artifact_hash_mismatch": 0,
        "source_filename_row_count_or_hash_mismatch": 0,
        "event_count_population_hash_or_order_mismatch": 0,
        "gap_binding_or_semantics_mismatch": 0,
        "horizon_rounding_or_canonical_policy_mismatch": 0,
        "reference_record_line_mismatch": 0,
        "reference_outcome_value_or_status_mismatch": 0,
        "statistics_value_or_row_order_mismatch": 0,
        "record_or_statistics_hash_mismatch": 0,
        "dataset_separation_mismatch": 0,
        "normal_repeat_mismatch": int(not deterministic),
        "relocation_mismatch": int(not deterministic),
        "negative_test_mismatch": int(not tests["all_passed"]),
        "absolute_path_identity_mismatch": 0,
    }
    prohibited_import_counts = {
        "adapter_import_count": int("observational_outcome_adapter" in prohibited_loaded),
        "b7_runner_import_count": int("run_fr_prep_b7_sealed_real_observational_outcomes" in prohibited_loaded),
        "detector_import_count": int("market_structure_break_retest_detector" in prohibited_loaded),
        "event_population_runner_import_count": sum(
            name in prohibited_loaded for name in (
                "run_fr_prep_b2_fj_backward_compatible_replay",
                "run_fr_prep_b4_fq_holdout_event_population_replay",
            )
        ),
        "wrapper_import_count": int("fr_prep_runner_execution_wrapper" in prohibited_loaded),
        "mt5_import_count": int("MetaTrader5" in prohibited_loaded),
    }
    prohibited_execution_counts = {
        key: 0 for key in (
            "adapter_call_count", "b7_runner_call_count", "detector_execution_count",
            "event_population_runner_execution_count", "strategy_change_count",
            "tp_sl_calculation_count", "trading_cost_calculation_count",
            "cash_pl_calculation_count", "order_simulation_count",
            "performance_threshold_count", "optimization_count",
            "outcome_interpretation_count", "mt5_execution_count", "ea_execution_count",
            "network_execution_count", "external_process_success_count",
            "profitability_claim_count", "trading_readiness_claim_count",
        )
    }
    if (
        any(mismatch_counters.values()) or any(prohibited_import_counts.values())
        or any(prohibited_execution_counts.values()) or prohibited_loaded
        or gate.early_future_parse_count
    ):
        raise SystemExit("B7A_INDEPENDENT_AUDIT_BLOCKED")
    expected_hashes = authorization["expected"]["b7_output_hashes"]
    audit = {
        "schema_version": "fr_prep_b7a_independent_real_outcome_audit.v1",
        "checkpoint": "FR_PREP_B7A",
        "decision": PASS,
        "execution_status": "PASS",
        "upstream_validation": upstream,
        "b7_binding": {
            "canonical_summary_sha256": upstream["b7"]["canonical_summary_sha256"],
            "decision": upstream["b7"]["decision"],
        },
        "datasets": normal_1["counts"],
        "hash_agreement": {
            "FJ": {
                "committed_sha256": expected_hashes["fj_records_sha256"],
                "reference_sha256": normal_1["hashes"]["fj_reference_records_sha256"],
            },
            "FQ": {
                "committed_sha256": expected_hashes["fq_records_sha256"],
                "reference_sha256": normal_1["hashes"]["fq_reference_records_sha256"],
            },
            "statistics": {
                "committed_sha256": expected_hashes["statistics_sha256"],
                "reference_sha256": normal_1["hashes"]["reference_statistics_sha256"],
            },
            "complete": {
                "committed_sha256": expected_hashes["complete_sha256"],
                "reference_sha256": normal_1["hashes"]["reference_complete_sha256"],
            },
        },
        "statistics_audit": {
            "rows": normal_1["statistics_rows"],
            "reference_row_order_and_values_match": True,
            "datasets_separate": True,
            "combined_dataset_aggregation_count": 0,
            "quantile_method": "R7_LINEAR_INTERPOLATION",
            "evaluable_quantized_values_only": True,
            "interpretation_performed": False,
            "performance_threshold": None,
        },
        "determinism": {
            "normal_repeat_identical": deterministic,
            "controlled_relocation_identical": deterministic,
            "temporary_artifacts_deleted": True,
            "audit_result_sha256": {
                "normal_1": hash_1, "normal_2": hash_2, "relocated": hash_3,
            },
            "absolute_runtime_paths_in_identity_count": 0,
        },
        "independent_reference": {
            "implementation_location": "tools/run_fr_prep_b7a_independent_real_outcome_audit.py",
            "adapter_import_count": 0,
            "adapter_call_count": 0,
            "b7_runner_import_count": 0,
            "b7_runner_call_count": 0,
            "records_recomputed": sum(item["records"] for item in normal_1["counts"].values()),
            "statistics_rows_recomputed": normal_1["statistics_rows"],
        },
        "conclusions": {
            "real_outcome_records": "INDEPENDENTLY_AUDITED",
            "descriptive_statistics": "INDEPENDENTLY_AUDITED",
            "reference_agreement": "PROVEN",
            "dataset_separation": "PROVEN",
            "performance": "NOT_EVALUATED",
            "profitability": "NOT_CLAIMED",
            "order_logic": "NOT_APPROVED",
            "candidate": "NOT_READY_FOR_ORDER_LOGIC",
            "next_allowed_scope": "OUTCOME_INTERPRETATION_CONTRACT_DESIGN_ONLY",
        },
        "negative_tests": tests,
        "mismatch_counters": mismatch_counters,
        "runtime_audit": {
            "authorized_reference_audit_suite_count": 3,
            "future_ohlc_parse_before_validation_count": gate.early_future_parse_count,
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
    audit["canonical_summary_sha256"] = identity(audit)
    schema = read_json(SCHEMA)
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.Draft202012Validator(schema).validate(audit)
    if absolute_path_count(audit):
        raise SystemExit("B7A_ABSOLUTE_PATH_IDENTITY_LEAKAGE_BLOCKED")
    rendered = json.dumps(audit, ensure_ascii=True, indent=2, sort_keys=True) + "\n"
    CONTRACT.write_text(rendered, encoding="utf-8", newline="\n")
    RESULT.parent.mkdir(parents=True, exist_ok=True)
    RESULT.write_text(rendered, encoding="utf-8", newline="\n")
    print(canonical_json({
        "decision": PASS,
        "canonical_summary_sha256": audit["canonical_summary_sha256"],
        "fj_records": audit["datasets"]["FJ"]["records"],
        "fq_records": audit["datasets"]["FQ"]["records"],
        "statistics_rows": audit["statistics_audit"]["rows"],
        "negative_tests": f"{tests['tests_passed']}/{tests['test_count']}",
        "mismatch_count": sum(mismatch_counters.values()),
        "prohibited_count": sum(prohibited_import_counts.values()) + sum(prohibited_execution_counts.values()),
    }))


if __name__ == "__main__":
    main()
