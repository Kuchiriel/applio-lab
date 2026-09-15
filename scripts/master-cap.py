#!/usr/bin/env python3
"""master-cap — master binaural de capítulo a partir dos .parts + blocking.
Uso: python3 master-cap.py <cap.wav.parts> caps/capNN.json caps/capNN-blocking.json <out.wav>
- Narrador: centro-frente, seco. Klein: posição por bloco (fixo; bloco C
  com varredura leve). SFX: posição da cena. Bed rua atrás (difuso) em
  loop + carroças L->R/R->L posicionadas.
"""
import json
import os
import sys

import numpy as np
import soundfile as sf

SR = 44100
PARTS, SEGS, BLOCK, OUT = sys.argv[1:5]
SFXD = "/home/nixos/Audio/sfx"

data = json.load(open(SEGS))["segments"]
blocking = json.load(open(BLOCK))
spk = {s["i"]: s["speaker"] for s in data}

# bloco de cada seg
blkof = {}
for bl in blocking["blocos"]:
    a, z = bl["segs"]
    for i in range(a, z + 1):
        blkof[i] = bl

POS = {"centro-frente": (0.0, 0.0), "centro-perto": (0.0, 0.15),
       "centro-esquerda": (-0.45, 0.1), "direita": (0.55, 0.1),
       "centro-direita": (0.3, 0.1), "frente-direita-perto": (0.35, 0.3),
       "movimento": None}


def load_seg(i):
    import glob
    cands = sorted(glob.glob(os.path.join(PARTS, "f%03d.wav" % i)))
    if not cands:
        return None
    y, sr = sf.read(cands[0])
    if y.ndim > 1:
        y = y.mean(axis=1)
    if sr != SR:
        import librosa
        y = librosa.resample(y, orig_sr=sr, target_sr=SR)
    return y.astype(np.float64)


def place_stereo(y, x, depth=0.0):
    """x: -1..1, depth 0..1 (reverb/absorção). Retorna (L,R)."""
    itd = int(x * 0.0006 * SR)
    gL = np.sqrt(max(0.0, (1 - x) / 2))
    gR = np.sqrt(max(0.0, (1 + x) / 2))
    n = len(y)
    L = np.zeros(n + abs(itd) + 1)
    R = np.zeros(n + abs(itd) + 1)
    if itd >= 0:
        L[itd:itd + n] += y * gL
        R[:n] += y * gR
    else:
        L[:n] += y * gL
        R[-itd:-itd + n] += y * gR
    if depth > 0:
        # reflexo curto = distância/sala (regra de ouro vrtonung)
        d = int((0.02 + depth * 0.06) * SR)
        wet = 0.12 + depth * 0.2
        for buf in (L, R):
            buf[d:] += buf[:-d] * wet
    m = max(len(L), len(R))
    return L[:m], R[:m]


def klein_pos(i):
    bl = blkof.get(i, {})
    kp = (bl.get("klein") or {}).get("pos", "centro-esquerda")
    if kp == "movimento":
        return None  # varredura tratada no mix
    if "frente-direita" in kp:
        return 0.7, 0.3
    if "centro-direita" in kp:
        return 0.6, 0.1
    if kp == "direita":
        return 0.7, 0.15
    if kp == "centro-esquerda":
        return -0.7, 0.1
    return 0.0, 0.15


L = np.zeros(1)
R = np.zeros(1)
cur = 0
gaps = {}  # (reaproveita silêncios do render: 0.35 padrão)


def push(st):
    global L, R, cur
    l, r = st
    need = cur + len(l)
    if len(L) < need:
        L = np.pad(L, (0, need - len(L)))
        R = np.pad(R, (0, need - len(R)))
    L[cur:cur + len(l)] += l
    R[cur:cur + len(r)] += r
    cur += len(l)


for s in data:
    i = s["i"]
    y = load_seg(i)
    if y is None:
        continue
    if s["speaker"] == "NARRADOR":
        st = place_stereo(y, 0.0, 0.0)
    elif s["speaker"] == "KLEIN":
        kp = klein_pos(i)
        if kp is None:
            # bloco C: varredura leve L->R dentro do próprio seg
            n = len(y)
            mid = n // 2
            l1, r1 = place_stereo(y[:mid], -0.3, 0.05)
            l2, r2 = place_stereo(y[mid:], 0.3, 0.05)
            st = (np.concatenate([l1, l2]), np.concatenate([r1, r2]))
        else:
            st = place_stereo(y, kp[0], kp[1])
    else:
        st = place_stereo(y, 0.0, 0.05)
    push(st)
    # respiro do render (0.35s; longa 0.9) preservado
    gap = 0.9 if (s["speaker"] == "NARRADOR" and len(s["text"]) > 350) else 0.35
    push((np.zeros(int(gap * SR)), np.zeros(int(gap * SR))))

# BED rua atrás em loop (difuso, sem ITD lateral) — bed-quarto-limpo
# (trecho 40-72s sem carro/avião; dono validou A=avião, C=youtuber — fora)
bed, sr0 = sf.read(os.path.join(SFXD, "bed-quarto-limpo.wav"))
if bed.ndim > 1:
    bed = bed.mean(axis=1)
if sr0 != SR:
    import librosa
    bed = librosa.resample(bed, orig_sr=sr0, target_sr=SR)
bed = bed.astype(np.float64) * 0.5
rep = int(np.ceil(len(L) / len(bed)))
bedL = np.tile(bed, rep)[:len(L)]
d = int(0.0004 * SR)
bedR = np.concatenate([np.zeros(d), bedL[:-d]])
L += bedL
R += bedR

# CARROÇAS aleatórias (dono 15/09: poucas de noite, direções e distâncias
# alternadas, sem loop estático). Seed fixa = reproduzível.
import random
random.seed(int(blocking.get("capitulo", 1)))
dur_min = len(L) / SR
events = []
t = 90.0
while t < dur_min - 30:
    t += random.uniform(120, 300)  # a cada 2-5 min
    if t >= dur_min - 20:
        break
    events.append((t, random.choice([-1, 1]),
                   random.choice(["near", "far"])))


def place_event(seg, t0, x0, x1, vol=1.0):
    m = len(seg)
    pan = np.linspace(x0, x1, m)
    itd = (pan * 0.0006 * SR).astype(int)
    gL = np.sqrt(np.clip((1 - pan) / 2, 0, 1)) * 0.5 * vol
    gR = np.sqrt(np.clip((1 + pan) / 2, 0, 1)) * 0.5 * vol
    s0 = int(t0 * SR)
    if s0 >= len(L):
        return
    m = min(m, len(L) - s0)
    idx = np.arange(m)
    L[s0:s0 + m] += seg[np.clip(idx - itd[:m], 0, len(seg) - 1)] * gL[:m]
    R[s0:s0 + m] += seg[np.clip(idx + itd[:m], 0, len(seg) - 1)] * gR[:m]


for t0, dirc, dist in events:
    ce, _ = sf.read(os.path.join(
        SFXD, "evento-carroca-%s.wav" % dist))
    if ce.ndim > 1:
        ce = ce.mean(axis=1)
    ce = ce.astype(np.float64)
    if dirc < 0:
        place_event(ce, t0, -1.0, 1.0)
    else:
        place_event(ce, t0, 1.0, -1.0)
    print("carroça t=%.0fs dir=%s dist=%s" % (t0, "E->D" if dirc < 0 else "D->E", dist))

st = np.stack([L, R], axis=1)
st /= max(1e-9, np.abs(st).max())
sf.write(OUT, (st * 0.89).astype(np.float32), SR)
print("OK:", OUT, "%.0fs" % (len(L) / SR))
