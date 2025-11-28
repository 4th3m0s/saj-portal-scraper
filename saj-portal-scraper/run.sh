#!/bin/bash
echo "Starting run.py Loop..."

scan_interval=$(grep -oP '"scan_interval"\s*:\s*\K[0-9]+' /data/options.json)

python3 /run.py -v

echo "Scan interval is: $scan_interval seconds"

while true; do
    echo "Timestamp: $(date '+%Y-%m-%d %H:%M:%S')"
    python3 /run.py
    echo "Next run is in $scan_interval seconds ..."
    sleep $scan_interval  # alle 5 Minuten
done