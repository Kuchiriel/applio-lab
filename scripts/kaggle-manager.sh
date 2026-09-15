#!/usr/bin/env bash
# Gerente da fila Kaggle: mantem ate 2 treinos RUNNING; empurra proximos ao liberar.
export LD_LIBRARY_PATH=/run/opengl-driver/lib:/nix/store/7vafhlh0lmcvi75jfyy09qwr4m3x1ks3-gcc-15.2.0-lib/lib:/nix/store/483x61iy35irm4wr2b7dwzihljhp6da2-zlib-1.3.2/lib:$LD_LIBRARY_PATH
K=/tmp/opencode/kvenv/bin/kaggle
LOG=/tmp/opencode/kaggle-queue.log
ALL="klein dunn neil narrador leonard megose daly alger hood"
kslug() { [ "$1" = klein ] && echo kuchiriel/klein-rvc-train || echo kuchiriel/lotm-$1-train; }
while true; do
  running=0
  for slug in $ALL; do
    st=$($K kernels status $(kslug $slug) 2>/dev/null | tail -1)
    echo "$(date +%H:%M) $(kslug $slug) $st" >>$LOG
    echo "$st" | grep -q RUNNING && running=$((running+1))
    if echo "$st" | grep -q COMPLETE; then
      d=/tmp/opencode/kaggle-out/$slug
      if [ ! -f "$d/$slug-best.pth" ] && [ ! -f "$d/klein-best.pth" ]; then
        mkdir -p $d; $K kernels output $(kslug $slug) -p $d >>$LOG 2>&1
        echo "$(date +%H:%M) $slug output: $(ls $d 2>/dev/null | tr '\n' ' ')" >>$LOG
      fi
    fi
  done
  for slug in neil narrador leonard daly alger klein; do
    [ $running -ge 2 ] && break
    st=$($K kernels status $(kslug $slug) 2>/dev/null | tail -1)
    if echo "$st" | grep -qE "404|Not Found|^$"; then
      echo "$(date +%H:%M) push $slug BLOQUEADO (dono: sem treino novo)" >>$LOG
    fi
  done
  sleep 900
done
