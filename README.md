# FEniCSx on Google Colab

This repository provides a **reproducible Google Colab setup** for running
**FEniCSx (dolfinx)** with MPI support using `micromamba`.

No local installation is required.

---

## 🚀 Colab Quick Start (1 Cell)

Open a new Google Colab notebook and run **this single cell**:

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
#    Option: add '--clean' to force reinstall
# ------------------------------
USE_CLEAN = False  # <--- Set True to remove existing environment
opts = "--clean" if USE_CLEAN else ""

# Run the setup script
get_ipython().run_line_magic(
    "run", f"{REPO_DIR / 'setup_fenicsx.py'} {opts}"
)

# ==================================================
# 5️⃣ Verify %%fenicsx magic is registered
# ==================================================
try:
    get_ipython().run_cell_magic('fenicsx', '--info -np 4', '')
except Exception as e:
    print("⚠️ %%fenicsx magic not found:", e)
```

After this finishes, the Jupyter cell magic %%fenicsx becomes available.

---

▶ Example

```python
%%fenicsx -np 4 --time

from mpi4py import MPI
import dolfinx

comm = MPI.COMM_WORLD

print(f"Hello from rank {comm.rank}", flush=True)
if comm.rank == 0:
    print(f"  dolfinx : {dolfinx.__version__}")
    print(f"  MPI size: {comm.size}")
```

This will measure elapsed time on rank `0`.

---

### 📦 What This Setup Does

- Installs FEniCSx using micromamba
- Enables MPI execution inside Colab
- Registers a custom Jupyter cell magic %%fenicsx
- Keeps everything reproducible via GitHub

---

### 🔁 Re-running

- Restarting the Colab runtime removes the environment
- Simply re-run the Quick Start cell to restore everything

---

### 🧹 Clean Reinstall (Optional)

To force a clean reinstall of the environment:

```python
%run {REPO_DIR / 'setup_fenicsx.py'} --clean
```
