#!/usr/bin/env python3
"""Imprime artículos del TREBEP (texto consolidado del BOE, RDL 5/2015).
Uso: python3 -I tools/trabajo/consulta.py 1 2 14   |   consulta.py buscar "palabra"
Necesita boe.html (https://www.boe.es/buscar/act.php?id=BOE-A-2015-11719), que no se sube al repo."""
import html, os, re, sys
s = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "boe.html"), encoding="utf8", errors="ignore").read()
partes = re.split(r'<div[^>]*\bid="((?:a|da|dt|dd|df)\w*)"', s)
arts = {}
for k, cuerpo in zip(partes[1::2], partes[2::2]):
    t = re.sub(r"</(p|h\d|li|blockquote)>", "\n", cuerpo)
    t = html.unescape(re.sub(r"<[^>]+>", "", t))
    t = re.sub(r"\[Bloque[^\]]*\]|Jurisprudencia", "", t)
    arts[k] = "\n".join(x.strip() for x in t.split("\n") if x.strip())
if sys.argv[1] == "buscar":
    q = sys.argv[2].lower()
    for k, v in arts.items():
        if q in v.lower(): print(k, "|", v.split("\n")[0][:100])
else:
    for a in sys.argv[1:]:
        print(arts.get("a" + a) or arts.get(a) or "no existe: " + a, "\n")
