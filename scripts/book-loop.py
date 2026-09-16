#!/usr/bin/env python3
"""book-loop — tacar um livro e o sistema se virar (dono 16/09).
Uso: book-loop.py <epub> "<pergunta>" [--caps 1-5]
1. Extrai capítulos p/ staging .md; 2. indexa no RAG (books);
3. rolling summary por capítulo (LLM); 4. responde pergunta com
RAG (books) + summaries (ring-context em arquivo).
"""
import json
import os
import re
import sys

sys.path.insert(0, "/home/nixos/projects/applio-lab")
sys.path.insert(0, "/home/nixos/projects/nixos-ai/modules/ai/jarvis/src")

EPUB, QUESTION = sys.argv[1], sys.argv[2]
STAGE = "/tmp/bookloop"
os.makedirs(STAGE, exist_ok=True)

from ebooklib import epub, ITEM_DOCUMENT
from bs4 import BeautifulSoup

bk = epub.read_epub(EPUB)
chap, cur, n = None, [], 0
files = []
for item in bk.get_items():
    if item.get_type() != ITEM_DOCUMENT:
        continue
    soup = BeautifulSoup(item.get_content(), "html.parser")
    for p in soup.find_all(["p", "h1", "h2", "h3"]):
        t = p.get_text().strip()
        if not t:
            continue
        if re.match(r"CAP[ÍI]TULO\s+(\d+)", t, re.I):
            if cur:
                f = os.path.join(STAGE, "cap%03d.md" % n)
                open(f, "w").write("# %s\n\n" % chap + "\n\n".join(cur))
                files.append(f)
                cur = []
            n += 1
            chap = t
            continue
        if chap:
            cur.append(t)
if cur:
    f = os.path.join(STAGE, "cap%03d.md" % n)
    open(f, "w").write("# %s\n\n" % chap + "\n\n".join(cur))
    files.append(f)
print("caps: %d" % len(files))

# rolling summaries ( UMA chamada por cap, curto)
from jarvis.providers.llm import LLMClient
from jarvis.core.config import Config

MAXC = int(os.environ.get("BOOKLOOP_CAPS", "0"))  # 0 = todos
client = LLMClient(Config())
summ = {}
for f in files[:MAXC or None]:
    txt = open(f).read()
    prev = json.dumps(summ, ensure_ascii=False)[:1500]
    prompt = ("Resuma este capítulo em 5 linhas (português): quem, onde, "
              "o que muda. Contexto anterior: %s\n\nTEXTO:\n%s" % (prev, txt[:6000]))
    r = client.chat_with_tools(
        messages=[{"role": "user", "content": prompt}],
        max_tokens=400, temperature=0.1,
        extra={"chat_template_kwargs": {"enable_thinking": False}})
    summ[os.path.basename(f)] = (r.content or "")[:800]
    print(os.path.basename(f), "ok", flush=True)
json.dump(summ, open("/tmp/bookloop-summ.json", "w"), ensure_ascii=False, indent=1)

# QA: RAG books (se indexado) + summaries como ring-context
try:
    from jarvis.core.rag import HybridSearch
    import asyncio
    hits = asyncio.run(HybridSearch().search(QUESTION, collection="books", top_k=5))
    ev = "\n".join(h.get("text", "")[:500] for h in (hits or [])[:5])
except Exception as e:
    ev = "(RAG indisponível: %s)" % str(e)[:100]
prompt = ("Com base nos resumos + trechos, responda (português, com capítulo):\n"
          "RESUMOS:\n%s\n\nTRECHOS:\n%s\n\nPERGUNTA: %s" % (
              json.dumps(summ, ensure_ascii=False)[:4000], ev, QUESTION))
r = client.chat_with_tools(
    messages=[{"role": "user", "content": prompt}],
    max_tokens=800, temperature=0.1,
    extra={"chat_template_kwargs": {"enable_thinking": False}})
print("RESPOSTA:\n", (r.content or "")[:1500])
