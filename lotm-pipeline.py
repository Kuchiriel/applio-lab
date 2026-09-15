#!/usr/bin/env python3
"""LOTM voice pipeline — ep1 provado, demais eps por vir.

Etapas (cada uma persiste artefato; rode em ordem ou separado):
  separate  mp4 -> vocals.wav (demucs htdemucs, CPU ok)
  vad       vocals -> segs.json (librosa split + merge)
  diarize   vocals -> diarizen RTTM (diarize pkg, min/max speakers)
  stt       vocals -> srt (whisper small pt)
  anchors   srt + ANCHORS -> split.json (regex dono -> falante)
  slice     split.json -> personagens/<nome>/*.wav (48kHz mono)
  verify    clips x refs (WeSpeaker) -> sim.json (tabela cosseno)

Refs e âncoras vivem em LOTM-MAPA-VOZES.md (fonte de verdade humana).
Uso de libs pesadas exige LD_LIBRARY_PATH do nix (ver README do lab).

Ex: python3 lotm-pipeline.py vad --vocals ep1-vocais-isolados.wav --out segs.json
"""
import argparse
import collections
import glob
import json
import os
import re
import subprocess
import sys

# Âncoras de conteúdo (dono, ep1). regex minúscula -> falante.
ANCHORS = [
    ("imperador transmigrou", "KLEIN"),
    ("primeiro cliente", "CUIDADORA"),
    ("destino é profundo|curso imprevisível", "CUIDADORA"),
    ("carta é o seu (passado|futuro)|passado, presente e futuro|concentre-se no que busca", "CUIDADORA"),
    ("por que está se passando por mim|vai cuidar dos seus baboínos|não é uma boa leitora", "CARTOMANTE"),
    ("klein\\!", "MELISSA"),
    ("exaltado|para bênçãos|bênçãos", "TOLO"),
    ("eu invoco", "TOLO"),
    ("o tolo", "KLEIN"),
]

REFS = {}  # nome -> wav de referência pura (passado via --ref Nome=arq)


def sh(cmd):
    print("+", " ".join(cmd), flush=True)
    subprocess.run(cmd, check=True)


def cmd_separate(a):
    os.makedirs(a.outdir, exist_ok=True)
    sh(["ffmpeg", "-y", "-v", "error", "-i", a.mp4, "-vn", "-ac", "1",
        "-ar", "44100", os.path.join(a.outdir, "mix.wav")])
    sh([sys.executable, "-m", "demucs.separate", "-n", "htdemucs",
        "--two-stems", "vocals", "-o", os.path.join(a.outdir, "sep"),
        os.path.join(a.outdir, "mix.wav")])


def cmd_vad(a):
    import librosa
    y, sr = librosa.load(a.vocals, sr=16000, mono=True)
    iv = librosa.effects.split(y, top_db=35, frame_length=2048, hop_length=512)
    segs = [(s / sr, e / sr) for s, e in iv if (e - s) / sr > 1.5]
    merged = []
    for s, e in segs:
        if merged and s - merged[-1][1] < 0.8:
            merged[-1][1] = e
        else:
            merged.append([s, e])
    json.dump(merged, open(a.out, "w"))
    tot = sum(e - s for s, e in merged)
    print("segmentos: %d | fala: %.1f min" % (len(merged), tot / 60))


def cmd_diarize(a):
    from diarize import diarize
    r = diarize(a.vocals, min_speakers=a.min_spk, max_speakers=a.max_spk)
    r.to_rttm(a.out)
    segs = r.to_list()
    tot = collections.defaultdict(float)
    for s in segs:
        tot[s["speaker"]] += s["end"] - s["start"]
    for k in sorted(tot):
        print(k, "%.1f min" % (tot[k] / 60))


def cmd_stt(a):
    # faster-whisper turbo (A/B 2026-09-14: 21s/4min GPU 11x, PT melhor que
    # small — "gaviões", "rezo", "infantis" corretos; small 16s mas mangled).
    # GPU ~2GB: rodar com LLM descarregado (fallback CPU int8 no script).
    import os
    here = os.path.dirname(os.path.abspath(__file__))
    out = os.path.join(a.outdir, os.path.splitext(os.path.basename(a.vocals))[0] + ".srt")
    sh([sys.executable, os.path.join(here, "scripts", "fw-stt.py"), a.vocals, out])


def _load_subs(path):
    subs = []
    raw = open(path, encoding="utf-8-sig").read().strip().split("\n\n")

    def ts(t):
        h, m, s = t.split(":")
        return int(h) * 3600 + int(m) * 60 + float(s.replace(",", "."))

    for b in raw:
        lines = b.split("\n")
        if len(lines) >= 3 and "-->" in lines[1]:
            x, y = lines[1].split(" --> ")
            subs.append((ts(x), ts(y), " ".join(lines[2:])))
    return subs


def cmd_anchors(a):
    subs = _load_subs(a.srt)
    turns = []
    for line in open(a.rttm):
        p = line.split()
        if a.speaker == "ALL" or p[7] == a.speaker:
            turns.append((float(p[3]), float(p[3]) + float(p[4]), p[7]))
    res = collections.defaultdict(list)
    unl = []
    for s, e, spk in turns:
        txt = " ".join(t for x, y, t in subs if x < e + 0.5 and y > s - 0.5)
        who = None
        for pat, name in ANCHORS:
            if re.search(pat, txt.lower()):
                who = name
                break
        (res[who] if who else unl).append(
            [s, e] if who else [s, e, txt[:100]])
        if who:
            res[who][-1] = [s, e]
    # unl guarda triplas; res guarda pares
    json.dump({k: v for k, v in res.items()}, open(a.out, "w"))
    json.dump(unl, open(a.out + ".unlabeled.json", "w"))
    for k in sorted(res):
        print("%-12s %d turnos" % (k, len(res[k])))
    print("SEM-ROTULO:", len(unl))


def cmd_slice(a):
    split = json.load(open(a.split))
    os.makedirs(a.outdir, exist_ok=True)
    for spk, lst in split.items():
        d = os.path.join(a.outdir, spk.lower())
        os.makedirs(d, exist_ok=True)
        n = 0
        for s, e in lst:
            if e - s < 1.0:
                continue
            # janela curta p/ não sangrar; clips longos o RVC fatia depois
            dur = min(e - s, 15)
            sh(["ffmpeg", "-y", "-v", "error", "-ss", str(s), "-to", str(s + dur),
                "-i", a.vocals, "-ar", "48000", "-ac", "1",
                os.path.join(d, "%s-%02d.wav" % (spk.lower()[:5], n))])
            n += 1
        print(spk, n, "clips")


def cmd_verify(a):
    import wespeakerruntime as w
    import numpy as np
    spk = w.Speaker(lang="en")

    def emb(f):
        e = np.array(spk.extract_embedding(f), dtype=float).ravel()
        return e / (np.linalg.norm(e) + 1e-9)

    refs = {}
    for item in a.ref:
        name, path = item.split("=", 1)
        refs[name] = emb(path)
    out = {}
    for f in sorted(glob.glob(os.path.join(a.clipdir, "*.wav"))):
        e = emb(f)
        s = {k: round(float(e @ v), 3) for k, v in refs.items()}
        best = max(s, key=s.get)
        out[os.path.basename(f)] = {"best": best, "sim": s}
        print(os.path.basename(f), best, s)
    json.dump(out, open(a.out, "w"), indent=1)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("separate"); s.add_argument("mp4"); s.add_argument("--outdir", default=".")
    v = sub.add_parser("vad"); v.add_argument("--vocals", required=True); v.add_argument("--out", required=True)
    d = sub.add_parser("diarize"); d.add_argument("--vocals", required=True); d.add_argument("--out", required=True)
    d.add_argument("--min-spk", type=int, default=4); d.add_argument("--max-spk", type=int, default=8)
    t = sub.add_parser("stt"); t.add_argument("--vocals", required=True); t.add_argument("--outdir", default=".")
    n = sub.add_parser("anchors"); n.add_argument("--srt", required=True); n.add_argument("--rttm", required=True)
    n.add_argument("--speaker", default="ALL"); n.add_argument("--out", required=True)
    c = sub.add_parser("slice"); c.add_argument("--split", required=True); c.add_argument("--vocals", required=True)
    c.add_argument("--outdir", required=True)
    f = sub.add_parser("verify"); f.add_argument("--clipdir", required=True); f.add_argument("--out", required=True)
    f.add_argument("--ref", action="append", default=[])
    a = p.parse_args()
    {"separate": cmd_separate, "vad": cmd_vad, "diarize": cmd_diarize,
     "stt": cmd_stt, "anchors": cmd_anchors, "slice": cmd_slice,
     "verify": cmd_verify}[a.cmd](a)


if __name__ == "__main__":
    main()
