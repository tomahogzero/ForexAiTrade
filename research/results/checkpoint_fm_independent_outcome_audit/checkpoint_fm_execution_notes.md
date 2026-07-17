# Checkpoint FM Execution Notes

The independent auditor reads FJ events, FK contract, FL canonical rows, the approved gap policy, and the three approved external GOLD# H1 CSV sources. It independently traverses post-confirmation bars and compares every FL event/horizon row.

The FL canonical CSV has CRLF in this Windows checkout, while the recorded FL hash represents its generated LF serialization. The auditor verifies the LF-normalized bytes against the frozen manifest hash; it does not rewrite the FL artifact.

Result: `FM_PASS_INDEPENDENT_OUTCOME_AUDIT`, material mismatch count `0`, byte-identical replay, broker-history completeness `NOT_PROVEN`.