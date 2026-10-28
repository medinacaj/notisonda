# Recuperación de publicación de Notisonda

> Método nativo, una rama/PR `fix/migracion-notisonda`, revisión independiente final. Continuación autorizada de auditoría/correcciones y publicación; se preservan cambios recientes del usuario.

**Base:** ed20700365dd0799a815297fc0ca3c25617b4bfe, migración pública a Notisonda. El repositorio remoto ahora es medinacaj/notisonda; checkout existente conserva su ubicación local.
**Goal/spec:** publicación y monitor vuelven a funcionar en `https://medinacaj.github.io/notisonda/`, con historial5000/agenda preservados; RSS derivados apuntan al sitio actual. CI deja de rechazar la nueva marca de caché y comprueba su comportamiento real, conservando respaldo/preferencias compatibles.

## Evidencia y alcance
- Issue116: monitor404, ruta anterior `/radar-rss-publico/data/`; nueva ruta `/notisonda/data/` responde200 con5000 noticias y generación2026-10-28T17:50:15Z.
- Deploy40761586402 falla en «Revisar estructura de fuentes», que ejecuta toda la suite Python: tres assertions antiguas del prefijo `radar-rss-v...` rechazan `notisonda-v1`. Catálogo no modificado.
- Monitor, recuperación de noticias/agenda y RSS derivados mantienen cuatro copias de la URL antigua. Un módulo pequeño de identidad pública compartida evita esa divergencia. Mantener firmas de funciones/BASE y seguridad de recuperación, sin relajar validación ni reiniciar datos.
- PR117 (iconos/tarjeta social) se inspeccionó, pero es trabajo visual independiente en otra rama del usuario; no copiar, modificar ni fusionar aquí. No cambiar SVG/PNG/manifest/index/SW ni claves o formatos `radar-*` que preservan datos. Sus tres fallos de calidad provienen de la misma base y se informa su estado real al terminar.
- No workflows/dependencias/servicios nuevos, ni cambio de umbrales, reintentos, schedule3h, retención45d/5000 o fuentes311/8. Documentación de estado apunta al sitio/repositorio nuevos; referencias históricas no se reescriben.

## Task 1: URL operativa y CI de migración
- [x] Tests offline RED que observan URL solicitada por monitor y recuperación; RSS generado con nombre/link Notisonda, manteniendo URLs/IDs originales de artículos.
- [x] Prueba real del ciclo activate del SW en Node: limpia cachés antiguas Radar/Notisonda, conserva la actual y las de otras apps. Sustituir tres assertions de marca obsoletas duplicadas por este comportamiento, sin cambiar el SW del usuario.
- [x] Implementar configuración compartida y adaptar solo sus consumidores; actualizar estado/documentar límites de la migración.
- [x] GREEN en casos nuevos y suite Python/Node, regresiones de respaldo/Dimension y alineación. Validación externa puntual del sitio aparte de tests.
- [ ] Una revisión independiente final; corregir importantes con RED→GREEN si aparecen, sin segunda revisión.
- [ ] PR/CI exacta, publicar y verificar URL actual, RSS derivados,5000/historial/agenda y cierre automático de alerta por monitor existente. No cerrar116 manualmente antes de la recuperación.

## Review focus
Recuperación nunca pierde datos al fallar red; no mezcla fuentes/IDs ni modifica formatos locales; URLs canónicas completas y `source` RSS correctos; SW actual/otrasapps conservados; integración compatible con PR117 sin tocar su rama.
