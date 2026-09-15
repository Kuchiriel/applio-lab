#!/usr/bin/env python3
"""Gera checks de review para um ep: top-20 trechos sem rotulo (mais longos).
Saida: check-NN-unknown.wav + checks-ep.txt com [minuto video] + STT + falante.
Uso: python3 gen-checks-ep.py ~/Audio/lotm/epN
"""
import json
import os
import subprocess
import sys


def ts(t):
    h, m, s = t.split(":")
    return int(h) * 3600 + int(m) * 60 + float(s.replace(",", "."))


def mmss(s):
    return "%d:%02d" % (int(s // 60), int(s % 60))


def load_subs(path):
    subs = []
    raw = open(path, encoding="utf-8-sig").read().strip().split("\n\n")
    for b in raw:
        lines = b.split("\n")
        if len(lines) >= 3 and "-->" in lines[1]:
            x, y = lines[1].split(" --> ")
            subs.append((ts(x), ts(y), " ".join(lines[2:])))
    return subs


def main():
    epdir = sys.argv[1]
    unl = json.load(open(os.path.join(epdir, "auto-labels.json.unlabeled.json")))
    out = subprocess.check_output(
        ["find", os.path.join(epdir, "sep"), "-name", "vocals.wav"]).decode().split()
    vocals = out[0]
    subs = load_subs(os.path.join(epdir, "vocals.srt"))
    turns = []
    rttm = os.path.join(epdir, "diarize.rttm")
    if os.path.exists(rttm):
        for line in open(rttm):
            p = line.split()
            turns.append((float(p[3]), float(p[3]) + float(p[4]), p[7]))

    def speaker_at(s, e):
        best, ov = "?", 0.0
        for x, y, spk in turns:
            o = min(e, y) - max(s, x)
            if o > ov:
                best, ov = spk, o
        return best

    cand = [u for u in unl if u[1] - u[0] >= 1.5]
    cand.sort(key=lambda u: -(u[1] - u[0]))
    top = sorted(cand[:20])
    lines = []
    for i, (s, e, _txt) in enumerate(top):
        dur = min(e - s, 30)
        wav = os.path.join(epdir, "check-%02d-unknown.wav" % i)
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", str(s),
                        "-to", str(s + dur), "-i", vocals,
                        "-ar", "48000", "-ac", "1", wav], check=True)
        full = " ".join(t for x, y, t in subs if x < e + 0.5 and y > s - 0.5)
        lines.append("## check-%02d-unknown.wav — video %s–%s (diarize %s)\nSTT: %s\n"
                     % (i, mmss(s), mmss(s + dur), speaker_at(s, e), full))
    open(os.path.join(epdir, "checks-ep.txt"), "w").write("\n".join(lines))
    print("%s: %d checks (%d sem-rotulo)" % (epdir, len(top), len(unl)), flush=True)


main()
