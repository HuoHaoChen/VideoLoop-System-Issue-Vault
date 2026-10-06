#!/bin/sh
# SIFE watcher launcher — bounded log growth, no admin required.
# Responsibilities (nothing else):
#   1. anti hot-loop guard: launchd KeepAlive can respawn instantly on failure
#   2. bound /tmp/sife-watcher.err so it can never grow without limit
#      while PRESERVING the most recent lines, so a NEW distinct error is never swallowed
#   3. exec the real watcher with the canonical arguments
set -u

SIFE_HOME="/Users/huohaochen/Desktop/Project/系统问题反馈引擎"
ERR_LOG="/tmp/sife-watcher.err"
STAMP="/tmp/sife-watcher.lastrun"
MAX_BYTES=$((5 * 1024 * 1024))   # 5 MiB ceiling
KEEP_LINES=2000                  # newest lines retained on rotation
MIN_INTERVAL=60                  # seconds; prevents launchd restart storms

# 1) anti hot-loop guard
now=$(date +%s)
if [ -f "$STAMP" ]; then
  last=$(cat "$STAMP" 2>/dev/null || echo 0)
  case "$last" in ''|*[!0-9]*) last=0 ;; esac
  delta=$((now - last))
  if [ "$delta" -ge 0 ] && [ "$delta" -lt "$MIN_INTERVAL" ]; then
    sleep $((MIN_INTERVAL - delta))
  fi
fi
date +%s > "$STAMP" 2>/dev/null || true

# 2) bounded log: keep a bounded tail, never truncate to nothing
if [ -f "$ERR_LOG" ]; then
  size=$(wc -c < "$ERR_LOG" 2>/dev/null || echo 0)
  case "$size" in ''|*[!0-9]*) size=0 ;; esac
  if [ "$size" -gt "$MAX_BYTES" ]; then
    if tail -n "$KEEP_LINES" "$ERR_LOG" > "$ERR_LOG.rot" 2>/dev/null; then
      mv "$ERR_LOG.rot" "$ERR_LOG" 2>/dev/null || rm -f "$ERR_LOG.rot"
    fi
  fi
fi

# 3) exec the real watcher (business semantics unchanged)
exec /usr/bin/python3 "$SIFE_HOME/scripts/watcher.py" --scan --verify --since 3
