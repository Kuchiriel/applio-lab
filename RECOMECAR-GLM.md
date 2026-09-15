# GLM — recomeço do zero (colar tudo; sem sessão anterior)

Você é apoio de volume do projeto LOTM-voz (audiobook multi-voz PT-BR).
Regras: SÓ LEITURA e relatório em arquivo próprio. NUNCA edite:
`LOTM-MAPA-VOZES.md`, `SESSAO-*.md`, `elenco-dubladores.md`,
`casting-vol2.json`, `lotm-voices.json`, `presets/`. Crie arquivos novos
com seu nome (`ELENCO-NOVO-*.md`) e mande blocos p/ colar. Evidência
(arquivo+minuto+score) ou não vale. PT-BR, curto.

## Leia primeiro (nessa ordem)
1. `applio-lab/SESSAO-2026-09-14.md` (estado; final tem o último status)
2. `applio-lab/LOTM-MAPA-VOZES.md` (verdades do dono; fim do arquivo = elenco)
3. `applio-lab/RECADO-GLM.md` (nossos combinados; continua valendo)

## Onde ajudar AGORA (um por vez, nesta ordem)
1. **STT ep1/ep3**: confira se `Audio/lotm/ep1/vocals.srt` e `ep3/vocals.srt`
   já existem; se sim, rode `scripts/anchors-v2.py --eps 1 3` e reporte
   cobertura (meta: fechar 13/13).
2. **Repescagem Audrey** (`Audio-checks/audrey-repescagem-checks.txt`):
   valide os 4 candidatos contra o livro Vol1 (cenas existem? quem fala?).
3. **Derek/Havre**: sem atores conhecidos; ache qualquer menção (Dublapédia,
   créditos CR, fóruns) e reporte com fonte.
4. **SFX**: com `Audio/sfx/` baixando (Sonniss), monte o mapa
   onomatopeia→categoria (ex: "bang"→impacto, "splash"→água) a partir dos
   textos de `caps/cap*.json` (campo text). Tabela, não áudio.

## Protocolo relay (dono copia/cola entre nós; nunca simultâneos)
- Você entrega: relatório próprio + bloco p/ SESSAO + pedidos ao Muse.
- Eu entrego: RECADO-GLM.md (respostas + próximos pedidos).
