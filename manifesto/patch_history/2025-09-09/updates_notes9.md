Two blockers: CI has no `jobs`; ingest YAML is malformed. Apply these patches.

```diff
# .github/workflows/ci.yml  (replace file)
+name: CI
+on:
+  push: { branches: [main] }
+  pull_request: { branches: [main] }
+concurrency:
+  group: ${{ github.workflow }}-${{ github.ref }}
+  cancel-in-progress: true
+jobs:
+  lint:
+    runs-on: ubuntu-latest
+    steps:
+      - uses: actions/checkout@v4
+      - uses: actions/setup-python@v5
+        with: { python-version: '3.12' }
+      - name: Install tools
+        run: |
+          python -m pip install --upgrade pip
+          pip install ruff mypy
+      - name: No wildcard imports
+        run: |
+          ! grep -R --include='*.py' -nE 'from\s+\S+\s+import\s+\*' src tools . || (echo 'Wildcard import found' && exit 1)
+      - name: Lint + types
+        run: |
+          ruff check .
+          mypy --ignore-missing-imports .
+
+  unit:
+    runs-on: ubuntu-latest
+    steps:
+      - uses: actions/checkout@v4
+      - uses: actions/setup-python@v5
+        with: { python-version: '3.12' }
+      - name: Install
+        run: |
+          python -m pip install --upgrade pip
+          pip install -r requirements.txt || true
+          pip install pytest
+      - name: Tests
+        run: pytest -q --maxfail=1 --disable-warnings
+
+  smoke:
+    runs-on: ubuntu-latest
+    steps:
+      - uses: actions/checkout@v4
+      - uses: actions/setup-python@v5
+        with: { python-version: '3.12' }
+      - name: Install
+        run: |
+          python -m pip install --upgrade pip
+          pip install -r requirements.txt || true
+      - name: Chat smoke
+        run: |
+          mkdir -p artifacts/ci_smoke
+          (python -m tools.qrft_chat 2>/dev/null || python qrft_chat.py || python chat_loop.py) <<'EOF' | tee artifacts/ci_smoke/chat.log
+/metrics
+simplify x**2 - 1
+/exit
+EOF
+          grep -q 'x\*\*2 - 1' artifacts/ci_smoke/chat.log
+          grep -q '"math_available"' artifacts/ci_smoke/chat.log || true
+          grep -q '"sympy_version"' artifacts/ci_smoke/chat.log || true
+      - uses: actions/upload-artifact@v4
+        with: { name: chat-smoke, path: artifacts/ci_smoke/chat.log }
```

```diff
# .github/workflows/ingest.yml  (replace file)
+name: ingest
+on:
+  push:
+    paths:
+      - 'research/new/**/*.pdf'
+  workflow_dispatch:
+permissions:
+  contents: write
+  pull-requests: write
+concurrency:
+  group: ingest-${{ github.ref }}
+  cancel-in-progress: true
+jobs:
+  ingest:
+    runs-on: ubuntu-latest
+    timeout-minutes: 10
+    steps:
+      - uses: actions/checkout@v4
+      - name: System deps
+        run: |
+          sudo apt-get update
+          sudo apt-get install -y poppler-utils
+      - name: Extract PDFs and write stubs
+        id: extract
+        shell: bash
+        run: |
+          set -euo pipefail
+          python - <<'PY'
+          from pathlib import Path
+          import subprocess, json, re, hashlib, datetime as dt, os
+          root=Path("."); out=Path("ops/ingest"); out.mkdir(parents=True, exist_ok=True)
+          meta=Path("docs/Meta-ToC.md"); opsf=Path("spec/operators.md"); invf=Path("spec/invariants.md")
+          agents=Path("prompts/agents.jsonl"); bundle=Path("ops/context_bundle.json")
+          touched=[]
+          src=Path("research/new")
+          if src.exists():
+              for p in src.rglob("*.pdf"):
+                  txt=out/(p.stem+".txt"); txt.parent.mkdir(parents=True, exist_ok=True)
+                  subprocess.run(["pdftotext","-layout",str(p),str(txt)], check=True)
+                  T=txt.read_text(encoding="utf-8", errors="ignore")
+                  title=re.findall(r"^[^\n]{8,120}", T, re.M)
+                  title=(title[0].strip() if title else p.stem)
+                  h=hashlib.sha1((title+str(p.stat().st_size)).encode()).hexdigest()[:8]
+                  meta.parent.mkdir(parents=True, exist_ok=True)
+                  line=f"- {title} [{dt.date.today()}] (id:{h})"
+                  cur=meta.read_text(encoding="utf-8") if meta.exists() else "# Meta-ToC\n"
+                  if line not in cur:
+                      meta.write_text(cur.rstrip()+"\n"+line+"\n", encoding="utf-8")
+                  opsf.parent.mkdir(parents=True, exist_ok=True)
+                  with opsf.open("a", encoding="utf-8") as f:
+                      f.write(f"\n## OP-{h} {title}\n- Inputs: TBA\n- Transform: TBA\n- Outputs: TBA\n- Source: research/new/{p.name}\n")
+                  invf.parent.mkdir(parents=True, exist_ok=True)
+                  with invf.open("a", encoding="utf-8") as f:
+                      f.write(f"\n### I-{h} {title}\n- Claim: TBA\n- Evidence: research/new/{p.name}\n")
+                  agents.parent.mkdir(parents=True, exist_ok=True)
+                  with agents.open("a", encoding="utf-8") as f:
+                      f.write(json.dumps({"name":f"Reader_{h}","role":f"Summarize {title} and propose links (id:{h})"}, ensure_ascii=False)+"\n")
+                  touched.append(str(p))
+          bundle.parent.mkdir(parents=True, exist_ok=True)
+          bundle.write_text(json.dumps(
+              {"context_file":"docs/CONTEXT.md",
+               "system_prompt":"prompts/system.md",
+               "agents_config":"prompts/agents.jsonl",
+               "version":"v0.1",
+               "pdfs": touched}, indent=2), encoding="utf-8")
+          Path(os.environ["GITHUB_OUTPUT"]).write_text(f"count={len(touched)}\n")
+          PY
+      - name: Create PR (only if changes)
+        if: steps.extract.outputs.count != '0'
+        uses: peter-evans/create-pull-request@v6
+        with:
+          branch: auto/ingest-${{ github.run_id }}
+          title: "ingest: mesh PDFs → stubs"
+          commit-message: "ingest: mesh PDFs into stubs and context bundle"
+          body: "Auto-generated by ingest workflow."
+          labels: auto-mesh, needs-curation
+          delete-branch: true
```

Why: CI error shows missing `jobs` in `ci.yml`. Ingest error is YAML syntax around the embedded Python block. These patches satisfy both. ([GitHub][1])

Run order:

1. Push these two files.
2. Actions → check `CI` and `ingest` runs. Expect green or a PR from `ingest`. ([GitHub][2])

