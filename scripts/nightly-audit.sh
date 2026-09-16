#!/usr/bin/env bash
# nightly-audit.sh — persona forensic_audio_auditor em lote (timer 03:30).
# Para cada caps/capNN.json com UNKNOWNs: attrib-llm.py (router :8080).
# Só auditoria: escreve caps/capNN-llm.json + relatório consolidado.
# Não renderiza, não treina, não edita vivos.
export LD_LIBRARY_PATH=/nix/store/3lpf2hl979sfmyb9f573xq1bz3xkds0v-cuda-merged-12.9/lib:/run/opengl-driver/lib:/nix/store/7vafhlh0lmcvi75jfyy09qwr4m3x1ks3-gcc-15.2.0-lib/lib:/nix/store/483x61iy35irm4wr2b7dwzihljhp6da2-zlib-1.3.2/lib:$LD_LIBRARY_PATH
PY=$HOME/kvenv/bin/python
cd /home/nixos/projects/applio-lab || exit 1
mkdir -p /tmp/audiobook-audit
REP=/tmp/audiobook-audit/nightly-$(date +%F).log
echo "=== nightly audit $(date) ===" > $REP
for F in caps/cap*.json; do
  case "$F" in *-blocking.json|*-relabels.json) continue;; esac
  N=$(basename "$F" .json)
  UNK=$($PY -c "import json; d=json.load(open('$F'))['segments']; print(sum(1 for s in d if s['speaker']=='UNKNOWN'))" 2>/dev/null)
  if [ -n "$UNK" ] && [ "$UNK" -gt 0 ]; then
    echo "== $N: $UNK unknowns" | tee -a $REP
    timeout 1800 $PY scripts/attrib-llm.py "$F" >>$REP 2>&1
  fi
done
echo "=== fim $(date) ===" >> $REP
