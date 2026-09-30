import importlib.util
from pathlib import Path
import unittest
import tempfile
import hashlib
import lab
import verify_results

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("publication", ROOT / "scripts/check_publication.py")
publication = importlib.util.module_from_spec(spec)
spec.loader.exec_module(publication)


class PublicationTests(unittest.TestCase):
    def test_ci_recomputation_preserves_source_records(self):
        with tempfile.TemporaryDirectory() as directory:
            env = lab.create(Path(directory) / "trial", "legitimate", "editable_approval")
            env.update()
            paths = [p for p in env.directory.rglob("*") if p.is_file()]
            before = {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
            actual = verify_results.recompute_ci(env.directory)
            self.assertFalse(actual["pass"])
            self.assertEqual(before, {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in paths})
            self.assertFalse((env.directory / "target-review.json").exists())

    def test_local_links_resolve_relative_to_page(self):
        with tempfile.TemporaryDirectory() as directory:
            page = Path(directory) / "index.html"
            (Path(directory) / "style.css").write_text("")
            publication.Links(page).feed('<link href="style.css"><a href="#results">Results</a>')
            with self.assertRaises(ValueError):
                publication.Links(page).feed('<a href="missing.json">Data</a>')

    def test_external_links_are_not_read_as_files(self):
        publication.Links(ROOT / "docs/index.html").feed(
            '<a href="https://github.com/example">Source</a>'
        )


if __name__ == "__main__":
    unittest.main()
