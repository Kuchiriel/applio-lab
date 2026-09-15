#!/usr/bin/env python3
"""mine-anchors — minera clips de UM personagem via anchors-v2, com filtro
anti-menção (lição GLM 15/09: âncora pega MENÇÃO, não fala).
Uso: python3 mine-anchors.py --who dunn --outdir datasets/dunn-mine
Filtra spans EN com: said/told/wrote/mentioned/received.*from/letter from X,
narrador-recap, 3ª pessoa. Mantém: 1ª pessoa, vocativo, comando.
Saída: clips + tabela MANTER/EXPULSAR p/ ouvido (path + minuto + STT).
"""
import argparse
import json
import glob
import os
import re
import subprocess

AUD = "/home/nixos/Audio/lotm"
MENTION_RE = re.compile(
    r"Dunn Smith's|\bDunn\b.{0,60}(said|told|wrote|mentioned|mentions|tells|"
    r"will handle|letter from|wrote to|teach|tell|blame|hash it out|helped|"
    r"gazed|followed|perched|dutifully)|"
    r"(received|teach|tell|blame|helped|with).{0,60}\bDunn\b|"
    r"^(Captain )?Dunn[?!.,…]*$|^- Dunn|,\s+Dunn[?!.,…]*$|\bDunn!$", re.I)
KEEP_CUE = re.compile(
    r"\b(you|your|Captain,|men|team|take|go|leave|focus|retreat|request|"
    r"need|must|will|fare|vamos|podemos|devemos|my|we|I'll|I've)\b", re.I)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--who", required=True)
    ap.add_argument("--outdir", required=True)
    a = ap.parse_args()
    who = a.who.lower()
    os.makedirs(a.outdir, exist_ok=True)
    kept, dropped = [], []
    for f in sorted(glob.glob(os.path.join(AUD, "ep*", "anchors-v2.json"))):
        ep = int(re.search(r"ep(\d+)", f).group(1))
        dd = os.path.dirname(f)
        voc = os.path.join(dd, "sep", "htdemucs", "mix", "vocals.wav")
        if not os.path.exists(voc):
            voc = os.path.join(dd, "ep%d-vocais-isolados.wav" % ep)
        if not os.path.exists(voc):
            continue
        data = json.load(open(f))
        for s in data["spans"]:
            if who not in [x.lower() for x in s["anchors"]]:
                continue
            dur = min(s["t1"] - s["t0"], 15.0)
            if dur < 1.0:
                continue
            en = s["en"]
            if MENTION_RE.search(en):
                dropped.append((ep, s["t0"], en[:70], "mencao-3p"))
                continue
            cue = bool(KEEP_CUE.search(en) or KEEP_CUE.search(s["pt"]))
            out = os.path.join(a.outdir, "ep%d-%05d.wav" % (ep, int(s["t0"])))
            subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", str(s["t0"]),
                            "-t", str(dur), "-i", voc, "-ar", "16000",
                            "-ac", "1", out], check=True)
            kept.append((ep, s["t0"], out, en[:70], s["pt"][:70], cue))
    print("kept %d, dropped %d (mencao)" % (len(kept), len(dropped)))
    tab = ["# mine %s — filtrado anti-menção" % who,
           "# [ ] path | ep mm:ss | EN | PT", ""]
    for ep, t0, out, en, pt, cue in kept:
        tab.append("[%s] %s | ep%d %02d:%02d | %s | %s" % (
            "fala?" if cue else "checar", out, ep, int(t0) // 60, int(t0) % 60, en, pt))
    open(os.path.join(a.outdir, "checks.txt"), "w").write("\n".join(tab) + "\n")
    open(os.path.join(a.outdir, "dropped.json"), "w").write(
        json.dumps(dropped, ensure_ascii=False, indent=1))


main()
