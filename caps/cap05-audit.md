# cap05 — audit (110 segs: 0-109) — "Ritual"

Fontes: texto literal+verbo; anchors-v2/ep1-anchors-v2.json (spans
"Audrey Hall Justice, Tarot Club" e "Alger Wilson The Hanged Man" ~t1375-1380:
a cena da névoa do fim do cap está no ep1 — corrobora segs 91-92=AUDREY,
101=ALGER); wiki Episode_1 + resumos caps 1-10 (ritual da sorte → névoa;
Audrey espelho; Alger no navio; "Senhor, onde é isto?" + uníssono; codinomes
Tolo/Justiça/Enforcado); parser.

Elenco da tenda (fato textual, segs 36-41): FALSA = treinadora de animais se
passando por cartomante (segs 12-34) → rótulo TREINADORA; VERDADEIRA chega no
seg36-37 (segs 37,41,43) → rótulo CARTOMANTE.

## Tabela

| seg | atual | veredito | final | evidência |
|---|---|---|---|---|
| 2 | KLEIN | CONFIRMA | KLEIN | "que eu transmigrei" 1ª pessoa |
| 8 | UNKNOWN | CORRIGE | NARRADOR | ""A Temperança," etc." = fim da enumeração narrativa do seg7 ("descobriu cartas familiares como..."); "etc." = voz do narrador |
| 9 | KLEIN | CONFIRMA | KLEIN | "meu" 1ª pessoa |
| 12 | UNKNOWN | CORRIGE | TREINADORA | "Embaralhe as cartas..." + "disse a cartomante". Parser: papel em minúsculas ("cartomante") fora do NAMES |
| 13 | KLEIN | CONFIRMA | KLEIN | "Zhou Mingrui perguntou" |
| 14 | KLEIN | CORRIGE | TREINADORA | "ela revelava um leve sorriso, dizendo: 'Claro... Eu sirvo apenas como leitora'" — sujeito "ela"=falsa cartomante; 1ª pessoa DELA contaminou o regex ("1ª pessoa de OUTRO") |
| 15 | NARRADOR | CORRIGE | KLEIN | "Zhou Mingrui imediatamente a questionou: 'Essa leitura não exige taxas...?'" = pergunta direta do Klein. Parser: "questionou" fora do VERBS |
| 16 | KLEIN | CONFIRMA | KLEIN | "eu já vi" |
| 17 | NARRADOR | CORRIGE | TREINADORA | "A cartomante ficou surpresa antes de dizer: 'É gratuito.'" Parser: "dizer" (infinitivo) fora do VERBS + papel fora do NAMES |
| 19 | UNKNOWN | CORRIGE | KLEIN | "Está feito." + "Ele colocou as cartas" (Zhou age) |
| 20 | KLEIN | CORRIGE | TREINADORA | "A cartomante segurou as cartas... disse: 'Me desculpe, esqueci de perguntar...'" — sujeito+verbo dela; "Me desculpe" é 1ª pessoa DELA |
| 21 | NARRADOR | CORRIGE | KLEIN | "Ele perguntou sem hesitar: 'Passado, presente e futuro.'" Parser: verbo+pronome ("Ele perguntou") não casa |
| 23 | NARRADOR | CORRIGE | TREINADORA | "A cartomante... disse: 'Então, por favor, embaralhe...'" — mesmo padrão seg17 |
| 24 | KLEIN | CONFIRMA | KLEIN | "Eu não perguntei" |
| 25 | UNKNOWN | CORRIGE | KLEIN | "Não haverá problemas...?" + "Ele colocou o baralho" (Zhou age) |
| 26 | UNKNOWN | CORRIGE | TREINADORA | "Sem problemas." + "A cartomante estendeu os dedos e puxou uma carta" (ela age) |
| 27 | UNKNOWN | CORRIGE | TREINADORA | "Esta carta simboliza o seu presente." + "A cartomante colocou a segunda carta" |
| 29 | UNKNOWN | CORRIGE | TREINADORA | "Esta carta simboliza o futuro." — sequência dela (seg28 narra ela pousando a 3ª carta) |
| 30 | KLEIN | CORRIGE | TREINADORA | "qual carta você gostaria de ver...? A cartomante levantou a cabeça... e fitou Zhou Mingrui" — sujeito dela; parser casou "Zhou" do vizinho (precedência errada, = cap4-seg57) |
| 31 | KLEIN | CONFIRMA | KLEIN | "disse Zhou Mingrui" |
| 34 | UNKNOWN | CORRIGE | TREINADORA | "O Louco," a cartomante leu suavemente" — leitura da carta. Parser: "leu/ler" fora do VERBS + papel fora do NAMES |
| 37 | UNKNOWN | CORRIGE | CARTOMANTE | "Por que está se passando por mim de novo!... é apenas uma treinadora de animais!" + seg38 (outra mulher, mais alta) = a VERDADEIRA chega brava |
| 39 | KLEIN | CORRIGE | TREINADORA | "A mulher que estava sentada... levantou-se e disse, descontente: 'Não se incomode... minha adivinhação...'" — a falsa se defendendo e fugindo (seg40 "trotar para fora") |
| 41 | UNKNOWN | CORRIGE | CARTOMANTE | "Senhor, gostaria que eu interpretasse...? a verdadeira cartomante olhou..." — sujeito explícito |
| 42 | NARRADOR | CORRIGE | KLEIN | "Os lábios de Zhou Mingrui tremeram e ele perguntou: 'É de graça?'" = pergunta do Klein |
| 43 | UNKNOWN | CORRIGE | CARTOMANTE | "...Não," respondeu a verdadeira cartomante." Parser: "respondeu"+artigo ("a verdadeira", minúsculo) não casa verbo-nome |
| 44 | UNKNOWN | CORRIGE | KLEIN | "Então, esqueça." + "Zhou Mingrui recolheu as mãos... agarrou revólver" |
| 46 | NARRADOR | HIPÓTESE | KLEIN | "Droga! Ele realmente arranjou um treinador de animais...?" — escárnio interno pós-tenda; sem 1ª pessoa |
| 47 | NARRADOR | HIPÓTESE | KLEIN | idem ("Um treinador... que não quisesse ser um adivinho...?") |
| 49 | UNKNOWN | CORRIGE | KLEIN | "Realmente não há o suficiente... Pobre Benson..." + "Zhou Mingrui não apenas havia gasto..." = lamento interno |
| 75 | NARRADOR | CORRIGE | KLEIN | "Se você não morreria se não estivesse cortejando a morte..." — seg74 atribui EXPLICITAMENTE: "um pensamento de escárnio surgiu na mente de Zhou Mingrui" |
| 80 | UNKNOWN | CORRIGE | KLEIN | "Que situação é essa?" + "Zhou Mingrui olhou em volta" — reação dele na névoa |
| 91 | UNKNOWN | CORRIGE | AUDREY | "Espelho, espelho, desperte..." + seg90 (Audrey na penteadeira) + seg94 ("Ela alternou entre muitas falas" = as falas 91-92 são dela) + anchor "Audrey Hall" |
| 92 | UNKNOWN | CORRIGE | AUDREY | "Em nome da família Hall, eu ordeno..." — "família Hall"=dela; idem |
| 95 | KLEIN | CORRIGE | AUDREY | "ela... disse em murmúrio suave: 'Papai estava mesmo mentindo...'" — sujeito "ela"=Audrey ("Papai" dela); 1ª pessoa de OUTRO contaminou o regex |
| 101 | ALGER | CONFIRMA | ALGER | "Alger murmurou" nome-verbo |
| 107 | UNKNOWN | HIPÓTESE | AUDREY | "Senhor, onde é isto?" — primeira voz assustada antes do uníssono (seg108); tom dela; sem marca textual — hipótese |
| 109 | UNKNOWN | HIPÓTESE | ALGER | "O que você planeja fazer?" — fala do uníssono (seg108 "falar em uníssono"); atribuído a Alger como porta-voz; hipótese |

## Correções (`--set`)
--set 8=NARRADOR --set 12=TREINADORA --set 14=TREINADORA --set 15=KLEIN
--set 17=TREINADORA --set 19=KLEIN --set 20=TREINADORA --set 21=KLEIN
--set 23=TREINADORA --set 25=KLEIN --set 26=TREINADORA --set 27=TREINADORA
--set 29=TREINADORA --set 30=TREINADORA --set 34=TREINADORA --set 37=CARTOMANTE
--set 39=TREINADORA --set 41=CARTOMANTE --set 42=KLEIN --set 43=CARTOMANTE
--set 44=KLEIN --set 49=KLEIN --set 75=KLEIN --set 80=KLEIN --set 91=AUDREY
--set 92=AUDREY --set 95=AUDREY

## Hipóteses
- --set 46=KLEIN --set 47=KLEIN (escárnio interno sem 1ª pessoa).
- --set 107=AUDREY --set 109=ALGER (ordem das vozes no uníssono, seg108; sem marca textual — confirmar c/ livro EN).

## Exceções do parser
1. Papel/função em minúsculas ("a cartomante", "a mulher", "a verdadeira cartomante") fora do NAMES → falas com verbo+papel viram UNKNOWN/narração (segs 12,17,23,34,43,106-cap4).
2. Verbos fora do VERBS: "questionou", "dizer", "leu/ler" (leitura de carta), "responder"+artigo (segs 15,17,34,43).
3. Verbo+pronome ele/ela (segs 21,42).
4. Precedência de vizinho sobre sujeito no próprio parágrafo (seg30 = cap4-seg57).
5. 1ª pessoa de OUTRO contamina pensamento-1p (segs 14,20,39,95 — o caso seg95 fecha o trio com cap3-seg52 e cap4-seg90).
6. Pensamento atribuído explicitamente ("surgiu na mente de Zhou", seg74-75) classificado como narração.

## Grafias
- "Tubarão Fantasma" (Ghost Shark — conferir termo canônico); "O Louco/O Mago/O Imperador/O Enforcado/A Temperança" ok (arcanos); "Backlund", "Loen" ok; "Cotovia"? n/a; "Sonia" (Mar Sonia ok).
