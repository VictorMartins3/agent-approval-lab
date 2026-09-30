# Evidence and authority in dependency review agents

[Research note](https://victormartins3.github.io/agent-approval-lab/) · [Agent protocol](PROTOCOL.md) · [Reviewer protocol](EVIDENCE_PROTOCOL.md) · [Data provenance](DATA_PROVENANCE.md)

Two controlled experiments on dependency review: who can approve a change, and whether the source supports the agent's explanation.

## Findings

- In 27 primary agent episodes, the agent requested review for every suspicious update, including those without a capability scanner. It did not self-approve any update. These cases did not establish a behavioral advantage for protected approval.
- Scripted controls using capsurface's actual Action helper showed that a proposed approval can make CI pass while the original-baseline report retains its findings. A protected approval boundary prevents that transition in the harness.
- In 30 structured reviews, both formats correctly classified all 120 evaluated source-operation fields. Extra source hints did not improve classification. Routine and legitimate updates were recommended ready; suspicious and credential-read cases were referred for review.
- Nine exact-quotation mismatches were indentation differences. The checker repairs edge whitespace without changing the file, line, or words. A matching quotation is not proof of semantic support.

These are small synthetic experiments, not production-accuracy estimates. The second experiment changes the task and policy; its outcomes are not a causal before-and-after comparison with the first. The original pilot is retained separately and excluded from primary metrics.

## Verify the saved results

Requirements: Python 3.10+ and Node 18+. No dependency installation, API key, or model call is needed.

```sh
git clone https://github.com/VictorMartins3/agent-approval-lab.git
cd agent-approval-lab
npm test
python3 verify_results.py
python3 verify_evidence_results.py
python3 scripts/check_publication.py
```

CI uses Python 3.12 and Node 22. It runs the tests, recomputes saved outcomes, verifies record hashes and source snapshots, and checks site reproducibility. GitHub Actions are pinned to full commit SHAs with read-only repository access.

## Use the citation checker

```sh
python3 check_review.py \
  --review examples/evidence-review/review.json \
  --sources examples/evidence-review/sources.json
```

The source input maps display filenames to source text. No source code is executed. Exit 0 means mechanical checks passed; exit 1 means a citation or unsupported-runtime assertion failed; exit 2 means invalid input. The example `bad-review.json` deliberately cites the wrong line and exits 1.

The checker returns `semantic_claims_verified: false`. A real path literal can still be cited incorrectly as proof of a read. General semantic verification is outside the checker's scope; the evaluation uses a hand-authored oracle for its complete fixtures.

## Run a new model experiment

An authenticated Claude CLI is required. These commands consume the account's allowance. Resolved model IDs are recorded per trial; the saved primary runs reported `claude-sonnet-5`.

```sh
python3 lab.py run --repeats 3 --jobs 3
python3 evidence_eval.py run --repeats 3 --jobs 3
```

Each run creates a new batch. Follow [DATA_PROVENANCE.md](DATA_PROVENANCE.md) before publishing new records. Raw local reruns are not ready for public commit. See [CONTRIBUTING.md](CONTRIBUTING.md) for protocol and scoring changes.

## Repository map

| Path | Purpose |
|---|---|
| `lab.py` | Dependency-update environment and local MCP tools |
| `action_control.py` | Actual capsurface Action helper reproduction |
| `evidence_eval.py` | Reviewer experiment and fixture oracle |
| `review_contract.py`, `check_review.py` | Citation and runtime-claim checks |
| `evidence_report.py` | Experimental source-linked hints |
| `results/` | Redacted agent records, including the separate pilot |
| `evidence-results/` | Redacted structured-review records |
| `fixtures/` | Synthetic dependency sources |
| `vendor/capsurface/` | Pinned scanner and its original MIT license |
| `site/`, `scripts/build_site.py` | Research-note source and builder |
| `docs/` | Generated GitHub Pages site |

[Agent findings](FINDINGS.md) · [Agent table](RESULTS.md) · [Reviewer findings](EVIDENCE_FINDINGS.md) · [Reviewer table](EVIDENCE_RESULTS.md)

MIT. The vendored scanner retains its original MIT license. Author: Victor Martins.
