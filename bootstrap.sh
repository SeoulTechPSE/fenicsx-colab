#!/usr/bin/env bash
set -e

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# --------------------------------------------------
# 1. Install FEniCSx (Drive optional)
# --------------------------------------------------
bash "${REPO_DIR}/setup/install_fenicsx.sh" "$@"

# --------------------------------------------------
# 2. Register %%fenicsx magic in THIS kernel
# --------------------------------------------------
python "${REPO_DIR}/setup_fenicsx.py"

echo "🎉 FEniCSx bootstrap complete"