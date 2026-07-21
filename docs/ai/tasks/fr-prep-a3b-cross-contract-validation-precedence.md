# FR-Prep-A3b Cross-Contract Validation Precedence

The stable code registry is [dataset_execution_descriptor_validation_codes.v1.json](../../../research/schemas/dataset_execution_descriptor_validation_codes.v1.json).

The frozen order is:

1. Descriptor root and schema version.
2. Required descriptor fields.
3. Validated synthetic source contract.
4. Validated synthetic gap-policy contract.
5. Dataset, role, symbol, and timeframe binding.
6. Source boundary binding.
7. Source and timeline identities/hashes.
8. Canonical timeline metadata.
9. Gap dataset binding.
10. Gap timestamp containment, then previous timestamp resolution, then next timestamp resolution.
11. Gap count reconciliation: total, accepted, unverified, then declared disposition total.
12. Classification allowlist identity.
13. Broker-history completeness.
14. Detector, outcome, and interpretation contract versions.
15. Execution mode, then detector permission, then outcome permission.
16. Requested forbidden actions: detector, event/ATR-event, TP/SL/outcome, then FN interpretation.

The validation root is synthetic and adapter-only. Runtime paths, exception strings, timestamps, temporary paths, detector state, and execution output are excluded from canonical failure output.
