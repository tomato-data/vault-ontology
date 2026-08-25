#!/bin/bash
cd "$(dirname "$0")"
for M in "BAAI/bge-m3" "nlpai-lab/KURE-v1" \
         "Snowflake/snowflake-arctic-embed-l-v2.0" "dragonkue/snowflake-arctic-embed-l-v2.0-ko"; do
  SLUG=$(echo "$M" | tr '/' '_')
  echo "=== START $M $(date +%H:%M:%S) ==="
  ./.venv/bin/python embed.py "$M" chunks.json vecs > "prog_$SLUG.log" 2>&1 && echo "=== DONE $M $(date +%H:%M:%S) ===" || echo "=== FAIL $M ==="
done
echo "=== ALL DONE $(date +%H:%M:%S) ==="
