#!/usr/bin/env bash
# Teste Dunn: 4 falas verificadas (cap12:22, cap13:25/39/48) base antonio -> RVC dunn CPU.
export PATH="$HOME/.nix-profile/bin:/etc/profiles/per-user/nixos/bin:/run/current-system/sw/bin:$PATH"
LOG=/tmp/opencode/dunn-test.log
OUT=/home/nixos/Audio/lotm/testes-timbre
mkdir -p $OUT
T1=$(python3 -c "import json;d=json.load(open('/home/nixos/projects/applio-lab/caps/cap12.json'));print([s['text'] for s in d['segments'] if s['i']==22][0])")
T2=$(python3 -c "import json;d=json.load(open('/home/nixos/projects/applio-lab/caps/cap13.json'));print([s['text'] for s in d['segments'] if s['i']==25][0])")
T3=$(python3 -c "import json;d=json.load(open('/home/nixos/projects/applio-lab/caps/cap13.json'));print([s['text'] for s in d['segments'] if s['i']==39][0])")
T4=$(python3 -c "import json;d=json.load(open('/home/nixos/projects/applio-lab/caps/cap13.json'));print([s['text'] for s in d['segments'] if s['i']==48][0])")
for n in 1 2 3 4; do
  eval "TT=\$T$n"
  /tmp/opencode/kvenv/bin/edge-tts --voice pt-BR-AntonioNeural --text "$TT" --write-media /tmp/dbase$n.mp3 >>$LOG 2>&1
  ffmpeg -y -v error -i /tmp/dbase$n.mp3 -ar 44100 -ac 1 $OUT/c$n.wav >>$LOG 2>&1
  eval "W$n=$OUT/c$n.wav"
done
echo "bases: $W1 $W2 $W3 $W4" | tee -a $LOG
code="from jarvis.core.voice_clone import clone_many;"
code="$code print(clone_many([('$W1','$OUT/d1.wav'),('$W2','$OUT/d2.wav'),('$W3','$OUT/d3.wav'),('$W4','$OUT/d4.wav')], cpu_only=True, model_path='/home/nixos/models/staging/Dunn_v2_400e_infer.pth', index_path=None, timeout_s=1800, pitch=None, index_rate=0.0))"
cd /home/nixos/projects/nixos-ai
nix develop --command python3 -c "$code" >>$LOG 2>&1
ffmpeg -y -v error -f concat -safe 0 -i <(printf "file '%s'\n" $OUT/d1.wav $OUT/d2.wav $OUT/d3.wav $OUT/d4.wav) -c copy $OUT/dunn-v2-antonio.wav >>$LOG 2>&1
echo "DUNN-TEST-SANTA fim: $(ls -lh $OUT/dunn-v2-antonio.wav 2>/dev/null)" | tee -a $LOG
