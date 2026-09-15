#!/usr/bin/env bash
# Teste jovialidade Klein v2: mesma frase, base antonio x kokoro-pm_santa, RVC p+2/i0.0.
export PATH="$HOME/.nix-profile/bin:/etc/profiles/per-user/nixos/bin:/run/current-system/sw/bin:$PATH"
export LD_LIBRARY_PATH=/run/opengl-driver/lib:/nix/store/7vafhlh0lmcvi75jfyy09qwr4m3x1ks3-gcc-15.2.0-lib/lib:$LD_LIBRARY_PATH
LOG=/tmp/opencode/young-test.log
OUT=/home/nixos/Audio/lotm/testes-timbre
mkdir -p $OUT
TXT="Eu sou Klein Moretti. Todos morrerão, inclusive eu. Mas hoje, vou tentar viver."
/tmp/opencode/kvenv/bin/edge-tts --voice pt-BR-AntonioNeural --text "$TXT" --write-media /tmp/young-base.mp3 >>$LOG 2>&1
ffmpeg -y -v error -i /tmp/young-base.mp3 -ar 44100 -ac 1 $OUT/young-base-antonio.wav >>$LOG 2>&1
jarvis speak "$TXT" --base kokoro --voice pm_santa --no-play >>$LOG 2>&1 | tail -1 > /tmp/young-santa-path.txt
SB=$(cat /tmp/young-santa-path.txt | tail -1)
ffmpeg -y -v error -i "$SB" -ar 44100 -ac 1 $OUT/young-base-santa.wav >>$LOG 2>&1
code="from jarvis.core.voice_clone import clone_many;"
code="$code print(clone_many([('$OUT/young-base-antonio.wav','$OUT/young-klein-antonio-p2.wav')], cpu_only=True, model_path='/home/nixos/models/staging/Klein_v2_400e_infer.pth', index_path=None, timeout_s=1800, pitch=2, index_rate=0.0));"
code="$code print(clone_many([('$OUT/young-base-santa.wav','$OUT/young-klein-santa-p2.wav')], cpu_only=True, model_path='/home/nixos/models/staging/Klein_v2_400e_infer.pth', index_path=None, timeout_s=1800, pitch=2, index_rate=0.0))"
nix develop --command python3 -c "$code" >>$LOG 2>&1
echo "YOUNG fim: $(ls -lh $OUT/young-klein-*.wav 2>/dev/null)" | tee -a $LOG
