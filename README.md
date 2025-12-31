# FEniCSx Colab Quick Start

This single cell will:

1. Mount Google Drive (for package cache)
2. Clone the FEniCSx Colab repository (idempotent)
3. Install the FEniCSx environment via micromamba
4. Register the `%%fenicsx` Jupyter cell magic
5. Optionally run self-test

---

```python
# --------------------------------------------------
# 1️⃣ Mount Google Drive (for cache)
# --------------------------------------------------
from google.colab import drive, output
import os
if not os.path.ismount("/content/drive"):
    drive.mount("/content/drive")

# ==================================================
# 2️⃣ Repo & paths
# ==================================================
from pathlib import Path
import subprocess, sys

REPO_URL = "https://github.com/seoultechpse/fenicsx-colab.git"
ROOT = Path("/content")
REPO_DIR = ROOT / "fenicsx-colab"

def run(cmd):
    #print("   $", " ".join(map(str, cmd)))
    subprocess.run(cmd, check=True)

# --------------------------------------------------
# 3️⃣ Clone repository (idempotent)
# --------------------------------------------------
if not REPO_DIR.exists():
    print("📥 Cloning fenicsx-colab...")
    run(["git", "clone", REPO_URL, str(REPO_DIR)])
elif not (REPO_DIR / ".git").exists():
    raise RuntimeError("Directory exists but is not a git repository")
else:
    print("📦 Repo already exists — skipping clone")

# --------------------------------------------------
# 4️⃣ Run setup in current kernel
# --------------------------------------------------
print("🚀 Running setup_fenicsx.py in current kernel")

# ------------------------------
# Option: add '--clean' to force reinstall
# ------------------------------
USE_CLEAN = False  # <=== Set True to remove existing environment
opts = "--clean" if USE_CLEAN else ""

# Run the setup script
get_ipython().run_line_magic(
    "run", f"{REPO_DIR / 'setup_fenicsx.py'} {opts}"
)

# ==================================================
# 5️⃣ Verify %%fenicsx magic is registered
# ==================================================
try:
    get_ipython().run_cell_magic('fenicsx', '--info', '')
except Exception as e:
    print("⚠️ %%fenicsx magic not found:", e)
```

## Notes

1. Goolge Drive cache

- Initial mount required; repeated runs are safe

2. --clean

- Set `USE_CLEAN = True` to remove existing FEniCSx environment and reinstall
- Default `False` preserves the environment and is faster

3. Cell magic

- After setup, you can use `%%fenicsx` in Colab for parallel MPI computations
- Options:
  - `-np N` → number of MPI ranks
  - `--time` → measure elapsed time

### Example usage:

```python
%%fenicsx -np 4 --time

from mpi4py import MPI
import dolfinx

comm = MPI.COMM_WORLD

if comm.rank == 0:
    print(f"Hello from rank {comm.rank}")
    print("  dolfinx :", dolfinx.__version__)
    print("  MPI size:", MPI.COMM_WORLD.size)
else:
    print(f"Hello from rank {comm.rank}")
```

This will print the rank output in order and measure elapsed time on rank 0.
