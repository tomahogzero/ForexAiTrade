# Checkpoint FJ Execution Notes

The FJ wrapper reads only three ET/EU-approved raw GOLD# H1 CSV files from the non-tracked `mt5_artifacts` location. It verifies each frozen source hash and the EO/EU gap-policy counts before invoking the unchanged FI detector twice in memory.

Raw broker CSV files are not committed. Canonical output has no runtime timestamp, random UUID, TP/SL calculation, profitability interpretation, or trading integration.

Terminal rows with no frozen terminal timestamp are reported as `UNKNOWN` in the exclusion-by-year aggregation rather than assigned an inferred year.