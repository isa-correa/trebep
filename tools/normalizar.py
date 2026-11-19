#!/usr/bin/env python3
"""Limpia el JSON de origen y deja las preguntas con un id estable.
Uso (desde la raíz): python3 tools/normalizar.py tools/origen-trebep-todo.json tools/preguntas.json"""
import json, re, sys

# clave del JSON de origen -> (origen en la app, prefijo del id)
GRUPOS = {"trebep_autoevaluacion": ("autoevaluacion", "au"), "trebep_oficiales": ("oficiales", "of"),
          "trebep_votaciones": ("votaciones", "vo"), "trebep_examenes": ("examenes", "ex"),
          "trebep_ejercicios": ("ejercicios", "ej"), "trebep_supuestos": ("supuestos", "su")}


def limpio(t):
    return re.sub(r"[ \t]+", " ", t.replace("\xa0", " ")).strip()


def parrafos(t):
    return "\n".join(limpio(x) for x in t.split("\n") if x.strip())


def titulo_caso(t):
    """'TREBEP (Mini supuesto 3)' -> 'Mini supuesto 3'."""
    m = re.match(r"^TREBEP \((.*)\)$", t)
    return m.group(1) if m else t


def main(origen, destino):
    d = json.load(open(origen, encoding="utf8"))
    preguntas, casos = [], {}
    for clave, (grupo, abr) in GRUPOS.items():
        for it, t in enumerate(d[clave], 1):
            cid = None
            if grupo == "supuestos":
                cid = f"caso-{it:02d}"
                casos[cid] = {"id": cid, "titulo": titulo_caso(t["test"]), "texto": parrafos(t.get("caso", ""))}
            for q in t["preguntas"]:
                r = {"id": f"{abr}-{it:02d}-{q['n']:03d}", "origen": grupo, "test": t["test"], "n": q["n"],
                     "enunciado": parrafos(q["enunciado"]), "opciones": [limpio(o) for o in q["opciones"]]}
                if cid:
                    r["caso"] = cid
                if re.search(r"pregunta anterior", r["enunciado"], re.I):
                    r["sigueA"] = f"{abr}-{it:02d}-{q['n']-1:03d}"
                preguntas.append(r)
    json.dump({"calendarios": {}, "casos": casos, "preguntas": preguntas},
              open(destino, "w", encoding="utf8"), ensure_ascii=False, indent=1)
    print(len(preguntas), "preguntas,", len(casos), "casos,", sum("caso" in p for p in preguntas), "en casos")


main(sys.argv[1], sys.argv[2])
