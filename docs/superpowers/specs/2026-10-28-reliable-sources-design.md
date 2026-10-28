# Ampliación de fuentes reconocidas en español

> Alcance inicial sobre la base de 221, ampliado posteriormente tras integrar PR102–110 y la nueva solicitud del usuario. El [plan de IA y estructura](../plans/2026-10-28-ia-site-structure.md) define el alcance final y el total de 276. Las observaciones de esta selección se conservan como históricas.

El propietario pide buscar más fuentes fidedignas y populares. La autorización previa permite aplicar la recomendación, verificarla y publicarla mediante una rama/PR. Se mantienen las ocho carpetas y se añaden 23 canales comprobados, priorizando medios reconocidos, agencias/radiotelevisión, ciencia, verificación e investigación y cobertura latinoamericana. No se promete infalibilidad editorial ni un ranking de audiencia que no se midió.

## Selección y alternativas

Se eligen un RSS directo de Billboard Español y 22 consultas RSS de Google Noticias identificadas RADAR. Se usa la conectividad autorizada y se preserva TLS; no se elude la política de red para consultar los editores. El RSS intermediado no se presenta como RSS directo ni como comprobación de los sitios bloqueados. Alternativas descartadas: añadir URLs supuestas sin entradas comprobadas o multiplicar consultas generales sin delimitar editor/idioma/territorio.

Internacionales suma 13 canales: RTVE, RFI, La Vanguardia Internacional, elDiario.es, El Confidencial Mundo, SINC, The Conversation en español, National Geographic España, AFP Factual, Maldita.es, Newtral, Billboard Español y Rolling Stone en Español. Latinoamérica suma 5: Chequeado, Primicias, El Universo, la diaria y OjoPúblico. Venezuela suma 3: Radio Fe y Alegría, Armando.info y El Diario. Maturín/Monagas suma 2 consultas territoriales, El Pitazo y Radio Fe y Alegría, con topónimos en el titular. Chile/Concepción y las dos carpetas técnicas conservan sus canales. Música/cultura queda en Internacionales, sin reabrir una carpeta 09 ni feeds culturales en inglés.

## Contratos

- Catálogo 244 suscripciones/8 carpetas; las 221 anteriores conservan nombre, URL, ID y categoría. Se sincroniza web/data/sources.json mediante parse_opml, sin recolección de red local ni snapshots de artículos nuevos.
- Disponibilidad registrada con instante UTC, URL exacta, HTTP, hash de respuesta, cantidad de entradas, fechas observadas y muestras mínimas públicas. Fechas de RSS/indexador son metadatos observados, no comprobación de hechos o de la fecha original del editor. Índices/autores pueden aparecer en agregadores; no llamar «artículos verificados» al total de entradas.
- Los diez canales de la ampliación anterior se revalidan sin sobrescribir su registro histórico pendiente del 24 de octubre. El Faro queda pendiente: la consulta ensayada no aportó una entrada reciente utilizable; no se declara inactivo el medio.
- No cambiar recolector, deduplicación, contadores, retención 45 d/5000, agenda, UI, preferencias o workflows. No añadir dependencias, cuentas, analítica, nuevos datos personales ni reproducir artículos completos.

## Evidencia y alcance

Se conservan atribución y enlaces a editores. Hay fuentes de España/Francia, Latinoamérica y Venezuela; las obligaciones editoriales/licencias varían por país y editor. La disponibilidad de un RSS no certifica derechos de reproducción adicional ni garantiza exactitud. Riesgo de agregación/indexación → consulta acotada, rótulo RADAR y revisión de muestras; disponibilidad futura → estado puntual, diagnóstico existente; mezcla territorial → intitle:Monagas/Maturín. Responsable de selección: mantenimiento del proyecto; publicaciones originales: cada editor.

Verificación offline de integridad, SHA de los 221 originales, correspondencia OPML/JSON/evidencia, categorías, idioma configurado y fechas relativas al instante de la observación. Revisión independiente, CI pertinente y publicación verificada. No inventar disponibilidad ni popularidad numérica.
