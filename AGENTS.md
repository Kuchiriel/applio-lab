# AGENTS.md — applio-lab (LOTM voz + audiobook)

> Entrypoint do lab. Leia este arquivo primeiro; ele aponta os detalhes.
> (Spec AGENTS.md: este é o mais próximo dos arquivos do lab, vence o root.)

## O que é
Audiobook multi-voz LOTM PT-BR (Edge/Kokoro + RVC) + datasets RVC por
personagem (Kaggle T4) + prospecção GuiaRenamer (Make). Dono tagueia por
ouvido; evidência > palpite.

## Regras duras
- Rótulo de dataset SÓ com prova (STT + livro ou ouvido). Diarize
  SUB-CLUSTERIZA: rótulo por segmento, nunca por falante.
- Klein×Tolo = mesmo ator: separar por CONTEÚDO, nunca timbre.
- Âncora de LORE não condena (protagonista narra; capitão dá briefing).
  Condena: 1ª pessoa de OUTRO, título/ritual alheio, voz feminina em pool
  masculino, cena onde o livro prova ausência.
- Mineração por âncora pega MENÇÃO, não fala — usar `scripts/mine-anchors.py`
  (filtro anti-menção v2, validado contra ground truth GLM 15/09).
- Legenda oficial NÃO serve p/ corte (dessincada). STT próprio > legenda.
- Kaggle free = max 2 GPUs + quota 30h/semana. Push além = rejeitado.
  Uploads ~3-70kB/s. G_* é checkpoint (extrair p/ _infer depois).
- Render usa código do repo via `scripts/batch-speak.py` (Edge=kvenv,
  kokoro=nix develop). NUNCA o binário `jarvis` do PATH (velho).
  Contrato formal: `../docs/architecture/CONTRATO-LAB-NIXOS.md`
  (invariantes + smoke test — ler antes de tocar em voice.py/rebuild).
- NUNCA botar filtro ffmpeg no render sem testar em sample isolado antes
  (15/09: afade+silenceremove zerou o RVC — cap mudo).
- `speak()` sem kokoro no env funziona só p/ base Edge (import lazy).
- Relabels do dono são por TEXTO (`caps/capNN-relabels.json`) e sobrevivem
  ao reparse. Parse nunca apaga correção.
- Kokoro: SEM SSML/emoção/CAPS — só pontuação + speed. Edge style =
  preset de prosódia (mstts é rejeitado). Narrador alvo 150-160wpm
  (santa: speed 0.8 ≈ 157wpm, medido via STT).

## Onde está o quê (detalhes — ler quando precisar)
| Assunto | Arquivo |
|---|---|
| Estado da sessão | `SESSAO-2026-09-14.md` (fim = mais recente) |
| Verdades validadas + elenco BR | `LOTM-MAPA-VOZES.md` |
| Fila ouvir/pendências/backlog | `BACKLOG.md` |
| Docs vivos do dono (só ele edita) | `personagens/*.md`, `casting-vol2.json`, `lotm-voices.json`, `presets/` |
| Relatórios de apoio | `personagens/ELENCO-*.md`, `PEDIDO-GLM-*.md`, `RECADO-GLM.md`, `RECOMECAR-GLM.md` |
| Pipeline/render | `lotm-pipeline.py`, `lotm-audiobook.py`, `scripts/` |
| Make/SerpApi runbook | `../guia-renamer-pro/scripts/operacao/make-cli.md` |

## Vozes oficiais (não mudar sem A/B + dono)
- NARRADOR = kokoro santa + Attenborough, speed 0.8, index 0.0
- KLEIN = antonio + Klein_v5, pitch 0, index 0.75 (youth p+2 aposentado)
- DUNN = kokoro santa + Dunn_v3 (v4 staged, quota Kaggle esgotada)
- NEIL = santa + Neil_v1 | fallback absoluto = antonio
- venv Python do lab = `~/.venvs/lab` (PERSISTENTE; `/tmp` apaga no reboot
  — kvenv morreu 15/09). `source lab-env.sh` antes de tudo (LD_LIBRARY_PATH
  + LABPY + recria symlink `/tmp/opencode/kvenv`).
