# cap06-audit — Capítulo 6: Beyonder (primeira reunião na névoa)

Total: 79 segs | UNKNOWN 13 (todos resolvidos) | correções: 16

## Tabela (só UNKNOWN + KLEIN/NARRADOR suspeitos)

| seg | atual | veredito | falante-final | evidência |
|---|---|---|---|---|
| 1 | KLEIN | CONFIRMA | KLEIN | 1ª pessoa + repete silenciosamente as perguntas da dupla; solo |
| 9 | NARRADOR | CONFIRMA | NARRADOR | fala do Fool embedada em narração ("ele falou calmamente...: 'Uma tentativa.'") — design do parser |
| 13 | NARRADOR | CONFIRMA | NARRADOR | diálogo da Audrey embedado ("Ela perguntou...: 'Senhor, a tentativa acabou?...'") |
| 19 | KLEIN | CONFIRMA | KLEIN | pensamento 1ª pessoa ("eu sou o mestre") |
| 23 | NARRADOR | CONFIRMA | NARRADOR | fala do Fool embedada ("rindo levemente. 'É claro, se fizer um pedido formal...'") |
| 27 | NARRADOR | CONFIRMA | NARRADOR | diálogo da Audrey embedado ("Ela disse...: 'Esta é uma experiência...'") |
| 30 | KLEIN | CONFIRMA | KLEIN | "Eu também gostaria..." + "reclamou interiormente" |
| 38 | NARRADOR | CONFIRMA | NARRADOR | murmúrio da Audrey embedado ("A garota... murmurar: 'Que fascinante...'") |
| 39 | NARRADOR | CONFIRMA | NARRADOR | reação interna do Klein narrada ("É certamente fascinante... Zhou...") |
| 40 | NARRADOR | CONFIRMA | NARRADOR | frame narrativo, sem fala |
| 41 | UNKNOWN | CORRIGE→ALGER | ALGER | seg40: "Alger... abriu a boca e respondeu à pergunta de Audrey"; "Você é de Loen?" = início da resposta |
| 42 | UNKNOWN | CORRIGE→ALGER | ALGER | continuação da resposta (Igrejas); anchors-v2/ep1: Evernight Goddess / churches |
| 43 | UNKNOWN | CORRIGE→ALGER | ALGER | continuação; seg44 confirma: "prestava pouca atenção às palavras de Alger" |
| 47 | UNKNOWN | CORRIGE→AUDREY | AUDREY | seg46 "Audrey ouviu Alger terminar... antes de suspirar"; 1ª pessoa recusando Igrejas ("não quero perder minha liberdade") = Audrey |
| 48 | NARRADOR | CONFIRMA | NARRADOR | "Alger soltou uma risada baixa e disse...: 'Não se pode...'" embedado |
| 49 | NARRADOR | CONFIRMA | NARRADOR | "ela insistiu: 'Não há outras soluções?'" embedado (Audrey) |
| 50 | NARRADOR | CONFIRMA | NARRADOR | frame narrativo (Alger olha p/ o "homem misterioso") |
| 51 | NARRADOR | CONFIRMA | NARRADOR | "disse com deliberação: 'Tenho dois conjuntos...'" embedado (Alger) |
| 52 | NARRADOR | CONFIRMA | NARRADOR | frame narrativo; murmúrio do Klein mantido narrado (ver H2/E2) |
| 53 | UNKNOWN | CORRIGE→AUDREY | AUDREY | tag explícita: "'Sério? Quais são...?' Audrey claramente sabia..." |
| 54 | NARRADOR | CONFIRMA | NARRADOR | "respondeu sem pressa: 'Como você sabe...'" embedado (Alger) |
| 55 | UNKNOWN | CORRIGE→ALGER | ALGER | dono das fórmulas descreve 'Marinheiro'; seg48/51 contexto |
| 56 | UNKNOWN | CORRIGE→AUDREY | AUDREY | pergunta da ouvinte ("Parece ótimo...?") |
| 57 | UNKNOWN | CORRIGE→ALGER | ALGER | tag explícita: "Alger não parou e continuou. 'A segunda poção... Espectador'" |
| 58 | NARRADOR | CONFIRMA | NARRADOR | "Alger enfatizou: 'Você deve se lembrar...'" embedado |
| 59 | NARRADOR | CONFIRMA | NARRADOR | "ela falou...: 'Por quê?... me apaixonei por... Espectadora'" embedado (Audrey) |
| 60 | NARRADOR | CONFIRMA | NARRADOR | "dizer em voz grave: 'O sangue de Tubarões Fantasma...'" embedado (Alger) |
| 61 | KLEIN | CORRIGE→AUDREY | AUDREY | frame: "Audrey... perguntou com preocupação: 'Se eu conseguir... Como pode me prometer...'"; parser fisgou "me" da citação (falso 1p) |
| 62 | KLEIN | CORRIGE→ALGER | ALGER | frame: "Alger disse calmamente: 'Eu lhe darei um endereço...'"; parser fisgou "Eu" da citação (1ª pessoa DE OUTRO) |
| 63 | UNKNOWN | CORRIGE→ALGER | ALGER | continuação de Alger ("testemunho do misterioso senhor"); seg64 "ele direcionou o olhar para Zhou" = Alger |
| 65 | UNKNOWN | CORRIGE→ALGER | ALGER | "Vós" dirigido ao Fool; seg64 Alger olhando p/ Zhou |
| 66 | UNKNOWN | CORRIGE→AUDREY | AUDREY | tag: "Os olhos de Audrey brilharam, e ela concordou" |
| 68 | KLEIN | CORRIGE→AUDREY | AUDREY | seg67 "De sua perspectiva" = POV Audrey; "ousaríamos enganá-lo" ('-lo' = o cavalheiro, 3ª pessoa — Klein não se trataria por '-lo'); "o sujeito à minha frente" = Alger do assento dela; parser fisgou "eu" (falso 1p) |
| 70 | UNKNOWN | CORRIGE→AUDREY | AUDREY | seg69 "Audrey se virou... e olhou para Zhou com seriedade" + pedido à testemunha |
| 71 | NARRADOR | CONFIRMA | NARRADOR | "Ela perguntou apressadamente: 'Senhor, como devemos...?'" embedado |
| 72 | NARRADOR | CONFIRMA | NARRADOR | "Alger assentiu... e repetiu a mesma pergunta" embedado |
| 76 | UNKNOWN | CORRIGE→KLEIN | KLEIN | Fool assume o nome; seg75 Klein sorri + seg77 "O Louco" (persona Tolo — ver H1) |
| 77 | NARRADOR | CONFIRMA | NARRADOR | "Disse de maneira amável e calma: 'O Louco.'" embedado |

## Correções (`relabel --set`)

```
--set 41=ALGER --set 42=ALGER --set 43=ALGER --set 47=AUDREY --set 53=AUDREY
--set 55=ALGER --set 56=AUDREY --set 57=ALGER --set 61=AUDREY --set 62=ALGER
--set 63=ALGER --set 65=ALGER --set 66=AUDREY --set 68=AUDREY --set 70=AUDREY
--set 76=KLEIN
```

## Hipóteses

- H1: falas do Fool (seg76 + cap07 segs 11,16,36-38,58,80) = persona TOLO do mesmo ator; separar por conteúdo futuramente. Por ora KLEIN.
- H2: seg52 "Sequência 9? Zhou murmurou" — murmúrio real do Klein, mas mantido NARRADOR (murmúrio narrado, sem voz própria no render atual).

## Exceções do parser (não consertar aqui)

- E1 `pensamento-1p`: dispara com "me/Eu/eu" DENTRO de citação de outro (segs 61,62,68). Falta regra: ignorar 1ª pessoa dentro de "..." quando há frame "X perguntou/disse:".
- E2 `speaker_of` ignora verbo de fala em parágrafo de narração (seg52 "Zhou Mingrui murmurou" → narração por acaso correto; verbo+nome só vale p/ parágrafo com travessão).
- E3 diálogo embedado em narração fica todo NARRADOR por design (segs 9,13,23,27,38,39,48,49,51,54,58,59,60,71,72,77) — correto p/ render atual, mas impede voz do personagem na citação.
