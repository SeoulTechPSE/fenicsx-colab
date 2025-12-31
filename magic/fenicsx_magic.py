import os, subprocess, tempfile, textwrap, shlex, time
from pathlib import Path
from IPython.core.magic import register_cell_magic

# ==================================================
# micromamba (ABSOLUTE PATH)
# ==================================================
MICROMAMBA = Path("/content/micromamba/bin/micromamba")

if not MICROMAMBA.exists():
    raise RuntimeError(
        "❌ micromamba not found at /content/micromamba/bin/micromamba\n"
        "Run setup_fenicsx.py first."
    )

# ==================================================
# MPI helpers
# ==================================================
def detect_mpi():
    try:
        out = subprocess.run(
            ["mpiexec", "--version"],
            capture_output=True, text=True, timeout=2
        )
        txt = (out.stdout + out.stderr).lower()
        if "open mpi" in txt:
            return "openmpi"
    except Exception:
        pass
    return "mpich"


def mpi_version():
    try:
        out = subprocess.run(
            ["mpiexec", "--version"],
            capture_output=True, text=True, timeout=2
        )
        return (out.stdout + out.stderr).splitlines()[0]
    except Exception:
        return "unknown"

# ==================================================
# %%fenicsx
# ==================================================
@register_cell_magic
def fenicsx(line, cell):
    args = shlex.split(line)

    np = 1
    info_mode = "--info" in args
    time_mode = "--time" in args

    if "-np" in args:
        np = int(args[args.index("-np") + 1])

    mpi_impl = detect_mpi()
    mpi_ver  = mpi_version()

    # --------------------------------------------------
    # command builder
    # --------------------------------------------------
    def cmd(script):
        if np == 1:
            return [
                str(MICROMAMBA), "run", "-n", "fenicsx",
                "python", script
            ]

        launcher = "mpirun" if mpi_impl == "openmpi" else "mpiexec"
        return [
            str(MICROMAMBA), "run", "-n", "fenicsx",
            launcher, "-n", str(np),
            "python", script
        ]

    # --------------------------------------------------
    # --info
    # --------------------------------------------------
    if info_mode:
        info_code = """
from mpi4py import MPI
import dolfinx, sys, platform, os

comm = MPI.COMM_WORLD
if comm.rank == 0:
    print("🐍 Python         :", sys.version.split()[0])
    print("📦 dolfinx        :", dolfinx.__version__)
    print("💻 Platform       :", platform.platform())
    print("🧵 MPI size       :", comm.size)
"""
        with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as f:
            f.write(info_code)
            script = f.name

        try:
            res = subprocess.run(cmd(script), capture_output=True, text=True)
            print(res.stdout, end="")
            print(res.stderr, end="")
        finally:
            os.remove(script)

        print("\n🔎 fenicsx runtime info")
        print("-----------------------")
        print("Environment       : fenicsx")
        print(f"MPI implementation: {mpi_impl.upper()}")
        print(f"MPI version       : {mpi_ver}")
        print(f"MPI ranks (-np)   : {np}")
        return

    # --------------------------------------------------
    # normal execution
    # --------------------------------------------------
    user_code = textwrap.dedent(cell)

    if time_mode:
        wrapped = f"""
from mpi4py import MPI
import time

_comm = MPI.COMM_WORLD
_t0 = time.perf_counter()

{user_code}

_comm.Barrier()
_t1 = time.perf_counter()

if _comm.rank == 0:
    print(f"⏱ Elapsed time: {{_t1 - _t0:.6f}} s")
"""
    else:
        wrapped = user_code

    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as f:
        f.write(wrapped)
        script = f.name

    try:
        res = subprocess.run(cmd(script), capture_output=True, text=True)
        print(res.stdout, end="")
        print(res.stderr, end="")
    finally:
        os.remove(script)