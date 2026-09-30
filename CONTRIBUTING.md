# Contributing

Use Python 3.10+ and Node 18+. There are no required third-party Python or npm dependencies.

```sh
npm test
python3 verify_results.py
python3 verify_evidence_results.py
python3 scripts/check_publication.py
python3 scripts/build_site.py
```

Keep historical prompts, responses and scores unchanged. New experiments belong in new timestamped batches, with a protocol and source snapshot captured before model execution. Retain failed and incomplete trials. Distinguish model outcomes from scripted controls and quote matching from semantic support.

Changes to claim scoring need tests for false positives, missed positives, uncertainty, missing citations, incorrect locations and whitespace-only differences. Document whether an analysis was specified before or after observing outputs.

The checked-in dataset includes tiny synthetic `node_modules` trees because they are the actual installed-tree inputs to the scanner. Do not replace them with packages downloaded from npm or execute their lifecycle scripts.

LLM reruns consume the operator's account allowance and require an authenticated CLI. They are manual experiments, not part of CI. For publication, follow `DATA_PROVENANCE.md` and run the publication check.
