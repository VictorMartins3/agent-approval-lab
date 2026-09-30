"""Check published records, source snapshots, links, and local-path redactions."""

import argparse
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data-manifest.json"
RECORDS = {
    "state.json",
    "events.jsonl",
    "claude.json",
    "result.json",
    "metadata.json",
    "prompt.txt",
    "protocol.json",
    "summary.json",
    "execution.json",
}


def record_files():
    for directory in ["results", "evidence-results"]:
        for path in sorted((ROOT / directory).rglob("*")):
            if path.is_file() and (
                path.name in RECORDS
                or path.name.endswith(".snapshot")
                or "node_modules" in path.parts
            ):
                yield path


def hashes():
    return {
        str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in record_files()
    }


class Links(HTMLParser):
    def __init__(self, path):
        super().__init__()
        self.path = path

    def handle_starttag(self, tag, attrs):
        for key, value in attrs:
            if (
                key not in ["href", "src"]
                or not value
                or value.startswith(("#", "https:", "http:", "mailto:", "data:"))
            ):
                continue
            target = (self.path.parent / value.split("#")[0]).resolve()
            if not target.is_file():
                raise ValueError(f"Broken local link in {self.path.name}: {value}")


def check(write_manifest=False):
    if write_manifest:
        MANIFEST.write_text(json.dumps(hashes(), indent=2) + "\n")
    expected = json.loads(MANIFEST.read_text())
    if hashes() != expected:
        raise ValueError("Published data differ from data-manifest.json")
    for parent in ["results", "evidence-results"]:
        for protocol in (ROOT / parent).glob("batch-*/protocol.json"):
            data = json.loads(protocol.read_text())
            for name, digest in data.get("source_sha256", {}).items():
                snapshot = protocol.parent / (name + ".snapshot")
                if hashlib.sha256(snapshot.read_bytes()).hexdigest() != digest:
                    raise ValueError("Experiment snapshot hash mismatch")
    tracked = subprocess.run(["git", "ls-files", "-z"], cwd=ROOT, text=True, capture_output=True)
    paths = (
        [ROOT / x for x in tracked.stdout.split("\0") if x]
        if tracked.returncode == 0 and tracked.stdout
        else [
            p
            for p in ROOT.rglob("*")
            if p.is_file()
            and not any(x in {".git", "work", "__pycache__"} for x in p.relative_to(ROOT).parts)
        ]
    )
    patterns = {
        "local home path": r"/(?:Users|home)/[A-Za-z0-9_.-]+/",
        "GitHub token": r"gh[pousr]_[A-Za-z0-9]{20,}",
        "API secret": r"sk-[A-Za-z0-9_-]{24,}",
        "private key": r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----",
    }
    for p in paths:
        if not p.is_file():
            continue
        content = p.read_text()
        for name, pattern in patterns.items():
            if re.search(pattern, content):
                raise ValueError(f"{name} in {p.relative_to(ROOT)}")
        if p.name == "claude.json":
            data = json.loads(content)
            if "session_id" in data or "uuid" in data:
                raise ValueError("Session identifier in public export")
    for p in (ROOT / "docs").glob("*.html"):
        Links(p).feed(p.read_text())
    for p in [*ROOT.glob("*.md"), *(ROOT / "site").glob("*")]:
        if p.is_file() and chr(8212) in p.read_text():
            raise ValueError(f"Em dash in presentation text: {p.name}")
    print(
        f"Checked {len(expected)} record hashes, source snapshots, publication paths, and site links"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-manifest", action="store_true")
    check(parser.parse_args().write_manifest)
