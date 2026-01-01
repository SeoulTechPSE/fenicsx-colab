#!/usr/bin/env bash
set -e

# ==================================================
# FEniCSx install script for Google Colab
# - micromamba binary : /content/micromamba/bin
# - package cache     : Google Drive (if mounted)
#                       or local (/content)
# ==================================================

echo "🔧 Installing FEniCSx with micromamba"

# --------------------------------------------------
# 1. Paths 
# --------------------------------------------------
MAMBA_ROOT_PREFIX="/content/micromamba" 
MAMBA_BIN="${MAMBA_ROOT_PREFIX}/bin/micromamba"

ENV_NAME="fenicsx"
YML_FILE="setup/fenicsx.yml"

# --------------------------------------------------
# 2. Package cache (Drive OPTIONAL)
# --------------------------------------------------
echo "📦 Checking package cache location..."

if [ -d "/content/drive/MyDrive" ]; then
  echo "   ✅ Google Drive detected — using persistent cache"
  export MAMBA_PKGS_DIRS="/content/drive/MyDrive/mamba_pkgs"
else
  echo "   ⚠️ Google Drive not mounted — using local cache"
  export MAMBA_PKGS_DIRS="/content/mamba_pkgs"
fi

# --------------------------------------------------
# 3. Create directories
# --------------------------------------------------
mkdir -p "${MAMBA_ROOT_PREFIX}/bin"
mkdir -p "${MAMBA_PKGS_DIRS}"

# --------------------------------------------------
# 4. Install micromamba (idempotent)
# --------------------------------------------------
if [ ! -x "${MAMBA_BIN}" ]; then
  echo "📥 Downloading micromamba..."
  curl -Ls https://micro.mamba.pm/api/micromamba/linux-64/latest \
    | tar -xvj -C "${MAMBA_ROOT_PREFIX}/bin" --strip-components=1 bin/micromamba
  chmod +x "${MAMBA_BIN}"
else
  echo "📦 micromamba already exists"
fi

export MAMBA_ROOT_PREFIX
export MAMBA_PKGS_DIRS

# --------------------------------------------------
# 5. Remove old env (optional: --clean)
# --------------------------------------------------
if [[ "${1:-}" == "--clean" ]]; then
  echo "🧹 Removing existing environment: ${ENV_NAME}"
  "${MAMBA_BIN}" env remove -n "${ENV_NAME}" -y || true
fi

# --------------------------------------------------
# 6. Create / update environment
# --------------------------------------------------
if "${MAMBA_BIN}" env list | grep -q "${ENV_NAME}"; then
  echo "🔁 Updating existing environment: ${ENV_NAME}"
  "${MAMBA_BIN}" env update -n "${ENV_NAME}" -f "${YML_FILE}"
else
  echo "🆕 Creating environment: ${ENV_NAME}"
  "${MAMBA_BIN}" env create -n "${ENV_NAME}" -f "${YML_FILE}"
fi

# --------------------------------------------------
# 7. Summary
# --------------------------------------------------
echo
echo "✅ FEniCSx environment ready"
echo "📦 micromamba : ${MAMBA_BIN}"
echo "📦 env name   : ${ENV_NAME}"
echo "📦 pkg cache  : ${MAMBA_PKGS_DIRS}"
echo