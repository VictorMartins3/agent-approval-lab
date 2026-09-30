# Follow-up result: keep the structured review contract

**The added evidence hints did not improve source-operation classification in this batch. Both formats classified every evaluated operation correctly when given the same explicit structured review contract.**

The practical implementation is a review format separating observations, risk interpretation and limits, with source citations checked mechanically. Keep the additional literal-pattern hints experimental; these results do not justify treating them as a required layer.

## What was run

30 completed reviews: five synthetic updates × two report formats × three repetitions. All returned model IDs were `claude-sonnet-5`. No incomplete trials or retries. Each response contained four source-operation assessments, yielding 120 assessed fields across both arms.

Both arms received the complete numbered source, actual capsurface JSON report, formatting-test result, a policy permitting documented opt-in changes after inspection, and the same output schema. The treatment additionally received source-linked literal-pattern hints and interpretation guidance. This is a reviewer experiment, not an autonomous coding/approval episode.

| Metric | Existing report + structured contract | Same contract + added evidence hints |
|---|---:|---:|
| Completed reviews | 15/15 | 15/15 |
| False positive operation claims | 0/51 absent-operation fields | 0/51 |
| Missed positive calls | 0/9 present-operation fields | 0/9 |
| Structured runtime overclaims | 0/15 | 0/15 |
| Routine/legitimate changes sent to review | 0/6 | 0/6 |
| Suspicious/read cases sent to review | 9/9 | 9/9 |
| Strict quotation mismatches | 7 | 2 |
| Mismatches remaining after whitespace normalization | 0 | 0 |

All nine quotation mismatches omitted indentation. Their file and line locations and substantive text were correct. The original strict scores remain unchanged; whitespace normalization is labeled as a post-hoc diagnostic. These are not nine invented citations, and the 7-versus-2 difference is not evidence of better semantic accuracy.

[Detailed table](EVIDENCE_RESULTS.md) · [interactive report](evidence.html) · [raw batch](evidence-results/batch-20260930-032822/summary.json) · [independent recomputation](evidence-results/batch-20260930-032822/verification.json)

## What to use

1. **Explicit operation claims.** Separate a path reference, a source call, and evidence that a call actually executed. A caller-provided filesystem write is also distinct from credential access.
2. **Separate fields for observations, risk interpretation and limits.** A reviewer can request investigation without asserting that credentials were stolen.
3. **Mechanical citation validation.** Require citations for positive operation claims, verify the named file and line against supplied source, normalize edge whitespace, and reject changed words or locations.
4. **Keep semantic review separate.** A real quotation can still be used to support the wrong conclusion. The general checker returns `semantic_claims_verified: false`; only this bounded fixture evaluation has a hand-authored oracle for semantic support.

The usable checker is [check_review.py](check_review.py), backed by [review_contract.py](review_contract.py). It rejects unsupported runtime assertions because this input contract contains no runtime trace. It never executes the source map. The [example](examples/evidence-review/review.json) and [deliberately bad example](examples/evidence-review/bad-review.json) demonstrate its pass/fail behavior without an LLM.

## What we can and cannot conclude

The original agent experiment escalated legitimate changes and sometimes overstated evidence. This follow-up produced more precise structured classifications and no routine/legitimate handoffs. **That historical difference is not a controlled estimate of improvement:** the task, role, output contract and review policy also changed. The controlled comparison here supports the narrower finding that extra literal-pattern hints supplied no additional classification gain over the clearer contract on these fixtures.

There are only three repetitions per cell and one model configuration. The fixtures are short. Source-call ground truth is manually specified, and the measured fields do not cover every sentence in free-form prose. Network and process calls have negative controls only, so their positive recall was not tested. Generalization to larger repositories, adversarial syntax or production agents is unproven.

The computed-read control is useful: the literal-pattern hints miss it, but the reviewer still identifies the read from the full source. This supports retaining complete source and explicit coverage limits instead of treating the hints as a complete operation inventory.

## Validation

- 20 automated tests pass, covering both the original approval harness and new evidence checks.
- All 30 primary responses were validated and rescored independently from saved artifacts.
- Batch source snapshots and hashes, source equality between arms, model IDs and permission-denial logs were checked.
- Wrong-line citations and unsupported runtime assertions are rejected; whitespace-only differences are repaired without changing the source location.
- Prior approval experiments and the capsurface checkout were preserved.
