# Repository Structure and Cleanup Plan

This project accumulated many top-level files over time (experiments, demos, reports). To reduce clutter, we follow these conventions:

- src/ — library code and reusable modules.
- tests/ — automated tests and stress/validation scripts.
- examples/ — runnable demos and quickstarts (e.g. run_consciousness_demo.py).
- scripts/ — CLI tools, operators, and helpers (e.g. model_inspect.py, qrft_chat.py).
- docs/ — documentation, design notes, and markdown reports.
- experiments/ and research/ — exploratory work, notebooks, and results.
- artifacts/ — generated reports and outputs (ignored in VCS).
- tools/, ops/, config/, prompts/, benchmarks/, demo/, spec/ — as named.

Use the helper script to preview suggested moves without changing anything:

    python3 scripts/inventory_root.py

Apply the moves (review first):

    python3 scripts/inventory_root.py --apply

This uses `git mv` so history is preserved. After applying, run tests and update any README snippets that reference moved paths.
