#!/usr/bin/env bash
# LOTM batch ep4-ep13: separate -> vad -> diarize -> stt -> anchors
# Log por episodio em ~/Audio/lotm/epN/batch.log. Continua no proximo ep se um falhar.
export LD_LIBRARY_PATH=/run/opengl-driver/lib:/nix/store/7vafhlh0lmcvi75jfyy09qwr4m3x1ks3-gcc-15.2.0-lib/lib:/nix/store/483x61iy35irm4wr2b7dwzihljhp6da2-zlib-1.3.2/lib:$LD_LIBRARY_PATH
PY=/home/nixos/kvenv/bin/python
PIPE=/home/nixos/projects/applio-lab/lotm-pipeline.py

for N in 4 5 6 7 8 9 10 11 12 13; do
  D=/home/nixos/Audio/lotm/ep$N
  mkdir -p "$D"
  echo "=== EP$N inicio $(date) ===" | tee -a "$D/batch.log"
  V=$(find "$D/sep" -name vocals.wav 2>/dev/null | head -1)
  if [ -z "$V" ]; then
    nice -n 10 "$PY" "$PIPE" separate /home/nixos/models/ep$N.mp4 --outdir "$D" >> "$D/batch.log" 2>&1 \
      || { echo "=== EP$N SEPARATE FALHOU $(date) ===" | tee -a "$D/batch.log"; continue; }
    V=$(find "$D/sep" -name vocals.wav | head -1)
  else
    echo "EP$N separate ja feito, pulando" | tee -a "$D/batch.log"
  fi
  if [ -z "$V" ]; then echo "=== EP$N sem vocals.wav, SKIP ===" | tee -a "$D/batch.log"; continue; fi
  echo "EP$N vocals=$V" | tee -a "$D/batch.log"
  [ -f "$D/segs.json" ] || nice -n 10 "$PY" "$PIPE" vad --vocals "$V" --out "$D/segs.json" >> "$D/batch.log" 2>&1 \
    || { echo "=== EP$N VAD FALHOU ===" | tee -a "$D/batch.log"; continue; }
  [ -f "$D/diarize.rttm" ] || nice -n 10 "$PY" "$PIPE" diarize --vocals "$V" --out "$D/diarize.rttm" >> "$D/batch.log" 2>&1 \
    || { echo "=== EP$N DIARIZE FALHOU ===" | tee -a "$D/batch.log"; continue; }
  [ -f "$D/vocals.srt" ] || nice -n 10 "$PY" "$PIPE" stt --vocals "$V" --outdir "$D" >> "$D/batch.log" 2>&1 \
    || { echo "=== EP$N STT FALHOU ===" | tee -a "$D/batch.log"; continue; }
  [ -f "$D/auto-labels.json" ] || nice -n 10 "$PY" "$PIPE" anchors --srt "$D/vocals.srt" --rttm "$D/diarize.rttm" --out "$D/auto-labels.json" >> "$D/batch.log" 2>&1 \
    || { echo "=== EP$N ANCHORS FALHOU ===" | tee -a "$D/batch.log"; continue; }
  echo "=== EP$N OK $(date) ===" | tee -a "$D/batch.log"
done
echo "=== BATCH FIM $(date) ==="
