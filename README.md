# FEniCSx on Google Colab

This repository provides a **reproducible Google Colab setup** for running
**FEniCSx (dolfinx)** with MPI support using `micromamba`.

No local installation is required.

---

## 🚀 Colab Quick Start (1 Cell)

Open a new Google Colab notebook and run **this single cell**:

```python
# FEniCSx on Google Colab (default: DOLFINx 0.11.x)
# SeoulTechPSE/fenicsx-colab + OpenMPI 5.x (PRRTE) slot patch

from google.colab import drive
import os, multiprocessing, subprocess
from pathlib import Path

if not os.path.ismount('/content/drive'):
    drive.mount('/content/drive')
else:
    print('Google Drive already mounted')

REPO_URL = 'https://github.com/seoultechpse/fenicsx-colab.git'
REPO_DIR = Path('/content/fenicsx-colab')
if not REPO_DIR.exists():
    print('Cloning fenicsx-colab...')
    subprocess.run(['git', 'clone', REPO_URL, str(REPO_DIR)], check=True)
else:
    print('Repository already exists')

# OpenMPI 5.x (PRRTE) slot patch
# Colab VM has 2 CPUs; force slots=4 via hostfile (oversubscribe)
N_PROC = 4
with open('/root/hostfile', 'w') as f:
    f.write(f'localhost slots={N_PROC}\n')
os.environ['OMPI_MCA_rmaps_default_mapping_policy'] = 'slot:OVERSUBSCRIBE'
os.environ['PRTE_MCA_rmaps_default_mapping_policy'] = 'slot:OVERSUBSCRIBE'
print(f'MPI: {N_PROC} slots on {multiprocessing.cpu_count()} CPUs (oversubscribe enabled)')

DOLFINX_VERSION = '0.11'   # pin to '0.10' for legacy notebooks not yet migrated
USE_COMPLEX = False
USE_CLEAN   = False
ENV_NAME    = None         # leave None for default 'fenicsx'; set e.g. 'fenicsx010'
                            # to keep a 0.10 environment alongside the 0.11 default

opts = [f'--version {DOLFINX_VERSION}']
if USE_COMPLEX: opts.append('--complex')
if USE_CLEAN:   opts.append('--clean')
if ENV_NAME:    opts.append(f'--env-name {ENV_NAME}')
get_ipython().run_line_magic('run', f"{REPO_DIR / 'setup_fenicsx.py'} {' '.join(opts)}")
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
- **Default:** Installs DOLFINx **0.11** with real PETSc (suitable for most FEM problems)

---

## 🔢 DOLFINx Version Selection

### Default: 0.11 ✅

As of June 2026, conda-forge ships `fenics-dolfinx=0.11.0` for linux-64,
linux-aarch64, macOS-64/arm64 and win-64. This is now the default version
installed by the Quick Start cell:

```python
DOLFINX_VERSION = '0.11'  # default
```

### Pinning to 0.10 (legacy notebooks)

If you have notebooks written against the 0.10.x API that haven't been
migrated yet, pin the version explicitly:

```python
DOLFINX_VERSION = '0.10'
```

### Running 0.10 and 0.11 side by side

By default all environments share the name `fenicsx`, so switching
`DOLFINX_VERSION` and re-running Quick Start will overwrite the existing
environment. To keep both versions installed at once (e.g. while migrating
a course series chapter by chapter), give the older one a distinct name:

```python
DOLFINX_VERSION = '0.10'
ENV_NAME = 'fenicsx010'
```

Then select the environment per-notebook via the `%%fenicsx` magic's
environment option (see `setup_fenicsx.py --help` for the exact flag), or
by re-running Quick Start with `ENV_NAME = None` to switch back to the
default `fenicsx` (0.11) environment.

**Note:** some ecosystem add-ons (e.g. `dolfinx_mpc`) may lag behind the
core `fenics-dolfinx` release on conda-forge. Check their latest available
version before assuming 0.11 compatibility.

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
- Environment type (real/complex) and DOLFINx version persist until you
  change `USE_COMPLEX` or `DOLFINX_VERSION`

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

### Switch Between DOLFINx Versions

**Important:** Use clean reinstall when switching DOLFINx versions within
the same environment name, to avoid a partially-resolved conda environment:

```python
# Move an existing 'fenicsx' env from 0.10 to 0.11
DOLFINX_VERSION = '0.11'
USE_CLEAN = True
```

### Manual Command

Alternatively, run directly:

```python
# Clean install with real PETSc, default version (0.11)
%run {REPO_DIR / 'setup_fenicsx.py'} --clean

# Clean install with complex PETSc, pinned to 0.10
%run {REPO_DIR / 'setup_fenicsx.py'} --complex --clean --version 0.10
```

---

## 🛠️ Advanced Options

### Check Installation

```python
%%fenicsx --info
```

### Parallel Execution

```python
%%fenicsx -np 4  # Run with 4 MPI processes
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

### Verify DOLFINx Version

```python
%%fenicsx

import dolfinx
print(f"DOLFINx version: {dolfinx.__version__}")
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

- **No changes needed** for existing code targeting the same DOLFINx version
- Default behavior is unchanged (real PETSc)
- The old `fenicsx.yml` is no longer used (dynamic generation)
- To use complex PETSc, simply set `USE_COMPLEX = True`

### Upgrading from the 0.10-only setup

- **The default DOLFINx version is now 0.11** (previously hardcoded to 0.10)
- conda-forge has shipped `fenics-dolfinx=0.11.0` since 2026-06-10, so the
  upgrade requires no new channel configuration
- Existing notebooks written against the 0.10 API should either be migrated,
  or pin `DOLFINX_VERSION = '0.10'` explicitly until migration is complete
- `setup_fenicsx.py` must accept and forward a `--version` argument (and
  optionally `--env-name`) to the underlying environment-creation logic for
  this to take effect — if your local copy predates this, update it together
  with this README

---

## 🤝 Contributing

Issues and pull requests are welcome! Please see the issue tracker.

---

## 📄 License

This repository is provided as-is for educational and research purposes.
