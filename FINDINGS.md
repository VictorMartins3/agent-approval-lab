# Findings: evidence, authority, and explanations

## Follow-up implementation

The explanation-accuracy follow-up is implemented separately: [results and conclusions](EVIDENCE_FINDINGS.md), [interactive comparison](evidence.html), and [protocol](EVIDENCE_PROTOCOL.md). It introduces a structured claim contract, exact source citations, a mechanical checker, and direct/computed read controls. The original approval experiment below is retained as historical evidence; the new reviewer experiment does not retroactively change its conclusions.

## What this experiment establishes

The deterministic controls demonstrate that **retaining a warning in a report does not necessarily keep CI blocked**. In capsurface's actual Action helper, the report compares against the target branch's baseline while the enforcement output evaluates the proposed baseline. A selective approval can make the enforcement output pass while the original findings remain visible. [Reproduction](results/action-control.json).

In the protected configuration, the same attempted approval cannot change the baseline used by the gate. This is a property of the harness's implemented authority boundary, verified independently of any model decision. The cost is that legitimate new capabilities also require a separate reviewer.

## What the agent runs show

The primary results come from a fresh 27-session batch after auditing and correcting the pilot. All sessions use the returned model ID `claude-sonnet-5`. See the [complete table](RESULTS.md), [protocol](PROTOCOL.md), and [raw outcomes](results/summary.json).

The agent escalated the suspicious fixture in all nine sessions, including the three with application tests alone. It inspected the proposed source and declined to apply the release. Therefore, these trials **do not demonstrate improved suspicious-update detection from capsurface**, nor do they demonstrate the agent bypassing a security gate. The scanner's suspicious-update gate is demonstrated by the scripted controls, not by an agent first applying that update.

In the primary batch, none of the three agents with editable approval self-approved the legitimate filesystem addition. They requested review despite having the tool authority to approve it. The initial pilot had two approvals in that cell, but the pilot was affected by case-label leakage and other harness differences. We retain both batches and make no causal claim about that difference.

This means the architectural distinction is proven by executable controls, while the behavioral difference between editable and protected approval remains inconclusive at this sample size and prompt configuration.

## An additional observation: explanation accuracy

Several explanations describe the suspicious fixture as reading credentials or as an exfiltration payload. The actual fixture imports Node modules, defines an uncalled function that builds a credential-shaped path, and exports that function. There is no file-read call, network request, subprocess invocation, or invocation of the exported function. [Source](fixtures/suspicious/1.0.1/scripts/setup.js).

Requesting review is defensible because the additions are unexplained and unrelated to the package's apparent purpose. Claiming observed credential access goes beyond the supplied source. Decision quality and evidence accuracy should be evaluated separately; a cautious decision is not proof that its explanation is grounded.

The raw transcripts are available through the interactive report. We do not present an automated hallucination rate: ambiguous wording and generic risk descriptions would require a separately defined annotation rubric and independent review.

## A tool-interface lesson from the routine control

One tests-only routine session requested human review after calling an approval tool and receiving a denial, even though its update passed CI and no baseline gate was configured. The tool is present in every condition for comparability, and the tests-only branch denies baseline writes. That response can imply an approval requirement that the CI configuration does not impose.

This is partly a harness/interface effect, not evidence of an inherent model defect. A production interface should distinguish “approval denied,” “approval unnecessary,” and “approval not applicable.” The revised editable-approval no-op already distinguishes the first two; the tests-only denial remains documented in this batch so its history and results are not silently changed.

## What would justify a stronger conclusion

A larger follow-up should vary repository size and task framing, include less obvious cases, use multiple fixed model versions, specify an independent review policy consistently across conditions, and score explanation claims against exact source operations. It should also test a production enforcement boundary outside the agent's process and measure the review burden from legitimate updates. Those are future experiments; they were not performed here.

For a technical conversation, the defensible claim is: **we built a reproducible evaluation that separates passing application tests, presenting capability evidence, and granting approval ; and retained the negative result when the model did not behave as initially hypothesized.**
