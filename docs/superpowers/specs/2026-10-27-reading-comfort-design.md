# Identidad legible y lectura cómoda

El propietario pide reemplazar un logo que no entiende y mejorar UI, UX y efectos para leer durante más tiempo en claro y oscuro. Continúa la autorización para ejecutar la recomendación y publicar. Se conserva la aplicación estática, sus cuatro destinos y su marca pequeña de24px: sin otro banner ni un nuevo tema superpuesto.

## Enfoque

Se elige una marca RSS convencional: dos arcos blancos y un punto ámbar sobre violeta, sin monograma, volumen ni detalles diminutos. SVG ligero para cabecera/favicon y PNG original generado para instalación; una única identidad. Alternativas descartadas: otra R abstracta seguiría siendo ambigua, un logotipo grande volvería a ocupar espacio y eliminar el color contradiría preferencias anteriores.

La paleta conserva violeta, azul, ámbar y ocho categorías. El claro usa papel cálido y tarjetas marfil; el oscuro, pizarra y texto blanco suavizado. Se busca contraste de texto normal >=4.5:1, controles/foco distinguibles y texto principal >=7:1, sin afirmar prevención médica de fatiga. Las superficies de lectura son uniformes; el relieve y los bordes de color siguen presentes con menos resplandor. Hover/foco usan transiciones breves de color/sombra, sin desplazar tarjetas ni rotar iconos. Se respetan reduced-motion y forced-colors.

## Lectura y controles

- Base16px; extractos15px/1.7, metadatos13px, titulares18px/1.45; cobertura16px/1.55. Destacado24–30px/1.32. Lector18px/1.8 con columna <=68ch.
- El ajuste existente Texto grande debe ampliar también Inicio, cobertura, Agenda y Resumen, además de Noticias/lector; se conserva su persistencia/respaldo y la elección del usuario. Sin nueva preferencia ni cuenta.
- Columnas automáticas por defecto para visitas sin selección previa y al restablecer. Tarjetas auto con mínimo280px limitado al espacio disponible,320px con texto grande. Las selecciones explícitas2–6 se conservan y mantienen su adaptación móvil.
- Acciones principales/táctiles >=44px. Entradas de texto y selects móviles >=16px, sin desactivar zoom. Cabecera de una fila, buscador desplegable móvil y logo24px se conservan.
- Fuente, fecha, estados leído/guardado, menús, filtros, comparación, mapa opcional y regreso del lector siguen operativos. Las noticias leídas mantienen contraste y no se atenúa toda la tarjeta.

## Alcance y evidencia

Solo presentación, valores de diseño existentes, iconos de instalación y documentación. Sin recolector, fuentes, red adicional, dependencias, contenido de terceros ni datos nuevos. La generación de marca usa formas genéricas sin material privado. Preferencias locales existentes, medios/atribución y jurisdicciones no cambian. No se certifica comodidad individual ni pruebas físicas de iPhone (Issue31).

Verificación con fixtures: preferencias por defecto/guardadas/restablecidas, tamaño grande entre rutas y lector, contraste de textos/estados en ambos modos, focos/controles y movimiento, formularios móviles, tamaños320–1440, capturas, Python/Node y navegadores de CI. Una revisión independiente final, PR y publicación verificada.

La revisión independiente encontró dos defectos heredados dentro del alcance: la pista0px al ocultar el lateral y el outline recortado del titular en colores forzados. Se corrigen con pista única al colapsar y anillo externo en la tarjeta. Sus regresiones comprueban recarga/cambio de viewport y captura con foco.
