#!/usr/bin/env python3
"""apply-audit — aplica --sets de audit por TEXTO (índices mudam no reparse).
Uso: python3 apply-audit.py <capNN.json novo> <capNN-audit.md> <capNN.json antigo (git)>
Retorna: aplicados, ignorados.
"""
import json
import re
import subprocess
import sys

segpath, audpath = sys.argv[1:3]
oldpath = sys.argv[3] if len(sys.argv) > 3 else None
data = json.load(open(segpath))
aud = open(audpath).read()
oldsegs = {}
if oldpath:
    oldsegs = {s["i"]: s["text"] for s in json.load(open(oldpath))["segments"]}
ap, ign = [], []
for m in re.finditer(r"--set\s+(\d+)=([A-Za-z-]+)", aud):
    i, who = int(m.group(1)), m.group(2)
    oldtxt = oldsegs.get(i)
    if not oldtxt:
        ign.append((i, who, "sem-texto-antigo"))
        continue
    hit = next((s for s in data["segments"] if s["text"] == oldtxt), None)
    if hit is None:
        hit = next((s for s in data["segments"]
                    if oldtxt[:50] in s["text"] or s["text"][:50] in oldtxt), None)
    if hit is None:
        ign.append((i, who, oldtxt[:50]))
        continue
    hit["speaker"] = who
    hit["conf"] = (hit.get("conf", "") + "+audit").strip("+")
    ap.append((i, who))
print("aplicados: %d ignorados: %d" % (len(ap), len(ign)))
for x in ign:
    print("  IGN:", x)
if ap:
    json.dump(data, open(segpath, "w"), ensure_ascii=False, indent=1)
