#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export PYTHONPATH="$ROOT/src:${PYTHONPATH:-}"
cd "$ROOT"
python3 -m pytest tests "$@"
