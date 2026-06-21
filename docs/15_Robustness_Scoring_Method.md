# Robustness Scoring Method

## Principles

Scoring is survival-first. A strategy that survives with moderate profit is preferred over one with high historical profit and fragile risk behavior.

## Execution vs Performance

Hard infrastructure failures do not receive a performance score.

Examples:

- `TIMEOUT`
- `NO_REPORT`
- `PARSE_ERROR`
- `CONFIG_MISMATCH`
- `PROCESS_ERROR`

These are runner or environment outcomes, not trading outcomes.

## Research Classifications

- `VALID_RESULT`
- `INSUFFICIENT_TRADES`
- `NO_TRADES`
- `NO_RISK_BUDGET`
- `RISK_GATE_FAILED`
- `VALIDATION_FAILED`
- `OOS_FAILED`
- `RESEARCH_CANDIDATE`

Gold cases blocked only because broker minimum lot exceeds the configured risk budget are classified as:

```text
NO_RISK_BUDGET
```

They are not automatically strategy failures.

## Minimum Gates

Candidate gates:

- drawdown <= 20%
- positive validation net result
- positive out-of-sample net result
- adequate trade count
- no abnormal dependence on one trade
- acceptable consecutive losses

Train profit alone does not approve a candidate.

## Tools

Parser:

```powershell
python tools\research_report_parser.py --report report.html --case case.json --output parsed_result.json
```

Scoring:

```powershell
python tools\research_score.py --runs-root research\runs --output research\results\all_scores.csv
```

Summary:

```powershell
python tools\generate_research_summary.py --runs-root research\runs --results-root research\results
```

## Warning

Backtest scores are research filters only. They are not proof of future profitability.
