#!/usr/bin/env python3
"""Une preguntas y respuestas razonadas en data/trebep.js. Solo entran las preguntas con respuesta.
Si algo no cuadra, avisa y para. Uso (desde la raíz): python3 tools/construir.py"""
import glob, json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from marcas import marca  # lo que el profesor marca como muy preguntado o poco preguntado

D = json.load(open("tools/preguntas.json", encoding="utf8"))
R = {}
for f in sorted(glob.glob("tools/respuestas/*.json")):
    R.update(json.load(open(f, encoding="utf8")))

BLOQUES = [("ambito", "Ámbito de aplicación (arts. 1 a 7)"), ("clases", "Clases de personal (arts. 8 a 13)"),
           ("derechos", "Derechos y deberes (arts. 14 a 20)"), ("retribuciones", "Retribuciones (arts. 21 a 30)"),
           ("negociacion", "Negociación colectiva (arts. 31 a 38)"),
           ("representacion", "Representación y derecho de reunión (arts. 39 a 46)"),
           ("jornada", "Jornada, permisos y vacaciones (arts. 47 a 51)"),
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
porid = {p["id"]: p for p in D["preguntas"]}
for p in D["preguntas"]:
    if p["id"] in R:
        primera.setdefault(clave(p), p["id"])
for p in D["preguntas"]:
    if p["id"] not in R and clave(p) in primera:
        o = primera[clave(p)]
        r = dict(R[o])
        # Si las opciones vienen en otro orden, se recolocan por su texto.
        pos = {norm(t): i for i, t in enumerate(p["opciones"])}
        m = [pos[norm(t)] for t in porid[o]["opciones"]]
        if m != list(range(len(m))):
            j = [None] * len(m)
            for i, k in enumerate(m):
                j[k] = r["justificaciones"][i]
            r["justificaciones"] = j
            r["correcta"] = m[r["correcta"]]
            if "correctas" in r:
                r["correctas"] = sorted(m[i] for i in r["correctas"])
                r["correcta"] = r["correctas"][0]
        R[p["id"]] = r
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
    q = {**p, **r}
    m = marca(q)
    if m:
        q["marca"] = m
    salida.append(q)
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

# Supuestos va ordenado como «Clases prácticas Bloque IV» del aula virtual: por clase y en el mismo orden.
# Un cuestionario o un ejercicio entra como caso corto (sin enunciado común) con la lista de sus preguntas,
# que siguen saliendo también en Examen. Los supuestos y mini supuestos son los casos de preguntas.json.
CLASES = [
    ("Clase práctica nº 1 · Arts. 1 a 30", [
        ("ex-01", "Cuestionario 1 · Ámbito de aplicación (arts. 1 a 7)"),
        ("ex-02", "Cuestionario 2 · Personal con legislación específica (art. 4)"),
        ("caso-02", "Mini supuesto 1 · Ámbito subjetivo (arts. 1 a 7)"),
        ("ex-03", "Cuestionario 3 · Clases de empleados públicos (arts. 8 a 13)"),
        ("caso-03", "Mini supuesto 2"),
        ("ex-04", "Cuestionario 4 · Derechos de los empleados públicos (arts. 14 y 15)"),
        ("ex-05", "Cuestionario 5 · Carrera profesional (arts. 16 a 20)"),
        ("ex-06", "Cuestionario 6 · Derechos retributivos (arts. 21 a 30)"),
        ("caso-04", "Mini supuesto 3"),
    ]),
    ("Clase práctica nº 2 · Arts. 31 a 51", [
        ("ex-07", "Cuestionario teórico 1 · Artículos 1 a 30"),
        ("ex-08", "Cuestionario teórico 2 · Artículos 31 a 36"),
        ("ej-01", "Ejercicio 1 · Materias objeto de negociación (art. 37)"),
        ("ex-09", "Cuestionario teórico 3 · Pactos y acuerdos (art. 38)"),
        ("ej-02", "Ejercicio 2 · Órganos de representación y crédito horario"),
        ("ex-10", "Cuestionario teórico 4 · Representación y reunión (arts. 39 a 46)"),
        ("caso-05", "Mini supuesto 4 · Permisos del artículo 48.a"),
        ("caso-06", "Mini supuesto 5 · Permisos del artículo 48"),
        ("caso-01", "Supuesto práctico 1 · Permisos y vacaciones (arts. 49 y 50)"),
    ]),
]
porcaso = {c["id"]: c for c in casos}
for i, (_, items) in enumerate(CLASES):
    for j, (src, nombre) in enumerate(items):
        if src in porcaso:
            porcaso[src].update(clase=i, orden=j, titulo=nombre)
            continue
        ids = sorted(p["id"] for p in salida if p["id"].startswith(src + "-"))
        if ids:
            casos.append({"id": "cl-" + src, "titulo": nombre, "texto": "", "corto": True, "ids": ids, "clase": i, "orden": j})
t = {"id": "trebep", "nombre": "TREBEP, Estatuto Básico del Empleado Público", "bloques": [{"id": a, "nombre": b} for a, b in BLOQUES],
     "calendarios": {}, "clases": [n for n, _ in CLASES], "casos": casos, "preguntas": salida}
with open("data/trebep.js", "w", encoding="utf8") as f:
    f.write("window.BANCO = window.BANCO || [];\nwindow.BANCO.push(" + json.dumps(t, ensure_ascii=False, separators=(",", ":")) + ");\n")
print(len(salida), "preguntas con respuesta de", len(D["preguntas"]), "·", len(ok), "supuestos completos ·",
      len(casos) - len(ok), "cuestionarios y ejercicios en Supuestos · data/trebep.js")
