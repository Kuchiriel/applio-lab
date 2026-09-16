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
         "murmurou", "comentou", "afirmou", "negou", "riu", "chorou", "pensou",
         "retrucou", "exalou", "questionou", "leu", "acenou", "assentiu",
         "balançou", "apontou", "continuou", "prosseguiu", "completou",
         "acrescentou", "concluiu", "ordenou", "insistiu", "praguejou",
         "ecoou", "repetiu", "desejava", "ponderou", "confessou")
NAMES = ("Klein", "Moretti", "Zhou", "Mingrui", "Benson", "Melissa", "Dunn",
         "Leonard", "Audrey", "Alger", "Daly", "Neil", "Roselle", "Welch",
         "Naya", "Klee", "Susie", "Hanass", "Vincent", "Azik", "Dalí",
         "Wendy", "Annie")
# Epítetos → personagem (audits caps 10/12, fase 2): sujeito explícito que
# o vizinho sobrescrevia. Normalizado antes do casamento verbo-nome.
EPITHETS = {"inspetor de olhos cinzentos": "DUNN",
            "inspetor de polícia de olhos cinzentos": "DUNN",
            "o policial": "DUNN",
            "olhos verdes e temperamento de poeta": "LEONARD"}
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


# Interjeições avulsas: SFX (nunca narrar) vs Klein (sentir/falar).
SFX_WORDS = {"pá", "toc", "bum", "crac", "bang", "plop", "clique",
             "shuasss", "honk", "fffffff", "crash", "splash", "thud", "clang",
             "clop", "clinque", "clangue"}


def speaker_of(paras, i, last_speaker):
    """Retorna (falante, confiança)."""
    p = paras[i]
    # entrada de diário datada ("29 de maio...") = Klein LENDO em voz alta
    # (fase 2: cap09 Welch; o morto não fala, quem lê é o Klein)
    if re.match(r"^[\u201c\"]?\d{1,2} de [a-zç]+\.?", p.strip(), re.I):
        return "KLEIN", "diario-lendo"
    # nota de rodapé virou parágrafo: coletar p/ RELOCAR após o [N]
    # (dono 15/09: nota do fim deve ser narrada logo após o marcador)
    mnote = re.match(r"^(?:\[(\d+)\]|(\d{1,2})\.\s)(.*)$", p, re.S)
    if mnote:
        return "NOTE:%s" % (mnote.group(1) or mnote.group(2)), mnote.group(3).strip()
    # citação “...”: COM verbo/nome = diálogo (resolve abaixo); leitura
    # (precedida de "dizia o seguinte:") = NARRADOR; avulsa sem
    # atribuição = UNKNOWN honesto (fase 2: pregão/invocação não são Klein;
    # continuação só em diálogo ativo comprovado).
    if p.startswith("\u201c"):
        has_attr = bool(re.search(r"(%s)" % "|".join(VERBS), p, re.I)) or \
            any(n.lower() in p.lower() for n in NAMES)
        if not has_attr:
            return "UNKNOWN", "citacao-sem-atribuicao"
        # cai no fluxo de diálogo abaixo (verbo-nome etc.)
        p = "— " + p
    # onomatopeia avulsa = SFX (dono 15/09: Pá!/Toc! não são fala).
    # Inclui repetição de char ("Ffffffff!", "Toc! Toc!") — fase 2.
    words = [w.strip(",.…! ").lower() for w in p.split()]
    if words and len(p) < 60 and all(
            w in SFX_WORDS or re.fullmatch(r"(.)\1{2,}", w) for w in words):
        return "SFX", "onomatopeia"
    # interjeição avulsa curta ("Doloroso!") = Klein sentindo (dono 15/09)
    if len(words) <= 3 and p.strip().endswith(("!", "…", "...")) and len(p) < 60 \
            and not p.startswith(("—", "–", "-", '"', "\u201c", "«")):
        return "KLEIN", "interjeicao-avulsa"
    # "Isto..." = expressão de realização do Klein ("já sei/entendi", dono 15/09)
    if re.match(r"^Isto[,.…]", p):
        return "KLEIN", "isto-realizacao"
    if not p.startswith(("—", "–", "-", '"', "\u201c", "\u201d", "«")):
        # pergunta avulsa curta sem atribuição = Klein pensando em voz alta
        # (audits caps 2-5; fase 2). SÓ ? — ! declarativa é narração
        # (regressão cap01 fase 2: "Era um texto..." é NARRADOR).
        ps = p.strip()
        has_1p = bool(re.search(
            r"\b(eu|meu|minha|meus|minhas|me|mim|vou|preciso|sinto|acho|quero|posso|dói)\b",
            ps, re.I))
        has_3p = bool(re.search(
            r"\b(ele|ela|eles|elas|seu|sua|Klein|Zhou|Mingrui)\b", ps))
        if re.match(r"^[^?!.]{2,150}\?$", ps) and len(ps) < 150 \
                and not re.search(r"(%s)" % "|".join(VERBS), ps, re.I) \
                and (has_1p or not has_3p):
            return "KLEIN", "pergunta-avulsa"
        # sujeito explícito (nome/epíteto + verbo) antes do pensamento-1p:
        # evita falso-1p com nome de OUTRO (audits caps 3/5/11; fase 2).
        # Epíteto + verbo de fala = sinal forte, retorna direto (fase 2:
        # "Naya... disse o inspetor..." não é Naya).
        for epi, who in EPITHETS.items():
            if epi in p.lower() and re.search(
                    r"(%s)" % "|".join(VERBS), p, re.I):
                return who, "epiteto-forte"
        plow2 = p
        m = re.search(r"([A-Z][\w]+)[^.!?]{0,80}?\s+(%s)" % "|".join(VERBS), plow2)
        if m and m.group(1).upper() in [n.upper() for n in NAMES] \
                and m.group(1).upper() not in ("KLEIN", "MORETTI", "ZHOU", "MINGRUI"):
            return m.group(1).upper(), "sujeito-narracao"
        m = re.search(r"(%s)\s+([A-Z][\w]+)" % "|".join(VERBS), plow2)
        if m and m.group(2).upper() in [n.upper() for n in NAMES]:
            return m.group(2).upper(), "sujeito-narracao-vn"
        # pensamento 1ª pessoa do protagonista = KLEIN, resto NARRADOR
        # ("seu eu" NÃO é 1ª pessoa — dono 15/09: varrer-de-olhos era narração)
        if re.search(r"(?<!seu )\b(eu|meu|minha|meus|minhas|me|mim|vou|preciso|será que|sinto|acho|quero|posso|devo|dói|doeu|hã)\b", p, re.I) \
                and len(p) < 300:
            return "KLEIN", "pensamento-1p"
        return "NARRADOR", "narração"
    # verbo de fala + nome no próprio parágrafo (epítetos normalizados antes)
    # Epíteto + verbo = sinal forte também em diálogo (fase 2)
    for epi, who in EPITHETS.items():
        if epi in p.lower() and re.search(
                r"(%s)" % "|".join(VERBS), p, re.I):
            return who, "epiteto-forte"
    plow = p
    for epi, who in EPITHETS.items():
        if epi in p.lower():
            plow = who + " " + p
            break
    m = re.search(r"(%s)\s+([A-Z][\w]+)" % "|".join(VERBS), plow)
    if m and m.group(2).upper() in [n.upper() for n in NAMES]:
        return m.group(2).upper(), "verbo-nome"
    m = re.search(r"([A-Z][\w]+)\s+(%s)" % "|".join(VERBS), plow)
    if m and m.group(1).upper() in [n.upper() for n in NAMES]:
        return m.group(1).upper(), "nome-verbo"
    # nome ... verbo à distância (ex: "Audrey acenou..., mas perguntou" —
    # audits caps 6-7: sujeito explícito longe do verbo)
    m = re.search(r"([A-Z][\w]+)[^.!?]{0,80}?\s+(%s)" % "|".join(VERBS), plow)
    if m and m.group(1).upper() in [n.upper() for n in NAMES]:
        return m.group(1).upper(), "nome-verbo-longo"
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
    idx = 0
    for i, p in enumerate(paras):
        # continuação minúscula = mesmo parágrafo do livro (dono 15/09: 18+19)
        if segs and p and p[0].islower():
            segs[-1]["text"] += " " + p
            continue
        # interjeição repetida ("Calma, calma, calma" até no meio do parágrafo)
        # = 1 seg por repetição (dono 15/09: espaçamento robótico; segs
        # separados ganham silêncio entre si)
        m = re.match(r"^(?P<inj>(?P<w>\w+)[,.…]*(?:\s+(?i:(?P=w))[,.…]*…?){2})(?P<rest>.*)$",
                     p.strip(), re.S)
        if m and len(m.group("inj")) < 120:
            # interjeição do protagonista em pensamento = KLEIN (dono 15/09)
            for rep in [w for w in re.split(r"\s+", m.group("inj").strip()) if w]:
                segs.append({"i": idx, "text": rep.strip(",.…! "),
                             "speaker": "KLEIN", "conf": "interjeicao-split"})
                idx += 1
            last = "KLEIN"
            rest = m.group("rest").strip()
            if rest:
                paras[i] = rest; p = rest  # reprocessa o resto no fluxo normal
            else:
                continue
        # "Isto.../Isso.../Ai..." + continuação narrativa = só o fragmento é
        # Klein ("já sei", dor); resto volta ao fluxo (dono 15/09)
        m2 = re.match(r"^((?:Isto|Isso|Ai|Ei|Ah|Oh|Hã)[,.…?!]+)(.*)$", p.strip(), re.S)
        if m2 and len(m2.group(2).strip()) > 20:
            segs.append({"i": idx, "text": m2.group(1).strip(), "speaker": "KLEIN",
                         "conf": "fragmento-klein"})
            idx += 1
            last = "KLEIN"
            paras[i] = m2.group(2).strip(); p = paras[i]
        # perguntas/exclamações líderes ("Uma arma? Um revólver? Zhou...") =
        # cada uma é fala do Klein; resto volta ao fluxo (dono 15/09).
        # NÃO splita onomatopeia pura ("Clinque! Clangue!" = SFX; fase 2).
        sfxonly = all(w.strip(",.…! ").lower() in SFX_WORDS
                      for w in p.strip().split()) and len(p.strip()) < 60
        while not sfxonly:
            m3 = re.match(r"^([^?!.]{2,90}[?!])\s+([A-ZÀ-Ú\"“].*)$", p.strip(), re.S)
            if not m3:
                break
            segs.append({"i": idx, "text": m3.group(1).strip(), "speaker": "KLEIN",
                         "conf": "pergunta-klein"})
            idx += 1
            last = "KLEIN"
            paras[i] = m3.group(2).strip(); p = paras[i]
        who, conf = speaker_of(paras, i, last)
        if who == "SKIP":
            continue
        if who.startswith("NOTE:"):
            # guarda nota p/ inserir após o segmento que cita [N]
            notes = getattr(cmd_parse, "_notes", None)
            if notes is None:
                cmd_parse._notes = notes = {}
            notes[who.split(":")[1]] = conf
            continue
        if who in ("ZHOU", "MINGRUI"):
            who, conf = "KLEIN", conf + "+alias-zhou"
        if who.startswith("ALT?"):
            who = "UNKNOWN"
        if who not in ("NARRADOR", "UNKNOWN"):
            last = who
        # leitura em voz alta ("...dizia o seguinte:" + citação) = NARRADOR
        # (fase 2: caderno cap01; sem isso vira UNKNOWN honesto)
        if conf == "citacao-sem-atribuicao" and segs and re.search(
                r"(dizia|diz|escrito|lia-se|seguinte)\s*:?\s*$",
                segs[-1]["text"]):
            who, conf = "NARRADOR", "citacao-leitura"
        # citação avulsa sem atribuição dentro de diálogo ativo continua o
        # falante anterior — MAS só se o anterior estava em diálogo (não
        # narração/pensamento) e a citação não é endereçamento (fase 2:
        # pregão de vendedor e invocação da Audrey não são Klein).
        if conf in ("citacao-narrada", "citacao-leitura") and last and last != "NARRADOR":
            prev = segs[-1].get("conf", "") if segs else ""
            addr = bool(re.search(
                r"\b(Venha|Beba|despert|ordeno|você|senhor|O que|Como|Onde|"
                r"Espelho|Em nome|gostaria)\b", p))
            if not addr and prev.split("+")[0] in (
                    "fragmento-klein", "pergunta-klein", "interjeicao-split",
                    "pergunta-avulsa", "verbo-nome", "nome-verbo",
                    "nome-verbo-longo", "sujeito-narracao-vn", "diario-lendo",
                    "citacao-narrada+cont-dialogo", "epiteto-forte"):
                who, conf = last, conf + "+cont-dialogo"
                last = who
        segs.append({"i": idx, "text": p, "speaker": who, "conf": conf})
        idx += 1
    # reloca notas [N] p/ logo após o segmento que as cita (dono 15/09)
    notes = getattr(cmd_parse, "_notes", {}) or {}
    cmd_parse._notes = {}
    if notes:
        final = []
        for s in segs:
            final.append(s)
            for n in sorted(notes, key=int):
                if "[%s]" % n in s["text"]:
                    final.append({"i": -1, "text": notes[n], "speaker": "NARRADOR",
                                  "conf": "nota-relocada"})
        segs = final
        for k, s in enumerate(segs):
            s["i"] = k
    # *palavra* = ênfase do autor. Raiva/profanidade → style angry;
    # resto (ex: *web novels* = estrangeirismo) só tira os asteriscos.
    ANGER_LEX = re.compile(r"merda|droga|inferno|maldit|idiota|estúpid|raiva|ódio|porra|caralho|desgraç|morte|matar|morrer", re.I)
    for s in segs:
        m_ang = re.search(r"\*(.+?)\*", s["text"])
        if m_ang:
            if ANGER_LEX.search(m_ang.group(1)):
                s["style"] = "angry"
                s["conf"] += "+anger"
            s["text"] = s["text"].replace("*", "")
    os.makedirs(a.outdir, exist_ok=True)
    out = os.path.join(a.outdir, "cap%02d.json" % a.chapter)
    # relabels persistentes do dono (por TEXTO, não índice: reparse não apaga
    # correção — dono 15/09: "toda versão nova volta o erro")
    relab_path = os.path.join(a.outdir, "cap%02d-relabels.json" % a.chapter)
    relabels = {}
    if os.path.exists(relab_path):
        relabels = json.load(open(relab_path))
    for s in segs:
        if s["text"] in relabels:
            s["speaker"] = relabels[s["text"]]
            s["conf"] = "dono-persistente"
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
    """Aplica correções do dono: --set 12=KLEIN --set 30=NARRADOR ...
    Salva TAMBÉM em capNN-relabels.json (por texto) p/ sobreviver ao reparse."""
    data = json.load(open(a.segments))
    fixes = {}
    for item in a.set:
        idx, who = item.split("=", 1)
        fixes[int(idx)] = who.strip().upper()
    relab_path = os.path.join(os.path.dirname(a.segments),
                              os.path.basename(a.segments).split(".")[0] + "-relabels.json")
    relabels = json.load(open(relab_path)) if os.path.exists(relab_path) else {}
    for s in data["segments"]:
        if s["i"] in fixes:
            print("[%d] %s -> %s" % (s["i"], s["speaker"], fixes[s["i"]]))
            s["speaker"] = fixes[s["i"]]
            s["conf"] = "dono"
            relabels[s["text"]] = fixes[s["i"]]
    json.dump(data, open(a.segments, "w"), ensure_ascii=False, indent=1)
    json.dump(relabels, open(relab_path, "w"), ensure_ascii=False, indent=1)
    print("salvo:", a.segments, "+", relab_path)


def cmd_render(a):
    import hashlib
    import shutil
    data = json.load(open(a.segments))
    voices = json.load(open(a.voices))
    tmp = a.out + ".parts"
    os.makedirs(tmp, exist_ok=True)
    if not getattr(a, "only", None):
        # sem --only: limpa intermediários velhos (.parts) — índices mudam
        # no reparse e arquivos stale confundem o verify (fase 2).
        # O cache real (.cache, por conteúdo) preserva a velocidade.
        import glob as _glob
        for f in _glob.glob(os.path.join(tmp, "g*.wav")) + \
                 _glob.glob(os.path.join(tmp, "f*.wav")):
            try:
                os.remove(f)
            except OSError:
                pass
    # Cache por conteúdo (base + RVC): re-render só refaz o que mudou.
    # `--only 12,13` refaz só esses segmentos (resto vem do cache).
    cdir = a.out + ".cache"
    os.makedirs(cdir, exist_ok=True)

    def bkey(text, speaker, v, style=None):
        # salt v3: regras de pronúncia mudam sem mudar o texto (dono 15/09:
        # "dou feedback e gera com problema de novo" = cache velho)
        h = hashlib.sha1(json.dumps(
            ["v3", text, speaker, v.get("base"), v.get("voice"),
             v.get("rate"), v.get("speed"), v.get("style"), style,
             v.get("rvc"), v.get("pitch", 0),
             v.get("index_rate", 0.75)], ensure_ascii=False).encode()).hexdigest()[:12]
        return h

    only = None
    if getattr(a, "only", None):
        only = set(int(x) for x in a.only.split(","))
        print("deltas:", sorted(only), flush=True)
    # 1. base de todos (UM processo batch-speak, código do repo via kvenv)
    REPO_SRC = "/home/nixos/projects/nixos-ai/modules/ai/jarvis/src"
    KENV = "/home/nixos/kvenv/bin/python"
    bj = os.path.join(tmp, "base-jobs.json")
    bo = os.path.join(tmp, "base-out.json")
    bj_list = []
    jobs = []  # (seg_i, base_wav, rvc_key)
    for s in data["segments"]:
        v = voices.get(s["speaker"], voices.get("UNKNOWN", {"base": "antonio", "rvc": None, "pitch": 0}))
        st = s.get("style") or v.get("style")
        key = bkey(s["text"], s["speaker"], v, st)
        g = os.path.join(tmp, "g%03d.wav" % s["i"])
        if s["speaker"] == "SFX":
            # Sem SFX real ainda: NARRADOR fala a onomatopeia (dono 15/09).
            # Quando o som existir, sfx-map.json marca p/ trocar no master.
            print("[sfx %d] %s (falado, sem som ainda)" % (s["i"], s["text"][:60]), flush=True)
            v = voices.get("NARRADOR", v)
            st = s.get("style") or v.get("style")
            key = bkey(s["text"], s["speaker"], v, st)
        cached = os.path.join(cdir, key + ".base.wav")
        if os.path.exists(cached):
            print("[cache %s] %s" % (s["speaker"], s["text"][:60]), flush=True)
            shutil.copy2(cached, g)
            jobs.append((s["i"], g, v.get("rvc"), v.get("pitch", 0), v.get("index_rate", 0.75), key))
        else:
            bj_list.append({"i": s["i"], "text": s["text"],
                            "base": v.get("base", "antonio"), "voice": v.get("voice"),
                            "rate": v.get("rate"), "speed": v.get("speed"),
                            "style": st})
    if bj_list:
        import copy
        driver = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scripts", "batch-speak.py")
        NIXDIR = "/home/nixos/projects/nixos-ai"
        got = {}
        # antonio (Edge) roda no kvenv (tem edge_tts); kokoro roda no nix develop (tem kokoro).
        parts = [("edge", [j for j in bj_list if j.get("base", "antonio") == "antonio"]),
                 ("kokoro", [j for j in bj_list if j.get("base", "antonio") != "antonio"])]
        for tag, lst in parts:
            if not lst:
                continue
            pj, po = os.path.join(tmp, "base-jobs-%s.json" % tag), os.path.join(tmp, "base-out-%s.json" % tag)
            json.dump(lst, open(pj, "w"), ensure_ascii=False)
            print("[batch-speak:%s] %d segmentos" % (tag, len(lst)), flush=True)
            if tag == "edge":
                env = dict(os.environ)
                env["PYTHONPATH"] = REPO_SRC + (":" + env["PYTHONPATH"] if env.get("PYTHONPATH") else "")
                r = subprocess.run([KENV, driver, pj, po],
                                   capture_output=True, text=True, timeout=7200, env=env)
            else:
                env2 = {k: v for k, v in os.environ.items() if k != "LD_LIBRARY_PATH"}
                r = subprocess.run(["nix", "develop", "--command", "python3", driver, pj, po],
                                   capture_output=True, text=True, timeout=7200, cwd=NIXDIR, env=env2)
            print((r.stdout or "")[-800:])
            if r.returncode != 0:
                print("FALHA batch-speak:%s:" % tag, (r.stderr or "")[-500:])
                sys.exit(1)
            got.update(json.load(open(po)))
        for j in bj_list:
            i, wav = j["i"], got.get(str(j["i"]), "")
            if not wav or wav.startswith("ERROR") or not os.path.exists(wav):
                print("FALHA seg", i, wav[:150])
                sys.exit(1)
            v = voices.get(next(s["speaker"] for s in data["segments"] if s["i"] == i),
                           {"rvc": None, "pitch": 0, "index_rate": 0.75})
            spk = next(s["speaker"] for s in data["segments"] if s["i"] == i)
            if spk == "SFX":
                v = voices.get("NARRADOR", v)  # mesmo mapeamento do cached (fase 2)
            st = next((s.get("style") for s in data["segments"] if s["i"] == i), None) or v.get("style")
            key = bkey(j["text"], spk, v, st)
            g = os.path.join(tmp, "g%03d.wav" % i)
            subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", wav,
                            "-ar", "44100", "-ac", "1", g], check=True)
            shutil.copy2(g, os.path.join(cdir, key + ".base.wav"))
            jobs.append((i, g, v.get("rvc"), v.get("pitch", 0), v.get("index_rate", 0.75), key))
    jobs.sort()
    # 2. RVC em lote por timbre (UMA carga por voz; sub-lotes de 5 p/ estabilidade)
    # Deltas: --only limita TTS; RVC reaproveita conversão cacheada.
    batches = []
    need = []
    for i, g, rvc, pitch, ir, k in jobs:
        if not rvc:
            continue
        if only is not None and i not in only:
            continue
        need.append((i, g, rvc, pitch, ir, k))
    groups = {}
    for i, g, rvc, pitch, ir, k in need:
        groups.setdefault((rvc, pitch or 0, ir), []).append((i, g, k))
    slug_of = lambda r: os.path.basename(r).rsplit(".", 1)[0]
    for (rvc, pitch, ir), lst in groups.items():
        todo = []
        for i, g, k in lst:
            dst = os.path.join(os.path.dirname(g), os.path.basename(g)[:-4] + "-%s.wav" % slug_of(rvc))
            ck = os.path.join(cdir, k + ".rvc.wav")
            if os.path.exists(ck):
                print("[cache-rvc %d]" % i, flush=True)
                shutil.copy2(ck, dst)
            else:
                todo.append((i, g, dst, ck))
        for b in range(0, len(todo), 5):
            sub = todo[b:b + 5]
            print("[rvc %s pitch=%s index=%.2f] %d/%d segs" % (rvc, pitch, ir, len(sub), len(lst)), flush=True)
            batches.append({"rvc": rvc, "pitch": pitch, "index_rate": ir,
                            "pairs": [[i, g, dst] for i, g, dst, ck in sub],
                            "cache": [ck for i, g, dst, ck in sub]})
    payload_f = os.path.join(tmp, "batches.json")
    json.dump(batches, open(payload_f, "w"))
    code = (
        "import json,sys; bb=json.load(open(sys.argv[1]));"
        "from jarvis.core.voice import _resolve_rvc;"
        "from jarvis.core.voice_clone import clone_many;"
        "out={};"
        "[(mp,ix,res,None) for b in bb for (mp,ix) in [_resolve_rvc(b['rvc'])]"
        " for res in [clone_many([(p[1],p[2]) for p in b['pairs']], cpu_only=True,"
        " model_path=mp, index_path=ix, timeout_s=1800, pitch=b['pitch'] or None,"
        " index_rate=b.get('index_rate', 0.75))]"
        " for _ in [out.update(res)]];"
        "print(json.dumps(out))"
    )
    r = subprocess.run(["nix", "develop", "--command", "python3", "-c", code, payload_f],
                       stdin=subprocess.DEVNULL,
                       capture_output=True, text=True,
                       timeout=3600, cwd=os.path.expanduser("~/projects/nixos-ai"))
    try:
        got = json.loads((r.stdout or "").strip().splitlines()[-1])
    except Exception:
        print("FALHA lote rvc", (r.stdout or "")[-300:], (r.stderr or "")[-300:])
        sys.exit(1)
    bad = [k for k, v in got.items() if v.startswith("ERROR")]
    if bad:
        print("FALHA clone:", bad[:3], list(got.values())[0][:150])
        sys.exit(1)
    # guarda conversões frescas no cache
    for b in batches:
        for (i, g, dst), ck in zip(b["pairs"], b["cache"]):
            if os.path.exists(dst):
                shutil.copy2(dst, ck)
    # 3. monta final (clone ou base) e concatena
    final = {}
    for i, g, rvc, pitch, ir, k in jobs:
        final[i] = os.path.join(os.path.dirname(g), os.path.basename(g)[:-4] + "-%s.wav" % slug_of(rvc)) if rvc else g
        if not os.path.exists(final[i]):
            print("FALTA:", final[i])
            sys.exit(1)
        if rvc:
            h = os.path.join(tmp, "f%03d.wav" % i)
            # (fade/trim no RVC REMOVIDO 15/09: afade+silenceremove zerava o
            # áudio — rms 0.10→0.004 medido. Chiado de borda fica p/ depois,
            # com teste em sample antes.)
            subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", final[i],
                            "-ar", "44100", "-ac", "1", h], check=True)
            final[i] = h
    conf_of = {s["i"]: s.get("conf", "") for s in data["segments"]}
    files = [final[s["i"]] for s in data["segments"]]
    # Respiro entre segmentos (dono 15/09: velho precisa de fôlego):
    # 0.35s padrão; 0.9s após narração longa (>350 chars) = respiro;
    # interjeição-split (Calma!) ganha gap aleatório 0.25-0.8s (humano,
    # nunca timing exato — dono 15/09).
    import random
    random.seed(7)
    sil = os.path.join(tmp, "sil.wav")
    sil_long = os.path.join(tmp, "sil-long.wav")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi",
                    "-i", "anullsrc=r=44100:cl=mono", "-t", "0.35", sil], check=True)
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi",
                    "-i", "anullsrc=r=44100:cl=mono", "-t", "0.9", sil_long], check=True)
    irgaps = {}
    for dur in (0.25, 0.4, 0.55, 0.7, 0.8):
        p = os.path.join(tmp, "sil-r%.2f.wav" % dur)
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi",
                        "-i", "anullsrc=r=44100:cl=mono", "-t", str(dur), p], check=True)
        irgaps[dur] = p
    mixed = []
    for n, s in enumerate(data["segments"]):
        mixed.append(final[s["i"]])
        if "interjeicao-split" in conf_of.get(s["i"], ""):
            mixed.append(random.choice(list(irgaps.values())))
        elif s["speaker"] == "NARRADOR" and len(s["text"]) > 350:
            mixed.append(sil_long)
        else:
            mixed.append(sil)
    lst = os.path.join(tmp, "list.txt")
    open(lst, "w").write("".join("file '%s'\n" % f for f in mixed))
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
    r.add_argument("--only", default=None, help="deltas: só refaz segs i,... (resto do cache)")
    t = sub.add_parser("tag"); t.add_argument("segments")
    l = sub.add_parser("relabel"); l.add_argument("segments"); l.add_argument("--set", action="append", default=[])
    a = p.parse_args()
    {"parse": cmd_parse, "render": cmd_render, "tag": cmd_tag, "relabel": cmd_relabel}[a.cmd](a)


if __name__ == "__main__":
    main()
