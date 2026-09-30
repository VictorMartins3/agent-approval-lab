"""Mechanical citation checks, deliberately separate from semantic claim validation."""

from copy import deepcopy


def normalize_citations(response, files):
    """Return a copy with whitespace-only citation differences repaired.

    Only supplied source-map keys are read. Exact text or leading/trailing
    whitespace equivalence is required; never search another line to rescue a
    wrong location. This checks quotations, not whether they entail a claim.
    """
    result = deepcopy(response)
    repairs, errors = [], []
    for operation, claim in result["operations"].items():
        if claim["status"] == "present" and not claim["citations"]:
            errors.append(
                {"operation": operation, "reason": "positive source claim requires a citation"}
            )
        for index, citation in enumerate(claim["citations"]):
            lines = files.get(citation["file"], "").splitlines()
            location = {
                "operation": operation,
                "citation": index,
                "file": citation["file"],
                "line": citation["line"],
            }
            line = citation["line"]
            if type(line) is not int or not 1 <= line <= len(lines):
                errors.append({**location, "reason": "unknown file or out-of-range line"})
                continue
            actual = lines[line - 1]
            if citation["quote"] == actual:
                continue
            if citation["quote"].strip() == actual.strip():
                repairs.append(
                    {**location, "original_quote": citation["quote"], "canonical_quote": actual}
                )
                citation["quote"] = actual
            else:
                errors.append(
                    {**location, "reason": "quoted text does not match the specified source line"}
                )
    return {
        "response": result,
        "repairs": repairs,
        "errors": errors,
        "citations_match": not errors,
        "semantic_claims_verified": False,
    }
