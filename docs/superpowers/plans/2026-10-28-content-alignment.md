# Corrección de alineación de página

> Ejecución nativa (`superpowers:executing-plans`), una rama/PR `fix/alineacion-contenido`, revisión independiente final. El usuario solicita corregir la desalineación de la captura; mantiene su autorización para ejecutar y publicar correcciones.

**Goal / spec:** cabecera, contenido y contenido del pie comparten ambos bordes en las cuatro rutas, con lateral visible/oculto y anchos personalizados; sin desbordamiento de320–2560px. Mantener tema, tamaños de lectura, estructura, fuentes y preferencias.
**Architecture:** conservar `.page`/`.main` y su ancho de lectura máximo1200px; dos tokens Dimension para ancho y margen interior; cabecera centrada con el mismo ancho útil, pie con el mismo margen. No cambios JS ni datos.
**Files:** web/dimension.css (causa), web/index.html y web/sw.js (versiones), browser_tests/dimension_regressions.py (geometría real).

## Causa observada
En1842px/lateral310px, cabecera x334/ancho1144 frente a Inicio x500/ancho1152. La regla final `margin:10px 24px 0` reemplaza `margin-inline:auto`; el máximo1144 no coincide con1200 menos48px del contenido. El pie usa28px, distinto de24px. La validación previa de no desbordamiento no detectaba estas diferencias.

## Criterios y revisión
- Comparar ambos bordes reales de cabecera/contenedor de ruta y del área interior del pie, tolerancia1px.
- Probar320/768/950/951/1200/1440/1842/2560px, lateral abierto240/310/480 y oculto en escritorio, cuatro rutas y temas claro/oscuro.
- No cambiar ancho completo de `.page`, navegación, archivo, catálogo311/8, servicios, dependencias ni workflows. Corrección visual sin datos nuevos ni cambios en atribución/privacidad/licencias.

### Task 1: Reproducir, corregir y verificar
- [x] Prueba de geometría RED para el caso de la captura y matriz de adaptación.
- [x] Tokens y reglas coherentes en la hoja activa, sin envolver/mover nodos ni añadir otra capa de overrides; CSS1.6.1/cache55.
- [x] GREEN en geometría, suite Dimension, Python/Node y responsive; capturas antes/después inspeccionadas.
- [ ] Revisión independiente única, corregir hallazgos importantes con RED→GREEN si aparecen.
- [ ] PR/CI exacta y publicación autorizada; verificar versión pública y árbol limpio/equivalente. Evidencia y estado final en PR/Actions/ledger.
