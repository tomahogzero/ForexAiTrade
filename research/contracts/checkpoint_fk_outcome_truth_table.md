# Checkpoint FK Outcome Classification Truth Table

| Condition within complete horizon | Outcome |
|---|---|
| Earlier valid bar touches TP only before any SL touch | `TP_FIRST` |
| Earlier valid bar touches SL only before any TP touch | `SL_FIRST` |
| First resolving valid bar touches both TP and SL | `AMBIGUOUS_SAME_BAR` |
| Complete horizon ends without either touch | `NO_RESOLUTION` |
| No earlier resolution and unverified gap enters required remaining sequence | `DATA_INCOMPLETE_GAP` |
| No earlier resolution and source ends before full horizon | `INSUFFICIENT_FUTURE_BARS` |
| Frozen event field/schema/finite value check fails | `INVALID_EVENT_INPUT` |

No outcome is calculated by FK.

## Gap Before/After Outcome

| Sequence | Frozen decision |
|---|---|
| TP/SL/ambiguous resolves before an unverified gap | Preserve the resolved outcome |
| No resolution before an unverified gap within remaining horizon | `DATA_INCOMPLETE_GAP` |
| Accepted daily/weekend closure | Do not consume a bar; continue at next valid bar |
| Source ends before complete horizon with no resolution | `INSUFFICIENT_FUTURE_BARS` |