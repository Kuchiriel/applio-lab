# LOTM — Mapa de vozes ep1 (evidência, não palpite)

> Regra: rótulo só com prova (STT + livro ou ouvido do dono).
> Hipótese marcada como HIPÓTESE até prova.

## Amostras (ouvido do dono, 2026-09-12)
- voz-0 (254Hz): KLEIN diálogo, COM efeitos/sonoros (dono 2026-09-12). Limpar antes de treinar.
- voz-1 (104Hz): MISTO nessa ordem — Klein + AUDREY HALL + SR. TOLO/LOUCO (névoa) (dono 2026-09-12).
  Guardar separador: voz do Tolo serve p/ cenas da névoa cinzenta no livro.
- voz-2 (103Hz): KLEIN narração, LIMPO — base do dataset (dono 2026-09-12; STT mostra
  exposição + pensamento interno verbatim do livro.)
- voz-3 (180Hz): TARÓLOGA/cuidadora + AUDREY no fim (dono 2026-09-12).

## Provas STT × livro (Vol 1, ~/Books)
- "Será que é algo como uma hemorragia cerebral?" — livro CONFIRMA (pensamento
  do Klein, cap.1). Falado no cluster 2 → cluster 2 contém voz do Klein.
- "névoa cinzenta" 73 hits / "Senhor Tolo" 3 hits / "Audrey" 469 hits no livro
  → termos-âncora p/ rotular falas futuras por conteúdo, não por F0.
- Nomes próprios saem mangled no STT (Beyonder→"Bionde", Antigonus→?, Augustus).
  Não usar nome próprio como chave de filtro.

## Clusters MFCC k=6 (ep1, demucs vocals, 20.3min fala)
- c2: 61 segs / 10.5min / 103Hz — Klein narração (CONFIRMADO dono+livro).
- c1: 41 segs / 5.8min / 104Hz — MISTO (leitura do caderno + diálogos; pode ter
  Benson/Melissa + Klein). NÃO assumir Klein puro.
- c0: 13 segs / 1.3min / 254Hz — Klein diálogo (dono) + checar contaminação.
- c3: 20 segs / 2.0min / 180Hz — cuidadora + Audrey (dono).
- c4/c5: migalhas (<0.5min) — ignorar por ora.

## Filtro v1 (atual, fraco)
- MFCC-13 mean+std + KMeans k=6. Separa estilo (narração×diálogo), NÃO
  personagem: c1 e c2 têm mesmo F0 e o mesmo falante pode estar nos dois.
- Próxima iteração: embeddings de falante (ECAPA) + âncoras de conteúdo
  (termos do livro) por segmento. Escalar p/ +episódios só com filtro v2.

## Datasets
- kuchiriel/jarvis (Kaggle): 7 clips, 2.8min — base do 300e.
- kuchiriel/klein-lotm (Kaggle, CRIADO 2026-09-12, PRIVADO): 60 clips, 10.4min
  de c2+c0. ⚠️ ROTULAGEM PRELIMINAR — revalidar com filtro v2 antes de treinar.
- Backup voz "divindade" (narrador grave c2-exposição): amostra em
  /tmp/opencode/lotm-amostra-klein.wav (perdida no reboot? re-extrair se preciso).
