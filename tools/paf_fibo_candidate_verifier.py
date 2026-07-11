#!/usr/bin/env python3
"""Offline verifier for PAF_FIBO_USABLE_DIRECTION_V1. Never emits trade signals."""
from __future__ import annotations
import argparse, csv, json
from collections import Counter
from pathlib import Path

REQUIRED=("run_id","window_index","phase","event_time","runtime_symbol","timeframe","authoritative_source","case_id","classification","paf_candidate_direction","paf_direction_is_usable_for_first_touch","paf_direction_source","paf_direction_reason","paf_fibo_direction_gap_reason","schema_origin")
DIRECTIONS={"BUY","SELL","DIRECTION_UNKNOWN"}; BOOLS={"true","false"}; GAPS={"NONE","PRICE_BETWEEN_EMAS","TREND_ALIGNMENT_CONFLICT","EMA_SLOPE_FLAT"}; ORIGINS={"NATIVE","LEGACY_NORMALIZED"}

def classify(r):
    missing=[k for k in REQUIRED if not str(r.get(k,"")).strip()]
    if missing: return "INVALID_DATA","MISSING_REQUIRED:"+",".join(missing)
    if r["paf_candidate_direction"] not in DIRECTIONS or r["paf_direction_is_usable_for_first_touch"].lower() not in BOOLS or r["paf_fibo_direction_gap_reason"] not in GAPS or r["schema_origin"] not in ORIGINS: return "INVALID_DATA","UNKNOWN_ENUM"
    if r["classification"] != "POSSIBLE_FIBO_PULLBACK": return "NOT_APPLICABLE","NON_FIBO_CLASSIFICATION"
    usable=r["paf_direction_is_usable_for_first_touch"].lower()=="true"; direction=r["paf_candidate_direction"]; gap=r["paf_fibo_direction_gap_reason"]
    if (usable and direction not in {"BUY","SELL"}) or (usable and gap!="NONE") or (not usable and direction in {"BUY","SELL"} and gap=="NONE"): return "INVALID_DATA","CONFLICTING_FIELDS"
    if not usable or direction not in {"BUY","SELL"} or gap!="NONE": return "REJECTED_DIRECTION_GAP",gap if gap!="NONE" else "DIRECTION_NOT_USABLE"
    return "ELIGIBLE_DIAGNOSTIC_ROW","USABLE_DIRECTION_COMPLETE"

def verify(rows):
    results=[]
    for i,r in enumerate(rows,2):
        outcome,reason=classify(r); results.append({**r,"candidate_outcome":outcome,"candidate_reason":reason,"source_row":i})
    counts=Counter(x["candidate_outcome"] for x in results)
    return results,{"input_rows":len(rows),"outcome_counts":dict(counts),"conservation_pass":sum(counts.values())==len(rows),"eligible_invariant_pass":all(x["paf_candidate_direction"] in {"BUY","SELL"} and x["paf_direction_is_usable_for_first_touch"].lower()=="true" and x["paf_fibo_direction_gap_reason"]=="NONE" for x in results if x["candidate_outcome"]=="ELIGIBLE_DIAGNOSTIC_ROW")}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--input",required=True); ap.add_argument("--output-csv"); ap.add_argument("--summary-json"); a=ap.parse_args()
    with open(a.input,encoding="utf-8-sig",newline="") as f: rows=list(csv.DictReader(f))
    results,summary=verify(rows)
    if a.output_csv:
        Path(a.output_csv).parent.mkdir(parents=True,exist_ok=True)
        with open(a.output_csv,"w",encoding="utf-8-sig",newline="") as f: w=csv.DictWriter(f,fieldnames=results[0].keys()); w.writeheader(); w.writerows(results)
    if a.summary_json: Path(a.summary_json).write_text(json.dumps(summary,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(summary,indent=2)); return 0 if summary["conservation_pass"] and summary["eligible_invariant_pass"] else 1
if __name__=="__main__": raise SystemExit(main())
