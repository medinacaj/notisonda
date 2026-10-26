# Correcciones pendientes verificadas

Petición: continuar las correcciones de la auditoría sobre main, sin reemplazarlo por ramas antiguas. Base: ebd1b15 (PR93). Implementación en el checkout cloud existente y una rama nueva, conforme a la preferencia ya acordada.

Se recupera la intención del PR76: comparar instantes UTC al elegir respaldo, rechazar fechas sin zona/inválidas y no continuar sin copia verificable. El PR92 aporta únicamente el encabezado OPML correcto: 221 fuentes y ocho carpetas. Las marcas masivas deben esperar el historial completo; si no se puede verificar, no se modifica la lectura. El aviso de actualización debe coincidir con el cron actual de tres horas.

Se adaptan estas correcciones al main vigente: fusionar las ramas antiguas completas introduciría cambios ajenos y revertiría comportamientos posteriores. No se cambian retención (45 días/5000), fuentes, agenda, proveedores ni dependencias. Las preferencias siguen locales. Se actualiza el estado del proyecto con evidencia de publicación y límites pendientes, sin afirmar validación física ni licencias.

Aceptación: selección cronológica correcta con offsets/equivalencias; recuperación segura ante fechas inválidas y red caída; lectura global/de carpeta sólo sobre archivo verificado; OPML idéntico salvo título; frecuencias coherentes; suite offline y regresiones HTTPS verdes; revisión independiente, CI, integración y comprobación pública.
