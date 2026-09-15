#!/usr/bin/env python3
"""STT faster-whisper turbo (GPU; fallback CPU int8). Uso: fw-stt.py vocals.wav out.srt"""
import sys


def ts(x):
    h, r = divmod(int(x), 3600)
    mnt, s = divmod(r, 60)
    return "%02d:%02d:%02d,%03d" % (h, mnt, s, int(x % 1 * 1000))


def main():
    vocals, out = sys.argv[1], sys.argv[2]
    from faster_whisper import WhisperModel
    try:
        m = WhisperModel("turbo", device="cuda", compute_type="float16")
    except Exception as e:
        print("GPU falhou (%s), CPU int8" % str(e)[:80], flush=True)
        m = WhisperModel("turbo", device="cpu", compute_type="int8")
    segs, _ = m.transcribe(vocals, language="pt", vad_filter=True)
    lines = []
    for i, s in enumerate(segs, 1):
        lines.append("%d\n%s --> %s\n%s\n" % (i, ts(s.start), ts(s.end), s.text.strip()))
    open(out, "w").write("\n".join(lines))
    print("STT ok: %d segs -> %s" % (len(lines), out), flush=True)


main()
