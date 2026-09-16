#!/usr/bin/env python3
"""review-grounded — revisor via harness LLMClient + validador de evidência.
Uso: kvenv/bin/python review-grounded.py caps/capNN.json
1. Pega vereditos capNN-llm.json; 2. revisa via LLMClient (disciplina do
   harness); 3. REJEITA evidência que não seja substring verbatim do texto
   (anti-alucinação); 4. salva capNN-rev.json (só vereditos com evidência
   grounded). Critério de parada: sem evidência grounded = mantém anterior.
"""
import json
import sys

sys.path.insert(0, "/home/nixos/projects/nixos-ai/modules/ai/jarvis/src")

SEGPATH = sys.argv[1]
data = json.load(open(SEGPATH))["segments"]
prev = json.load(open(SEGPATH.replace(".json", "-llm.json")))
byid = {s["i"]: s for s in data}

from jarvis.providers.llm import LLMClient
from jarvis.core.config import Config

client = LLMClient(Config())
CTX = "\n".join("[%d] %s" % (s["i"], s["text"][:200]) for s in data)
prop = "\n".join("%s -> %s (%s)" % (k, v.get("sp"), v.get("porque", ""))
                 for k, v in sorted(prev.items(), key=lambda x: int(x[0])))

prompt = (
    "Você é REVISOR INDEPENDENTE. Abaixo vereditos de falante por segmento.\n"
    "Para CADA um, responda UMA LINHA: NUMERO: CONFIRMO|REFUTO FALANTE | \"CITAÇÃO\" | motivo curto.\n"
    "A CITAÇÃO é COPIADA E COLADA do segmento, byte por byte: proibido "
    "reticências, paráfrase, normalização ou completar frase. Vou conferir "
    "por código e rejeitar o que não for substring exata. Sem citação, MANTER.\n\n"
    "CAPÍTULO:\n%s\n\nVEREDITOS:\n%s" % (CTX, prop))
resp = client.chat_with_tools(
    messages=[{"role": "user", "content": prompt}],
    max_tokens=2048, temperature=0.1,
    extra={"chat_template_kwargs": {"enable_thinking": False}})
txt = resp.content or ""
print(txt[:1500])

import re

final, rej = {}, 0
for m in re.finditer(
        r"(\d+)\s*(?:->\s*NUMERO\s*:)?\s*:?\s*(CONFIRMO|REFUTO|MANTER)\s*([A-Z-]+)?\s*\|?\s*[\"“]([^\"”]*)[\"”]?",
        txt):
    i, v, sp, quote = m.group(1), m.group(2), m.group(3), (m.group(4) or "")
    seg = byid.get(int(i), {}).get("text", "")
    if quote and quote not in seg:
        rej += 1
        continue  # alucinação: evidência não está no texto
    if v == "REFUTO" and sp:
        final[i] = {"sp": sp, "porque": "revisor+evidência", "quote": quote}
    elif v == "CONFIRMO":
        old = prev.get(i, {})
        final[i] = {"sp": old.get("sp"), "porque": "confirmado",
                    "quote": quote}
print("grounded: %d rejeitadas: %d" % (len(final), rej))
json.dump(final, open(SEGPATH.replace(".json", "-rev.json"), "w"),
          ensure_ascii=False, indent=1)
