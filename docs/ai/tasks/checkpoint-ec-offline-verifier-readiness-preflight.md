# Checkpoint EC Offline Verifier Readiness Preflight

Date: 2026-07-11

Decision: `BLOCKED_ROW_LEVEL_DZ_ARTIFACT_NOT_COMMITTED`

Committed DZ summary artifacts contain aggregate and per-window evidence but no row-level records for the 2,353 Fibo rows required by `PAF_FIBO_USABLE_DIRECTION_V1`.

- verifier implementation: `NOT_APPROVED`
- validation: `NOT_RUN`
- order logic: `FAIL_NOT_APPROVED`
- PAF: `NOT_READY_FOR_ORDER_LOGIC`

Next: Checkpoint ED docs-only row-level artifact contract. Do not reconstruct rows from aggregates or treat fixture-only tests as real validation.
