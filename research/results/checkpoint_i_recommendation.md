# Checkpoint I Recommendation

Classification: `KEEP_BASELINE_RESEARCH_MORE`

No live/demo setting change is approved. No final candidate is approved.

## Rationale

- Session `Asia` has small validation/OOS sample (23/9); avoid filter decisions.
- Session `London` has small validation/OOS sample (27/26); avoid filter decisions.
- Session `London/New York overlap` has small validation/OOS sample (26/13); avoid filter decisions.
- Session `New York` has small validation/OOS sample (24/13); avoid filter decisions.
- Session `Other/Unknown` has small validation/OOS sample (5/1); avoid filter decisions.
- Direction `buy` has small validation/OOS sample (59/18); avoid filter decisions.
- Regime `breakout` has small validation/OOS sample (22/14); avoid filter decisions.
- Spread bucket `21-25` has small validation/OOS sample (3/5); avoid filter decisions.

## Guardrails

- No optimization was performed.
- No strategy entry logic was changed.
- No exit behavior was changed.
- No new strategy branch was added.
- Demo forward testing remains blocked.
