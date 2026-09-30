#!/usr/bin/env python3
"""Validate a structured review against a supplied source map; no code execution."""

import argparse
import json
from pathlib import Path
import sys
import evidence_eval
import review_contract


def check(response, sources):
    if not evidence_eval.validate(response):
        raise ValueError("Review does not match the structured review contract")
    if not isinstance(sources, dict) or any(
        not isinstance(k, str) or not isinstance(v, str) for k, v in sources.items()
    ):
        raise ValueError("Sources must map relative display filenames to source strings")
    result = review_contract.normalize_citations(response, sources)
    result["runtime_claim_supported"] = not response["runtime_execution_established"]
    # This contract accepts source evidence only; runtime claims need a separate trace.
    result["mechanical_checks_pass"] = (
        result["citations_match"] and result["runtime_claim_supported"]
    )
    return result


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--review", type=Path, required=True)
    p.add_argument("--sources", type=Path, required=True)
    p.add_argument("--out", type=Path)
    args = p.parse_args()
    try:
        result = check(json.loads(args.review.read_text()), json.loads(args.sources.read_text()))
        text = json.dumps(result, indent=2) + "\n"
        if args.out:
            args.out.write_text(text)
        else:
            print(text, end="")
        sys.exit(0 if result["mechanical_checks_pass"] else 1)
    except (ValueError, OSError) as e:
        print(str(e), file=sys.stderr)
        sys.exit(2)
