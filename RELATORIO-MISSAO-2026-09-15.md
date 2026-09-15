# Relatório — auditoria caps 2-12 + integração (missão ChatGPT 15/09)

## Estado
- arquivos analisados: ~60 (código, caps, anchors, presets, docs, testes)
- capítulos auditados: 11 (caps 2-12, 1062 segmentos)
- UNKNOWN resolvidos: 181/181 (44+78+59)
- correções propostas: 265 `--set` (NÃO aplicadas — caps/*.json protegidos,
  aguardam revisão do dono)
- hipóteses pendentes: 22 (monólogo sem 1ª pessoa, uníssono, vozes novas)
- SFX catalogados: 16 (+ sfx-map.json do cap01)
- blockings: 11/11 criados; validador: 0 erros

## Achados críticos
1. Parser perde nome fora de NAMES (Wendy etc.) — falha mais cara caps 4-5.
2. `vizinho` atropela sujeito explícito (cap08, cap12 segs 25/38: KLEIN que
   era Dunn — 1ª pessoa alheia condena).
3. Falso-1p: 1ª pessoa DE OUTRO contamina pensamento-1p (caps 3/5/11).
4. Aspas retas do diário → UNKNOWN em massa (cap09).
5. RVC achata ?/! (medido pyin). Chiado "s" = resíduo RVC (medido).
6. CLI `speak` não expunha `--style` (CORRIGIDO).
7. SFX_WORDS sem clop/clinque/clangue (CORRIGIDO) + VERBS +3 (CORRIGIDO).

## Melhorias aplicadas (mínimas, testadas)
- VERBS += retrucou/exalou/questionou/leu; SFX += clop/clinque/clangue.
- CLI --style exposto + passthrough.
- scripts/validate-caps.py (0 erros), scripts/verify-render.py.

## Hipóteses pendentes
- Dunn v4 (68/4.7min) resolve? Treino travado sem quota Kaggle (reset 19/09).
- Khoy "Coz" (samples p/ ouvido). Index_rate ótimo p/ ?/! (sem teste).
- 7 rótulos novos sem voz (CAPITAO, ANNIE, CONDE-HALL...). TOLO split futuro.

## Integração LOTM→NixOS-AI
1. Interface usada: `speak()` batch + `clone_many()` direto. 2. Oferecida:
   mesma + CLI. 3. Compatíveis após fix --style. 4. Duplicação: STT turbo
   só no lab (jarvis default small/cpu). 5. RVC resolvido igual
   (_resolve_rvc). 6-11. index/pitch/idioma/style preservados no profile.
   12. playback separado (play flag). 13. voice.py: nenhuma mudança
   necessária além do --style (feito). 14-15. resto nice-to-have.
