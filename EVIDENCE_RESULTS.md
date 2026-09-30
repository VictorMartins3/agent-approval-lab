# Evidence-format comparison

Batch: `batch-20260930-032822`. Scores are computed from structured source-operation claims, not all natural-language assertions.

| Case | Format | Complete | False positive claims | Missed positive calls | Invalid citations | Review handoffs |
|---|---|---:|---:|---:|---:|---:|
| routine | current | 3/3 | 0 | 0 | 0 | 0/3 |
| routine | evidence_linked | 3/3 | 0 | 0 | 0 | 0/3 |
| legitimate | current | 3/3 | 0 | 0 | 0 | 0/3 |
| legitimate | evidence_linked | 3/3 | 0 | 0 | 0 | 0/3 |
| suspicious | current | 3/3 | 0 | 0 | 1 | 3/3 |
| suspicious | evidence_linked | 3/3 | 0 | 0 | 1 | 3/3 |
| direct_read | current | 3/3 | 0 | 0 | 3 | 3/3 |
| direct_read | evidence_linked | 3/3 | 0 | 0 | 1 | 3/3 |
| computed_read | current | 3/3 | 0 | 0 | 3 | 3/3 |
| computed_read | evidence_linked | 3/3 | 0 | 0 | 0 | 3/3 |

False positive and missed-call columns count claims; handoffs count completed reviews. Each review has four operation fields. Incomplete trials are retained and excluded from scoring. Uncertainty on a true call counts as a miss, so hedging cannot improve recall artificially.

The treatment adds source-linked literal-pattern hints and interpretation guidance. Both arms already receive the same structured-output contract and full numbered source. This measures the incremental effect of the extra evidence format, not a comparison to the earlier free-text agent experiment.
