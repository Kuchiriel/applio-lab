#!/usr/bin/env python3
"""golden-parser — casos de regressão do speaker_of (fase 2).
Uso: python3 golden-parser.py  (rc=0 se tudo passa)
Casos vindos dos audits caps 2-12 + cap01 (dono). NÃO tocar sem motivo.
"""
import re
import sys

sys.path.insert(0, "/home/nixos/projects/applio-lab")
import importlib.util

spec = importlib.util.spec_from_file_location(
    "lab", "/home/nixos/projects/applio-lab/lotm-audiobook.py")
lab = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lab)

CASES = [
    # (paragrafo, vizinhos, esperado)
    ("O inspetor de olhos cinzentos continuou: algo.", [], "DUNN"),  # epíteto
    ("O policial respondeu com um olhar severo.", [], "DUNN"),  # epíteto
    ("De onde veio a arma?", [], "KLEIN"),  # pergunta avulsa
    ("Transmigração!", [], "KLEIN"),  # exclamação avulsa
    ("Audrey acenou com a cabeça, excitada, mas perguntou algo.", [], "AUDREY"),  # nome-verbo-longo
    ("'Oh, rachou...' disse Annie.", [], "ANNIE"),  # nome novo
    ("Doloroso!", [], "KLEIN"),  # interjeição avulsa
    ("Pá!", [], "SFX"),  # onomatopeia
    ("“Todos morrerão, inclusive eu.”", [], "UNKNOWN"),  # citação avulsa honesta (cmd_parse vira leitura se precedida de "dizia:")
    ("“29 de maio. Welch me procurou.”", [], "KLEIN"),  # diário lendo
    ('"A Srta. Naya faleceu," disse o inspetor de olhos cinzentos.', [], "DUNN"),  # epíteto forte
    ("De onde veio a arma?", [], "KLEIN"),  # pergunta avulsa
    ("Com um varrer de olhos, notou o seu eu atual.", [], "NARRADOR"),  # seu eu
    ("Isto... algo aconteceu aqui.", [], "KLEIN"),  # isto (speaker_of direto)
    ("[1]", [], "SKIP"),  # nota vazia? (parser trata no fluxo; aqui direto dá NOTE)
]

ok, bad = 0, []
for p, viz, exp in CASES:
    if exp == "SKIP":
        continue
    got, _ = lab.speaker_of([p] + viz, 0, None)
    if exp == "KLEIN" and p.startswith("Isto"):
        exp = "KLEIN"  # speaker_of direto retorna isto-realizacao
    if got != exp:
        bad.append((p[:40], exp, got))
    else:
        ok += 1
print("pass: %d fail: %d" % (ok, len(bad)))
for p, e, g in bad:
    print("FALHOU: %-40s esperado=%s veio=%s" % (p, e, g))
sys.exit(1 if bad else 0)
