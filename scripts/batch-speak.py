#!/usr/bin/env python3
"""batch-speak — sintetiza N bases TTS num processo só (código do repo).
Uso: kvenv/bin/python batch-speak.py jobs.json saida.json
jobs: [{i, text, base, voice, rate, speed, style}]
saida: {i: wav_path_ou_ERROR}
Rodar com PYTHONPATH=<repo>/modules/ai/jarvis/src (+ LD_LIBRARY_PATH p/ kokoro).
"""
import json
import sys
import time

from jarvis.core.voice import speak


def one(j):
    try:
        return speak(
            j["text"], voice=j.get("voice"), play=False, keep_wav=True,
            base=j.get("base", "antonio"), rate=j.get("rate"),
            speed=j.get("speed"), style=j.get("style"),
        )
    except Exception as e:  # nunca derruba o lote
        return "ERROR: %s" % e


def main():
    jobs = json.load(open(sys.argv[1]))
    out = {}
    for j in jobs:
        wav = one(j)
        # Edge é flaky (429/rede): retry c/ backoff antes de desistir
        for wait in (5, 15, 30, 60):
            if not (isinstance(wav, str) and wav.startswith("ERROR")):
                break
            print("[batch %s] retry em %ds (%s)" % (j["i"], wait, wav[:80]), flush=True)
            time.sleep(wait)
            wav = one(j)
        out[str(j["i"])] = wav
        print("[batch %s] %s" % (j["i"], (wav[:90] if isinstance(wav, str) else wav)), flush=True)
    json.dump(out, open(sys.argv[2], "w"))


main()
