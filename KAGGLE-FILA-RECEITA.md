# Fila Kaggle — receita (aprendizado 2026-09-14)

## Limites (conta free)
- **MAX 2 sessões GPU concorrentes.** Push além = `Maximum batch GPU session count`
  e o kernel NEM É CRIADO (rejeição, não fila).
- `kernels status` 404 = sem sessão (nunca iniciou), não é falha.
- 400e no T4 ≈ 3–6h. Fila de N ≈ N×4h÷2 slots.
- Uploads ~70kB/s/arquivo (265 clips ≈ 1–2h). Ordem de push = prioridade.

## Procedimento
1. Upload dataset antes (`version` se existe, `create` se novo).
2. Push em até 2; **ler o retorno de cada push**.
3. Gerente em loop (`/tmp/opencode/kaggle-manager.sh`): conta RUNNING a cada
   15min; se <2 empurra o próximo; se COMPLETE baixa output.
4. Confirmar criação: `kernels list --search <slug>`.
5. T4 via metadata (`machine_shape: NvidiaTeslaT4`, `enable_gpu: true`, CLI 2.2.4
   do kvenv); provar GPU no cell1 (`nvidia-smi --list-gpus`).
6. Export: último `G_*.pth` + `added_*.index` → staging; G_ é checkpoint
   (extract p/ `_infer` depois).

## Padrão agente (qualquer fila longa)
Filas+vigias+logs em `/tmp/opencode/`; inhibitor no PID do worker;
guarda p/ timers; presets de voz versionados; nunca sobrescrever oficiais.
