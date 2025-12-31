from pathlib import Path
import os
import subprocess
import sys

# ==================================================
# Google Drive mount helper (Colab-safe)
# ==================================================
def ensure_drive_mounted():
    # Only run on Google Colab
    if "google.colab" not in sys.modules:
        return

    from google.colab import drive
    if not os.path.ismount("/content/drive"):
        drive.mount("/content/drive")

# ==================================================
# Configuration
# ==================================================
REPO_URL = "https://github.com/seoultechpse/fenicsx-colab.git"

ROOT = Path("/content")
REPO_DIR = ROOT / "fenicsx-colab"

INSTALL_SCRIPT = REPO_DIR / "setup" / "install_fenicsx.sh"
MAGIC_FILE     = REPO_DIR / "magic" / "fenicsx_magic.py"
TEST_FILE      = REPO_DIR / "tests" / "test_fenicsx_basic.py"

MICROMAMBA = Path("/content/micromamba/bin/micromamba")

# ==================================================
# Helpers
# ==================================================
def run(cmd, cwd=None):
    print("$", " ".join(map(str, cmd)))
    subprocess.run(cmd, cwd=cwd, check=True)

# ==================================================
# 1. Ensure Google Drive (for cache persistence)
# ==================================================
ensure_drive_mounted()

if not (ROOT / "drive" / "MyDrive").exists():
    print("❌ Google Drive not available.")
    print("This setup requires Google Drive for package cache.")
    sys.exit(1)

# ==================================================
# 2. Clone repository
# ==================================================
if not REPO_DIR.exists():
    print("📥 Cloning repository...")
    run(["git", "clone", REPO_URL, str(REPO_DIR)])
elif not (REPO_DIR / ".git").exists():
    print("❌ Directory exists but is not a git repository:", REPO_DIR)
    sys.exit(1)
else:
    print("📦 Repo already cloned — skipping")

# ==================================================
# 3. Install FEniCSx environment
# ==================================================
opts = sys.argv[1:]   # e.g. --clean
print("🔧 Installing FEniCSx environment...")
run(["bash", str(INSTALL_SCRIPT), *opts], cwd=REPO_DIR)

# ==================================================
# 4. Load %%fenicsx magic
# ==================================================
print("✨ Loading fenicsx Jupyter magic...")
with open(MAGIC_FILE) as f:
    exec(f.read(), globals())

print("🎉 fenicsx ready")

# ==================================================
# 5. Self-test
# ==================================================
print("\n🧪 Running fenicsx self-test...")

run(
    [
        str(MICROMAMBA), "run", "-n", "fenicsx",
        "mpiexec", "-n", "4",
        "python", str(TEST_FILE),
    ],
    cwd=REPO_DIR,
)

print("🧪 fenicsx self-test passed ✅")