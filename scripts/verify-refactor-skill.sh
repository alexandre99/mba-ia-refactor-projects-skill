#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SOURCE="$ROOT/code-smells-project/.codex/skills/refactor-arch"
TARGETS=(
  "$ROOT/ecommerce-api-legacy/.codex/skills/refactor-arch"
  "$ROOT/task-manager-api/.codex/skills/refactor-arch"
)

status=0
for target in "${TARGETS[@]}"; do
  if ! diff -ru --exclude='.DS_Store' "$SOURCE" "$target"; then
    echo "Skill copy diverged: ${target#$ROOT/}" >&2
    status=1
  else
    echo "Verified identical: ${target#$ROOT/}"
  fi
done

exit "$status"
