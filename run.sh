#!/usr/bin/env bash
# Convenience wrapper to run UGC Factory without manually activating venv
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ ! -d "$DIR/.venv" ]; then
    echo "❌ Virtualenv not found. Run ./setup.sh first."
    exit 1
fi

source "$DIR/.venv/bin/activate"
exec ugc "$@"
