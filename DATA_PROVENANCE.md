# Data provenance and public export

The public repository includes the complete outcome-bearing records from:

- 27 initial pilot agent episodes, retained under `results/pilot-*` and excluded from primary metrics.
- 27 revised primary agent episodes under `results/batch-*`.
- 30 structured reviewer trials under `evidence-results/batch-*`.

These experiments use synthetic dependency releases. No private repository source, customer data, credential contents, or real malicious package is included.

## Export transformations

Local absolute workspace paths are replaced with `/research/agent-approval-lab`; user-home prefixes are replaced with `/research/user`. Public path normalization changes neither model decisions nor fixture source. Historical MCP launch configurations retain their role as records; they are not portable launch commands. Run the top-level scripts to reproduce a new batch.

The `claude.json` files retain outcome-bearing fields: model result and structured output, model IDs and token counters, error status, permission denials, turn count, stop reason and duration. Session identifiers, request UUIDs and unrelated transport/telemetry fields are omitted. Cost fields are also omitted. Published files are **redacted exports**, not byte-for-byte raw transport logs.

Prompt text, operation classifications, citation text, decisions, tool calls and their results are retained. The experiment source snapshots and recorded snapshot hashes are preserved. The full local originals remain outside this publication.

Preflight smoke runs, scratch work, account configuration, local browser state, outreach drafts and Python caches are excluded. No model is queried by CI. CI recomputes the saved scores and the final primary agent CI states using the pinned scanner and fixture files.

## Reproduction versus exact replication

The scanner is vendored at the SHA in `vendor/REVISION`, with its original MIT license. The experiment snapshots record the evaluation code used at execution time. Recomputing saved outcomes is deterministic for the included fixtures. Rerunning the model is not expected to reproduce identical wording or decisions: the original runs used the configured CLI default, and resolved model IDs are recorded per trial.

The first pilot and later reviewer experiment have different protocols. Their results should not be pooled to claim an intervention effect. See `PROTOCOL.md` and `EVIDENCE_PROTOCOL.md` for the changes and limitations.
