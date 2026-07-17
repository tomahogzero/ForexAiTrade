# Checkpoint FL Execution Notes

The evaluator consumes only the frozen FJ event CSV, FK contract JSON, approved 2023-2025 raw GOLD# H1 CSV sources, and frozen EO/EU gap policy. It uses Decimal arithmetic, starts after confirmation, counts valid bars only, and evaluates the four frozen horizons independently.

Canonical output contains diagnostic first-touch labels only. It has no runtime timestamp, random UUID, order, monetary P/L, spread, commission, swap, slippage, position-sizing, or execution model fields.

Raw broker CSV files are not committed. Broker-history completeness remains `NOT_PROVEN`.