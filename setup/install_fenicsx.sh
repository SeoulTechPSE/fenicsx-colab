#!/usr/bin/env bash
set -e

# ==================================================
# FEniCSx install script for Google Colab
# Supports both real and complex PETSc versions
# ==================================================

# --------------------------------------------------
# Default values
# --------------------------------------------------
PETSC_TYPE="real"  # Default to real for backward compatibility
CLEAN_INSTALL=false

# --------------------------------------------------
# Parse arguments
# --------------------------------------------------
while [[ $# -gt 0 ]]; do
  case $1 in
    --complex)
      PETSC_TYPE="complex"
      shift
      ;;
    --real)
      PETSC_TYPE="real"
      shift
      ;;
    --clean)
      CLEAN_INSTALL=true
      shift
      ;;
    --help|-h)
      echo "Usage: $0 [OPTIONS]"
      echo ""
      echo "Install FEniCSx with micromamba on Google Colab"
      echo ""
      echo "OPTIONS:"
      echo "  --complex           Install complex PETSc version"
      echo "  --real              Install real PETSc version (default)"
      echo "  --clean             Remove existing environment before install"
      echo "  --help              Show this help message"
      echo ""
      echo "EXAMPLES:"
      echo "  $0                  # Install with real PETSc (default)"
      echo "  $0 --complex        # Install with complex PETSc"
      echo "  $0 --clean          # Clean install with real PETSc"
      echo "  $0 --complex --clean # Clean install with complex PETSc"
      echo ""
      echo "NOTES:"
      echo "  - Real PETSc (default): Recommended for most FEM problems"
      echo "  - Complex PETSc: Required for eigenvalue problems, frequency domain analysis"
      echo "  - Package cache automatically uses Google Drive if mounted"
      exit 0
      ;;
    *)
      echo "❌ Unknown option: $1"
      echo "Run '$0 --help' for usage information"
      exit 1
      ;;
  esac
done

# --------------------------------------------------
# Display configuration
# --------------------------------------------------
echo "=============================================="
echo "🔧 FEniCSx Installation Configuration"
echo "=============================================="
echo "PETSc type   : ${PETSC_TYPE}"
echo "Clean install: ${CLEAN_INSTALL}"
echo "=============================================="
echo

# --------------------------------------------------
# Paths
# --------------------------------------------------
MAMBA_ROOT_PREFIX="/content/micromamba"
MAMBA_BIN="${MAMBA_ROOT_PREFIX}/bin/micromamba"
ENV_NAME="fenicsx"

# --------------------------------------------------
# Package cache (Drive OPTIONAL)
# --------------------------------------------------
echo "📦 Checking package cache location..."

if [ -d "/content/drive/MyDrive" ]; then
  echo "   ✅ Google Drive detected — using persistent cache"
  export MAMBA_PKGS_DIRS="/content/drive/MyDrive/mamba_pkgs"
else
  echo "   ⚠️  Google Drive not mounted — using local cache"
  export MAMBA_PKGS_DIRS="/content/mamba_pkgs"
fi

# --------------------------------------------------
# Create directories
# --------------------------------------------------
mkdir -p "${MAMBA_ROOT_PREFIX}/bin"
mkdir -p "${MAMBA_PKGS_DIRS}"

# --------------------------------------------------
# Install micromamba (idempotent)
# [CHANGED] Old method used micro.mamba.pm/api which returned a .tar.bz2 archive
# piped through tar -xvj. That endpoint has become unreliable (truncated downloads).
# New method downloads a single statically-linked binary directly from GitHub Releases.
# --------------------------------------------------
if [ ! -x "${MAMBA_BIN}" ]; then
  echo "📥 Downloading micromamba..."
  curl -fsSL \
    "https://github.com/mamba-org/micromamba-releases/releases/latest/download/micromamba-linux-64" \
    -o "${MAMBA_BIN}"
  chmod +x "${MAMBA_BIN}"
  echo "   ✅ micromamba downloaded successfully"
else
  echo "📦 micromamba already exists"
fi

export MAMBA_ROOT_PREFIX
export MAMBA_PKGS_DIRS

# --------------------------------------------------
# Remove old env if --clean
# --------------------------------------------------
if ${CLEAN_INSTALL}; then
  echo "🧹 Removing existing environment: ${ENV_NAME}"
  "${MAMBA_BIN}" env remove -n "${ENV_NAME}" -y || true
fi

# --------------------------------------------------
# Create environment YAML on-the-fly
# --------------------------------------------------
echo "📝 Generating environment configuration..."

TEMP_YML="/tmp/fenicsx_${PETSC_TYPE}.yml"

if [ "${PETSC_TYPE}" = "complex" ]; then
  PETSC_SPEC="petsc=*=complex*"
else
  PETSC_SPEC="petsc=*=real*"
fi

{
  echo "name: ${ENV_NAME}"
  echo "channels:"
  echo "  - conda-forge"
  echo "dependencies:"
  echo "  - ${PETSC_SPEC}"
  echo "  - slepc"
  echo "  - fenics-dolfinx=0.10"
  echo "  - mpi4py"
  echo "  - scipy"
  echo "  - sympy"
  echo "  - networkx"
  echo "  - vtk"
  echo "  - pyvista>=0.45.0"
  echo "  - python-gmsh"
  echo "  - ipywidgets"
  echo "  - trame"
  echo "  - trame-client"
  echo "  - trame-server"
  echo "  - trame-vtk"
  echo "  - trame-vuetify"
  echo "  - jupyter-book"
  echo "  - jupytext"
  echo "  - sphinx>=6.0.0"
  echo "variables:"
  echo "  PYVISTA_OFF_SCREEN: false"
  echo "  PYVISTA_JUPYTER_BACKEND: \"trame\""
  echo "  LIBGL_ALWAYS_SOFTWARE: 1"
} > "${TEMP_YML}"

echo "✅ Configuration created: ${TEMP_YML}"
echo "   PETSc spec: ${PETSC_SPEC}"
echo

# --------------------------------------------------
# Create / update environment
# --------------------------------------------------
if "${MAMBA_BIN}" env list | grep -q "^${ENV_NAME} "; then
  echo "🔄 Updating existing environment: ${ENV_NAME}"
  "${MAMBA_BIN}" env update -n "${ENV_NAME}" -f "${TEMP_YML}"
else
  echo "🆕 Creating environment: ${ENV_NAME}"
  "${MAMBA_BIN}" env create -n "${ENV_NAME}" -f "${TEMP_YML}"
fi

# --------------------------------------------------
# Verify installation
# --------------------------------------------------
echo
echo "🔍 Verifying installation..."

"${MAMBA_BIN}" run -n "${ENV_NAME}" python -c "
from dolfinx import default_scalar_type
import numpy as np

if np.issubdtype(default_scalar_type, np.complexfloating):
    petsc_type = 'complex'
    scalar_type = 'complex128'
else:
    petsc_type = 'real'
    scalar_type = 'float64'

print(f'✅ Installed PETSc type: {petsc_type}')
print(f'   Scalar type: {scalar_type}')
" || echo "⚠️  Could not verify installation"

# --------------------------------------------------
# Summary
# --------------------------------------------------
echo
echo "=============================================="
echo "✅ FEniCSx environment ready"
echo "=============================================="
echo "📦 micromamba : ${MAMBA_BIN}"
echo "📦 env name   : ${ENV_NAME}"
echo "📦 pkg cache  : ${MAMBA_PKGS_DIRS}"
echo "📦 PETSc type : ${PETSC_TYPE}"
echo
echo "To activate in Python:"
echo "  import sys"
echo "  sys.path.insert(0, '${MAMBA_ROOT_PREFIX}/envs/${ENV_NAME}/lib/python3.11/site-packages')"
echo
echo "Or run commands directly:"
echo "  ${MAMBA_BIN} run -n ${ENV_NAME} python your_script.py"
echo "=============================================="

# Cleanup
rm -f "${TEMP_YML}"
