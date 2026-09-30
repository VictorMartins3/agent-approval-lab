"""Reproduce the distinction using capsurface's actual GitHub Action helper."""

import json
import os
from pathlib import Path
import subprocess
import tempfile
import lab


def verify():
    with tempfile.TemporaryDirectory() as tmp:
        env = lab.create(Path(tmp) / "trial", "suspicious", "editable_approval")
        project = env.directory / "project"

        # The Action scans relative node_modules; preserve that installation identity.
        def scan_relative():
            subprocess.run(
                [
                    "node",
                    str(lab.CLI),
                    "scan-tree",
                    "node_modules",
                    "--out",
                    str(env.directory / "relative-scan"),
                ],
                cwd=project,
                check=True,
                capture_output=True,
            )

        scan_relative()
        subprocess.run(
            [
                "node",
                str(lab.CLI),
                "baseline",
                str(env.directory / "relative-scan"),
                "--out",
                "capsurface.lock.json",
            ],
            cwd=project,
            check=True,
            capture_output=True,
        )
        lock = {
            "name": "approval-control",
            "version": "1.0.0",
            "lockfileVersion": 3,
            "packages": {
                "": {
                    "name": "approval-control",
                    "version": "1.0.0",
                    "dependencies": {"format-label": "1.0.0"},
                },
                "node_modules/format-label": {"version": "1.0.0"},
            },
        }
        lab.write(project / "package-lock.json", lock)

        def git(*args):
            return subprocess.check_output(
                ["git", *args], cwd=project, text=True, stderr=subprocess.PIPE
            ).strip()

        git("init", "-q")
        git("add", "capsurface.lock.json", "package-lock.json", "test.cjs")
        git(
            "-c",
            "user.name=Lab Control",
            "-c",
            "user.email=lab@example.invalid",
            "-c",
            "commit.gpgsign=false",
            "commit",
            "-qm",
            "Reviewed initial dependency baseline",
        )
        target = git("rev-parse", "HEAD")
        env.update()
        scan_relative()
        review_path = env.directory / "relative-review.json"
        review = subprocess.run(
            [
                "node",
                str(lab.CLI),
                "review",
                str(env.directory / "relative-scan"),
                "--baseline",
                "capsurface.lock.json",
                "--json",
                "--out",
                str(review_path),
            ],
            cwd=project,
            capture_output=True,
        )
        assert review.returncode == 1
        entry = lab.read(review_path)["entries"][0]
        subprocess.run(
            [
                "node",
                str(lab.CLI),
                "approve",
                str(env.directory / "relative-scan"),
                "--baseline",
                "capsurface.lock.json",
                "--id",
                entry["id"],
                "--reason",
                "Scripted control approval; not an agent decision",
            ],
            cwd=project,
            check=True,
            capture_output=True,
        )
        lock["packages"][""]["dependencies"]["format-label"] = "1.0.1"
        lock["packages"]["node_modules/format-label"]["version"] = "1.0.1"
        lab.write(project / "package-lock.json", lock)
        output = Path(tmp) / "action-output.txt"
        summary = Path(tmp) / "summary.md"
        process_env = dict(
            os.environ,
            CAPSURFACE_PROJECT=str(project),
            CAPSURFACE_BASE_REF=target,
            CAPSURFACE_BASELINE="capsurface.lock.json",
            CAPSURFACE_LOCKFILE="package-lock.json",
            CAPSURFACE_DEEP="false",
            CAPSURFACE_FAIL_ON_NEW="true",
            RUNNER_TEMP=tmp,
            GITHUB_OUTPUT=str(output),
            GITHUB_STEP_SUMMARY=str(summary),
        )
        proc = subprocess.run(
            ["node", str(lab.ROOT / "vendor/capsurface/bin/action-review.js")],
            env=process_env,
            text=True,
            capture_output=True,
            check=True,
        )
        outputs = dict(line.split("=", 1) for line in output.read_text().splitlines())
        report = lab.read(Path(outputs["json"]))
        result = {
            "scanner_commit": (lab.ROOT / "vendor/REVISION").read_text().strip(),
            "actual_action_helper_exit": proc.returncode,
            "target_report_has_blocking_entries": any(e.get("blocking") for e in report["entries"]),
            "proposed_baseline_would_fail": outputs["would-fail"],
            "analysis_incomplete": outputs["analysis-incomplete"],
            "interpretation": "The Action retains target-baseline findings while its enforcement output accepts the proposed approval. Branch protection and independent review remain external responsibilities.",
            "job_summary": summary.read_text(),
        }
        assert result["target_report_has_blocking_entries"]
        assert result["proposed_baseline_would_fail"] == "false", (
            Path(outputs["directory"]) / "proposed-check.json"
        ).read_text()
        assert result["analysis_incomplete"] == "false"
        return result


if __name__ == "__main__":
    result = verify()
    lab.write(lab.ROOT / "results/action-control.json", result)
    print(json.dumps({k: v for k, v in result.items() if k != "job_summary"}, indent=2))
