#!/usr/bin/env python3
"""Audiobook LOTM — cap. a cap.: segmenta narração×fala, atribui falante,
sintetiza com voz por personagem (base + RVC + pitch) e concatena.

Etapas:
  parse .../Vol1.epub --chapter 1 --> caps/cap01.json (segmentos + falante)
  render caps/cap01.json --> cap01.wav (via `jarvis speak`)

Atribuição (sem marcar na mão):
  1. travessão (—) = fala; resto = NARRADOR (pensamento em 1ª pessoa = KLEIN).
  2. verbo de fala + nome no mesmo parágrafo ou vizinhos ("disse X", "X perguntou").
  3. alternância: fala sem marca após fala de A em diálogo A-B = B.
  4. resíduo = UNKNOWN (LLM local depois; nunca adivinha).

Mapa de vozes (personagens/lotm-voices.json):
  {"NARRADOR": {"base": "antonio", "rvc": null, "pitch": 0},
   "KLEIN": {"base": "antonio", "rvc": "klein", "pitch": 0}, ...}
"""
import argparse
import json
import os
import re
import subprocess
import sys

VERBS = ("disse", "perguntou", "respondeu", "gritou", "sussurrou", "exclamou",
         "murmurou", "comentou", "afirmou", "negou", "riu", "chorou", "pensou")
NAMES = ("Klein", "Moretti", "Zhou", "Mingrui", "Benson", "Melissa", "Dunn",
         "Leonard", "Audrey", "Alger", "Daly", "Neil", "Roselle", "Welch",
         "Naya", "Klee", "Susie", "Hanass", "Vincent", "Azik", "Dalí")
NAME_RE = r"(?:%s)[\w ]{0,20}" % "|".join(NAMES)


def parse_epub(epub_path, chapter):
    from ebooklib import epub, ITEM_DOCUMENT
    from bs4 import BeautifulSoup
    bk = epub.read_epub(epub_path)
    # epub splitado: título num arquivo, texto nos seguintes. Varre em ordem.
    items = [i for i in bk.get_items() if i.get_type() == ITEM_DOCUMENT]
    cur_title, cur_paras = None, None
    for item in items:
        soup = BeautifulSoup(item.get_content(), "html.parser")
        for p in soup.find_all("p"):
            t = p.get_text().strip()
            if not t:
                continue
            m = re.match(r"CAPÍTULO\s+(\d+)\s*:?\s*(.*)", t, re.I)
            if m:
                if cur_paras is not None:
                    return cur_title, cur_paras  # próximo capítulo: fecha
                if int(m.group(1)) == chapter:
                    cur_title = t
                    cur_paras = []
                continue
            if cur_paras is not None:
                cur_paras.append(t)
    if cur_paras is not None:
        return cur_title, cur_paras
    raise SystemExit("capítulo %d não achado" % chapter)


def speaker_of(paras, i, last_speaker):
    """Retorna (falante, confiança)."""
    p = paras[i]
    if not p.startswith("—"):
        # pensamento 1ª pessoa do protagonista = KLEIN, resto NARRADOR
        if re.search(r"\b(eu|meu|minha|me|mim|vou|preciso|será que)\b", p, re.I) \
                and len(p) < 300:
            return "KLEIN", "pensamento-1p"
        return "NARRADOR", "narração"
    # verbo de fala + nome no próprio parágrafo
    m = re.search(r"(%s)\s+([A-Z][\w]+)" % "|".join(VERBS), p)
    if m and m.group(2).upper() in [n.upper() for n in NAMES]:
        return m.group(2).upper(), "verbo-nome"
    m = re.search(r"([A-Z][\w]+)\s+(%s)" % "|".join(VERBS), p)
    if m and m.group(1).upper() in [n.upper() for n in NAMES]:
        return m.group(1).upper(), "nome-verbo"
    # vizinhos (anterior/posterior, narração colada)
    for j in (i - 1, i + 1):
        if 0 <= j < len(paras) and not paras[j].startswith("—"):
            for v in VERBS:
                m = re.search(r"%s\s+([A-Z][\w]+)" % v, paras[j])
                if m and m.group(1).upper() in [n.upper() for n in NAMES]:
                    return m.group(1).upper(), "vizinho"
    # alternância simples: última fala conhecida em diálogo
    if last_speaker and last_speaker != "NARRADOR":
        return "ALT?(%s)" % last_speaker, "alternância-fraca"
    return "UNKNOWN", "resíduo"


def cmd_parse(a):
    title, paras = parse_epub(a.epub, a.chapter)
    segs, last = [], None
    for i, p in enumerate(paras):
        who, conf = speaker_of(paras, i, last)
        if who.startswith("ALT?"):
            who = "UNKNOWN"
        if who not in ("NARRADOR", "UNKNOWN"):
            last = who
        segs.append({"i": i, "text": p, "speaker": who, "conf": conf})
    os.makedirs(a.outdir, exist_ok=True)
    out = os.path.join(a.outdir, "cap%02d.json" % a.chapter)
    json.dump({"title": title, "segments": segs}, open(out, "w"), ensure_ascii=False, indent=1)
    from collections import Counter
    print(title, "|", len(segs), "segmentos")
    for k, v in Counter(s["speaker"] for s in segs).most_common():
        print("  %-12s %d" % (k, v))


def cmd_tag(a):
    """Imprime segmentos p/ o dono taguear: [i] = FALANTE."""
    data = json.load(open(a.segments))
    for s in data["segments"]:
        print("[%d] %s | %s" % (s["i"], s["speaker"], s["text"][:150]))


def cmd_relabel(a):
    """Aplica correções do dono: --set 12=KLEIN --set 30=NARRADOR ..."""
    data = json.load(open(a.segments))
    fixes = {}
    for item in a.set:
        idx, who = item.split("=", 1)
        fixes[int(idx)] = who.strip().upper()
    for s in data["segments"]:
        if s["i"] in fixes:
            print("[%d] %s -> %s" % (s["i"], s["speaker"], fixes[s["i"]]))
            s["speaker"] = fixes[s["i"]]
            s["conf"] = "dono"
    json.dump(data, open(a.segments, "w"), ensure_ascii=False, indent=1)
    print("salvo:", a.segments)


def cmd_render(a):
    data = json.load(open(a.segments))
    voices = json.load(open(a.voices))
    tmp = a.out + ".parts"
    os.makedirs(tmp, exist_ok=True)
    # 1. base de todos (rápido, sem RVC)
    jobs = []  # (seg_i, base_wav, rvc_key)
    for s in data["segments"]:
        v = voices.get(s["speaker"], voices.get("UNKNOWN", {"base": "antonio", "rvc": None, "pitch": 0}))
        cmd = ["jarvis", "speak", s["text"], "--no-play"]
        if v.get("base", "antonio") != "antonio":
            cmd += ["--base", v["base"]]
        print("[base %s] %s" % (s["speaker"], s["text"][:60]), flush=True)
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        line = (r.stdout or "").strip().splitlines()
        wav = line[-1] if line else ""
        if not wav or wav.startswith("ERROR") or not os.path.exists(wav):
            print("FALHA seg", s["i"], (r.stdout or "")[-200:], (r.stderr or "")[-200:])
            sys.exit(1)
        g = os.path.join(tmp, "g%03d.wav" % s["i"])
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", wav,
                        "-ar", "44100", "-ac", "1", g], check=True)
        jobs.append((s["i"], g, v.get("rvc"), v.get("pitch", 0)))
    # 2. RVC em lote por timbre (UMA carga por voz, via nix develop)
    need_clone = [(i, g, rvc, pitch) for i, g, rvc, pitch in jobs if rvc]
    groups = {}
    for i, g, rvc, pitch in need_clone:
        groups.setdefault((rvc, pitch or 0), []).append((i, g))
    for (rvc, pitch), lst in groups.items():
        # lotes de até 5 (lote grande derruba o driver sem isolamento)
        for b in range(0, len(lst), 5):
            sub = lst[b:b + 5]
            print("[rvc %s pitch=%s] %d/%d segs, 1 carga" % (rvc, pitch, len(sub), len(lst)), flush=True)
            pairs = [[i, g, g.replace(".wav", "-%s.wav" % rvc)] for i, g in sub]
        payload_f = os.path.join(tmp, "batch-%s.json" % rvc)
        json.dump({"pairs": pairs, "rvc": rvc, "pitch": pitch}, open(payload_f, "w"))
        code = (
            "import json,sys; d=json.load(open(sys.argv[1]));"
            "from jarvis.core.voice import _resolve_rvc;"
            "from jarvis.core.voice_clone import clone_many;"
            "mp, ix = _resolve_rvc(d['rvc']);"
            "res = clone_many([(p[1], p[2]) for p in d['pairs']], cpu_only=True,"
            " model_path=mp, index_path=ix, timeout_s=1800,"
            " pitch=d['pitch'] or None);"
            "print(json.dumps(res))"
        )
        r = subprocess.run(["nix", "develop", "--command", "python3", "-c", code, payload_f],
                           stdin=subprocess.DEVNULL,
                           capture_output=True, text=True,
                           timeout=3600, cwd=os.path.expanduser("~/projects/nixos-ai"))
        try:
            got = json.loads((r.stdout or "").strip().splitlines()[-1])
        except Exception:
            print("FALHA lote rvc", rvc, (r.stdout or "")[-300:], (r.stderr or "")[-300:])
            sys.exit(1)
        bad = [k for k, v in got.items() if v.startswith("ERROR")]
        if bad:
            print("FALHA clone:", bad[:3], list(got.values())[0][:150])
            sys.exit(1)
    # 3. monta final (clone ou base) e concatena
    final = {}
    for i, g, rvc, pitch in jobs:
        final[i] = g.replace(".wav", "-%s.wav" % rvc) if rvc else g
        if not os.path.exists(final[i]):
            print("FALTA:", final[i])
            sys.exit(1)
        if rvc:
            h = os.path.join(tmp, "f%03d.wav" % i)
            subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", final[i],
                            "-ar", "44100", "-ac", "1", h], check=True)
            final[i] = h
    files = [final[s["i"]] for s in data["segments"]]
    lst = os.path.join(tmp, "list.txt")
    open(lst, "w").write("".join("file '%s'\n" % f for f in files))
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0",
                    "-i", lst, "-c", "copy", a.out], check=True)
    print("OK:", a.out)


def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    q = sub.add_parser("parse"); q.add_argument("epub"); q.add_argument("--chapter", type=int, required=True)
    q.add_argument("--outdir", default="caps")
    r = sub.add_parser("render"); r.add_argument("segments"); r.add_argument("--voices", required=True)
    r.add_argument("--out", required=True)
    t = sub.add_parser("tag"); t.add_argument("segments")
    l = sub.add_parser("relabel"); l.add_argument("segments"); l.add_argument("--set", action="append", default=[])
    a = p.parse_args()
    {"parse": cmd_parse, "render": cmd_render, "tag": cmd_tag, "relabel": cmd_relabel}[a.cmd](a)


if __name__ == "__main__":
    main()
