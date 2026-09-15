#!/usr/bin/env bash
# A/B narrador: mesma base Edge-Antonio -> Lenval vs Attenborough (CPU, pitch 0, index 0.0).
export PATH="$HOME/.nix-profile/bin:/etc/profiles/per-user/nixos/bin:/run/current-system/sw/bin:$PATH"
LOG=/tmp/opencode/ab-narrador.log
TXT="Este é o mundo dos Beyonders. Ao beber certas poções, humanos comuns podem obter os poderes dos Beyonders. Eles se tornam capazes de acender a divindade."
BASE=$(jarvis speak "$TXT" --no-play 2>>$LOG | tail -1)
echo "base=$BASE" | tee -a $LOG
[ -f "$BASE" ] || { echo "FALHA base TTS" | tee -a $LOG; exit 1; }
OUT=/home/nixos/Audio/lotm/testes-timbre
mkdir -p $OUT
code="import sys; from jarvis.core.voice_clone import clone_many;"
code="$code print(clone_many([('$BASE','$OUT/narr-lenval.wav')], cpu_only=True, model_path='/home/nixos/models/candidates/LenvalBrown50m300e.pth', index_path=None, timeout_s=1800, pitch=None, index_rate=0.0));"
code="$code print(clone_many([('$BASE','$OUT/narr-attenborough.wav')], cpu_only=True, model_path='/home/nixos/models/candidates/DavidAttenborough.pth', index_path=None, timeout_s=1800, pitch=None, index_rate=0.0))"
nix develop --command python3 -c "$code" >>$LOG 2>&1
echo "AB fim $(date): $(ls -lh $OUT/narr-*.wav 2>/dev/null)" | tee -a $LOG
