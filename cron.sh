#!/usr/bin/env bash

THIS_DIR=$(cd "$(dirname "$0")" || exit 2; pwd)
PYTHON3=${PYTHON3-"/usr/local/bin/python3"}
TELETYPER=${TELETYPER-"$THIS_DIR/run.py"}

pgrep -f "$TELETYPER" >/dev/null && exit 0

$PYTHON3 "$TELETYPER" --mode bot --lvl error
exit $?
