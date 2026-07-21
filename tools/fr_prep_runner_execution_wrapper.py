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
