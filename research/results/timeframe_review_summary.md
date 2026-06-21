# EURUSD Timeframe Review Summary

This review compares M30/H1/H4 using existing strategy logic and existing conservative settings. It is not optimization.

| Case | TF | Train Profit | Validation Profit | OOS Profit | Validation Trades | OOS Trades | Status |
|---|---|---:|---:|---:|---:|---:|---|
| EURUSD_H1_10000 | H1 | -40.96 | 61.38 | 41.03 | 105 | 62 | RESEARCH_MORE |
| EURUSD_H4_10000 | H4 | -37.3 | -23.15 | -5.74 | 6 | 27 | REJECT_FOR_NOW |
| EURUSD_M30_10000 | M30 | -7.14 | -20.45 | 56.51 | 5 | 71 | REJECT_FOR_NOW |

## Questions

### Does EURUSD H1 remain the best baseline?

Yes, for now H1 remains the baseline for further research because validation and out-of-sample are both positive while M30 and H4 fail one or more review checks. H1 is still `RESEARCH_MORE`, not an approved or live-ready candidate.

### Does M30 increase trade count without destroying risk?

No. M30 validation/OOS trades are 5/71; validation is negative and has too few trades. Review status: `REJECT_FOR_NOW`.

### Does H4 trade too little?

Yes. H4 validation/OOS trades are 6/27, with validation and out-of-sample both negative. Low-trade H4 phases should be rejected for candidate selection.

### Which timeframe should be used as baseline?

Use EURUSD H1 as the next baseline for diagnostics-only research. H1 status: `RESEARCH_MORE`.

### Should low-trade phases be rejected?

Yes for candidate selection. They may remain for diagnostics, but should not drive strategy changes or optimization.
