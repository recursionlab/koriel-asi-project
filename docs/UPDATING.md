# Applying `manifesto/updates`

Place pending materials under `manifesto/updates/` with one of:

* `*.patch` or `*.diff` — unified diffs applied via `git apply`.
* `files/` — mirrored into repo root.
* `workflows/` — copied to `.github/workflows/`.
* `requirements/`, `docs/`, `scripts/`, `src/`, `tests/` — copied into matching trees.
* Optional `manifest.json`:
  ```json
  { "copies": [ {"src": "manifesto/updates/files/README.md", "dst": "README.md"} ] }
  ```

Commands:
```bash
make apply-updates         # apply + quick checks
