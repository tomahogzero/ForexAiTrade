#!/usr/bin/env python3
"""FR-Prep-B3 frozen FQ source/gap preflight; never executes the detector."""
from __future__ import annotations
import argparse,contextlib,copy,hashlib,importlib,io,json,ntpath,os,posixpath,shutil,subprocess,sys,tempfile
from pathlib import Path
import jsonschema

sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1]
TOOLS=ROOT/"tools"
AUTH=ROOT/"research/contracts/fr_prep_b3_fq_holdout_preflight_authorization.v1.json"
AUTH_SCHEMA=ROOT/"research/schemas/fr_prep_b3_fq_holdout_preflight_authorization.v1.schema.json"
EVIDENCE=ROOT/"research/contracts/fr_prep_b3_fq_holdout_preflight.v1.json"
EVIDENCE_SCHEMA=ROOT/"research/schemas/fr_prep_b3_fq_holdout_preflight.v1.schema.json"
RESULT=ROOT/"research/results/checkpoint_fr_prep_b3/fq_holdout_preflight_summary.json"
FROZEN_ROOT=ROOT/"research/results/checkpoint_fq_holdout_gap_boundary"
MODE="fq-holdout-preflight"
PASS="FR_PREP_B3_PASS_FQ_HOLDOUT_PREFLIGHT_SEALED"
ARTIFACTS=("checkpoint_fq_source_integrity.json","checkpoint_fq_gap_inventory.json","checkpoint_fq_gap_summary.json","checkpoint_fq_fail_closed_usability.json","checkpoint_fq_decision.json","checkpoint_fq_sha256_manifest.json","checkpoint_fq_deterministic_replay.json")
BASE=ARTIFACTS[:5]
DETECTOR="market_structure_break_retest_detector"
EXT_MARKERS=("terminal64","metatrader",".ex5","expertadvisor")

def canon(v): return json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=True)
def digest(v): return hashlib.sha256(canon(v).encode("ascii")).hexdigest()
def file_hash(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read_json(p): return json.loads(Path(p).read_text(encoding="utf-8"))
def abs_count(v):
    if isinstance(v,dict): return sum(abs_count(x) for x in v.values())
    if isinstance(v,list): return sum(abs_count(x) for x in v)
    return int(isinstance(v,str) and (ntpath.isabs(v) or posixpath.isabs(v)))

class ExternalAudit:
    def __init__(self): self.blocked=[]; self.success=0
    def deny(self,kind,command):
        self.blocked.append({"kind":kind,"mt5_or_ea":any(x in str(command).lower() for x in EXT_MARKERS)})
        raise RuntimeError("B3_EXTERNAL_PROCESS_BLOCKED")
    def __enter__(self):
        self.popen=subprocess.Popen; self.system=os.system; self.startfile=getattr(os,"startfile",None)
        subprocess.Popen=lambda command,*a,**k:self.deny("subprocess",command)
        os.system=lambda command:self.deny("os.system",command)
        if self.startfile is not None: os.startfile=lambda path,*a,**k:self.deny("os.startfile",path)
        return self
    def __exit__(self,*_):
        subprocess.Popen=self.popen; os.system=self.system
        if self.startfile is not None: os.startfile=self.startfile

def validate_bound_file(binding):
    p=(ROOT/binding["path"]).resolve()
    if not p.is_file() or file_hash(p)!=binding["file_sha256"]: raise SystemExit("B3_BOUND_FILE_MISMATCH")
    return p

def load_artifacts(root):
    return {name:read_json(Path(root)/name) for name in ARTIFACTS}

def normalized_artifacts(artifacts):
    out=copy.deepcopy(artifacts)
    for row in out["checkpoint_fq_source_integrity.json"]["yearly_files"]:
        row["path"]=ntpath.basename(row["path"])
    first={name:out[name] for name in BASE}
    out["checkpoint_fq_sha256_manifest.json"]={"artifacts":{name:digest(value) for name,value in first.items()}}
    out["checkpoint_fq_deterministic_replay.json"]={"byte_identical":True,"mismatch_count":0,"canonical_payload_sha256":digest(first)}
    return out

def make_runtime_contract(base,source_root):
    out=copy.deepcopy(base)
    by_name={x["filename"]:x for x in AUTH_DATA["source_files"]}
    if {Path(x["path"]).name for x in out["source_files"]}!=set(by_name): raise SystemExit("B3_SOURCE_SET_MISMATCH")
    for spec in out["source_files"]:
        name=Path(spec["path"]).name; approved=by_name[name]; p=(Path(source_root)/name).resolve()
        if not p.is_file() or file_hash(p)!=approved["sha256"] or spec["rows"]!=approved["rows"]:
            raise SystemExit("B3_SOURCE_INTEGRITY_MISMATCH")
        spec["path"]=str(p)
    return out

def invoke_validator(module,out_root,contract_path,counters):
    counters["fq_validator_execution_count"]+=1
    old_root,old_contract=module.ROOT,module.CONTRACT
    module.ROOT=Path(out_root); module.CONTRACT=Path(contract_path)
    try:
        with contextlib.redirect_stdout(io.StringIO()): module.main()
    finally:
        module.ROOT, module.CONTRACT=old_root,old_contract
    return load_artifacts(out_root)

def expect_failure(fn):
    try: fn()
    except (SystemExit,RuntimeError,ValueError): return True
    return False

def validate_expected(artifacts,expected):
    source=artifacts["checkpoint_fq_source_integrity.json"]
    gaps=artifacts["checkpoint_fq_gap_summary.json"]
    decision=artifacts["checkpoint_fq_decision.json"]
    replay=artifacts["checkpoint_fq_deterministic_replay.json"]
    got={"bars":source["timeline"]["total_merged_bars"],"timeline_sha256":source["timeline"]["canonical_timeline_sha256"],"gaps":gaps["total_detected_gaps"],"accepted_weekend_closures":gaps["routine_weekend_closures_accepted"],"accepted_daily_closures":gaps["routine_daily_closures_accepted"],"unverified_gaps":gaps["unverified_gaps"],"fq_decision":decision["decision"],"deterministic_payload_sha256":replay["canonical_payload_sha256"]}
    if got!=expected: raise SystemExit("B3_FROZEN_EXPECTATION_MISMATCH")
    return got

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--mode",required=True,choices=[MODE])
    parser.add_argument("--authorization",required=True)
    parser.add_argument("--source-root",required=True)
    parser.add_argument("--output-root",required=True)
    args=parser.parse_args()
    if Path(args.authorization).resolve()!=AUTH.resolve() or Path(args.output_root).resolve()!=RESULT.parent.resolve():
        raise SystemExit("B3_PATH_NOT_AUTHORIZED")

    global AUTH_DATA
    AUTH_DATA=read_json(AUTH); auth_schema=read_json(AUTH_SCHEMA)
    jsonschema.Draft202012Validator.check_schema(auth_schema)
    jsonschema.Draft202012Validator(auth_schema).validate(AUTH_DATA)
    bindings=AUTH_DATA["bindings"]
    b2a_contract_path=validate_bound_file(bindings["b2a_contract"])
    b2a_result_path=validate_bound_file(bindings["b2a_result"])
    validate_bound_file(bindings["wrapper"]); validate_bound_file(bindings["fq_validator"])
    source_contract_path=validate_bound_file(bindings["source_contract"])
    b2a=read_json(b2a_contract_path); b2a_result=read_json(b2a_result_path)
    b2a_core={k:v for k,v in b2a.items() if k!="canonical_summary_sha256"}
    b2a_identity=digest(b2a_core)
    if b2a_identity!=bindings["b2a_contract"]["canonical_summary_sha256"] or b2a.get("canonical_summary_sha256")!=b2a_identity or b2a_result.get("canonical_summary_sha256")!=b2a_identity:
        raise SystemExit("B3_B2A_IDENTITY_MISMATCH")
    frozen={}
    for name,expected_hash in AUTH_DATA["frozen_artifacts"].items():
        p=FROZEN_ROOT/name
        if not p.is_file() or file_hash(p)!=expected_hash: raise SystemExit("B3_FROZEN_ARTIFACT_MISMATCH")
        frozen[name]=read_json(p)
    source_root=Path(args.source_root).resolve()
    source_contract=read_json(source_contract_path)
    runtime_contract=make_runtime_contract(source_contract,source_root)
    expected=AUTH_DATA["expected"]
    validate_expected(frozen,expected)

    if str(TOOLS) not in sys.path: sys.path.insert(0,str(TOOLS))
    before=set(sys.modules)
    wrapper=importlib.import_module("fr_prep_runner_execution_wrapper")
    counts={"preflight_authorization_count":0,"fq_validator_execution_count":0,"detector_execution_count":0,"event_generation_count":0,"atr_event_generation_count":0,"tp_sl_calculation_count":0,"outcome_generation_count":0,"fn_interpretation_count":0,"holdout_execution_count":0,"mt5_execution_count":0,"ea_execution_count":0}
    def gate(auth,state,executor):
        counts["preflight_authorization_count"]+=1
        return wrapper.execute_fq_holdout_preflight(auth,state,executor)
    state={"b2a_validated":True,"b2a_summary_sha256":b2a_identity,"source_rows":expected["bars"],"canonical_timeline_sha256":expected["timeline_sha256"],"gap_count":expected["gaps"],"accepted_weekend_closures":expected["accepted_weekend_closures"],"accepted_daily_closures":expected["accepted_daily_closures"],"unverified_gaps":expected["unverified_gaps"],"fq_decision":expected["fq_decision"],"deterministic_payload_sha256":expected["deterministic_payload_sha256"]}

    with ExternalAudit() as external:
        def positive_suite():
            fq=importlib.import_module("run_checkpoint_fq_holdout_gap_boundary")
            with tempfile.TemporaryDirectory(prefix="fr_prep_b3_") as tmp:
                t=Path(tmp); c1=t/"contract1.json"; c2=t/"contract2.json"
                c1.write_text(json.dumps(runtime_contract),encoding="utf-8"); c2.write_text(json.dumps(runtime_contract),encoding="utf-8")
                one=invoke_validator(fq,t/"normal1",c1,counts)
                two=invoke_validator(fq,t/"normal2",c2,counts)
                relocated=t/"relocated_sources"; relocated.mkdir()
                for spec in AUTH_DATA["source_files"]:
                    shutil.copyfile(source_root/spec["filename"],relocated/spec["filename"])
                relocation_contract=make_runtime_contract(source_contract,relocated)
                c3=t/"contract3.json"; c3.write_text(json.dumps(relocation_contract),encoding="utf-8")
                three=invoke_validator(fq,t/"relocated_output",c3,counts)
                return one,two,three,fq,t
        one,two,three,fq,_=gate(AUTH_DATA,state,positive_suite)

        tests={}
        bad=copy.deepcopy(AUTH_DATA); bad["mode"]="WRONG"
        tests["wrong_authorization_blocked"]=expect_failure(lambda:gate(bad,state,lambda:None))
        with tempfile.TemporaryDirectory(prefix="fr_prep_b3_negative_") as negtmp:
            n=Path(negtmp)
            missing_contract=make_runtime_contract(source_contract,source_root)
            missing_contract["source_files"][0]["path"]=str(n/"missing.csv")
            mc=n/"missing_contract.json"; mc.write_text(json.dumps(missing_contract),encoding="utf-8")
            tests["missing_source_blocked"]=expect_failure(lambda:invoke_validator(fq,n/"missing_out",mc,counts))
            altered=n/"altered"; altered.mkdir()
            for spec in AUTH_DATA["source_files"]: shutil.copyfile(source_root/spec["filename"],altered/spec["filename"])
            with (altered/AUTH_DATA["source_files"][0]["filename"]).open("ab") as stream: stream.write(b"\n")
            altered_contract=copy.deepcopy(source_contract)
            for spec in altered_contract["source_files"]: spec["path"]=str(altered/Path(spec["path"]).name)
            ac=n/"altered_contract.json"; ac.write_text(json.dumps(altered_contract),encoding="utf-8")
            tests["altered_source_blocked"]=expect_failure(lambda:invoke_validator(fq,n/"altered_out",ac,counts))
        wrong_state=copy.deepcopy(state); wrong_state["source_rows"]+=1; wrong_state["canonical_timeline_sha256"]="0"*64
        tests["wrong_counts_or_hash_blocked"]=expect_failure(lambda:gate(AUTH_DATA,wrong_state,lambda:None))
        bad=copy.deepcopy(AUTH_DATA); bad["detector_import_allowed"]=True
        tests["detector_request_blocked"]=expect_failure(lambda:gate(bad,state,lambda:None))
        bad=copy.deepcopy(AUTH_DATA); bad["holdout_execution_allowed"]=True
        tests["holdout_execution_request_blocked"]=expect_failure(lambda:gate(bad,state,lambda:None))
        tests["external_process_blocked"]=expect_failure(lambda:subprocess.Popen(["terminal64.exe","/blocked"]))
        tests["absolute_runtime_path_leakage_detected"]=abs_count({"runtime_source_root":str(source_root)})==1

    after=set(sys.modules); imported=after-before
    module_counts={"wrapper_import_count":int("fr_prep_runner_execution_wrapper" in imported),"fq_validator_import_count":int("run_checkpoint_fq_holdout_gap_boundary" in imported),"detector_import_count":int(DETECTOR in imported or DETECTOR in sys.modules),"mt5_ea_import_count":sum(any(x in name.lower() for x in EXT_MARKERS) for name in imported)}
    committed_hashes={name:file_hash(FROZEN_ROOT/name) for name in ARTIFACTS}
    normalized_frozen=normalized_artifacts(frozen); normalized_three=normalized_artifacts(three)
    relocation_self_consistent=(three["checkpoint_fq_sha256_manifest.json"]=={"artifacts":{name:digest(three[name]) for name in BASE}} and three["checkpoint_fq_deterministic_replay.json"]=={"byte_identical":True,"mismatch_count":0,"canonical_payload_sha256":digest({name:three[name] for name in BASE})})
    mismatch={"normal_run_1_mismatch":int(one!=frozen),"normal_run_2_mismatch":int(two!=frozen),"normal_repeat_mismatch":int(one!=two),"relocation_semantic_mismatch":int(normalized_three!=normalized_frozen),"relocation_manifest_mismatch":int(not relocation_self_consistent),"count_or_hash_mismatch":int(validate_expected(one,expected)!=expected),"negative_test_mismatch":int(not all(tests.values())),"prohibited_import_mismatch":int(module_counts["detector_import_count"]!=0 or module_counts["mt5_ea_import_count"]!=0)}
    if any(mismatch.values()) or module_counts["wrapper_import_count"]!=1 or module_counts["fq_validator_import_count"]!=1:
        raise SystemExit("B3_PREFLIGHT_VALIDATION_FAILED")

    evidence={"schema_version":"fr_prep_b3_fq_holdout_preflight.v1","checkpoint":"FR_PREP_B3","decision":PASS,
    "b2a_evidence":{"canonical_summary_sha256":b2a_identity,"contract_file_sha256":file_hash(b2a_contract_path),"result_file_sha256":file_hash(b2a_result_path),"validated":True},
    "fq_preflight":expected,
    "artifact_comparison":{"normal_run_1_matches_committed":True,"normal_run_2_matches_committed":True,"normal_runs_identical":True,"relocation_semantics_match":True,"relocation_manifest_self_consistent":True,"committed_artifact_file_sha256":committed_hashes},
    "mismatch_counters":mismatch,
    "negative_tests":{"passed":sum(tests.values()),"total":len(tests),"all_passed":all(tests.values()),"results":tests},
    "runtime_audit":{"module_import_counts":module_counts,"function_execution_counts":counts,"external_process_audit":{"successful_launch_count":external.success,"blocked_launch_count":len(external.blocked)},"counter_provenance":{"module_imports":"sys.modules before/after delta and final prohibited-module absence","function_executions":"audited wrapper gate and FQ validator dispatch counters","external_process":"subprocess, os.system and os.startfile interception"}},
    "absolute_runtime_path_in_canonical_identity_count":0,"holdout_execution_allowed":False,"detector_executed":False,"events_generated":False,"atr_events_generated":False,"tp_sl_calculated":False,"outcomes_generated":False,"fn_interpretation_performed":False,"mt5_executed":False,"ea_executed":False,"performance":"NOT_EVALUATED","profitability":"NOT_CLAIMED","order_logic":"NOT_APPROVED","candidate":"NOT_READY_FOR_ORDER_LOGIC"}
    evidence["canonical_summary_sha256"]=digest(evidence)
    if abs_count(evidence): raise SystemExit("B3_ABSOLUTE_PATH_IDENTITY_LEAK")
    evidence_schema=read_json(EVIDENCE_SCHEMA)
    jsonschema.Draft202012Validator.check_schema(evidence_schema)
    jsonschema.Draft202012Validator(evidence_schema).validate(evidence)
    EVIDENCE.write_text(json.dumps(evidence,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    summary={"decision":PASS,"canonical_summary_sha256":evidence["canonical_summary_sha256"],"bars":expected["bars"],"gaps":expected["gaps"],"accepted_weekend_closures":expected["accepted_weekend_closures"],"accepted_daily_closures":expected["accepted_daily_closures"],"unverified_gaps":expected["unverified_gaps"],"fq_decision":expected["fq_decision"],"timeline_sha256":expected["timeline_sha256"],"deterministic_payload_sha256":expected["deterministic_payload_sha256"],"mismatch_count":sum(mismatch.values()),"negative_tests":{"passed":sum(tests.values()),"total":len(tests)},"prohibited_import_count":module_counts["detector_import_count"]+module_counts["mt5_ea_import_count"],"prohibited_execution_count":sum(counts[k] for k in ("detector_execution_count","event_generation_count","atr_event_generation_count","tp_sl_calculation_count","outcome_generation_count","fn_interpretation_count","holdout_execution_count","mt5_execution_count","ea_execution_count")),"performance":"NOT_EVALUATED","profitability":"NOT_CLAIMED"}
    RESULT.parent.mkdir(parents=True,exist_ok=True); RESULT.write_text(json.dumps(summary,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(summary,sort_keys=True))

if __name__=="__main__": main()
