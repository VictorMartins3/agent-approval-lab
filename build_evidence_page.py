"""Offline artifact for the source-evidence comparison."""

import html
import evidence_eval as ev
import lab

batch = sorted((lab.ROOT / "evidence-results").glob("batch-*"))[-1]
rows = lab.read(batch / "summary.json")
escape = html.escape
summary = ""
for arm in ev.ARMS:
    valid = [r for r in rows if r["arm"] == arm and r["complete"]]
    absent = sum(not value for r in valid for value in ev.oracle(r["case"])[0].values())
    present = sum(value for r in valid for value in ev.oracle(r["case"])[0].values())

    def count(key):
        return sum(len(row["scores"][key]) for row in valid)

    benign = [r for r in valid if r["case"] in ["routine", "legitimate"]]
    risky = [r for r in valid if r["case"] in ["suspicious", "direct_read", "computed_read"]]
    summary += f"<tr><td>{arm}</td><td>{len(valid)}/{sum(r['arm'] == arm for r in rows)}</td><td>{count('false_present')}/{absent}</td><td>{count('missed_present')}/{present}</td><td>{count('invalid_citations')}</td><td>{sum(r['scores']['requested_review'] for r in benign)}/{len(benign)}</td><td>{sum(r['scores']['ready_on_review_case'] for r in risky)}/{len(risky)}</td></tr>"

cards = ""
for row in rows:
    title = f"{row['case']} · {row['arm']} · repetition {row['repeat']}"
    body = "<p>Incomplete; retained in the dataset.</p>"
    if row["complete"]:
        response = row["response"]
        body = f"<p><b>Decision:</b> {escape(response['decision'])}</p>"
        for op, value in response["operations"].items():
            body += f"<p><b>{op}:</b> {value['status']}</p>"
            for citation in value["citations"]:
                body += f"<pre>{escape(citation['file'])}:{citation['line']}\n{escape(citation['quote'])}</pre>"
        for field in ["observations", "risk_interpretation", "limits"]:
            body += f'<h3>{field.replace("_", " ").capitalize()}</h3><p class="explanation">{escape(response[field])}</p>'
        body += f"<pre>{escape(lab.json.dumps(row['scores'], indent=2))}</pre>"
    cards += f'<details data-case="{row["case"]}"><summary>{escape(title)}</summary>{body}<p><a href="{row["run"]}/prompt.txt">Exact input</a> · <a href="{row["run"]}/result.json">Scored review</a> · <a href="{row["run"]}/claude.json">Raw model output</a></p></details>'

models = ", ".join(sorted({m for r in rows for m in r.get("models", [])}))
page = """<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Does the evidence support the claim?</title>
<style>body{margin:0;background:#f5f7f2;color:#192c29;font:16px/1.65 system-ui,sans-serif}main{max-width:1120px;margin:auto;padding:56px 24px}h1{font-size:clamp(34px,5vw,58px);line-height:1.12;letter-spacing:-1.5px;max-width:900px}h2{margin-top:38px}h3{font-size:16px}a{color:#006d58}p{max-width:900px}.eyebrow{font:600 12px monospace;color:#006d58;letter-spacing:2px}.lead{font-size:21px;color:#536b65}.table{overflow:auto}table{border-collapse:collapse;font-size:14px;width:100%}th,td{padding:12px;text-align:left;border-bottom:1px solid #d9e4dd;white-space:nowrap}th{color:#536b65;font-weight:500}.note{background:#faf1df;padding:18px;border-left:3px solid #d6a24a}details{background:#fff;border:1px solid #d9e4dd;padding:18px;margin:12px 0;border-radius:8px}summary{cursor:pointer;font-weight:600}pre{overflow:auto;background:#edf2ec;padding:14px;font-size:13px}.explanation{white-space:pre-wrap;font-size:14px}select{padding:8px;font:inherit;border:1px solid #d9e4dd;border-radius:6px;background:white}footer{font-size:13px;color:#536b65;margin-top:40px}</style></head><body><main>
<div class="eyebrow">CAPSURFACE / EXPLANATION ACCURACY</div><h1>Does the evidence support the claim?</h1>
<p class="lead">A credential-shaped path is not a credential read. A call in source is not proof of runtime execution.</p>
<p>__MODELS__ · 5 synthetic cases · 2 report formats · 3 repetitions per cell</p>
<h2>The comparison</h2><p>Both formats include full numbered source, the real capsurface report, and the same structured review contract. The evidence-linked format adds literal-pattern hints and interpretation limits. This tests their incremental value; the control already has a clearer task than the earlier free-text agent experiment.</p>
<div class="table"><table><thead><tr><th>Format</th><th>Complete</th><th>False positives / absent calls</th><th>Misses / present calls</th><th>Bad citations</th><th>Routine + legitimate handoffs</th><th>Review cases marked ready</th></tr></thead><tbody>__TABLE__</tbody></table></div>
<p>“Bad citations” uses the original strict text-matching rule, including indentation differences. The <a href="__AUDIT__">separate citation audit</a> distinguishes whitespace repairs from incorrect locations or text.</p>
<p class="note">Scores apply to four structured source-operation fields. They do not certify every statement in the free-text explanation. The ground truth is manually defined for these complete fixtures; it is not a general semantic verifier. Small sample, one configured model, no production-accuracy claim.</p>
<h2>Read the evidence</h2><p><a href="EVIDENCE_FINDINGS.md">Findings</a> · <a href="EVIDENCE_PROTOCOL.md">Protocol and limitations</a> · <a href="EVIDENCE_RESULTS.md">Detailed results</a> · <a href="index.html">Original approval experiment</a></p>
<label for="case">Case: </label><select id="case"><option value="all">All</option>__OPTIONS__</select>__CARDS__
<h2>Reproduce</h2><pre>npm test
python3 evidence_eval.py run --repeats 3 --jobs 3
python3 evidence_eval.py report
python3 build_evidence_page.py</pre>
<footer>No lifecycle script or credential-reading function was executed. Reviewer sessions had no execution tools. Exact inputs, responses and scores are linked above.</footer></main><script>document.getElementById('case').addEventListener('change',e=>{for(const node of document.querySelectorAll('[data-case]'))node.hidden=e.target.value!=='all'&&node.dataset.case!==e.target.value;});</script></body></html>"""
for key, value in {
    "__MODELS__": escape(models),
    "__TABLE__": summary,
    "__CARDS__": cards,
    "__OPTIONS__": "".join(f"<option>{c}</option>" for c in ev.CASES),
    "__AUDIT__": str((batch / "verification.json").relative_to(lab.ROOT)),
}.items():
    page = page.replace(key, value)
lab.write(lab.ROOT / "evidence.html", "\n".join(line.rstrip() for line in page.splitlines()) + "\n")
print("Built evidence.html")
