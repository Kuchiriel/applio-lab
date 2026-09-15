#!/usr/bin/env python3
"""blocking-gen — blocking padrão quando não há audit (capítulos simples).
Uso: python3 blocking-gen.py caps/capNN.json
Gera caps/capNN-blocking.json: 1 bloco por ~15 segs, Klein alterna
centro-esquerda/direita por bloco (variação mínima honesta), SFX
detectados por léxico. Marcar "hipotese": true (posição não lida da cena).
"""
import json
import re
import sys

segpath = sys.argv[1]
data = json.load(open(segpath))
segs = data["segments"]
SFXHINT = re.compile(r"[!…]\s*$")
blocks = []
poss = ["centro-esquerda", "direita"]
bi = 0
for a in range(0, len(segs), 15):
    chunk = segs[a:a + 15]
    sfx = [s["i"] for s in chunk if s["speaker"] == "SFX"]
    blocks.append({
        "id": chr(65 + bi), "segs": [chunk[0]["i"], chunk[-1]["i"]],
        "local": "hipotese",
        "klein": {"pos": poss[bi % 2], "nota": "auto, revisar na leitura da cena"},
        "hipotese": True, "sfx_segs": sfx})
    bi += 1
out = {"capitulo": int(re.search(r"cap(\d+)", segpath).group(1)),
       "titulo": data.get("title", ""),
       "narrador": {"pos": "centro-frente", "nota": "fogueira, nunca move"},
       "blocos": blocks}
json.dump(out, open(segpath.replace(".json", "-blocking.json"), "w"),
          ensure_ascii=False, indent=1)
print("blocking: %d blocos (hipotese)" % len(blocks))
