"""Build the public research note from the checked-in experiment records."""

import html
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
REPOSITORY = "https://github.com/VictorMartins3/agent-approval-lab"


def load(path):
    return json.loads((ROOT / path).read_text())


def link(path, label):
    return f'<a href="{REPOSITORY}/blob/main/{path}">{html.escape(label)}</a>'


def build():
    agents = load("results/summary.json")
    batch = sorted((ROOT / "evidence-results").glob("batch-*"))[-1]
    reviews = json.loads((batch / "summary.json").read_text())
    audit = json.loads((batch / "verification.json").read_text())
    if len(agents) != 27 or len(reviews) != 30 or not all(r["complete"] for r in agents + reviews):
        raise ValueError("The research note requires its complete, specified datasets")
    agent_rows = []
    names = {
        "tests_only": "Application tests",
        "editable_approval": "Editable approval",
        "protected_approval": "Protected approval",
    }
    for case in ["routine", "legitimate", "suspicious"]:
        for condition, name in names.items():
            group = [r for r in agents if r["case"] == case and r["condition"] == condition]
            agent_rows.append(
                f'<tr><th scope="row">{case.capitalize()}</th><td>{name}</td><td>{sum(r["decision"] == "ready" for r in group)}/{len(group)}</td><td>{sum(r["requested_review"] for r in group)}/{len(group)}</td><td>{sum(r["approved"] for r in group)}/{len(group)}</td></tr>'
            )
    review_rows = []
    for arm, name in [
        ("current", "Report + structured contract"),
        ("evidence_linked", "Same contract + source hints"),
    ]:
        group = [r for r in reviews if r["arm"] == arm]
        claims = sum(len(r["scores"]["false_present"]) for r in group)
        misses = sum(len(r["scores"]["missed_present"]) for r in group)
        benign = [r for r in group if r["case"] in ["routine", "legitimate"]]
        risky = [r for r in group if r["case"] in ["suspicious", "direct_read", "computed_read"]]
        review_rows.append(
            f'<tr><th scope="row">{name}</th><td>{claims}/51</td><td>{misses}/9</td><td>{sum(r["scores"]["requested_review"] for r in benign)}/{len(benign)}</td><td>{sum(r["scores"]["requested_review"] for r in risky)}/{len(risky)}</td></tr>'
        )
    if any(r["scores"]["false_present"] or r["scores"]["missed_present"] for r in reviews):
        raise ValueError("Review classifications changed; revise the research note")
    repairs = sum(r["whitespace_repairs"] for r in audit["citation_audit"])
    if repairs != 9 or any(r["remaining_citation_errors"] for r in audit["citation_audit"]):
        raise ValueError("Citation findings changed; revise the research note")
    record = "results/batch-20260930-031429/trial-26899684a97a/state.json"
    excerpt = (
        "a new scripts/setup.js that reads process.env.HOME + '/.npmrc' (npm auth token location)"
    )
    if excerpt not in load(record)["submission"]["reason"]:
        raise ValueError("The excerpt must match the recorded explanation")
    source = (ROOT / "fixtures/suspicious/1.0.1/scripts/setup.js").read_text()
    lines = "".join(
        f'<span class="code-line"><span class="line-number" aria-hidden="true">{i}</span>{html.escape(text)}</span>'
        for i, text in enumerate(source.splitlines(), 1)
    )
    artifacts = [
        ("README.md", "Repository and reproduction", "Code, requirements, and commands."),
        ("PROTOCOL.md", "Agent protocol", "Tools, approval policies, and pilot corrections."),
        (
            "EVIDENCE_PROTOCOL.md",
            "Reviewer protocol",
            "Output contract, fixture labels, and scoring rules.",
        ),
        (
            "results/summary.json",
            "27 agent outcomes",
            "Decisions, actions, and independently recomputed CI.",
        ),
        (
            str((batch / "summary.json").relative_to(ROOT)),
            "30 structured reviews",
            "Complete responses and operation-level scores.",
        ),
        (
            str((batch / "verification.json").relative_to(ROOT)),
            "Citation audit",
            "Original scores and whitespace normalization.",
        ),
        (
            "results/action-control.json",
            "Action control",
            "Actual capsurface Action helper output.",
        ),
        (
            "DATA_PROVENANCE.md",
            "Data provenance",
            "Public-export redactions and reproduction limits.",
        ),
    ]
    items = "".join(
        f"<li>{link(path, title)}<span>{description}</span></li>"
        for path, title, description in artifacts
    )
    template = (ROOT / "site/index.template.html").read_text()
    replacements = {
        "{{AGENT_ROWS}}": "".join(agent_rows),
        "{{REVIEW_ROWS}}": "".join(review_rows),
        "{{SOURCE}}": lines,
        "{{EXCERPT}}": html.escape(excerpt),
        "{{EXCERPT_LINK}}": link(record, "Read the complete response"),
        "{{ARTIFACTS}}": items,
        "{{REPOSITORY}}": REPOSITORY,
    }
    for key, value in replacements.items():
        template = template.replace(key, value)
    if "{{" in template:
        raise ValueError("Unresolved template value")
    destination = ROOT / "docs"
    destination.mkdir(exist_ok=True)
    (destination / "index.html").write_text(template)
    shutil.copyfile(ROOT / "site/style.css", destination / "style.css")
    (destination / ".nojekyll").write_text("")
    print("Built docs/index.html from 27 agent episodes and 30 structured reviews")


if __name__ == "__main__":
    build()
