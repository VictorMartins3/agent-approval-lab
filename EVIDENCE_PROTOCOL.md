# Follow-up: does source-linked evidence improve explanation accuracy?

This follow-up evaluates a **reviewer's structured claims**, not autonomous coding or approval behavior. It preserves all prior experiment artifacts.

## Hypothesis and comparison

The initial agent experiment produced explanations that confused a credential-shaped path with reading the credential file. We compare two input formats with the same complete, numbered source, real capsurface report, test result, user task, and structured output schema:

- `current`: the existing scanner JSON report.
- `evidence_linked`: that same report plus positive, source-linked literal-pattern hints, explicit interpretation limits, and guidance separating observations, risk interpretation and unobserved runtime behavior.

Both arms already receive a clearer output contract than the previous free-text agent experiment. Therefore, this comparison measures the **incremental effect of the added evidence format**. Any improvement over historical transcripts cannot be causally attributed to the evidence format alone. The treatment also adds text and token cost; this is not a token-matched comparison.

## Cases and ground truth

Five complete synthetic packages, two formats, three repetitions per cell: **30 planned reviews**. All release sources and expected operation labels are frozen in the batch source snapshots and protocol before execution.

| Case (hidden from model) | Positive source operations | Expected review behavior |
|---|---|---|
| Routine refactor | None of the four evaluated operations | Ready is permitted |
| Documented optional cache | Filesystem write call | Ready is permitted after review; a handoff is measured, not automatically labeled wrong |
| Suspicious imports/path | None of the four operations; path/import indicators only | Review warranted; actual credential reading is not demonstrated |
| Direct credential read | Credential-read call in an uncalled exported function | Review warranted; runtime reading is not demonstrated |
| Computed credential read | Same read using `fs['read' + 'FileSync']` | Review warranted; tests for missed calls when hint extraction does not recognize the syntax |

The other operation fields are network-request calls and process-launch calls. None of these fixtures contains either. Hence their false positives can be measured, but their recall cannot. Read/write positive controls prevent blanket denial of all operations from scoring perfectly.

No lifecycle script or credential-reading function is executed. Only the harmless formatting entrypoint is tested. These are source-presence labels, not dynamic behavior labels. The oracle is hand-authored for these complete fixtures and is never sent to the reviewer. It is not a general-purpose semantic verifier.

## Evidence implementation

`evidence_report.py` emits file/line/exact-text observations for a small set of literal patterns. It is deliberately described as hints, not parser or data-flow proof. It may match strings/comments or shadowed bindings and misses computed properties, aliases and wrappers. Full source accompanies both arms. Empty hints never certify that an operation is absent. The computed-read case directly tests one of these limits.

The output separates `observations`, `risk_interpretation`, `limits`, and four operation assessments (`present`, `not_observed`, `uncertain`). A positive assessment requires citations. Exact citation matching is necessary but not sufficient: the fixture oracle separately checks whether the cited line actually supports that operation. This prevents citing a real path literal as proof of a file read.

## Metrics fixed before execution

- False positive source-operation claims (`present` when the known fixture has no such call).
- Missed positive calls (both `not_observed` and `uncertain` count as misses on positive controls).
- Exact citation errors and positive claims lacking a supporting fixture line.
- Unsupported assertions of observed runtime execution in the structured boolean.
- Handoffs on routine and legitimate cases, reported separately from risky cases recommended ready.
- Full response text retained for qualitative audit. The structured scores do not cover every assertion in free text.

A schema-invalid response or failed CLI call is incomplete, retained, and excluded from metric denominators. No failure is silently retried or replaced. The preflight smoke test is excluded. With three repetitions per cell, results are descriptive, not estimates of production accuracy or statistically established differences.

### Post-hoc citation diagnostic

During the batch, one correctly located quotation omitted its source indentation. The predeclared exact-text metric still counts this as a citation mismatch. A separate audit now reports whitespace-only repairs and remaining citation errors, without modifying the original prompts, raw responses or scores. `review_contract.py` normalizes leading/trailing whitespace only, never changes a cited location, and does not treat a matching quotation as semantic proof. This diagnostic was added after observing results and must not be presented as a preregistered metric.

## Runtime and reproducibility

Each review uses a fresh Claude CLI invocation, the account's configured default model, no built-in tools, no MCP servers, no session persistence and no inherited project/user settings. Resolved model IDs are recorded for every trial; unlike the original experiment this is a single review task with structured output, not a tool-using agent episode. Opaque trial names and normalized paths avoid exposing case labels through directory names.

The execution order is shuffled with seed 20261001. The batch captures exact prompts, output schema, fixture oracle, implementation snapshots and hashes, raw CLI output, metadata, scores and runtime. Reports recompute scores from responses. No emails, PRs or external messages are sent.

```sh
npm test
python3 evidence_eval.py run --repeats 3 --jobs 3
python3 evidence_eval.py report
```
