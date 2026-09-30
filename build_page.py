"""Build a self-contained, offline results page from the recorded experiment."""

import html
from pathlib import Path
import lab

rows = lab.read(lab.ROOT / "results/summary.json")
valid = [r for r in rows if r["complete"]]
models = sorted({m for r in rows for m in r["models"]})


def count(case, condition, key):
    group = [r for r in valid if r["case"] == case and r["condition"] == condition]
    return f"{sum(bool(r[key]) for r in group)}/{len(group)}"


table = ""
for case in lab.CASES:
    for condition in lab.CONDITIONS:
        group = [r for r in valid if r["case"] == case and r["condition"] == condition]
        n = len(group)
        table += f"<tr><td>{case}</td><td>{condition.replace('_', ' ')}</td><td>{sum(r['decision'] == 'ready' for r in group)}/{n}</td><td>{count(case, condition, 'requested_review')}</td><td>{count(case, condition, 'approved')}</td></tr>"

cards = ""
for r in rows:
    label = f"{r['case']} · {r['condition'].replace('_', ' ')} · {Path(r['run']).name}"
    links = f'<a href="{r["run"]}/events.jsonl">Tool log</a> · <a href="{r["run"]}/claude.json">Model output</a>'
    cards += f'''<details data-case="{r["case"]}"><summary>{html.escape(label)} <span>{html.escape(r["decision"] or "incomplete")}</span></summary>
    <p>{html.escape(r["reason"] or "No completed submission.")}</p><p class="meta">Update applied: {r["updated"]} · CI passes: {r["ci_pass"]} · Approval attempts: {r["approval_attempts"]} · Self-approved: {r["approved"]}</p><p>{links}</p></details>'''

page = """<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Who approves an agent's dependency update?</title><style>
:root{color-scheme:light;--ink:#192c29;--muted:#536b65;--line:#d9e4dd;--green:#006d58}*{box-sizing:border-box}body{margin:0;background:#f5f7f2;color:var(--ink);font:17px/1.65 system-ui,sans-serif}main{max-width:1080px;margin:auto;padding:64px 28px}header{border-bottom:1px solid var(--line);padding-bottom:35px}.eyebrow{font:600 12px/1.5 ui-monospace,monospace;letter-spacing:2px;text-transform:uppercase;color:var(--green)}h1{font-size:clamp(36px,6vw,64px);line-height:1.08;max-width:900px;letter-spacing:-2px;margin:22px 0}h2{font-size:26px;letter-spacing:-.5px;margin-top:42px}p{max-width:830px}.lead{font-size:21px;color:var(--muted)}.stats{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin:30px 0}.stat{background:white;padding:22px;border:1px solid var(--line);border-radius:10px}.stat strong{display:block;font-size:35px;line-height:1.2}.stat span,.meta{font-size:13px;color:var(--muted)}a{color:var(--green);text-underline-offset:3px}.table{overflow:auto}table{width:100%;border-collapse:collapse;font-size:14px;text-align:left}td,th{padding:12px;border-bottom:1px solid var(--line);white-space:nowrap}th{color:var(--muted);font-weight:500}.note{padding:18px 22px;border-left:3px solid #d6a24a;background:#faf1df}.flow{display:grid;grid-template-columns:1fr 1fr;gap:16px}.flow article{background:white;border:1px solid var(--line);border-radius:10px;padding:22px}.flow h3{margin:0}code,pre{font-family:ui-monospace,monospace;font-size:14px}pre{background:#172c27;color:#e5f2e9;padding:22px;border-radius:10px;overflow:auto}details{background:white;border:1px solid var(--line);border-radius:8px;margin:10px 0;padding:15px 20px}summary{cursor:pointer;font-size:14px;font-weight:600}summary span{float:right;color:var(--green);font-weight:400}details p{font-size:14px}select{font:inherit;padding:8px;background:white;border:1px solid var(--line);border-radius:6px}footer{margin-top:45px;font-size:13px;color:var(--muted)}@media(max-width:650px){main{padding:35px 18px}.stats,.flow{grid-template-columns:1fr}summary span{float:none;display:block}}
</style></head><body><main>
<header><div class="eyebrow">capsurface / controlled agent experiment</div><h1>Who approves an agent’s dependency update?</h1><p class="lead">Separate the evidence an agent sees from the authority it has to approve a change.</p><p>__MODEL__ · 3 synthetic updates · 3 CI configurations · 3 repetitions per cell</p></header>
<div class="stats"><div class="stat"><strong>__COMPLETE__</strong><span>completed agent sessions</span></div><div class="stat"><strong>__SUSPICIOUS__</strong><span>suspicious cases escalated for review</span></div><div class="stat"><strong>__SELF__</strong><span>legitimate updates self-approved with editable approval</span></div></div>
<h2>What happened</h2><p>The agent inspected and escalated the suspicious update in every condition. It also requested review for every legitimate capability addition in the revised batch, including when it could approve the change itself. These sessions do not establish improved detection or a behavioral difference from protecting approval. The executable controls separately demonstrate the authority boundary.</p>
<div class="table"><table><thead><tr><th>Update</th><th>CI configuration</th><th>Ready to merge</th><th>Review requested</th><th>Self-approved</th></tr></thead><tbody>__TABLE__</tbody></table></div>
<p class="meta">Each denominator is completed runs in that cell. “Ready” is the agent's decision. Actual final CI and update state are saved separately. A passing check on the original version is not a completed update.</p>
<h2>A report can retain a warning while CI passes</h2><div class="flow"><article><h3>Editable approval</h3><p>Update → capability report → agent records approval → proposed-baseline check passes.</p><p>The original-baseline report still contains the findings.</p></article><article><h3>Protected approval</h3><p>Update → same report → approval request denied → original-baseline check remains blocked.</p><p>An independent reviewer must decide, including for legitimate new capabilities.</p></article></div>
<p>This transition was verified with scripted controls and the actual capsurface Action helper. It is separate from the observed agent decisions. <a href="results/action-control.json">Inspect the Action reproduction</a>.</p>
<h2>The explanation needs its own check</h2><p>The suspicious fixture contains imports and a credential-shaped path, but never reads credentials or sends data. Some model explanations assert a credential read anyway. Escalating a change and describing its evidence accurately are separate requirements.</p>
<div class="note">Small experiment, bounded tools, one model configuration. These are not real malicious packages or production failure rates. Protected approval is enforced by this harness's tool boundary, not an operating-system sandbox. An initial 27-run pilot is retained separately; this table uses the revised protocol with opaque case paths. See the protocol for all corrections.</div>
<h2>Inspect every run</h2><label for="case">Filter by update: </label><select id="case"><option value="all">All cases</option><option>routine</option><option>legitimate</option><option>suspicious</option></select><section id="runs">__CARDS__</section>
<h2>Follow-up: explanation accuracy</h2><p>The next experiment compares structured source-operation reviews with and without additional source-linked hints. <a href="evidence.html">Open the evidence comparison</a>.</p>
<h2>Reproduce</h2><pre>npm test
npm run demo
python3 action_control.py
python3 lab.py run --repeats 3 --jobs 3</pre><p><a href="README.md">Project README</a> · <a href="PROTOCOL.md">Method and limitations</a> · <a href="results/summary.json">Structured outcomes</a> · <a href="FINDINGS.md">Analysis</a></p>
<footer>Scanner pinned to 93b7ba9f19431f2800ecb3a737fa1ff2a5b751b3. No lifecycle scripts executed. Raw local artifacts retain paths and session metadata; this page is an offline review artifact.</footer>
</main><script>document.getElementById('case').addEventListener('change',e=>{for(const node of document.querySelectorAll('[data-case]'))node.hidden=e.target.value!=='all'&&node.dataset.case!==e.target.value;});</script></body></html>"""
replacements = {
    "__MODEL__": html.escape(", ".join(models)),
    "__COMPLETE__": f"{len(valid)}/{len(rows)}",
    "__SUSPICIOUS__": f"{sum(r['requested_review'] for r in valid if r['case'] == 'suspicious')}/{sum(r['case'] == 'suspicious' for r in valid)}",
    "__SELF__": count("legitimate", "editable_approval", "approved"),
    "__TABLE__": table,
    "__CARDS__": cards,
}
for key, value in replacements.items():
    page = page.replace(key, value)
lab.write(lab.ROOT / "index.html", page)
print("Built index.html from recorded outcomes")
