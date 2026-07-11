# Checkpoint DW Stability-Gate Decision

Date: 2026-07-11

DW selects `DATA_LIMITATION_BLOCKS_GATE_REVISION`.

The absolute historical gate remains `FAIL` because the CY-W3 to DB-W1 consecutive weak pair remains in the evidence set. Although the latest 6 windows contain no weak window and the latest 8 contain one isolated weak window, those horizons were inspected after outcomes were known and were not preregistered.

Selecting a favorable horizon now would risk post-hoc gate fitting. DI-W3 also lacks committed per-window gap-reason attribution. Therefore no dual historical/trailing gate is proposed or approved in DW.

Future Checkpoint DX should preregister the horizon, pass criteria, evidence requirement, and missing-data handling before any new evidence is collected. No MT5 execution is approved.

Rule-candidate and order-logic gates remain `FAIL`. PAF remains `NOT_READY_FOR_ORDER_LOGIC`.
