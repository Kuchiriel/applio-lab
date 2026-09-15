#!/usr/bin/env python3
"""anchors-v2 — fuzzy-match EN (~/Audio/lotm/anchors-en/epNN.json) x PT
(epN/vocals.srt do whisper) -> epN/anchors-v2.json + dicionario de
de-embaralhamento (mangled-PT -> nome EN canonico).

Motivacao (RECADO-GLM §2 + MAPA): STT PT embaralha nomes proprios
("Bionde" -> Beyonder); a estrutura de cena EN e a arma de conteudo
contra pares mesmo-ator (Klein x Tolo). Tolerancia a dessincronia:
janela temporal + bonus por nomes proprios fuzzy + alinhamento monotono.

Saida por ep: {meta:{skew_medio, matched, total_en}, spans:[{t0,t1,en,pt,
score,anchors}], lexicon:{mangled:canonico}}
Uso:
  LD_LIBRARY_PATH=... /tmp/opencode/kvenv/bin/python scripts/anchors-v2.py --eps 2 4 5
  (sem --eps: todos os eps com SRT; ep1/ep3 exigem STT previo)
"""
import argparse
import difflib
import glob
import json
import os
import re
import statistics

LOTM = os.path.expanduser("~/Audio/lotm")

# Nomes/termos-canoneiros (EN) — papel/estrutura; minúsculo.
CANON = {
    "beyonder", "antigonus", "zaratul", "klein", "moretti", "audrey", "hall",
    "alger", "wilson", "leonard", "mitchell", "dunn", "smith", "daly",
    "simone", "melissa", "benson", "tingen", "backlund", "spectator",
    "seer", "hanged man", "the fool", "tarot club", "gray carriage",
    "law of bastardy", "nighthawks", "madam sharon",
    "hanass vincent", "mister z", "roselle gustav", "church of evernight",
    "evernight goddess", "steam and machinery", "第六", "iron age",
    "fifth epoch", "chanis gate", "spirituality", "diviner",
    # pathways / títulos do Clube do Tarô (arma de conteúdo anti Klein×Tolo)
    "seer", "clown", "marionettist", "magician", "oracle", "justice",
    "apothecary", "spectator", "hanged man", "the fool", "tarot club",
}

# Aliases manuais de quirks do STT PT observados em produção (v2).
# Só entra aqui o que foi VISTO em spans reais (evidência, não palpite).
MANUAL_ALIAS = {
    "clain": "klein",  # ep4: "Ah, Clain. Bom dia... senhor Neil" (Blackthorn)
}

WORD = re.compile(r"[a-zà-ú']+")

# Palavras comuns PT que NÃO podem virar chave do lexicon (falso-cognato
# com nome canon: "será" ~ seer). Chaves válidas: missa->Melissa (contexto).
STOP_PT = {"sera", "será", "mesa", "casa", "cara", "para", "uma", "como"}


def norm(s):
    return " ".join(WORD.findall(s.lower()))


def load_srt(path):
    subs = []
    raw = open(path, encoding="utf-8-sig").read().strip().split("\n\n")

    def ts(t):
        h, m, s = t.replace(",", ".").split(":")
        return int(h) * 3600 + int(m) * 60 + float(s)

    for b in raw:
        lines = b.split("\n")
        if len(lines) >= 3 and "-->" in lines[1]:
            x, y = lines[1].split(" --> ")
            subs.append([ts(x), ts(y), " ".join(lines[2:])])
    return subs


def canon_hits(text):
    t = " " + norm(text) + " "
    hits = []
    for c in CANON:
        if " " in c:
            if " " + c + " " in t:
                hits.append(c)
        elif " " + c + " " in t:
            hits.append(c)
    return hits


def fuzzy_name_hits(en_text, pt_text):
    """Nomes EN (canon) casando fuzzy no PT (edit-dist <=2 por token)."""
    pt_tokens = set(WORD.findall(pt_text.lower()))
    out = []
    for p in pt_tokens:  # aliases manuais vistos em produção (evidência)
        if p in MANUAL_ALIAS:
            out.append((p, MANUAL_ALIAS[p], 0.9))
    for c in canon_hits(en_text):
        cw = c.split()
        if len(cw) == 1:
            for p in pt_tokens:
                if p in STOP_PT:
                    continue
                if p == cw[0]:
                    out.append((c, c, 1.0))
                    break
                if len(p) > 3 and difflib.SequenceMatcher(None, p, cw[0]).ratio() >= 0.75:
                    out.append((p, c, difflib.SequenceMatcher(None, p, cw[0]).ratio()))
                    break
    return out


def seq_sim(a, b):
    return difflib.SequenceMatcher(None, norm(a), norm(b)).ratio()


def best_overlap_pair(t0, t1, pt):
    """Melhor par PT por FRACAO de overlap da linha EN (janela de folga)."""
    best, bf = None, 0.0
    for k, (p0, p1, ptext) in enumerate(pt):
        ov = min(t1 + 1.5, p1) - max(t0 - 1.5, p0)
        if ov <= 0:
            continue
        frac = min(ov / (t1 - t0), 1.0)
        if frac > bf:
            bf, best = frac, k
    return best, bf


def match_ep(n):
    en_path = os.path.join(LOTM, "anchors-en", "ep%02d.json" % n)
    srt_path = os.path.join(LOTM, "ep%d" % n, "vocals.srt")
    if not (os.path.exists(en_path) and os.path.exists(srt_path)):
        return None
    en = json.load(open(en_path))
    pt = load_srt(srt_path)
    spans, lex, skews, matched, hi = [], {}, [], 0, 0
    for t0, t1, etext in en:
        k, frac = best_overlap_pair(t0, t1, pt)
        if k is None or frac < 0.35:
            continue
        p0, p1, ptext = pt[k]
        qual = round(seq_sim(etext, ptext), 3)  # metadado (idiomas diferentes!)
        fh = fuzzy_name_hits(etext, ptext)
        # anchors = canon EN-side (multi-palavra incluido) + fuzzy PT (lexicon)
        anchors = sorted(set(canon_hits(etext)) | {c for _, c, _ in fh})
        for p, c, r in fh:
            if p != c and lex.get(p) in (None, c):
                lex[p] = c
        matched += 1
        skews.append((p0 + p1) / 2 - (t0 + t1) / 2)
        if frac >= 0.7 and (anchors or qual >= 0.35):
            hi += 1
        spans.append({"t0": t0, "t1": t1, "en": etext, "pt": ptext,
                      "score": qual, "overlap": round(frac, 2),
                      "anchors": anchors})
    out = {
        "meta": {"ep": n, "total_en": len(en), "matched": matched,
                 "alta_conf": hi,
                 "skew_medio_s": round(statistics.median(skews), 2) if skews else None,
                 "fonte_en": "anchors-en/ep%02d.json" % n,
                 "fonte_pt": "ep%d/vocals.srt (whisper-small)" % n},
        "spans": spans, "lexicon": dict(sorted(lex.items())),
    }
    dst = os.path.join(LOTM, "ep%d" % n, "anchors-v2.json")
    json.dump(out, open(dst, "w"), ensure_ascii=False, indent=1)
    print("ep%-2d matched %3d/%3d (%3d alta) | skew %6.2fs | lex %2d | %s"
          % (n, matched, len(en), hi, out["meta"]["skew_medio_s"] or 0,
             len(lex), dst), flush=True)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--eps", type=int, nargs="*", default=[])
    a = ap.parse_args()
    eps = a.eps or [int(os.path.basename(p)[2:4]) for p in
                    sorted(glob.glob(os.path.join(LOTM, "anchors-en", "ep*.json")))]
    lex_all = {}
    for n in eps:
        r = match_ep(n)
        if r:
            for k, v in r["lexicon"].items():
                lex_all.setdefault(k, set()).add(v)
    # persiste lexicon agregado (+aliases manuais) em anchors-en/
    lex_out = {k: sorted(v) for k, v in sorted(lex_all.items())}
    json.dump(lex_out, open(os.path.join(LOTM, "anchors-en", "lexicon.json"), "w"),
              ensure_ascii=False, indent=1)
    for k, v in MANUAL_ALIAS.items():
        lex_all.setdefault(k, set()).add(v)
    if lex_all:
        print("\n== DICIONARIO DE-EMBARALHAMENTO (agregado) ==")
        for k in sorted(lex_all):
            print("%-14s -> %s" % (k, "/".join(sorted(lex_all[k]))))


if __name__ == "__main__":
    main()
