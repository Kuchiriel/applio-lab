#!/usr/bin/env python3
"""Matricula WeSpeaker a partir dos checks limpos (labels do dono) e classifica
os trechos sem-rotulo por cosseno contra o centroide de cada personagem.
Prova de limiar: mostra sim propria (ref x ref mesmo char) vs cruzada.
Uso: LD_LIBRARY_PATH=... kvenv-python enroll.py --eps 4 5 6 --top 30 --out /tmp/opencode/enroll-pilot.json
"""
import argparse
import glob
import json
import os
import subprocess
import sys

BADFLAGS = {"MISTO", "EXCLUIR", "HIPOTESE", "SFX-CORPO", "WAV-CORTADO", "AMOSTRA-UNICA"}
AUD = "/home/nixos/Audio/lotm"
TMP = "/tmp/opencode/enroll-tmp"


def load_refs(eps):
    refs = {}
    for ep in eps:
        lab = json.load(open(f"{AUD}/ep{ep}/ep{ep}-labels.json"))
        for c in lab["checks"]:
            if c.get("who") in ("MUSICA",) or set(c.get("flags", [])) & BADFLAGS:
                continue
            if "+" in c["who"]:
                continue
            clip = c["clip"] if c["clip"].startswith("check") or c["clip"].startswith("spk") else None
            p = f"{AUD}/ep{ep}/{c['clip']}"
            if os.path.exists(p):
                refs.setdefault(c["who"], []).append(p)
    return refs


def main():
    a = argparse.ArgumentParser()
    a.add_argument("--eps", nargs="+", type=int, required=True)
    a.add_argument("--top", type=int, default=30)
    a.add_argument("--out", required=True)
    o = a.parse_args()
    os.makedirs(TMP, exist_ok=True)

    import numpy as np
    import wespeakerruntime as w
    spk = w.Speaker(lang="en")

    def emb(f):
        e = np.array(spk.extract_embedding(f), dtype=float).ravel()
        return e / (np.linalg.norm(e) + 1e-9)

    refs = load_refs(o.eps)
    conv = {}

    def c16(p):
        if p not in conv:
            o16 = os.path.join(TMP, "ref-%d.wav" % len(conv))
            subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", p,
                            "-ar", "16000", "-ac", "1", o16], check=True)
            conv[p] = o16
        return conv[p]

    cent = {}
    for who, files in refs.items():
        E = np.stack([emb(c16(f)) for f in files])
        c = E.mean(axis=0)
        cent[who] = c / (np.linalg.norm(c) + 1e-9)
        print(f"REF {who}: {len(files)} clips", flush=True)
    print(f"classes: {sorted(cent)}", flush=True)

    # prova de limiar: sim entre refs do mesmo char vs melhor outro char
    print("--- prova (ref x centroide proprio vs melhor rival) ---", flush=True)
    for who, files in refs.items():
        for f in files:
            e = emb(c16(f))
            s = {k: round(float(e @ v), 3) for k, v in cent.items()}
            rival = max((v, k) for k, v in s.items() if k != who)
            print(f"{who} {os.path.basename(f)} self={s[who]} rival={rival[1]}:{rival[0]}", flush=True)

    # classifica unknowns
    rep = {}
    for ep in o.eps:
        unl = json.load(open(f"{AUD}/ep{ep}/auto-labels.json.unlabeled.json"))
        v = subprocess.check_output(
            ["find", f"{AUD}/ep{ep}/sep", "-name", "vocals.wav"]).decode().split()[0]
        cand = sorted([u for u in unl if 1.5 <= u[1] - u[0] <= 12.0],
                      key=lambda u: -(u[1] - u[0]))[:o.top] if o.top else [u for u in unl if 1.5 <= u[1] - u[0] <= 12.0]
        rep[ep] = []
        for s, e, txt in cand:
            dur = min(e - s, 30)
            wav = f"{TMP}/ep{ep}-{int(s)}.wav"
            subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", str(s),
                            "-to", str(s + dur), "-i", v,
                            "-ar", "16000", "-ac", "1", wav], check=True)
            q = emb(wav)
            srt = sorted(((float(q @ c), k) for k, c in cent.items()), reverse=True)
            rep[ep].append({"s": round(s, 1), "e": round(e, 1),
                            "best": srt[0][1], "sim": round(srt[0][0], 3),
                            "rival": srt[1][1], "margin": round(srt[0][0] - srt[1][0], 3)})
            print(f"ep{ep} {s:.0f}s best={srt[0][1]} {srt[0][0]:.3f} rival={srt[1][1]} marg={srt[0][0]-srt[1][0]:.3f} :: {txt[:60]}", flush=True)
    json.dump(rep, open(o.out, "w"))
    print("OUT", o.out, flush=True)


main()
