#!/usr/bin/env bash
# Prepara .pth/.index que a fila baixar: copia p/ ~/models/staging/ como
# CANDIDATOS (nunca sobrescreve oficiais). Roda enquanto a fila vive + 1h extra.
LOG=/tmp/opencode/stager.log
mkdir -p /home/nixos/models/staging
END=$(( $(date +%s) + 12*3600 ))
while [ $(date +%s) -lt $END ]; do
  for d in /tmp/opencode/kaggle-out/*/; do
    slug=$(basename $d)
    for f in "$d"*.pth "$d"*.index; do
      [ -f "$f" ] || continue
      dst=/home/nixos/models/staging/$slug-$(basename $f)
      if [ ! -f "$dst" ]; then
        cp "$f" "$dst" && echo "$(date) staged: $dst ($(du -h "$dst" | cut -f1))" >>$LOG
      fi
    done
  done
  sleep 600
done
echo "$(date) stager fim" >>$LOG
