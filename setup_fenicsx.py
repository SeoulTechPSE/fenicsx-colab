from pathlib import Path
import subprocess, os, sys

# ==================================================
# Repository-relative paths
# ==================================================
REPO_DIR = Path(__file__).resolve().parent

INSTALL_SCRIPT = REPO_DIR / "setup" / "install_fenicsx.sh"
MAGIC_FILE     = REPO_DIR / "magic" / "fenicsx_magic.py"

MICROMAMBA = "/content/micromamba/bin/micromamba"

# DOLFINx versions known to be available on conda-forge at the time this
# script was last updated. Kept in sync with install_fenicsx.sh.
KNOWN_VERSIONS = ["0.7", "0.7.3", "0.8", "0.8.0", "0.9", "0.9.0",
                  "0.10", "0.10.0", "0.11", "0.11.0"]
DEFAULT_VERSION = "0.11"
DEFAULT_ENV_NAME = "fenicsx"

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
    """Parse command-line arguments for PETSc type, DOLFINx version,
    environment name, and clean option."""
    petsc_type = "real"  # Default to real for backward compatibility
    clean = False
    dolfinx_version = DEFAULT_VERSION
    env_name = DEFAULT_ENV_NAME

    def split_eq(arg):
        # Supports both "--version=0.11" and a bare flag returning None
        if "=" in arg:
            return arg.split("=", 1)[1]
        return None

    i = 1
    while i < len(sys.argv):
        arg = sys.argv[i]
        if arg == "--complex":
            petsc_type = "complex"
        elif arg == "--real":
            petsc_type = "real"
        elif arg == "--clean":
            clean = True
        elif arg == "--version":
            if i + 1 >= len(sys.argv):
                print("❌ --version requires a value, e.g. --version 0.11")
                sys.exit(1)
            dolfinx_version = sys.argv[i + 1]
            i += 1
        elif arg.startswith("--version="):
            dolfinx_version = split_eq(arg)
        elif arg == "--env-name":
            if i + 1 >= len(sys.argv):
                print("❌ --env-name requires a value, e.g. --env-name fenicsx010")
                sys.exit(1)
            env_name = sys.argv[i + 1]
            i += 1
        elif arg.startswith("--env-name="):
            env_name = split_eq(arg)
        elif arg in ["--help", "-h"]:
            print(f"""
FEniCSx Setup Script

Usage: python setup_fenicsx.py [OPTIONS]

OPTIONS:
  --complex            Install complex PETSc version
  --real               Install real PETSc version (default)
  --clean              Remove existing environment before install
  --version VERSION    DOLFINx version to install (default: {DEFAULT_VERSION})
  --env-name NAME       Conda env name (default: {DEFAULT_ENV_NAME})
  --help, -h            Show this help message

EXAMPLES:
  python setup_fenicsx.py                            # Install {DEFAULT_VERSION}, real PETSc (default)
  python setup_fenicsx.py --complex                   # Install {DEFAULT_VERSION}, complex PETSc
  python setup_fenicsx.py --version 0.10               # Pin to 0.10 (e.g. for legacy notebooks)
  python setup_fenicsx.py --version 0.10 --env-name fenicsx010  # keep 0.10 alongside {DEFAULT_VERSION}
  python setup_fenicsx.py --clean                      # Clean install with default version

NOTES:
  - Real PETSc (default): Recommended for most standard FEM problems
  - Complex PETSc: Required for eigenvalue problems, frequency-domain analysis
  - DOLFINx {DEFAULT_VERSION} is the current default; pass --version 0.10 to pin
    older notebooks that have not yet been migrated
  - Use %%fenicsx magic after setup to run FEniCSx code in Jupyter
""")
            sys.exit(0)
        else:
            print(f"⚠️  Unknown option: {arg}")
            print("Run 'python setup_fenicsx.py --help' for usage information")
        i += 1

    return petsc_type, clean, dolfinx_version, env_name

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
petsc_type, clean_install, dolfinx_version, env_name = parse_args()

if dolfinx_version not in KNOWN_VERSIONS:
    print(f"⚠️  DOLFINx version '{dolfinx_version}' is not in the known list "
          f"({', '.join(KNOWN_VERSIONS)}).")
    print("   Proceeding anyway — conda-forge may have a newer release that")
    print("   this script's KNOWN_VERSIONS list hasn't been updated for yet.")
    print()

# ==================================================
# 0. Display configuration
# ==================================================
print("=" * 70)
print("🔧 FEniCSx Setup Configuration")
print("=" * 70)
print(f"DOLFINx version : {dolfinx_version}")
print(f"PETSc type      : {petsc_type}")
print(f"Env name        : {env_name}")
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
install_args = ["--version", dolfinx_version]
if petsc_type == "complex":
    install_args.append("--complex")
# Note: --real is the default, no need to pass it explicitly

if env_name != DEFAULT_ENV_NAME:
    install_args += ["--env-name", env_name]
# Note: default env name ("fenicsx") needs no explicit flag

if clean_install:
    install_args.append("--clean")

run(["bash", str(INSTALL_SCRIPT)] + install_args, cwd=REPO_DIR)
print()

# ==================================================
# 3. Verify installation
# ==================================================
print("🔍 Verifying installation...")
try:
    result = run([
        MICROMAMBA, "run", "-n", env_name,
        "python", "-c",
        """
import dolfinx
from dolfinx import default_scalar_type
import numpy as np

print(f'✅ Installed: DOLFINx {dolfinx.__version__}')
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
# Must be set BEFORE exec(), since fenicsx_magic.py reads this at load time
# to decide which conda environment %%fenicsx targets.
os.environ["FENICSX_ENV_NAME"] = env_name

print("✨ Loading FEniCSx Jupyter magic...", end=" ")
code = MAGIC_FILE.read_text()
exec(compile(code, str(MAGIC_FILE), "exec"), globals())
print(f"%%fenicsx registered (env: {env_name})")

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
print(f"📌 Note: DOLFINx {dolfinx_version} is installed in env '{env_name}'")
if petsc_type == "complex":
    print("   - Complex PETSc: use for eigenvalue problems, frequency-domain analysis")
    print("   - Some examples may require real PETSc")
else:
    print("   - Real PETSc: recommended for most FEM problems")
    print("   - For complex problems, reinstall with --complex")
print("=" * 70)
