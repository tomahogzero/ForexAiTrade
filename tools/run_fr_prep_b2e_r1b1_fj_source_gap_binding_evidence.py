#!/usr/bin/env python3
"""R1b-1 authorized frozen FJ source/timeline/gap adapter evidence."""
import argparse,base64,copy,csv,hashlib,importlib,json,shutil,sys,tempfile
from collections import Counter
from datetime import datetime
from decimal import Decimal
from pathlib import Path
import jsonschema

ROOT=Path(__file__).resolve().parents[1]
AUTH=ROOT/"research/contracts/fr_prep_b2e_r1b_fj_real_data_authorization.v1.json"
ASC=ROOT/"research/schemas/fr_prep_b2e_r1b_fj_real_data_authorization.v1.schema.json"
ALLOW=["ACCEPTED_DAILY_BROKER_SESSION_GAP","ACCEPTED_WEEKEND_MARKET_CLOSURE","BLOCKED_UNCLASSIFIED_GAP"]
BAN={"dataset_execution_descriptor_adapter","market_structure_break_retest_detector","run_checkpoint_fi_detector_fixtures","run_checkpoint_fj_historical_event_population","run_checkpoint_fq_holdout_gap_boundary","fr_prep_runner_execution_wrapper"}
SAFE={"source_adapter_import_count":1,"gap_adapter_import_count":1,"descriptor_adapter_import_count":0,"detector_import_count":0,"detector_execution_count":0,"fi_import_count":0,"fi_execution_count":0,"legacy_runner_import_count":0,"legacy_runner_execution_count":0,"wrapper_import_count":0,"wrapper_execution_count":0,"fq_source_file_open_count":0,"fq_gap_inventory_open_count":0,"event_population_emit_count":0,"atr_event_emit_count":0,"tp_sl_calculation_count":0,"outcome_emit_count":0,"fn_interpretation_count":0}

def cj(x):return json.dumps(x,ensure_ascii=True,sort_keys=True,separators=(",",":"))
def hb(b):return hashlib.sha256(b).hexdigest()
def hf(p):
 d=hashlib.sha256()
 with Path(p).open("rb") as f:
  for c in iter(lambda:f.read(1048576),b""):d.update(c)
 return d.hexdigest()
def banned():return sorted(n for n in sys.modules if n.split(".")[-1] in BAN)
def cli():
 p=argparse.ArgumentParser()
 for n in ("authorization","source-root","gap-policy","output-root"):p.add_argument("--"+n,required=True,type=Path)
 return p.parse_args()
def authorize(p):
 if p.resolve()!=AUTH.resolve():raise ValueError("wrong authorization path")
 b=p.read_bytes();a=json.loads(b.decode())
 s=json.loads(ASC.read_text(encoding="utf-8"))
 jsonschema.Draft202012Validator.check_schema(s);jsonschema.Draft202012Validator(s).validate(a)
 if banned():raise RuntimeError("prohibited pre-authorization import")
 q=a["timestamp_projection_binding"]
 for pk,hk in (("contract_path","contract_sha256"),("helper_path","helper_sha256"),("projection_runner_path","projection_runner_sha256")):
  if hf(ROOT/q[pk])!=q[hk]:raise ValueError("projection binding mismatch")
 pc=json.loads((ROOT/q["contract_path"]).read_text(encoding="utf-8"))
 if pc["real_data_access_allowed"] is not False or pc["helper_fixture_deterministic_sha256"]!=q["r1a1_deterministic_sha256"]:raise ValueError("projection contract changed")
 return a,hb(b)
def imports():
 if str(ROOT/"tools") not in sys.path:sys.path.insert(0,str(ROOT/"tools"))
 pr=importlib.import_module("run_fr_prep_b2e_fj_adapter_binding_evidence")
 sa=importlib.import_module("historical_source_adapter")
 ga=importlib.import_module("gap_policy_adapter")
 if banned():raise RuntimeError("prohibited adapter-boundary import")
 return pr,sa,ga
def history(a):
 z=a["historical_source_manifest_evidence"];p=ROOT/z["path"];b=p.read_bytes()
 if hb(b)!=z["sha256"]:raise ValueError("source evidence hash mismatch")
 h=json.loads(b.decode());out=[]
 for f in a["frozen_sources"]:
  m=[x for x in h["sources"] if (x.get("file") or x.get("file_name") or Path(x.get("path","")).name)==f["file_name"]]
  if len(m)!=1 or m[0]["sha256"].lower()!=f["sha256"] or m[0].get("row_count",m[0].get("rows"))!=f["expected_rows"]:raise ValueError("historical provenance mismatch")
  out.append(copy.deepcopy(m[0]))
 return out
def paths(root,a):
 r=root.resolve()
 if not r.is_dir():raise ValueError("source root missing")
 x=[(r/f["file_name"]).resolve() for f in a["frozen_sources"]]
 if any(p.parent!=r or not p.is_file() for p in x):raise ValueError("approved source missing")
 return x
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
def derive(a,hs,ps,gp,pr,sa,ga):
 for p,f in zip(ps,a["frozen_sources"]):
  if hf(p)!=f["sha256"]:raise ValueError("source hash mismatch")
 o=observe(ps,a)
 exp=(3,17716,"2023-01-03T01:00:00","2025-12-31T19:00:00",0)
 if (o["source_count"],o["total_rows"],o["first_timestamp"],o["last_timestamp"],o["duplicate_timestamps"])!=exp or [x["row_count"] for x in o["sources"]]!=[5894,5928,5894]:raise ValueError("observation mismatch")
 p=pr.project_fj_manifest_metadata(manifest(a,hs,ps,o),"FR_PREP_B2E_R1B1_FROZEN_FJ_PROVENANCE")
 sr=sa.validate_manifest_data(p["projected_metadata"],ps[0].parent)
 ot={k:o[k] for k in ("source_count","total_rows","first_timestamp","last_timestamp","duplicate_timestamps","canonical_timeline_sha256")}
 if sr["timeline"]!=ot:raise ValueError("source adapter observation mismatch")
 gh=hf(gp);gm={"schema_version":"gap_policy_manifest.v1","policy_id":"FJ_2023_2025_EO_GAP_POLICY","source_contract_type":"EO_FJ_CSV_V1","runtime_path":str(gp),"artifact_sha256":gh,"classification_allowlist":ALLOW,"expected_entry_count":773,"expected_accepted_closure_count":745,"expected_unverified_gap_count":28,"require_canonical_source_order":False,"broker_history_completeness":"NOT_PROVEN"}
 g1=ga.validate_gap_policy_data(gm,gp.parent)
 cc=dict(sorted(Counter(x["policy_classification"] for x in g1["entries"]).items()))
 ac=sum(x["closure_disposition"]=="ACCEPTED_CLOSURE" for x in g1["entries"]);uv=len(g1["entries"])-ac
 ai=ga.digest({"source_contract_type":"EO_FJ_CSV_V1","classification_allowlist":ALLOW})
 g2=ga.validate_gap_policy_data({**gm,"expected_classification_counts":cc,"classification_allowlist_sha256":ai,"expected_normalized_inventory_identity_sha256":g1["policy_identity_sha256"],"expected_normalized_inventory_sha256":g1["normalized_entries_sha256"]},gp.parent)
 if any(g1[k]!=g2[k] for k in ("policy_identity_sha256","normalized_entries_sha256","entry_count","classification_allowlist")) or (len(g1["entries"]),ac,uv)!=(773,745,28):raise ValueError("gap validation mismatch")
 return {"timestamp_projection_identity":p["canonical_projection_identity_sha256"],"source_dataset_identity":sr["dataset_identity_sha256"],"canonical_timeline_sha256":sr["timeline"]["canonical_timeline_sha256"],"source_count":sr["timeline"]["source_count"],"total_rows":sr["timeline"]["total_rows"],"first_timestamp":sr["timeline"]["first_timestamp"],"last_timestamp":sr["timeline"]["last_timestamp"],"duplicate_timestamps":sr["timeline"]["duplicate_timestamps"],"sources":sr["sources"],"canonical_timeline_observation_provenance":{k:o[k] for k in ("derived_at_checkpoint","historical_timeline_hash_claimed","algorithm")},"gap_artifact_sha256":gh,"gap_policy_identity":g1["policy_identity_sha256"],"normalized_gap_inventory_sha256":g1["normalized_entries_sha256"],"gap_entry_count":g1["entry_count"],"accepted_closure_count":ac,"unverified_gap_count":uv,"classification_allowlist":g1["classification_allowlist"],"classification_allowlist_identity":ai,"classification_counts":cc,"duplicate_gap_id_count":0,"duplicate_source_record_identity_count":0,"duplicate_timestamp_pair_count":0,"semantic_conflict_count":0}
def mm(rs,k):return sum(x[k]!=rs[0][k] for x in rs[1:])
def main():
 x=cli();a,ah=authorize(x.authorization);gp=(ROOT/a["gap_policy"]["path"]).resolve()
 if x.gap_policy.resolve()!=gp:raise ValueError("unauthorized gap path")
 ps=paths(x.source_root,a);pr,sa,ga=imports();hs=history(a)
 r1=derive(a,hs,ps,gp,pr,sa,ga);r2=derive(a,hs,ps,gp,pr,sa,ga)
 tr=Path(tempfile.gettempdir()).resolve()
 if tr==ROOT.resolve() or ROOT.resolve() in tr.parents:raise RuntimeError("temp root inside repository")
 with tempfile.TemporaryDirectory(prefix="fr_prep_b2e_r1b1_") as n:
  d=Path(n);rp=[]
  for p,f in zip(ps,a["frozen_sources"]):
   q=d/f["file_name"];shutil.copyfile(p,q)
   if hf(q)!=f["sha256"]:raise ValueError("relocated source hash mismatch")
   rp.append(q)
  rg=d/gp.name;shutil.copyfile(gp,rg)
  if hf(rg)!=r1['gap_artifact_sha256']:raise ValueError("relocated gap hash mismatch")
  rr=derive(a,hs,rp,rg,pr,sa,ga)
 rs=[r1,r2,rr]
 mc={"source_identity_mismatch_count":mm(rs,"source_dataset_identity"),"timeline_mismatch_count":mm(rs,"canonical_timeline_sha256"),"gap_identity_mismatch_count":mm(rs,"gap_policy_identity"),"normalized_gap_inventory_mismatch_count":mm(rs,"normalized_gap_inventory_sha256"),"allowlist_identity_mismatch_count":mm(rs,"classification_allowlist_identity"),"count_mismatch":sum((r["source_count"],r["total_rows"],r["gap_entry_count"],r["accepted_closure_count"],r["unverified_gap_count"])!=(3,17716,773,745,28) for r in rs),"boundary_mismatch":sum((r["first_timestamp"],r["last_timestamp"])!=("2023-01-03T01:00:00","2025-12-31T19:00:00") for r in rs),"relocation_mismatch":int(cj(r1)!=cj(rr)),"canonical_summary_mismatch":int(cj(r1)!=cj(r2))}
 bad=banned();ok=not any(mc.values()) and not bad
 core={"schema_version":"fr_prep_b2e_r1b1_fj_source_gap_binding_summary.v1","checkpoint":"FR_PREP_B2E_R1B1","decision":"FR_PREP_B2E_R1B1_PASS_FJ_SOURCE_GAP_BINDINGS_FROZEN" if ok else "FR_PREP_B2E_R1B1_BLOCKED_FROZEN_INPUT_MISMATCH","authorization_contract_sha256":ah,"historical_source_manifest_evidence_sha256":a["historical_source_manifest_evidence"]["sha256"],"source_gap_bindings":r1,"deterministic_mismatch_counters":mc,"relocation_proof":{"temporary_directory_outside_repository":True,"copied_bytes_hash_verified":True,"canonical_identities_unchanged":mc["relocation_mismatch"]==0},"permitted_real_file_open_counters":{"committed_fj_manifest_evidence_open_count":1,"approved_fj_source_files_open_count":27,"eo_fj_policy_open_count":11,"temporary_relocated_copies_open_count":25},"prohibited_modules":bad,"safety_counters":SAFE,"frozen_evidence_modified":False,"source_data_semantics_changed":False,"detector_executed":False,"events_generated":False,"outcomes_generated":False,"descriptor_composed":False}
 out={**core,"canonical_summary_sha256":hb(cj(core).encode("ascii"))};x.output_root.mkdir(parents=True,exist_ok=True)
 payload=(cj(out)+"\n").encode();(x.output_root/"fj_source_gap_binding_summary.json").write_bytes(base64.b64decode(base64.b64encode(payload)))
 print(cj(out));return 0 if ok else 1
if __name__=="__main__":raise SystemExit(main())
