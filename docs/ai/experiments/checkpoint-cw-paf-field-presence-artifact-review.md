# Checkpoint CW Experiment Memory: PAF Field Presence Artifact Review

Date: 2026-07-09

## Input

Checkpoint CV run:

- RunId: `run_20260709_182444`
- Case: `GOLD_HASH_H1_PAF_FIELD_PRESENCE_CV_cv_field_presence_20260301_20260308`
- Symbol/timeframe: `GOLD#` H1
- Window: `2026-03-01` to `2026-03-08`

## Artifact Review Outcome

CV artifacts support the following:

- MT5 report artifact was found.
- Parsed report shows `total_trades=0`.
- PAF diagnostics were generated from `ea_mirror.log`.
- Checkpoint CT field presence is confirmed.
- Parser gap reason summaries are present.
- No forbidden trade actions were detected.
- No baseline fallback marker was detected.

## Interpretation

Direction unknown rows are now split into explainable buckets. The key remaining possible-setup issues are:

- Fibo Pullback: trend alignment conflict / price between EMAs
- Zone Rejection: wick too small

This is useful diagnostic evidence, but the sample is still too small to approve order logic.

## Status

`FIELD_PRESENCE_CONFIRMED`

`PAF_NOT_READY_FOR_ORDER_LOGIC`

## Next

Prepare Checkpoint CX approval package for multi-window field-presence and direction-gap stability validation.
