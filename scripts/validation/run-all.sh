#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

scripts=(
  "$ROOT_DIR/scripts/validation/validate-code-smells.sh"
  "$ROOT_DIR/scripts/validation/validate-ecommerce-legacy.sh"
  "$ROOT_DIR/scripts/validation/validate-task-manager.sh"
)

for script in "${scripts[@]}"; do
  if [[ ! -f "$script" ]]; then
    echo "validation script missing: $script" >&2
    exit 1
  fi
  echo "==> Running $(basename "$script")"
  bash "$script"
done
