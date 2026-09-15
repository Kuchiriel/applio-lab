# cap02 — audit (81 segs: 0-80) — "Situação"

Fontes: texto literal+verbo; anchors-v2/ep1-anchors-v2.json (ep1=caps 1-14);
wiki Episode_1 (Adapted Chapters 1-14, resumo: Klein acorda com ferida curada,
lâmpada a gás, moeda, revólver, ritual da sorte); parser lotm-audiobook.py
`speaker_of`/`cmd_parse`.

## Tabela (só UNKNOWN + suspeitos + correções)

| seg | atual | veredito | final | evidência |
|---|---|---|---|---|
| 0 | NARRADOR | CORRIGE | SFX | "Toc! Toc! Toc!" = batida; onomatopeia avulsa. Parser: regra onomatopeia (SFX_WORDS tem "toc") não disparou |
| 4 | UNKNOWN | CORRIGE | KLEIN | "Isto..." = fragmento-realização do Klein diante do espelho (segs 1-3). Parser: regex ^Isto falha entre aspas ASCII; caiu no ramo diálogo→resíduo |
| 9 | UNKNOWN | CORRIGE | KLEIN | "O que está acontecendo?", ele murmurou" — cena solo, verbo de fala+pronome. Parser: VERBS não casa "murmurou"+pronome (só nome próprio) |
| 19 | UNKNOWN | CORRIGE | KLEIN | "Hum..." + ação do Zhou (pressiona têmpora, busca memória). Parser: "Hum" fora do léxico de fragmentos (Isto/Isso/Ai/Ei/Ah/Oh/Hã) e fora da interjeição-avulsa (tem continuação) |
| 25 | KLEIN | CORRIGE | NARRADOR | "No dia a dia, era preciso comprar..." — 3ª pessoa impessoal, exposição do penny, sem marca 1ª pessoa. Falso positivo do regex pensamento-1p |
| 27 | NARRADOR | CORRIGE | SFX | "Clinque! Clangue!" = moeda no medidor. Parser: "clinque/clangue" fora do SFX_WORDS → narração |
| 30 | NARRADOR | CONFIRMA | NARRADOR | "houve um som agudo!" = descrição narrativa, não onomatopeia pura |
| 36 | UNKNOWN | CORRIGE | KLEIN | "Os efeitos restauradores...?" + "murmurava silenciosamente" (Zhou). Parser: "murmurava" (imperfeito) fora do VERBS; ALT?(KLEIN)→UNKNOWN |
| 39 | KLEIN | CONFIRMA | KLEIN | "minha cabeça / minha irmã" 1ª pessoa |
| 53 | UNKNOWN | CORRIGE | KLEIN | "Disparar um tiro...?" + "Zhou Mingrui teve uma ideia" = dedução interna, cena solo |
| 56 | UNKNOWN | CORRIGE | KLEIN | "De fato..." + ação do Zhou (olha cartucho, balança cabeça). Mesmo padrão seg36 |
| 57 | KLEIN | CONFIRMA | KLEIN | pensamento; citação do caderno embutida ("Todos morrerão...") é leitura, não diálogo |
| 58 | NARRADOR | CORRIGE | KLEIN | "De onde veio a arma?" = pergunta-dedução da cadeia 58-61 (seg61 é KLEIN c/ "eu"). Parser: pergunta-líder só splita intra-parágrafo |
| 59 | NARRADOR | CORRIGE | KLEIN | idem ("Foi suicídio ou suicídio forjado?") |
| 60 | NARRADOR | CORRIGE | KLEIN | idem ("Em que tipo de problema...?") |
| 61 | KLEIN | CONFIRMA | KLEIN | "eu transmigrei" 1ª pessoa |
| 65 | NARRADOR | CONFIRMA | NARRADOR | "Clique. Clique. Clique... A mão direita..." = ação narrativa c/ SFX embutido (SFX anotado no blocking; split futuro opcional) |
| 66 | KLEIN | CONFIRMA | KLEIN | "para mim / eu transmigraria" |
| 67 | KLEIN | CONFIRMA | KLEIN | "eu tentei um ritual" |
| 77 | NARRADOR | CORRIGE | KLEIN | "Transmigração!" = interjeição avulsa 1 palavra+!. Parser: regra interjeicao-avulsa não disparou |
| 78 | UNKNOWN | CORRIGE | KLEIN | "Há uma clara possibilidade...?" + "Zhou Mingrui parou... e se sentou ereto" = decisão interna |

## Correções (`--set`)
--set 0=SFX --set 4=KLEIN --set 9=KLEIN --set 19=KLEIN --set 25=NARRADOR
--set 27=SFX --set 36=KLEIN --set 53=KLEIN --set 56=KLEIN --set 58=KLEIN
--set 59=KLEIN --set 60=KLEIN --set 77=KLEIN --set 78=KLEIN

## Hipóteses
Nenhuma. (seg65: split SFX opcional, não é hipótese de falante.)

## Exceções do parser
1. Fragmento-líder entre aspas ASCII ("Isto...") não casa `^Isto` → resíduo (seg4).
2. VERBS só no perfeito 3ª p.: "murmurava" escapa (seg36); idem "responder/dizendo" (caps 3-4).
3. Verbo de fala + pronome (ele/ela) sem nome próprio → resíduo/ALT (seg9).
4. "Hum" fora do léxico de fragmentos (seg19).
5. SFX_WORDS incompleto: clinque/clangue (seg27).
6. Pergunta-dedução em parágrafo próprio não vira Klein (pergunta-líder só intra-parágrafo) — segs 58-60.
7. Interjeição-avulsa não disparou ("Transmigração!", seg77).
8. Falso positivo pensamento-1p sem 1ª pessoa visível (seg25).

## Grafias
- "Tingen City" (EN no meio do PT, seg46) vs "Cidade de Tingen"; "Khoy" (conferir vs livro); "George III", "Loen" ok; "yuans" (anacronismo proposital, manter).
