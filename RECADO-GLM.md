# RECADO-GLM — handoff 2026-09-14 (noite)

> Pra próxima sessão GLM/SOLAR. Estado em disco verificado; detalhes no
> relatório da sessão: `personagens/ELENCO-NOVO-2026-09-14.md` (§1-§8).

## 1) Novos caminhos (reorganização feita pelo dono)
| O que | Onde |
|---|---|
| Vídeos LOTM ep1-13 | `~/Videos/lotm/ep*.mp4` (FORA de ~/models e ~/Audio) |
| Legendas oficiais S1 | `~/Videos/lotm/*.srt` (⚠️ dessincadas p/ corte — MAPA 09-13; usar só p/ STT-âncora) |
| Vídeos AoT No Regrets | `~/Videos/aot/noregrets-{p1,p2}.mp4` |
| Kits de áudio AoT | `~/Audio/aot-noregrets/p*/` (era Audio/levi/) |
| Scripts do lab (14) | `applio-lab/scripts/` (consolidados; enroll.py, slice-pools.py, purify-klein.py, kaggle-*, gen-*, etc.) |
| Registro de reuso | `personagens/reuse-registry.json` (Levi→Klein, duplos, mortos liberam) |
| INVENTARIO.md | atualizado no disco (`~/Audio/lotm/INVENTARIO.md`) |

## 2) Pedidos do dono (em aberto, nesta ordem)
1. **Prova da angelica com tabela**: re-rodar pureza do angelica-v1 com
   distratores POR GÊNERO (Klein + Dunn p/ masculino; Melissa/Audrey p/
   feminino) + STT de cada clip suspeito; entregar tabela clip×score×STT
   p/ o dono ouvir e decidir expulsão. (Base: relatório §7-§8.)
2. **Re-run geral da pureza v2** com distratores por gênero (a ref AUDREY
   sozinha é fraca: klein-v1 deu 136/199 "audrey") + STT nos Tier-1.
3. **Protocolo de refs** (lição §7): toda ref passa por pureza-check com
   distratores ANTES de virar âncora de verify; refs ref-*.wav internas
   dos pools também suspeitas — matrícula é fonte do problema.
4. **Docs vivos são do dono**: GLM/SOLAR só relata (arquivo novo de
   relatório ≠ editar). Propostas de mudança em relatório, dono cola.

## 3) Aprovado / já aplicado
- Grafias no MAPA (linhas 163-165): Sharon≠Sharron, Maric (não "Marric"),
  Xio Derecha canônico — crédito "correção GLM 2026-09-14".
- Quarentena por F0 (dunn-v2) é prática da casa — MAS não pegou timbre
  (16 suspeitos sobreviveram; relatório §8). Purga dos Tier-1 (megose,
  angelica, elizabeth, christina, selena, sharon + masculinos ≥0.7)
  AINDA pendente de ouvido do dono; nada removido até agora.
- Especiais dublados: dono NÃO achou dublagem na CR (contraria ANIDT/
  ANMTV) — fonte bloqueada; revisitar quando T2 sair.

## 4) Estado técnico (para não redescobrir)
- kvenv: `/tmp/opencode/kvenv` VIVO pós-reboot. Exige
  `LD_LIBRARY_PATH=/nix/store/7vafhlh...-gcc-15.2.0-lib/lib:/nix/store/483x...-zlib-1.3.2/lib:/nix/store/n12n...-libffi-3.7.1/lib`
  (mesma receita de scripts/../chain-cap01.sh; os scripts consolidados
  devem assumir isso).
- Pureza: `pureza-pools.py` (repo) → `~/Audio/lotm/datasets/pureza-report.json`.
- Auditorias p/ ouvido: `Audio-checks/audrey-repescagem-checks.txt`,
  `Audio-checks/pureza-pools-checks.txt` (6 candidatos Audrey ep4 + tiers).
- Anomalia 37:04-37:15 ep4: RESOLVIDA (§7) — Klein monologa na janela;
  "Tonta" = provável Susie; check-19 do ep4-labels proposto p/ revisão.

## 5) anchors-v2 (2026-09-14, noite — pedido do Muse Spark 1.3)
- EN indexado: `~/Audio/lotm/anchors-en/ep01-13.json` (5328 linhas
  [t0,t1,texto]; fonte provável: eps 1-10 legendas oficiais, 11-13 STT).
- Matcher: `applio-lab/scripts/anchors-v2.py` — overlap temporal (≥0.35
  da linha EN) + fuzzy de nomes (difflib ≥0.75) + stoplist PT.
- Resultado 11 eps c/ SRT: **4188/4745 matched (88%)**, 723 alta-conf
  (overlap ≥0.7 + âncora ou score ≥0.35), skew −0.13s a −0.62s (mesmo
  eixo temporal; tolerância de dessincronia OK).
- Saída: `epN/anchors-v2.json` (spans EN×PT c/ âncoras) + lexicon
  agregado `anchors-en/lexicon.json` (23 entradas): antigo/antigonos→
  Antigonus, leona/leonardo/leonor→Leonard, tinden/tinge/tingian→Tingen,
  backland→Backlund, milissa/missa→Melissa, moret→Moretti, zarathou→
  Zaratul, dali→Daly, Clain→Klein (anotado p/ v2, fuzzy 0.75 não pegou).
- PENDENTE: ep1 e ep3 sem vocals.srt — STT catch-up RODANDO desanexado
  (whisper small; ep1 usa `ep1-vocais-isolados.wav`, kit nomenclatura
  antiga; ep3 a ~45% 13:10/~30min). Quando concluir: re-rodar
  `scripts/anchors-v2.py --eps 1 3` e regenerar lexicon (automático).
- IMPORTANTE: EN×PT não casa por texto (idiomas diferentes — 1ª versão
  deu 17/547); casamento é TEMPORAL, texto é metadado de qualidade.
  Âncoras vêm do lado EN do span casado (v2); fuzzy PT só p/ lexicon.

## 6) Experimento rotulagem-por-conteúdo (klein-v3, 2026-09-14 noite)
- Script: `scripts/relabel-conteudo.py --pool <pool>` — cruza clip
  (epN-SSSSS = segundo) c/ anchors-v2, classifica SELF/OUTRO/SEM-ANC,
  cruza c/ pureza-report (timbre). Relatório: `datasets/klein-v3-relabel.json`.
- klein-v3: SELF 11 | OUTRO 31 (14 risco-diálogo + 17 lore-benigno) |
  SEM-ANC 49. Concordância timbre×conteúdo só 41/92 → timbre isolado
  NÃO basta (falso positivo cross-gender + Klein-narrador citando nomes).
- ACHADO: `ep4-00856` = prece da AUDREY dentro do pool do Klein
  ("obrigada, senhor Enforcado, por me tornar uma espectadora" — 1ª
  pessoa feminina; timbre dissera Klein = a confusão clássica).
- Tabela p/ ouvido (7 prioritários): `Audio-checks/klein-v3-relabel-checks.txt`.
- Mangles novos p/ lexicon: professor Azek→Azik, biônder→Beyonder,
  Dan Smith→Dunn (agregados na próxima passada do matcher).
- Lição: âncora de LORE (antigonus/zaratul/nighthawks) ≠ contaminação —
  Klein NARRA sobre elas. Risco real = âncora de DIÁLOGO/título alheio.

## 7) Diretriz Muse + relabel dunn-v2/neil-v1 (2026-09-14, noite)
- MUSE: validar método no Klein ANTES de escalar (relabel "todos os
  pools" suspenso); ouvido do dono = última milha nos casos de fronteira.
- Aplicado: relabel dunn-v2 e neil-v1 (pools já treinados, sem GPU).
  Upgrade no script: classe AMBIG (co-ocorrência por ENREDO não condena —
  Leonard=parceiro do Dunn nos Nighthawks; Dunn=colega de escritório
  do Neil; Klein/lore por causa).
- dunn-v2: 0 SELF | 5 AMBIG | OUTRO 20 (17 lore-benigno + 3 ambíguos) |
  42 SEM-ANC. neil-v1: 0 SELF | 17 AMBIG | OUTRO 5 (todos lore — Neil é
  sacerdote da Deusa Evernight) | 32 SEM-ANC. Nenhuma condenação forte.
- Lista consolidada p/ ouvido (7 klein + 3 dunn):
  `Audio-checks/ouvido-2026-09-14.txt`.
- Status STT ep1/ep3: vivos (760% CPU, 31min; ep3 rastejou nas óperas —
  fallback temperatura do whisper). anchors-v2 --eps 1 3 quando fechar.
- PEDIDOS AO MUSE (via dono): (1) ouvir ep4-00856 PRIMEIRO — é o teste
  do método todo (prece da Audrey c/ timbre Klein); (2) manter formato
  [t0,t1,texto] em anchors-en/ p/ futuras fontes (especiais dublados,
  T2) — o matcher já consome; (3) confirmar fonte dos EN ep11-13
  (STT? legenda?) p/ calibrar confiança dos metadados deles.

## 8) Vereditos do ouvido-solar + resposta Muse (2026-09-14, noite)
- MUSE confirmou: EN ep11-13 = MESMOS .ass de fã dos outros (baixados
  juntos); match menor só porque eps são curtos. Formato [t0,t1,texto]
  mantido. → metadados de confiança: homogêneos, ajustar nada.
- 10 clips de ouvido re-auditados c/ janela EN COMPLETA + livro + wiki:
  - DUNN PROVADO: dunn-v2/ep10-00766 — "I can't use Nightmare" =
    habilidade exclusiva dele (Seq.7 Nightmare, 2+ fontes web). Timbre
    (Klein) errou: confusão macho-macho.
  - KLEIN PROVADO: ep4-01507 ("my responsibility to save MELISSA" =
    irmã) e ep12-00362 ("sent the letters… Azik and Daly reply" =
    monólogo). 918/923 = Klein perguntando sobre mundo espiritual
    (Daly é menção).
  - AUDREY PROVÁVEL: ep4-00856 (cena da poção no EN + 1ª pessoa fem;
    livro V1 tem a cena da Espectadora). Expulsar do klein-v3.
  - SUSPEITA DE INTRUSO NOVO: dunn-v2/ep12-01416 ("vessel is stable…
    stand guard" = vilão/Megose?) e klein-v3/ep10-01435 ("minha
    investigação" — EN diz FRYE'S investigation → Frye/Rothier?).
  - Balanço: timbre errou 2x, conteúdo pegou as 2. MÉTODO VALIDADO.
- STT ep1/ep3: vivos (ep3 rastejou nas óperas; ep1 ~62%).
  anchors-v2 --eps 1 3 ao fechar.
