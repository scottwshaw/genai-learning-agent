#!/bin/bash
set -euo pipefail

if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

pip install --quiet --break-system-packages --ignore-installed blinker \
  -r "$CLAUDE_PROJECT_DIR/web/requirements.txt"
