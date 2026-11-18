#!/usr/bin/env bash
# Usage: scripts/pull_models.sh qwen3:4b nomic-embed-text
# Starts each model download in the BACKGROUND and returns immediately. Never block on this.
set -u
mkdir -p .logs .state
command -v ollama >/dev/null 2>&1 || { echo "ollama not installed -> https://ollama.com/download"; exit 1; }
curl -s http://localhost:11434/api/tags >/dev/null 2>&1 || { (nohup ollama serve > .logs/ollama-serve.log 2>&1 &); sleep 4; }
for m in "$@"; do
  if ollama list | awk 'NR>1{print $1}' | grep -qx "$m"; then echo "present: $m"; continue; fi
  log=".logs/pull-${m//[:\/]/_}.log"
  nohup ollama pull "$m" > "$log" 2>&1 &
  echo "$m $! $log" >> .state/pulls.txt
  echo "started in background: $m (log: $log)"
done
