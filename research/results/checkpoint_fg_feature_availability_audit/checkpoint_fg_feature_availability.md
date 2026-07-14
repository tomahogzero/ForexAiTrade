# Checkpoint FG Feature Availability Audit

{
  "execution_status": "PASS",
  "decision": "FG_PASS_FEATURES_AVAILABLE",
  "raw_schema_rows_checked": 5894,
  "h1_gaps_detected": 256,
  "feature_inventory": [
    [
      "H1 timestamp",
      "<DATE>+<TIME>",
      "AVAILABLE",
      "DETERMINISTIC",
      "none",
      "exclude gap/incomplete sequence"
    ],
    [
      "open/high/low/close",
      "<OPEN>/<HIGH>/<LOW>/<CLOSE>",
      "AVAILABLE",
      "DETERMINISTIC",
      "none",
      "exclude invalid row"
    ],
    [
      "confirmed swing high",
      "2-left/2-right high derivation",
      "AVAILABLE",
      "DETERMINISTIC",
      "right-side leak if early",
      "usable only after center+2 close"
    ],
    [
      "confirmed swing low",
      "2-left/2-right low derivation",
      "AVAILABLE",
      "DETERMINISTIC",
      "right-side leak if early",
      "usable only after center+2 close"
    ],
    [
      "swing knowable time",
      "center index + 2 completed bars",
      "AVAILABLE",
      "DETERMINISTIC",
      "premature use",
      "no use before right-side bars close"
    ],
    [
      "most recent confirmed swing",
      "ordered confirmed-swing state",
      "AVAILABLE",
      "DETERMINISTIC",
      "future-swing selection",
      "state contains confirmed swings only"
    ],
    [
      "bullish close break",
      "close > confirmed swing high",
      "AVAILABLE",
      "DETERMINISTIC",
      "wick/future leak",
      "reject wick-only and unconfirmed level"
    ],
    [
      "bearish close break",
      "close < confirmed swing low",
      "AVAILABLE",
      "DETERMINISTIC",
      "wick/future leak",
      "reject wick-only and unconfirmed level"
    ],
    [
      "12-trading-bar retest window",
      "sequential bar index delta",
      "AVAILABLE",
      "DETERMINISTIC",
      "none",
      "exclude retest after bar 12"
    ],
    [
      "exact swing-level retest",
      "OHLC touch of stored broken level",
      "AVAILABLE",
      "DETERMINISTIC",
      "level substitution",
      "retain exact break level"
    ],
    [
      "bullish confirmation",
      "close > open and close > prior high",
      "AVAILABLE",
      "DETERMINISTIC",
      "prior-bar ordering",
      "reject failed condition"
    ],
    [
      "bearish confirmation",
      "close < open and close < prior low",
      "AVAILABLE",
      "DETERMINISTIC",
      "prior-bar ordering",
      "reject failed condition"
    ],
    [
      "diagnostic entry reference",
      "confirmation close",
      "AVAILABLE",
      "DETERMINISTIC",
      "none",
      "diagnostic only; never order instruction"
    ],
    [
      "ATR availability",
      "approved offline_atr_14 completed bars",
      "AVAILABLE",
      "DETERMINISTIC",
      "future ATR leak",
      "prior completed 14 bars only"
    ],
    [
      "year and direction",
      "timestamp year and frozen rule direction",
      "AVAILABLE",
      "DETERMINISTIC",
      "none",
      "derive only from event-time state"
    ],
    [
      "gap/incomplete detection",
      "timestamp delta and row validation",
      "AVAILABLE",
      "DETERMINISTIC",
      "silent bridge",
      "DATA_INCOMPLETE_GAP exclusion"
    ],
    [
      "duplicate-candidate inputs",
      "break identifier, direction, confirmation time",
      "AVAILABLE",
      "DETERMINISTIC",
      "duplicate emission",
      "one event per break/direction"
    ],
    [
      "historical-bar sufficiency",
      "left-side and ATR count",
      "AVAILABLE",
      "DETERMINISTIC",
      "under-history",
      "exclude insufficient history"
    ],
    [
      "right-side-bar sufficiency",
      "two subsequent completed bars",
      "AVAILABLE",
      "DETERMINISTIC",
      "look-ahead",
      "exclude unconfirmed swing"
    ],
    [
      "deterministic event-key inputs",
      "run/source, bar time, direction, break id",
      "AVAILABLE",
      "DETERMINISTIC",
      "provenance loss",
      "exact provenance key"
    ]
  ],
  "fixture_tests": {
    "valid_long_sequence": true,
    "valid_short_sequence": true,
    "wick_only_false_break": true,
    "swing_not_yet_confirmed": true,
    "retest_after_12_bar_window": true,
    "confirmation_failure": true,
    "gap_inside_required_sequence": true,
    "duplicate_candidate_sequence": true
  },
  "blockers": [],
  "future_fh_scope": "FH may implement a deterministic event-generator prototype only, using exactly FF definitions and FG exclusions; no outcomes.",
  "strategy_performance_status": "NOT_EVALUATED",
  "order_logic_status": "NOT_APPROVED",
  "candidate_status": "NOT_READY_FOR_ORDER_LOGIC",
  "profitability_claim": false
}
