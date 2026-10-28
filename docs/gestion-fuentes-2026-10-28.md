# Configuración y gestión de fuentes

El catálogo conserva las **311 suscripciones, ocho categorías originales y sus URL/identificadores**. Esta mejora se aplica al gestor personal; no modifica la recopilación ni crea cuentas.

## Fallas corregidas
- Las URL RSS y web existían en `sources/feeds.opml` y `web/data/sources.json`, pero el listado ocultaba el acceso dentro del diálogo de detalles. Ahora son enlaces visibles y el RSS tiene acción de copia; el CSV permite inspeccionar la base completa con direcciones e identificadores. Los enlaces RSS extensos ocupan hasta tres líneas, conservan el destino completo y se pueden leer íntegros en Detalles o copiar; así una búsqueda larga de Google no ocupa toda la pantalla.
- Filas antes asociadas por nombre/categoría ahora utilizan ID. Dos fuentes con el mismo nombre se administran por separado.
- Las acciones por carpeta reflejan asignaciones personales y recalculan cantidades después de cambiar una fuente individual. La exportación OPML ya no vuelve a los nombres/categorías originales.
- Las carpetas personales y las modificaciones de categorías originales ya no se recortan a 160 miembros al recargar; la lectura local admite hasta 4000 IDs por carpeta. No recupera miembros que versiones anteriores ya hayan sobrescrito: un respaldo previo puede restaurarlos.
- Restablecer preferencias también desactiva y persiste el modo ligero, conservando leídas, guardadas, carpetas, etiquetas y actividades.
- La explicación de Apariencia aclara que los ajustes pertenecen a este navegador. El modo ligero tiene prioridad sobre fotografías y se puede elegir manualmente. El selector de antigüedad no amplía el archivo público de 45 días/hasta 5000 noticias.
- Los diagnósticos consultan las URL por ID en el catálogo, porque `status.json` no duplica ese campo. El panel abierto se actualiza al aplicar una nueva publicación.

## Funciones inspiradas en lectores como Feedly

| Acción | Resultado en Radar RSS |
|---|---|
| Buscar una suscripción | Nombre, categoría, carpeta personal, dominio o dirección completa del RSS. |
| Filtrar catálogo | Visibles/ocultas, RSS directo/RADAR y último estado publicado: correcta, error, vacía, antigua o sin diagnóstico. |
| Revisar una fuente | RSS y web enlazados, copiar dirección, detalles de identidad/carpeta/último chequeo y acceso a sus noticias. |
| Organizar | Carpetas personales y movimiento de fuentes; se conserva la categoría original para inspección. |
| Exportar suscripciones | OPML de fuentes visibles, con nombres y pertenencias personales, incluso varias carpetas o fuentes sin carpeta. |
| Examinar la base | CSV de todo el catálogo, independiente de filtros: ID, nombre, RSS, web, carpetas, tipo, visibilidad y estado. |
| Importar desde un lector | OPML local con previa, cancelar/aplicar e informe de URL no reconocidas. |
| Leer y conservar | Siguen disponibles sin leer/leídas, Guardadas, copias locales, etiquetas, búsquedas guardadas, palabras silenciadas, atajos y respaldo JSON. |

No se utiliza la API de Feedly ni se afirma equivalencia con todas sus funciones. El estado «lectura correcta» significa que la última recopilación pudo procesar el canal; no verifica cada noticia ni garantiza disponibilidad futura. Una fuente oculta puede funcionar correctamente en el servidor.

## Importación OPML

1. Exporta tus suscripciones desde tu lector y elige **Configuración → Mis fuentes → Importar desde Feedly u otro lector (OPML)**.
2. Revisa fuentes reconocidas, carpetas, apariciones repetidas y entradas sin incorporar. Puedes descargar el informe CSV.
3. Aplicar activa las fuentes reconocidas y une sus pertenencias con las carpetas existentes. Los nombres coincidentes se reutilizan sin distinguir mayúsculas; los niveles anidados se representan como `Carpeta / Subcarpeta`. El resto de tus fuentes y carpetas se conserva.
4. Si una fuente no está en el catálogo, el informe conserva nombre/URL/motivo para incorporarla posteriormente al OPML del repositorio y verificar su feed. Importar no simula una suscripción activa ni hace consultas de red a esas direcciones.

La coincidencia utiliza la URL registrada, normalizando mayúsculas del dominio/puerto estándar/fragmento, sin convertir http a https ni reordenar parámetros de búsqueda. No se empareja por nombre o dominio. La misma URL en varias carpetas conserva sus pertenencias; sus repeticiones no añaden fuentes nuevas.

Límites explícitos: archivo de 1 MB, hasta 1000 entradas RSS/Atom y 2000 elementos outline, 25 carpetas personales y nombres de hasta 45 caracteres. Se rechazan XML malformado, DTD y entidades. Solo se abren enlaces http(s) sin credenciales. Aplicar comprueba que no haya cambiado la publicación y guarda las tres claves antes de cambiar el estado activo; si falla revierte las escrituras realizadas y comunica si tampoco pudo recuperarlas. El usuario no necesita aceptar una importación para ver su informe.

## Datos y evidencia

OPML/CSV/JSON se generan o leen localmente por petición del visitante. No se envían preferencias ni archivos a un servidor; abrir voluntariamente RSS/web sí visita el sitio enlazado. Sin nuevos proveedores, dependencias, rastreo ni sincronización. El CSV neutraliza fórmulas de hoja de cálculo. Este cambio no certifica derechos sobre contenido externo ni cumplimiento legal; conserva atribución/enlaces y los límites anteriores de retención.

Las pruebas se ejecutan sin consultar medios: utilidades reales en Node a través de la CI Python existente y flujos completos en Playwright (URL, filtros, identidad, carpetas, OPML, cancelación, almacenamiento, actualización y modo ligero). El PR y sus Actions registran resultados sobre el commit exacto. No equivalen a probar un iPhone físico o todas las exportaciones de terceros.
