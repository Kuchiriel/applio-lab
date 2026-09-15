#!/usr/bin/env python3
"""verify-v2 — verificação reversa do capítulo (dono 15/09: 1432 caps).
Camadas:
 0. medidas: mudo/clipping/burst/silêncio/duração por segmento.
 1. acústica: embedding WeSpeaker de cada seg final vs REFs de voz
    (klein-ref média de segs Klein aprovados; narr-ref idem). Flag SWAP
    se similaridade com a voz ESPERADA < outra voz - margem.
 2. textual: segunda opinião independente (speaker_of do parser) sobre o
    texto; flag DIVERGE se render != segunda opinião e não for UNKNOWN.
Uso: kvenv/bin/python verify-v2.py <cap.wav.parts> caps/capNN.json
"""
import glob
import json
import os
import sys

import numpy as np
import soundfile as sf

PARTS, SEGS = sys.argv[1:3]
REFS = {"KLEIN": [], "NARRADOR": []}

sys.path.insert(0, "/home/nixos/projects/applio-lab")
import importlib.util

spec = importlib.util.spec_from_file_location(
    "lab", "/home/nixos/projects/applio-lab/lotm-audiobook.py")
lab = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lab)

_wes = None
_TMP = {}


def wes():
    global _wes
    if _wes is None:
        import wespeakerruntime as w
        _wes = w.Speaker(lang="en")
    return _wes


def emb(wav):
    import subprocess
    if wav not in _TMP:
        o16 = "/tmp/opencode/v2-%d.wav" % len(_TMP)
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", wav,
                        "-ar", "16000", "-ac", "1", o16], check=True)
        _TMP[wav] = o16
    import numpy as np
    e = np.array(wes().extract_embedding(_TMP[wav]), dtype=float).ravel()
    return e / (np.linalg.norm(e) + 1e-9)


def cos(a, b):
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-9))


data = json.load(open(SEGS))["segments"]
# REFs: segs aprovados do cap01 (dono aprovou o cap; gross-error detection)
ref_files = {"KLEIN": [46, 49, 52], "NARRADOR": [3, 24, 31]}
for who, ids in ref_files.items():
    for i in ids:
        f = os.path.join(PARTS, "f%03d.wav" % i)
        if os.path.exists(f):
            REFS[who].append(emb(f))
REFS = {k: np.mean(v, axis=0) for k, v in REFS.items() if v}

print("seg speaker | dur rms peak | simK simN | flags")
issues = 0
for s in data:
    i = s["i"]
    f = os.path.join(PARTS, "f%03d.wav" % i)
    if not os.path.exists(f):
        print(i, s["speaker"], "SEM-ARQUIVO")
        issues += 1
        continue
    y, sr = sf.read(f)
    if y.ndim > 1:
        y = y.mean(axis=1)
    dur = len(y) / sr
    rms = float(np.sqrt(np.mean(y ** 2)))
    peak = float(np.abs(y).max())
    flags = []
    if rms < 0.002:
        flags.append("MUDO")
    if peak > 0.98:
        flags.append("CLIP")
    if rms > 0.15:
        flags.append("BURST?")
    sk = cos(emb(f), REFS["KLEIN"]) if "KLEIN" in REFS else -9
    sn = cos(emb(f), REFS["NARRADOR"]) if "NARRADOR" in REFS else -9
    if s["speaker"] == "KLEIN" and sn > sk + 0.05:
        flags.append("SWAP?narr(%.2f>%.2f)" % (sn, sk))
    if s["speaker"] == "NARRADOR" and sk > sn + 0.05:
        flags.append("SWAP?klein(%.2f>%.2f)" % (sk, sn))
    if s["speaker"] in ("KLEIN", "NARRADOR"):
        second, _ = lab.speaker_of([s["text"]], 0, None)
        if second in ("KLEIN", "NARRADOR") and second != s["speaker"]:
            flags.append("DIVERGE:%s" % second)
    mark = " ".join(flags)
    if mark:
        issues += 1
        print("%d %s | %.1fs %.4f %.2f | K%.2f N%.2f | %s" % (
            i, s["speaker"], dur, rms, peak, sk, sn, mark))
print("issues: %d/%d" % (issues, len(data)))
