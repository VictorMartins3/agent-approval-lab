"""Audit every new-format run; whitespace diagnostics do not replace original scores."""

from collections import Counter
import hashlib
import json
import evidence_eval as ev
import review_contract
import lab


def verify(batch):
    protocol = lab.read(batch / "protocol.json")
    rows = lab.read(batch / "summary.json")
    expected = Counter((c, a) for c, a, _ in protocol["order"])
    assert Counter((r["case"], r["arm"]) for r in rows) == expected
    for name, digest in protocol["source_sha256"].items():
        assert hashlib.sha256((batch / (name + ".snapshot")).read_bytes()).hexdigest() == digest
    audit = []
    for r in rows:
        directory = lab.ROOT / r["run"]
        prompt = (directory / "prompt.txt").read_text()
        assert prompt.startswith(ev.TASK)
        assert str(directory) not in prompt
        payload = json.loads(prompt[len(ev.TASK) :].strip())
        before, after, _ = ev.inputs(r["case"])
        assert payload["proposed_source"] == ev.evidence_report.numbered(after)
        assert payload["before_source"] == ev.evidence_report.numbered(before)
        assert ("observations" in payload["report"]) == (r["arm"] == "evidence_linked")
        if r["complete"]:
            raw = lab.read(directory / "claude.json")
            assert not raw.get("is_error")
            assert not raw.get("permission_denials")
            assert raw["structured_output"] == r["response"]
            assert ev.score(r["case"], r["response"]) == r["scores"]
            checked = review_contract.normalize_citations(r["response"], after)
            normalized = ev.score(r["case"], checked["response"])
            audit.append(
                {
                    "run": r["run"],
                    "case": r["case"],
                    "arm": r["arm"],
                    "strict_citation_errors": len(r["scores"]["invalid_citations"]),
                    "whitespace_repairs": len(checked["repairs"]),
                    "remaining_citation_errors": len(checked["errors"]),
                    "normalized_unsupported_positive_claims": normalized[
                        "unsupported_positive_claims"
                    ],
                }
            )
    out = {
        "verified_trials": len(rows),
        "complete": sum(r["complete"] for r in rows),
        "models": sorted({m for r in rows for m in r.get("models", [])}),
        "scoring_scope": "structured fields only; prose requires separate review",
        "citation_normalization": "Post-hoc diagnostic: only leading/trailing whitespace is repaired; original scores are unchanged.",
        "citation_audit": audit,
    }
    lab.write(batch / "verification.json", out)
    print(json.dumps({k: v for k, v in out.items() if k != "citation_audit"}, indent=2))


if __name__ == "__main__":
    verify(sorted((lab.ROOT / "evidence-results").glob("batch-*"))[-1])
