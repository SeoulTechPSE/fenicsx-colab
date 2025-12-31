# FEniCSx Colab Quick Start

This single cell will set up FEniCSx on Google Colab and
register the `%%fenicsx` Jupyter cell magic.

**Features**

- 🖥 micromamba executable: `/content/micromamba/bin/micromamba` (Colab local)
- 💾 Package cache: Google Drive `/content/drive/MyDrive/mamba_pkgs`
- 🔄 Safe for repeated runs: existing repo/env will be skipped
- 🧹 `--clean` option to force environment reinstallation

---

```python
# --------------------------------------------------
# 1️⃣ Mount Google Drive (for cache)
# --------------------------------------------------
from google.colab import drive, output
import os
if not os.path.ismount("/content/drive"):
    drive.mount("/content/drive")

# --------------------------------------------------

from pathlib import Path
import subprocess, sys

REPO_URL = "https://github.com/seoultechpse/fenicsx-colab.git"
ROOT = Path("/content")
REPO_DIR = ROOT / "fenicsx-colab"

def run(cmd):
    #print("   $", " ".join(map(str, cmd)))
    subprocess.run(cmd, check=True)

# --------------------------------------------------
# 2️⃣ Clone repo (idempotent)
# --------------------------------------------------
if not REPO_DIR.exists():
    print("📥 Cloning fenicsx-colab...")
    run(["git", "clone", REPO_URL, str(REPO_DIR)])
elif not (REPO_DIR / ".git").exists():
    raise RuntimeError("Directory exists but is not a git repository")
else:
    print("📦 Repo already exists — skipping clone")

# --------------------------------------------------
# 3️⃣ Run setup IN THIS KERNEL (CRITICAL)
# --------------------------------------------------
print("🚀 Running setup_fenicsx.py in current kernel")
get_ipython().run_line_magic(
    "run", str(REPO_DIR / "setup_fenicsx.py")
)
```

### Usage Examples

- Displays MPI implementation, Python version, FEniCSx version, and active environment info.

```python
%%fenicsx --info
```

- Runs your FEniCSx code using 4 MPI ranks.

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

### Options

- `--clean` : Remove existing environment and reinstall from scratch.
- `--time` : Measure execution time of the cell.

### Notes

- `micromamba` executable is local (`/content/micromamba/bin/micromamba`)
- Only package cache is stored on Drive (`/content/drive/MyDrive/mamba_pkgs`)
- Avoid placing the `micromamba` executable itself on Drive (permission issues may occur).
