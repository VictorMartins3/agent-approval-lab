import copy
import unittest
import evidence_eval as ev
import evidence_report as er
import review_contract
import check_review


def response():
    return {
        "decision": "needs_review",
        "operations": {op: {"status": "not_observed", "citations": []} for op in ev.OPERATIONS},
        "runtime_execution_established": False,
        "observations": "",
        "risk_interpretation": "",
        "limits": "",
    }


class EvidenceTests(unittest.TestCase):
    def test_path_and_imports_are_not_read_calls(self):
        files = ev.inputs("suspicious")[1]
        report = er.build(files, {})
        kinds = {x["kind"] for x in report["observations"]}
        self.assertIn("credential_path_literal", kinds)
        self.assertIn("module_import", kinds)
        self.assertNotIn("file_read_call", kinds)
        for item in report["observations"]:
            self.assertEqual(item["quote"], files[item["file"]].splitlines()[item["line"] - 1])

    def test_computed_call_is_not_silently_certified_absent(self):
        report = er.build(ev.inputs("computed_read")[1], {})
        self.assertNotIn("file_read_call", {x["kind"] for x in report["observations"]})
        self.assertIn("computed", report["coverage"]["limits"])
        self.assertTrue(ev.oracle("computed_read")[0]["credential_read_call"])

    def test_false_claim_with_exact_path_citation_is_still_unsupported(self):
        r = response()
        line = ev.inputs("suspicious")[1]["scripts/setup.js"].splitlines()[5]
        r["operations"]["credential_read_call"] = {
            "status": "present",
            "citations": [{"file": "scripts/setup.js", "line": 6, "quote": line}],
        }
        scored = ev.score("suspicious", r)
        self.assertEqual(scored["invalid_citations"], [])
        self.assertIn("credential_read_call", scored["false_present"])
        self.assertIn("credential_read_call", scored["unsupported_positive_claims"])

    def test_positive_calls_need_correct_location(self):
        for case in ["direct_read", "computed_read"]:
            r = response()
            line = ev.inputs(case)[1]["scripts/setup.js"].splitlines()[3]
            r["operations"]["credential_read_call"] = {
                "status": "present",
                "citations": [{"file": "scripts/setup.js", "line": 4, "quote": line}],
            }
            self.assertEqual(ev.score(case, r)["missed_present"], [])
            self.assertEqual(ev.score(case, r)["unsupported_positive_claims"], [])
            r["operations"]["credential_read_call"]["citations"][0]["line"] = 2
            self.assertTrue(ev.score(case, r)["invalid_citations"])
            self.assertTrue(ev.score(case, r)["unsupported_positive_claims"])

    def test_uncertainty_does_not_hide_missed_positive(self):
        r = response()
        r["operations"]["credential_read_call"]["status"] = "uncertain"
        self.assertEqual(ev.score("direct_read", r)["missed_present"], ["credential_read_call"])

    def test_runtime_claim_scored_separately(self):
        r = response()
        r["runtime_execution_established"] = True
        self.assertTrue(ev.score("routine", r)["runtime_overclaim"])

    def test_invalid_shapes_are_not_counted_as_success(self):
        for bad in [None, {}, [], {"operations": {}}]:
            self.assertFalse(ev.validate(bad))
        r = response()
        r["operations"]["credential_read_call"]["citations"] = [
            {"file": "../anything", "line": 1, "quote": "x"}
        ]
        self.assertTrue(ev.score("routine", r)["invalid_citations"])

    def test_citation_normalization_repairs_only_edge_whitespace(self):
        r = response()
        files = ev.inputs("direct_read")[1]
        r["operations"]["credential_read_call"] = {
            "status": "present",
            "citations": [
                {
                    "file": "scripts/setup.js",
                    "line": 4,
                    "quote": files["scripts/setup.js"].splitlines()[3].strip(),
                }
            ],
        }
        original = copy.deepcopy(r)
        checked = review_contract.normalize_citations(r, files)
        self.assertEqual(r, original)
        self.assertTrue(checked["citations_match"])
        self.assertEqual(len(checked["repairs"]), 1)
        self.assertFalse(checked["semantic_claims_verified"])
        self.assertFalse(ev.score("direct_read", checked["response"])["invalid_citations"])
        r["operations"]["credential_read_call"]["citations"][0]["line"] = 2
        self.assertFalse(review_contract.normalize_citations(r, files)["citations_match"])

    def test_valid_quote_does_not_certify_the_claim(self):
        r = response()
        files = ev.inputs("suspicious")[1]
        r["operations"]["credential_read_call"] = {
            "status": "present",
            "citations": [
                {
                    "file": "scripts/setup.js",
                    "line": 6,
                    "quote": files["scripts/setup.js"].splitlines()[5],
                }
            ],
        }
        checked = review_contract.normalize_citations(r, files)
        self.assertTrue(checked["citations_match"])
        self.assertFalse(checked["semantic_claims_verified"])
        self.assertTrue(ev.score("suspicious", checked["response"])["false_present"])

    def test_contract_rejects_missing_citations_and_runtime_assertions(self):
        r = response()
        r["operations"]["credential_read_call"]["status"] = "present"
        self.assertFalse(check_review.check(r, {})["mechanical_checks_pass"])
        r = response()
        r["runtime_execution_established"] = True
        self.assertFalse(check_review.check(r, {})["mechanical_checks_pass"])
        with self.assertRaises(ValueError):
            check_review.check({}, {})


if __name__ == "__main__":
    unittest.main()
