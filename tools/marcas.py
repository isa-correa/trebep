"""Lo que el profesor marca en sus apuntes como estrella, clave de examen o poco preguntado.

Todavía no hay marcas: se añadirán cuando lleguen los apuntes. Mientras MARCAS esté vacío, ninguna pregunta
lleva marca y el filtro «Solo estrella y clave de examen» sale a cero.

Cada marca se ata a artículos del TREBEP. Una pregunta recibe la marca si su precepto cita ese artículo
(o ese apartado: "10.4" atrapa "art. 10.4" y "art. 10.4.a)", pero no "art. 10.5").
Si a una pregunta le tocan varias, gana la de más nivel: estrella, luego clave, luego poco.
Entre dos del mismo nivel gana la que va antes en la lista: por eso las concretas van delante de las generales.

Para añadir una marca: una línea más en MARCAS con (nivel, artículos, lo que dice el profesor).
Los artículos van separados por comas; "75-83" es un rango de artículos enteros.
Después, volver a ejecutar python3 tools/construir.py.
"""
import re

NIVELES = {"estrella": 3, "clave": 2, "poco": 1}

# ("estrella" | "clave" | "poco", "artículos", "lo que dice el profesor")
MARCAS = [
]


def _specs(texto):
    """'10.4, 10.5' -> [('10', '4'), ('10', '5')]; '75-83' -> un spec por artículo."""
    res = []
    for parte in texto.split(","):
        parte = parte.strip()
        m = re.fullmatch(r"(\d+)-(\d+)", parte)
        if m:
            res += [(str(a), "") for a in range(int(m.group(1)), int(m.group(2)) + 1)]
            continue
        m = re.fullmatch(r"(\d+)((?:\.\w+)*)", parte)
        if m:
            res.append((m.group(1), m.group(2).lstrip(".")))
    return res


def citas(precepto):
    """Artículos que cita un precepto: 'Art. 10.4 del TREBEP' -> {('10', '4')}."""
    res = set()
    for trozo in re.split(r";|\s+y\s+(?=arts?\b)|,\s*(?=arts?\b)", precepto, flags=re.I):
        m = re.search(r"\barts?\b\.?\s*(.*)", trozo, re.I)
        if not m:
            continue
        nums = re.split(r"\s(?:de la|del|de)\s|\bTREBEP\b", m.group(1))[0]
        for n in re.finditer(r"(\d+)((?:\.\w+)*)\)?(?:\s*(?:a|-)\s*(\d+))?", nums):
            a = int(n.group(1))
            if n.group(3) and not n.group(2):
                b = int(n.group(3))
                if b - a <= 20:
                    res.update((str(x), "") for x in range(a, b + 1))
                continue
            res.add((str(a), n.group(2).lstrip(".")))
    return res


def _toca(cita, spec):
    art, ap = cita
    s_art, s_ap = spec
    if art != s_art:
        return False
    return not s_ap or ap == s_ap or ap.startswith(s_ap + ".")


def marca(p):
    """Devuelve {'nivel': ..., 'nota': ...} o None."""
    if not MARCAS:
        return None
    cs = citas(p.get("precepto") or "")
    mejor = None
    for nivel, arts, nota in MARCAS:
        if any(_toca(c, s) for c in cs for s in _specs(arts)):
            if not mejor or NIVELES[nivel] > NIVELES[mejor[0]]:
                mejor = (nivel, nota)
    return {"nivel": mejor[0], "nota": mejor[1]} if mejor else None
