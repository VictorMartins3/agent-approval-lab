# Who approves an agent's dependency update?

A small, reproducible comparison of **review evidence** and **approval authority**.

## Follow-up: explanation accuracy

The second experiment adds a structured review contract and compares the existing report with extra source-linked observations. It includes direct and computed credential-read calls as positive controls, alongside the original inert indicators and legitimate changes.

- [Interactive evidence comparison](evidence.html)
- [Results](EVIDENCE_RESULTS.md), [analysis](EVIDENCE_FINDINGS.md), and [protocol](EVIDENCE_PROTOCOL.md)
- `evidence_report.py`: source-linked literal-pattern hints and explicit coverage limits.
- `review_contract.py`: checks exact citation locations and repairs edge whitespace only.
- `check_review.py`: validates a structured review against a supplied source map, without running source code.

Try the mechanical checker (no LLM or network needed):

```sh
python3 check_review.py --review examples/evidence-review/review.json \
  --sources examples/evidence-review/sources.json
```

Exit 0 means mechanical checks pass, 1 means a citation or unsupported-runtime assertion failed, and 2 means invalid input. `bad-review.json` in the same folder deliberately cites the wrong line and exits 1. The examples are authored test inputs, not model results.

**A matching quotation does not prove that it supports the claim.** The checker deliberately returns `semantic_claims_verified: false`. Semantic support is scored separately against a hand-authored oracle only in the bounded experiment. General source analysis needs a stronger verifier.

Reproduce the comparison with `python3 evidence_eval.py run --repeats 3 --jobs 3`; rebuild and verify results with `python3 evidence_eval.py report`, `python3 verify_evidence_results.py`, and `python3 build_evidence_page.py`.

## Original approval experiment

An agent receives the same dependency-update task under three CI configurations:

1. **Tests only:** run the application's formatting assertions.
2. **Editable approval:** show capsurface's report against the original baseline, but enforce the baseline the agent can approve.
3. **Protected approval:** show the same report and enforce the original baseline outside the agent's tools. The agent can request independent review, but cannot grant it.

The second and third conditions deliberately separate seeing a warning from having authority to dismiss it. The protected condition is a policy implemented by this harness, **not a new capsurface feature or an OS sandbox**.

## Read the evidence

- [Observed agent runs](RESULTS.md)
- [Offline interactive report](index.html)
- [Machine-readable agent outcomes](results/summary.json)
- [Scripted controls](results/controls.json)
- [Actual capsurface Action reproduction](results/action-control.json)
- [Method and limitations](PROTOCOL.md)

All inputs are synthetic. There is no claim of discovering a vulnerability in Anthropic, Claude Code, Mendral, or a real npm package. No dependency is downloaded and no lifecycle script is executed. The suspicious fixture is inert: it contains module imports and a credential-shaped path, but no credential read, network request, or child-process call.

## Run locally

Requirements: Python 3.10+, Node 18+, Git. Real agent runs additionally require the Claude CLI and an authenticated account. They use the account's existing default model and consume its usage allowance; resolved model IDs are saved in each `claude.json`.

```sh
npm test                         # validate the harness and approval boundary
npm run demo                     # nine deterministic controls, no LLM needed
python3 action_control.py        # invoke the actual capsurface Action helper
python3 lab.py run --repeats 3 --jobs 3  # 27 independent Claude sessions
npm run report                   # regenerate the agent result table
python3 build_page.py             # regenerate the offline HTML report
npm run verify:results           # reconcile all logs and independently rerun final CI
```

There are no pip or npm packages to install. The capsurface scanner is vendored from commit `93b7ba9f19431f2800ecb3a737fa1ff2a5b751b3`; see [revision](vendor/REVISION) and its [MIT license](vendor/capsurface/LICENSE). The user's working checkout was not modified. The experiment uses the basic scanner, not optional AST analysis.

## What the agent can do

The Claude CLI receives six local MCP tools: inspect the project, apply the supplied update, run CI, record approval, request review, and submit a decision. Application tests and capsurface run as real Node processes. Approval invokes the actual `capsurface approve` command. Tools return the actual scanner's structured evidence.

The agent has no shell, general file editor, external MCP tools, or web access in this experiment. It can choose actions and reasons, but cannot alter fixtures, tests, the harness, or the protected baseline. This is a bounded dependency-maintenance agent, not a benchmark of unrestricted coding agents. A JSON submission is independently checked against actual final CI and update state.

The first 27-run pilot is retained separately. The primary batch uses corrected opaque trial paths, an explicit approval-no-op result, and a routine fixture that retains the original String coercion. See the protocol history before comparing the batches.

## The useful distinction

The original baseline can remain visible in a report while the effective CI check accepts a proposed approval. The [Action control](action_control.py) demonstrates this using capsurface's actual `action-review.js`, not just an emulation. This is documented behavior: the caller must establish who can approve baseline changes through repository permissions and review.

Moving approval outside the agent's authority prevents self-approval in this harness. It also creates a handoff for legitimate new capabilities. Whether this tradeoff is useful depends on the deployment's risk and review policy.

## Transport

The small stdio MCP server follows the official [MCP transport](https://modelcontextprotocol.io/specification/2025-03-26/basic/transports) and [tool](https://modelcontextprotocol.io/specification/2025-03-26/server/tools) specifications. It only serves this local experiment.
