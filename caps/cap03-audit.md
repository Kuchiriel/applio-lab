# cap03 — audit (74 segs: 0-73) — "Melissa"

Fontes: texto literal+verbo; wiki Episode_1 (caps 1-14: Melissa acorda pontual,
relógio de bolso, café com pão de centeio, lista de compras, Benson fora);
anchors ep1 (spans domésticos, sem falas EN×PT decisivas aqui); parser.

## Tabela

| seg | atual | veredito | final | evidência |
|---|---|---|---|---|
| 10 | UNKNOWN | CORRIGE | KLEIN | "Melissa está acordada..." + "Zhou Mingrui sorriu" — pensamento do Zhou (memória de Klein: "como se ela fosse sua irmã"). Parser: "sorriu" fora do VERBS |
| 11 | KLEIN | CONFIRMA | KLEIN | "eu não tenho uma irmã" 1ª pessoa |
| 25 | KLEIN | CONFIRMA | KLEIN | "minha cabeça" 1ª pessoa |
| 27 | UNKNOWN | CORRIGE | MELISSA | "O que aconteceu?" + "Melissa olhou curiosa ao ouvir a comoção" (reação à gaveta batida, seg26). Parser: "olhou" fora do VERBS |
| 35 | UNKNOWN | CORRIGE | KLEIN | "Parece que quebrou de novo." + "Ele olhou para a irmã" + seg36 "tentava encontrar um assunto de conversação" = fala do Zhou p/ Melissa |
| 42 | UNKNOWN | CORRIGE | MELISSA | "Está certo agora", ela disse" — "ela"=Melissa (conserta relógio, segs 37-41). Parser: verbo+pronome ("ela disse") não casa (só nome próprio) |
| 45 | NARRADOR | HIPÓTESE | KLEIN | "Por que sua expressão continha...?" — pergunta retórica POV interno, cadeia 45-50 (seg49 KLEIN). Sem 1ª pessoa explícita → hipótese |
| 46 | NARRADOR | HIPÓTESE | KLEIN | idem ("Seria um olhar de amor... por um irmão retardado?") |
| 49 | KLEIN | CONFIRMA | KLEIN | "vou considerá-lo como suicídio" 1ª pessoa |
| 50 | NARRADOR | CORRIGE | KLEIN | "Ela estava dormindo...? Ou o suicídio de Klein está envolto em mistério?" — continuação direta do seg49 (mesma dedução). Parser: sem 1ª pessoa → narração |
| 52 | KLEIN | CORRIGE | MELISSA | "Klein, tire todo o pão restante..." + "ela dizia com uma voz doce" — vocativo "Klein" (Klein não fala o próprio nome) + sujeito "ela". Parser: "Vou fazer" (fala DELA em 1ª pessoa) contaminou o regex pensamento-1p |
| 57 | NARRADOR | CORRIGE | MELISSA | "Lembre-se de comprar pão fresco..." — continuação do discurso da Melissa (seg52) |
| 58 | NARRADOR | CORRIGE | MELISSA | idem ("compre o carneiro e as ervilhas") |
| 60 | UNKNOWN | CORRIGE | KLEIN | "Certo." = resposta do Zhou (padrão confirmado no seg68 "Certo. Sem problemas, respondeu Zhou Mingrui") |
| 66 | NARRADOR | CORRIGE | MELISSA | "Klein, não compre muito carneiro..." + "dizendo" (virou o corpo na porta). Parser: "dizendo" (gerúndio) fora do VERBS |
| 67 | NARRADOR | CORRIGE | MELISSA | continuação ("só precisamos de oito libras de pão") |
| 68 | KLEIN | CONFIRMA | KLEIN | "respondeu Zhou Mingrui" verbo-nome+alias |
| 73 | KLEIN | CONFIRMA | KLEIN | "eu realmente desejo voltar" 1ª pessoa |

## Correções (`--set`)
--set 10=KLEIN --set 27=MELISSA --set 35=KLEIN --set 42=MELISSA
--set 50=KLEIN --set 52=MELISSA --set 57=MELISSA --set 58=MELISSA
--set 60=KLEIN --set 66=MELISSA --set 67=MELISSA

## Hipóteses
- --set 45=KLEIN --set 46=KLEIN (monólogo interno sem marca 1ª pessoa; cadeia 45-50).

## Exceções do parser
1. Verbo de ação/estado ("sorriu/olhou") + nome não é fala → resíduo; decisão exige contexto (segs 10, 27).
2. Verbo de fala + pronome ele/ela → resíduo/ALT (seg42 "ela disse").
3. Gerúndio "dizendo" fora do VERBS (seg66).
4. Fala de OUTRO em 1ª pessoa ("Vou fazer", seg52) dentro de parágrafo narrativo contamina o regex pensamento-1p — caso canônico da regra "1ª pessoa de OUTRO condena".
5. Pergunta-dedução sem 1ª pessoa classificada como narração (seg50 vs seg49).

## Grafias
- "Khoy" (conferir); "Backlund", "Feysac", "Loen" ok; "oito libras" + conversão p/ meio quilo (seg61, exposição correta).
