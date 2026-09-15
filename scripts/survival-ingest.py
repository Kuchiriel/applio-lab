#!/usr/bin/env python3
"""Ingestão survival: EPUB/PDF -> .md limpo (tabelas preservadas, chunk por header).
Uso: python3 survival-ingest.py ~/Books outdir/
Pula: LOTM*, test_*, HFC (não-survival). PDFs exigem pymupdf.
"""
import os
import re
import sys

SKIP = ("lotm", "test_", "hfc", "oceanofpdf.com_life_in_the_universe",
        "oceanofpdf.com_origins")


def clean(t):
    t = re.sub(r"\n{3,}", "\n\n", t)
    return t.strip()


def epub_to_md(path):
    from ebooklib import epub, ITEM_DOCUMENT
    from bs4 import BeautifulSoup
    bk = epub.read_epub(path)
    parts = []
    for item in bk.get_items():
        if item.get_type() != ITEM_DOCUMENT:
            continue
        soup = BeautifulSoup(item.get_content(), "html.parser")
        for tbl in soup.find_all("table"):
            rows = []
            for tr in tbl.find_all("tr"):
                cells = [c.get_text(" ", strip=True) for c in tr.find_all(["td", "th"])]
                if cells:
                    rows.append("| " + " | ".join(cells) + " |")
            if rows:
                tbl.replace_with("\n" + "\n".join(rows) + "\n")
        for h in soup.find_all(["h1", "h2", "h3", "h4"]):
            lvl = int(h.name[1])
            h.replace_with("\n" + "#" * lvl + " " + h.get_text(" ", strip=True) + "\n")
        txt = soup.get_text("\n")
        if len(txt.strip()) > 200:
            parts.append(txt)
    return clean("\n\n".join(parts))


def pdf_to_md(path):
    import fitz
    doc = fitz.open(path)
    parts = []
    for pno, page in enumerate(doc):
        tabs = page.find_tables()
        txt = page.get_text("text")
        for t in tabs:
            md = "\n".join("| " + " | ".join(c or "" for c in row) + " |" for row in t.extract())
            txt += "\n" + md + "\n"
        if len(txt.strip()) > 200:
            parts.append(f"\n## página {pno + 1}\n" + txt)
    return clean("\n\n".join(parts))


def main():
    src, out = sys.argv[1], sys.argv[2]
    os.makedirs(out, exist_ok=True)
    for f in sorted(os.listdir(src)):
        low = f.lower()
        if not low.endswith((".epub", ".pdf")):
            continue
        if low.startswith(SKIP):
            continue
        dst = os.path.join(out, os.path.splitext(f)[0] + ".md")
        if os.path.exists(dst):
            print("pula (existe):", f, flush=True)
            continue
        try:
            md = epub_to_md(os.path.join(src, f)) if low.endswith(".epub") else pdf_to_md(os.path.join(src, f))
            open(dst, "w").write("# " + f + "\n\n" + md)
            print("ok: %s (%dk chars)" % (f, len(md) // 1024), flush=True)
        except Exception as e:
            print("FALHA %s: %s" % (f, str(e)[:100]), flush=True)


main()
