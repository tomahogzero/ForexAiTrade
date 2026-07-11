# Checkpoint DU Weak-Window Stability Plan

Date: 2026-07-11

## Scope

Documentation-only plan for reviewing repeated/consecutive weak Fibo windows after Checkpoint DS.

## Frozen Classification

- weak: Fibo usable first-touch rows `< 5`
- watch: `5-6`
- normal for stability review: `>= 7`

These are diagnostic labels, not trading parameters.

## Current Weak Windows

- DR-W1: 3 usable
- CY-W3: 2 usable
- DB-W1: 2 usable
- DI-W3: 4 usable
- consecutive pair: CY-W3 -> DB-W1

Weak windows total 27 Fibo rows, 11 usable rows, and 16 gaps. They represent 5.0% of combined Fibo usable rows and have 59.3% internal gap share.

## Next Steps

- DV: artifact-only chronological stability map for all 20 windows
- DW: docs-only decision on whether to keep the absolute gate or propose a separately approved historical/trailing specification

No MT5, Strategy Tester, optimization, EA/preset changes, order logic, demo/live test, or profitability claim.
