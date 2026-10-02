#!/usr/bin/env bash
# guarded.sh <logfile> <cmd...>
# setsid + nice; if MemAvailable < MIN_AVAIL_MB (default 4000) kill the whole process tree,
# wait for RAM to recover (> RESUME_MB, default 6000) and retry (up to RETRIES, default 3).
log="$1"; shift; MIN=${MIN_AVAIL_MB:-4000}; RES=${RESUME_MB:-6000}; TRIES=${RETRIES:-3}; s=$(date +%s)
avail() { awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo; }
tree() { local p; for p in $(ps -o pid= --ppid "$1" 2>/dev/null); do tree "$p"; done; echo "$1"; }
: > "$log"; n=0
while :; do
  n=$((n+1)); killed=0
  setsid nice -n 10 "$@" >> "$log" 2>&1 & pid=$!
  while kill -0 $pid 2>/dev/null; do
    if [ "$(avail)" -lt "$MIN" ]; then
      echo "WATCHDOG kill (attempt $n): MemAvailable=$(avail)MB" >> "$log"
      pids=$(tree $pid); kill -TERM $pids 2>/dev/null; sleep 5; kill -KILL $pids 2>/dev/null; killed=1; break
    fi
    sleep 3
  done
  wait $pid; rc=$?
  [ $killed = 0 ] && break
  [ $n -ge $TRIES ] && { rc=137; break; }
  while [ "$(avail)" -lt "$RES" ]; do sleep 15; done
  echo "WATCHDOG retry $((n+1))" >> "$log"
done
echo "GUARDED_EXIT rc=$rc t=$(( $(date +%s)-s ))s" > "$log.exit"; exit $rc
