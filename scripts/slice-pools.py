#!/usr/bin/env python3
"""Fatia pools RVC por personagem a partir do enroll (refs limpas do dono +
predicoes em limiar ESTRITO). Verificacao 'do meu modo': embedding sim+margin,
sem ouvido.
Uso: python3 slice-pools.py --enroll /tmp/opencode/enroll-v3.json --eps 4 5 6 7 8 9 10 11 12 13
Saida: ~/Audio/lotm/datasets/<slug>-v1/ + pools-report.json
"""
import argparse
import json
import os
import subprocess

AUD = "/home/nixos/Audio/lotm"
DS = "/home/nixos/Audio/lotm/datasets"
BADFLAGS = {"MISTO", "EXCLUIR", "HIPOTESE", "SFX-CORPO", "WAV-CORTADO", "AMOSTRA-UNICA"}


def slug(who):
    return {"Klein": "klein", "Velho Neil": "neil", "Dunn Smith": "dunn",
            "Hood Eugen": "hood", "Leonard": "leonard", "Azik": "azik",
            "Alger Wilson": "alger", "Audrey Hall": "audrey", "Melissa": "melissa",
            "Sr Tolo": "tolo", "Hanass Vincent": "hanass", "Madame Sharon": "sharon",
            "Daly": "daly", "Glacis": "glacis", "Mr. Z": "mrz",
            "Elizabeth": "elizabeth", "Selena": "selena",
            "NARRADOR-ABERTURA": "narrador", "Imperador Roselle": "roselle",
            "Benson": "benson", "Dennis": "dennis", "Katarina": "katarina",
            "Angelica": "angelica", "Christina": "christina", "Megose": "megose",
            "Rozanne": "rozanne", "Lanevus": "lanevus", "Trissy": "trissy",
            "Triss": "triss", "Anna Wayne": "anna", "Ademisaul": "ademisaul",
            "Reverendo Crestet": "crestet", "Capitao Havre": "havre",
            "Vendedor de amuletos do mercado subterraneo": "vendedor",
            "Artefato 0-08 Pena": "pena"}.get(who)


def cut(src, s, dur, dst):
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", str(s),
                    "-to", str(s + dur), "-i", src,
                    "-ar", "48000", "-ac", "1", dst], check=True)


def main():
    a = argparse.ArgumentParser()
    a.add_argument("--enroll", required=True)
    a.add_argument("--eps", nargs="+", type=int, required=True)
    a.add_argument("--sim", type=float, default=0.55)
    a.add_argument("--margin", type=float, default=0.15)
    o = a.parse_args()
    enr = json.load(open(o.enroll))
    rep = {}
    for ep in o.eps:
        lab = json.load(open(f"{AUD}/ep{ep}/ep{ep}-labels.json"))
        v = subprocess.check_output(
            ["find", f"{AUD}/ep{ep}/sep", "-name", "vocals.wav"]).decode().split()[0]
        # 1) refs limpas (copia)
        for c in lab["checks"]:
            who = c.get("who", "")
            s = slug(who)
            if not s or set(c.get("flags", [])) & BADFLAGS or "+" in who:
                continue
            d = os.path.join(DS, s + "-v1")
            os.makedirs(d, exist_ok=True)
            src = os.path.join(AUD, f"ep{ep}", c["clip"])
            if os.path.exists(src):
                n = len([f for f in os.listdir(d) if f.endswith(".wav")])
                subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", src,
                                "-ar", "48000", "-ac", "1",
                                os.path.join(d, f"ref-{ep}-{n:02d}.wav")], check=True)
        # 2) predicoes estritas
        for u in enr.get(str(ep), enr.get(ep, [])):
            if u["sim"] < o.sim or u["margin"] < o.margin:
                continue
            s = slug(u["best"])
            if not s:
                continue
            d = os.path.join(DS, s + "-v1")
            os.makedirs(d, exist_ok=True)
            n = len([f for f in os.listdir(d) if f.endswith(".wav")])
            dur = min(u["e"] - u["s"], 15)
            cut(v, u["s"], dur, os.path.join(d, f"ep{ep}-{int(u['s']):05d}.wav"))
    # relatorio
    import wave
    import contextlib
    for d in sorted(os.listdir(DS)):
        p = os.path.join(DS, d)
        if not os.path.isdir(p) or d in ("klein-v4", "narrador-abertura"):
            continue
        files = sorted(f for f in os.listdir(p) if f.endswith(".wav"))
        tot = 0.0
        for f in files:
            try:
                with contextlib.closing(wave.open(os.path.join(p, f))) as wv:
                    tot += wv.getnframes() / wv.getframerate()
            except Exception:
                pass
        rep[d] = {"clips": len(files), "min": round(tot / 60, 2)}
        print(f"{d}: {len(files)} clips {tot/60:.1f}min", flush=True)
    json.dump(rep, open(os.path.join(DS, "pools-report.json"), "w"), indent=1)


main()
