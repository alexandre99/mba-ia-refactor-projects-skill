#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SOURCE="$ROOT/code-smells-project/.codex/skills/refactor-arch"
TARGETS=(
  "$ROOT/ecommerce-api-legacy/.codex/skills/refactor-arch"
  "$ROOT/task-manager-api/.codex/skills/refactor-arch"
)

if [[ ! -f "$SOURCE/SKILL.md" ]]; then
  echo "Canonical skill not found: $SOURCE" >&2
  exit 1
fi

for target in "${TARGETS[@]}"; do
  rm -rf "$target"
  mkdir -p "$(dirname "$target")"
  cp -R "$SOURCE" "$target"
  echo "Synchronized: ${target#$ROOT/}"
done

"$ROOT/scripts/verify-refactor-skill.sh"
