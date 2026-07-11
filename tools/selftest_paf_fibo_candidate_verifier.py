#!/usr/bin/env python3
from paf_fibo_candidate_verifier import classify

BASE={"run_id":"r","window_index":"1","phase":"p","event_time":"t","runtime_symbol":"GOLD#","timeframe":"H1","authoritative_source":"ea_mirror.log","case_id":"c","classification":"POSSIBLE_FIBO_PULLBACK","paf_candidate_direction":"BUY","paf_direction_is_usable_for_first_touch":"true","paf_direction_source":"EMA_CONTEXT","paf_direction_reason":"OK","paf_fibo_direction_gap_reason":"NONE","schema_origin":"NATIVE"}
cases=[(BASE,"ELIGIBLE_DIAGNOSTIC_ROW"),({**BASE,"paf_candidate_direction":"DIRECTION_UNKNOWN","paf_direction_is_usable_for_first_touch":"false","paf_fibo_direction_gap_reason":"PRICE_BETWEEN_EMAS"},"REJECTED_DIRECTION_GAP"),({**BASE,"classification":"NO_SETUP"},"NOT_APPLICABLE"),({**BASE,"runtime_symbol":""},"INVALID_DATA"),({**BASE,"paf_candidate_direction":"DIRECTION_UNKNOWN"},"INVALID_DATA"),({**BASE,"paf_fibo_direction_gap_reason":"NEW_REASON"},"INVALID_DATA")]
for row,expected in cases:
    actual,_=classify(row); assert actual==expected,(actual,expected)
print("PASS: 6 verifier fixtures")
