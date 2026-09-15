# cap04 — audit (107 segs: 0-106) — "Adivinhação"

Fontes: texto literal+verbo; wiki Episode_1 (caps 1-14: compras, Smyrin,
praça do circo, tenda da cartomante, tarô=Roselle); parser.

## Tabela

| seg | atual | veredito | final | evidência |
|---|---|---|---|---|
| 2 | KLEIN | CONFIRMA | KLEIN | "Ele murmurou... Não vou a uma entrevista" — solo |
| 13 | NARRADOR | HIPÓTESE | KLEIN | "Vejam só, seus desenhos são tão bonitos..." — entusiasmo interno com as notas (cadeia 12→15); imperativo retórico, sem 1ª pessoa |
| 14 | NARRADOR | HIPÓTESE | KLEIN | idem ("Olhem, a marca d'água...") |
| 27 | KLEIN | CONFIRMA | KLEIN | "Eu acabaria disparando...?" 1ª pessoa |
| 35 | UNKNOWN | CORRIGE | VENDEDOR | "Venha experimentar nosso delicioso peixe assado!" — pregão; seg42 confirma "vendedores ambulantes... gritavam" |
| 36 | UNKNOWN | CORRIGE | VENDEDOR | idem (sopa de ostra) |
| 37 | UNKNOWN | CORRIGE | VENDEDOR | idem (peixe do porto) |
| 38 | UNKNOWN | CORRIGE | VENDEDOR | idem (muffins e enguia) |
| 39 | UNKNOWN | CORRIGE | VENDEDOR | idem ("Concha! Concha! Concha!") |
| 40 | UNKNOWN | CORRIGE | VENDEDOR | idem (vegetais) |
| 54 | NARRADOR | HIPÓTESE | KLEIN | "Ah, os biscoitos de Tingen... são muito deliciosos..." + seg55 "engoliu saliva e sorriu" = desejo interno do Zhou |
| 56 | UNKNOWN | CORRIGE | KLEIN | "Senhora Smyrin, oito libras de pão de centeio." — pedido do Klein; confirmado pela resposta da Wendy no seg57 |
| 57 | KLEIN | CORRIGE | WENDY | "Ah. Caro Klein, onde está Benson?... Wendy perguntou sorrindo." — verbo+nome NO PRÓPRIO parágrafo ("perguntou" + "Wendy"); vocativo "Caro Klein". Parser retornou KLEIN via vizinho (seg58 "Zhou") — precedência errada |
| 58 | KLEIN | CONFIRMA | KLEIN | "respondeu Zhou Mingrui" |
| 59 | NARRADOR | CORRIGE | WENDY | "Ele é realmente um rapaz trabalhador..." — fala da Wendy (cadeia 57-61; "rapaz"=Benson) |
| 60 | NARRADOR | CORRIGE | WENDY | "Tudo está bom agora. Você já se formou..." — fala da Wendy (2ª pessoa p/ Klein) |
| 61 | UNKNOWN | CORRIGE | KLEIN | "Senhora Smyrin, a senhora parece..." + "responder com um sorriso seco" (Zhou). Parser: "responder" (infinitivo) fora do VERBS |
| 66 | KLEIN | CONFIRMA | KLEIN | "Zhou Mingrui murmurou" |
| 70 | UNKNOWN | CORRIGE | WENDY | "Não, eu sempre fui assim tão jovem," respondeu Wendy" — verbo+nome no próprio! Parser falhou porque "Wendy" NÃO está no léxico NAMES → ALT?(KLEIN)→UNKNOWN |
| 73 | KLEIN | CONFIRMA | KLEIN | "Zhou Mingrui perguntou" |
| 75 | UNKNOWN | CORRIGE | WENDY | "Você tem que agradecer..." disse Wendy" — mesmo motivo (Wendy fora do NAMES) |
| 82 | UNKNOWN | CORRIGE | KLEIN | "Há uma apresentação de circo amanhã à noite?" + "lia seu conteúdo em voz baixa" = Klein lendo o panfleto |
| 83 | NARRADOR | HIPÓTESE | KLEIN | "Melissa definitivamente gostaria. No entanto, qual é o preço...?" + seg84 (aproxima-se p/ perguntar) = cálculo interno |
| 86 | UNKNOWN | CORRIGE | TREINADORA | "Gostaria de tentar uma adivinhação?" + seg85 "a voz rouca de uma mulher" — a falsa cartomante (cap5 seg38-39 prova que é a treinadora de animais) |
| 89 | UNKNOWN | CORRIGE | KLEIN | "Não," + "Zhou Mingrui balançou a cabeça" = resposta do Klein |
| 90 | KLEIN | CORRIGE | TREINADORA | "Minha adivinhação de tarô é muito precisa." — é a MULHER insistindo (seg91 o Zhou "ficou pasmo" reagindo a ela). Parser: "Minha" (1ª pessoa DELA) contaminou o regex — "1ª pessoa de OUTRO" |
| 91 | UNKNOWN | CORRIGE | KLEIN | "Tarô..." + "Zhou Mingrui ficou pasmo" = reação do Klein |
| 92-104 | NARRADOR | CONFIRMA | NARRADOR | lore Roselle/tarô/igrejas = exposição; lore citada não condena e aqui não há marca de fala |
| 105 | KLEIN | CONFIRMA | KLEIN | "eu vou tentar" + "disse" (fala direta do Klein, não só pensamento) |
| 106 | NARRADOR | CORRIGE | TREINADORA | "o senhor é o primeiro aqui hoje, então é por conta da casa" + "A mulher disse" — fala da falsa cartomante. Parser: "disse"+advérbio (sem nome) e "mulher" fora do NAMES |

## Correções (`--set`)
--set 35=VENDEDOR --set 36=VENDEDOR --set 37=VENDEDOR --set 38=VENDEDOR
--set 39=VENDEDOR --set 40=VENDEDOR --set 56=KLEIN --set 57=WENDY
--set 59=WENDY --set 60=WENDY --set 61=KLEIN --set 70=WENDY --set 75=WENDY
--set 82=KLEIN --set 86=TREINADORA --set 89=KLEIN --set 90=TREINADORA
--set 91=KLEIN --set 106=TREINADORA

## Hipóteses
- --set 13=KLEIN --set 14=KLEIN (entusiasmo interno sem 1ª pessoa).
- --set 54=KLEIN (desejo interno; seg55 corrobora).
- --set 83=KLEIN (cálculo interno; seg84 corrobora).

## Exceções do parser
1. Nome fora do léxico NAMES ("Wendy", "mulher/cartomante" como papel) → verbo+nome válido vira ALT/UNKNOWN (segs 70, 75) ou narração (106).
2. Precedência de vizinho sobre verbo+nome no próprio parágrafo (seg57: "Wendy perguntou" perdido p/ "Zhou" do seg58).
3. "responder/dizendo" (infinitivo/gerúndio) fora do VERBS (segs 61, cap3-66 idem).
4. 1ª pessoa de OUTRO contamina pensamento-1p (seg90 "Minha adivinhação...").
5. Pregões de multidão sem verbo+nome → UNKNOWN correto (não adivinhar); veredito manual VENDEDOR via seg42.

## Grafias
- "Smyrin" (padaria; conferir vs livro); "Alface e Carne" (tradução literal — conferir EN); "Tingen", "Backlund", "Feysac", "Intis", "Feynapotter", "Lenburg", "Masin", "Sauron" ok; "Palácio Bordo Branco" (tradução literal — conferir); nomes do ritual ("Senhor Imortal..." etc. — conferir).
