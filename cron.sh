#!/usr/bin/env bash

THIS_DIR=$(cd "$(dirname "$0")" || exit 2; pwd)
PYTHON3=${PYTHON3-"/usr/local/bin/python3"}
TELETYPER=${TELETYPER-"$THIS_DIR/run.py"}

running() {
    pgrep -f "$TELETYPER" >/dev/null && return 0; return 1
}

quitting() {
    if running; then pkill -f "$TELETYPER"; else return 0; fi
    while running; do echo -n "."; sleep 0.125; done
    echo -e "\nbye!"; return 0
}


while getopts ":q" OPTION; do
    case $OPTION in
        q) quitting && exit 0 ;;
        ?) echo "?!?" ;;
    esac
done

if running; then exit 0; fi
$PYTHON3 "$TELETYPER" --mode bot --lvl error
exit $?
