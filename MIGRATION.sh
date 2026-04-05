#!/bin/bash
# MIGRATION.sh - Temporary rsync during ultra-skills build
#
# Purpose: This script copies the ultra-skills content from the original repo
# (~/src/agentic-peer-review-repo/ultra-skills/) to the standalone repo
# (~/src/ultra-skills/) during the build/stabilization phase.
#
# Status: TEMPORARY. The source repo is still the system of record for development.
# Once the build is complete and all tests pass, we will finalize ownership
# and remove symlinks pointing to the old location.
#
# After the build is done, we'll:
#  1. Verify all skills pass their verification gates
#  2. Update ~/.claude/skills symlinks to point here instead
#  3. Archive or deprecate the agentic-peer-review-repo copy
#
# Usage:
#   bash MIGRATION.sh
#
# This should be run from the ultra-skills repo root.

set -e

SOURCE="${HOME}/src/agentic-peer-review-repo/ultra-skills/"
DEST="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ ! -d "$SOURCE" ]; then
    echo "Error: Source directory not found: $SOURCE"
    exit 1
fi

if [ ! -d "$DEST/.git" ]; then
    echo "Error: Destination is not a git repo: $DEST"
    exit 1
fi

echo "Rsyncing ultra-skills content..."
echo "  FROM: $SOURCE"
echo "  TO:   $DEST"
echo ""

# Sync everything except .git and MIGRATION.sh
# (we own those locally, don't sync them from source)
rsync -av --delete \
    --exclude='.git' \
    --exclude='.gitignore' \
    --exclude='MIGRATION.sh' \
    "$SOURCE" "$DEST"

echo ""
echo "✓ Rsync complete."
echo ""
echo "NOTE: This is a temporary copy during the build phase."
echo "      Source of truth is still: $SOURCE"
echo "      Once build is complete, we'll finalize the move."
