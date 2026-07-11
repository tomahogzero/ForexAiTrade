#!/usr/bin/env python3
"""Extract committed-contract PAF Fibo rows from existing diagnostic logs only."""
from __future__ import annotations
import argparse, csv, json, re, sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from paf_diagnostic_parser import extract_diagnostics, load_json, read_text

RUN_IDS = ("run_20260711_145612", "run_20260711_152017", "run_20260711_153941")
FIELDS = ("run_id","window_index","phase","event_time","runtime_symbol","timeframe","authoritative_source","case_id","classification","paf_candidate_direction","paf_direction_is_usable_for_first_touch","paf_direction_source","paf_direction_reason","paf_fibo_direction_gap_reason","schema_origin")

def main() -> int:
    ap=argparse.ArgumentParser(); ap.add_argument("--source-root", required=True); ap.add_argument("--output-root", default="research/results"); a=ap.parse_args()
    root=Path(a.source_root); out=Path(a.output_root); rows=[]; missing=[]
    for run_id in RUN_IDS:
        run=root/run_id
        if not run.is_dir(): missing.append(run_id); continue
        for case_dir in sorted(p for p in run.iterdir() if p.is_dir()):
            log=case_dir/"ea_mirror.log"
            if not log.exists(): missing.append(f"{run_id}/{case_dir.name}/ea_mirror.log"); continue
            case=load_json(case_dir/"case.json"); phase=str(case.get("phase") or "")
            m=re.search(r"dz_w(\d{3})_", phase)
            diagnostics,_=extract_diagnostics(read_text(log))
            for d in diagnostics:
                if d.get("classification") != "POSSIBLE_FIBO_PULLBACK": continue
                native=all(k in d for k in ("paf_candidate_direction","paf_direction_is_usable_for_first_touch","paf_direction_source","paf_direction_reason","paf_fibo_direction_gap_reason"))
                rows.append({"run_id":run_id,"window_index":int(m.group(1)) if m else "","phase":phase,"event_time":d.get("time",""),"runtime_symbol":case.get("actual_symbol",case.get("symbol","")),"timeframe":case.get("timeframe",""),"authoritative_source":"ea_mirror.log","case_id":case.get("case_id",case_dir.name),"classification":d.get("classification",""),"paf_candidate_direction":d.get("paf_candidate_direction",""),"paf_direction_is_usable_for_first_touch":d.get("paf_direction_is_usable_for_first_touch",""),"paf_direction_source":d.get("paf_direction_source",""),"paf_direction_reason":d.get("paf_direction_reason",""),"paf_fibo_direction_gap_reason":d.get("paf_fibo_direction_gap_reason",""),"schema_origin":"NATIVE" if native else "LEGACY_NORMALIZED"})
    if missing: print(json.dumps({"status":"BLOCKED_SOURCE_ARTIFACT_MISSING","missing":missing},indent=2)); return 2
    out.mkdir(parents=True,exist_ok=True); csv_path=out/"checkpoint_ef_paf_fibo_row_level_diagnostics.csv"
    with csv_path.open("w",newline="",encoding="utf-8-sig") as f: w=csv.DictWriter(f,fieldnames=FIELDS); w.writeheader(); w.writerows(rows)
    usable=Counter(str(r["paf_direction_is_usable_for_first_touch"]).lower() for r in rows); gaps=Counter(r["paf_fibo_direction_gap_reason"] for r in rows if str(r["paf_direction_is_usable_for_first_touch"]).lower()!="true")
    summary={"execution_status":"PASS","source_runs":list(RUN_IDS),"row_count":len(rows),"usable_true":usable["true"],"usable_false":usable["false"],"gap_reasons":dict(gaps),"window_count":len({r["window_index"] for r in rows}),"reconciliation_pass":len(rows)==2353 and usable["true"]==1600 and usable["false"]==753 and gaps==Counter({"PRICE_BETWEEN_EMAS":554,"TREND_ALIGNMENT_CONFLICT":198,"EMA_SLOPE_FLAT":1}) and len({r["window_index"] for r in rows})==156,"no_mt5_run":True,"profitability_claim":False}
    (out/"checkpoint_ef_paf_fibo_row_level_summary.json").write_text(json.dumps(summary,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    (out/"checkpoint_ef_paf_fibo_row_level_summary.md").write_text("# Checkpoint EF Row-Level Extraction\n\n"+"\n".join(f"- {k}: `{v}`" for k,v in summary.items())+"\n",encoding="utf-8")
    print(json.dumps(summary,indent=2)); return 0 if summary["reconciliation_pass"] else 1
if __name__=="__main__": raise SystemExit(main())
