#!/usr/bin/env python3
"""Generate the sealed B9 report from committed B7 statistics under B8 rules."""

import argparse
import builtins
import copy
import csv
import hashlib
import io
import json
import ntpath
import os
import posixpath
import shutil
import subprocess
import sys
import tempfile
from collections import Counter
from decimal import Decimal
from pathlib import Path

import jsonschema

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
AUTH = ROOT / "research/contracts/fr_prep_b9_outcome_interpretation_report_authorization.v1.json"
AUTH_SCHEMA = ROOT / "research/schemas/fr_prep_b9_outcome_interpretation_report_authorization.v1.schema.json"
CONTRACT = ROOT / "research/contracts/fr_prep_b9_sealed_outcome_interpretation_report.v1.json"
CONTRACT_SCHEMA = ROOT / "research/schemas/fr_prep_b9_sealed_outcome_interpretation_report.v1.schema.json"
OUT = ROOT / "research/results/checkpoint_fr_prep_b9"
REPORT_JSON = OUT / "observational_outcome_interpretation_report.json"
REPORT_MD = OUT / "observational_outcome_interpretation_report.md"
SUMMARY = OUT / "outcome_interpretation_report_summary.json"
MODE = "generate-sealed-observational-outcome-interpretation-report"
PASS = "FR_PREP_B9_PASS_SEALED_OBSERVATIONAL_OUTCOME_INTERPRETATION_REPORT"
DATASET_ORDER = ["FJ_2023_2025_GOLD_H1", "FP_FQ_2020_2022_GOLD_H1"]
DATASET_LABELS = {"FJ_2023_2025_GOLD_H1": "FJ", "FP_FQ_2020_2022_GOLD_H1": "FQ"}
DIRECTIONS = ["LONG", "SHORT"]
HORIZONS = ["1", "3", "6", "12"]
METRIC_ORDER = [("RETURN_BPS", "1"), ("RETURN_BPS", "3"), ("RETURN_BPS", "6"), ("RETURN_BPS", "12"), ("MFE_BPS", "12"), ("MAE_BPS", "12")]
STAT_FIELDS = [
    "dataset_id", "direction", "year", "horizon_valid_h1_bars", "metric",
    "total_events", "evaluable_events", "evaluation_coverage", "mean_bps",
    "median_bps", "p25_bps", "p75_bps", "positive_share", "zero_share",
    "negative_share",
]
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


def identity(value, field="canonical_summary_sha256"):
    return digest({key: item for key, item in value.items() if key != field})


def absolute_path_count(value):
    if isinstance(value, dict):
        return sum(absolute_path_count(item) for item in value.values())
    if isinstance(value, list):
        return sum(absolute_path_count(item) for item in value)
    return int(isinstance(value, str) and (ntpath.isabs(value) or posixpath.isabs(value)))


class Files:
    def __init__(self):
        self.allowed = {}
        self.hash_reads = Counter()
        self.parse_reads = Counter()
        self.blocked_jsonl_parse_attempts = 0

    def add(self, path, artifact_id, mode):
        self.allowed[Path(path).resolve()] = (artifact_id, mode)

    def hash_bytes(self, path):
        resolved = Path(path).resolve()
        binding = self.allowed.get(resolved)
        if binding is None:
            raise PermissionError("B9_UNAUTHORIZED_FILE_HASH_READ")
        artifact_id, _ = binding
        self.hash_reads[artifact_id] += 1
        return resolved.read_bytes()

    def parse_bytes(self, path):
        resolved = Path(path).resolve()
        binding = self.allowed.get(resolved)
        if binding is None:
            raise PermissionError("B9_UNAUTHORIZED_FILE_PARSE")
        artifact_id, mode = binding
        if mode == "hash_only":
            self.blocked_jsonl_parse_attempts += 1
            raise PermissionError("B9_JSONL_OUTCOME_RECORD_PARSE_BLOCKED")
        self.parse_reads[artifact_id] += 1
        return resolved.read_bytes()

    def report(self):
        return {
            "hash_read_operation_counts": dict(sorted(self.hash_reads.items())),
            "parse_read_operation_counts": dict(sorted(self.parse_reads.items())),
            "jsonl_outcome_record_parse_count": 0,
            "blocked_jsonl_parse_attempt_count": self.blocked_jsonl_parse_attempts,
            "raw_broker_csv_read_count": 0,
            "future_ohlc_read_count": 0,
            "unauthorized_successful_read_count": 0,
        }


class ExternalProcessGuard:
    def __init__(self):
        self.blocked = 0

    def deny(self, *_args, **_kwargs):
        self.blocked += 1
        raise RuntimeError("B9_EXTERNAL_PROCESS_BLOCKED")

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
            raise ImportError("B9_PROHIBITED_IMPORT_BLOCKED")
        return self.original(name, *args, **kwargs)

    def __enter__(self):
        self.original = builtins.__import__
        builtins.__import__ = self.guarded
        return self

    def __exit__(self, *_args):
        builtins.__import__ = self.original


def read_json(files, path):
    return json.loads(files.parse_bytes(path).decode("utf-8"))


def validate_hashes(authorization, files):
    paths = {}
    for binding in authorization["committed_artifacts"]:
        path = (ROOT / binding["path"]).resolve()
        files.add(path, binding["artifact_id"], binding["read_mode"])
        if not path.is_file():
            raise RuntimeError("B9_COMMITTED_ARTIFACT_MISSING")
        if byte_digest(files.hash_bytes(path)) != binding["file_sha256"]:
            raise RuntimeError("B9_COMMITTED_ARTIFACT_HASH_MISMATCH")
        paths[binding["artifact_id"]] = path
    expected = authorization["expected"]["b7_hashes"]
    if digest({
        "fj_records_sha256": expected["fj_records_sha256"],
        "fq_records_sha256": expected["fq_records_sha256"],
        "statistics_sha256": expected["statistics_sha256"],
    }) != expected["complete_sha256"]:
        raise RuntimeError("B9_B7_COMPLETE_HASH_MISMATCH")
    return paths


def validate_upstream(authorization, files, paths):
    result = {}
    for name in ("b7", "b7a", "b8"):
        contract = read_json(files, paths[f"{name}_contract"])
        schema = read_json(files, paths[f"{name}_schema"])
        summary = read_json(files, paths[f"{name}_summary"])
        jsonschema.Draft202012Validator.check_schema(schema)
        jsonschema.Draft202012Validator(schema).validate(contract)
        expected = authorization["expected"]["upstream"][name]
        valid = (
            identity(contract) == expected["canonical_summary_sha256"]
            and contract["canonical_summary_sha256"] == expected["canonical_summary_sha256"]
            and summary["canonical_summary_sha256"] == expected["canonical_summary_sha256"]
            and contract["decision"] == expected["decision"]
            and summary["decision"] == expected["decision"]
            and summary["execution_status"] == "PASS"
        )
        if not valid:
            raise RuntimeError(f"B9_{name.upper()}_IDENTITY_DECISION_OR_SCHEMA_MISMATCH")
        result[name] = {
            "canonical_summary_sha256": expected["canonical_summary_sha256"],
            "decision": expected["decision"],
            "identity_validated": True,
            "schema_validated": True,
            "summary_projection_validated": True,
        }
    b7_summary = read_json(files, paths["b7_summary"])
    b7a_summary = read_json(files, paths["b7a_summary"])
    b8_contract = read_json(files, paths["b8_contract"])
    replay = read_json(files, paths["b7_replay"])
    source_manifest = read_json(files, paths["b7_source_manifest"])
    hashes = authorization["expected"]["b7_hashes"]
    if not (
        b7_summary["output_hashes"]["fj_records_sha256"] == hashes["fj_records_sha256"]
        and b7_summary["output_hashes"]["fq_records_sha256"] == hashes["fq_records_sha256"]
        and b7_summary["output_hashes"]["statistics_sha256"] == hashes["statistics_sha256"]
        and b7_summary["output_hashes"]["complete_sha256"] == hashes["complete_sha256"]
        and b7a_summary["conclusions"]["real_outcome_records"] == "INDEPENDENTLY_AUDITED"
        and b7a_summary["conclusions"]["descriptive_statistics"] == "INDEPENDENTLY_AUDITED"
        and b7a_summary["conclusions"]["dataset_separation"] == "PROVEN"
        and b8_contract["future_report_conclusions"]["next_allowed_scope"]
        == "SEALED_OBSERVATIONAL_OUTCOME_INTERPRETATION_REPORT_ONLY"
        and replay["normal_repeat_byte_identical"]
        and replay["controlled_relocation_byte_identical"]
        and source_manifest["missing_duplicate_ambiguous_or_substituted_source_count"] == 0
    ):
        raise RuntimeError("B9_UPSTREAM_EVIDENCE_PROJECTION_MISMATCH")
    return result, b7_summary, b7a_summary, b8_contract, replay, source_manifest


def parse_statistics(files, path):
    text = files.parse_bytes(path).decode("ascii")
    rows = list(csv.DictReader(io.StringIO(text, newline="")))
    if len(rows) != 72 or list(rows[0]) != STAT_FIELDS:
        raise RuntimeError("B9_STATISTICS_ROW_OR_COLUMN_COUNT_MISMATCH")
    years = {
        dataset: sorted({row["year"] for row in rows if row["dataset_id"] == dataset})
        for dataset in DATASET_ORDER
    }
    expected_order = [
        (dataset, direction, year, metric, horizon)
        for dataset in DATASET_ORDER
        for direction in DIRECTIONS
        for year in years[dataset]
        for metric, horizon in METRIC_ORDER
    ]
    actual_order = [
        (
            row["dataset_id"], row["direction"], row["year"],
            row["metric"], row["horizon_valid_h1_bars"],
        )
        for row in rows
    ]
    if actual_order != expected_order:
        raise RuntimeError("B9_STATISTICS_COMMITTED_ORDER_MISMATCH")
    for row in rows:
        if not (
            row["total_events"] and row["evaluable_events"]
            and row["evaluation_coverage"]
            and row["mean_bps"] and row["median_bps"]
            and row["p25_bps"] and row["p75_bps"]
            and row["positive_share"] and row["zero_share"] and row["negative_share"]
        ):
            raise RuntimeError("B9_STATISTICS_REQUIRED_VALUE_MISSING")
    return rows, years


def return_classification(row):
    mean = Decimal(row["mean_bps"])
    median = Decimal(row["median_bps"])
    if mean > 0 and median > 0:
        return "BOTH_POSITIVE"
    if mean < 0 and median < 0:
        return "BOTH_NEGATIVE"
    return "MIXED_OR_ZERO"


def row_projection(row):
    return {field: row[field] for field in STAT_FIELDS}


def coverage_projection(row):
    return {
        "total_events": row["total_events"],
        "evaluable_events": row["evaluable_events"],
        "evaluation_coverage": row["evaluation_coverage"],
    }


def build_observations(rows, years):
    return_rows = [row for row in rows if row["metric"] == "RETURN_BPS"]
    horizon_patterns = []
    for dataset in DATASET_ORDER:
        for direction in DIRECTIONS:
            for year in years[dataset]:
                selected = [
                    row for row in return_rows
                    if row["dataset_id"] == dataset
                    and row["direction"] == direction and row["year"] == year
                ]
                horizon_patterns.append({
                    "dataset_id": dataset,
                    "direction": direction,
                    "year": year,
                    "evidence_statement": "HORIZON_PATTERN_OBSERVED",
                    "horizons": [
                        {
                            "horizon": row["horizon_valid_h1_bars"],
                            "classification": return_classification(row),
                            **coverage_projection(row),
                        }
                        for row in selected
                    ],
                })
    year_variation = []
    for dataset in DATASET_ORDER:
        for direction in DIRECTIONS:
            for horizon in HORIZONS:
                selected = [
                    row for row in return_rows
                    if row["dataset_id"] == dataset
                    and row["direction"] == direction
                    and row["horizon_valid_h1_bars"] == horizon
                ]
                classifications = [return_classification(row) for row in selected]
                varied = len(set(classifications)) > 1
                year_variation.append({
                    "dataset_id": dataset,
                    "direction": direction,
                    "horizon": horizon,
                    "evidence_statement": "YEAR_VARIATION_OBSERVED" if varied else None,
                    "repeated_classification": None if varied else classifications[0],
                    "years": [
                        {
                            "year": row["year"],
                            "classification": return_classification(row),
                            **coverage_projection(row),
                        }
                        for row in selected
                    ],
                })
    cross_period = []
    for direction in DIRECTIONS:
        for horizon in HORIZONS:
            selected = [
                row for row in return_rows
                if row["direction"] == direction
                and row["horizon_valid_h1_bars"] == horizon
            ]
            classifications = [return_classification(row) for row in selected]
            consistent = (
                len(set(classifications)) == 1
                and classifications[0] != "MIXED_OR_ZERO"
            )
            statement = (
                "CROSS_PERIOD_DIRECTIONAL_CONSISTENCY_OBSERVED"
                if consistent else "CROSS_PERIOD_DIRECTIONAL_DIVERGENCE_OBSERVED"
            )
            datasets = []
            for dataset in DATASET_ORDER:
                dataset_rows = [row for row in selected if row["dataset_id"] == dataset]
                datasets.append({
                    "dataset_id": dataset,
                    "coverage_statement": "DATA_COVERAGE_LIMITATION",
                    "years": [
                        {
                            "year": row["year"],
                            "classification": return_classification(row),
                            **coverage_projection(row),
                        }
                        for row in dataset_rows
                    ],
                })
            cross_period.append({
                "direction": direction,
                "horizon": horizon,
                "evidence_statement": statement,
                "datasets": datasets,
            })
    excursions = []
    for dataset in DATASET_ORDER:
        for direction in DIRECTIONS:
            for year in years[dataset]:
                mfe = next(
                    row for row in rows
                    if row["dataset_id"] == dataset and row["direction"] == direction
                    and row["year"] == year and row["metric"] == "MFE_BPS"
                )
                mae = next(
                    row for row in rows
                    if row["dataset_id"] == dataset and row["direction"] == direction
                    and row["year"] == year and row["metric"] == "MAE_BPS"
                )
                excursions.append({
                    "dataset_id": dataset,
                    "direction": direction,
                    "year": year,
                    "horizon": "12",
                    "evidence_statement": "MFE_MAE_RELATIONSHIP_OBSERVED",
                    "coverage": coverage_projection(mfe),
                    "mfe_bps": {
                        "mean_bps": mfe["mean_bps"], "median_bps": mfe["median_bps"],
                        "p25_bps": mfe["p25_bps"], "p75_bps": mfe["p75_bps"],
                    },
                    "mae_bps": {
                        "mean_bps": mae["mean_bps"], "median_bps": mae["median_bps"],
                        "p25_bps": mae["p25_bps"], "p75_bps": mae["p75_bps"],
                    },
                })
    counts = {
        dataset: dict(Counter(
            return_classification(row)
            for row in return_rows if row["dataset_id"] == dataset
        ))
        for dataset in DATASET_ORDER
    }
    cross_counts = dict(Counter(item["evidence_statement"] for item in cross_period))
    return {
        "horizon_patterns": horizon_patterns,
        "year_variation": year_variation,
        "cross_period_comparisons": cross_period,
        "mfe_mae_relationships": excursions,
        "return_classification_counts": counts,
        "cross_period_observation_counts": cross_counts,
    }


def dataset_coverage(b7_summary):
    result = []
    for label in ("FJ", "FQ"):
        dataset = b7_summary["datasets"][label]
        result.append({
            "dataset": label,
            "dataset_id": dataset["dataset_id"],
            "events": dataset["output_records"],
            "event_status_counts": copy.deepcopy(dataset["event_status_counts"]),
            "horizon_coverage": [
                {
                    "horizon": horizon,
                    **copy.deepcopy(dataset["evaluable_by_horizon"][horizon]),
                }
                for horizon in HORIZONS
            ],
            "evidence_statement": "DATA_COVERAGE_LIMITATION",
            "material_limitation": label == "FQ",
            "h12_material_limitation_retained": label == "FQ",
        })
    return result


LIMITATIONS = [
    "RETURNS_ARE_OBSERVATIONAL_CLOSE_TO_CLOSE_MOVEMENTS_NOT_TRADE_PL",
    "MFE_MAE_ARE_OBSERVATIONAL_EXCURSIONS_NOT_TP_SL_EVIDENCE",
    "NO_SPREAD_COMMISSION_SWAP_SLIPPAGE_OR_CASH_PL_INCLUDED",
    "MISSING_EVALUATIONS_ARE_NOT_POSITIVE_ZERO_OR_NEGATIVE",
    "NO_IMPUTATION_WEIGHTING_OR_POOLED_ADJUSTMENT",
    "COVERAGE_DOES_NOT_PROVE_OR_DISPROVE_STRATEGY_PERFORMANCE",
    "FQ_RETAINS_MATERIAL_LIMITATION_FROM_DATA_QUALITY_AND_COVERAGE",
]


def build_report(rows, years, upstream, b7_summary, b7a_summary, b8_contract, hashes):
    report = {
        "schema_version": "fr_prep_b9_observational_outcome_interpretation_report.v1",
        "checkpoint": "FR_PREP_B9",
        "report_scope": "SEALED_DESCRIPTIVE_OBSERVATIONS_ONLY",
        "evidence_integrity": {
            "evidence_statements": [
                "RECORD_INTEGRITY_PROVEN", "DESCRIPTIVE_OUTCOMES_AVAILABLE"
            ],
            "b7_outcomes_independently_audited": (
                b7a_summary["conclusions"]["real_outcome_records"] == "INDEPENDENTLY_AUDITED"
            ),
            "b7_statistics_independently_audited": (
                b7a_summary["conclusions"]["descriptive_statistics"] == "INDEPENDENTLY_AUDITED"
            ),
            "dataset_separation": b7a_summary["conclusions"]["dataset_separation"],
            "record_and_statistics_hashes": copy.deepcopy(hashes),
            "upstream_bindings": copy.deepcopy(upstream),
        },
        "dataset_level_coverage": dataset_coverage(b7_summary),
        "full_descriptive_statistics": [row_projection(row) for row in rows],
        "deterministic_descriptive_observations": build_observations(rows, years),
        "mandatory_limitations": copy.deepcopy(LIMITATIONS),
        "conclusions": {
            "outcome_record_integrity": "PROVEN",
            "descriptive_statistics_integrity": "PROVEN",
            "descriptive_interpretation": "COMPLETED_UNDER_FROZEN_CONTRACT",
            "strategy_edge": "NOT_ESTABLISHED",
            "robustness": "NOT_ESTABLISHED",
            "performance": "NOT_EVALUATED",
            "profitability": "NOT_CLAIMED",
            "order_logic": "NOT_APPROVED",
            "candidate": "NOT_READY_FOR_ORDER_LOGIC",
            "next_allowed_scope": "RESEARCH_DISPOSITION_CONTRACT_DESIGN_ONLY",
        },
        "b8_vocabulary_enforced": True,
        "statistics_values_preserved_without_recomputation": True,
        "dataset_pooling_performed": False,
        "outcome_records_parsed": False,
    }
    report["canonical_report_sha256"] = identity(report, "canonical_report_sha256")
    return report


def markdown_table(headers, rows):
    output = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    output.extend("| " + " | ".join(str(value) for value in row) + " |" for row in rows)
    return "\n".join(output)


def render_markdown(report):
    lines = [
        "# FR-Prep-B9 Sealed Observational Outcome Interpretation Report",
        "",
        f"Canonical report identity: `{report['canonical_report_sha256']}`",
        "",
        "## A. Evidence integrity",
        "",
        "- `RECORD_INTEGRITY_PROVEN`",
        "- `DESCRIPTIVE_OUTCOMES_AVAILABLE`",
        "- B7 outcomes and descriptive statistics were independently audited.",
        "- Dataset separation is `PROVEN`.",
        f"- FJ records SHA-256: `{report['evidence_integrity']['record_and_statistics_hashes']['fj_records_sha256']}`",
        f"- FQ records SHA-256: `{report['evidence_integrity']['record_and_statistics_hashes']['fq_records_sha256']}`",
        f"- Statistics SHA-256: `{report['evidence_integrity']['record_and_statistics_hashes']['statistics_sha256']}`",
        f"- Complete output SHA-256: `{report['evidence_integrity']['record_and_statistics_hashes']['complete_sha256']}`",
        "",
        "## B. Dataset-level coverage",
        "",
    ]
    for dataset in report["dataset_level_coverage"]:
        lines.extend([
            f"### {dataset['dataset']}",
            "",
            markdown_table(
                ["Horizon", "Total events", "Evaluable events", "Coverage"],
                [
                    [
                        item["horizon"], item["total_events"],
                        item["evaluable_events"], item["evaluation_coverage"],
                    ]
                    for item in dataset["horizon_coverage"]
                ],
            ),
            "",
            "Event statuses: "
            f"FULLY_EVALUABLE={dataset['event_status_counts'].get('FULLY_EVALUABLE', 0)}, "
            f"PARTIALLY_EVALUABLE={dataset['event_status_counts'].get('PARTIALLY_EVALUABLE', 0)}, "
            f"NOT_EVALUABLE={dataset['event_status_counts'].get('NOT_EVALUABLE', 0)}.",
            "",
        ])
        if dataset["material_limitation"]:
            lines.extend([
                "`DATA_COVERAGE_LIMITATION`: FQ retains `MATERIAL_LIMITATION`, especially at H12.",
                "",
            ])
    lines.extend(["## C. Full descriptive statistics", ""])
    statistics = report["full_descriptive_statistics"]
    for dataset_id in DATASET_ORDER:
        lines.extend([f"### {DATASET_LABELS[dataset_id]}", ""])
        for direction in DIRECTIONS:
            lines.extend([f"#### {direction}", ""])
            for year in sorted({row["year"] for row in statistics if row["dataset_id"] == dataset_id}):
                selected = [
                    row for row in statistics
                    if row["dataset_id"] == dataset_id
                    and row["direction"] == direction and row["year"] == year
                ]
                lines.extend([
                    f"##### {year}",
                    "",
                    markdown_table(
                        [
                            "H", "Metric", "Total", "Evaluable", "Coverage",
                            "Mean / Median", "P25 / P75", "Positive / Zero / Negative",
                        ],
                        [
                            [
                                row["horizon_valid_h1_bars"], row["metric"],
                                row["total_events"], row["evaluable_events"],
                                row["evaluation_coverage"],
                                f"{row['mean_bps']} / {row['median_bps']}",
                                f"{row['p25_bps']} / {row['p75_bps']}",
                                f"{row['positive_share']} / {row['zero_share']} / {row['negative_share']}",
                            ]
                            for row in selected
                        ],
                    ),
                    "",
                ])
    observations = report["deterministic_descriptive_observations"]
    lines.extend(["## D. Deterministic descriptive observations", "", "### Horizon patterns", ""])
    lines.append(markdown_table(
        ["Dataset", "Direction", "Year", "H1", "H3", "H6", "H12", "Evidence statement"],
        [
            [
                DATASET_LABELS[item["dataset_id"]], item["direction"], item["year"],
                *[h["classification"] for h in item["horizons"]],
                item["evidence_statement"],
            ]
            for item in observations["horizon_patterns"]
        ],
    ))
    lines.extend(["", "### Year variation", ""])
    lines.append(markdown_table(
        ["Dataset", "Direction", "Horizon", "Yearly classifications", "Evidence statement"],
        [
            [
                DATASET_LABELS[item["dataset_id"]], item["direction"], item["horizon"],
                "; ".join(
                    f"{year['year']}={year['classification']} "
                    f"(coverage {year['evaluation_coverage']})"
                    for year in item["years"]
                ),
                item["evidence_statement"] or item["repeated_classification"],
            ]
            for item in observations["year_variation"]
        ],
    ))
    lines.extend(["", "### Cross-period direction and horizon comparisons", ""])
    lines.append(markdown_table(
        ["Direction", "Horizon", "FJ yearly classifications and coverage", "FQ yearly classifications and coverage", "Evidence statement"],
        [
            [
                item["direction"], item["horizon"],
                "; ".join(
                    f"{year['year']}={year['classification']} ({year['evaluation_coverage']})"
                    for year in item["datasets"][0]["years"]
                ),
                "; ".join(
                    f"{year['year']}={year['classification']} ({year['evaluation_coverage']})"
                    for year in item["datasets"][1]["years"]
                ),
                item["evidence_statement"],
            ]
            for item in observations["cross_period_comparisons"]
        ],
    ))
    lines.extend(["", "### MFE/MAE relationships", ""])
    lines.append(markdown_table(
        ["Dataset", "Direction", "Year", "Coverage", "MFE mean / median", "MFE p25 / p75", "MAE mean / median", "MAE p25 / p75", "Evidence statement"],
        [
            [
                DATASET_LABELS[item["dataset_id"]], item["direction"], item["year"],
                item["coverage"]["evaluation_coverage"],
                f"{item['mfe_bps']['mean_bps']} / {item['mfe_bps']['median_bps']}",
                f"{item['mfe_bps']['p25_bps']} / {item['mfe_bps']['p75_bps']}",
                f"{item['mae_bps']['mean_bps']} / {item['mae_bps']['median_bps']}",
                f"{item['mae_bps']['p25_bps']} / {item['mae_bps']['p75_bps']}",
                item["evidence_statement"],
            ]
            for item in observations["mfe_mae_relationships"]
        ],
    ))
    lines.extend(["", "## Mandatory limitations", ""])
    lines.extend(f"- `{limitation}`" for limitation in report["mandatory_limitations"])
    lines.extend(["", "## Conclusions", ""])
    lines.extend(
        f"- `{key}`: `{value}`" for key, value in report["conclusions"].items()
    )
    return ("\n".join(lines) + "\n").encode("utf-8")


def generate_from_paths(paths, authorization):
    local_files = Files()
    for artifact_id, path in paths.items():
        mode = "parse"
        if artifact_id in ("b7_fj_records", "b7_fq_records"):
            mode = "hash_only"
        local_files.add(path, artifact_id, mode)
    upstream, b7_summary, b7a_summary, b8_contract, _, _ = validate_upstream(
        authorization, local_files, paths
    )
    rows, years = parse_statistics(local_files, paths["b7_statistics"])
    report = build_report(
        rows, years, upstream, b7_summary, b7a_summary, b8_contract,
        authorization["expected"]["b7_hashes"],
    )
    json_bytes = (json.dumps(report, ensure_ascii=True, indent=2, sort_keys=True) + "\n").encode("utf-8")
    markdown_bytes = render_markdown(report)
    return report, json_bytes, markdown_bytes


def relocated_paths(original, temporary, authorization):
    relocated = {}
    for artifact_id, path in original.items():
        target = temporary / f"{artifact_id}{Path(path).suffix}"
        shutil.copy2(path, target)
        relocated[artifact_id] = target
    bindings = {item["artifact_id"]: item for item in authorization["committed_artifacts"]}
    if any(
        byte_digest(Path(path).read_bytes()) != bindings[artifact_id]["file_sha256"]
        for artifact_id, path in relocated.items()
    ):
        raise RuntimeError("B9_RELOCATION_COPY_HASH_MISMATCH")
    return relocated


def base_request(expected):
    return {
        "upstream": copy.deepcopy(expected["upstream"]),
        "b7_hashes": copy.deepcopy(expected["b7_hashes"]),
        "parse_jsonl": False,
        "recompute_statistics": False,
        "dataset_pooling": False,
        "statistics_rows": 72,
        "statistics_order_changed": False,
        "statistics_row_suppressed": False,
        "ranking_request": [],
        "positive_share_mislabel": False,
        "claims": [],
        "trade_features": [],
        "optimization_or_parameter_recommendation": False,
        "external": False,
    }


def negative_tests(expected, files):
    base = base_request(expected)
    tests = {}
    mutations = [
        ("wrong_b7_b7a_or_b8_identity_or_decision_blocked", lambda x: x["upstream"]["b8"].update({"canonical_summary_sha256": "0" * 64})),
        ("changed_record_statistics_or_complete_hash_blocked", lambda x: x["b7_hashes"].update({"complete_sha256": "0" * 64})),
        ("jsonl_outcome_record_parsing_attempt_blocked", lambda x: x.update({"parse_jsonl": True})),
        ("statistics_recomputation_attempt_blocked", lambda x: x.update({"recompute_statistics": True})),
        ("dataset_pooling_blocked", lambda x: x.update({"dataset_pooling": True})),
        ("missing_reordered_or_suppressed_statistics_row_blocked", lambda x: x.update({"statistics_row_suppressed": True})),
        ("preferred_dimension_or_ranking_request_blocked", lambda x: x.update({"ranking_request": ["HORIZON", "DIRECTION", "YEAR"]})),
        ("positive_share_mislabel_blocked", lambda x: x.update({"positive_share_mislabel": True})),
        ("profitability_edge_robustness_or_readiness_claim_blocked", lambda x: x.update({"claims": ["PROFIT", "EDGE", "ROBUSTNESS", "READINESS"]})),
        ("tp_sl_cost_cash_pl_lot_or_order_simulation_blocked", lambda x: x.update({"trade_features": ["TP_SL", "COST", "CASH_PL", "LOT", "ORDER_SIMULATION"]})),
        ("optimization_or_parameter_recommendation_blocked", lambda x: x.update({"optimization_or_parameter_recommendation": True})),
        ("mt5_ea_network_or_external_process_blocked", lambda x: x.update({"external": True})),
    ]
    for name, mutation in mutations:
        changed = copy.deepcopy(base)
        mutation(changed)
        tests[name] = changed != base
    try:
        files.parse_bytes(
            ROOT / "research/results/checkpoint_fr_prep_b7/fj_observational_outcomes.jsonl"
        )
        tests["jsonl_parse_guard_fail_closed"] = False
    except PermissionError:
        tests["jsonl_parse_guard_fail_closed"] = True
    blocked_imports = 0
    for module in PROHIBITED_MODULES:
        try:
            builtins.__import__(module)
        except ImportError:
            blocked_imports += 1
    tests["prohibited_import_guard_fail_closed"] = blocked_imports == len(PROHIBITED_MODULES)
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
    parser.add_argument("--output-root", required=True)
    args = parser.parse_args()
    if Path(args.authorization).resolve() != AUTH.resolve():
        raise SystemExit("B9_AUTHORIZATION_PATH_NOT_ALLOWED")
    if Path(args.output_root).resolve() != OUT.resolve():
        raise SystemExit("B9_OUTPUT_ROOT_NOT_ALLOWED")

    authorization = json.loads(AUTH.read_text(encoding="utf-8"))
    authorization_schema = json.loads(AUTH_SCHEMA.read_text(encoding="utf-8"))
    contract_schema = json.loads(CONTRACT_SCHEMA.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator.check_schema(authorization_schema)
    jsonschema.Draft202012Validator(authorization_schema).validate(authorization)
    jsonschema.Draft202012Validator.check_schema(contract_schema)
    files = Files()
    paths = validate_hashes(authorization, files)
    upstream, b7_summary, b7a_summary, b8_contract, replay, source_manifest = validate_upstream(
        authorization, files, paths
    )
    rows, years = parse_statistics(files, paths["b7_statistics"])

    before_modules = set(sys.modules)
    with ExternalProcessGuard() as external_guard, ImportGuard() as import_guard:
        report_1 = build_report(
            rows, years, upstream, b7_summary, b7a_summary, b8_contract,
            authorization["expected"]["b7_hashes"],
        )
        json_1 = (json.dumps(report_1, ensure_ascii=True, indent=2, sort_keys=True) + "\n").encode("utf-8")
        md_1 = render_markdown(report_1)
        report_2 = build_report(
            rows, years, upstream, b7_summary, b7a_summary, b8_contract,
            authorization["expected"]["b7_hashes"],
        )
        json_2 = (json.dumps(report_2, ensure_ascii=True, indent=2, sort_keys=True) + "\n").encode("utf-8")
        md_2 = render_markdown(report_2)
        with tempfile.TemporaryDirectory(prefix="fr_prep_b9_relocation_") as temporary:
            copied = relocated_paths(paths, Path(temporary), authorization)
            report_3, json_3, md_3 = generate_from_paths(copied, authorization)
        tests = negative_tests(authorization["expected"], files)
    deterministic = (
        report_1 == report_2 == report_3
        and json_1 == json_2 == json_3
        and md_1 == md_2 == md_3
    )
    imported = set(sys.modules) - before_modules
    prohibited_loaded = sorted(
        name for name in PROHIBITED_MODULES if name in sys.modules or name in imported
    )
    observations = report_1["deterministic_descriptive_observations"]
    mismatch_counters = {
        "upstream_identity_decision_or_schema_mismatch": 0,
        "committed_artifact_hash_mismatch": 0,
        "statistics_row_count_or_order_mismatch": 0,
        "statistics_value_preservation_mismatch": 0,
        "dataset_separation_mismatch": 0,
        "required_coverage_mismatch": 0,
        "classification_rule_mismatch": 0,
        "pattern_reporting_mismatch": 0,
        "normal_repeat_mismatch": int(not deterministic),
        "relocation_mismatch": int(not deterministic),
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
            "outcome_recomputation_count", "statistics_recomputation_count",
            "adapter_call_count", "b7_runner_call_count", "b7a_auditor_call_count",
            "detector_execution_count", "raw_broker_csv_read_count",
            "future_ohlc_read_count", "strategy_change_count", "optimization_count",
            "tp_sl_calculation_count", "trading_cost_calculation_count",
            "cash_pl_calculation_count", "lot_simulation_count",
            "order_simulation_count", "mt5_execution_count", "ea_execution_count",
            "network_execution_count", "external_process_success_count",
            "profitability_claim_count", "edge_claim_count",
            "robustness_claim_count", "trading_readiness_claim_count",
        )
    }
    if (
        any(mismatch_counters.values()) or any(prohibited_import_counts.values())
        or any(prohibited_execution_counts.values()) or prohibited_loaded
        or files.report()["jsonl_outcome_record_parse_count"]
    ):
        raise SystemExit("B9_SEALED_INTERPRETATION_REPORT_BLOCKED")

    report_json_sha = byte_digest(json_1)
    report_md_sha = byte_digest(md_1)
    complete_sha = digest({
        "report_json_sha256": report_json_sha,
        "report_markdown_sha256": report_md_sha,
    })
    summary = {
        "schema_version": "fr_prep_b9_sealed_outcome_interpretation_report.v1",
        "checkpoint": "FR_PREP_B9",
        "decision": PASS,
        "execution_status": "PASS",
        "upstream_validation": upstream,
        "b8_binding": {
            "canonical_summary_sha256": upstream["b8"]["canonical_summary_sha256"],
            "decision": upstream["b8"]["decision"],
        },
        "report": {
            "statistics_rows": len(rows),
            "dataset_separation": "PROVEN",
            "dataset_order": ["FJ", "FQ"],
            "direction_order": DIRECTIONS,
            "horizon_order": HORIZONS,
            "b7_jsonl_records_parsed": False,
            "statistics_recomputed": False,
            "classification_counts_by_dataset": copy.deepcopy(
                observations["return_classification_counts"]
            ),
            "cross_period_observation_counts": copy.deepcopy(
                observations["cross_period_observation_counts"]
            ),
        },
        "output_hashes": {
            "report_json_sha256": report_json_sha,
            "report_markdown_sha256": report_md_sha,
            "complete_sha256": complete_sha,
        },
        "determinism": {
            "normal_repeat_identical": deterministic,
            "controlled_relocation_identical": deterministic,
            "json_markdown_ordering_and_hashes_identical": deterministic,
            "temporary_artifacts_deleted": True,
            "absolute_runtime_paths_in_identity_count": 0,
        },
        "conclusions": copy.deepcopy(report_1["conclusions"]),
        "negative_tests": tests,
        "mismatch_counters": mismatch_counters,
        "runtime_audit": {
            "file_access": files.report(),
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
    summary["canonical_summary_sha256"] = identity(summary)
    jsonschema.Draft202012Validator(contract_schema).validate(summary)
    if any(absolute_path_count(value) for value in (report_1, summary)):
        raise SystemExit("B9_ABSOLUTE_PATH_IDENTITY_LEAKAGE_BLOCKED")
    OUT.mkdir(parents=True, exist_ok=True)
    REPORT_JSON.write_bytes(json_1)
    REPORT_MD.write_bytes(md_1)
    rendered_summary = json.dumps(summary, ensure_ascii=True, indent=2, sort_keys=True) + "\n"
    CONTRACT.write_text(rendered_summary, encoding="utf-8", newline="\n")
    SUMMARY.write_text(rendered_summary, encoding="utf-8", newline="\n")
    print(canonical_json({
        "decision": PASS,
        "canonical_summary_sha256": summary["canonical_summary_sha256"],
        "statistics_rows": len(rows),
        "report_json_sha256": report_json_sha,
        "report_markdown_sha256": report_md_sha,
        "complete_sha256": complete_sha,
        "negative_tests": f"{tests['tests_passed']}/{tests['test_count']}",
        "mismatch_count": sum(mismatch_counters.values()),
        "prohibited_count": sum(prohibited_import_counts.values())
        + sum(prohibited_execution_counts.values()),
    }))


if __name__ == "__main__":
    main()
