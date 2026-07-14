#!/usr/bin/env python3
"""Artifact-only conservative FE decision from FC contract and FD report."""
from __future__ import annotations
import argparse,json
from pathlib import Path

def main():
 p=argparse.ArgumentParser();p.add_argument('--fd-report',required=True);p.add_argument('--results-root',required=True);a=p.parse_args()
 fd=json.loads(Path(a.fd_report).read_text(encoding='utf-8'))
 required={'full_population','direction','year','atr_regime','setup_subtype','diagnostic_reason','market_session'}
 if set(fd['dimensions'])!=required or fd['atr_boundaries']!={'p33':4.4567000000000005,'p67':7.02}:raise SystemExit('FC frozen contract integrity failed')
 full=fd['dimensions']['full_population']['ALL']
 if any(full[f'H{h}']['outcomes']['TP_FIRST']>=full[f'H{h}']['outcomes']['SL_FIRST'] for h in (6,12,24,48)):raise SystemExit('Unexpected FD full-population condition; FE disposition requires review')
 decision={
  'execution_status':'PASS','method':'artifact-only FC/FD research decision gate','fc_fd_contract_integrity':'PASS','selected_disposition':'REJECT_CURRENT_CANDIDATE',
  'full_population_first':full,'all_preregistered_subgroups':fd['dimensions'],
  'decision_matrix':[
   {'option':'REJECT_CURRENT_CANDIDATE','selected':True,'evidence':'All full-population horizons have TP_FIRST counts below SL_FIRST; no preregistered subgroup is selected to override full-population evidence.'},
   {'option':'RESEARCH_MORE_WITH_NEW_HYPOTHESIS','selected':False,'reason':'FD supplies no separately preregistered non-trading hypothesis that is justified without post-hoc selection.'},
   {'option':'INSUFFICIENT_EVIDENCE','selected':False,'reason':'Current evidence is sufficient for a conservative disposition, not for execution design.'},
   {'option':'ELIGIBLE_FOR_SEPARATE_FORWARD_DIAGNOSTIC_DESIGN','selected':False,'reason':'Consistency/adequacy criteria are not met without selecting post-hoc subgroups; order logic remains unapproved.'}],
  'limitations':['Broker-history completeness is NOT_PROVEN.','Horizon populations differ because fail-closed exclusions differ.','Outcome counts/rates are diagnostic labels, not profitability, expected return, or trading-edge evidence.','setup subtype, diagnostic reason, and market session are NOT_AVAILABLE.'],
  'future_conditions':['No current follow-up checkpoint is justified.','Any future candidate requires a separately preregistered new hypothesis, frozen inputs, and materially new independent evidence before a new decision gate.'],
  'strategy_performance_status':'NOT_EVALUATED','order_logic_status':'NOT_APPROVED','paf_status':'NOT_READY_FOR_ORDER_LOGIC','profitability_claim':False}
 root=Path(a.results_root);root.mkdir(parents=True,exist_ok=True)
 (root/'checkpoint_fe_research_decision_gate.json').write_text(json.dumps(decision,indent=2)+'\n',encoding='utf-8')
 lines=['# Checkpoint FE Research Decision Gate','',f"- selected disposition: `{decision['selected_disposition']}`",'- strategy performance: `NOT_EVALUATED`','- order logic: `NOT_APPROVED`','- PAF: `NOT_READY_FOR_ORDER_LOGIC`','- profitability: `NOT_CLAIMED`','', 'No follow-up checkpoint is justified for the current candidate.']
 (root/'checkpoint_fe_research_decision_gate.md').write_text('\n'.join(lines)+'\n',encoding='utf-8');print(json.dumps(decision,indent=2));return 0
if __name__=='__main__':raise SystemExit(main())
