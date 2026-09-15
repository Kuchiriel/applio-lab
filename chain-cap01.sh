#!/usr/bin/env bash
# Cadeia de renders cap01 por narrador: espera o attenborough terminar,
# depois rendeza o lenval. Uso: ./chain-cap01.sh
export PATH="$HOME/.nix-profile/bin:/etc/profiles/per-user/nixos/bin:/run/current-system/sw/bin:$PATH"
export LD_LIBRARY_PATH=/nix/store/7vafhlh0lmcvi75jfyy09qwr4m3x1ks3-gcc-15.2.0-lib/lib:$LD_LIBRARY_PATH
LOG=/tmp/opencode/chain-cap01.log
while ! grep -q "^OK:.*cap01-attenborough.wav" /tmp/opencode/cap01-atten.log 2>/dev/null; do
  if ! kill -0 4017886 2>/dev/null; then echo "$(date) atten morreu sem OK, aborto cadeia" >>$LOG; exit 1; fi
  sleep 120
done
echo "$(date) atten OK, lancando lenval" >>$LOG
/tmp/opencode/kvenv/bin/python lotm-audiobook.py render caps/cap01.json \
  --voices personagens/presets/voices-narr-lenval.json \
  --out /home/nixos/Audio/lotm/cap01-lenval.wav >>/tmp/opencode/cap01-lenval.log 2>&1
echo "$(date) lenval fim rc=$?" >>$LOG
