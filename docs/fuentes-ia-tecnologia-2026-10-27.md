# Ampliación de inteligencia artificial, informática y tecnología — 27-10-2026

## Alcance y conservación
Se proponen **27 canales nuevos en español** sobre IA, investigaciones, papers, conferencias, lanzamientos, software, hardware, seguridad y tecnología empresarial. Son 23 feeds de medios y cuatro consultas temáticas de Google Noticias. Total propuesto: **248 fuentes en las mismas ocho carpetas** (221 originales intactas). El OPML es la fuente de verdad; se actualiza el catálogo JSON estático y la prueba de regresión de cantidad. No se cambian el colector, la deduplicación, la frecuencia de publicación, las otras categorías ni la política de retención.

## Fuentes incorporadas
**IA (10):** Agencia SINC (Tecnología, Ciencia y Agenda); Planeta Chatbot; Maldita Tecnología; Enrique Dans; radar MIT Technology Review en español; radar de papers/estudios; radar de congresos/conferencias; radar de modelos/herramientas. 

**Tecnología (17):** Microsiervos, Naukas, Computer Hoy, El Chapuzas Informático, Profesional Review, SoftZone, MuyComputerPRO, Silicon, 20minutos Tecnología, La Vanguardia Tecnología, Omicrono, MuySeguridad, tuexperto, MovilZona, elDiario.es Tecnología, Xataka Android y MuyPymes.

## Estado de comprobación y límites
- **Evidencia externa:** 20 de las 23 URL de editor respondieron a consultas con tipo MIME XML/RSS o contaban con comprobación previa en lectores RSS. Esto **no equivale** a validar el contenido interno ni fechas de artículos.
- **Pendiente por intermitencia o acceso:** MuyComputerPRO, MuySeguridad y MuyPymes mostraron tiempo de espera en la última revisión; Silicon cuenta con evidencia previa en lector RSS, pero el acceso desde esta sesión no permitió inspección directa. La presencia en catálogo no significa actividad garantizada.
- **MIT Technology Review en español:** el portal existe en `https://www.technologyreview.es/`, pero no se confirmó feed RSS propio. Por ello se incorpora un **RADAR de Google Noticias**, rotulado como intermediario y separado del feed en inglés ya existente. Las búsquedas de papers, eventos y lanzamientos también son consultas del buscador, no canales editoriales directos.
- **Publicación real:** pendiente de ejecución por GitHub Actions tras revisión y fusión de la rama. La verificación operativa requiere revisar `web/data/status.json`, el número de entradas y la actualidad de cada nueva fuente. No se da por comprobado que un feed publique artículos recientes solo por devolver un MIME XML/RSS.

## Aspectos técnicos y legales
Se mantienen IDs derivados de URL, agrupación y deduplicación existentes, atribución, enlaces originales y retención de 45 días. No se almacenan nuevas credenciales ni datos personales. Los titulares/resúmenes son de terceros: se conservan las mismas reglas de uso del recolector; la accesibilidad de un feed no implica licencia para reproducir contenido completo. Jurisdicciones de medios: principalmente España y Latinoamérica; evaluar condiciones editoriales individualmente cuando proceda.
