# FEniCSx on Google Colab

This repository provides a **reproducible Google Colab setup** for running
**FEniCSx (dolfinx)** with MPI support using `micromamba`.

No local installation is required.

---

## 🚀 Colab Quick Start (1 Cell)

Open a new Google Colab notebook and run **this single cell**:

```python
# --------------------------------------------------
# 1️⃣ Mount Google Drive (optional, for cache)
# --------------------------------------------------
from google.colab import drive
import os

if not os.path.ismount("/content/drive"):
    drive.mount("/content/drive")
else:
    print("📦 Google Drive already mounted")

# --------------------------------------------------
# 2️⃣ Clone fenicsx-colab repository (idempotent)
# --------------------------------------------------
from pathlib import Path
import subprocess

REPO_URL = "https://github.com/seoultechpse/fenicsx-colab.git"
ROOT = Path("/content")
REPO_DIR = ROOT / "fenicsx-colab"

def run(cmd):
    subprocess.run(cmd, check=True)

if not REPO_DIR.exists():
    print("📥 Cloning fenicsx-colab...")
    run(["git", "clone", REPO_URL, str(REPO_DIR)])
elif not (REPO_DIR / ".git").exists():
    raise RuntimeError("Directory exists but is not a git repository")
else:
    print("📦 Repository already exists — skipping clone")

# --------------------------------------------------
# 3️⃣ Run setup_fenicsx.py IN THIS KERNEL (CRITICAL)
# --------------------------------------------------
print("🚀 Running setup_fenicsx.py in current kernel")

# ⚙️ Configuration
USE_COMPLEX = False  # <--- Set True ONLY if you need complex PETSc
USE_CLEAN = False    # <--- Set True to remove existing environment

# Build options
opts = []
if USE_COMPLEX:
    opts.append("--complex")
if USE_CLEAN:
    opts.append("--clean")

opts_str = " ".join(opts) if opts else ""

get_ipython().run_line_magic(
    "run", f"{REPO_DIR / 'setup_fenicsx.py'} {opts_str}"
)

# --------------------------------------------------
# 4️⃣ Sanity check
# --------------------------------------------------
try:
    get_ipython().run_cell_magic('fenicsx', '--info -np 4', '')
except Exception as e:
    print("⚠️ %%fenicsx magic not found:", e)
```

After this finishes, the Jupyter cell magic `%%fenicsx` becomes available.

---

## ▶ Example Usage

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

## 📦 What This Setup Does

- Installs FEniCSx using `micromamba`
- Enables MPI execution inside Colab
- Registers a custom Jupyter cell magic `%%fenicsx`
- Keeps everything reproducible via GitHub
- **Default:** Installs real PETSc (suitable for most FEM problems)

---

## ⚙️ PETSc Type Selection

### Real PETSc (Default) ✅

**Installed by default** - suitable for most users:

```python
USE_COMPLEX = False  # Default setting
```

**Use for:**

- Standard FEM problems (heat transfer, elasticity, fluid dynamics)
- Nonlinear problems
- Mixed finite element formulations
- Most tutorials and examples

### Complex PETSc

**Explicitly enable** when needed:

```python
USE_COMPLEX = True  # Set this to install complex PETSc
```

**Use for:**

- Eigenvalue problems (modal analysis)
- Frequency domain analysis
- Time-harmonic wave equations
- Electromagnetic simulations

**Note:** Complex PETSc uses 2x memory and has some limitations with mixed formulations.

---

## 🔄 Re-running

- Restarting the Colab runtime removes the environment
- Simply re-run the Quick Start cell to restore everything
- Environment type (real/complex) persists until you change `USE_COMPLEX`

---

## 🧹 Clean Reinstall

### Force Clean Reinstall

```python
USE_CLEAN = True  # Force removal of existing environment
```

### Switch Between Real and Complex

**Important:** Always use clean reinstall when switching PETSc types:

```python
# Switch to complex PETSc
USE_COMPLEX = True
USE_CLEAN = True

# Switch back to real PETSc
USE_COMPLEX = False
USE_CLEAN = True
```

### Manual Command

Alternatively, run directly:

```python
# Clean install with real PETSc
%run {REPO_DIR / 'setup_fenicsx.py'} --clean

# Clean install with complex PETSc
%run {REPO_DIR / 'setup_fenicsx.py'} --complex --clean
```

---

## 🛠️ Advanced Options

### Check Installation

```python
%%fenicsx --info
```

### Parallel Execution

```python
%%fenicsx -np 8  # Run with 8 MPI processes
```

### Timing

```python
%%fenicsx --time  # Measure execution time
```

### Combined Options

```python
%%fenicsx -np 4 --time  # 4 processes with timing
```

---

## 🐛 Troubleshooting

### Compilation Errors

If you encounter JIT compilation errors:

```bash
# Clear FEniCSx cache
!rm -rf ~/.cache/fenics
```

Then reinstall:

```python
USE_CLEAN = True  # Set this and re-run Quick Start
```

### Verify PETSc Type

Check which PETSc type is installed:

```python
%%fenicsx

from dolfinx import default_scalar_type
import numpy as np

if np.issubdtype(default_scalar_type, np.complexfloating):
    print("✅ Complex PETSc (complex128)")
else:
    print("✅ Real PETSc (float64)")
```

### Magic Not Found

If `%%fenicsx` is not recognized:

1. Make sure you ran the setup in **this kernel** (not via `!python`)
2. Check that step 3 used `get_ipython().run_line_magic()`
3. Restart runtime and re-run the Quick Start cell

---

## 📝 Migration Notes

### From Previous Versions

If you're upgrading from an older setup:

- **No changes needed** for existing code
- Default behavior is unchanged (real PETSc)
- The old `fenicsx.yml` is no longer used (dynamic generation)
- To use complex PETSc, simply set `USE_COMPLEX = True`

---

## 🤝 Contributing

Issues and pull requests are welcome! Please see the issue tracker.

---

## 📄 License

This repository is provided as-is for educational and research purposes.
