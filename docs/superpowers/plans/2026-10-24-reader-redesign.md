# Noticias: navegación persistente, portada y fuentes

Objetivo solicitado: lateral visible y ocultable en escritorio, cabecera y marca compactas, últimas noticias en carrusel, cobertura secundaria discreta, más entretenimiento internacional, carpetas Maturín/Monagas y Concepción/Biobío, firma LinkedIn y tema automático con elección manual.

Decisiones de implementación: conservar la cabecera funcional de búsqueda/configuración, retirar navegación horizontal redundante; carrusel manual accesible en lugar de clima (no añadir proveedor/API sin una necesidad comprobada); mantener las fuentes existentes y añadir consultas regionales e internacionales, sin mover identidades ni inventar fotos.

- [x] Lateral persistente escritorio con preferencia de ocultar, drawer móvil con foco y Escape, tema system por defecto y manual persistido; firma enlaza https://www.linkedin.com/in/medinacaj/.
- [x] Carrusel con al menos tres noticias si hay datos, controles manuales y scroll táctil; tipografía compacta sin fotos y radar/tendencias plegados.
- [x] Catálogo añade Maturín/Monagas y cultura/entretenimiento internacional; mantiene Concepción y sus fuentes del Biobío. Geografía Venezuela/Latinoamérica incluye Monagas; cultura no se fuerza a Chile.
- [x] Pruebas de comportamiento y suite existente, móvil/escritorio y revisión independiente.
- [ ] PR96: recuperar/verificar antes de aplicar; URL y ref del repositorio seleccionado devuelven404/no existe. Se solicitó enlace al usuario; no sustituirlo por cambios supuestos.

Red: medios y Google Noticias bloqueados por política del entorno. Se guardaron destinos específicos en el borrador para revisión en ajustes; esto no habilita red ni acredita disponibilidad. Registro de fuentes nuevas debe distinguir configuración de verificación HTTP real. Sin consultas externas en tests, sin dependencias productivas nuevas, sin despliegue ni merge automático.
