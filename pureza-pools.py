#!/usr/bin/env python3
"""Pureza-check dos pools datasets/* (SOLAR 2026-09-14).

WeSpeaker com 2 refs-distrator: KLEIN (klein-v4/c0-00) e AUDREY
(audrey-v1/ep10-01673). Um clip de pool NAO-klein/audrey cujo best
seja KLEIN/AUDREY com sim >= threshold e' SUSPEITO (contaminacao ou
mislabel). Excecoes (KLEIN vencer e' esperado): klein* (self) e levi
(mesmo dublador Rodrigo Rossi — separar por papel, ver MAPA).

Saida: JSON com per-clip + resumo por pool + lista de suspeitos.
Uso (NixOS):
  LD_LIBRARY_PATH=/nix/store/7vafhlh0lmcvi75jfyy09qwr4m3x1ks3-gcc-15.2.0-lib/lib:/nix/store/483x61iy35irm4wr2b7dwzihljhp6da2-zlib-1.3.2/lib:/nix/store/n12n9j8bikaiy8cvhdwhj3ziz427lycx-libffi-3.7.1/lib \\
  /home/nixos/kvenv/bin/python pureza-pools.py
"""
import argparse
import glob
import json
import os

import numpy as np
import wespeakerruntime as w

p = argparse.ArgumentParser(description=__doc__)
p.add_argument("--datasets", default=os.path.expanduser("~/Audio/lotm/datasets"))
p.add_argument("--out", default=None)
p.add_argument("--th", type=float, default=0.5)
a = p.parse_args()
out = a.out or os.path.join(a.datasets, "pureza-report.json")

spk = w.Speaker(lang="en")


def emb(f):
    e = np.array(spk.extract_embedding(f), dtype=float).ravel()
    return e / (np.linalg.norm(e) + 1e-9)


REFS = {
    "KLEIN": emb(os.path.join(a.datasets, "klein-v4", "c0-00.wav")),
    "AUDREY": emb(os.path.join(a.datasets, "audrey-v1", "ep10-01673.wav")),
}
SELF_KLEIN = {"klein", "levi"}  # Klein vencer aqui e' coerencia, nao contaminacao

report, suspect_all = {}, []
pools = sorted(
    d for d in glob.glob(os.path.join(a.datasets, "*"))
    if os.path.isdir(d) and glob.glob(os.path.join(d, "*.wav"))
)
for pool in pools:
    name = os.path.basename(pool)
    per = {}
    stats = {"n": 0, "klein": 0, "audrey": 0, "suspects": []}
    for f in sorted(glob.glob(os.path.join(pool, "*.wav"))):
        e = emb(f)
        sims = {k: round(float(e @ v), 3) for k, v in REFS.items()}
        best = max(sims, key=sims.get)
        stats["n"] += 1
        stats["klein" if best == "KLEIN" else "audrey"] += 1
        base = os.path.basename(f)
        per[base] = {"best": best, "sim": sims}
        if sims[best] >= a.th:
            poolkey = name.replace("-v1", "").replace("-v2", "").replace("-abertura", "")
            expect_klein = poolkey in SELF_KLEIN
            if (best == "KLEIN") != expect_klein:
                stats["suspects"].append({"clip": base, "best": best, "sim": sims[best]})
                suspect_all.append((name, base, best, sims[best]))
    report[name] = dict(stats, clips=per)
    print("%-22s n=%4d klein=%4d audrey=%4d suspeitos=%d"
          % (name, stats["n"], stats["klein"], stats["audrey"], len(stats["suspects"])),
          flush=True)

json.dump(report, open(out, "w"))
print("\n== SUSPEITOS (th %.2f; klein*/levi: vitoria KLEIN e' esperada) ==" % a.th)
for name, clip, best, s in suspect_all:
    print("%-22s %-24s %s %s" % (name, clip, best, s))
print("TOTAL suspeitos:", len(suspect_all))
print("relatorio:", out)
