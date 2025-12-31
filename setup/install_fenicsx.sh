#!/usr/bin/env bash
set -e

ENV_NAME=fenicsx
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
YML_FILE="$ROOT_DIR/env/fenicsx.yml"

# Drive cache
MAMBA_ROOT_PREFIX=/content/drive/MyDrive/micromamba
export MAMBA_ROOT_PREFIX
export PATH=$MAMBA_ROOT_PREFIX/bin:$PATH
export MAMBA_LOG_LEVEL=error

HASH_FILE=$MAMBA_ROOT_PREFIX/.${ENV_NAME}_yml.hash

# --------------------------------------------------
# Parse options
# --------------------------------------------------
FORCE=false
CLEAN=false

for arg in "$@"; do
  case $arg in
    --force) FORCE=true ;;
    --clean) CLEAN=true ;;
  esac
done

# --------------------------------------------------
# Drive check
# --------------------------------------------------
if [ ! -d /content/drive/MyDrive ]; then
  echo "❌ Google Drive is not mounted"
  exit 1
fi

mkdir -p "$MAMBA_ROOT_PREFIX"

# --------------------------------------------------
# micromamba
# --------------------------------------------------

if [ ! -x "$MAMBA_ROOT_PREFIX/bin/micromamba" ]; then
  echo "🔧 Installing micromamba..."
  mkdir -p "$MAMBA_ROOT_PREFIX/bin"
  wget -qO- https://micromamba.snakepit.net/api/micromamba/linux-64/latest \
    | tar -xvj bin/micromamba
  mv bin/micromamba "$MAMBA_ROOT_PREFIX/bin/"
  chmod +x "$MAMBA_ROOT_PREFIX/bin/micromamba"
fi

# --------------------------------------------------
# Hash
# --------------------------------------------------
NEW_HASH=$(sha256sum "$YML_FILE" | awk '{print $1}')
OLD_HASH=$(cat "$HASH_FILE" 2>/dev/null || echo "")

# --------------------------------------------------
# Clean
# --------------------------------------------------
if $CLEAN; then
  echo "🔥 Cleaning environment"
  rm -rf "$MAMBA_ROOT_PREFIX/envs/$ENV_NAME"
  rm -f "$HASH_FILE"
fi

# --------------------------------------------------
# Exists?
# --------------------------------------------------
ENV_EXISTS=false
if micromamba env list | awk '{print $1}' | grep -qx "$ENV_NAME"; then
  ENV_EXISTS=true
fi

# --------------------------------------------------
# Install
# --------------------------------------------------
if $ENV_EXISTS && [ "$NEW_HASH" = "$OLD_HASH" ] && ! $FORCE; then
  echo "✅ $ENV_NAME is up to date"
else
  echo "🔄 Installing $ENV_NAME"
  $ENV_EXISTS && micromamba remove -n "$ENV_NAME" -y --quiet
  micromamba create -n "$ENV_NAME" -f "$YML_FILE" -y
  echo "$NEW_HASH" > "$HASH_FILE"
  echo "🎉 fenicsx environment ready"
fi