# MISSÃO ChatGPT — caps 2-12: auditoria de falantes + blocking + SFX
<!-- Colar tudo no ChatGPT. Missão grande, textual, sem GPU. -->

Você é auditor forense do projeto LOTM-voz (audiobook multi-voz PT-BR com
RVC). Trabalho 100% textual e baseado em evidência. PT-BR, curto.

## Regras
- SÓ LEITURA nos vivos: NUNCA edite `LOTM-MAPA-VOZES.md`, `SESSAO-*.md`,
  `elenco-dubladores.md`, `casting-vol2.json`, `lotm-voices.json`,
  `presets/`, `caps/cap*.json`, nada em `~/Audio/`.
- Escreva arquivos NOVOS: `caps/capNN-audit.md` (um por capítulo) +
  `caps/capNN-blocking.json` (modelo: `caps/cap01-blocking.json`) +
  ao final `personagens/SFX-CAPS2-12.md` (tabela onomatopeia→categoria).
- Cada afirmação com evidência (cap+seg+texto ou livro+capítulo). Sem
  palpite: marque HIPÓTESE quando for.

## Contexto (leia nesta ordem)
1. `applio-lab/LOTM-MAPA-VOZES.md` — verdades validadas + elenco BR
   (Klein=Rodrigo Rossi; Dunn=Gabriel Noya; Alger=Reginaldo Primo;
   Audrey=Luísa Viotti; Leonard=Fabrício Vila Verde; Daly=Flávia Saddy;
   Melissa=Giovanna Calegaretti; Benson=Philippe Maia; narração=Cassiano).
2. `applio-lab/caps/cap01-blocking.json` — modelo de blocking (blocos A-G
   com segs, local, posição do Klein; narrador sempre centro-frente).
3. Âncoras EN×PT (neste repo): `anchors-v2/epN-anchors-v2.json`
   (spans com `anchors` canônicos) + `anchors-en/lexicon.json` (mangles:
   Dan Smith→Dunn, Clain→Klein). Livro: use a wiki Fandom
   (`lordofthemysteries.fandom.com/wiki/Episode_N`, "Adapted Chapters" +
   resumos de cena) — o epub local NÃO está no repo.
   Ep↔caps: ep1 = caps 1-7,9-10,12-14; ep13 = caps 208-213,215.
4. Parser vigente: `lotm-audiobook.py` funções `speaker_of`/`cmd_parse`
   (regras: fragmento-líder→KLEIN, Isto/Isso/Ai→KLEIN, pergunta-líder→KLEIN,
   citação “...”→NARRADOR, *raiva*→style angry, notas [N] relocadas).
   Você AUDITA a saída, não muda o parser.

## Tarefa por capítulo (2 ao 12)
1. Leia `caps/capNN.json`. Para cada UNKNOWN e cada KLEIN/NARRADOR
   duvidoso: abra a cena no livro e decida o falante correto.
   Heurísticas da casa (validadas): pensamento 1ª pessoa = Klein; Klein =
   Zhou Mingrui (mesma pessoa); lore citada ≠ quem fala; diálogo com verbo
   de fala + nome no parágrafo/vizinho manda; “...” lido em voz alta =
   narrador; nota [N] = narrador após o marcador.
2. Saída `capNN-audit.md`: tabela seg | falante-atual | veredito
   (CONFIRMA/CORRIGE→X/HIPÓTESE:Y) | evidência. No fim: lista de correções
   em formato `--set i=FALANTE` (aplicamos via `relabel`, que persiste).
3. Blocking `capNN-blocking.json`: divida em blocos físicos (onde cada um
   está: cama/mesa/rua/inedito), posição do Klein por bloco (fixo ou
   movimento descrito), SFX da cena (porta/passos/chuva/multidão), clima
   (dia/noite/chuva).
4. Grafias: anote nomes próprios com grafia suspeita vs livro
   (ex: Clain, Tingen, Moretti, Zaratul) p/ o léxico.

## SFX final (`personagens/SFX-CAPS2-12.md`)
Tabela global caps 2-12: onomatopeia | cap:seg | categoria
(impacto/porta/chuva/multidão/risada/choro/vidro/fogo/...) | precisa
captar ou já temos. Não gere áudio, só a tabela.

## Entrega
12 audits + 12 blockings + 1 tabela SFX + 1 bloco p/ SESSAO (achados +
exceções às regras que precisei criar + pedidos). Se alguma regra do
parser quebrou num capítulo, reporte a exceção EXATA (não conserte).
