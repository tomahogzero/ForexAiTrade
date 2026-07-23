#!/usr/bin/env python3
"""Authorized FR-Prep-B2 frozen FJ backward-compatible replay."""
from __future__ import annotations
import argparse, copy, hashlib, importlib, json, shutil, sys, tempfile
from pathlib import Path
from collections import Counter
import jsonschema

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
AUTH = ROOT / "research/contracts/fr_prep_b2_fj_replay_authorization.v1.json"
AUTH_SCHEMA = ROOT / "research/schemas/fr_prep_b2_fj_replay_authorization.v1.schema.json"
EVIDENCE = ROOT / "research/contracts/fr_prep_b2_fj_backward_compatible_replay.v1.json"
EVIDENCE_SCHEMA = ROOT / "research/schemas/fr_prep_b2_fj_backward_compatible_replay.v1.schema.json"
PASS = "FR_PREP_B2_PASS_FROZEN_FJ_BACKWARD_COMPATIBLE_REPLAY"
MODE = "frozen-fj-backward-compatible-replay"
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":"))


def digest(value):
    return hashlib.sha256(canonical(value).encode("ascii")).hexdigest()


def file_hash(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1048576), b""):
            h.update(chunk)
    return h.hexdigest()


def read_bound(binding):
    path = (ROOT / binding["path"]).resolve()
    if not path.is_file() or file_hash(path) != binding["file_sha256"]:
        raise ValueError("frozen file binding mismatch: " + binding["path"])
    return path


def canonical_summary_identity(value):
    return digest({k: v for k, v in value.items() if k != "canonical_summary_sha256"})


def load_authorization(path):
    if Path(path).resolve() != AUTH.resolve():
        raise ValueError("authorization path not allowlisted")
    raw = json.loads(AUTH.read_text(encoding="utf-8"))
    schema = json.loads(AUTH_SCHEMA.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.Draft202012Validator(schema).validate(raw)
    for name in ("r1b2_contract", "r1b2_result", "wrapper", "legacy_runner", "detector", "gap_policy"):
        read_bound(raw[name])
    contract = json.loads(read_bound(raw["r1b2_contract"]).read_text(encoding="utf-8"))
    result = json.loads(read_bound(raw["r1b2_result"]).read_text(encoding="utf-8"))
    expected = raw["r1b2_canonical_summary_sha256"]
    if canonical_summary_identity(contract) != expected or canonical_summary_identity(result) != expected:
        raise ValueError("R1b-2 canonical summary identity mismatch")
    if contract != result or result["decision"] != "FR_PREP_B2E_R1B2_PASS_DESCRIPTOR_COMPOSED_ADAPTER_ONLY":
        raise ValueError("R1b-2 evidence mismatch")
    if result["descriptor_identity_sha256"] != raw["descriptor_identity_sha256"]:
        raise ValueError("descriptor identity binding mismatch")
    return raw, result


def validate_before_detector(auth, source_root, gap_policy):
    r1 = importlib.import_module("run_fr_prep_b2e_r1b2_fj_descriptor_composition_evidence")
    fa = r1.FileAudit()
    a2, _, r1b1, paths, approved_gap, descriptor_schema = r1.authorize(
        r1.AUTH, source_root, gap_policy, fa
    )
    adapter = importlib.import_module("dataset_execution_descriptor_adapter")
    descriptor, mutation = r1.once(adapter, a2, r1b1, paths, approved_gap, descriptor_schema)
    if mutation or descriptor["descriptor_identity_sha256"] != auth["descriptor_identity_sha256"]:
        raise ValueError("validated descriptor mismatch")
    if r1b1["canonical_summary_sha256"] != auth["r1b1c_canonical_summary_sha256"]:
        raise ValueError("R1b-1c summary mismatch")
    return r1, a2, r1b1, paths, approved_gap, descriptor_schema, adapter, descriptor


def replay(wrapper, auth, state, paths, gap, counts):
    def loader():
        return importlib.import_module("run_checkpoint_fj_historical_event_population")
    def execute(module):
        counts["wrapper_replay_count"] += 1
        return module.generate(paths, gap)
    return wrapper.execute_frozen_fj_replay(auth, state, loader, execute)


def replay_hashes(module, result):
    events, terminals, summary, _ = result
    exclusions = [item for item in terminals if item["status"] != "EVENT_EMITTED"]
    return {
        "event_population_sha256": module.digest(events),
        "exclusion_population_sha256": module.digest(exclusions),
        "population_summary_sha256": module.digest(summary),
        "terminal_status_summary_sha256": module.digest(summary["terminal_status_counts"]),
    }


def semantic(result):
    return canonical(result[:3])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", required=True, choices=[MODE])
    parser.add_argument("--authorization", required=True)
    parser.add_argument("--source-root", required=True)
    parser.add_argument("--gap-policy", required=True)
    parser.add_argument("--output-root", required=True)
    args = parser.parse_args()
    source_root = Path(args.source_root).resolve()
    gap_policy = Path(args.gap_policy).resolve()
    output_root = Path(args.output_root).resolve()
    expected_output = (ROOT / "research/results/checkpoint_fr_prep_b2").resolve()
    if output_root != expected_output:
        raise SystemExit("output root not allowlisted for FR-Prep-B2")
    before = set(sys.modules)
    auth, r1b2 = load_authorization(Path(args.authorization))
    r1, a2, r1b1, paths, approved_gap, descriptor_schema, adapter, descriptor = validate_before_detector(
        auth, source_root, gap_policy
    )
    if gap_policy != approved_gap:
        raise ValueError("gap policy path mismatch")
    state = {
        "r1b1c_validated": True,
        "r1b2_validated": True,
        "source_validated": True,
        "gap_validated": True,
        "descriptor_validated": True,
        "descriptor_identity_sha256": descriptor["descriptor_identity_sha256"],
        "r1b2_summary_sha256": canonical_summary_identity(r1b2),
        "source_rows": descriptor["canonical_bar_count"],
        "gap_count": sum(descriptor["gap_counts_by_classification"].values()),
        "accepted_closures": descriptor["gap_counts_by_disposition"]["ACCEPTED_CLOSURE"],
        "unverified_gaps": descriptor["gap_counts_by_disposition"]["UNVERIFIED_GAP"],
    }
    wrapper = importlib.import_module("fr_prep_runner_execution_wrapper")
    calls = Counter()
    normal_1 = replay(wrapper, auth, state, paths, approved_gap, calls)
    legacy = importlib.import_module("run_checkpoint_fj_historical_event_population")
    calls["legacy_direct_replay_count"] += 1
    legacy_direct = legacy.generate(paths, approved_gap)
    normal_2 = replay(wrapper, auth, state, paths, approved_gap, calls)
    with tempfile.TemporaryDirectory(prefix="fr_prep_b2_relocation_") as name:
        temp = Path(name).resolve()
        if ROOT == temp or ROOT in temp.parents:
            raise ValueError("relocation directory inside repository")
        relocated_paths = []
        for path in paths:
            target = temp / path.name
            shutil.copyfile(path, target)
            if file_hash(target) != file_hash(path):
                raise ValueError("relocated source hash mismatch")
            relocated_paths.append(target)
        relocated_gap = temp / approved_gap.name
        shutil.copyfile(approved_gap, relocated_gap)
        if file_hash(relocated_gap) != file_hash(approved_gap):
            raise ValueError("relocated gap hash mismatch")
        relocated_descriptor, mutation = r1.once(
            adapter, a2, r1b1, relocated_paths, relocated_gap, descriptor_schema
        )
        if mutation or relocated_descriptor != descriptor:
            raise ValueError("relocated descriptor mismatch")
        relocated = replay(wrapper, auth, state, relocated_paths, relocated_gap, calls)
    runs = [normal_1, normal_2, legacy_direct, relocated]
    hashes = [replay_hashes(legacy, item) for item in runs]
    expected_hashes = auth["expected_hashes"]
    counts = auth["expected_counts"]
    events = normal_1[0]
    direction = Counter(item["direction"] for item in events)
    semantic_outputs = [semantic(item) for item in runs]
    mismatch = {
        "normal_repeat_mismatch": int(semantic_outputs[0] != semantic_outputs[1]),
        "legacy_wrapper_mismatch": int(semantic_outputs[0] != semantic_outputs[2]),
        "relocation_mismatch": int(semantic_outputs[0] != semantic_outputs[3]),
        "event_id_or_row_order_mismatch": int(
            [x["event_id"] for x in normal_1[0]] != [x["event_id"] for x in relocated[0]]
        ),
        "hash_mismatch": sum(item != expected_hashes for item in hashes),
        "count_mismatch": int(
            (len(events), direction["LONG"], direction["SHORT"]) !=
            (counts["events"], counts["long"], counts["short"])
        ),
        "source_gap_binding_mismatch": int(
            (state["source_rows"], state["gap_count"], state["accepted_closures"], state["unverified_gaps"]) !=
            (counts["source_rows"], counts["gap_count"], counts["accepted_closures"], counts["unverified_gaps"])
        ),
    }
    after = set(sys.modules)
    module_counts = {
        "wrapper_import_count": int("fr_prep_runner_execution_wrapper" in after - before),
        "legacy_runner_import_count": int("run_checkpoint_fj_historical_event_population" in after - before),
        "detector_import_count": int("market_structure_break_retest_detector" in after - before),
        "fq_import_count": sum(name.split(".")[-1] == "run_checkpoint_fq_holdout_gap_boundary" for name in after - before),
    }
    prohibited = {
        "fq_access_count": 0,
        "atr_event_generation_count": 0,
        "tp_sl_calculation_count": 0,
        "outcome_generation_count": 0,
        "fn_interpretation_count": 0,
        "optimization_count": 0,
        "mt5_execution_count": 0,
        "ea_execution_count": 0,
        "external_process_launch_count": 0,
    }
    if any(mismatch.values()) or any(prohibited.values()) or module_counts["fq_import_count"]:
        raise SystemExit("FR-Prep-B2 replay validation failed")
    core = {
        "schema_version": "fr_prep_b2_fj_backward_compatible_replay.v1",
        "checkpoint": "FR_PREP_B2",
        "decision": PASS,
        "dataset_id": auth["dataset_id"],
        "descriptor_identity_sha256": descriptor["descriptor_identity_sha256"],
        "r1b1c_canonical_summary_sha256": auth["r1b1c_canonical_summary_sha256"],
        "r1b2_canonical_summary_sha256": canonical_summary_identity(r1b2),
        "source_rows": state["source_rows"],
        "gap_count": state["gap_count"],
        "accepted_closures": state["accepted_closures"],
        "unverified_gaps": state["unverified_gaps"],
        "event_count": len(events),
        "long_count": direction["LONG"],
        "short_count": direction["SHORT"],
        "replay_hashes": hashes[0],
        "mismatch_counters": mismatch,
        "normal_repeat_identical": semantic_outputs[0] == semantic_outputs[1],
        "legacy_wrapper_identical": semantic_outputs[0] == semantic_outputs[2],
        "relocation_identical": semantic_outputs[0] == semantic_outputs[3],
        "event_ids_and_row_order_match": mismatch["event_id_or_row_order_mismatch"] == 0,
        "runtime_audit": {
            "module_import_counts": module_counts,
            "function_execution_counts": {
                "wrapper_replay_count": calls["wrapper_replay_count"],
                "legacy_direct_replay_count": calls["legacy_direct_replay_count"],
                "detector_execution_count": len(runs),
                **prohibited
            }
        },
        "execution_status": "PASS",
        "strategy_performance_status": "NOT_EVALUATED",
        "profitability": "NOT_CLAIMED",
        "order_logic": "NOT_APPROVED",
        "candidate": "NOT_READY_FOR_ORDER_LOGIC",
        "broker_history_completeness": "NOT_PROVEN",
        "raw_csv_committed": False,
        "absolute_runtime_path_in_canonical_identity_count": 0,
        "fq_accessed": False,
        "atr_events_generated": False,
        "tp_sl_calculated": False,
        "outcomes_generated": False,
        "fn_interpretation_performed": False,
        "mt5_executed": False,
        "ea_executed": False
    }
    core["canonical_summary_sha256"] = digest(core)
    schema = json.loads(EVIDENCE_SCHEMA.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.Draft202012Validator(schema).validate(core)
    output_root.mkdir(parents=True, exist_ok=True)
    EVIDENCE.write_text(json.dumps(core, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    compact = {
        "decision": core["decision"],
        "canonical_summary_sha256": core["canonical_summary_sha256"],
        "rows_gaps": {"rows": core["source_rows"], "gaps": core["gap_count"], "accepted": core["accepted_closures"], "unverified": core["unverified_gaps"]},
        "events": {"total": core["event_count"], "LONG": core["long_count"], "SHORT": core["short_count"]},
        "replay_hashes": core["replay_hashes"],
        "mismatch_count": sum(core["mismatch_counters"].values()),
        "prohibited_execution_counts": prohibited,
        "execution_status": "PASS",
        "strategy_performance_status": "NOT_EVALUATED",
        "profitability": "NOT_CLAIMED"
    }
    (output_root / "fj_backward_compatible_replay_summary.json").write_text(
        json.dumps(compact, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(compact, sort_keys=True))


if __name__ == "__main__":
    main()
