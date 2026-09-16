#!/usr/bin/env python3
"""selfref-bench — ponto ótimo de passes (papers: saturação 2-3, viés cresce).
Ground truth: 275 vereditos dos audits caps 2-12 (inv265).
Passes: P0=parser atual; P1=+attrib-llm; P2=+review-grounded 1×;
P3=+review 2×. Gate DISC: só revisa divergência; early stop em acordo.
Métricas por pass: acurácia, melhorias, degradações, ratio I/D.
Uso: kvenv/bin/python selfref-bench.py [--n 40]
"""
import json
import os
import random
import sys

sys.path.insert(0, "/home/nixos/projects/applio-lab")
sys.path.insert(0, "/home/nixos/projects/nixos-ai/modules/ai/jarvis/src")

N = int(sys.argv[sys.argv.index("--n") + 1]) if "--n" in sys.argv else 40
inv = json.load(open("/tmp/opencode/inv265.json"))
random.seed(7)
sample = random.sample(inv, min(N, len(inv)))

from jarvis.providers.llm import LLMClient
from jarvis.core.config import Config

client = LLMClient(Config())
EL = ("KLEIN, NARRADOR, MELISSA, BENSON, DUNN, LEONARD, ALGER, AUDREY, DALY,"
      " NEIL, ROZANNE, SFX, UNKNOWN")


def ask(prompt, tokens=600):
    r = client.chat_with_tools(
        messages=[{"role": "user", "content": prompt}],
        max_tokens=tokens, temperature=0.1,
        extra={"chat_template_kwargs": {"enable_thinking": False}})
    return r.content or ""


import re


def parse_sp(txt):
    m = re.search(r"(KLEIN|NARRADOR|MELISSA|BENSON|DUNN|LEONARD|ALGER|AUDREY|"
                  r"DALY|NEIL|ROZANNE|SFX|UNKNOWN)", txt)
    return m.group(1) if m else "UNKNOWN"


def quote_grounded(txt, seg):
    for m in re.finditer(r"[\"“]([^\"”]{8,})[\"”]", txt):
        if m.group(1) in seg:
            return True
    return False


res = []
for k, o in enumerate(sample):
    d = json.load(open(
        "/home/nixos/projects/applio-lab/caps/cap%s.json" % o["cap"]))["segments"]
    seg = next((s["text"] for s in d if s["text"][:60] == o["txt"][:60]), o["txt"])
    truth, cur = o["prop"], o["atual"]
    row = {"id": "%s:%d" % (o["cap"], o["i"]), "truth": truth, "p0": cur,
           "ok0": cur == truth}
    # P1: atribuição direta
    t1 = ask("Romance LOTM PT-BR. Quem fala? Responda só FALANTE - evidência.\n"
             "Elenco: %s.\nKlein=Zhou Mingrui. 1ª pessoa=KLEIN. Narração=NARRADOR.\n"
             "Texto: %s" % (EL, seg[:400]))
    v1 = parse_sp(t1)
    row.update({"p1": v1, "ok1": v1 == truth})
    # P2/P3: revisão com gate (só se divergir do P1; early stop em acordo)
    v, ok = v1, row["ok1"]
    for p in (2, 3):
        if v == cur:
            row["stop%d" % p] = "acordo"
            break
        t = ask("REVISOR. Veredito atual: %s. Texto: %s\n"
                "CONFIRME com CITAÇÃO EXATA copiada do texto, ou REFUTE com outro "
                "FALANTE + citação exata. Proibido paráfrase." % (v, seg[:400]),
                tokens=400)
        if not quote_grounded(t, seg):
            row["stop%d" % p] = "sem-evidencia"
            break
        v = parse_sp(t)
        row["p%d" % p] = v
        row["ok%d" % p] = (v == truth)
    row["pfinal"] = v
    row["okfinal"] = (v == truth)
    res.append(row)
    print("%s truth=%s p0=%s p1=%s final=%s" % (
        row["id"], truth, cur, v1, v), flush=True)

json.dump(res, open("/tmp/opencode/selfref-%d.json" % N, "w"), ensure_ascii=False)
for p in ("ok0", "ok1", "okfinal"):
    acc = sum(1 for r in res if r.get(p)) / len(res)
    print("%s: %.2f" % (p, acc))
