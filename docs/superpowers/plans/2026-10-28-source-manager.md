# Gestión de fuentes — Implementation Plan

> Método nativo: superpowers:executing-plans. Mismo checkout y rama `feat/gestion-fuentes-configuracion`; autorización persistente para ejecutar recomendaciones/publicar. Una revisión independiente final.

**Goal:** URLs visibles y una gestión de fuentes/carpetas/OPML coherente.
**Architecture:** `source-tools.js` contiene utilidades puras/OPML; `app.js` mantiene la base de configuración y `library.js` conecta su organización personal existente. Sin servicios/dependencias.
**Tech Stack:** JS estático, DOMParser, localStorage, Node/unittest/Playwright existentes.
**Spec:** docs/superpowers/specs/2026-10-28-source-manager-design.md.

## Global Constraints
- Base 7e0573428c5a37134c170beda050c0fddc3fce0f, 311 suscripciones y sus IDs/URLs intactos.
- Sin workflows, dependencias, recopilación remota, cuentas ni datos nuevos publicados.
- OPML importado solo activa/reorganiza fuentes conocidas, previa/confirmación/cancelación; desconocidas se informan.
- Preservar guardadas/leídas/etiquetas/agenda, claro/oscuro, teclado y 320 px.
- Ledger/evidencia: /workspace/scratch/source-manager/progress.md; no red en pruebas.

## Review Focus
- Nombres iguales y fuente en múltiples carpetas: siempre usar ID, exportar todas las pertenencias sin confundir categorías originales.
- Google RSS con parámetros diferentes, URLs inseguras, XML malformado/DTD, duplicados y fuentes desconocidas: coincidencia conservadora y cero red/efectos previos a aplicar.
- Carpeta >160 miembros, categorías renombradas y límites OPML: recarga/exportación/importación sin pérdida silenciosa.
- Fallo de localStorage/importación y fuente nueva desde publicación pendiente: no cambios parciales ni totales/estados inventados.
- Filtros combinados, enlaces/copiar, foco/teclado/texto grande y pantallas 320 px en ambos temas.

### Task 1: Utilidades de catálogo y portabilidad
**Files:** web/source-tools.js, tests/test_source_tools.cjs, tests/test_source_management.py.
**Interfaces:** `RadarSourceTools` expone normalización segura de URL, clasificación/filtros de catálogo, CSV, OPML con carpetas y lectura/emparejamiento conservador de OPML. UI consume los mismos IDs que sources.json.
- [ ] Escribir y observar RED en Node para URLs, filtros, estado desconocido, duplicados, CSV y OPML personalizado; wrapper Python ejecuta Node en CI actual.
- [ ] Implementar mínimo y observar GREEN; parser XML se verifica en navegador real en Task 2.

### Task 2: Configuración coherente y gestor de fuentes
**Files:** web/app.js, web/library.js, web/library.css, web/index.html, web/features.js, web/sw.js, browser_tests/dimension_regressions.py.
**Interfaces:** filas con `data-source-id`, identidad por ID, UI usa `RadarSourceTools`; biblioteca aporta carpetas actuales/acciones/exportación e importación previsualizada.
- [ ] Pruebas navegador RED de URL/búsqueda/filtros; toggle/categoría; movimiento/OPML exportado; importación/cancelación/seguridad/almacenamiento; >160/reinicio ligero.
- [ ] Implementar listado legible con enlaces/estado/filtros, corregir conteos y organización, exportación CSV/OPML e importación con informe y previa; integrar assets sin duplicar renderizadores.
- [ ] Comprobar ambos temas/320 px, foco/enlaces/copiar, preferencias persistidas, límites e importación sin cambios parciales. GREEN en pruebas pertinentes y batería completa.
- [ ] Documentar resultados/alcance Feedly/limitaciones y versionar shell/caché; revisar diff y commit.

### Task 3: Revisión e integración
- [ ] Una revisión independiente final del diff contra base; resolver hallazgos importantes con RED→GREEN y suite completa, sin segunda revisión.
- [ ] PR/CI exacta, integrar/publicar con autorización persistente; comprobar assets/datos web y árbol local limpio/equivalente.
- [ ] Informar funciones reales y límites (importación de desconocidas necesita catálogo público; sin sincronización).
