#!/usr/bin/env python3
"""relabel-conteudo — auditoria de pool por CONTEUDO (anchors-v2), v1.

Cada clip do pool chama-se epN-SSSSS.wav (segundo de inicio; slice-pools.py).
Janela = [start-2, start+17). Cruza com epN/anchors-v2.json (spans EN x PT)
e classifica pelos anchors canonicos da janela:
  SELF    - anchors compativeis com o dono do pool (p/ klein-v3: klein,
            moretti, seer, the fool, tarot club, clown)
  OUTRO   - janela ancorada em personagem/titulo alheio (suspeito de pool
            errado; MENCAO pode enganar — dono decide no ouvido)
  SEM-ANC - janela sem ancora (conteudo nao decide; timbre manda)
  VAZIO   - sem spans na janela (fora da cobertura EN)
Cruza com pureza-report.json (timbre) e mostra concordancia/divergencia.
PROPOSTA apenas — nada e movido.
Uso: /tmp/opencode/kvenv/bin/python relabel-conteudo.py --pool klein-v3
"""
import argparse
import glob
import json
import os
import re

AUD = os.path.expanduser("~/Audio/lotm")
DS = os.path.join(AUD, "datasets")

# anchors compativeis com cada pool (prefixo do nome -> set de anchors)
SELF = {
    "klein": {"klein", "moretti", "seer", "the fool", "tarot club", "clown"},
    "levi": {"levi"},  # Ataque dos Titãs; anchors EN não cobrem — vira SEM-ANC
    "dunn": {"dunn", "dunn smith"},
    "neil": {"neil"},
    "leonard": {"leonard", "leonard mitchell"},
    "daly": {"daly", "daly simone"},
    "alger": {"alger", "alger wilson", "the hanged man"},
    "audrey": {"audrey", "audrey hall", "justice"},
}
# Co-ocorrência por ENREDO (cenas do pool SEMPRE têm esses presentes):
# âncora deles na janela não condena (diálogo Klein<->Dunn/Neil constante).
AMBIG = {
    "dunn": {"klein", "moretti", "nighthawks", "leonard"},  # Leonard = parceiro de cena
    "neil": {"klein", "moretti", "nighthawks", "chanis gate", "dunn"},  # colega de escritório
    "leonard": {"klein", "moretti", "nighthawks", "dunn"},
    "daly": {"klein", "moretti", "spirituality"},
    "alger": {"klein", "tarot club", "the fool"},
    "audrey": {"klein", "tarot club", "the fool", "alger"},
}
# Co-ocorrência por ENREDO (cenas do pool SEMPRE têm esses presentes):
# âncora deles na janela não condena (diálogo Klein<->Dunn/Neil constante).
AMBIG = {
    "dunn": {"klein", "moretti", "nighthawks", "leonard"},  # Leonard = parceiro de cena
    "neil": {"klein", "moretti", "nighthawks", "chanis gate", "dunn"},  # colega de escritório
}
# outros anchors conhecidos (tudo que não é SELF nem vazio vira OUTRO)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pool", default="klein-v3")
    ap.add_argument("--win-before", type=float, default=2.0)
    ap.add_argument("--win-after", type=float, default=17.0)
    a = ap.parse_args()
    poolkey = a.pool.split("-")[0]
    self_ok = SELF.get(poolkey, {poolkey})
    ambig = AMBIG.get(poolkey, set())

    pureza = {}
    pr = os.path.join(DS, "pureza-report.json")
    if os.path.exists(pr):
        rep = json.load(open(pr))
        for c, v in rep.get(a.pool, {}).get("clips", {}).items():
            pureza[c] = v

    clips = sorted(glob.glob(os.path.join(DS, a.pool, "ep*.wav")))
    out, counts = {}, {"SELF": 0, "AMBIG": 0, "OUTRO": 0, "SEM-ANC": 0, "VAZIO": 0}
    cross = []
    for f in clips:
        base = os.path.basename(f)
        m = re.match(r"ep(\d+)-(\d+)\.wav", base)
        if not m:
            continue
        ep, start = int(m.group(1)), int(m.group(2))
        w0, w1 = start - a.win_before, start + a.win_after
        av = os.path.join(AUD, "ep%d" % ep, "anchors-v2.json")
        spans = []
        if os.path.exists(av):
            for s in json.load(open(av))["spans"]:
                if s["t1"] > w0 and s["t0"] < w1:
                    spans.append(s)
        anchors = sorted({x for s in spans for x in s["anchors"]})
        others = [x for x in anchors if x not in self_ok and x not in ambig]
        if not spans:
            ver, det = "VAZIO", []
        elif not anchors:
            ver, det = "SEM-ANC", []
        elif others:
            ver, det = "OUTRO", others
        elif any(x in ambig for x in anchors):
            ver, det = "AMBIG", [x for x in anchors if x in ambig]
        else:
            ver, det = "SELF", [x for x in anchors if x in self_ok]
        counts[ver] += 1
        tim = pureza.get(base, {})
        out[base] = {
            "ep": ep, "start": start, "janela": [round(w0, 1), round(w1, 1)],
            "veredito": ver, "anchors_outro": det, "anchors": anchors,
            "pt": " | ".join(s["pt"][:60] for s in spans[:3]),
            "timbre": {"best": tim.get("best"), "sim": tim.get("sim")},
        }
        flag_t = tim.get("best") == "AUDREY" and max(tim.get("sim", {}).values() or [0]) >= 0.5
        cross.append((base, ver, tim.get("best"), flag_t))

    json.dump(out, open(os.path.join(DS, a.pool + "-relabel.json"), "w"),
              ensure_ascii=False, indent=1)
    n = sum(counts.values())
    print("== %s: %d clips — veredito por CONTEUDO ==" % (a.pool, n))
    for k, v in counts.items():
        print("  %-7s %3d (%.0f%%)" % (k, v, 100 * v / max(n, 1)))
    print("\n== OUTRO (detalhe; MENCAO pode enganar) ==")
    for base, v in out.items():
        if v["veredito"] == "OUTRO":
            print("  %-18s %s" % (base, ",".join(v["anchors_outro"])))
    n_ambig = sum(1 for v in out.values() if v["veredito"] == "AMBIG")
    print("  (AMBIG %d — co-ocorrência por enredo, não condena)" % n_ambig)
    print("\n== CRUZAMENTO timbre x conteudo ==")
    agree = sum(1 for _, ver, best, _ in cross
                if (ver == "OUTRO") == (best == "AUDREY"))
    print("  concordancia: %d/%d" % (agree, len(cross)))
    print("  -- timbre acusa (AUDREY>=.5) mas conteudo nao:")
    for base, ver, best, ft in cross:
        if ft and ver != "OUTRO":
            print("     %-18s conteudo=%s" % (base, ver))
    print("  -- conteudo acusa (OUTRO) mas timbre nao:")
    for base, ver, best, ft in cross:
        if ver == "OUTRO" and not ft:
            print("     %-18s timbre=%s" % (base, best))
    print("\nrelatorio:", os.path.join(DS, a.pool + "-relabel.json"))


main()
