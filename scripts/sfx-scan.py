#!/usr/bin/env python3
"""sfx-scan — varre caps com o dicionário HD (cena + onomatopeia).
Uso: python3 sfx-scan.py caps/capNN.json
Saída: cues seg Policei | categoria | keyword | arquivo SFX (ou FALTA).
Base: hd-import/sound_effects.json (112 linhas, PT-BR).
"""
import json
import sys

D = json.load(open("/home/nixos/projects/applio-lab/hd-import/sound_effects.json"))
segs = json.load(open(sys.argv[1]))["segments"]
cues = []
for s in segs:
    t = s["text"]
    tl = t.lower()
    for cat, info in D.get("sound_effects", {}).items():
        for kw in info.get("keywords", []):
            if kw.lower() in tl:
                cues.append((s["i"], s["speaker"], cat, kw, info.get("file")))
                break
    for ono in D.get("onomatopoeia", []):
        if ono.lower() in tl and s["speaker"] != "SFX":
            cues.append((s["i"], s["speaker"], "onomatopeia-falada", ono, None))
print("cues: %d" % len(cues))
have = {"rain", "wind", "fire", "ocean"}
for i, sp, cat, kw, f in cues:
    print("[%d] %s | %s | %s | %s" % (
        i, sp, cat, kw[:40], f if f else "FALTA-arquivo"))
