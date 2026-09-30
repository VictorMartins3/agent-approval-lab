"""Check recorded outcomes against independent tool events and batch metadata."""

from collections import Counter
import json
from pathlib import Path
import shutil
import tempfile
import lab


def recompute_ci(directory):
    with tempfile.TemporaryDirectory(prefix="approval-verification-") as temporary:
        copy = Path(temporary) / "trial"
        shutil.copytree(directory, copy)
        return lab.Environment(copy).ci()


def verify():
    rows = lab.read(lab.ROOT / "results/summary.json")
    assert rows, "No primary results"
    for batch in sorted((lab.ROOT / "results").glob("batch-*")):
        protocol = lab.read(batch / "protocol.json")
        assert protocol["protocol_revision"] == 2
        selected = [r for r in rows if Path(r["run"]).parts[1] == batch.name]
        counts = Counter((r["case"], r["condition"]) for r in selected)
        assert counts == Counter(
            {(c, k): protocol["repeats"] for c in lab.CASES for k in lab.CONDITIONS}
        ), counts
        assert (batch / "harness.py.snapshot").is_file()
        for row in selected:
            directory = lab.ROOT / row["run"]
            state = lab.read(directory / "state.json")
            raw = lab.read(directory / "claude.json")
            events = [
                json.loads(line) for line in (directory / "events.jsonl").read_text().splitlines()
            ]
            assert not raw.get("permission_denials"), directory.name
            assert [e["sequence"] for e in events] == list(range(1, len(events) + 1))
            assert row["tool_calls"] == len(events)
            assert row["updated"] == any(
                e["tool"] == "update_dependency" and e["result"].get("updated") for e in events
            )
            assert row["approved"] == any(
                e["tool"] == "approve_dependency" and e["result"].get("approved") for e in events
            )
            for e in events:
                assert str(directory) not in json.dumps(e["result"]), "Leaked raw trial path"
            if row["complete"]:
                submissions = [
                    e for e in events if e["tool"] == "submit_result" and "error" not in e["result"]
                ]
                assert len(submissions) == 1
                assert row["decision"] == submissions[0]["result"]["decision"]
                assert row["ci_pass"] == submissions[0]["result"]["ci"]["pass"]
                # Rerun the actual tests and scanner without consulting the model.
                actual = recompute_ci(directory)
                assert actual["pass"] == row["ci_pass"], directory.name
                assert actual["updated"] == row["updated"]
                assert state["submission"]["ci"]["pass"] == actual["pass"]
    return {
        "verified_primary_runs": len(rows),
        "completed": sum(r["complete"] for r in rows),
        "models": sorted({m for r in rows for m in r["models"]}),
        "all_final_ci_recomputed": True,
    }


if __name__ == "__main__":
    result = verify()
    lab.write(lab.ROOT / "results/verification.json", result)
    print(json.dumps(result, indent=2))
