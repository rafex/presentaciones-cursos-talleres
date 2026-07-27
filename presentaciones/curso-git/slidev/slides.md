---
theme: default
title: Git para colaborar
author: Raúl Eduardo González Argote
date: 26 julio 2026
transition: slide-left
aspectRatio: 16/9
layout: cover
class: cover-slide
---

# Git para colaborar

## Entender el historial antes de moverlo

<div class="cover-meta">Curso básico · ejemplos con archivos de texto</div>

<!--
[Sources]
No hay assets externos. El contenido es una explicación didáctica de conceptos básicos de Git.
-->

---
class: section-slide
---

# Git no es una carpeta compartida

Es un sistema para guardar estados, comparar decisiones y coordinar copias del historial.

<div class="big-quote">La colaboración ocurre cuando compartimos <span>historial</span>, no cuando pisamos la misma carpeta.</div>

<!--
[Sources]
https://git-scm.com/book/en/v2/Getting-Started-About-Version-Control
-->

---

# La promesa de este curso

Al terminar, podrás explicar con tus propias palabras:

<v-clicks>

- qué guarda Git cuando hacemos un commit;
- qué diferencia hay entre tu copia local y un remote;
- cuándo conviene merge, rebase o ff-only;
- por qué subir cambios pequeños y frecuentes reduce los conflictos.

</v-clicks>

<div class="bottom-note">No vamos a memorizar recetas: vamos a seguir el viaje de un archivo.</div>

<!--
[Sources]
No hay fuentes externas; son objetivos didácticos del curso.
-->

---
class: story-slide
---

# El meme del viernes

<div class="terminal joke-terminal">
  <div class="terminal-bar"><span></span><span></span><span></span><b>viernes 18:42</b></div>
  <div class="terminal-body">
    <div class="muted"># Equipo, ya quedó todo en mi rama</div>
    <div><span class="accent">$</span> git push</div>
    <div class="danger">remote: conflict detected</div>
    <div><span class="accent">$</span> git push --force</div>
    <div class="danger">error: please fix conflicts first</div>
    <div class="muted">“Que lo arregle quien llegue primero el lunes”</div>
  </div>
</div>

<div class="callout danger-callout">No es una estrategia de integración. Es deuda de coordinación.</div>

<!--
[Sources]
No hay fuentes externas; el escenario es un ejemplo didáctico basado en la mala práctica descrita por el usuario.
-->

---

# El problema no es el viernes

El problema es acumular demasiado tiempo entre dos conversaciones con el historial compartido.

<pre class="timeline">Lunes       Ana trabaja ───────────────────────────────┐
            Luis trabaja ──────────────────────────────┤  cada quien ve un mundo
                                                       │
Viernes     ambos intentan unir 4 días de decisiones ──┘  conflicto grande</pre>

<div class="principle">Git integra texto; el equipo debe integrar trabajo.</div>

<!--
[Sources]
https://git-scm.com/book/en/v2/Git-Branching-Branches-in-a-Nutshell
-->

---
class: section-slide
---

# El modelo mental: Git guarda instantáneas

No guarda una “carpeta mágica”. Cada commit describe cómo estaba el proyecto en un momento y apunta a su antecesor.

<div class="snapshot-row">
  <div class="snapshot"><span>A</span><strong>inicio</strong><code>agenda.txt</code></div>
  <div class="arrow">→</div>
  <div class="snapshot"><span>B</span><strong>agrega demo</strong><code>agenda.txt</code></div>
  <div class="arrow">→</div>
  <div class="snapshot"><span>C</span><strong>reordena cierre</strong><code>agenda.txt</code></div>
</div>

<div class="caption">Puedes volver a mirar cualquier instantánea sin perder las demás.</div>

<!--
[Sources]
https://git-scm.com/book/en/v2/Getting-Started-What-is-Git%3F
-->

---

# Sigamos un archivo de texto

<pre class="text-file">agenda.txt · commit A

1. Bienvenida
2. Preguntas</pre>

<pre v-click class="text-file">agenda.txt · commit B

1. Bienvenida
2. Demo con archivos de texto
3. Preguntas</pre>

<pre v-click class="text-file">agenda.txt · commit C

1. Bienvenida
2. Preguntas
3. Demo con archivos de texto</pre>

<div class="bottom-note">Git no adivina intención: registra estados y la relación entre ellos.</div>

<!--
[Sources]
https://git-scm.com/book/en/v2/Git-Basics-Recording-Changes-to-the-Repository
-->

---
layout: two-cols
---

# Hay cuatro lugares distintos

<div class="place-list">
  <div><b>1</b><span>Working tree</span><small>los archivos que estás editando</small></div>
  <div><b>2</b><span>Staging area</span><small>lo que elegiste preparar</small></div>
  <div><b>3</b><span>Repositorio local</span><small>el historial completo en tu equipo</small></div>
  <div><b>4</b><span>Remote</span><small>otra copia nombrada del historial</small></div>
</div>

::right::

<div class="pipeline">
  <div class="pipe-node active">archivo editado</div>
  <div class="pipe-arrow">↓</div>
  <div class="pipe-node">selección preparada</div>
  <div class="pipe-arrow">↓</div>
  <div class="pipe-node">commit local</div>
  <div class="pipe-arrow">⇄</div>
  <div class="pipe-node remote">remote compartido</div>
</div>

<div class="caption">add, commit, push, fetch y pull mueven información entre lugares distintos.</div>

<!--
[Sources]
https://git-scm.com/book/en/v2/Getting-Started-Git-Basics
https://git-scm.com/docs/gitremote
-->

---

# Un commit es una decisión pequeña y nombrada

<pre class="commit-file">commit 7f3a
parent 2c91
autor: Ana
mensaje: Agrega la sección de preguntas

agenda.txt
+ 3. Preguntas</pre>

<div class="commit-reading">
  <div><b>Qué cambió</b><span>un archivo de texto</span></div>
  <div><b>Por qué cambió</b><span>un mensaje entendible</span></div>
  <div><b>De dónde viene</b><span>un padre en el historial</span></div>
</div>

<div class="principle">Un commit útil se puede leer como una frase.</div>

<!--
[Sources]
https://git-scm.com/book/en/v2/Git-Basics-Viewing-the-Commit-History
-->

---

# Una rama es un marcador, no una copia de carpeta

<div class="branch-graph">
  <div class="branch-line main-line"><span class="commit">A</span><span class="commit">B</span><span class="label main-label">main</span></div>
  <div class="branch-line feature-line"><span class="commit">A</span><span class="commit">B</span><span class="commit hot">C</span><span class="label feature-label">ana</span></div>
  <div class="branch-legend">ana apunta a C · main apunta a B · los commits viven en el historial común</div>
</div>

<div class="caption">Crear una rama es mover un nombre para trabajar con libertad, no duplicar el proyecto.</div>

<!--
[Sources]
https://git-scm.com/book/en/v2/Git-Branching-Branches-in-a-Nutshell
-->

---
class: dark-slide
---

# ¿Dónde vive el historial?

<div class="network">
  <div class="repo">Ana<br><small>repo local</small></div>
  <div class="wire"><span>fetch / push</span></div>
  <div class="repo central">origin<br><small>repo compartido</small></div>
  <div class="wire"><span>fetch / push</span></div>
  <div class="repo">Luis<br><small>repo local</small></div>
</div>

<div class="network secondary">
  <div class="repo">backup<br><small>otro remote</small></div>
  <div class="wire"><span>push</span></div>
  <div class="repo">Ana<br><small>repo local</small></div>
</div>

<div class="dark-claim">Cada participante tiene una copia del historial.<br><span>El remote coordina; no contiene la única verdad posible.</span></div>

<!--
[Sources]
https://git-scm.com/book/en/v2/Getting-Started-About-Version-Control
https://git-scm.com/book/en/v2/Git-Basics-Working-with-Remotes
-->

---

# “Centralizado” describe el flujo, no la naturaleza de Git

<div class="compare-line">
  <div class="compare-item">
    <strong>Flujo centralizado</strong>
    <p>Un remote principal: origin.</p>
    <small>Todos sincronizan con el mismo punto de coordinación.</small>
  </div>
  <div class="compare-divider">≠</div>
  <div class="compare-item">
    <strong>Git distribuido</strong>
    <p>Cada clon tiene historial local completo.</p>
    <small>Puedes inspeccionar, crear ramas y hacer commits sin red.</small>
  </div>
</div>

<div class="principle">Un solo remote no convierte a Git en un sistema centralizado.</div>

<!--
[Sources]
https://git-scm.com/book/en/v2/Getting-Started-About-Version-Control
https://git-scm.com/book/en/v2/Git-Basics-Working-with-Remotes
-->

---

# Un remote es una conexión con nombre

<pre class="remote-list">origin   → repositorio principal del equipo
upstream → repositorio original de un proyecto
backup   → copia de respaldo
cliente  → repositorio de una organización</pre>

<div class="remote-lesson">
  <span class="remote-token">origin</span>
  <span class="remote-arrow">no significa “servidor de Git”</span>
  <span class="remote-token">es sólo un alias</span>
</div>

<div class="caption">Puedes tener uno, varios o ninguno. origin es una convención, no una arquitectura.</div>

<!--
[Sources]
https://git-scm.com/docs/git-remote
https://git-scm.com/book/en/v2/Git-Basics-Working-with-Remotes
-->

---

# Los cuatro movimientos que sí debes distinguir

<div class="movement-list">
  <div><code>clone</code><span>crea tu copia inicial, con historial</span></div>
  <div><code>fetch</code><span>trae referencias nuevas; no cambia tus archivos</span></div>
  <div><code>pull</code><span>fetch + integración en tu rama actual</span></div>
  <div><code>push</code><span>publica tus commits en un remote</span></div>
</div>

<div class="flow-strip"><b>traer primero</b><span>fetch / pull</span><b>integrar</b><span>merge / rebase</span><b>publicar después</b><span>push</span></div>

<!--
[Sources]
https://git-scm.com/docs/git-fetch
https://git-scm.com/docs/git-pull
https://git-scm.com/docs/git-push
-->

---
class: section-slide
---

# El ciclo sano de un día

<div class="day-cycle">
  <div class="day-step"><b>1</b><span>Trae el historial reciente</span><code>fetch / pull</code></div>
  <div class="day-step"><b>2</b><span>Haz una tarea pequeña</span><code>agenda.txt</code></div>
  <div class="day-step"><b>3</b><span>Guarda una decisión clara</span><code>commit</code></div>
  <div class="day-step"><b>4</b><span>Comparte al terminar</span><code>push</code></div>
</div>

<div class="big-quote">La frecuencia correcta es: <span>cuando termina una unidad nuclear de trabajo.</span></div>

<!--
[Sources]
https://git-scm.com/book/en/v2/Git-Basics-Recording-Changes-to-the-Repository
https://git-scm.com/book/en/v2/Git-Basics-Working-with-Remotes
-->

---

# Integrar cambios: primero mira qué pasó

Ana y Luis trabajaron desde el mismo punto:

<pre class="branch-history">main: A ── B

ana:  A ── B ── C   “agrega agenda”
luis: A ── B ── D   “agrega notas”</pre>

<v-click>
<div class="merge-prediction">Si tocaron líneas distintas de agenda.txt, Git puede combinar C y D automáticamente.</div>
</v-click>

<div class="principle">El auto-merge funciona mejor cuando las diferencias son pequeñas y recientes.</div>

<!--
[Sources]
https://git-scm.com/book/en/v2/Git-Branching-Basic-Branching-and-Merging
-->

---

# Merge conserva la historia de dos caminos

<div class="merge-graph">
  <div class="graph-row"><span>A</span><span>→ B</span><span>→ D</span><span class="merge-line">↘</span></div>
  <div class="graph-row feature"><span class="indent"> </span><span>↘ C</span><span class="merge-line">↗</span><span class="merge-node">M</span></div>
  <div class="graph-label">M tiene dos padres: queda visible el encuentro de las ramas.</div>
</div>

<div class="caption">Úsalo cuando quieras conservar el contexto de la integración.</div>

<!--
[Sources]
https://git-scm.com/docs/git-merge
https://git-scm.com/book/en/v2/Git-Branching-Basic-Branching-and-Merging
-->

---

# Rebase reacomoda una línea sobre otra

Antes:

<pre class="rebase-graph">main:    A ── B ── D
                    ╲
feature:             C</pre>

Después:

<pre class="rebase-graph">main:    A ── B ── D ── C'
                         ↑
                 mismo trabajo, nuevo padre</pre>

<div class="rebase-warning"><b>Importante:</b> C cambia de identidad. Rebase reescribe commits.</div>

<div class="caption">Úsalo para ordenar trabajo local o una rama que todavía no compartiste.</div>

<!--
[Sources]
https://git-scm.com/docs/git-rebase
https://git-scm.com/book/en/v2/Git-Branching-Rebasing
-->

---

# Merge y rebase responden preguntas distintas

<div class="decision-table">
  <div class="decision-head"><span>Si preguntas…</span><span>La opción suele ser…</span></div>
  <div><span>¿Quiero conservar el encuentro de dos ramas?</span><code>merge</code></div>
  <div><span>¿Quiero limpiar mi rama local antes de compartirla?</span><code>rebase</code></div>
  <div><span>¿Quiero avanzar sin crear un merge commit?</span><code>ff-only</code></div>
</div>

<div class="principle">La política del equipo importa: no reescribas una rama que otras personas ya usan.</div>

<!--
[Sources]
https://git-scm.com/book/en/v2/Git-Branching-Rebasing
https://git-scm.com/docs/git-merge
-->

---

# ff-only: integrar sin dibujar una bifurcación

Si tu rama local sólo está detrás:

<pre class="ff-graph">antes:    A ── B        main
                    └─ C    origin/main

después:  A ── B ── C  main avanza al mismo commit</pre>

<div class="ff-rule"><code>git merge --ff-only origin/main</code><span>falla si hay dos caminos que realmente necesitan decidirse.</span></div>

<div class="caption">Es una baranda de seguridad: no inventa una integración ni resuelve un conflicto por ti.</div>

<!--
[Sources]
https://git-scm.com/docs/git-merge
-->

---
class: dark-slide
---

# ¿Cuándo aparece un conflicto?

Dos personas editaron la misma zona de acuerdos.txt:

<pre class="conflict-file">&lt;&lt;&lt;&lt;&lt;&lt;&lt; ana
- Revisar cambios antes de las 16:00
=======
- Revisar cambios antes de las 17:00
&gt;&gt;&gt;&gt;&gt;&gt;&gt; luis</pre>

<div class="conflict-answer"><b>Git no sabe qué decisión representa al equipo.</b><br>La persona debe leer ambas versiones, elegir una combinación y crear un nuevo commit.</div>

<!--
[Sources]
https://git-scm.com/book/en/v2/Git-Branching-Basic-Branching-and-Merging
-->

---

# Resolver no es “borrar las marcas”

El resultado correcto expresa una decisión humana:

<pre class="text-file">acuerdos.txt · resultado acordado

- Revisar cambios antes de las 16:00
- Si hay bloqueos, avisar en el canal del equipo</pre>

<div class="resolution-steps"><span>1. leer</span><span>2. conversar</span><span>3. editar</span><span>4. comprobar</span><span>5. commit</span></div>

<div class="principle">Un conflicto pequeño es una conversación corta. Uno acumulado se convierte en investigación.</div>

<!--
[Sources]
https://git-scm.com/book/en/v2/Git-Tools-Advanced-Merging
-->

---

# Lo que pasa cuando esperas hasta el viernes

<div class="causal-flow">
  <span>4 días sin traer cambios</span><b>→</b>
  <span>ramas divergentes</span><b>→</b>
  <span>conflictos en muchas zonas</span><b>→</b>
  <span>prisa y poca memoria</span><b>→</b>
  <span>push and run</span>
</div>

<div class="callout danger-callout">El último que toca la integración hereda decisiones que nunca estuvo presente para discutir.</div>

<!--
[Sources]
No hay fuente externa; es un modelo causal didáctico construido a partir del problema descrito por el usuario.
-->

---

# La alternativa: integración continua de verdad

<pre class="day-log">09:00  fetch / pull       “¿qué cambió mientras dormía?”
11:30  commit pequeño     “terminé una unidad”
13:00  push               “el equipo ya puede verla”
15:00  fetch / pull       “me pongo al día”
17:00  commit + push      “cierro el día con historial compartido”</pre>

<div class="healthy-flow"><span>cambio pequeño</span><b>→</b><span>historial fresco</span><b>→</b><span>auto-merge sencillo</span></div>

<div class="caption">Subir diariamente no significa publicar trabajo roto: significa compartir unidades nucleares, revisables y con contexto.</div>

<!--
[Sources]
https://git-scm.com/book/en/v2/Git-Basics-Working-with-Remotes
-->

---
class: section-slide
---

# Un mini laboratorio con archivos de texto

Trabajaremos sobre menu.txt:

<div class="lab-grid">
  <div><b>Ana</b><pre>1. Sopa
2. Pan</pre><small>agrega una opción</small></div>
  <div><b>Luis</b><pre>1. Sopa
2. Pan</pre><small>corrige el orden</small></div>
  <div><b>Pregunta</b><pre>¿Editaron la misma línea?</pre><small>predice: auto-merge o conflicto</small></div>
</div>

<div class="bottom-note">La práctica no evalúa velocidad. Evalúa si puedes explicar qué ocurrió en el historial.</div>

<!--
[Sources]
No hay fuentes externas; ejercicio original para el curso.
-->

---

# Reglas para llevarte hoy

<v-clicks>

- Piensa en commits como decisiones, no como “guardados”.
- Distingue working tree, staging, repo local y remote.
- Trae cambios antes de empezar y comparte cuando cierres una unidad.
- Usa merge para conservar contexto; rebase para ordenar trabajo no compartido.
- Usa ff-only como baranda cuando no quieres integrar a ciegas.
- Si aparece un conflicto, conversa la decisión: Git no puede inventarla.

</v-clicks>

<!--
[Sources]
https://git-scm.com/book/en/v2/Git-Branching-Branching-Workflows
https://git-scm.com/book/en/v2/Git-Basics-Working-with-Remotes
-->

---
layout: statement
class: final-slide
---

# El mejor historial es el que el equipo puede entender mañana.

<div class="final-subtitle">Pequeño · frecuente · explícito · compartido</div>

<!--
[Sources]
No hay fuentes externas; cierre didáctico original.
-->

---
class: contact-slide
---

# Contacto

> Raúl Eduardo González Argote

- 🔗 [**LinkedIn**](https://www.linkedin.com/in/soft-architect-raul-gonzalez) para seguir en contacto
- ✉️ [**rafex@rafex.dev**](mailto:rafex@rafex.dev) para dudas o charlas
- 💻 [**github.com/rafex**](https://github.com/rafex)
- 📝 [**theworldofrafex.blog**](https://theworldofrafex.blog/)

<div class="contact-logo" role="img" aria-label="Rafex · Una idea diferente"></div>

<!--
[Sources]
Datos de contacto del autor, siguiendo la diapositiva de contacto de Boost Desarrollo.
-->
