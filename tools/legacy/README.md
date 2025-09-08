Moved trivial top-level scripts

This folder contains heuristic-selected, small top-level scripts that were moved
out of the repository root to keep the project root focused on packages and
library code. These moves were performed by `tools/repo/organize_repo.py --apply`.

If you want to restore a file to the repository root, move it back and run the
organizer again.

Files moved:
- model_inspect.py
- run_consciousness_demo.py
- test_complete_transcendence_system.py

This directory is intentionally a holding area; consider converting useful
scripts into `src/` modules or `scripts/` and adding integration tests instead
of leaving them here indefinitely.
