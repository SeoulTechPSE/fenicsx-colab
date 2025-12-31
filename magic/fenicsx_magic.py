# ==================================================
# fenicsx_magic.py 
# ==================================================

import os, subprocess, tempfile, textwrap, shlex
from IPython.core.magic import register_cell_magic

# --------------------------------------------------
# Hard-coded micromamba path (NO PATH DEPENDENCY)
# --------------------------------------------------
MICROMAMBA = "/content/micromamba/bin/micromamba"
ENV_NAME = "fenicsx"

# --------------------------------------------------
# MPI detection helpers
# --------------------------------------------------
def detect_mpi(env):
    try:
        out = subprocess.run(
            ["mpiexec", "--version"],
            env=env, capture_output=True, text=True, timeout=2
        )
        txt = (out.stdout + out.stderr).lower()
        if "open mpi" in txt or "open-mpi" in txt:
            return "openmpi"
    except Exception:
        pass
    return "mpich"

def mpi_version(env):
    try:
        out = subprocess.run(
            ["mpiexec", "--version"],
            env=env, capture_output=True, text=True, timeout=2
        )
        return (out.stdout + out.stderr).splitlines()[0]
    except Exception:
        return "unknown"


# --------------------------------------------------
# %%fenicsx cell magic
# --------------------------------------------------
@register_cell_magic
def fenicsx(line, cell):
    args = shlex.split(line)

    # -----------------------------
    # Options
    # -----------------------------
    np = 1
    info_mode = "--info" in args
    time_mode = "--time" in args

    if "-np" in args:
        np = int(args[args.index("-np") + 1])

    # -----------------------------
    # Environment
    # -----------------------------
    env = os.environ.copy()
    env.update({
        "OMPI_ALLOW_RUN_AS_ROOT": "1",
        "OMPI_ALLOW_RUN_AS_ROOT_CONFIRM": "1",
    })

    mpi_impl = detect_mpi(env)
    mpi_ver  = mpi_version(env)

    # -----------------------------
    # Command builder
    # -----------------------------
    def build_cmd(script):
        if np == 1:
            return [
                MICROMAMBA, "run", "-n", ENV_NAME,
                "python", script
            ]

        launcher = "mpirun" if mpi_impl == "openmpi" else "mpiexec"
        return [
            MICROMAMBA, "run", "-n", ENV_NAME,
            launcher, "-n", str(np),
            "python", script
        ]

    # -----------------------------
    # --info mode
    # -----------------------------
    if info_mode:
        info_code = """
from mpi4py import MPI
import dolfinx, sys, platform, os

comm = MPI.COMM_WORLD
if comm.rank == 0:
    print("🐍 Python          :", sys.version.split()[0])
    print("📦 dolfinx         :", dolfinx.__version__)
    print("💻 Platform        :", platform.platform())
    print("🧵 Running as root :", os.geteuid() == 0)
"""
        with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as f:
            f.write(info_code)
            script = f.name

        try:
            res = subprocess.run(
                build_cmd(script),
                env=env, capture_output=True, text=True
            )
            print(res.stdout, end="")
            print(res.stderr, end="")
        finally:
            os.remove(script)

        print("\n🔎 fenicsx runtime info")
        print("-----------------------")
        print(f"Environment        : {ENV_NAME}")
        print(f"micromamba         : {MICROMAMBA}")
        print(f"MPI implementation : {mpi_impl.upper()}")
        print(f"MPI version        : {mpi_ver}")
        print(f"MPI ranks (-np)    : {np}")
        return

    # -----------------------------
    # Normal execution (with optional timing)
    # -----------------------------
    user_code = textwrap.dedent(cell)

    if time_mode:
        wrapped = f"""
from mpi4py import MPI
import time

_comm = MPI.COMM_WORLD
_rank = _comm.rank
_size = _comm.size

# -----------------
# synchronize before timing
# -----------------
_comm.Barrier()
_t0 = time.perf_counter()

# -----------------
# User code
# -----------------
{user_code}

# -----------------
# synchronize after user code
# -----------------
_comm.Barrier()
_t1 = time.perf_counter()

# -----------------
# elapsed time only on rank 0
# -----------------
if _rank == 0:
    print(f"⏱ Elapsed time: {{_t1 - _t0:.6f}} s")
"""
    else:
        wrapped = user_code

    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as f:
        f.write(wrapped)
        script = f.name

    try:
        res = subprocess.run(
            build_cmd(script),
            env=env, capture_output=True, text=True
        )
        print(res.stdout, end="")
        print(res.stderr, end="")
    finally:
        os.remove(script)