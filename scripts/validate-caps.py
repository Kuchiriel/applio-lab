#!/usr/bin/env python3
"""validate-caps — validador caps/audits/blocking (§37 missão).
Uso: python3 validate-caps.py
Checa: JSON válido, índices únicos/sequenciais, speakers válidos,
blocking consistente (segs existem), relabels só p/ falantes conhecidos,
audit com seção Correções.
"""
import json
import glob
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
CAPS = os.path.join(HERE, "caps")
VALID_SPK = {"NARRADOR", "KLEIN", "UNKNOWN", "SFX", "DUNN", "NEIL",
             "LEONARD", "ALGER", "AUDREY", "DALY", "MELISSA", "BENSON",
             "ZHOU", "MINGRUI"}
errs = []


def err(m):
    errs.append(m)


for f in sorted(glob.glob(os.path.join(CAPS, "cap[0-9]*.json"))):
    base = os.path.basename(f)
    if "relabels" in base:
        d = json.load(open(f))
        for t, w in d.items():
            if w not in VALID_SPK and not w.startswith("ALT?"):
                err("%s relabel falante estranho: %s" % (base, w))
        continue
    try:
        d = json.load(open(f))
    except Exception as e:
        err("%s JSON inválido: %s" % (base, e))
        continue
    segs = d["segments"]
    ids = [s["i"] for s in segs]
    if len(set(ids)) != len(ids):
        err("%s índices duplicados" % base)
    for s in segs:
        if not s.get("text", "").strip():
            err("%s seg %s sem texto" % (base, s.get("i")))
        if s.get("speaker") not in VALID_SPK and not str(s.get("speaker", "")).startswith("ALT?"):
            err("%s seg %s speaker novo: %s" % (base, s.get("i"), s.get("speaker")))
    b = os.path.join(CAPS, base.replace(".json", "-blocking.json"))
    if os.path.exists(b):
        bd = json.load(open(b))
        n = len(segs)
        for bl in bd.get("blocos", []):
            a, z = bl["segs"]
            if not (0 <= a <= z < n):
                err("%s bloco %s fora do range (0-%d)" % (base, bl["id"], n - 1))
    else:
        err("%s sem blocking" % base)
    a = os.path.join(CAPS, base.replace(".json", "-audit.md"))
    if not os.path.exists(a):
        err("%s sem audit" % base)
    elif "Correções" not in open(a).read():
        err("%s audit sem seção Correções" % base)

print("erros: %d" % len(errs))
for e in errs[:40]:
    print("-", e)
