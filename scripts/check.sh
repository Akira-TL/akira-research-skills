#!/usr/bin/env bash
set -euo pipefail

REPO="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO"

python -m unittest discover -s skills/research/akira-research/tests
python -m unittest discover -s skills/research/literature/tests

git diff --check
