# Test de oposición C1 AGE: TREBEP

Exámenes tipo test del Estatuto Básico del Empleado Público (TREBEP, Bloque IV), con las respuestas explicadas. Misma app que [ley-39](https://github.com/isa-correa/ley-39): Examen y Supuestos, estadísticas y repaso de falladas, todo guardado en el navegador (claves `trebep-*`).

Se publica tal cual en GitHub Pages: no necesita compilar nada. Solo hay que subir `index.html`, `css`, `js` y `data`.

## Estado

- Las **890 preguntas** del aula virtual están extraídas en `tools/preguntas.json` (con id estable): 16 tests de autoevaluación (275), 10 oficiales (195), 5 de votaciones (162), 10 exámenes (161), 2 ejercicios (27) y 6 supuestos (70).
- Las respuestas razonadas se van añadiendo en `tools/respuestas/*.json`. Solo entran en la web las preguntas con respuesta, y un supuesto solo sale cuando tiene todas las suyas.
- Los apuntes del profesor (`TREBEP_apuntes_fuente.html`) llegan a la clase 1, arts. 1 a 30. Lo que marca como estrella o clave de examen está en `tools/marcas.py`, y sus explicaciones y ejemplos de clase van en el campo `ojo` de cada pregunta, empezando por «En clase:». Falta desde el art. 31.

## Flujo

1. `python3 tools/normalizar.py tools/origen-trebep-todo.json tools/preguntas.json` limpia el JSON de origen y asigna ids (`au-01-001`: origen, test, pregunta).
2. Las respuestas van en `tools/respuestas/lote-NN.json`, por id:
   ```json
   {"au-01-001": {"bloque": "ambito", "precepto": "Art. 1.1 del TREBEP", "correcta": 1,
                  "justificaciones": ["No. ...", "Es esta. ...", "No. ...", "No. ..."]}}
   ```
   `correcta` es el índice desde 0; `justificaciones` lleva una por opción. Opcionales: `ojo`, `revisar` y `correctas` (respuesta múltiple, solo en supuestos). Una pregunta repetida en otro test hereda la respuesta de la primera.
3. `python3 tools/construir.py` valida y genera `data/trebep.js`. Si algo no cuadra, avisa y para. Sube el número `?v=` en `index.html` cuando cambien los datos.

Bloques: `ambito`, `clases`, `derechos`, `retribuciones`, `negociacion`, `deberes`, `acceso`, `adquisicion`, `provision`, `situaciones`, `disciplina`, `otros` (nombres en `tools/construir.py`).

## Orígenes

Autoevaluación, Oficiales, Votaciones, Exámenes y Ejercicios salen en Examen. Supuestos va ordenado como «Clases prácticas Bloque IV» del aula virtual: un desplegable por clase práctica con sus cuestionarios (los Exámenes 1 a 10), ejercicios, mini supuestos y supuestos, en el mismo orden. El orden y los títulos están en `CLASES`, en `tools/construir.py`: cuando haya una clase nueva, se añade ahí. Los cuestionarios y ejercicios siguen saliendo también en Examen.

## Apuntes (tools/volumen.py)

La pestaña Apuntes lleva el volumen «TREBEP · Apuntes» (23 hojas A4 apaisadas, clase 1, arts. 1 a 30): una entrada con el método del supuesto y los señuelos, cinco bloques con su teoría y su práctica (ámbito, clases de empleados, derechos, carrera y retribuciones) y un cierre con cifras y plazos, quién decide y glosario. Se importa con:

```bash
python3 tools/construir.py                                  # primero, para que data/trebep.js tenga las preguntas
python3 -I tools/volumen.py /ruta/a/2_Apuntes_por_bloques   # PDF -> img/esquemas/*.webp y data/esquemas.js
```

Hace falta PyMuPDF y Pillow. Cada hoja declara en `HOJAS` qué artículos cubre, y cada pregunta recibe hasta 5 hojas de teoría cuyos artículos coinciden con los de su precepto (las más concretas primero), que salen en el botón «Consultar apuntes». Las hojas de entrada, práctica y cierre salen en Apuntes pero no cuelgan de ninguna pregunta. Para añadir una hoja nueva: ponla en la carpeta con su número, añade una línea a `HOJAS` (y a `BLOQUES` si hay bloque nuevo) y vuelve a ejecutar. Sube el número `?v=` de `esquemas.js` en `index.html` para que el móvil no use la versión guardada.

## Movimiento

Las animaciones van en `js/movimiento.js`, con GSAP 3.13 y su plugin Flip copiados en `js/vendor/` (sin CDN). Con "reducir movimiento" activado no se anima nada.
