from pathlib import Path
import subprocess, os, sys

# ==================================================
# Repository-relative paths
# ==================================================
REPO_DIR = Path(__file__).resolve().parent

INSTALL_SCRIPT = REPO_DIR / "setup" / "install_fenicsx.sh"
MAGIC_FILE     = REPO_DIR / "magic" / "fenicsx_magic.py"
TEST_FILE      = REPO_DIR / "tests" / "test_fenicsx_basic.py"

MICROMAMBA = "/content/micromamba/bin/micromamba"

# ==================================================
# Helpers
# ==================================================
def run(cmd, cwd=None):
    #print("   $", " ".join(map(str, cmd)))
    result = subprocess.run(cmd, cwd=cwd, check=True)
    print(result.stdout)

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
# 0. Ensure Google Drive (for cache)
# ==================================================
# if "google.colab" in sys.modules:
#     from google.colab import drive
#     if not os.path.ismount("/content/drive"):
#         drive.mount("/content/drive")

if not Path("/content/drive/MyDrive").exists():
    print("❌ Google Drive not available. Required for package cache.")
    sys.exit(1)    

# ==================================================
# 1. Install / update FEniCSx environment
# ==================================================
opts = sys.argv[1:]   # e.g. --clean / --force
print("🔧 Installing FEniCSx environment...")
run(["bash", str(INSTALL_SCRIPT), *opts], cwd=REPO_DIR)

# ==================================================
# 2. Load %%fenicsx magic
# ==================================================
print("✨ Loading FEniCSx Jupyter magic...")
code = MAGIC_FILE.read_text()
exec(compile(code, str(MAGIC_FILE), "exec"), globals())
print("✅ %%fenicsx registered")

# ==================================================
# 3. Optional self-test
# ==================================================
if TEST_FILE.exists():
    print("\n🧪 Running fenicsx self-test...")
    run([
        MICROMAMBA, "run", "-n", "fenicsx",
        "mpiexec", "-n", "4",
        "python", str(TEST_FILE)
    ])
    print("🧪 fenicsx self-test passed ✅")
else:
    print("⚠️ No self-test found — skipping")
