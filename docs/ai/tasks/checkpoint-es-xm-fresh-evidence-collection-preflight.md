# Checkpoint ES XM Fresh Evidence Collection Preflight

Date: 2026-07-12

Decision: `ES_BLOCKED_UNOWNED_MT5_PROCESS_AND_NO_SAFE_EXPORT_INTERFACE`.

An XM MT5 terminal was already running before ES. Its PID was not started by ES and must not be killed, restarted, or automatically controlled. This environment has no desktop/MT5 UI automation and no existing non-UI exporter capable of producing the fresh per-gap EQ evidence bundle.

- fresh evidence collection: `NOT_RUN`
- ES-started terminal PIDs: `0`
- Strategy Tester: `NOT_RUN`
- policy/validator/joiner/shadow backtest: `UNCHANGED/NOT_RUN`
- strategy performance: `NOT_EVALUATED`

User direction is required: provide an offline evidence bundle, close the existing terminal and authorize an ES-owned instance with a controlled export path, or explicitly authorize attach/control of the existing PID with a usable UI/export interface.
