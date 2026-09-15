# PEDIDO-GLM — auditoria Dunn v2+v3 (colar tudo; sem sessão anterior)

Você é apoio forense do projeto LOTM-voz (audiobook multi-voz PT-BR, RVC).
Você roda NESTE host, com acesso total aos arquivos e ao CLI `jarvis`.
Regras: SÓ LEITURA. NUNCA edite: `LOTM-MAPA-VOZES.md`, `SESSAO-*.md`,
`elenco-dubladores.md`, `casting-vol2.json`, `lotm-voices.json`, `presets/`,
nada em `~/Audio/`. Escreva relatório novo (`ELENCO-DUNN-*.md`) + bloco
p/ colar na SESSAO. Evidência (arquivo+minuto+capítulo/cena) ou não vale.
PT-BR, curto. Pode pesquisar na internet o que tiver dúvida (wiki, fóruns,
Dublapédia) — cite a fonte.

## Ferramentas do host (USE)
- `jarvis rag "<pergunta>" --top-k 5` — busca semântica no código/docs do
  projeto (ex: "dunn dataset relabel", "relabel-conteudo método").
  Limitação conhecida: retorna paths + scores, sem snippets — abra o arquivo.
- `jarvis recall "<tema>" --top-k 5` — memória episódica (fatos e decisões
  de sessões passadas). Bom p/ "o que já tentamos com X?".
- `jarvis lessons "<erro ou padrão>"` — lições de erros passados.
- `jarvis remember "<fato>"` — grave achados importantes p/ próximas sessões.
- Arquivos de áudio/vídeo: ouça com ffplay; leia `~/Audio/lotm/epN/*.srt`
  (STT turbo, grudado no áudio) — NÃO use legenda oficial p/ corte.
- Comece com: `jarvis recall "dunn"` + `jarvis rag "dunn dataset auditoria"`.

## Contexto (leia nesta ordem)
1. `applio-lab/LOTM-MAPA-VOZES.md` (verdades validadas; fim = elenco BR:
   Dunn = Gabriel Noya; morto libera ator)
2. `applio-lab/RECADO-GLM.md` §6-§8 (método relabel-conteúdo validado:
   timbre errou 2x, conteúdo pegou as 2)
3. `applio-lab/BACKLOG.md` (fila e pendências)

## O problema
Modelo RVC do Dunn (71 clips, 4.9min) soa como "santa bugado e rouco",
não como Dunn. Hipóteses: (a) contaminação residual, (b) volume insuficiente.
Klein foi salvo pela mesma receita (quarentena F0 + pureza + relabel-conteúdo
+ expulsão de intrusos provados). Repita o julgamento para o Dunn.

## Dados p/ julgar (tudo em disco)
- `~/Audio/lotm/datasets/dunn-v2-relabel.json` — 67 clips classificados:
  42 SEM-ANC / 20 OUTRO / 5 AMBIG. Foque nos 25 não-SEM-ANC.
- `~/Audio/lotm/datasets/dunn-mine/` (25 wavs) +
  `applio-lab/Audio-checks/dunn-mine-checks.txt` — 25 spans com âncora
  "dunn" minerados das legendas EN, cada linha com path + minuto do vídeo
  + STT turbo. Marque MANTER/EXPULSAR por linha.
- REF de matrícula (Dunn PROVADO, não julgar): `dunn-v2/ep10-00766`
  ("I can't use Nightmare" = habilidade exclusiva dele, Seq.7).
- Suspeito conhecido: `dunn-v2/ep12-01416` ("vessel is stable… stand guard"
  = vilão/Megose? julgar com prioridade).
- Âncoras: `~/Audio/lotm/epN/anchors-v2.json` (spans EN×PT com `anchors`
  canônicos); `~/Audio/lotm/anchors-en/lexicon.json` (mangles conhecidos:
  Dan Smith→Dunn, biônder→Beyonder, Azek→Azik).
- Livro: `~/Books/LotM Vol 1 - Palhaço (Clown).epub` (Dunn morre no ep13 da
  S1 — dataset NÃO cresce na S2; só flashbacks).

## Método (grau de certeza)
1. Para cada clip/span, abra a janela EN completa no anchors-v2 do ep
   (não o fragmento) + ache a cena no livro (busque termos-âncora no epub).
2. Calibre ep↔capítulo pela wiki: `lordofthemysteries.fandom.com/wiki/
   Episode_N` (cada página tem "Adapted Chapters" + "Characters in Order
   of Appearance"). Ex: ep1 = caps 1-7,9-10,12-14; ep13 = caps 208-213,215.
3. Regra de ouro: âncora de LORE (beyonder/tingen/backlund/nighthawks)
   NÃO condena — Dunn é capitão e dá briefing sobre elas. Condena só:
   diálogo em 1ª pessoa de OUTRO personagem, título/ritual alheio
   (ex: prece da Audrey), voz feminina, ou cena onde o livro prova que
   Dunn NÃO está presente.
4. Cenas-chave do Dunn (âncoras de certeza): ep1 interrogatório + teste
   do sonho; ep10 caso (Nightmare); ep12-13 ritual/sacrifício.

## Entrega
Tabela: clip | MANTER/EXPULSAR | evidência (minuto + capítulo/cena +
fonte web se usada). No fim: estimativa de volume limpo restante (clips
+ minutos) e veredito: dá p/ treinar ou precisa caçar mais (onde?).
Bloco p/ SESSAO + pedidos ao Muse.
