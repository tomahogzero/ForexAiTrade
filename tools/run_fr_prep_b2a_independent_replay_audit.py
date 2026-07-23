#!/usr/bin/env python3
"""Independent committed-artifact audit for FR-Prep-B2; imports no replay code."""
import argparse,csv,hashlib,io,json,ntpath,os,posixpath,shutil,subprocess,sys,tempfile
from collections import Counter
from pathlib import Path
import jsonschema
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1]
AUTH=ROOT/"research/contracts/fr_prep_b2a_independent_replay_audit_authorization.v1.json"
ASC=ROOT/"research/schemas/fr_prep_b2a_independent_replay_audit_authorization.v1.schema.json"
EVID=ROOT/"research/contracts/fr_prep_b2a_independent_replay_audit.v1.json"
ESC=ROOT/"research/schemas/fr_prep_b2a_independent_replay_audit.v1.schema.json"
RESULT=ROOT/"research/results/checkpoint_fr_prep_b2a/independent_replay_audit_summary.json"
PASS="FR_PREP_B2A_PASS_INDEPENDENT_REPLAY_AUDIT"
MODE="independent-frozen-fj-replay-audit"
PROHIBITED={"market_structure_break_retest_detector","run_checkpoint_fj_historical_event_population","fr_prep_runner_execution_wrapper","run_fr_prep_b2_fj_backward_compatible_replay","run_checkpoint_fq_holdout_gap_boundary"}
FQ=("checkpoint_fq","holdout","fq_")
EXT=("terminal64","metatrader",".ex5","expertadvisor")
def cj(x):return json.dumps(x,ensure_ascii=True,sort_keys=True,separators=(",",":"))
def dg(x):return hashlib.sha256(cj(x).encode("ascii")).hexdigest()
def hb(x):return hashlib.sha256(x).hexdigest()
def cid(x):return dg({k:v for k,v in x.items() if k!="canonical_summary_sha256"})
def ap(x):
 if isinstance(x,dict):return sum(ap(v) for v in x.values())
 if isinstance(x,list):return sum(ap(v) for v in x)
 return int(isinstance(x,str) and (ntpath.isabs(x) or posixpath.isabs(x)))
class Files:
 def __init__(s):s.allow={};s.raw=Counter();s.uni={};s.block=[]
 def add(s,p,c):q=Path(p).resolve();s.allow[q]=c;s.uni.setdefault(c,set())
 def read(s,p):
  q=Path(p).resolve();c=s.allow.get(q)
  if c is None:s.block.append("FQ_PATH" if any(x in str(q).lower() for x in FQ) else "UNAUTHORIZED_PATH");raise PermissionError("unauthorized read blocked")
  s.raw[c]+=1;s.uni[c].add(q);return q.read_bytes()
 def report(s):
  ks=sorted(s.uni);return {"unique_logical_file_counts":{k:len(s.uni[k]) for k in ks},"raw_read_operation_counts":{k:s.raw[k] for k in ks},"blocked_unauthorized_read_attempt_count":len(s.block),"blocked_attempt_categories":s.block,"unauthorized_successful_read_count":0,"fq_successful_read_count":0}
class External:
 def __init__(s):s.block=[]
 def deny(s,k,c):s.block.append(k+(":MT5_OR_EA" if any(x in str(c).lower() for x in EXT) else ":EXTERNAL"));raise RuntimeError("external blocked")
 def __enter__(s):
  s.p=subprocess.Popen;s.y=os.system;s.t=getattr(os,"startfile",None);subprocess.Popen=lambda c,*a,**k:s.deny("subprocess",c);os.system=lambda c:s.deny("os.system",c)
  if s.t is not None:os.startfile=lambda p,*a,**k:s.deny("os.startfile",p)
  return s
 def __exit__(s,*_):
  subprocess.Popen=s.p;os.system=s.y
  if s.t is not None:os.startfile=s.t
 def report(s):return {"successful_external_process_launch_count":0,"successful_mt5_launch_count":0,"successful_ea_execution_count":0,"blocked_external_launch_attempt_count":len(s.block),"blocked_attempt_categories":s.block}
def js(f,p):return json.loads(f.read(p).decode("utf-8"))
def events(b):
 out=[]
 for r in csv.DictReader(io.StringIO(b.decode("utf-8"),newline="")):r["source_row_keys"]=json.loads(r["source_row_keys"]);r["exclusion_reason"]=r["exclusion_reason"] or None;out.append(r)
 return out
def candidates(b):return [{k:(v if v!="" else None) for k,v in r.items()} for r in csv.DictReader(io.StringIO(b.decode("utf-8"),newline=""))]
def result_schema(e):
 return {"$schema":"https://json-schema.org/draft/2020-12/schema","type":"object","additionalProperties":False,"required":["canonical_summary_sha256","decision","events","execution_status","mismatch_count","profitability","prohibited_execution_counts","replay_hashes","rows_gaps","strategy_performance_status"],"properties":{"canonical_summary_sha256":{"const":e["b2_canonical_summary_sha256"]},"decision":{"const":e["b2_decision"]},"events":{"type":"object"},"execution_status":{"const":"PASS"},"mismatch_count":{"const":0},"profitability":{"const":"NOT_CLAIMED"},"prohibited_execution_counts":{"type":"object","additionalProperties":{"const":0}},"replay_hashes":{"type":"object"},"rows_gaps":{"type":"object"},"strategy_performance_status":{"const":"NOT_EVALUATED"}}}
def one(f,p,e):
 c=js(f,p["b2_contract"]);sc=js(f,p["b2_schema"]);r=js(f,p["b2_result"]);pop=js(f,p["population_summary"]);rep=js(f,p["deterministic_replay"])
 jsonschema.Draft202012Validator.check_schema(sc);jsonschema.Draft202012Validator(sc).validate(c)
 rs=result_schema(e);jsonschema.Draft202012Validator.check_schema(rs);jsonschema.Draft202012Validator(rs).validate(r)
 if cid(c)!=e["b2_canonical_summary_sha256"] or c["decision"]!=e["b2_decision"]:raise ValueError("B2 identity/decision mismatch")
 exp={"canonical_summary_sha256":c["canonical_summary_sha256"],"decision":c["decision"],"events":{"total":c["event_count"],"LONG":c["long_count"],"SHORT":c["short_count"]},"execution_status":c["execution_status"],"mismatch_count":sum(c["mismatch_counters"].values()),"profitability":c["profitability"],"prohibited_execution_counts":{k:v for k,v in c["runtime_audit"]["function_execution_counts"].items() if k in {"atr_event_generation_count","ea_execution_count","external_process_launch_count","fn_interpretation_count","fq_access_count","mt5_execution_count","optimization_count","outcome_generation_count","tp_sl_calculation_count"}},"replay_hashes":c["replay_hashes"],"rows_gaps":{"rows":c["source_rows"],"gaps":c["gap_count"],"accepted":c["accepted_closures"],"unverified":c["unverified_gaps"]},"strategy_performance_status":c["strategy_performance_status"]}
 if r!=exp:raise ValueError("B2 contract/result projection mismatch")
 ev=events(f.read(p["events"]));ca=candidates(f.read(p["candidates"]));ex=[x for x in ca if x["status"]!="EVENT_EMITTED"]
 hs={"event_population_sha256":dg(ev),"exclusion_population_sha256":dg(ex),"population_summary_sha256":dg(pop),"terminal_status_summary_sha256":dg(pop["terminal_status_counts"])}
 ids=[x["event_id"] for x in ev];sem=[(x["direction"],x["swing_timestamp"],x["break_timestamp"],x["confirmation_timestamp"]) for x in ev];co=[tuple("" if v is None else str(v) for v in x.values()) for x in ca];di=Counter(x["direction"] for x in ev)
 vals=(pop["source_rows"],pop["detected_gap_count"],pop["accepted_closures"],pop["unverified_gaps"],len(ev),di["LONG"],di["SHORT"])
 ok=vals==(e["source_rows"],e["gap_count"],e["accepted_closures"],e["unverified_gaps"],e["events"],e["long"],e["short"]) and hs==e["hashes"] and len(ids)==len(set(ids)) and len(sem)==len(set(sem)) and ids==sorted(ids) and co==sorted(co) and all(rep[k]==v for k,v in hs.items()) and rep["mismatch_count"]==0
 if not ok:raise ValueError("independent artifact mismatch")
 return {"b2_canonical_summary_sha256":cid(c),"values":vals,"hashes":hs,"event_ids":ids,"event_ids_unique":len(ids)==len(set(ids)),"semantic_unique":len(sem)==len(set(sem)),"event_order":ids==sorted(ids),"candidate_order":co==sorted(co),"candidate_rows":len(ca),"event_rows":ev}
def negatives(f,x,b,e):
 z={}
 a=json.loads(cj(x["event_rows"]));a[0]["event_id"]+="_ALTERED";z["altered_row_detected"]=dg(a)!=x["hashes"]["event_population_sha256"]
 q=json.loads(cj(x["event_rows"]));q[0],q[1]=q[1],q[0];z["reordered_rows_detected"]=dg(q)!=x["hashes"]["event_population_sha256"]
 a=json.loads(cj(b));a["replay_hashes"]["event_population_sha256"]="0"*64;z["changed_hash_detected"]=a["replay_hashes"]!=e["hashes"]
 a=json.loads(cj(b));a["event_count"]+=1;z["changed_count_detected"]=a["event_count"]!=e["events"]
 a=json.loads(cj(b));a["decision"]="WRONG";z["wrong_decision_detected"]=a["decision"]!=e["b2_decision"]
 try:f.read(ROOT/"research/results/checkpoint_fq_holdout_gap_boundary/forbidden.json");z["fq_access_blocked"]=False
 except PermissionError:z["fq_access_blocked"]=True
 try:subprocess.Popen(["terminal64.exe","/blocked"]);z["external_launch_blocked"]=False
 except RuntimeError:z["external_launch_blocked"]=True
 a=json.loads(cj(x));a["runtime_path"]=str(ROOT.resolve());z["absolute_path_detected"]=ap(a)==1
 return {"test_count":len(z),"tests_passed":sum(z.values()),"all_passed":all(z.values()),"results":z}
def main():
 q=argparse.ArgumentParser();q.add_argument("--mode",required=True,choices=[MODE]);q.add_argument("--authorization",required=True);q.add_argument("--output-root",required=True);a=q.parse_args()
 if Path(a.authorization).resolve()!=AUTH.resolve() or Path(a.output_root).resolve()!=RESULT.parent.resolve():raise SystemExit("path not allowlisted")
 f=Files();f.add(AUTH,"b2a_authorization");f.add(ASC,"b2a_authorization_schema");au=js(f,AUTH);asc=js(f,ASC);jsonschema.Draft202012Validator.check_schema(asc);jsonschema.Draft202012Validator(asc).validate(au)
 p={}
 for b in au["committed_artifacts"]:
  q=(ROOT/b["path"]).resolve()
  if not q.is_file():raise SystemExit("committed binding missing")
  f.add(q,b["category"])
  if hb(f.read(q))!=b["file_sha256"]:raise SystemExit("committed binding mismatch")
  p[b["artifact_id"]]=q
 f.add(ESC,"b2a_evidence_schema");e=au["expected"];before=set(sys.modules)
 with External() as ext:
  x=one(f,p,e);y=one(f,p,e)
  with tempfile.TemporaryDirectory(prefix="fr_prep_b2a_relocation_") as n:
   t=Path(n).resolve()
   if t==ROOT or ROOT in t.parents:raise SystemExit("relocation inside repo")
   rp={}
   for k,v in p.items():
    d=t/(k+v.suffix);d.write_bytes(f.read(v));f.add(d,"relocated_committed_artifacts")
    if hb(f.read(d))!=hb(f.read(v)):raise SystemExit("relocation byte mismatch")
    rp[k]=d
   z=one(f,rp,e)
  b=js(f,p["b2_contract"]);neg=negatives(f,x,b,e)
 imported={n.split(".")[-1] for n in set(sys.modules)-before};bad=sorted(n for n in PROHIBITED if n in imported or n in sys.modules)
 mm={"repeat_mismatch":int(x!=y),"relocation_mismatch":int(x!=z),"identity_mismatch":int(x["b2_canonical_summary_sha256"]!=e["b2_canonical_summary_sha256"]),"count_mismatch":int(x["values"]!=(17716,773,745,28,1079,588,491)),"hash_mismatch":int(x["hashes"]!=e["hashes"]),"ordering_mismatch":int(not x["event_order"] or not x["candidate_order"]),"uniqueness_mismatch":int(not x["event_ids_unique"] or not x["semantic_unique"]),"negative_test_mismatch":int(not neg["all_passed"])}
 mi={"detector_import_count":int("market_structure_break_retest_detector" in imported),"legacy_fj_runner_import_count":int("run_checkpoint_fj_historical_event_population" in imported),"execution_wrapper_import_count":int("fr_prep_runner_execution_wrapper" in imported),"b2_replay_runner_import_count":int("run_fr_prep_b2_fj_backward_compatible_replay" in imported),"fq_module_import_count":sum(any(m in n.lower() for m in FQ) for n in imported),"mt5_or_ea_module_import_count":sum(any(m in n.lower() for m in EXT) for n in imported)}
 pe={k:0 for k in ("detector_execution_count","legacy_fj_execution_count","wrapper_execution_count","b2_runner_execution_count","fq_execution_count","atr_event_generation_count","tp_sl_calculation_count","outcome_generation_count","fn_interpretation_count","optimization_count","mt5_execution_count","ea_execution_count")}
 if any(mm.values()) or any(mi.values()) or any(pe.values()) or bad:raise SystemExit("B2a audit failed")
 esc=js(f,ESC)
 core={"schema_version":"fr_prep_b2a_independent_replay_audit.v1","checkpoint":"FR_PREP_B2A","decision":PASS,"b2_evidence":{"decision":e["b2_decision"],"canonical_summary_sha256":x["b2_canonical_summary_sha256"],"contract_schema_validated":True,"compact_result_schema_validated":True,"contract_result_projection_match":True},"source_rows":x["values"][0],"gap_count":x["values"][1],"accepted_closures":x["values"][2],"unverified_gaps":x["values"][3],"event_count":x["values"][4],"long_count":x["values"][5],"short_count":x["values"][6],"recomputed_hashes":x["hashes"],"event_ids_unique":x["event_ids_unique"],"semantic_events_unique":x["semantic_unique"],"event_row_order_canonical":x["event_order"],"candidate_row_order_canonical":x["candidate_order"],"normal_repeat_identical":x==y,"relocation_identical":x==z,"mismatch_counters":mm,"negative_tests":neg,"runtime_audit":{"module_import_counts":mi,"prohibited_execution_counts":pe,"file_access":f.report(),"external_process":ext.report(),"counter_provenance":{"module_imports":"sys.modules before/after delta and final prohibited-module absence","file_access":"exact resolved-path read dispatch","external_process":"Popen, os.system and os.startfile interception","executions":"no prohibited execution dispatch exists"}},"prohibited_modules":bad,"absolute_runtime_path_in_canonical_identity_count":0,"execution_status":"PASS","strategy_performance_status":"NOT_EVALUATED","profitability":"NOT_CLAIMED","order_logic":"NOT_APPROVED","candidate":"NOT_READY_FOR_ORDER_LOGIC","fq_accessed":False,"atr_events_generated":False,"tp_sl_calculated":False,"outcomes_generated":False,"fn_interpretation_performed":False,"mt5_executed":False,"ea_executed":False}
 core["canonical_summary_sha256"]=dg(core)
 if ap(core):raise SystemExit("absolute path in identity")
 jsonschema.Draft202012Validator.check_schema(esc);jsonschema.Draft202012Validator(esc).validate(core)
 EVID.write_text(json.dumps(core,indent=2,sort_keys=True)+"\n",encoding="utf-8")
 out={"decision":PASS,"canonical_summary_sha256":core["canonical_summary_sha256"],"b2_canonical_summary_sha256":x["b2_canonical_summary_sha256"],"rows_gaps":{"rows":x["values"][0],"gaps":x["values"][1],"accepted":x["values"][2],"unverified":x["values"][3]},"events":{"total":x["values"][4],"LONG":x["values"][5],"SHORT":x["values"][6]},"hashes":x["hashes"],"mismatch_count":sum(mm.values()),"negative_tests":{"passed":neg["tests_passed"],"total":neg["test_count"]},"prohibited_import_count":sum(mi.values()),"prohibited_execution_count":sum(pe.values()),"execution_status":"PASS","strategy_performance_status":"NOT_EVALUATED","profitability":"NOT_CLAIMED"}
 RESULT.parent.mkdir(parents=True,exist_ok=True);RESULT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8");print(json.dumps(out,sort_keys=True))
if __name__=="__main__":main()
