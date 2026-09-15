#!/usr/bin/env bash
# LOOP Capítulos Klein-only: parse -> audit -> blocking -> render -> master -> verify.
# Loop virtuoso (dono 15/09): cada cap melhora geração + verificação.
# Uso: ./loop-klein-only.sh   (logs em /tmp/opencode/loop-capNN.log)
export LD_LIBRARY_PATH=/nix/store/3lpf2hl979sfmyb9f573xq1bz3xkds0v-cuda-merged-12.9/lib:/run/opengl-driver/lib:/nix/store/7vafhlh0lmcvi75jfyy09qwr4m3x1ks3-gcc-15.2.0-lib/lib:/nix/store/483x61iy35irm4wr2b7dwzihljhp6da2-zlib-1.3.2/lib:$LD_LIBRARY_PATH
export PATH="$HOME/.nix-profile/bin:/etc/profiles/per-user/nixos/bin:/run/current-system/sw/bin:$PATH"
cd /home/nixos/projects/applio-lab
EPUB="/home/nixos/Books/LotM Vol 1 - Palhaço (Clown).epub"
for N in 02 09 22 25 26 30; do
  LOG=/tmp/opencode/loop-cap$N.log
  echo "=== CAP$N $(date) ===" | tee $LOG
  # 1. parse fresco (regras atuais)
  /tmp/opencode/kvenv/bin/python lotm-audiobook.py parse "$EPUB" --chapter $((10#$N)) --outdir caps >>$LOG 2>&1 || { echo "PARSE FALHOU" | tee -a $LOG; continue; }
  # 2. aplica audit por texto (versão git = texto auditado)
  git -C /home/nixos/projects show HEAD:applio-lab/caps/cap$N.json > /tmp/opencode/cap$N-old.json 2>>$LOG
  /tmp/opencode/kvenv/bin/python scripts/apply-audit.py caps/cap$N.json caps/cap$N-audit.md /tmp/opencode/cap$N-old.json >>$LOG 2>&1
  # 3. blocking (existe p/ 02/09; gera p/ resto)
  [ -f caps/cap$N-blocking.json ] || /tmp/opencode/kvenv/bin/python scripts/blocking-gen.py caps/cap$N.json >>$LOG 2>&1
  # 4. render
  /tmp/opencode/kvenv/bin/python lotm-audiobook.py render caps/cap$N.json --voices personagens/lotm-voices.json --out /home/nixos/Audio/lotm/cap$N-kleinv5.wav >>$LOG 2>&1 || { echo "RENDER FALHOU" | tee -a $LOG; continue; }
  # 5. master binaural
  /tmp/opencode/kvenv/bin/python scripts/master-cap.py /home/nixos/Audio/lotm/cap$N-kleinv5.wav.parts caps/cap$N.json caps/cap$N-blocking.json /home/nixos/Audio/lotm/cap$N-MASTER.wav >>$LOG 2>&1 || echo "MASTER FALHOU" >>$LOG
  # 6. verify-v2 (reporta; correção no próximo giro)
  /tmp/opencode/kvenv/bin/python scripts/verify-v2.py /home/nixos/Audio/lotm/cap$N-kleinv5.wav.parts caps/cap$N.json > /tmp/opencode/verify-cap$N.log 2>&1
  tail -3 /tmp/opencode/verify-cap$N.log >>$LOG
  echo "=== CAP$N FIM $(date) ===" | tee -a $LOG
done
echo "LOOP FIM $(date)" | tee -a /tmp/opencode/loop-caps.log
