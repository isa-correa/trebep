#!/usr/bin/env python3
"""Une preguntas y respuestas razonadas en data/trebep.js. Solo entran las preguntas con respuesta.
Si algo no cuadra, avisa y para. Uso (desde la raíz): python3 tools/construir.py"""
import glob, json, re, sys

D = json.load(open("tools/preguntas.json", encoding="utf8"))
R = {}
for f in sorted(glob.glob("tools/respuestas/*.json")):
    R.update(json.load(open(f, encoding="utf8")))

BLOQUES = [("ambito", "Ámbito de aplicación (arts. 1 a 7)"), ("clases", "Clases de personal (arts. 8 a 13)"),
           ("derechos", "Derechos y deberes (arts. 14 a 20)"), ("retribuciones", "Retribuciones, jornada y permisos (arts. 21 a 30)"),
           ("negociacion", "Negociación colectiva y representación (arts. 31 a 38)"),
           ("deberes", "Deberes y código de conducta (arts. 52 a 54)"),
           ("acceso", "Acceso al empleo público (arts. 55 a 62)"),
           ("adquisicion", "Adquisición y pérdida de la relación de servicio (arts. 63 a 68)"),
           ("provision", "Ordenación de la actividad profesional y provisión (arts. 69 a 84)"),
           ("situaciones", "Situaciones administrativas (arts. 85 a 92)"),
           ("disciplina", "Régimen disciplinario (arts. 93 a 98)"),
           ("otros", "Otras normas relacionadas")]
validos = {b for b, _ in BLOQUES}
norm = lambda x: re.sub(r"\W+", "", x.lower())
clave = lambda p: norm(p["enunciado"]) + "|" + "|".join(sorted(map(norm, p["opciones"])))
# Una pregunta repetida en otro test hereda la respuesta de la primera que se respondió.
primera = {}
for p in D["preguntas"]:
    if p["id"] in R:
        primera.setdefault(clave(p), p["id"])
for p in D["preguntas"]:
    if p["id"] not in R and clave(p) in primera:
        R[p["id"]] = R[primera[clave(p)]]
err, salida = [], []
for p in D["preguntas"]:
    r = R.get(p["id"])
    if not r:
        continue
    if len(r["justificaciones"]) != len(p["opciones"]):
        err.append(f"{p['id']}: {len(r['justificaciones'])} justificaciones para {len(p['opciones'])} opciones")
    if not 0 <= r["correcta"] < len(p["opciones"]):
        err.append(f"{p['id']}: correcta fuera de rango")
    if "correctas" in r:
        c = r["correctas"]
        if not (isinstance(c, list) and len(c) >= 2 and c == sorted(set(c)) and all(isinstance(i, int) and 0 <= i < len(p["opciones"]) for i in c) and r["correcta"] == c[0]):
            err.append(f"{p['id']}: correctas no válidas")
    if r["bloque"] not in validos:
        err.append(f"{p['id']}: bloque {r['bloque']}")
    if re.search("[—–]", json.dumps(r, ensure_ascii=False)):
        err.append(f"{p['id']}: lleva raya o semirraya")
    salida.append({**p, **r})
# La misma pregunta en dos tests: misma respuesta, y en los exámenes solo sale una.
grupos = {}
for p in salida:
    grupos.setdefault(clave(p), []).append(p)
for g in grupos.values():
    if len(g) > 1:
        if len({norm(p["opciones"][p["correcta"]]) for p in g}) > 1:
            err.append("respuesta distinta en la misma pregunta: " + ", ".join(p["id"] for p in g))
        for p in g:
            p["dup"] = g[0]["id"]
fantasma = set(R) - {p["id"] for p in D["preguntas"]}
if fantasma:
    err.append(f"ids desconocidos: {sorted(fantasma)}")
if err:
    sys.exit("\n".join(err))

# Un supuesto solo sale cuando todas sus preguntas tienen respuesta.
total, hechas = {}, {}
for p in D["preguntas"]:
    if "caso" in p:
        total[p["caso"]] = total.get(p["caso"], 0) + 1
for p in salida:
    if "caso" in p:
        hechas[p["caso"]] = hechas.get(p["caso"], 0) + 1
casos = [c for k, c in D["casos"].items() if hechas.get(k) == total.get(k)]
ok = {c["id"] for c in casos}
salida = [p for p in salida if "caso" not in p or p["caso"] in ok]
t = {"id": "trebep", "nombre": "TREBEP, Estatuto Básico del Empleado Público", "bloques": [{"id": a, "nombre": b} for a, b in BLOQUES],
     "calendarios": {}, "casos": casos, "preguntas": salida}
with open("data/trebep.js", "w", encoding="utf8") as f:
    f.write("window.BANCO = window.BANCO || [];\nwindow.BANCO.push(" + json.dumps(t, ensure_ascii=False, separators=(",", ":")) + ");\n")
print(len(salida), "preguntas con respuesta de", len(D["preguntas"]), "·", len(casos), "supuestos completos · data/trebep.js")
