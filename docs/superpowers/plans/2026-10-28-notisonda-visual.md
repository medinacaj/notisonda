# Completar identidad visual de Notisonda — PR117

> Ejecución nativa sobre la rama existente `branding/notisonda-visual`, sin reemplazar el diseño aportado por el usuario. Base estable bd356ee83e63f259f703b11d1bff66ea568cd05b; PR117 originalce81c431e228acee45358e411e4ea2bc6fd88eda, base actual integrada sin conflicto.

**Goal/spec:** integrar los SVG de Notisonda y publicarlos con iconos PNG para instalación/Apple y tarjeta social PNG1200×630. Mantener marca24px, alineación, temas, fuentes311/8, preferencias/respaldos y GUID existentes. Completar textos de identidad en exportaciones/ayuda/compartir sin cambiar esquemas técnicos `radar-*`.
**Approach:** exportar los SVG originales mediante renderizado de Chromium, sin red ni rediseño; PNG nuevos con nombres Notisonda, conservar todos los PNG históricos. Metadatos sociales y apple-touch apuntan a PNG; manifest ofrece PNG192/512 y maskable512 además de SVG. Shell incluye assets y usa notisonda-v3. Fuentes vectoriales originales se conservan.
**Files:** SVG originales del PR, cinco PNG nuevos, index/manifest/sw, library/features/source-tools/v13/agenda (solo textos públicos/nombres de descarga y PRODID), tests de assets/contratos de identidad y pruebas browser existentes. Sin workflows/dependencias/servicios nuevos.

## Task 1
- [x] RED: apple-touch PNG180, OG/Twitter PNG1200×630, manifest PNG192/512/maskable512 y assets reales; fuentes SVG/PNG históricos preservados.
- [x] Exportar PNG fieles al SVG; corregir referencias/metadatos/precaché y copias de marca, conservando formatos JSON, claves de almacenamiento y UID calendario.
- [x] GREEN: Python/Node,38 regresiones Dimension,9 de respaldo y12 de agenda; inspección visual de exportaciones y cabecera móvil/escritorio, sin certificar dispositivos físicos ni cachés de redes sociales.
- [ ] Una revisión independiente final; hallazgos importantes RED→GREEN si aparecen. CI exacta del PR117, integrar/publicar y comprobar assets/identidad/diagnóstico.

## Review focus
Dimensiones/MIME y PNG realmente descargables; icono maskable con margen seguro; metadatos de ambos canales a una imagen rastreable; referencias del shell; compatibilidad de respaldos antiguos y UID estables; conservación de assets y texto del diseñador; sin cambios de alineación/tamaño de marca ni efectos nuevos.
