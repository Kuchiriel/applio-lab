#!/usr/bin/env python3
"""attrib-llm — atribuição de falante via LLM local (router :8080).
Uso: python3 attrib-llm.py caps/capNN.json [--only 3,7,12]
Alvos: UNKNOWNs + confs fracas. Prompt com contexto do capítulo + elenco.
Saída: caps/capNN-llm.json {i: {speaker, motivo}} (PROPOSTA, não aplica).
"""
import json
import re
import sys
import urllib.request

SEGPATH = sys.argv[1]
ONLY = None
if "--only" in sys.argv:
    ONLY = set(int(x) for x in sys.argv[sys.argv.index("--only") + 1].split(","))

ELENCO = ("KLEIN (Zhou Mingrui, protagonista, jovem, pensa/fala em 1ª pessoa), "
          "NARRADOR (voz onisciente 3ª pessoa), MELISSA (irmã), BENSON (irmão), "
          "DUNN (capitão), LEONARD, ALGER, AUDREY, DALY, NEIL, VENN (vendedor), "
          "WENDY, ANNIE (criada), TREINADORA, CARTOMANTE")

data = json.load(open(SEGPATH))["segments"]
WEAK = {"resíduo", "alternância-fraca", "citacao-sem-atribuicao"}
targets = [s for s in data if s["speaker"] == "UNKNOWN" or s.get("conf", "") in WEAK]
if ONLY is not None:
    targets = [s for s in targets if s["i"] in ONLY]
print("alvos: %d" % len(targets))

CTX = "\n".join("[%d] (%s) %s" % (s["i"], s["speaker"], s["text"][:160]) for s in data)


def ask(batch):
    qs = "\n".join("SEG %d: %s" % (s["i"], s["text"][:300]) for s in batch)
    prompt = (
        "Você atribui falas em um romance (Lord of the Mysteries, cap. em PT-BR).\n"
        "Elenco: %s.\n"
        "Klein=Zhou Mingrui (mesma pessoa). Pensamento 1ª pessoa=KLEIN. "
        "Narração 3ª pessoa=NARRADOR. Diálogo com verbo+nome manda. "
        "Lore citada não indica falante.\n\nCAPÍTULO (índice, falante-atual, texto):\n%s\n\n"
        "Decida o falante de:\n%s\n"
        "Responda UMA LINHA POR SEG, formato exato:\n"
        "NUMERO: FALANTE - motivo curto\n"
        "FALANTE ∈ {KLEIN,NARRADOR,MELISSA,BENSON,DUNN,LEONARD,ALGER,AUDREY,"
        "DALY,NEIL,VENN,WENDY,ANNIE,TREINADORA,CARTOMANTE,SFX,UNKNOWN}. "
        "UNKNOWN só se impossível. Sem JSON, sem rodeios." % (ELENCO, CTX, qs))
    body = json.dumps({"model": "bonsai", "messages": [{"role": "user", "content": prompt}],
                       "temperature": 0.1, "max_tokens": 1200}).encode()
    req = urllib.request.Request("http://localhost:8080/v1/chat/completions",
                                 data=body, headers={"Content-Type": "application/json"})
    r = urllib.request.urlopen(req, timeout=300)
    txt = json.load(r)["choices"][0]["message"]["content"]
    out = {}
    for m in re.finditer(r"(\d+)\s*:\s*([A-Z-]+)\s*-\s*(.+)", txt):
        out[m.group(1)] = {"sp": m.group(2), "porque": m.group(3).strip()[:100]}
    return out


out = {}
for b in range(0, len(targets), 5):
    batch = targets[b:b + 5]
    try:
        r = ask(batch)
        out.update(r)
        print("lote %d: %s" % (b // 5, {k: v.get("sp") for k, v in r.items()}))
    except Exception as e:
        print("lote %d FALHOU: %s" % (b // 5, str(e)[:100]))
json.dump(out, open(SEGPATH.replace(".json", "-llm.json"), "w"), ensure_ascii=False, indent=1)
print("salvo:", SEGPATH.replace(".json", "-llm.json"), "| vereditos:", len(out))
