#!/usr/bin/env python3
"""Run only the frozen FC diagnostic subgroup report on EU outcomes."""
from __future__ import annotations
import argparse,csv,json
from collections import Counter
from pathlib import Path

OUT=('TP_FIRST','SL_FIRST','AMBIGUOUS_SAME_BAR','NO_RESOLUTION')
def percentile(values,p):
    values=sorted(values); pos=(len(values)-1)*p; lo=int(pos); hi=min(lo+1,len(values)-1); return values[lo]+(values[hi]-values[lo])*(pos-lo)
def summarize(rows,h):
    inc=[r for r in rows if r[f'h{h}_eligibility']=='INCLUDED']; exc=[r for r in rows if r[f'h{h}_eligibility']=='EXCLUDED']; c=Counter(r[f'h{h}_outcome'] for r in inc)
    result={'population':len(rows),'included':len(inc),'excluded':len(exc),'exclusion_rate_pct':round(len(exc)/len(rows)*100,2),'status':'DESCRIPTIVE' if len(inc)>=30 else 'INSUFFICIENT_SAMPLE'}
    result['outcomes']={o:c[o] for o in OUT}
    if len(inc)>=30: result['descriptive_rates_pct']={o:round(c[o]/len(inc)*100,2) for o in OUT}
    return result
def main():
 p=argparse.ArgumentParser();p.add_argument('--outcomes-csv',required=True);p.add_argument('--results-root',required=True);a=p.parse_args()
 rows=list(csv.DictReader(Path(a.outcomes_csv).open(encoding='utf-8',newline='')))
 if len(rows)!=1600 or len({(r['run_id'],r['case_id'],r['event_time']) for r in rows})!=1600:raise SystemExit('event-key conservation failed')
 vals=[float(r['atr']) for r in rows]; p33,p67=percentile(vals,.33),percentile(vals,.67)
 def atr_group(r):
  x=float(r['atr']);return 'LOW' if x<p33 else 'MID' if x<=p67 else 'HIGH'
 dimensions={'full_population':{'ALL':rows},'direction':{v:[r for r in rows if r['paf_candidate_direction']==v] for v in ('BUY','SELL')},'year':{v:[r for r in rows if r['event_time'][:4]==v] for v in ('2023','2024','2025')},'atr_regime':{v:[r for r in rows if atr_group(r)==v] for v in ('LOW','MID','HIGH')},'setup_subtype':{'NOT_AVAILABLE':[]},'diagnostic_reason':{'NOT_AVAILABLE':[]},'market_session':{'NOT_AVAILABLE':[]}}
 report={'execution_status':'PASS','method':'FC-preregistered artifact-only subgroup report','total_events':1600,'atr_boundaries':{'p33':p33,'p67':p67},'dimensions':{},'strategy_performance_status':'NOT_EVALUATED','order_logic_status':'NOT_APPROVED','paf_status':'NOT_READY_FOR_ORDER_LOGIC','profitability_claim':False}
 for dim,groups in dimensions.items():report['dimensions'][dim]={name:({'availability':'NOT_AVAILABLE'} if name=='NOT_AVAILABLE' else {f'H{h}':summarize(group,h) for h in (6,12,24,48)}) for name,group in groups.items()}
 root=Path(a.results_root);root.mkdir(parents=True,exist_ok=True);(root/'checkpoint_fd_preregistered_subgroups.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');(root/'checkpoint_fd_preregistered_subgroups.md').write_text('# Checkpoint FD Preregistered Subgroups\n\nDiagnostic hypotheses only; no performance conclusion.\n\n'+json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(report,indent=2));return 0
if __name__=='__main__':raise SystemExit(main())
