#!/usr/bin/env bash
# Fila Kaggle: upload dataset (version/create) + push kernel por personagem.
export LD_LIBRARY_PATH=/run/opengl-driver/lib:/nix/store/7vafhlh0lmcvi75jfyy09qwr4m3x1ks3-gcc-15.2.0-lib/lib:/nix/store/483x61iy35irm4wr2b7dwzihljhp6da2-zlib-1.3.2/lib:$LD_LIBRARY_PATH
K=/home/nixos/kvenv/bin/kaggle
LOG=/tmp/opencode/kaggle-queue.log
for slug in klein dunn neil narrador leonard megose daly alger hood; do
  echo "=== $slug $(date) ===" | tee -a $LOG
  if [ "$slug" = klein ]; then
    $K datasets version -p /tmp/opencode/kaggle-ds/klein -m "v5: ep4-13 pools + v4 merge (265 clips 16.6min)" >>$LOG 2>&1
  else
    $K datasets create -p /tmp/opencode/kaggle-ds/$slug >>$LOG 2>&1 \
      || $K datasets version -p /tmp/opencode/kaggle-ds/$slug -m "update $(date +%F)" >>$LOG 2>&1
  fi
  echo "--- push kernel $slug ---" | tee -a $LOG
  $K kernels push -p /tmp/opencode/kaggle-ky/$slug >>$LOG 2>&1
  sleep 20
done
echo "=== FILA LANCADA $(date) ===" | tee -a $LOG
# vigia: status a cada 15min, baixa output dos COMPLETE
while true; do
  sleep 900
  for slug in klein dunn neil narrador leonard megose daly alger hood; do
    case $slug in klein) ky=kuchiriel/klein-rvc-train;; *) ky=kuchiriel/lotm-$slug-train;; esac
    st=$($K kernels status $ky 2>/dev/null | tail -1)
    echo "$(date +%H:%M) $ky $st" >>$LOG
    if echo "$st" | grep -q COMPLETE; then
      d=/tmp/opencode/kaggle-out/$slug
      if [ ! -f "$d/$slug-best.pth" ] && [ ! -f "$d/klein-best.pth" ]; then
        mkdir -p $d; $K kernels output $ky -p $d >>$LOG 2>&1
        echo "$(date +%H:%M) $slug output baixado: $(ls $d 2>/dev/null | tr '\n' ' ')" >>$LOG
      fi
    fi
  done
done
