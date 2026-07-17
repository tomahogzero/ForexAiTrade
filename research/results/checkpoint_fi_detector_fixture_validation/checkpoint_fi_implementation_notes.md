# Checkpoint FI Implementation Notes

The FI detector is fixture-only. It accepts caller-provided bars in canonical `(timestamp, source_row_key)` order and does not enumerate filesystem datasets, connect to MT5, calculate TP/SL, or create orders.

Validation is deterministic: fixed JSON inputs, committed golden expected outputs, two replay runs, exact schema verification, and metadata/input-order ID invariance.

Future FJ scope is execution against an explicitly approved historical dataset for event coverage/exclusion/count reporting only. No outcomes are permitted.