# FASE 2 — relatório (missão ChatGPT 15/09)

## Parser: 275 → 54 auto + 172 relabel + 48 outro (+1 sem-match)
- Causas raiz (não 275 bugs): vizinho⊃sujeito, falso-1p, NAMES incompleto,
  aspas-diário, diálogo sem atribuição, SFX-léxico, epítetos.
- Fixes: EPITHETS (Dunn×2, Leonard), epiteto-forte, sujeito-narracao±vn,
  nome-verbo-longo, pergunta-avulsa (?+1p/¬3p), diario-lendo, leitura,
  cont-dialogo (só diálogo ativo, sem endereçamento), VERBS+9, NAMES+2
  (Wendy, Annie), SFX repeat-char.
- Regressões pegas e revertidas: citacao→NARRADOR global (169),
  cont-dialogo agressivo, pergunta !-declarativa (cap01: 6).
- Cap01: 0 diffs. Golden: 14/14. Validador: real (achava vacuo antes).

## Classificação 275
- PARSER_BUG absorvidos: 54 (onomatopeia 14, sujeito 19, epithet 6,
  pergunta-avulsa 6, verbo-nome 7, nome-verbo-longo 5 — alguns overlap).
- DATA_EXCEPTION (relabel): 172 entradas em
  `personagens/RELABELS-PENDENTES-caps2-12.json` (171 únicas + 1 duplicada;
  contagem anterior dizia 173 — corrigido na preservação 15/09) — diálogo
  sem atribuição (UNKNOWN honesto), falantes sem voz
  (VENDEDOR/TREINADORA/CARTOMANTE/CAPITAO...), cena.
- NARRATIVE_EXCEPTION:uotro 48 — diário (KLEIN vs audit NARRADOR: CONFLITO
  registrado, minha decisão: quem lê em voz alta é o Klein; dono decide
  no ouvido), CAPITAO/HOMEM-LOIRO (sem voz), CARTOMANTE→KLEIN fallback.
- INSUFFICIENT: 22 hipóteses dos audits (mantidas).
- UPSTREAM: splits/merges (2 sem-match).

## RVC/TTS/STT/integração
- RVC ?/!: sem novos testes (mesmo resultado fase 1). index_rate sweep e
  f0_method: NÃO TESTADO (CPU ok, mas priorizado parser;&_JOB futuro).
- Chiado "s": hipótese resíduo-RVC mantida; gate adiado (filtro quebrou
  tudo 1× — regra: testar em sample).
- STT: lab turbo/cuda vs jarvis small/cpu — divergência documentada, sem
  troca (P4 manda medir; medição pendente de janela GPU).
- Cache: salt v3 invalida em mudança de regra (bug do "volta o erro"
  corrigido). Teste pitch→rerun em curso.
- Contrato: --style exposto no CLI (fase 1). Voice profile atual resolve
  base/voice/rate/speed/style/rvc/pitch/index_rate — sem schema novo.
- Performance: base Edge ~5-15s/seg; kokoro ~10s/seg; RVC CPU ~1-2min/seg
  em lotes de 5; render cap01 ≈ 40-70min.

## Pendências reais
- Dono: aplicar 172 relabels? (patch preservado em
  `personagens/RELABELS-PENDENTES-caps2-12.json`; caps protegidos — SEM
  autorização, não apliquei).
- Dono ouvido: diário KLEIN×NARRADOR (cap09), Khoy, ?/!.
- Quota Kaggle reset 19/09 (dunn-v4/melissa).
- STT turbo no jarvis (comparar antes).

## Cache: TESTADO
- Mudança de pitch (2→5) refez RVC ([rvc], não [cache-rvc]) — salt v3 OK.
- Limitação: --only exige .parts de render completo (assembly itera todos).
  Delta real = mesmo --out de antes. Documentado, sem fix agora.
