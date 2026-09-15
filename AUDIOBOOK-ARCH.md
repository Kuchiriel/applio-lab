# Audiobook — arquitetura GERADOR × LEITOR (2026-09-14)

## GERADOR offline (wav final; qualidade máxima, sem pressa)
Pipeline por segmento: parse → atribui voz → BASE → RVC personagem → master.
Camadas (bloco a bloco, depois sobrepostas):
1. VOZ (Edge/Kokoro/XTTS + RVC presets por personagem).
2. SFX (onomatopeia→tabela; curadoria Sonniss/Pixabay em ~/Audio/sfx/).
3. AMBIÊNCIA INFERIDA (LLM lê a cena e emite [AMB]: quarto/lampião/moeda
   no medidor mesmo sem onomatopeia; presets Tingen/Backlund: carroças,
   walla, chuva).
4. MÚSICA de clima por cena.
5. MASTER (loudnorm + mix).
6. ESPACIAL (futuro): binaural — posicionar personagens/SFX no campo
   estéreo (ffmpeg `sofalizer`+HRTF ou `pan` simples por personagem).
- BASE por caso: Edge Antonio (adulto padrão) | Kokoro pm_santa (idoso) |
  **XTTS-v2 + referência EMOCIONAL do próprio dub** (segmentos `emo=`).
- RVC: presets por personagem (pitch/index/protect/f0 em lotm-voices.json).
- Master: ffmpeg loudnorm + concat (rápido, local).
- Candidatos avaliados: CosyVoice 2/3 (Apache-2.0, emoção; PT-BR incerto),
  Fish Speech S2 (multilíngue, instruções; checar PT), Dia (diálogo
  multi-falante; checar PT), F5-TTS (rápido), Zonos (melhor, lento 30s+).

## LEITOR realtime (play/pause; inferência RÁPIDA)
- Código: modules/ai/jarvis audiobook.py + legado. Motor: Edge/Kokoro
  streaming (XTTS stream <200ms só com GPU livre).
- REGRA: realtime = base SEM RVC (RVC-CPU lento p/ streaming; RVC-GPU só
  se :8080/treinos ociosos). RVC fica no gerador.

## Licenças (atenção comercial)
- XTTS-v2: coqui-public-model-license (não-Apache; checar uso comercial).
- CosyVoice: Apache-2.0. Fish/Dia: checar por modelo.

## Mapa espacial (pesquisa 15/09: NYT R&D, vrtonung, Berklee, Spatial Storybook)
- Narrador (não-diegético): CENTRO-FRENTE, perto, seco (head-locked da
  fogueira). Voz principal nunca sai da frente (inteligibilidade 2-5kHz).
- Klein: L/C/R por cena, coerente (sentado = lado fixo; pensa = centro mais
  perto/baixo; fala = posição da cena). Micro-movimento sutil.
- Luta/beyonder: espalhar largo, movimentos grandes, SFX posicionados,
  altura NUNCA (ouvido humano não resolve vertical; reservado = não usar).
- REGRA DE OURO (vrtonung): pan SEM room soa colado na cabeça — toda posição
  precisa de reflexo/reverb próprio (aecho por posição).
- Formato final = estéreo binaural normal (qualquer fone; sem decoder).
