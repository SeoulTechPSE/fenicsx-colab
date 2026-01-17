from pathlib import Path
import subprocess, os, sys

# ==================================================
# Repository-relative paths
# ==================================================
REPO_DIR = Path(__file__).resolve().parent

INSTALL_SCRIPT = REPO_DIR / "setup" / "install_fenicsx.sh"
MAGIC_FILE     = REPO_DIR / "magic" / "fenicsx_magic.py"

MICROMAMBA = "/content/micromamba/bin/micromamba"

# ==================================================
# Helpers
# ==================================================
def run(cmd, cwd=None):
    result = subprocess.run(
        cmd, 
        cwd=cwd, 
        check=True,
        capture_output=True,
        text=True
    )
    return result

# ==================================================
# Parse arguments
# ==================================================
def parse_args():
    """Parse command-line arguments for PETSc type and clean option"""
    petsc_type = "real"  # Default to real for backward compatibility
    clean = False
    
    i = 1
    while i < len(sys.argv):
        arg = sys.argv[i]
        if arg == "--complex":
            petsc_type = "complex"
        elif arg == "--real":
            petsc_type = "real"
        elif arg == "--clean":
            clean = True
        elif arg in ["--help", "-h"]:
            print("""
FEniCSx Setup Script

Usage: python setup_fenicsx.py [OPTIONS]

OPTIONS:
  --complex           Install complex PETSc version
  --real              Install real PETSc version (default)
  --clean             Remove existing environment before install
  --help, -h          Show this help message

EXAMPLES:
  python setup_fenicsx.py                 # Install with real PETSc (default)
  python setup_fenicsx.py --complex       # Install with complex PETSc
  python setup_fenicsx.py --clean         # Clean install with real PETSc
  python setup_fenicsx.py --complex --clean  # Clean install with complex PETSc

NOTES:
  - Real PETSc (default): Recommended for most standard FEM problems
  - Complex PETSc: Required for eigenvalue problems, frequency-domain analysis
  - Use %%fenicsx magic after setup to run FEniCSx code in Jupyter
""")
            sys.exit(0)
        else:
            print(f"⚠️  Unknown option: {arg}")
            print("Run 'python setup_fenicsx.py --help' for usage information")
        i += 1
    
    return petsc_type, clean

# ==================================================
# Sanity checks
# ==================================================
if not INSTALL_SCRIPT.exists():
    print("❌ install_fenicsx.sh not found:", INSTALL_SCRIPT)
    sys.exit(1)

if not MAGIC_FILE.exists():
    print("❌ fenicsx_magic.py not found:", MAGIC_FILE)
    sys.exit(1)

# ==================================================
# Parse command-line arguments
# ==================================================
petsc_type, clean_install = parse_args()

# ==================================================
# 0. Display configuration
# ==================================================
print("=" * 70)
print("🔧 FEniCSx Setup Configuration")
print("=" * 70)
print(f"PETSc type      : {petsc_type}")
print(f"Clean install   : {clean_install}")
print("=" * 70)
print()

# ==================================================
# 1. Check Google Drive (for cache)
# ==================================================
USE_DRIVE_CACHE = False

if Path("/content/drive/MyDrive").exists():
    print("📦 Google Drive detected — using persistent cache")
    USE_DRIVE_CACHE = True
else:
    print("⚠️  Google Drive not mounted — using local cache (/content)")

print()
  
# ==================================================
# 2. Install / update FEniCSx environment
# ==================================================
print("🔧 Installing FEniCSx environment...")

# Build install script arguments
install_args = []
if petsc_type == "complex":
    install_args.append("--complex")
# Note: --real is the default, no need to pass it explicitly

if clean_install:
    install_args.append("--clean")

run(["bash", str(INSTALL_SCRIPT)] + install_args, cwd=REPO_DIR)
print()

# ==================================================
# 3. Verify installation
# ==================================================
print("🔍 Verifying PETSc type...")
try:
    result = run([
        MICROMAMBA, "run", "-n", "fenicsx",
        "python", "-c",
        """
from dolfinx import default_scalar_type
import numpy as np

if np.issubdtype(default_scalar_type, np.complexfloating):
    print('✅ Installed: Complex PETSc (complex128)')
else:
    print('✅ Installed: Real PETSc (float64)')
"""
    ])
    print(result.stdout.strip())
except Exception as e:
    print(f"⚠️  Could not verify installation: {e}")

print()

# ==================================================
# 4. Load %%fenicsx magic
# ==================================================
print("✨ Loading FEniCSx Jupyter magic...", end=" ")
code = MAGIC_FILE.read_text()
exec(compile(code, str(MAGIC_FILE), "exec"), globals())
print("%%fenicsx registered")

print()
print("=" * 70)
print("✅ FEniCSx setup complete!")
print("=" * 70)
print()
print("Next steps:")
print("  1. Run %%fenicsx --info to verify installation")
print("  2. Use %%fenicsx in cells to run FEniCSx code")
print("  3. Use -np N for parallel execution (e.g., %%fenicsx -np 4)")
print()
if petsc_type == "complex":
    print("📌 Note: Complex PETSc is installed")
    print("   - Use for eigenvalue problems, frequency-domain analysis")
    print("   - Some examples may require real PETSc")
else:
    print("📌 Note: Real PETSc is installed")
    print("   - Recommended for most FEM problems")
    print("   - For complex problems, reinstall with --complex")
print("=" * 70)