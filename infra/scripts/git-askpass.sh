#!/bin/sh
# Called by git when it needs credentials.
# Reads from mounted secret file, falls back to env var.
if [ -f /run/secrets/github-pat ]; then
    cat /run/secrets/github-pat
else
    echo "$GITHUB_PAT"
fi
