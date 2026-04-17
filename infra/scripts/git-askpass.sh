#!/bin/sh
# Called by git when it needs credentials.
# Echoes $GITHUB_PAT from the environment — no secrets in this file.
echo "$GITHUB_PAT"
