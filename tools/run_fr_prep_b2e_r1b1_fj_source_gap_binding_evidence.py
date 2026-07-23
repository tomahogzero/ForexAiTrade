#!/usr/bin/env python3
"""Internal R1b-1 frozen FJ binding validation with observed runtime audit."""
import builtins,copy,csv,hashlib,importlib,json,ntpath,os,posixpath,shutil,subprocess,sys,tempfile
from collections import Counter
from datetime import datetime
from decimal import Decimal
from pathlib import Path
import jsonschema

ROOT=Path(__file__).resolve().parents[1]
AUTH=ROOT/"research/contracts/fr_prep_b2e_r1b_fj_real_data_authorization.v1.json"
ASC=ROOT/"research/schemas/fr_prep_b2e_r1b_fj_real_data_authorization.v1.schema.json"
ALLOW=["ACCEPTED_DAILY_BROKER_SESSION_GAP","ACCEPTED_WEEKEND_MARKET_CLOSURE","BLOCKED_UNCLASSIFIED_GAP"]
IMODS={"historical_source_adapter":"source_adapter_import_count","gap_policy_adapter":"gap_adapter_import_count","dataset_execution_descriptor_adapter":"descriptor_adapter_import_count","market_structure_break_retest_detector":"detector_import_count","run_checkpoint_fi_detector_fixtures":"fi_import_count","run_checkpoint_fj_historical_event_population":"legacy_runner_import_count","fr_prep_runner_execution_wrapper":"wrapper_import_count","run_checkpoint_fq_holdout_gap_boundary":"fq_runner_import_count"}
ALLOWED={"historical_source_adapter","gap_policy_adapter"}
EXE=("descriptor_composition_count","detector_execution_count","fi_execution_count","legacy_runner_execution_count","wrapper_execution_count","fq_execution_count","event_population_emit_count","atr_event_emit_count","tp_sl_calculation_count","outcome_emit_count","fn_interpretation_count")
FCATS=("committed_fj_source_manifest_evidence","approved_original_fj_source_files","authorized_eo_fj_gap_policy","relocated_temporary_files","unauthorized_files","fq_source_files","fq_gap_inventories")

def cj(x):return json.dumps(x,ensure_ascii=True,sort_keys=True,separators=(",",":"))
def hb(b):return hashlib.sha256(b).hexdigest()
def hf(p):
 d=hashlib.sha256()
 with Path(p).open("rb") as f:
  for c in iter(lambda:f.read(1048576),b""):d.update(c)
 return d.hexdigest()
def base(n):return n.split(".")[-1]
def badmods():return sorted(n for n in sys.modules if base(n) in set(IMODS)-ALLOWED)

class RuntimeAudit:
 def __init__(s):
  s.before=set(sys.modules);s.dispatch=[];s.rejected=[];s.calls=Counter();s.launches=[]
 def prof(s,frame,event,arg):
  del arg
  if event!="call":return
  m=base(str(frame.f_globals.get("__name__","")));f=frame.f_code.co_name.lower()
  mp={"dataset_execution_descriptor_adapter":"descriptor_composition_count","market_structure_break_retest_detector":"detector_execution_count","run_checkpoint_fi_detector_fixtures":"fi_execution_count","run_checkpoint_fj_historical_event_population":"legacy_runner_execution_count","fr_prep_runner_execution_wrapper":"wrapper_execution_count","run_checkpoint_fq_holdout_gap_boundary":"fq_execution_count"}
  if m in mp:s.calls[mp[m]]+=1
  if m=="run_checkpoint_fj_historical_event_population":s.calls["event_population_emit_count"]+=1
  if "atr" in f and "event" in f:s.calls["atr_event_emit_count"]+=1
  if "tp_sl" in f or "take_profit_stop_loss" in f:s.calls["tp_sl_calculation_count"]+=1
  if "outcome" in f and ("emit" in f or "generate" in f):s.calls["outcome_emit_count"]+=1
  if "interpret" in f and "fn" in f:s.calls["fn_interpretation_count"]+=1
 def block(s,cmd):
  s.launches.append(" ".join(map(str,cmd)) if isinstance(cmd,(list,tuple)) else str(cmd));raise RuntimeError("external execution prohibited")
 def __enter__(s):
  s.oldprof=sys.getprofile();sys.setprofile(s.prof);s.oldpop=subprocess.Popen;s.oldsys=os.system
  subprocess.Popen=lambda cmd,*a,**k:s.block(cmd);os.system=lambda cmd:s.block(cmd)
  s.oldstart=getattr(os,"startfile",None)
  if s.oldstart is not None:os.startfile=lambda path,*a,**k:s.block(path)
  return s
 def __exit__(s,*x):
  subprocess.Popen=s.oldpop;os.system=s.oldsys;sys.setprofile(s.oldprof)
  if s.oldstart is not None:os.startfile=s.oldstart
 def imp(s,n):
  if n not in ALLOWED:s.rejected.append(n);raise RuntimeError("unauthorized import")
  s.dispatch.append(n);return importlib.import_module(n)
 def imports(s):
  added=set(sys.modules)-s.before
  return {v:sum(base(x)==k for x in added) for k,v in IMODS.items()}
 def executions(s):return {k:s.calls.get(k,0) for k in EXE}
 def external(s):
  low=[x.lower() for x in s.launches]
  return {"subprocess_launch_count":len(low),"mt5_terminal_launch_count":sum("terminal64.exe" in x for x in low),"ea_execution_count":sum(".ex5" in x for x in low),"observed_launches":s.launches}

class FileAudit:
 def __init__(s):
  s.allowed={};s.unique={k:set() for k in FCATS};s.raw=Counter()
 def add(s,p,c):s.allowed[Path(p).resolve()]=c
 def see(s,p,mode):
  if isinstance(p,int) or ("r" not in mode and "+" not in mode):return
  q=Path(p).resolve();c=s.allowed.get(q)
  if c is None:s.raw["unauthorized_files"]+=1;s.unique["unauthorized_files"].add(q);raise RuntimeError("unauthorized read-open: "+str(q))
  s.raw[c]+=1;s.unique[c].add(q)
 def __enter__(s):
  s.bo=builtins.open;s.po=Path.open
  def bo(p,mode="r",*a,**k):s.see(p,mode);return s.bo(p,mode,*a,**k)
  def po(p,mode="r",*a,**k):s.see(p,mode);return s.po(p,mode,*a,**k)
  builtins.open=bo;Path.open=po;return s
 def __exit__(s,*x):builtins.open=s.bo;Path.open=s.po
 def report(s):
  return {"unique_logical_file_counts":{k:len(s.unique[k]) for k in FCATS},"raw_read_open_operation_counts":{k:s.raw.get(k,0) for k in FCATS},"accessed_file_names_by_category":{k:sorted(p.name for p in s.unique[k]) for k in FCATS}}

def authorize(p):
 if p.resolve()!=AUTH.resolve():raise ValueError("wrong authorization path")
 b=p.read_bytes();a=json.loads(b.decode());sc=json.loads(ASC.read_text(encoding="utf-8"))
 jsonschema.Draft202012Validator.check_schema(sc);jsonschema.Draft202012Validator(sc).validate(a)
 if badmods():raise RuntimeError("prohibited pre-authorization import")
 q=a["timestamp_projection_binding"]
 for pk,hk in (("contract_path","contract_sha256"),("helper_path","helper_sha256"),("projection_runner_path","projection_runner_sha256"),("r1b1_internal_runner_path","r1b1_internal_runner_sha256")):
  if hf(ROOT/q[pk])!=q[hk]:raise ValueError("projection binding mismatch: "+pk)
 pc=json.loads((ROOT/q["contract_path"]).read_text(encoding="utf-8"))
 if pc["real_data_access_allowed"] is not False or pc["helper_fixture_deterministic_sha256"]!=q["r1a1_deterministic_sha256"]:raise ValueError("projection contract changed")
 return a,hb(b)
def sourcepaths(root,a):
 r=root.resolve()
 if not r.is_dir():raise ValueError("source root missing")
 ps=[(r/x["file_name"]).resolve() for x in a["frozen_sources"]]
 if any(p.parent!=r or not p.is_file() for p in ps):raise ValueError("approved source missing")
 return ps
def history(a):
 z=a["historical_source_manifest_evidence"];b=(ROOT/z["path"]).read_bytes()
 if hb(b)!=z["sha256"]:raise ValueError("source evidence hash mismatch")
 h=json.loads(b.decode());out=[]
 for f in a["frozen_sources"]:
  m=[x for x in h["sources"] if (x.get("file") or x.get("file_name") or Path(x.get("path","")).name)==f["file_name"]]
  if len(m)!=1 or m[0]["sha256"].lower()!=f["sha256"] or m[0].get("row_count",m[0].get("rows"))!=f["expected_rows"]:raise ValueError("historical provenance mismatch")
  out.append(copy.deepcopy(m[0]))
 return out
def dec(x):return format(Decimal(x).normalize(),"f")
def observe(ps,a):
 bars=[];src=[];cols={"<DATE>","<TIME>","<OPEN>","<HIGH>","<LOW>","<CLOSE>"}
 for p,f in zip(ps,a["frozen_sources"]):
  sb=[]
  with p.open(encoding="utf-8-sig",newline="") as h:
   r=csv.DictReader(h,delimiter="\t")
   if r.fieldnames is None or not cols.issubset(r.fieldnames):raise ValueError("MT5 columns mismatch")
   for n,row in enumerate(r,2):
    t=datetime.strptime(row["<DATE>"]+" "+row["<TIME>"],"%Y.%m.%d %H:%M:%S").isoformat()
    q={"timestamp":t,"source_id":f["source_id"],"source_row_key":f["source_id"]+":"+str(n),"open":dec(row["<OPEN>"]),"high":dec(row["<HIGH>"]),"low":dec(row["<LOW>"]),"close":dec(row["<CLOSE>"])}
    sb.append(q);bars.append(q)
  src.append({"source_id":f["source_id"],"file_name":f["file_name"],"row_count":len(sb),"first_timestamp":sb[0]["timestamp"],"last_timestamp":sb[-1]["timestamp"]})
 bars.sort(key=lambda x:(x["timestamp"],x["source_row_key"]));ts=[x["timestamp"] for x in bars]
 return {"derived_at_checkpoint":"FR_PREP_B2E_R1B1","historical_timeline_hash_claimed":False,"algorithm":{"encoding":"UTF-8-SIG","timestamp_format":"%Y.%m.%d %H:%M:%S","decimal_normalization":"Decimal.normalize_then_fixed","ordering":"timestamp_then_source_row_key","canonical_json":"sorted_keys_compact_ascii"},"sources":src,"source_count":len(src),"total_rows":len(bars),"first_timestamp":ts[0],"last_timestamp":ts[-1],"duplicate_timestamps":len(ts)-len(set(ts)),"canonical_timeline_sha256":hb(cj(bars).encode("ascii"))}
def manifest(a,hs,ps,o):
 ss=[];ids=[]
 for h,f,p in zip(hs,a["frozen_sources"],ps):
  ss.append({"source_id":f["source_id"],"file_name":f["file_name"],"path":f["file_name"],"runtime_path":str(p),"sha256":f["sha256"],"size_bytes":h.get("size_bytes"),"row_count":f["expected_rows"],"first_timestamp":h["first_timestamp"],"last_timestamp":h["last_timestamp"]})
  ids.append({"source_id":f["source_id"],"file_name":f["file_name"],"runtime_path":str(p)})
 return {"mapping_profile":"FJ_SOURCE_PROVENANCE_V1","dataset_context":{"dataset_id":a["dataset_id"],"symbol":a["symbol"],"timeframe":a["timeframe"],"boundary_start_timestamp":hs[0]["first_timestamp"],"boundary_end_timestamp":hs[-1]["last_timestamp"],"broker_history_completeness":"NOT_PROVEN","expected_timeline":{"source_count":o["source_count"],"total_rows":o["total_rows"],"first_timestamp":hs[0]["first_timestamp"],"last_timestamp":hs[-1]["last_timestamp"],"duplicate_timestamps":o["duplicate_timestamps"],"canonical_timeline_sha256":o["canonical_timeline_sha256"]}},"provenance":{"symbol":a["symbol"],"timeframe":a["timeframe"],"broker_history_completeness":"NOT_PROVEN","raw_broker_csv_committed":False,"sources":ss},"source_identities":ids}
def derive(a,hs,ps,gp,project,sa,ga):
 for p,f in zip(ps,a["frozen_sources"]):
  if hf(p)!=f["sha256"]:raise ValueError("source hash mismatch")
 o=observe(ps,a)
 if (o["source_count"],o["total_rows"],o["first_timestamp"],o["last_timestamp"],o["duplicate_timestamps"])!=(3,17716,"2023-01-03T01:00:00","2025-12-31T19:00:00",0) or [x["row_count"] for x in o["sources"]]!=[5894,5928,5894]:raise ValueError("observation mismatch")
 p=project(manifest(a,hs,ps,o),"FR_PREP_B2E_R1B1_FROZEN_FJ_PROVENANCE");sr=sa.validate_manifest_data(p["projected_metadata"],ps[0].parent)
 ot={k:o[k] for k in ("source_count","total_rows","first_timestamp","last_timestamp","duplicate_timestamps","canonical_timeline_sha256")}
 if sr["timeline"]!=ot:raise ValueError("source adapter mismatch")
 gh=hf(gp);gm={"schema_version":"gap_policy_manifest.v1","policy_id":"FJ_2023_2025_EO_GAP_POLICY","source_contract_type":"EO_FJ_CSV_V1","runtime_path":str(gp),"artifact_sha256":gh,"classification_allowlist":ALLOW,"expected_entry_count":773,"expected_accepted_closure_count":745,"expected_unverified_gap_count":28,"require_canonical_source_order":False,"broker_history_completeness":"NOT_PROVEN"}
 g1=ga.validate_gap_policy_data(gm,gp.parent);cc=dict(sorted(Counter(x["policy_classification"] for x in g1["entries"]).items()));ac=sum(x["closure_disposition"]=="ACCEPTED_CLOSURE" for x in g1["entries"]);uv=len(g1["entries"])-ac;ai=ga.digest({"source_contract_type":"EO_FJ_CSV_V1","classification_allowlist":ALLOW})
 g2=ga.validate_gap_policy_data({**gm,"expected_classification_counts":cc,"classification_allowlist_sha256":ai,"expected_normalized_inventory_identity_sha256":g1["policy_identity_sha256"],"expected_normalized_inventory_sha256":g1["normalized_entries_sha256"]},gp.parent)
 if any(g1[k]!=g2[k] for k in ("policy_identity_sha256","normalized_entries_sha256","entry_count","classification_allowlist")) or (len(g1["entries"]),ac,uv)!=(773,745,28):raise ValueError("gap mismatch")
 return {"timestamp_projection_identity":p["canonical_projection_identity_sha256"],"input_mutation_count":int(p["input_mutated"]),"source_dataset_identity":sr["dataset_identity_sha256"],"canonical_timeline_sha256":sr["timeline"]["canonical_timeline_sha256"],"source_count":sr["timeline"]["source_count"],"total_rows":sr["timeline"]["total_rows"],"first_timestamp":sr["timeline"]["first_timestamp"],"last_timestamp":sr["timeline"]["last_timestamp"],"duplicate_timestamps":sr["timeline"]["duplicate_timestamps"],"sources":sr["sources"],"canonical_timeline_observation_provenance":{k:o[k] for k in ("derived_at_checkpoint","historical_timeline_hash_claimed","algorithm")},"gap_artifact_sha256":gh,"gap_policy_identity":g1["policy_identity_sha256"],"normalized_gap_inventory_sha256":g1["normalized_entries_sha256"],"gap_entry_count":g1["entry_count"],"accepted_closure_count":ac,"unverified_gap_count":uv,"classification_allowlist":g1["classification_allowlist"],"classification_allowlist_identity":ai,"classification_counts":cc,"duplicate_gap_id_count":0,"duplicate_source_record_identity_count":0,"duplicate_timestamp_pair_count":0,"semantic_conflict_count":0}
def mm(rs,k):return sum(x[k]!=rs[0][k] for x in rs[1:])
def abscount(x):
 if isinstance(x,dict):return sum(abscount(v) for v in x.values())
 if isinstance(x,list):return sum(abscount(v) for v in x)
 return int(isinstance(x,str) and (ntpath.isabs(x) or posixpath.isabs(x)))
def evidence(a,ah,r,mc,fa,ra):
 im=ra.imports();ex=ra.executions();ext=ra.external();fr=fa.report();uq=fr["unique_logical_file_counts"]
 expuq={"committed_fj_source_manifest_evidence":1,"approved_original_fj_source_files":3,"authorized_eo_fj_gap_policy":1,"relocated_temporary_files":4,"unauthorized_files":0,"fq_source_files":0,"fq_gap_inventories":0}
 expim={"source_adapter_import_count":1,"gap_adapter_import_count":1,"descriptor_adapter_import_count":0,"detector_import_count":0,"fi_import_count":0,"legacy_runner_import_count":0,"wrapper_import_count":0,"fq_runner_import_count":0}
 ident={k:r[k] for k in ("timestamp_projection_identity","source_dataset_identity","canonical_timeline_sha256","gap_policy_identity","normalized_gap_inventory_sha256","classification_allowlist_identity")};ap=abscount(ident);bad=badmods()
 ok=not any(mc.values()) and uq==expuq and im==expim and not any(ex.values()) and not any(ext[k] for k in ("subprocess_launch_count","mt5_terminal_launch_count","ea_execution_count")) and r["input_mutation_count"]==0 and ap==0 and not bad
 q=a["timestamp_projection_binding"]
 core={"schema_version":"fr_prep_b2e_r1b1_fj_source_gap_bindings.v1","checkpoint":"FR_PREP_B2E_R1B1C","binding_origin_checkpoint":"FR_PREP_B2E_R1B1","decision":"FR_PREP_B2E_R1B1_PASS_FROZEN_BINDING_EVIDENCE" if ok else "FR_PREP_B2E_R1B1_BLOCKED_RUNTIME_AUDIT","authorization_contract":{"path":"research/contracts/fr_prep_b2e_r1b_fj_real_data_authorization.v1.json","sha256":ah},"timestamp_projection_contract":{"path":q["contract_path"],"sha256":q["contract_sha256"],"helper_path":q["helper_path"],"helper_sha256":q["helper_sha256"],"r1a1_deterministic_sha256":q["r1a1_deterministic_sha256"],"r1a2_deterministic_sha256":q["r1a2_deterministic_sha256"],"r1b1_projection_identity":r["timestamp_projection_identity"]},"historical_source_manifest_evidence":a["historical_source_manifest_evidence"],"dataset":{"dataset_id":a["dataset_id"],"dataset_role":a["dataset_role"],"symbol":a["symbol"],"timeframe":a["timeframe"],"execution_mode":a["execution_mode"],"mapping_profile":"FJ_SOURCE_PROVENANCE_V1","broker_history_completeness":"NOT_PROVEN","raw_broker_csv_committed":False},"sources":r["sources"],"frozen_boundaries":{"first_timestamp":r["first_timestamp"],"last_timestamp":r["last_timestamp"]},"source_count":r["source_count"],"total_rows":r["total_rows"],"duplicate_timestamps":r["duplicate_timestamps"],"source_dataset_identity":r["source_dataset_identity"],"canonical_timeline_sha256":r["canonical_timeline_sha256"],"canonical_timeline_observation_provenance":r["canonical_timeline_observation_provenance"],"gap_binding":{"artifact_path":a["gap_policy"]["path"],"artifact_sha256":r["gap_artifact_sha256"],"policy_id":"FJ_2023_2025_EO_GAP_POLICY","source_contract_type":"EO_FJ_CSV_V1","gap_policy_identity":r["gap_policy_identity"],"normalized_gap_inventory_sha256":r["normalized_gap_inventory_sha256"],"classification_allowlist":r["classification_allowlist"],"classification_allowlist_identity":r["classification_allowlist_identity"],"classification_counts":r["classification_counts"],"entry_count":r["gap_entry_count"],"accepted_closure_count":r["accepted_closure_count"],"unverified_gap_count":r["unverified_gap_count"],"duplicate_gap_id_count":0,"duplicate_source_record_identity_count":0,"duplicate_timestamp_pair_count":0,"semantic_conflict_count":0},"deterministic_mismatch_counters":mc,"relocation_proof":{"temporary_directory_outside_repository":True,"copied_bytes_hash_verified":True,"canonical_identities_unchanged":mc["relocation_mismatch"]==0},"runtime_audit":{"counter_provenance":{"module_imports":"sys.modules before/after delta plus allowlisted import dispatch","function_execution":"sys.setprofile call events classified by module and function","file_access":"resolved-path read-open interception at pathlib.Path.open and builtins.open","external_execution":"subprocess.Popen, os.system, and os.startfile launch interception"},"module_import_counts":im,"import_dispatches":ra.dispatch,"rejected_import_dispatches":ra.rejected,"function_execution_counts":ex,"file_access":fr,"external_execution":ext},"execution_mode":"ADAPTER_VALIDATION_ONLY","broker_history_completeness":"NOT_PROVEN","performance":"NOT_EVALUATED","profitability":"NOT_CLAIMED","order_logic":"NOT_APPROVED","candidate":"NOT_READY_FOR_ORDER_LOGIC","frozen_evidence_modified":False,"source_data_semantics_changed":False,"detector_executed":False,"events_generated":False,"atr_events_generated":False,"tp_sl_calculated":False,"outcomes_generated":False,"descriptor_composed":False,"mt5_executed":False,"ea_executed":False,"input_mutation_count":r["input_mutation_count"],"absolute_runtime_path_in_canonical_identity_count":ap,"unauthorized_file_access_count":uq["unauthorized_files"],"prohibited_modules":bad}
 return {**core,"canonical_summary_sha256":hb(cj(core).encode("ascii"))}
def run_authorized_binding(authorization_path,source_root,gap_policy_path,output_root,project_metadata):
 a,ah=authorize(authorization_path);gp=(ROOT/a["gap_policy"]["path"]).resolve()
 if gap_policy_path.resolve()!=gp:raise ValueError("unauthorized gap policy path")
 ps=sourcepaths(source_root,a);fa=FileAudit();fa.add(ROOT/a["historical_source_manifest_evidence"]["path"],"committed_fj_source_manifest_evidence")
 for p in ps:fa.add(p,"approved_original_fj_source_files")
 fa.add(gp,"authorized_eo_fj_gap_policy");ra=RuntimeAudit()
 with ra:
  sa=ra.imp("historical_source_adapter");ga=ra.imp("gap_policy_adapter")
  with fa:
   hs=history(a);r1=derive(a,hs,ps,gp,project_metadata,sa,ga);r2=derive(a,hs,ps,gp,project_metadata,sa,ga)
   tr=Path(tempfile.gettempdir()).resolve()
   if tr==ROOT.resolve() or ROOT.resolve() in tr.parents:raise RuntimeError("temp root inside repository")
   with tempfile.TemporaryDirectory(prefix="fr_prep_b2e_r1b1c_") as n:
    d=Path(n);rp=[]
    for p,f in zip(ps,a["frozen_sources"]):
     q=d/f["file_name"];fa.add(q,"relocated_temporary_files");shutil.copyfile(p,q)
     if hf(q)!=f["sha256"]:raise ValueError("relocated source hash mismatch")
     rp.append(q)
    rg=d/gp.name;fa.add(rg,"relocated_temporary_files");shutil.copyfile(gp,rg)
    if hf(rg)!=r1["gap_artifact_sha256"]:raise ValueError("relocated gap hash mismatch")
    rr=derive(a,hs,rp,rg,project_metadata,sa,ga)
 rs=[r1,r2,rr];mc={"source_identity_mismatch_count":mm(rs,"source_dataset_identity"),"timeline_mismatch_count":mm(rs,"canonical_timeline_sha256"),"gap_identity_mismatch_count":mm(rs,"gap_policy_identity"),"normalized_gap_inventory_mismatch_count":mm(rs,"normalized_gap_inventory_sha256"),"allowlist_identity_mismatch_count":mm(rs,"classification_allowlist_identity"),"count_mismatch":sum((x["source_count"],x["total_rows"],x["gap_entry_count"],x["accepted_closure_count"],x["unverified_gap_count"])!=(3,17716,773,745,28) for x in rs),"boundary_mismatch":sum((x["first_timestamp"],x["last_timestamp"])!=("2023-01-03T01:00:00","2025-12-31T19:00:00") for x in rs),"relocation_mismatch":int(cj(r1)!=cj(rr)),"canonical_summary_mismatch":int(cj(r1)!=cj(r2))}
 out=evidence(a,ah,r1,mc,fa,ra)
 if out["decision"]!="FR_PREP_B2E_R1B1_PASS_FROZEN_BINDING_EVIDENCE":raise RuntimeError("runtime audit failed")
 output_root.mkdir(parents=True,exist_ok=True);(output_root/"fj_source_gap_binding_summary.json").write_text(cj(out)+"\n",encoding="utf-8");return out
def main():
 print("fail closed: internal helper; use run_fr_prep_b2e_fj_adapter_binding_evidence.py --mode ...",file=sys.stderr);return 2
if __name__=="__main__":raise SystemExit(main())
