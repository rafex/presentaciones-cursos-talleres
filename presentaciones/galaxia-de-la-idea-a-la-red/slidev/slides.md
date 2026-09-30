---
theme: default
title: "galaxIA: de una idea a una red"
author: Raúl Eduardo González Argote
date: septiembre 2026
transition: slide-left
aspectRatio: 16/9
fonts:
  provider: none
layout: cover
class: cover-slide
---

# galaxIA

## De una idea a una red: por qué nació, cómo cambió en tres meses y cómo puedes sumarte

<div class="cover-meta">Charla · 45 min · público técnico y estudiantes</div>

<!--
Notas del orador:
- Esta es la segunda charla de galaxIA. La primera fue el 3 de julio de 2026 ("Reutiliza tus equipos viejos para una red soberana e IA"); hoy contamos qué pasó desde entonces.
- Ritmo: ~35 min de charla y ~10 de preguntas. Hay slides de respaldo al final por si alguien pide más detalle.
- Todo lo que se llama "snapshot" viene de mi laboratorio del 27-28 de septiembre de 2026: es una observación propia, no un release estable.

[Sources]
https://github.com/rafex/presentaciones-cursos-talleres/tree/main/presentaciones/red-soberana-de-ia
-->

---

# Ruta de hoy

<div class="cards four">
<div class="card"><h3>1 · Por qué nació</h3><p>El problema y la pregunta que dieron origen a galaxIA.</p></div>
<div class="card violet"><h3>2 · De dónde partimos</h3><p>La primera charla, 3 de julio: qué mostramos y qué prometimos.</p></div>
<div class="card green"><h3>3 · Cómo cambió</h3><p>De un Registry central a una red P2P, y de TypeScript a Rust.</p></div>
<div class="card amber"><h3>4 · Retos y cómo sumarte</h3><p>Lo que falta y cinco caminos concretos para ayudar.</p></div>
</div>

<div class="callout" style="margin-top:1.6rem">Al final: <b>~10 min de preguntas</b>. Si algo se quedó corto, hay slides de respaldo.</div>

<!--
Notas del orador:
- Cuatro bloques. Los tiempos aproximados: 9 min el origen y el punto de partida, 12 min la evolución, 7 min los retos, 5 min cómo sumarse, ~10 min de preguntas.
- Aviso al público técnico: habrá IPs, puertos y versiones reales del laboratorio; al público de estudiantes: nada de eso es necesario para seguir la historia.
-->

---
class: section-slide
---

<div class="kicker">Acto 1</div>

# Por qué nació

Un problema, una pregunta y una apuesta.

<!--
Notas del orador:
- Pausa breve. Este bloque es corto: el origen en tres ideas.
-->

---

# La IA útil se concentró

<div class="two-wide">
<div>

ChatGPT, Claude y Gemini son herramientas **excelentes**, pero centralizadas:

- Un solo proveedor decide **disponibilidad** y **precio**.
- Tus datos viven **en su servidor**.
- Si el servicio cambia o desaparece, **te quedas sin nada**.

<div class="callout warn">No es una crítica a esas herramientas: es una <b>dependencia</b> que la mayoría no eligió conscientemente.</div>

</div>
<div class="figure">

<img src="./assets/images/modelo-nube.svg" alt="Modelo de nube: tú, un solo proveedor y tus datos en su servidor" />

</div>
</div>

<!--
Notas del orador:
- Pregunta al público: "¿cuántos usaron una IA en la última semana? ¿cuántos saben dónde se guardan sus conversaciones?".
- Idea central: no se trata de rechazar la nube, sino de notar que hoy casi no hay alternativa organizada para una comunidad pequeña.

[Sources]
Primera charla, slide "El modelo de nube tradicional": https://github.com/rafex/presentaciones-cursos-talleres/tree/main/presentaciones/red-soberana-de-ia
-->

---
class: statement-slide
---

# Mientras tanto, hay hardware que ya nadie usa

<div class="big-quote">Laptops de oficina, mini-PC, una Raspberry Pi en un cajón. <span>¿Y si una comunidad pudiera armar su propia IA con lo que ya tiene?</span></div>

<!--
Notas del orador:
- Aquí nace la apuesta: el hardware modesto no es el caso raro, es el caso base. Todo el diseño parte de eso: nada de GPU obligatoria, nada de servidores dedicados.
- Deja la pregunta en pantalla unos segundos antes de avanzar.

[Sources]
https://github.com/rafex/galaxIA/blob/main/README.md
-->

---

# La pregunta

<div class="two-wide">
<div>

¿Cómo sería una IA útil **para tu escuela, tu equipo o tu colectivo**…

- **sin mandar tus datos** a un tercero,
- **sin pagar** una suscripción,
- **sin depender** de que ese servicio siga existiendo mañana?

**La respuesta de galaxIA:** una red donde cada equipo aporta *una capacidad distinta* y **nadie es dueño de toda la red**.

</div>
<div class="figure">

<img src="./assets/images/modelo-soberana.svg" alt="Red soberana: tú, tu equipo, el equipo de un vecino y el de la comunidad" />

</div>
</div>

<!--
Notas del orador:
- Este es el cambio de modelo mental: no reemplazar a un proveedor por otro, sino no depender de ningún proveedor único.
- Cada nodo es de alguien distinto: el tuyo, el de un vecino, el de la comunidad.

[Sources]
Primera charla, slide "La alternativa: red soberana federada": https://github.com/rafex/presentaciones-cursos-talleres/tree/main/presentaciones/red-soberana-de-ia
-->

---

# Lo que queríamos que fuera verdad

<div class="cards two-col">
<div class="card"><h3>Con el hardware que ya existe</h3><p>Sin presupuesto nuevo: lo modesto es el caso base, no la excepción.</p></div>
<div class="card violet"><h3>Sin ceder el control de los datos</h3><p>Cada nodo decide qué guarda y a quién responde.</p></div>
<div class="card green"><h3>Sumarse sin pedir permiso</h3><p>Cualquiera aporta un nodo si cumple el contrato del protocolo.</p></div>
<div class="card amber"><h3>Privacidad dentro del protocolo</h3><p>No un aviso legal: <code>scope</code>, <code>retention</code> y <code>provenance</code> viajan en cada mensaje.</p></div>
</div>

<!--
Notas del orador:
- Cuatro principios que siguen en pie tres meses después. Veremos cuáles se cumplieron y cuáles siguen siendo reto.
- `scope` limita quién puede resolver tu petición (local, network, community, external); `retention` dice qué hace cada nodo con tus datos; `provenance` deja constancia de qué modelo razonó y a dónde viajaron los datos.

[Sources]
https://github.com/rafex/galaxIA/blob/main/docs/trust.md
https://github.com/rafex/presentaciones-cursos-talleres/tree/main/presentaciones/red-soberana-de-ia
-->

---

# El nombre y su vocabulario

`galaxIA` = *galaxy* + *IA*. Los roles siguen la metáfora:

<div class="dense">

| Concepto técnico | Nombre galaxIA | Qué hace |
|---|---|---|
| Nodo que razona (LLM) | **Star** | Genera las respuestas |
| Nodo con una herramienta | **Satellite** | OCR, base de conocimiento, RAG… |
| Nodo con su propio ciclo de razonamiento | **Nova** | Razona en varias rondas antes de responder |
| Punto de entrada al swarm | **Atlas** | Ayuda a un nodo nuevo a encontrar la red |
| Orquestador | **Navigator** | Elige qué Star y qué Satellites usar |
| Anuncio de capacidades | **Beacon** | Lo que un nodo dice que sabe hacer |
| Tarea enviada a un nodo | **Mission** | Una petición de chat o de herramienta |
| Chat web | **Portal** | La entrada humana a la red |

</div>

<!--
Notas del orador:
- No hace falta memorizarlo: reaparece en los diagramas. Lo esencial: Star razona, Satellite ejecuta una capacidad, Navigator decide quién hace qué, Atlas solo ayuda a entrar.
- Aclara que "Atlas" ya no es un registro central (eso cambia en el Acto 2).
- Nova existe en el diseño, pero no está desplegada en el laboratorio actual.

[Sources]
https://github.com/rafex/galaxIA/blob/main/docs/vocabulario.md
-->

---

<div class="kicker">Punto de partida · 3 de julio de 2026</div>

# La primera charla: tres equipos y un Registry

<div class="two">
<div class="figure">

<img src="./assets/images/hardware-real.svg" alt="Router TP-Link con OpenWrt, laptop, Bastion y Raspberry Pi 4B" />

</div>
<div>

**El hardware**

- Router TP-Link con OpenWrt (`192.168.1.0/24`)
- Laptop i5 · Debian 13 → *Registry + chat*
- Bastion i7 · Debian 13 → *LLM con llama.cpp*
- Raspberry Pi 4B · DietPi → *OCR con Tesseract*

**El protocolo**

- JSON sobre WebSocket
- Un **Registry central**: `hello → register → heartbeat` cada 10 s
- SDK solo en TypeScript

</div>
</div>

<!--
Notas del orador:
- Esa fue la demo: tres equipos, tres roles, una sola red. Funcionaba de punta a punta con hardware real y heterogéneo, pero todo pasaba por el Registry de la laptop.
- El Registry nunca iniciaba la conexión: el nodo llegaba primero. Eso permitía redes asimétricas, pero también dejaba un punto único de falla.

[Sources]
https://github.com/rafex/presentaciones-cursos-talleres/tree/main/presentaciones/red-soberana-de-ia
-->

---

# Así se veía la red

<div class="figure">

<img src="./assets/images/topologia-3-equipos.svg" alt="Usuario, laptop con Registry y chat, Bastion con LLM local y Raspberry Pi con OCR" />

</div>

<div class="callout warn">Todo dependía de <b>un Registry central</b>: si la laptop caía, la red dejaba de existir.</div>

<!--
Notas del orador:
- Este diagrama es el "antes". Recuérdenlo: en el Acto 2 lo comparamos con el "después".
- Los tres mensajes `hello / register / ping` eran el pegamento de esa versión; hoy ya no existen en el protocolo.

[Sources]
https://github.com/rafex/presentaciones-cursos-talleres/tree/main/presentaciones/red-soberana-de-ia
-->

---

# Lo que prometimos en «Qué sigue»

<div class="cards four">
<div class="card"><h3>SDKs en más lenguajes</h3><p>Rust, Python y Java: "hoy solo hay TypeScript".</p></div>
<div class="card violet"><h3>Identidad criptográfica real</h3><p>Ed25519 en lugar del DID simplificado.</p></div>
<div class="card green"><h3>Descubrimiento descentralizado</h3><p>Reemplazar el Registry central por mDNS/DHT.</p></div>
<div class="card amber"><h3>Confianza comunitaria</h3><p>Reputación, vetos y políticas de privacidad más finas.</p></div>
</div>

<div class="callout" style="margin-top:1.6rem">Guarda estas cuatro promesas: <b>las revisamos al final del Acto 2</b>.</div>

<!--
Notas del orador:
- Esta fue literalmente la última slide de contenido de la primera charla. La usamos como checklist honesto: ¿qué cumplimos en tres meses?
- No adelantes el resultado; en el Acto 2 hay una slide donde se marca cada una.

[Sources]
https://github.com/rafex/presentaciones-cursos-talleres/tree/main/presentaciones/red-soberana-de-ia
-->
