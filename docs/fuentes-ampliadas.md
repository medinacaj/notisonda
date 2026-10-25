# Ampliación del catálogo — 24 de octubre de 2026

El catálogo propone **226 suscripciones en nueve carpetas**. Se conservan las
211 anteriores con los mismos nombres, URL, IDs y categorías, incluidas las
33 de Concepción. Se añaden seis canales para Maturín/Monagas y nueve para
cultura y entretenimiento internacional.

## Disponibilidad pendiente

**Los 15 canales nuevos no tienen disponibilidad comprobada en esta sesión.**
La política de red del entorno impide consultar Google Noticias y los medios.
Se validaron la sintaxis de las consultas, la ausencia de URL repetidas, los
IDs estables y la correspondencia entre OPML y JSON; no se observaron entradas
ni fechas de publicación. El registro
[`sources/discovery-verification.json`](../sources/discovery-verification.json)
mantiene `pendiente_conectividad`, con cantidad, fecha de publicación y fecha de
verificación nulas. La carpeta puede aparecer sin noticias hasta que el colector
obtenga contenido real. No se presenta esa ausencia como inactividad del medio.

Se usan consultas RSS del buscador, no rutas de RSS directo supuestas. Que una
consulta sea sintácticamente válida no garantiza indexación ni cobertura completa.
Se requiere comprobar los resultados tras habilitar el acceso y revisar las
fuentes sin contenido o con resultados ajenos al ámbito previsto antes de dar la
ampliación por operativa.

## Maturín / Monagas (08)

- La Verdad de Monagas: consulta acotada al dominio y a Maturín/Monagas.
- La Prensa de Monagas: consulta acotada al dominio y a Maturín/Monagas.
- El Periódico de Monagas: consulta acotada al dominio y a Maturín/Monagas.
- Diario El Oriental: consulta acotada al dominio y a Maturín.
- El Nacional: consulta acotada al dominio y a Maturín/Monagas.
- Radar territorial general de Maturín/Monagas, identificado como buscador.

Estos canales no mueven ni sustituyen suscripciones previas de Venezuela. Las
consultas son diferentes y pueden devolver artículos coincidentes; el colector
deduplica por artículo y calcula medios independientes, no el número de consultas.
La vista geográfica de Venezuela y su resumen incluyen 05 y 08; Latinoamérica
incluye 04–08. La carpeta 08 conserva navegación y selección individuales.

## Cultura y entretenimiento internacional (09)

BBC Mundo, Variety, Billboard, The Hollywood Reporter, People, EFE, El País,
Euronews y Rolling Stone. Las consultas incluyen cine, música, artistas,
televisión, literatura o actualidad del entretenimiento, según la especialidad.
Los canales anglófonos consultan la edición estadounidense en inglés y los
hispanohablantes la edición española. La selección no se limita a Chile y no se
incluye automáticamente en filtros geográficos de Chile, Venezuela o
Latinoamérica. Los artículos pueden estar en español o inglés; no se traducen
automáticamente ni se inventan titulares.

## Revalidación

Con conectividad autorizada, consultar cada URL `feed` del registro mediante el
colector con TLS y controles de destino habilitados, y registrar el resultado
real, cantidad observada y última publicación. No cambiar los campos pendientes
por éxito sin una respuesta RSS/Atom interpretable. Revisar pertinencia territorial
y temática, errores, artículos viejos y duplicación editorial; retirar o ajustar
consultas sin cobertura útil por una decisión explícita.

La incorporación conserva atribución, enlaces originales y preferencias locales.
Maturín/Monagas y sus editores locales están en Venezuela; los canales culturales
incluyen editores de varios países. La validación técnica no verifica licencias
individuales ni autoriza reproducción adicional de contenidos. No se añaden
cuentas, analítica, credenciales ni almacenamiento de datos personales.
