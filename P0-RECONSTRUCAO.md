# P0 — Reconstrução (auditoria ChatGPT 15/09)

## Mapa
AUDIO (mp4) → separate (demucs vocals) → VAD (segs.json) → diarize
(WeSpeaker ResNet34 RTTM) → STT (faster-whisper turbo, vocals.srt) →
anchors-v2 (EN×PT spans) → pools (slice) → pureza/relabel (tabela) →
Kaggle T4 (400e) → extract _infer → staging + .index par-stem.
Paralelo: epub → parse (speaker_of) → caps/capNN.json → tag/relabel dono →
render (batch-speak bases + RVC lote + concat) → master (SFX/binaural).

## Contratos LOTM↔NixOS-AI (verificados no código)
- Render chama `speak()` via batch (kvenv/nix) e `clone_many()` direto.
- `lotm-voices.json` ≈ voice profile (base/voice/rate/speed/style/rvc/
  pitch/index_rate). Presets em `personagens/presets/`.
- `speak(text, voice, play, clone, speed, pitch, base, rvc, rvc_index,
  keep_wav, rate, index_rate, f0_method, style)` — CONFIRMADO em voice.py.
- `_resolve_rvc()` aceita alias|path; index = stem .index ou None.
- Riscos: binário `jarvis` do PATH é velho (usar repo); kokoro exige env
  nix; Edge flaky (retry); RVC lote CPU (GPU vaza); cache por conteúdo
  com salt (v3 atual — bump em mudança de regra).
- STT jarvis usa faster-whisper (turbo portado? VERIFICAR — fw-stt é do lab).

## Hipóteses testáveis (ordenadas)
1. RVC achata ?/! (MEDIDO pyin: base -100/+64 → RVC -114/-101).
2. Chiado "s" = resíduo RVC onde base é silêncio (MEDIDO rms 0.005 vs 0).
3. Dunn ruim = contaminação 30-40% (v4 com 68 limpos decide).
4. Narrador 150-160wpm = santa speed 0.8 (MEDIDO 157wpm).
5. Khoy "Coz" = limitação santa/RVC (samples p/ ouvido).
6. Style Edge = prosódia sutil, não emoção (vereditos dono).

## Plano
P1 audits 2-12 (subagentes) → blocking+SFX → parser/regressão →
P2-P3 voz → P4 integração → relatórios.
