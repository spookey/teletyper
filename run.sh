#!/usr/bin/env bash

THIS_DIR=$(cd "$(dirname "$0")" || exit 2; pwd)
CONFIG=${CONFIG-"$THIS_DIR/conf.sh"}
LOG_FILE=${LOG_FILE-"$THIS_DIR/log/log.log"}
PYTHON3=${PYTHON3-"/usr/local/bin/python3"}
TELETYPER=${TELETYPER-"$THIS_DIR/teletyper.py"}

pgrep -f "$TELETYPER" && exit 0

# shellcheck source=conf.sh
[[ -f "$CONFIG" ]] && . "$CONFIG"

$PYTHON3 "$TELETYPER" \
    --log-file="$LOG_FILE" \
    --telegram-token="$TELEGRAM_TOKEN" \
    --tumblr-consumer-key="$TUMBLR_CONSUMER_KEY" \
    --tumblr-consumer-secret="$TUMBLR_CONSUMER_SECRET" \
    --tumblr-oauth-token="$TUMBLR_OAUTH_TOKEN" \
    --tumblr-oauth-secret="$TUMBLR_OAUTH_SECRET" \
    --tumblr-blog-name="$TUMBLR_BLOG_NAME" \
    --tumblr-blog-state="$TUMBLR_BLOG_STATE" \

exit $?
