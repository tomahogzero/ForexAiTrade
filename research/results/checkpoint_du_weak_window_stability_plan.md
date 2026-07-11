# Checkpoint DU Weak-Window Stability Review Plan

Date: 2026-07-11

Checkpoint DU is documentation-only. It defines how to review weak-window stability without running MT5, changing thresholds to force a pass, or interpreting diagnostic coverage as profitability.

The frozen weak-window criterion remains fewer than 5 Fibo usable first-touch rows. Known weak windows are DR-W1 (3), CY-W3 (2), DB-W1 (2), and DI-W3 (4). CY-W3 and DB-W1 remain a consecutive weak pair.

Across the four weak windows there are 27 Fibo rows, 11 usable rows, and 16 direction gaps. They represent 5.0% of combined Fibo usable rows, while their internal gap share is 59.3%.

Future Checkpoint DV should create an artifact-only chronological map for all 20 windows. Future Checkpoint DW may then decide whether to keep the absolute historical gate or propose a separately approved dual historical/trailing stability specification. Neither checkpoint may change thresholds to manufacture a pass or approve trading/order logic.

PAF remains `NOT_READY_FOR_ORDER_LOGIC`.
