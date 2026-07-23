"""Synthetic-only FR-Prep-B runner authorization boundary; never imports detector core."""
from __future__ import annotations
import hashlib, json
from pathlib import Path

AUTH_VERSION="fr_prep_runner_execution_authorization.v1"
STAGE="FR_PREP_B1_SYNTHETIC_ONLY"
MODES=frozenset({"FJ_BACKWARD_COMPATIBLE_REPLAY_ONLY","PREFLIGHT_ONLY"})
OPS=frozenset({"VALIDATE_SOURCE","VALIDATE_GAP_POLICY","COMPOSE_EXECUTION_DESCRIPTOR","RECONCILE_FROZEN_COUNTS","EMIT_SEALED_PREFLIGHT_REPORT","IMPORT_DETECTOR","EXECUTE_DETECTOR","EMIT_EVENT_POPULATION","EMIT_ATR_EVENTS","CALCULATE_TP_SL","EMIT_OUTCOMES","APPLY_FN_INTERPRETATION"})
PRE=frozenset({"VALIDATE_SOURCE","VALIDATE_GAP_POLICY","COMPOSE_EXECUTION_DESCRIPTOR","RECONCILE_FROZEN_COUNTS","EMIT_SEALED_PREFLIGHT_REPORT"})
FJ=frozenset({"VALIDATE_SOURCE","VALIDATE_GAP_POLICY","COMPOSE_EXECUTION_DESCRIPTOR","RECONCILE_FROZEN_COUNTS","IMPORT_DETECTOR","EXECUTE_DETECTOR","EMIT_EVENT_POPULATION"})
REQUIRED=("schema_version","implementation_stage","dataset_id","mode","requested_operations","detector_execution_allowed","outcome_execution_allowed")
class ValidationError(ValueError):
 def __init__(self,code): self.code=code; super().__init__(code)
def canon(v): return json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=True)
def digest(v): return hashlib.sha256(canon(v).encode()).hexdigest()
def counters(): return {"real_detector_import_count":0,"real_detector_execution_count":0,"injected_stub_loader_count":0,"injected_stub_execution_count":0,"event_population_emit_count":0,"atr_event_emit_count":0,"tp_sl_calculation_count":0,"outcome_emit_count":0,"fn_interpretation_count":0,"real_fj_fq_file_open_count":0}
def load_authorization(path):
 if not Path(path).is_file(): raise ValidationError("AUTHORIZATION_ARTIFACT_MISSING")
 try: raw=json.loads(Path(path).read_text(encoding="utf-8"))
 except (json.JSONDecodeError,UnicodeError): raise ValidationError("AUTHORIZATION_JSON_MALFORMED")
 if not isinstance(raw,dict): raise ValidationError("AUTHORIZATION_JSON_MALFORMED")
 return raw
def _validate_auth(a):
 if a.get("schema_version")!=AUTH_VERSION: raise ValidationError("AUTHORIZATION_SCHEMA_VERSION_UNSUPPORTED")
 if any(k not in a for k in REQUIRED): raise ValidationError("AUTHORIZATION_REQUIRED_FIELD_MISSING")
 if a["mode"] not in MODES: raise ValidationError("AUTHORIZATION_MODE_NOT_ALLOWLISTED")
 if not isinstance(a["requested_operations"],list) or any(x not in OPS for x in a["requested_operations"]): raise ValidationError("REQUESTED_OPERATION_NOT_ALLOWLISTED")
 if a["implementation_stage"]!=STAGE or a["dataset_id"] in {"FJ_2023_2025_GOLD_H1","FP_FQ_2020_2022_GOLD_H1"} or not a["dataset_id"].startswith("SYNTH_"): raise ValidationError("B1_REAL_DATASET_REJECTED")
 allowed=PRE if a["mode"]=="PREFLIGHT_ONLY" else FJ
 if any(x not in allowed for x in a["requested_operations"]): raise ValidationError("MODE_OPERATION_NOT_AUTHORIZED")
 if a["mode"]=="PREFLIGHT_ONLY" and a["detector_execution_allowed"]: raise ValidationError("DETECTOR_PERMISSION_CONTRADICTS_MODE")
 if a["outcome_execution_allowed"]: raise ValidationError("OUTCOME_PERMISSION_NOT_FALSE")
 return allowed
def execute(path, synthetic, loader=None, executor=None):
 c=counters(); a=load_authorization(path); allowed=_validate_auth(a)
 if not synthetic.get("source_valid",True): raise ValidationError("SOURCE_VALIDATION_FAILED")
 if not synthetic.get("gap_valid",True): raise ValidationError("GAP_POLICY_VALIDATION_FAILED")
 d=synthetic.get("descriptor",{})
 if d.get("dataset_id")!=a["dataset_id"]: raise ValidationError("AUTHORIZATION_DATASET_ID_MISMATCH")
 expected="ADAPTER_VALIDATION_ONLY" if a["mode"]=="PREFLIGHT_ONLY" else "SYNTHETIC_FJ_REPLAY_BOUND"
 if d.get("execution_mode")!=expected: raise ValidationError("AUTHORIZATION_DESCRIPTOR_MODE_CONFLICT")
 if not synthetic.get("descriptor_valid",True): raise ValidationError("DESCRIPTOR_VALIDATION_FAILED")
 if not synthetic.get("counts_valid",True): raise ValidationError("FROZEN_COUNT_RECONCILIATION_FAILED")
 # Detector access is deliberately after every validation/reconciliation gate.
 event=None
 if "IMPORT_DETECTOR" in allowed and "IMPORT_DETECTOR" in a["requested_operations"]:
  if loader is None: raise ValidationError("SYNTHETIC_DETECTOR_LOADER_REQUIRED")
  c["injected_stub_loader_count"]+=1; loaded=loader()
  if "EXECUTE_DETECTOR" in a["requested_operations"]:
   c["injected_stub_execution_count"]+=1; event=(executor or loaded)()
  if "EMIT_EVENT_POPULATION" in a["requested_operations"]: c["event_population_emit_count"]+=1
 report={"authorization_identity":digest(a),"authorization_mode":a["mode"],"dataset_identity":digest({"dataset_id":a["dataset_id"]}),"source_validation_identity":"SYNTH_SOURCE","source_validation_sha256":"0"*64,"gap_policy_validation_identity":"SYNTH_GAP","gap_policy_validation_sha256":"1"*64,"execution_descriptor_identity":digest(d),"execution_descriptor_sha256":digest(d),"reconciled_synthetic_counts":synthetic.get("counts",{}),"allowed_operations":sorted(allowed),"rejected_execution_capabilities":sorted(OPS-allowed),"detector_import_count":c["real_detector_import_count"],"detector_execution_count":c["real_detector_execution_count"],"safety_status":{"broker_history_completeness":"NOT_PROVEN","strategy_performance":"NOT_EVALUATED","profitability":"NOT_CLAIMED","order_logic":"NOT_APPROVED","candidate":"NOT_READY_FOR_ORDER_LOGIC"}}
 return {"report":report,"synthetic_event_population":event,"counters":c}


# FR-Prep-B2 exact frozen-FJ authorization boundary. This extension is kept
# separate from the B1 synthetic validator so B1 behavior remains compatible.
B2_STAGE = "FR_PREP_B2_FROZEN_FJ_BACKWARD_COMPATIBLE_REPLAY"
B2_DATASET = "FJ_2023_2025_GOLD_H1"
B2_DESCRIPTOR_ID = "dd325e9a81de40c07e5a579226b4d82d3bfdb06b8a14e3f1a562b8e847119848"
B2_SUMMARY_ID = "b34fc49c4fc83696abceeccf6d2194253be83811b14b4ed060e33b3eed7936a3"
B2_EXPECTED = {
    "source_rows": 17716,
    "gap_count": 773,
    "accepted_closures": 745,
    "unverified_gaps": 28,
}
B2_OPERATIONS = frozenset({
    "VALIDATE_FROZEN_R1B1C_EVIDENCE",
    "VALIDATE_FROZEN_R1B2_DESCRIPTOR",
    "IMPORT_FROZEN_DETECTOR",
    "EXECUTE_FROZEN_FJ_REPLAY",
    "COMPARE_LEGACY_EVENT_POPULATION",
    "CONTROLLED_RELOCATION_REPLAY",
})


def execute_frozen_fj_replay(authorization, validated, loader, executor):
    """Execute the exact FJ replay only after every frozen gate is proven."""
    if not isinstance(authorization, dict):
        raise ValidationError("B2_AUTHORIZATION_NOT_OBJECT")
    if authorization.get("implementation_stage") != B2_STAGE:
        raise ValidationError("B2_AUTHORIZATION_STAGE_MISMATCH")
    if authorization.get("dataset_id") != B2_DATASET:
        raise ValidationError("B2_AUTHORIZATION_DATASET_MISMATCH")
    if authorization.get("mode") != "FJ_BACKWARD_COMPATIBLE_REPLAY_ONLY":
        raise ValidationError("B2_AUTHORIZATION_MODE_MISMATCH")
    requested = authorization.get("requested_operations")
    if not isinstance(requested, list) or set(requested) != B2_OPERATIONS:
        raise ValidationError("B2_AUTHORIZATION_OPERATION_MISMATCH")
    if authorization.get("detector_execution_allowed") is not True:
        raise ValidationError("B2_DETECTOR_PERMISSION_REQUIRED")
    denied = ("outcome_execution_allowed", "fq_access_allowed", "atr_event_generation_allowed", "tp_sl_calculation_allowed", "fn_interpretation_allowed", "mt5_execution_allowed", "ea_execution_allowed")
    if any(authorization.get(key) is not False for key in denied):
        raise ValidationError("B2_PROHIBITED_PERMISSION_NOT_FALSE")
    if not isinstance(validated, dict):
        raise ValidationError("B2_VALIDATION_STATE_MISSING")
    exact = {
        "r1b1c_validated": True,
        "r1b2_validated": True,
        "source_validated": True,
        "gap_validated": True,
        "descriptor_validated": True,
        "descriptor_identity_sha256": B2_DESCRIPTOR_ID,
        "r1b2_summary_sha256": B2_SUMMARY_ID,
        **B2_EXPECTED,
    }
    if any(validated.get(key) != value for key, value in exact.items()):
        raise ValidationError("B2_FROZEN_BINDING_MISMATCH")
    if loader is None or executor is None:
        raise ValidationError("B2_LAZY_DETECTOR_BOUNDARY_REQUIRED")
    loaded = loader()
    return executor(loaded)

# FR-Prep-B3 exact frozen-FQ preflight boundary. This gate authorizes source
# and gap validation only; it cannot import or execute the detector.
B3_STAGE = "FR_PREP_B3_FQ_HOLDOUT_PREFLIGHT_ONLY"
B3_DATASET = "FP_FQ_2020_2022_GOLD_H1"
B3_B2A_SUMMARY_ID = "1f63983bf783452bd0e56d6c265f67f3baccbaae644eedcacb59a1f79a895251"
B3_OPERATIONS = frozenset({
    "VALIDATE_B2A_INDEPENDENT_AUDIT",
    "VALIDATE_FROZEN_FQ_SOURCES",
    "VALIDATE_FROZEN_FQ_GAPS",
    "COMPARE_COMMITTED_FQ_ARTIFACTS",
    "DETERMINISTIC_PREFLIGHT_REPLAY",
    "CONTROLLED_RELOCATION_PREFLIGHT",
})
B3_EXPECTED = {
    "source_rows": 17731,
    "canonical_timeline_sha256": "4ff441fa895c3e7d8f256b11501d7dac6bf5e606ef1c90d2d409c39689a81c38",
    "gap_count": 774,
    "accepted_weekend_closures": 149,
    "accepted_daily_closures": 0,
    "unverified_gaps": 625,
    "fq_decision": "FQ_CONDITIONAL_PASS_HIGH_EXCLUSION_RISK",
    "deterministic_payload_sha256": "1b724dda83136a926beb48125b4d2ebc771fa642d798ad556df8b3905d86e641",
}


def execute_fq_holdout_preflight(authorization, validated, executor):
    """Run only the exact FQ source/gap preflight after every gate is proven."""
    if not isinstance(authorization, dict):
        raise ValidationError("B3_AUTHORIZATION_NOT_OBJECT")
    if authorization.get("implementation_stage") != B3_STAGE:
        raise ValidationError("B3_AUTHORIZATION_STAGE_MISMATCH")
    if authorization.get("dataset_id") != B3_DATASET:
        raise ValidationError("B3_AUTHORIZATION_DATASET_MISMATCH")
    if authorization.get("mode") != "FQ_HOLDOUT_PREFLIGHT_ONLY":
        raise ValidationError("B3_AUTHORIZATION_MODE_MISMATCH")
    requested = authorization.get("requested_operations")
    if not isinstance(requested, list) or set(requested) != B3_OPERATIONS:
        raise ValidationError("B3_AUTHORIZATION_OPERATION_MISMATCH")
    denied = (
        "holdout_execution_allowed",
        "detector_import_allowed",
        "detector_execution_allowed",
        "event_generation_allowed",
        "atr_event_generation_allowed",
        "tp_sl_calculation_allowed",
        "outcome_execution_allowed",
        "fn_interpretation_allowed",
        "external_process_allowed",
        "mt5_execution_allowed",
        "ea_execution_allowed",
    )
    if any(authorization.get(key) is not False for key in denied):
        raise ValidationError("B3_PROHIBITED_PERMISSION_NOT_FALSE")
    if not isinstance(validated, dict):
        raise ValidationError("B3_VALIDATION_STATE_MISSING")
    exact = {
        "b2a_validated": True,
        "b2a_summary_sha256": B3_B2A_SUMMARY_ID,
        **B3_EXPECTED,
    }
    if any(validated.get(key) != value for key, value in exact.items()):
        raise ValidationError("B3_FROZEN_BINDING_MISMATCH")
    if executor is None:
        raise ValidationError("B3_PREFLIGHT_EXECUTOR_REQUIRED")
    return executor()
