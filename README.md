# Test de oposición C1 AGE: TREBEP

Exámenes tipo test del Estatuto Básico del Empleado Público (TREBEP, Bloque IV), con las respuestas explicadas. Misma app que [ley-39](https://github.com/isa-correa/ley-39): Examen y Supuestos, estadísticas y repaso de falladas, todo guardado en el navegador (claves `trebep-*`).

Se publica tal cual en GitHub Pages: no necesita compilar nada. Solo hay que subir `index.html`, `css`, `js` y `data`.

## Estado

- Las **890 preguntas** del aula virtual están extraídas en `tools/preguntas.json` (con id estable): 16 tests de autoevaluación (275), 10 oficiales (195), 5 de votaciones (162), 10 exámenes (161), 2 ejercicios (27) y 6 supuestos (70).
- Las respuestas razonadas se van añadiendo en `tools/respuestas/*.json`. Solo entran en la web las preguntas con respuesta, y un supuesto solo sale cuando tiene todas las suyas.

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

Autoevaluación, Oficiales, Votaciones, Exámenes y Ejercicios salen en Examen. Los supuestos (un caso común y sus preguntas) salen en Supuestos, en dos grupos: Supuestos prácticos y Mini supuestos.

## Movimiento

Las animaciones van en `js/movimiento.js`, con GSAP 3.13 y su plugin Flip copiados en `js/vendor/` (sin CDN). Con "reducir movimiento" activado no se anima nada.
