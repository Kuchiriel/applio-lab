#!/usr/bin/env python3
"""verify-render — self-debug do capítulo via STT (dono 15/09: ouviu 5x, cansa).
Uso: python3 verify-render.py <cap.wav> caps/capNN.json
1. STT turbo do wav final; 2. alinha cada segmento (texto normalizado) na
   transcrição em ordem; 3. reporta: FALTANDO (texto do seg não achado),
   ORDEM (fora de sequência), e lista segs p/ revisão.
Não verifica falante (STT não sabe quem fala) — só conteúdo/cobertura.
"""
import json
import re
import sys


def norm(t):
    t = t.lower()
    t = re.sub(r"[^\w\s]", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def main():
    wav, segpath = sys.argv[1], sys.argv[2]
    from faster_whisper import WhisperModel
    model = WhisperModel("turbo", device="cuda", compute_type="float16")
    tr = " ".join(s.text for s in model.transcribe(wav, language="pt")[0])
    full = norm(tr)
    data = json.load(open(segpath))
    pos, missing, ooo = 0, [], []
    for s in data["segments"]:
        words = norm(s["text"]).split()
        if len(words) < 3:
            continue
        key = " ".join(words[:6])
        at = full.find(key, max(0, pos - 200))
        if at < 0:
            missing.append((s["i"], s["speaker"], s["text"][:80]))
        else:
            if at < pos - 200:
                ooo.append((s["i"], s["text"][:60]))
            pos = at + len(key)
    print("segmentos: %d  faltando: %d  fora-de-ordem: %d" % (
        len(data["segments"]), len(missing), len(ooo)))
    for i, sp, t in missing:
        print("FALTA [%d] %s | %s" % (i, sp, t))
    for i, t in ooo:
        print("ORDEM [%d] %s" % (i, t))


main()
