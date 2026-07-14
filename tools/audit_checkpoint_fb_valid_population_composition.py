#!/usr/bin/env python3
"""Artifact-only composition audit for EU fail-closed inclusions/exclusions."""
from __future__ import annotations
import argparse, csv, json
from collections import Counter, defaultdict
from pathlib import Path

def main() -> int:
    p=argparse.ArgumentParser(); p.add_argument('--outcomes-csv',required=True); p.add_argument('--results-root',required=True); a=p.parse_args()
    rows=list(csv.DictReader(Path(a.outcomes_csv).open(encoding='utf-8',newline='')))
    if len(rows)!=1600 or len({(r['run_id'],r['case_id'],r['event_time']) for r in rows})!=1600: raise SystemExit('event-key conservation failed')
    report={'execution_status':'PASS','method':'artifact-only composition audit','total_events':1600,'broker_history_completeness':'NOT_PROVEN','horizons':{},'strategy_performance_status':'NOT_EVALUATED','order_logic_status':'NOT_APPROVED','paf_status':'NOT_READY_FOR_ORDER_LOGIC','profitability_claim':False}
    for h in (6,12,24,48):
        by_year=defaultdict(Counter); by_direction=defaultdict(Counter)
        for r in rows:
            status=r[f'h{h}_eligibility']; by_year[r['event_time'][:4]][status]+=1; by_direction[r['paf_candidate_direction']][status]+=1
        if sum(v['INCLUDED']+v['EXCLUDED'] for v in by_year.values())!=1600: raise SystemExit(f'conservation H{h}')
        report['horizons'][str(h)]={'by_year':{k:dict(v) for k,v in sorted(by_year.items())},'by_direction':{k:dict(v) for k,v in sorted(by_direction.items())}}
    root=Path(a.results_root);root.mkdir(parents=True,exist_ok=True)
    (root/'checkpoint_fb_valid_population_composition.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    (root/'checkpoint_fb_valid_population_composition.md').write_text('# Checkpoint FB Valid Population Composition Audit\n\nDiagnostic coverage only; not strategy performance.\n\n'+json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2));return 0
if __name__=='__main__': raise SystemExit(main())
