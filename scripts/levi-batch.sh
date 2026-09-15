#!/usr/bin/env bash
# Espera os 2 mp4 do Levi e roda o pipeline (separate->vad->diarize->stt->anchors).
export LD_LIBRARY_PATH=/run/opengl-driver/lib:/nix/store/7vafhlh0lmcvi75jfyy09qwr4m3x1ks3-gcc-15.2.0-lib/lib:/nix/store/483x61iy35irm4wr2b7dwzihljhp6da2-zlib-1.3.2/lib:$LD_LIBRARY_PATH
PY=/tmp/opencode/kvenv/bin/python
PIPE=/home/nixos/projects/applio-lab/lotm-pipeline.py
LOG=/tmp/opencode/levi-batch.log
while [ ! -f /home/nixos/Audio/levi/noregrets-p1.mp4 ] || [ ! -f /home/nixos/Audio/levi/noregrets-p2.mp4 ]; do sleep 120; done
echo "downloads ok $(date)" >>$LOG
for P in p1 p2; do
  D=/home/nixos/Audio/levi/$P
  mkdir -p "$D"
  echo "=== $P inicio $(date) ===" | tee -a "$D/batch.log"
  V=$(find "$D/sep" -name vocals.wav 2>/dev/null | head -1)
  if [ -z "$V" ]; then
    nice -n 10 "$PY" "$PIPE" separate /home/nixos/Audio/levi/noregrets-$P.mp4 --outdir "$D" >> "$D/batch.log" 2>&1 \
      || { echo "=== $P SEPARATE FALHOU ===" | tee -a "$D/batch.log"; continue; }
    V=$(find "$D/sep" -name vocals.wav | head -1)
  fi
  [ -f "$D/segs.json" ] || nice -n 10 "$PY" "$PIPE" vad --vocals "$V" --out "$D/segs.json" >> "$D/batch.log" 2>&1 || continue
  [ -f "$D/diarize.rttm" ] || nice -n 10 "$PY" "$PIPE" diarize --vocals "$V" --out "$D/diarize.rttm" >> "$D/batch.log" 2>&1 || continue
  [ -f "$D/vocals.srt" ] || nice -n 10 "$PY" "$PIPE" stt --vocals "$V" --outdir "$D" >> "$D/batch.log" 2>&1 || continue
  [ -f "$D/auto-labels.json" ] || nice -n 10 "$PY" "$PIPE" anchors --srt "$D/vocals.srt" --rttm "$D/diarize.rttm" --out "$D/auto-labels.json" >> "$D/batch.log" 2>&1 || continue
  echo "=== $P OK $(date) ===" | tee -a "$D/batch.log"
done
echo "LEVI BATCH FIM $(date)" >>$LOG
