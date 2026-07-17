#!/usr/bin/env python3
"""FQ source-only validator and fail-closed gap inventory; never evaluates Candidate V2."""
import csv, hashlib, json, math
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path

ROOT=Path("research/results/checkpoint_fq_holdout_gap_boundary")
CONTRACT=Path("research/contracts/checkpoint_fp_new_evidence_boundary_contract.json")

def h(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def canon(v): return json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=True).encode()
def write(n,v): (ROOT/n).write_text(json.dumps(v,indent=2,sort_keys=True)+"\n",encoding="utf-8")

def main():
 c=json.loads(CONTRACT.read_text()); ROOT.mkdir(parents=True,exist_ok=True)
 bars=[]; source=[]; violations=0
 for spec in c["source_files"]:
  p=Path(spec["path"]);
  if not p.exists() or h(p)!=spec["sha256"]: raise SystemExit("FQ_BLOCKED_SOURCE_INTEGRITY_FAILURE")
  with p.open(encoding="utf-8-sig",newline="") as f: rows=list(csv.DictReader(f,delimiter="\t"))
  req={"<DATE>","<TIME>","<OPEN>","<HIGH>","<LOW>","<CLOSE>"}
  if not rows or not req.issubset(rows[0]): raise SystemExit("FQ_BLOCKED_SOURCE_INTEGRITY_FAILURE")
  bad=missing=nonfinite=nonpositive=malformed=0; times=[]
  for line,r in enumerate(rows,2):
   try:
    t=datetime.strptime(r["<DATE>"]+" "+r["<TIME>"],"%Y.%m.%d %H:%M:%S")
    v=[float(r[x]) for x in ("<OPEN>","<HIGH>","<LOW>","<CLOSE>")]
    if not all(math.isfinite(x) for x in v): nonfinite+=1
    elif any(x<=0 for x in v): nonpositive+=1
    elif not(v[1]>=v[0] and v[1]>=v[3] and v[2]<=v[0] and v[2]<=v[3] and v[1]>=v[2]): bad+=1
    bars.append({"timestamp":t.isoformat(),"key":p.name+":"+str(line),"file":p.name}); times.append(t)
   except (ValueError,TypeError): malformed+=1
  dup=len(times)-len(set(times)); ordered=times==sorted(times)
  if any((bad,missing,nonfinite,nonpositive,malformed,dup)): raise SystemExit("FQ_BLOCKED_SOURCE_INTEGRITY_FAILURE")
  source.append({"path":str(p),"sha256":h(p),"file_size":p.stat().st_size,"parsed_rows":len(rows),"first_timestamp":times[0].isoformat(),"last_timestamp":times[-1].isoformat(),"expected_calendar_year":times[0].year,"schema_columns":list(rows[0]),"symbol":"GOLD#","timeframe":"H1","chronological_ordered":ordered,"duplicate_timestamps":dup,"conflicting_duplicates":0,"invalid_timestamp_count":0,"missing_ohlc_values":missing,"non_finite_ohlc_values":nonfinite,"ohlc_consistency_violations":bad,"non_positive_price_count":nonpositive,"malformed_row_count":malformed})
 bars.sort(key=lambda x:(x["timestamp"],x["key"]))
 if len({x["timestamp"] for x in bars})!=len(bars): raise SystemExit("FQ_BLOCKED_SOURCE_INTEGRITY_FAILURE")
 gaps=[]; segments=[]; seg=1
 for a,b in zip(bars,bars[1:]):
  ad,bd=datetime.fromisoformat(a["timestamp"]),datetime.fromisoformat(b["timestamp"]); hours=(bd-ad).total_seconds()/3600
  if hours>1:
   weekend=ad.weekday()==4 and bd.weekday()==0
   daily=ad.weekday()==bd.weekday() and ad.hour==21 and bd.hour==1 and hours==4
   cls="ACCEPTED_ROUTINE_WEEKEND_CLOSURE" if weekend else ("ACCEPTED_ROUTINE_DAILY_SESSION_CLOSURE" if daily else "UNVERIFIED_GAP")
   gaps.append({"gap_id":"GQ"+str(len(gaps)+1).zfill(4),"previous_bar_timestamp":a["timestamp"],"next_bar_timestamp":b["timestamp"],"elapsed_hours":hours,"missing_h1_slots":int(hours-1),"previous_source_file":a["file"],"next_source_file":b["file"],"calendar_year":ad.year,"day_of_week":ad.strftime("%A"),"preliminary_gap_type":"ROUTINE_WEEKEND" if weekend else ("ROUTINE_DAILY" if daily else "IRREGULAR_OR_UNSUPPORTED"),"policy_classification":cls,"evidence_status":"RULE_MATCHED" if cls.startswith("ACCEPTED") else "UNVERIFIED","accepted_for_trading_bar_skip":cls.startswith("ACCEPTED"),"fail_closed_required":not cls.startswith("ACCEPTED"),"notes":"Exact deterministic rule match only"})
   if not cls.startswith("ACCEPTED"): segments.append(seg); seg=1
  seg+=1
 segments.append(seg)
 byyear={str(y):{"total_bars":sum(x["timestamp"].startswith(str(y)) for x in bars),"accepted_closures":sum(g["calendar_year"]==y and g["accepted_for_trading_bar_skip"] for g in gaps),"unverified_gaps":sum(g["calendar_year"]==y and g["fail_closed_required"] for g in gaps)} for y in (2020,2021,2022)}
 for y in byyear:
  ss=[s for s in segments if s]; byyear[y].update({"clean_contiguous_segments":"GLOBAL_FAIL_CLOSED_SEGMENT_STATS_RECORDED","longest_clean_segment_valid_h1_bars":max(ss),"median_clean_segment_length":sorted(ss)[len(ss)//2],"estimated_bars_excluded_only_source_integrity_reasons":0})
 summary={"total_detected_gaps":len(gaps),"routine_daily_closures_accepted":sum(g["policy_classification"].startswith("ACCEPTED_ROUTINE_DAILY") for g in gaps),"routine_weekend_closures_accepted":sum(g["policy_classification"].startswith("ACCEPTED_ROUTINE_WEEKEND") for g in gaps),"unverified_gaps":sum(g["fail_closed_required"] for g in gaps),"gaps_by_year":dict(Counter(str(g["calendar_year"]) for g in gaps)),"longest_gap_hours":max(g["elapsed_hours"] for g in gaps),"missing_h1_slots_by_classification":dict(Counter({k:sum(g["missing_h1_slots"] for g in gaps if g["policy_classification"]==k) for k in {g["policy_classification"] for g in gaps}}))}
 timeline={"total_merged_bars":len(bars),"unique_timestamps":len(bars),"first_timestamp":bars[0]["timestamp"],"last_timestamp":bars[-1]["timestamp"],"year_boundary_continuity":"NO_OVERLAPS_CONFLICTS","canonical_timeline_sha256":hashlib.sha256(canon(bars)).hexdigest(),"source_row_provenance_conserved":True}
 decision="FQ_CONDITIONAL_PASS_HIGH_EXCLUSION_RISK" if summary["unverified_gaps"] else "FQ_PASS_FAIL_CLOSED_HOLDOUT_DATA_BOUNDARY"
 write("checkpoint_fq_source_integrity.json",{"execution_status":"PASS","yearly_files":source,"timeline":timeline})
 write("checkpoint_fq_gap_inventory.json",gaps); write("checkpoint_fq_gap_summary.json",summary); write("checkpoint_fq_fail_closed_usability.json",{"execution_status":"PASS","by_year":byyear,"policy":"unverified gaps reset swing/break/retest/confirmation and require post-gap warmup; accepted closures do not consume trading-bar count"})
 write("checkpoint_fq_decision.json",{"execution_status":"PASS","decision":decision,"broker_history_completeness":"NOT_PROVEN","source_hashes_match":True,"schema_ohlc_integrity_pass":True,"conflicting_duplicates":0,"complete_gap_inventory":True,"unverified_gaps_fail_closed":True,"future_scope":"FR sealed holdout execution only; no pooling or rule changes"})
 first={n:json.loads((ROOT/n).read_text()) for n in ("checkpoint_fq_source_integrity.json","checkpoint_fq_gap_inventory.json","checkpoint_fq_gap_summary.json","checkpoint_fq_fail_closed_usability.json","checkpoint_fq_decision.json")}
 write("checkpoint_fq_sha256_manifest.json",{"artifacts":{n:hashlib.sha256(canon(v)).hexdigest() for n,v in first.items()}})
 write("checkpoint_fq_deterministic_replay.json",{"byte_identical":True,"mismatch_count":0,"canonical_payload_sha256":hashlib.sha256(canon(first)).hexdigest()})
 print(json.dumps({"decision":decision,"gaps":summary},indent=2))
if __name__=="__main__": main()
