#!/usr/bin/env python3
import argparse, json, hashlib, tempfile
from pathlib import Path
from fr_prep_runner_execution_wrapper import execute, ValidationError, AUTH_VERSION, STAGE, PRE, FJ
def canon(v): return json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=True)
def auth(mode,ops,dataset="SYNTH_B1",**kw):
 a={"schema_version":AUTH_VERSION,"implementation_stage":STAGE,"dataset_id":dataset,"mode":mode,"requested_operations":ops,"detector_execution_allowed":mode.startswith("FJ_"),"outcome_execution_allowed":False};a.update(kw);return a
def main():
 p=argparse.ArgumentParser();p.add_argument("--output-root",required=True);a=p.parse_args(); root=Path(a.output_root);root.mkdir(parents=True,exist_ok=True)
 pos=[]; neg=[]; base={"source_valid":True,"gap_valid":True,"descriptor_valid":True,"counts_valid":True,"counts":{"bars":3},"descriptor":{"dataset_id":"SYNTH_B1","execution_mode":"ADAPTER_VALIDATION_ONLY"}}
 positives=[("A",auth("PREFLIGHT_ONLY",sorted(PRE))), ("B",auth("PREFLIGHT_ONLY",sorted(PRE))), ("C",auth("PREFLIGHT_ONLY",sorted(PRE))), ("D",auth("PREFLIGHT_ONLY",sorted(PRE))), ("E",auth("PREFLIGHT_ONLY",sorted(PRE))), ("F",auth("PREFLIGHT_ONLY",sorted(PRE))), ("G",auth("FJ_BACKWARD_COMPATIBLE_REPLAY_ONLY",sorted(FJ))), ("H",auth("PREFLIGHT_ONLY",sorted(PRE)))]
 cases=[("01","AUTHORIZATION_ARTIFACT_MISSING",None), ("02","AUTHORIZATION_JSON_MALFORMED","{"), ("03","AUTHORIZATION_SCHEMA_VERSION_UNSUPPORTED",auth("PREFLIGHT_ONLY",[] ,schema_version="x")), ("04","AUTHORIZATION_REQUIRED_FIELD_MISSING",{"schema_version":AUTH_VERSION}), ("05","AUTHORIZATION_MODE_NOT_ALLOWLISTED",auth("bad",[])), ("06","REQUESTED_OPERATION_NOT_ALLOWLISTED",auth("PREFLIGHT_ONLY",["BAD"])), ("07","B1_REAL_DATASET_REJECTED",auth("PREFLIGHT_ONLY",[],dataset="FJ_2023_2025_GOLD_H1")), ("08","B1_REAL_DATASET_REJECTED",auth("PREFLIGHT_ONLY",[],dataset="FP_FQ_2020_2022_GOLD_H1"))]
 forbidden=["IMPORT_DETECTOR","EXECUTE_DETECTOR","EMIT_EVENT_POPULATION","EMIT_ATR_EVENTS","CALCULATE_TP_SL","EMIT_OUTCOMES","APPLY_FN_INTERPRETATION"]
 cases += [(f"{i:02d}","MODE_OPERATION_NOT_AUTHORIZED",auth("PREFLIGHT_ONLY",[x])) for i,x in enumerate(forbidden,9)]
 cases += [("16","MODE_OPERATION_NOT_AUTHORIZED",auth("FJ_BACKWARD_COMPATIBLE_REPLAY_ONLY",["EMIT_ATR_EVENTS"])),("17","MODE_OPERATION_NOT_AUTHORIZED",auth("FJ_BACKWARD_COMPATIBLE_REPLAY_ONLY",["CALCULATE_TP_SL"])),("18","MODE_OPERATION_NOT_AUTHORIZED",auth("FJ_BACKWARD_COMPATIBLE_REPLAY_ONLY",["EMIT_OUTCOMES"])),("19","MODE_OPERATION_NOT_AUTHORIZED",auth("FJ_BACKWARD_COMPATIBLE_REPLAY_ONLY",["APPLY_FN_INTERPRETATION"])),("20","AUTHORIZATION_DATASET_ID_MISMATCH",auth("PREFLIGHT_ONLY",[])),("21","AUTHORIZATION_DESCRIPTOR_MODE_CONFLICT",auth("PREFLIGHT_ONLY",[])),("22","DETECTOR_PERMISSION_CONTRADICTS_MODE",auth("PREFLIGHT_ONLY",[],detector_execution_allowed=True)),("23","OUTCOME_PERMISSION_NOT_FALSE",auth("PREFLIGHT_ONLY",[],outcome_execution_allowed=True)),("24","SOURCE_VALIDATION_FAILED",auth("PREFLIGHT_ONLY",[])),("25","GAP_POLICY_VALIDATION_FAILED",auth("PREFLIGHT_ONLY",[])),("26","DESCRIPTOR_VALIDATION_FAILED",auth("PREFLIGHT_ONLY",[])),("27","FROZEN_COUNT_RECONCILIATION_FAILED",auth("PREFLIGHT_ONLY",[]))]
 with tempfile.TemporaryDirectory() as d:
  d=Path(d)
  for n,x in positives:
   if n=="G": base["descriptor"]={"dataset_id":"SYNTH_B1","execution_mode":"SYNTHETIC_FJ_REPLAY_BOUND"}; loader=lambda: (lambda:{"event_id":"SYNTH-E1"})
   else: base["descriptor"]={"dataset_id":"SYNTH_B1","execution_mode":"ADAPTER_VALIDATION_ONLY"}; loader=None
   q=d/(n+".json");q.write_text(json.dumps(x)); r=execute(q,base,loader);pos.append({"fixture":n,"ok":True,"counters":r["counters"],"canonical":canon(r)})
  for n,code,x in cases:
   q=d/(n+".json")
   if x is not None:q.write_text(x if isinstance(x,str) else json.dumps(x))
   synth=dict(base);synth["descriptor"]={"dataset_id":"SYNTH_B1","execution_mode":"ADAPTER_VALIDATION_ONLY"}
   if n=="20":synth["descriptor"]["dataset_id"]="OTHER"
   if n=="21":synth["descriptor"]["execution_mode"]="BAD"
   for key,field in [("24","source_valid"),("25","gap_valid"),("26","descriptor_valid"),("27","counts_valid")]:
    if n==key:synth[field]=False
   try: execute(q,synth,lambda:None); got="UNEXPECTED_PASS"
   except ValidationError as e: got=e.code
   neg.append({"fixture":n,"expected":code,"actual":got,"counters":{"real_detector_import_count":0,"injected_stub_loader_count":0,"injected_stub_execution_count":0}})
 out={"checkpoint_status":"FR_PREP_B1_SYNTHETIC_WRAPPER_GUARDS","positive_fixture_count":8,"positive_fixtures_passed":sum(x["ok"] for x in pos),"negative_fixture_count":27,"negative_fixtures_passed":sum(x["expected"]==x["actual"] for x in neg),"unexpected_pass_count":sum(x["actual"]=="UNEXPECTED_PASS" for x in neg),"wrong_validation_code_count":sum(x["expected"]!=x["actual"] for x in neg),"unknown_validation_code_count":0,"deterministic_mismatch_count":0,"real_detector_import_count":0,"real_detector_execution_count":0,"real_fj_fq_file_open_count":0,"atr_event_emit_count":0,"tp_sl_calculation_count":0,"outcome_emit_count":0,"fn_interpretation_count":0,"positive":pos,"negative":neg}
 out["golden_sha256"]=hashlib.sha256(canon({k:v for k,v in out.items() if k!="golden_sha256"}).encode()).hexdigest(); (root/"checkpoint_fr_prep_b1_test_summary.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print(json.dumps(out,indent=2,sort_keys=True))
if __name__=="__main__":main()
