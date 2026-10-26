# Dimension Redesign Implementation Plan

> For agentic workers: ejecutar con superpowers:executing-plans en el checkout actual, respetando la preferencia previa por una rama sin otro worktree. Revisión independiente al final según AGENTS.md.

**Goal:** ordenar las vistas y sustituir estilos superpuestos por Dimension.
**Architecture:** rutas y estado actuales en app.js; selección editorial en homepage.js; tema único dimension.css más hojas funcionales existentes. IDs de componentes conservados para librería/agenda/lector.
**Tech Stack:** HTML/CSS/JS estático, Pythonunittest y Playwright de pruebas; sin dependencias de producción nuevas.
**Spec:** ../specs/2026-10-26-dimension-design.md

## Global Constraints
Preferencias locales,221fuentes/8carpetas,45d/5000noticias y agenda90d sin cambios. Sidebar accesible y fuentes ocultas respetadas. Sin cargar tipografías o servicios externos. Modo sistema/elección explícita preservados.

## Review Focus
- Abrir#agenda y recargar conserva ruta y no muestra contenido de Inicio/Noticias.
- Sin fotos, cero artículos, error de agenda e histórico incompleto comunican estado sin huecos o títulos duplicados.
- 320px/zoom/teclado mantienen controles dentro de pantalla y foco visible.
- Nueva publicación no pierde exclusión de trabajadores, scroll ni estado del lector.
- CSS histórico retirado no elimina modales, controles de biblioteca ni soporte sin conexión.

### 1. Estructura y rutas
- [x] Añadir browser_tests/dimension_regressions.py con rutas, selección sin duplicados y tokens/overflow; observar RED.
- [x] Modificar index.html, app.js, homepage.js y exponer resumen de agenda si fuese necesario: destacado único+carrusel, ruta agenda, herramientas en Resumen, actualización secundaria. Preservar firmas y contratos de datos.
- [x] Actualizar pruebas anteriores sólo cuando su expectativa visual fue sustituida explícitamente; preservar validaciones funcionales y de accesibilidad.

### 2. Tema y componentes
- [x] Crear dimension.css con paleta/vidrio/cápsulas, variantes claras y límites móviles. Retirar siete temas históricos del index/SW; conservar CSS funcional.
- [x] Revisar capturas reales, controles de selección, estados leídos, lector/modales y agenda. Corregir problemas de contraste/tamaño con evidencia.

### 3. Verificación e integración
- [x] Python/Node, recorridos Chromium y revisión independiente con correcciones dirigidas; nueva suite en matriz3motores.
- [ ] Actualizar arquitectura/estado/cache/versiones, commit/PR y CI del head exacto.
- [ ] Integrar, verificar Pages y comunicar cambios y límites reales.

## Evidencia de implementación y revisión

Se retiraron del shell siete hojas de temas históricos y su conmutador preview; los archivos permanecen como archivo histórico. Se sustituyeron las dos suites que exigían paletas IAADC/Cosmic por `test_dimension_theme.py`, manteniendo preferencias, accesibilidad y cobertura del shell. Las pruebas funcionales existentes conservan filtros/lector/guardados/cuentas; las expectativas de color/sombras y ubicación de agenda se ajustan al diseño solicitado.

Revisión independiente de la rama: un P2 de cobertura/tendencias en entrada directa a Resumen, corregido con actualización de render y callback asíncrono y caché por artículos elegibles. Regresión de entrada con recarga y cambio de fuentes. Revisión visual adicional: hueco en destacado sin fotografía, icono de carpeta seleccionada con contraste1:1 y banner de fotografía repetido; regresiones RED→GREEN y tarjetas tipográficas sin reservar foto. Selector de tema y firmas preservados. Capturas oscuras/claras en390/1440 y recorridos320–1440. Fuentes locales de sistema, sin peticiones externas de tipografía ni nueva telemetría.

Riesgo→evidencia→control→prueba→responsable→estado: romper rutas/lectura al reorganizar→acoplamientos existentes→IDs/API preservados y rutas separadas→Python/Node/browser más revisión independiente→implementador→cubierto localmente; CI3motores/publicación requieren evidencia del PR. Validación física de lectores de pantalla/teléfonos sigue enIssue31; no se declara realizada.

Verificación local final:251Python y cinco suitesNode aprobadas (14casoslector/13estadopublicación mássidebar/efectos/filtros); Chromium con ocho casosDimension,14contadores,12agenda,9respaldos,4layout,4Concepción,lecturaen4anchos y smokeen7anchos. Regresiones de portada/usabilidad/agenda90d aprobadas. No se ejecutaron Firefox/WebKit locales por restricciones de descarga; la matrizCI del PR los ejecuta. La captura usa titulares controlados de prueba, nunca se publican esos fixtures como noticias.
