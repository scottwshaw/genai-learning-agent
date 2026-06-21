#!/bin/sh
# Called by git when it needs credentials.
# Git calls this once for username, once for password.
case "$1" in
    Username*) echo "x-access-token" ;;
    *)
        if [ -f /run/secrets/github-pat ]; then
            cat /run/secrets/github-pat
        else
            echo "$GITHUB_PAT"
        fi
        ;;
esac
