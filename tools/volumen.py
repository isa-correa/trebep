#!/usr/bin/env python3
"""Importa el volumen «TREBEP · Apuntes» a la pestaña Apuntes y a los botones «Consultar apuntes».

Uso (desde la raíz del repo):  python3 -I tools/volumen.py <carpeta con los PDF de las hojas>

La carpeta es 2_Apuntes_por_bloques: un PDF por hoja, con nombre NN_titulo.pdf (NN = número de hoja).
Antes hay que haber ejecutado tools/construir.py, porque la relación pregunta -> apuntes se calcula
con las preguntas que ya están en data/trebep.js.

Hace tres cosas:
  1. Convierte cada hoja a WebP (2400 px de ancho) en img/esquemas/<id>-1.webp.
  2. Escribe data/esquemas.js con tres cosas:
       window.ESQUEMAS  el catálogo (título, imagen, artículos que cubre)
       window.APUNTES   los bloques de la pestaña Apuntes, con su teoría y su práctica
       window.ESQ_PREG  pregunta -> hasta 5 hojas, las que cubren los artículos de su precepto
  3. Las hojas de entrada, cierre y práctica salen en Apuntes pero no cuelgan de ninguna pregunta.

Para añadir una hoja nueva: ponla en la carpeta, añade una línea a HOJAS y vuelve a ejecutar.
Sube el número ?v= de esquemas.js en index.html para que el móvil no use la versión guardada.
"""
import glob, json, os, re, sys

import fitz  # PyMuPDF
from PIL import Image

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, "tools"))
from marcas import citas  # artículos que cita un precepto

ANCHO = 2400          # píxeles de ancho: suficiente para acercar el zoom sin ver borroso
MAX_POR_PREGUNTA = 5  # hojas como máximo en el botón de una pregunta
RANGO_MAX = 40        # un precepto con un rango más ancho no apunta a nada concreto

# número de hoja -> (id, título, artículos que cubre, tipo)
# tipo: "entrada" y "cierre" salen en su bloque; "teoria" y "practica" van en su bloque de temario.
# Los artículos se escriben como "10", "14-15" o varios separados por comas.
HOJAS = {
    1: ("portada", "Portada e índice", "", "entrada"),
    2: ("metodo", "Método del supuesto práctico", "", "entrada"),
    3: ("senuelos", "Los señuelos que más se repiten", "", "entrada"),
    4: ("t1-aplica", "A quién se aplica el TREBEP", "2-5", "teoria"),
    5: ("t1-art4", "Las ocho letras del art. 4", "4", "teoria"),
    6: ("t1-practica", "Práctica y trampas del ámbito", "1-7", "practica"),
    7: ("t2-clases", "Las cuatro clases de empleados", "8,9,12,13", "teoria"),
    8: ("t2-interinos", "Los interinos del art. 10", "10", "teoria"),
    9: ("t2-laboral", "Laboral, eventual y directivo", "11-13", "teoria"),
    10: ("t2-practica", "Práctica: qué empleado es y cómo cesa", "8-13", "practica"),
    11: ("t3-14-15", "Art. 14 frente al art. 15", "14,15", "teoria"),
    12: ("t3-practica", "Práctica: ¿art. 14 o art. 15?", "14,15", "practica"),
    13: ("t4-escalera", "La escalera de la carrera profesional", "16", "teoria"),
    14: ("t4-promocion", "Promoción interna y evaluación del desempeño", "17-20", "teoria"),
    15: ("t4-practica", "Práctica: qué modalidad de carrera es", "16-20", "practica"),
    16: ("t5-estructura", "La estructura retributiva", "21,22", "teoria"),
    17: ("t5-basicas", "Básicas frente a complementarias", "23,24", "teoria"),
    18: ("t5-otros", "Quién cobra qué: interinos, prácticas, laboral y diferidas", "25-27,29", "teoria"),
    19: ("t5-indemnizaciones", "Indemnizaciones y deducción de retribuciones", "28,30", "teoria"),
    20: ("t5-practica", "Práctica: qué cobra y qué se le descuenta", "21-30", "practica"),
    21: ("cifras", "Cifras y plazos", "", "cierre"),
    22: ("decide", "Quién decide y qué no se aplica", "", "cierre"),
    23: ("glosario", "Glosario de términos de examen", "", "cierre"),
}

# bloques de la pestaña Apuntes: (id, etiqueta, nombre, descripción, hojas)
BLOQUES = [
    ("0", "00", "Entrada", "Portada, método del supuesto práctico y los señuelos que más se repiten. Para empezar.", [1, 2, 3]),
    ("1", "01", "Ámbito de aplicación", "Arts. 1 a 7. A quién se aplica el Estatuto y qué personal tiene legislación propia.", [4, 5, 6]),
    ("2", "02", "Clases de empleados públicos", "Arts. 8 a 13. Las cuatro clases de empleados, interinos incluidos.", [7, 8, 9, 10]),
    ("3", "03", "Derechos de los empleados", "Arts. 14 y 15. Derechos individuales y derechos individuales ejercidos colectivamente.", [11, 12]),
    ("4", "04", "Carrera profesional", "Arts. 16 a 20. Carrera, promoción interna y evaluación del desempeño.", [13, 14, 15]),
    ("5", "05", "Retribuciones", "Arts. 21 a 30. Estructura retributiva, sueldos, indemnizaciones y deducciones.", [16, 17, 18, 19, 20]),
    ("6", "06", "Cierre", "Cifras y plazos, quién decide y glosario. Para repasar.", [21, 22, 23]),
]


def articulos(spec):
    """'8-9,12-13' -> {8, 9, 12, 13}"""
    res = set()
    for t in spec.split(","):
        t = t.strip()
        if not t:
            continue
        a, _, b = t.partition("-")
        res.update(range(int(a), int(b or a) + 1))
    return res


def convertir(pdf, destino):
    doc = fitz.open(pdf)
    pag = doc[0]
    z = ANCHO / pag.rect.width
    pix = pag.get_pixmap(matrix=fitz.Matrix(z, z), alpha=False)
    im = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    im.save(destino, "WEBP", quality=85, method=6)
    return im.width, im.height


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    carpeta = sys.argv[1]
    salida = os.path.join(RAIZ, "img", "esquemas")
    os.makedirs(salida, exist_ok=True)

    catalogo = {}
    for n, (eid, titulo, arts, tipo) in HOJAS.items():
        pdfs = glob.glob(os.path.join(carpeta, "%02d_*.pdf" % n))
        if len(pdfs) != 1:
            sys.exit("Falta la hoja %02d (o hay más de una) en %s" % (n, carpeta))
        w, h = convertir(pdfs[0], os.path.join(salida, eid + "-1.webp"))
        catalogo[eid] = {"titulo": titulo, "paginas": [{"src": "img/esquemas/%s-1.webp" % eid, "w": w, "h": h}], "a": arts}

    apuntes = []
    for bid, etq, nombre, desc, hojas in BLOQUES:
        grupos = []
        teoria = [HOJAS[n][0] for n in hojas if HOJAS[n][3] in ("teoria", "entrada", "cierre")]
        practica = [HOJAS[n][0] for n in hojas if HOJAS[n][3] == "practica"]
        if practica:
            grupos = [{"nombre": "Teoría", "ids": teoria}, {"nombre": "Práctica", "ids": practica}]
        else:
            grupos = [{"nombre": None, "ids": teoria}]
        apuntes.append({"id": bid, "etq": etq, "nombre": nombre, "desc": desc, "grupos": grupos})

    # pregunta -> hojas que cubren los artículos de su precepto (primero las más concretas)
    s = open(os.path.join(RAIZ, "data", "trebep.js"), encoding="utf-8").read()
    preguntas = json.loads(s[s.index('{"id"'):s.rindex("}") + 1])["preguntas"]
    candidatas = [(len(articulos(a)), n, eid) for n, (eid, t, a, tipo) in HOJAS.items() if tipo == "teoria" and a]
    por_pregunta = {}
    for p in preguntas:
        cit = {int(a) for a, _ in citas(p.get("precepto", ""))}
        if not cit or max(cit) - min(cit) > RANGO_MAX:
            continue
        ok = sorted((n_arts, n, eid) for n_arts, n, eid in candidatas if articulos(catalogo[eid]["a"]) & cit)
        if ok:
            por_pregunta[p["id"]] = [eid for _, _, eid in ok[:MAX_POR_PREGUNTA]]

    with open(os.path.join(RAIZ, "data", "esquemas.js"), "w", encoding="utf-8") as f:
        f.write("window.ESQUEMAS = " + json.dumps(catalogo, ensure_ascii=False) + ";\n")
        f.write("window.APUNTES = " + json.dumps(apuntes, ensure_ascii=False) + ";\n")
        f.write("window.ESQ_PREG = " + json.dumps(por_pregunta, ensure_ascii=False) + ";\n")
    print("hojas:", len(catalogo), "· preguntas con apuntes:", len(por_pregunta), "de", len(preguntas))


if __name__ == "__main__":
    main()
