#!/usr/bin/env python3
"""R1b-2 authorized adapter-only frozen FJ descriptor composition."""
import argparse,builtins,copy,hashlib,importlib,json,ntpath,os,posixpath,shutil,subprocess,sys,tempfile
from collections import Counter
from pathlib import Path
import jsonschema
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1]
AUTH=ROOT/"research/contracts/fr_prep_b2e_r1b2_fj_descriptor_composition_authorization.v1.json"
ASC=ROOT/"research/schemas/fr_prep_b2e_r1b2_fj_descriptor_composition_authorization.v1.schema.json"
PASS="FR_PREP_B2E_R1B2_PASS_DESCRIPTOR_COMPOSED_ADAPTER_ONLY"
R1PASS="FR_PREP_B2E_R1B1_PASS_FROZEN_BINDING_EVIDENCE"
R1ID="da22164a2cf95c2524ea645a65e07eb3a1188df836d97b963e1cd577657cfd44"
EXP={"schema_version":"dataset_execution_descriptor.v1","dataset_id":"FJ_2023_2025_GOLD_H1","dataset_role":"DEVELOPMENT_BACKWARD_COMPATIBILITY_REPLAY","symbol":"GOLD#","timeframe":"H1","boundary_start_timestamp":"2023-01-03T01:00:00","boundary_end_timestamp":"2025-12-31T19:00:00","source_manifest_identity_sha256":"b9cc38c6da2474ba22947053a6333f4b7312c2e39221cd1cb4ff3cf47f6c7122","source_manifest_sha256":"10f03b021a9e391af689c9f635f8094758245367f76b79d6d4e7a0bc48641764","canonical_timeline_identity_sha256":"8d2224fb62b21918f608868f3c9f404ba7feb93df7273fe8102da1a0188fce71","canonical_timeline_sha256":"3afe66cadf8e7ecdfd9aa8f37145ca5fe047a62b66f62ef82dad11887ecbdd02","canonical_bar_count":17716,"canonical_timeline_boundary":{"first_timestamp":"2023-01-03T01:00:00","last_timestamp":"2025-12-31T19:00:00"},"gap_policy_identity_sha256":"8390e1079a05af021701887da42e1824b6982af7da64137d23289324be31f8f9","gap_policy_sha256":"d94812339fa30ec9cb4fdbe617b105fc72211bda79d19ce50a618ee819dd1ca4","gap_counts_by_classification":{"ACCEPTED_DAILY_BROKER_SESSION_GAP":594,"ACCEPTED_WEEKEND_MARKET_CLOSURE":151,"BLOCKED_UNCLASSIFIED_GAP":28},"gap_counts_by_disposition":{"ACCEPTED_CLOSURE":745,"UNVERIFIED_GAP":28},"classification_allowlist_identity_sha256":"c8b13c2d53f40826a69dc732dd5ab03fee3d6cc299d32be50f8fab02270c237e","broker_history_completeness":"NOT_PROVEN","detector_contract_version":"DETECTOR_NOT_EXECUTED_ADAPTER_ONLY_V1","outcome_contract_version":"OUTCOME_NOT_EXECUTED_ADAPTER_ONLY_V1","interpretation_contract_version":"INTERPRETATION_NOT_EXECUTED_ADAPTER_ONLY_V1","execution_mode":"ADAPTER_VALIDATION_ONLY","detector_execution_allowed":False,"outcome_execution_allowed":False,"descriptor_identity_sha256":"dd325e9a81de40c07e5a579226b4d82d3bfdb06b8a14e3f1a562b8e847119848"}
IM={"dataset_execution_descriptor_adapter":"descriptor_adapter_import_count","historical_source_adapter":"source_adapter_import_count","gap_policy_adapter":"gap_adapter_import_count","market_structure_break_retest_detector":"detector_import_count","run_checkpoint_fi_detector_fixtures":"fi_import_count","run_checkpoint_fj_historical_event_population":"legacy_runner_import_count","fr_prep_runner_execution_wrapper":"wrapper_import_count","run_checkpoint_fq_holdout_gap_boundary":"fq_runner_import_count"}
OKMOD={"dataset_execution_descriptor_adapter","historical_source_adapter","gap_policy_adapter"}
FC=("r1b2_authorization_contract","r1b2_authorization_schema","r1b1c_binding_contract","r1b1c_binding_result","r1b1c_binding_schema","descriptor_adapter_source","descriptor_schema","approved_original_fj_source_files","authorized_eo_fj_gap_policy","relocated_temporary_files","unauthorized_files","fq_source_files","fq_gap_inventories")
def cj(x):return json.dumps(x,ensure_ascii=True,sort_keys=True,separators=(",",":"))
def hb(x):return hashlib.sha256(x).hexdigest()
def hf(p):
 d=hashlib.sha256()
 with Path(p).open("rb") as f:
  for b in iter(lambda:f.read(1048576),b""):d.update(b)
 return d.hexdigest()
def base(n):return n.split(".")[-1]
def badmods():return sorted(n for n in sys.modules if base(n) in set(IM)-OKMOD)
def abscount(x):
 if isinstance(x,dict):return sum(abscount(v) for v in x.values())
 if isinstance(x,list):return sum(abscount(v) for v in x)
 return int(isinstance(x,str) and (ntpath.isabs(x) or posixpath.isabs(x)))
class RuntimeAudit:
 def __init__(s):s.before=set(sys.modules);s.dispatch=[];s.rejected=[];s.calls=Counter();s.launches=[]
 def prof(s,fr,event,arg):
  del arg
  if event!="call":return
  m=base(str(fr.f_globals.get("__name__","")));f=fr.f_code.co_name.lower()
  if m=="dataset_execution_descriptor_adapter":
   mp={"compose_dataset_execution_descriptor":"descriptor_composition_count","validate_dataset_execution_descriptor":"descriptor_validation_count","validate_adapter_only_invocation":"adapter_only_guard_validation_count"}
   if f in mp:s.calls[mp[f]]+=1
  mm={"market_structure_break_retest_detector":"detector_execution_count","run_checkpoint_fi_detector_fixtures":"fi_execution_count","run_checkpoint_fj_historical_event_population":"legacy_runner_execution_count","fr_prep_runner_execution_wrapper":"wrapper_execution_count","run_checkpoint_fq_holdout_gap_boundary":"fq_execution_count"}
  if m in mm:s.calls[mm[m]]+=1
  if m=="run_checkpoint_fj_historical_event_population":s.calls["event_population_count"]+=1
  if "atr" in f and "event" in f:s.calls["atr_event_count"]+=1
  if "tp_sl" in f or "take_profit_stop_loss" in f:s.calls["tp_sl_count"]+=1
  if "outcome" in f and ("emit" in f or "generate" in f):s.calls["outcome_count"]+=1
  if "interpret" in f and "fn" in f:s.calls["fn_interpretation_count"]+=1
 def block(s,kind,cmd):s.launches.append({"kind":kind,"command":str(cmd)});raise RuntimeError("external execution prohibited")
 def __enter__(s):
  s.op=sys.getprofile();s.po=subprocess.Popen;s.sy=os.system;s.st=getattr(os,"startfile",None);sys.setprofile(s.prof)
  subprocess.Popen=lambda c,*a,**k:s.block("subprocess",c);os.system=lambda c:s.block("os.system",c)
  if s.st is not None:os.startfile=lambda p,*a,**k:s.block("os.startfile",p)
  return s
 def __exit__(s,*x):
  subprocess.Popen=s.po;os.system=s.sy;sys.setprofile(s.op)
  if s.st is not None:os.startfile=s.st
 def imp(s):s.dispatch.append("dataset_execution_descriptor_adapter");return importlib.import_module("dataset_execution_descriptor_adapter")
 def imports(s):
  added=set(sys.modules)-s.before
  return {v:sum(base(x)==k for x in added) for k,v in IM.items()}
 def executions(s):
  ns=("descriptor_composition_count","descriptor_validation_count","adapter_only_guard_validation_count","detector_execution_count","event_population_count","atr_event_count","tp_sl_count","outcome_count","fn_interpretation_count","fi_execution_count","legacy_runner_execution_count","wrapper_execution_count","fq_execution_count")
  return {n:s.calls.get(n,0) for n in ns}
 def external(s):
  return {"subprocess_launch_count":sum(x["kind"]=="subprocess" for x in s.launches),"os_system_launch_count":sum(x["kind"]=="os.system" for x in s.launches),"os_startfile_launch_count":sum(x["kind"]=="os.startfile" for x in s.launches),"mt5_terminal_launch_count":sum("terminal64.exe" in x["command"].lower() for x in s.launches),"ea_execution_count":sum(".ex5" in x["command"].lower() for x in s.launches),"observed_launches":s.launches}
class FileAudit:
 def __init__(s):s.allowed={};s.unique={k:set() for k in FC};s.raw=Counter();s.attempts=[]
 def allow(s,p,c):s.allowed[Path(p).resolve()]=c
 def see(s,p,mode):
  if isinstance(p,int) or ("r" not in mode and "+" not in mode):return
  q=Path(p).resolve();c=s.allowed.get(q)
  if c is None:s.raw["unauthorized_files"]+=1;s.unique["unauthorized_files"].add(q);s.attempts.append(str(q));raise RuntimeError("unauthorized read-open: "+str(q))
  s.raw[c]+=1;s.unique[c].add(q)
 def __enter__(s):
  s.bo=builtins.open;s.po=Path.open
  def bo(p,mode="r",*a,**k):s.see(p,mode);return s.bo(p,mode,*a,**k)
  def po(p,mode="r",*a,**k):s.see(p,mode);return s.po(p,mode,*a,**k)
  builtins.open=bo;Path.open=po;return s
 def __exit__(s,*x):builtins.open=s.bo;Path.open=s.po
 def report(s):return {"unique_logical_file_counts":{k:len(s.unique[k]) for k in FC},"raw_read_open_operation_counts":{k:s.raw.get(k,0) for k in FC},"accessed_file_names_by_category":{k:sorted(p.name for p in s.unique[k]) for k in FC},"unauthorized_path_attempts":s.attempts}
def readj(p,h):
 b=p.read_bytes()
 if hb(b)!=h:raise ValueError("file SHA-256 mismatch: "+p.name)
 return json.loads(b.decode()),hb(b)
def r1id(x):return hb(cj({k:v for k,v in x.items() if k!="canonical_summary_sha256"}).encode("ascii"))
def assert_frozen(e):
 d=e["dataset"];g=e["gap_binding"];b=e["frozen_boundaries"];t=e["timestamp_projection_contract"]
 if (d["dataset_id"],d["dataset_role"],d["symbol"],d["timeframe"],d["execution_mode"],d["broker_history_completeness"])!=("FJ_2023_2025_GOLD_H1","DEVELOPMENT_BACKWARD_COMPATIBILITY_REPLAY","GOLD#","H1","ADAPTER_VALIDATION_ONLY","NOT_PROVEN"):raise ValueError("frozen dataset mismatch")
 if (e["source_count"],e["total_rows"],e["duplicate_timestamps"],b["first_timestamp"],b["last_timestamp"])!=(3,17716,0,"2023-01-03T01:00:00","2025-12-31T19:00:00"):raise ValueError("frozen timeline mismatch")
 if (t["r1b1_projection_identity"],e["source_dataset_identity"],e["canonical_timeline_sha256"],g["gap_policy_identity"],g["normalized_gap_inventory_sha256"],g["classification_allowlist_identity"])!=("1d7151761233277824bdd8772b945b61939195b1feb0b8a19fdf93769ded6053","b9cc38c6da2474ba22947053a6333f4b7312c2e39221cd1cb4ff3cf47f6c7122","3afe66cadf8e7ecdfd9aa8f37145ca5fe047a62b66f62ef82dad11887ecbdd02","8390e1079a05af021701887da42e1824b6982af7da64137d23289324be31f8f9","d94812339fa30ec9cb4fdbe617b105fc72211bda79d19ce50a618ee819dd1ca4","c8b13c2d53f40826a69dc732dd5ab03fee3d6cc299d32be50f8fab02270c237e"):raise ValueError("frozen identity mismatch")
 if (g["entry_count"],g["accepted_closure_count"],g["unverified_gap_count"],g["classification_counts"])!=(773,745,28,{"ACCEPTED_DAILY_BROKER_SESSION_GAP":594,"ACCEPTED_WEEKEND_MARKET_CLOSURE":151,"BLOCKED_UNCLASSIFIED_GAP":28}):raise ValueError("frozen gap count mismatch")
 if any(g[k] for k in ("duplicate_gap_id_count","duplicate_source_record_identity_count","duplicate_timestamp_pair_count","semantic_conflict_count")):raise ValueError("frozen duplicate/conflict mismatch")
def validate_r1(c,r,b):
 if c!=r:raise ValueError("R1b-1c contract/result semantic mismatch")
 for n,x in (("contract",c),("result",r)):
  if x.get("decision")!=b["required_decision"]:raise ValueError("wrong R1b-1c decision: "+n)
  if x.get("canonical_summary_sha256")!=b["required_canonical_summary_sha256"]:raise ValueError("wrong R1b-1c canonical summary field: "+n)
  if r1id(x)!=b["required_canonical_summary_sha256"]:raise ValueError("wrong R1b-1c canonical summary identity: "+n)
 assert_frozen(c)
def authorize(ap,sroot,gp,fa):
 if ap.resolve()!=AUTH.resolve():raise ValueError("wrong authorization path")
 fa.allow(AUTH,"r1b2_authorization_contract");fa.allow(ASC,"r1b2_authorization_schema")
 with fa:
  ab=AUTH.read_bytes();a=json.loads(ab.decode());asc=json.loads(ASC.read_text(encoding="utf-8"));jsonschema.Draft202012Validator.check_schema(asc);jsonschema.Draft202012Validator(asc).validate(a);ah=hb(ab)
  z=a["r1b1c_evidence_binding"];db=a["descriptor_adapter_binding"]
  cp=(ROOT/z["contract_path"]).resolve();rp=(ROOT/z["result_path"]).resolve();sp=(ROOT/z["schema_path"]).resolve();dp=(ROOT/db["path"]).resolve();ds=(ROOT/db["descriptor_schema_path"]).resolve();ag=(ROOT/a["authorized_gap_policy"]["path"]).resolve()
  for p,c in ((cp,"r1b1c_binding_contract"),(rp,"r1b1c_binding_result"),(sp,"r1b1c_binding_schema"),(dp,"descriptor_adapter_source"),(ds,"descriptor_schema"),(ag,"authorized_eo_fj_gap_policy")):fa.allow(p,c)
  if gp.resolve()!=ag:raise ValueError("unauthorized gap-policy path")
  sr=sroot.resolve()
  if not sr.is_dir():raise ValueError("runtime source root missing")
  ps=[]
  for f in a["frozen_sources"]:
   p=(sr/f["file_name"]).resolve()
   if p.parent!=sr or not p.is_file():raise ValueError("approved FJ source missing")
   fa.allow(p,"approved_original_fj_source_files");ps.append(p)
  c,_=readj(cp,z["contract_file_sha256"]);r,_=readj(rp,z["result_file_sha256"]);sc,_=readj(sp,z["schema_file_sha256"]);jsonschema.Draft202012Validator.check_schema(sc);jsonschema.Draft202012Validator(sc).validate(c);jsonschema.Draft202012Validator(sc).validate(r);validate_r1(c,r,z)
  if hf(dp)!=db["file_sha256"]:raise ValueError("descriptor adapter hash mismatch")
  dsc,_=readj(ds,db["descriptor_schema_file_sha256"]);jsonschema.Draft202012Validator.check_schema(dsc)
  for p,f in zip(ps,a["frozen_sources"]):
   if hf(p)!=f["file_sha256"]:raise ValueError("approved FJ source hash mismatch")
  if hf(ag)!=a["authorized_gap_policy"]["file_sha256"]:raise ValueError("authorized gap-policy hash mismatch")
 return a,ah,c,ps,ag,dsc
def request(a,e,ps,gp):
 ss=[]
 for f,o,p in zip(a["frozen_sources"],e["sources"],ps):ss.append({"schema_version":"source_file_descriptor.v1","source_id":f["source_id"],"file_name":f["file_name"],"runtime_path":str(p),"sha256":f["file_sha256"],"size_bytes":o["size_bytes"],"row_count":f["row_count"],"first_timestamp":o["first_timestamp"],"last_timestamp":o["last_timestamp"],"format":"MT5_TSV_OHLC_V1"})
 g=e["gap_binding"];b=e["frozen_boundaries"]
 return {"schema_version":"synthetic_dataset_composition_request.v1","dataset_role":a["dataset_role"],"execution_mode":"ADAPTER_VALIDATION_ONLY","gap_dataset_binding":{"dataset_id":a["dataset_id"],"symbol":a["symbol"],"timeframe":a["timeframe"],"boundary_start_timestamp":b["first_timestamp"],"boundary_end_timestamp":b["last_timestamp"]},"historical_source_manifest":{"schema_version":"historical_source_manifest.v1","dataset_id":a["dataset_id"],"symbol":a["symbol"],"timeframe":a["timeframe"],"boundary_start_timestamp":b["first_timestamp"],"boundary_end_timestamp":b["last_timestamp"],"broker_history_completeness":"NOT_PROVEN","raw_broker_csv_committed":False,"sources":ss,"expected_timeline":{"source_count":e["source_count"],"total_rows":e["total_rows"],"first_timestamp":b["first_timestamp"],"last_timestamp":b["last_timestamp"],"duplicate_timestamps":e["duplicate_timestamps"],"canonical_timeline_sha256":e["canonical_timeline_sha256"]}},"gap_policy_manifest":{"schema_version":"gap_policy_manifest.v1","policy_id":g["policy_id"],"source_contract_type":g["source_contract_type"],"runtime_path":str(gp),"artifact_sha256":g["artifact_sha256"],"classification_allowlist":g["classification_allowlist"],"classification_allowlist_sha256":g["classification_allowlist_identity"],"expected_entry_count":g["entry_count"],"expected_accepted_closure_count":g["accepted_closure_count"],"expected_unverified_gap_count":g["unverified_gap_count"],"expected_classification_counts":g["classification_counts"],"expected_normalized_inventory_identity_sha256":g["gap_policy_identity"],"expected_normalized_inventory_sha256":g["normalized_gap_inventory_sha256"],"require_canonical_source_order":False,"broker_history_completeness":"NOT_PROVEN"}}
def once(ad,a,e,ps,gp,dsc):
 q=request(a,e,ps,gp);snap=copy.deepcopy(q);root=ps[0].parent;d=ad.compose_dataset_execution_descriptor(q,root);ad.validate_dataset_execution_descriptor(d,q,root,None,{"gap_entry_count":773,"accepted_closure_count":745,"unverified_gap_count":28,"declared_total_gap_count":773});jsonschema.Draft202012Validator(dsc).validate(d)
 if d!=EXP:raise ValueError("derived descriptor differs from frozen expectation")
 return d,int(q!=snap)
def mm(ds,k):return sum(x[k]!=ds[0][k] for x in ds[1:])
def evidence(a,ah,r,ds,mut,fa,ra):
 d,x,y=ds;mc={"descriptor_mismatch":sum(v!=d for v in ds[1:]),"source_identity_mismatch":mm(ds,"source_manifest_identity_sha256"),"source_manifest_sha_mismatch":mm(ds,"source_manifest_sha256"),"timeline_identity_mismatch":mm(ds,"canonical_timeline_identity_sha256"),"timeline_sha_mismatch":mm(ds,"canonical_timeline_sha256"),"gap_identity_mismatch":mm(ds,"gap_policy_identity_sha256"),"gap_sha_mismatch":mm(ds,"gap_policy_sha256"),"classification_identity_mismatch":mm(ds,"classification_allowlist_identity_sha256"),"count_mismatch":sum((v["canonical_bar_count"],v["gap_counts_by_disposition"])!=(17716,{"ACCEPTED_CLOSURE":745,"UNVERIFIED_GAP":28}) for v in ds),"boundary_mismatch":sum((v["boundary_start_timestamp"],v["boundary_end_timestamp"])!=("2023-01-03T01:00:00","2025-12-31T19:00:00") for v in ds),"relocation_mismatch":int(y!=d),"repeated_composition_mismatch":int(x!=d)}
 im=ra.imports();ex=ra.executions();ext=ra.external();fr=fa.report();uq=fr["unique_logical_file_counts"];bad=badmods();ap=abscount(d)
 eim={"descriptor_adapter_import_count":1,"source_adapter_import_count":1,"gap_adapter_import_count":1,"detector_import_count":0,"fi_import_count":0,"legacy_runner_import_count":0,"wrapper_import_count":0,"fq_runner_import_count":0}
 eex={"descriptor_composition_count":3,"descriptor_validation_count":3,"adapter_only_guard_validation_count":3,"detector_execution_count":0,"event_population_count":0,"atr_event_count":0,"tp_sl_count":0,"outcome_count":0,"fn_interpretation_count":0,"fi_execution_count":0,"legacy_runner_execution_count":0,"wrapper_execution_count":0,"fq_execution_count":0}
 euq={"r1b2_authorization_contract":1,"r1b2_authorization_schema":1,"r1b1c_binding_contract":1,"r1b1c_binding_result":1,"r1b1c_binding_schema":1,"descriptor_adapter_source":1,"descriptor_schema":1,"approved_original_fj_source_files":3,"authorized_eo_fj_gap_policy":1,"relocated_temporary_files":4,"unauthorized_files":0,"fq_source_files":0,"fq_gap_inventories":0}
 ok=not any(mc.values()) and im==eim and ex==eex and uq==euq and not any(ext[k] for k in ("subprocess_launch_count","os_system_launch_count","os_startfile_launch_count","mt5_terminal_launch_count","ea_execution_count")) and mut==ap==0 and not bad
 z=a["r1b1c_evidence_binding"];db=a["descriptor_adapter_binding"]
 core={"schema_version":"fr_prep_b2e_r1b2_fj_descriptor_composition.v1","checkpoint":"FR_PREP_B2E_R1B2","decision":PASS if ok else "FR_PREP_B2E_R1B2_BLOCKED_RUNTIME_AUDIT","r1b1c_evidence_binding":{"contract_path":z["contract_path"],"contract_file_sha256":z["contract_file_sha256"],"result_path":z["result_path"],"result_file_sha256":z["result_file_sha256"],"decision":r["decision"],"canonical_summary_sha256":r1id(r),"contract_result_semantically_identical":True},"authorization_contract":{"path":"research/contracts/fr_prep_b2e_r1b2_fj_descriptor_composition_authorization.v1.json","file_sha256":ah},"descriptor_adapter":{"path":db["path"],"file_sha256":db["file_sha256"],"descriptor_schema_path":db["descriptor_schema_path"],"descriptor_schema_file_sha256":db["descriptor_schema_file_sha256"]},"composed_descriptor":d,"descriptor_identity_sha256":d["descriptor_identity_sha256"],"deterministic_mismatch_counters":mc,"normal_repeat_identical":x==d,"relocation_proof":{"temporary_directory_outside_repository":True,"copied_bytes_hash_verified":True,"complete_descriptor_identical":y==d,"canonical_identities_unchanged":y==d},"runtime_audit":{"counter_provenance":{"module_imports":"sys.modules before/after delta following one authorized lazy descriptor import dispatch","function_execution":"sys.setprofile call events classified by exact module and function","file_access":"resolved-path read-open interception at pathlib.Path.open and builtins.open","external_execution":"subprocess.Popen, os.system, and os.startfile launch interception"},"module_import_counts":im,"import_dispatches":ra.dispatch,"rejected_import_dispatches":ra.rejected,"function_execution_counts":ex,"file_access":fr,"external_execution":ext},"execution_mode":"ADAPTER_VALIDATION_ONLY","broker_history_completeness":"NOT_PROVEN","descriptor_composed":True,"descriptor_validated":True,"detector_executed":False,"events_generated":False,"atr_events_generated":False,"tp_sl_calculated":False,"outcomes_generated":False,"fn_interpretation_performed":False,"fq_accessed":False,"mt5_executed":False,"ea_executed":False,"performance":"NOT_EVALUATED","profitability":"NOT_CLAIMED","order_logic":"NOT_APPROVED","candidate":"NOT_READY_FOR_ORDER_LOGIC","frozen_evidence_modified":False,"source_data_semantics_changed":False,"input_mutation_count":mut,"absolute_runtime_path_in_canonical_identity_count":ap,"unauthorized_file_access_count":uq["unauthorized_files"],"prohibited_modules":bad}
 return {**core,"canonical_summary_sha256":hb(cj(core).encode("ascii"))}
def run(ap,sroot,gp,out):
 if ap.resolve()!=AUTH.resolve():raise ValueError("wrong authorization path")
 fa=FileAudit();a,ah,r,ps,ag,dsc=authorize(ap,sroot,gp,fa);ra=RuntimeAudit();ds=[];mut=0
 with ra:
  ad=ra.imp()
  with fa:
   for i in range(2):
    d,m=once(ad,a,r,ps,ag,dsc);ds.append(d);mut+=m
   tr=Path(tempfile.gettempdir()).resolve()
   if tr==ROOT or ROOT in tr.parents:raise RuntimeError("temporary root inside repository")
   with tempfile.TemporaryDirectory(prefix="fr_prep_b2e_r1b2_") as n:
    td=Path(n).resolve();rps=[]
    for p,f in zip(ps,a["frozen_sources"]):
     q=td/f["file_name"];fa.allow(q,"relocated_temporary_files");shutil.copyfile(p,q)
     if hf(q)!=f["file_sha256"]:raise ValueError("relocated source hash mismatch")
     rps.append(q)
    rg=td/ag.name;fa.allow(rg,"relocated_temporary_files");shutil.copyfile(ag,rg)
    if hf(rg)!=a["authorized_gap_policy"]["file_sha256"]:raise ValueError("relocated gap hash mismatch")
    d,m=once(ad,a,r,rps,rg,dsc);ds.append(d);mut+=m
 ev=evidence(a,ah,r,ds,mut,fa,ra)
 if ev["decision"]!=PASS:raise RuntimeError("R1b-2 runtime audit failed")
 out.mkdir(parents=True,exist_ok=True);(out/"fj_descriptor_composition_summary.json").write_text(cj(ev)+"\n",encoding="utf-8");return ev
def parser():
 p=argparse.ArgumentParser(description="Fail-closed R1b-2 descriptor composition evidence");p.add_argument("--mode",required=True,choices=("r1b2-descriptor-composition",));p.add_argument("--authorization",type=Path,required=True);p.add_argument("--source-root",type=Path,required=True);p.add_argument("--gap-policy",type=Path,required=True);p.add_argument("--output-root",type=Path,required=True);return p
def main():
 a=parser().parse_args();r=run(a.authorization,a.source_root,a.gap_policy,a.output_root);print(cj(r));return 0
if __name__=="__main__":raise SystemExit(main())
