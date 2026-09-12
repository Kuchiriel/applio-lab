# Receita: melhorar Jarvis .pth/.index (medido 2026-09-12)

Dataset `kuchiriel/jarvis`: 7 clips, **2.8 min**, 48kHz consistente,
RMS ~0.07 (sem clipping, sem silêncio dominante). Tamanho: TINY.

Modelo atual: 62 epochs (`Jarvis_62e_434s_best_epoch.pth`).

## Diagnóstico (docs Applio + studio guides)

- Dataset tiny (1–3 min) pede **400–500 epochs** (docs: 200–400 geral;
  studio rule: tiny = 400–500). 62e = provavelmente undertrained.
- Risco: overfit (dataset pequeno memoriza). Mitiga: TensorBoard
  (curva g/total loss), save a cada 25, escolhe pré-overfit.
- Batch 4 (dataset curto), RMVPE, pretrained G/D ligado, 48kHz.

## Receita Kaggle T4x2 (cells 1–3 do lab)

1. Cell 1 (install) + upload dataset (já existe `kuchiriel/jarvis`).
2. Preprocess 48kHz → Extract RMVPE → Train: batch 4, 400 epochs,
   save every 25, pretrained ON, TensorBoard ligado.
3. Para quando a curva achatar/piorar (esperado 250–400).
4. Train Index (faiss) → Cell 3 exporta `.pth` + `.index`.
5. Troca em `~/models/` + teste `jarvis speak --clone` antes/depois.

## Não fazer

- Não treinar do zero sem pretrained (desperdício em dataset tiny).
- Não usar Silverhand p/ Jarvis (outra voz/outro projeto).
- Não confiar em epoch alto sozinho: ouvir checkpoint conta mais.
