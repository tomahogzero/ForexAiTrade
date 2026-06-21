# ForexAiTrade Diagnostics Summary

Diagnostics are based on EA mirror logs and MT5 reports. They are not profitability proof.

## Case Diagnoses

| Case | Diagnosis |
|---|---|
| EURUSD_H1_10000 | EURUSD_H1_10000: RESEARCH_MORE. Validation and OOS are positive with acceptable trade counts, but train is weak (net=-40.96, trades=22). Net profits={'out_of_sample': 41.03, 'train': -40.96, 'validation': 61.38}, trades={'out_of_sample': 62, 'train': 22, 'validation': 105}; not a strong candidate. |
| EURUSD_H4_10000 | EURUSD_H4_10000: REJECT_FOR_NOW. Validation is negative (-23.15) and validation trades are 6. Net profits={'out_of_sample': -5.74, 'train': -37.3, 'validation': -23.15}, trades={'out_of_sample': 27, 'train': 17, 'validation': 6}; not a strong candidate. |
| EURUSD_M30_10000 | EURUSD_M30_10000: REJECT_FOR_NOW. Validation is negative (-20.45) and validation trades are 5. Net profits={'out_of_sample': 56.51, 'train': -7.14, 'validation': -20.45}, trades={'out_of_sample': 71, 'train': 21, 'validation': 5}; not a strong candidate. |

## Direct Answers

### Why does EURUSD H1 remain RESEARCH_MORE?

EURUSD H1 had negative train performance and only 22 train trades, while validation and out-of-sample were positive with acceptable trade counts. This is interesting enough for diagnostics, but it is not a strong candidate or forward/live-ready result.

### Why is EURUSD M30 rejected for now?

EURUSD M30 has positive out-of-sample, but validation is negative and validation trades are extremely low. Positive OOS alone is not enough for forward/live readiness.

### Why is EURUSD H4 rejected for now?

EURUSD H4 has negative validation and out-of-sample results, and validation/OOS trade counts are low. It should not drive strategy changes or optimization.

### What if GOLD# appears in this run?

GOLD# cases with broker minimum lot / risk-budget blocks should remain NEEDS_RISK_BUDGET_REVIEW. That condition is not automatically a strategy-entry failure, and the EA must not force minimum lot or increase risk automatically.

### Which symbol/timeframe deserves further research from this checkpoint?

EURUSD H1 deserves baseline tracking and further diagnostics only. M30 and H4 should be rejected for now.

### Which cases should be rejected for now?

EURUSD M30 and EURUSD H4 should be rejected for now. Low-trade phases should not be used to justify optimization or new strategy work.
