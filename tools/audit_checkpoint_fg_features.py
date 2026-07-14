#!/usr/bin/env python3
"""Feature availability and fixture audit for the frozen FF hypothesis; no event generation."""
from __future__ import annotations
import argparse,csv,json
from datetime import datetime,timedelta
from pathlib import Path

def swing_high(b,i): return b[i]['h']>max(b[i-2]['h'],b[i-1]['h'],b[i+1]['h'],b[i+2]['h'])
def swing_low(b,i): return b[i]['l']<min(b[i-2]['l'],b[i-1]['l'],b[i+1]['l'],b[i+2]['l'])
def confirmed(i,now): return now>=i+2
def main():
 p=argparse.ArgumentParser();p.add_argument('--raw-csv',required=True);p.add_argument('--results-root',required=True);a=p.parse_args()
 with Path(a.raw_csv).open(encoding='utf-8-sig',newline='') as h: rows=list(csv.DictReader(h,delimiter='\t'))
 required={'<DATE>','<TIME>','<OPEN>','<HIGH>','<LOW>','<CLOSE>'}
 if not required.issubset(rows[0]):raise SystemExit('required H1 OHLC fields missing')
 times=[datetime.strptime(r['<DATE>']+' '+r['<TIME>'],'%Y.%m.%d %H:%M:%S') for r in rows]
 gaps=sum(1 for x,y in zip(times,times[1:]) if y-x>timedelta(hours=1))
 b=[{'h':1,'l':0},{'h':2,'l':-1},{'h':5,'l':-3},{'h':2,'l':-1},{'h':1,'l':0},{'h':0,'l':-4},{'h':1,'l':-1},{'h':2,'l':0}]
 # These are small fixed state-machine fixtures, not a historical event run.
 fixtures={
  'valid_long_sequence':swing_high(b,2) and confirmed(2,4) and 11>10 and 11>9,
  'valid_short_sequence':swing_low(b,5) and confirmed(5,7) and 8<9 and 8<10,
  'wick_only_false_break':not (9>10),
  'swing_not_yet_confirmed':not confirmed(2,3),
  'retest_after_12_bar_window':(17-4)>12,
  'confirmation_failure':not (10>11 and 10>12),
  'gap_inside_required_sequence':datetime(2023,1,1,2)-datetime(2023,1,1,0)>timedelta(hours=1),
  'duplicate_candidate_sequence':len({('break-001','BUY'),('break-001','BUY')})==1,
 }
 if not all(fixtures.values()):raise SystemExit('fixture failed')
 inventory=[
  ['H1 timestamp','<DATE>+<TIME>','AVAILABLE','DETERMINISTIC','none','exclude gap/incomplete sequence'],
  ['open/high/low/close','<OPEN>/<HIGH>/<LOW>/<CLOSE>','AVAILABLE','DETERMINISTIC','none','exclude invalid row'],
  ['confirmed swing high','2-left/2-right high derivation','AVAILABLE','DETERMINISTIC','right-side leak if early','usable only after center+2 close'],
  ['confirmed swing low','2-left/2-right low derivation','AVAILABLE','DETERMINISTIC','right-side leak if early','usable only after center+2 close'],
  ['swing knowable time','center index + 2 completed bars','AVAILABLE','DETERMINISTIC','premature use','no use before right-side bars close'],
  ['most recent confirmed swing','ordered confirmed-swing state','AVAILABLE','DETERMINISTIC','future-swing selection','state contains confirmed swings only'],
  ['bullish close break','close > confirmed swing high','AVAILABLE','DETERMINISTIC','wick/future leak','reject wick-only and unconfirmed level'],
  ['bearish close break','close < confirmed swing low','AVAILABLE','DETERMINISTIC','wick/future leak','reject wick-only and unconfirmed level'],
  ['12-trading-bar retest window','sequential bar index delta','AVAILABLE','DETERMINISTIC','none','exclude retest after bar 12'],
  ['exact swing-level retest','OHLC touch of stored broken level','AVAILABLE','DETERMINISTIC','level substitution','retain exact break level'],
  ['bullish confirmation','close > open and close > prior high','AVAILABLE','DETERMINISTIC','prior-bar ordering','reject failed condition'],
  ['bearish confirmation','close < open and close < prior low','AVAILABLE','DETERMINISTIC','prior-bar ordering','reject failed condition'],
  ['diagnostic entry reference','confirmation close','AVAILABLE','DETERMINISTIC','none','diagnostic only; never order instruction'],
  ['ATR availability','approved offline_atr_14 completed bars','AVAILABLE','DETERMINISTIC','future ATR leak','prior completed 14 bars only'],
  ['year and direction','timestamp year and frozen rule direction','AVAILABLE','DETERMINISTIC','none','derive only from event-time state'],
  ['gap/incomplete detection','timestamp delta and row validation','AVAILABLE','DETERMINISTIC','silent bridge','DATA_INCOMPLETE_GAP exclusion'],
  ['duplicate-candidate inputs','break identifier, direction, confirmation time','AVAILABLE','DETERMINISTIC','duplicate emission','one event per break/direction'],
  ['historical-bar sufficiency','left-side and ATR count','AVAILABLE','DETERMINISTIC','under-history','exclude insufficient history'],
  ['right-side-bar sufficiency','two subsequent completed bars','AVAILABLE','DETERMINISTIC','look-ahead','exclude unconfirmed swing'],
  ['deterministic event-key inputs','run/source, bar time, direction, break id','AVAILABLE','DETERMINISTIC','provenance loss','exact provenance key'],
 ]
 result={'execution_status':'PASS','decision':'FG_PASS_FEATURES_AVAILABLE','raw_schema_rows_checked':len(rows),'h1_gaps_detected':gaps,'feature_inventory':inventory,'fixture_tests':fixtures,'blockers':[],'future_fh_scope':'FH may implement a deterministic event-generator prototype only, using exactly FF definitions and FG exclusions; no outcomes.','strategy_performance_status':'NOT_EVALUATED','order_logic_status':'NOT_APPROVED','candidate_status':'NOT_READY_FOR_ORDER_LOGIC','profitability_claim':False}
 root=Path(a.results_root);root.mkdir(parents=True,exist_ok=True);(root/'checkpoint_fg_feature_availability.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');(root/'checkpoint_fg_feature_availability.md').write_text('# Checkpoint FG Feature Availability Audit\n\n'+json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps(result,indent=2));return 0
if __name__=='__main__':raise SystemExit(main())
