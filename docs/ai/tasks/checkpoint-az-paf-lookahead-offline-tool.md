# Checkpoint AZ: PAF Lookahead Offline Tool

Date: 2026-07-07

## Scope

Add an offline Python tool that joins existing PAF shadow outcome rows with a provided OHLC bar CSV.

No EA/source code changes.
No preset changes.
No MT5 run.
No Strategy Tester run.
No optimization.
No lot/risk increase.
No profitability claim.

## Tool

`tools/paf_lookahead_joiner.py`

Inputs:

- `research/results/paf_shadow_outcomes_all_cases.csv`
- external or future-generated `paf_lookahead_bars.csv`

Required bar columns:

- `time`
- `open`
- `high`
- `low`
- `close`

Outputs:

- `research/results/paf_shadow_outcomes_enriched.csv`
- `research/results/paf_lookahead_join_summary.json`
- `research/results/paf_lookahead_join_summary.md`

## Guardrails

The tool:

- does not run MT5
- does not send orders
- does not simulate live execution
- does not change EA behavior
- must not be imported into EA runtime
- must not be used to tune parameters after seeing results

## Future Data Rule

Lookahead data is allowed only after diagnostic events exist and only for offline research.

Lookahead data must never feed `CPriceActionFiboStrategy::Evaluate()` or any trading decision.

## Validation

Syntax check:

```powershell
python -m py_compile tools\paf_lookahead_joiner.py
```

No MT5 validation is performed in this checkpoint.

## Next Safe Step

Checkpoint BA should define how to safely produce or provide `paf_lookahead_bars.csv`, then run the joiner on a known artifact set.
