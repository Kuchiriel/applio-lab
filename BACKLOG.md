# BACKLOG — não esquecer (dono 15/09 manhã; fila de ouvido atualizada 15/09)

## OUVIDO DO DONO (nesta ordem — resto arquivado ou obsoleto)
1. `Audio/lotm/cap01-attenborough-kleinv5.wav` — capítulo atual (erros novos?
   reporte com minuto + frase)
2. `comparativos/dunn-v3-dunnline.wav` — Dunn v3, fala do Dunn, base santa
3. `comparativos/young-klein-v5-p0.wav` × `young-klein-v5-p2.wav` — A/B
   slider (p0 = oficial; confirma se o "s" sumiu)
4. `comparativos/leonard-v2-test.wav` + `daly-v2-test.wav` (+ v1 p/ comparar)
5. `style-{plain,cheerful,sad,angry,unfriendly}.wav` — ATENÇÃO: refeitos e
   STT-verificados (os antigos narravam tags, substituídos)
6. Tabelas (Audio-checks/): `dunn-mine-checks.txt` (25 MANTER/EXPULSAR) >
   `ouvido-2026-09-14.txt` (10 clips: 7 klein + 3 dunn) >
   `klein-v3-relabel-checks.txt` > `audrey-repescagem-checks.txt` >
   `pureza-pools-checks.txt`
7. Reservas GLM (ouvido fino): dunn-v2/ep10-00757 + ep9-00961
   (clips em `Audio/lotm/datasets/dunn-v2/`)
- OBSOLETOS (não ouvir): cap01-kleinv4b, young-klein-{antonio,santa}-p2,
  dunn-{test-antonio,v2-antonio,v3-antonio,v3-santa}, narr-speed-* (isolado
  não julga — velocidade se avalia no capítulo).

## Ouvir (fila, nesta ordem)
1. `cap01-attenborough-kleinv5.wav` — ESPERAR re-render (pitch0+Moréti pendente)
2. `comparativos/dunn-v3-dunnline.wav` — PRONTO (fala do Dunn, base santa)
3. `comparativos/young-klein-v5-p0.wav` vs `young-klein-v5-p2.wav` — A/B slider
4. `comparativos/leonard-v2-test.wav` + `daly-v2-test.wav` — assando
5. `style-{plain,cheerful,sad,angry,unfriendly}.wav` — REFEITOS, STT-verificados
6. `dunn-mine-checks.txt` (Audio-checks/) — 25 linhas MANTER/EXPULSAR (tabela
   com path + minuto do vídeo + STT turbo)
7. `leonard-v1-test.wav` + `daly-v1-test.wav` — base de comparação v1

## Dunn — receita Klein aplicada
- [x] mineração 31 spans âncora → 25 clips + STT + tabela
- [ ] dono marca MANTER/EXPULSAR na tabela
- [ ] dunn-v4 = v2 keeps + aprovados da tabela (+ expurga ep12-1416) → push
- [ ] se ainda ruim: GLM caça Noya em outros papéis (política ator-em-papel)

## SFX — lista de compras p/ dono (não achei)
- [ ] carroça passando (pass-by, rua de pedra, ~5-10s, distante)
- [ ] passos faint em madeira/pedra (bem baixinhos)
- [ ] vento noturno leve / night air
- [x] room tone quarto pequeno + heater (baixando Sonniss archive.org)
- [ ] thud corpo (Pá! cap01:29) + knock madeira (Toc!) + shiver (Arrepios!)

## Montagem SFX (plano p/ fone do dono)
- Layers: BED room-tone em loop baixo (-30dB) + CIDADE abafada eventual
  (carroça/passo a -24dB, 2-3x por cap) + SPOT no momento exato (thud/knock).
- Primeiro teste: quarto cap01 (bed + 1 carroça distante aos ~4min).
- Binaural SÓ no master final (ffmpeg pan; TTS é mono, sem efeito no TTS).

## Binaural master (final, não agora)
- Narrador centro-frente (história de fogueira); Klein L/C/R por fala coerente;
  NUNCA atrás/abaixo/voando (reservar p/ lutas/beyonders).

## JARVIS permanente (custo 0, componentes)
- [x] pronúncia/footnote/chunk/style-prosódia/speed-hash no repo (voice.py)
- [ ] STT turbo default no módulo stt do jarvis (fw-stt.py é do lab; portar
  modelo=turbo + fallback cpu-int8 p/ jarvis stt) — voice pipeline SEGUE
  quebrado, não arrumar agora
- [ ] batch-speak.py → virar subcomando do lab (hoje avulso em scripts/)

## Treinos
- [x] leonard-v2 + daly-v2 (COMPLETE, extraindo)
- [ ] melissa-v2 staged (push quando sobrar slot; dataset fino, continuar depois)
- [ ] alger/hood BLOQUEADOS (dono)
