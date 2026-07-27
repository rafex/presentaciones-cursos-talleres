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
Notas del orador:
- Presenta el curso como una explicación del modelo mental de Git, no como una lista de recetas.
- El hilo conductor será un archivo de texto que pasa por commits, ramas y remotes.
- Indica que la práctica completa vive en:
  https://github.com/rafex/IB-git

Arranque para el grupo:
~~~bash
git clone https://github.com/rafex/IB-git.git git-taller
cd git-taller
bash setup-global.sh
~~~

[Sources]
https://github.com/rafex/IB-git
-->

---
class: section-slide
---

# Git no es una carpeta compartida

Es un sistema para guardar estados, comparar decisiones y coordinar copias del historial.

<div class="big-quote">La colaboración ocurre cuando compartimos <span>historial</span>, no cuando pisamos la misma carpeta.</div>

<!--
Notas del orador:
- Pregunta: “¿Git es una carpeta compartida o un historial de decisiones?”
- Aclara que cada clon tiene su propio working tree y su propio repositorio local.
- Repite la frase: la carpeta es el material de trabajo; el historial es lo que permite colaborar.

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
Notas del orador:
- Lee los cuatro resultados como la promesa del curso.
- Explica que cada concepto se demostrará con archivos de texto, no con una aplicación compleja.
- Anuncia el repositorio de práctica y que cada ejercicio tiene su propio setup.sh.

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
Notas del orador:
- Usa el meme como gancho y pregunta quién ha recibido una rama “terminada” el viernes por la tarde.
- Señala que git push --force no resuelve un conflicto; puede reescribir trabajo remoto.
- Pide que distingan el síntoma (push rechazado) de la causa (historial desactualizado y decisiones acumuladas).

Comandos para una demostración segura:
~~~bash
git status
git log --oneline --graph --all
git fetch
~~~

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
Notas del orador:
- Pide al grupo que identifique qué cambios no conoce cada persona el lunes.
- Explica que traer cambios al comenzar y compartir unidades nucleares reduce la distancia entre historiales.
- Conecta con la regla práctica: pull/fetch antes de empezar y push al cerrar una unidad revisable.

Comando para visualizar la divergencia:
~~~bash
git log --oneline --graph --all
~~~

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
Notas del orador:
- Introduce el ejercicio 01 del repositorio IB-git.
- Pide ejecutar el setup y observar que se crea un repositorio independiente.

~~~bash
cd ejercicios/01-commits
bash setup.sh
cd taller-01
git status
~~~

- Explica que el objetivo es crear los estados A, B y C de agenda.txt.

[Sources]
https://git-scm.com/book/en/v2/Getting-Started-What-is-Git%3F
https://github.com/rafex/IB-git/blob/main/ejercicios/01-commits/README.md
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
Notas del orador:
- Haz una pausa después de cada estado y pregunta: “¿qué quedó registrado en este commit?”
- La secuencia para el estado A es:

~~~bash
git status
git add agenda.txt
git commit -m "agrega agenda inicial"
git log --oneline
~~~

- Para B y C se repite el ciclo: editar, git status, git add, git commit y git log.
- Al final muestra que se puede volver a inspeccionar A sin borrar B ni C:

~~~bash
git show HEAD~2:agenda.txt
git diff HEAD~2 HEAD
~~~

[Sources]
https://git-scm.com/book/en/v2/Git-Basics-Recording-Changes-to-the-Repository
https://github.com/rafex/IB-git/blob/main/ejercicios/01-commits/README.md
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
Notas del orador:
- Recorre el flujo de izquierda a derecha y explica qué comando mueve información.
- Working tree: se edita el archivo y se inspecciona con git status/git diff.
- Staging: git add selecciona lo que entrará al próximo commit.
- Repo local: git commit guarda la decisión y git log permite leerla.
- Remote: git push publica; git fetch trae referencias sin tocar archivos; git pull trae e integra.

Demostración:
~~~bash
git status
git diff
git add agenda.txt
git diff --staged
git commit -m "describe la decisión"
git log --oneline
~~~

[Sources]
https://git-scm.com/book/en/v2/Getting-Started-Git-Basics
https://git-scm.com/docs/gitremote
https://github.com/rafex/IB-git/blob/main/recursos/modelo-mental.md
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
Notas del orador:
- Explica que un commit no es sólo “guardar”: tiene contenido, autor, mensaje, padre e identidad.
- Pide leerlo como una frase: “Ana agrega la sección de preguntas a partir de 2c91”.

Comandos:
~~~bash
git show HEAD
git log --oneline
git show HEAD~1
~~~

- Conecta el mensaje del commit con la colaboración: un mensaje claro reduce preguntas futuras.

[Sources]
https://git-scm.com/book/en/v2/Git-Basics-Viewing-the-Commit-History
https://github.com/rafex/IB-git/blob/main/recursos/cheat-sheet.md
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
Notas del orador:
- Introduce el ejercicio 02: una rama es un nombre móvil que apunta a un commit.
- Ejecuta el setup y muestra que crear la rama no duplica la carpeta.

~~~bash
cd ejercicios/02-ramas
bash setup.sh
cd taller-02
git branch
git branch ana
git switch ana
~~~

- En ana: edita agenda.txt, agrega, commit y luego vuelve a main.

~~~bash
git add agenda.txt
git commit -m "agrega sección de cierre"
git switch main
cat agenda.txt
git log --oneline --graph --all
~~~

- Pregunta: “¿Dónde quedó el commit de ana y qué rama apunta a él?”

[Sources]
https://git-scm.com/book/en/v2/Git-Branching-Branches-in-a-Nutshell
https://github.com/rafex/IB-git/blob/main/ejercicios/02-ramas/README.md
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
Notas del orador:
- Introduce el ejercicio 03: habrá un repositorio bare llamado origin y dos clones, ana y luis.
- Recalca que origin es una copia nombrada, no “la carpeta central” de Git.

~~~bash
cd ejercicios/03-remotes
bash setup.sh
cd taller-03/ana
git remote -v
git log --oneline
~~~

- Explica que ambos clones tienen historial local y pueden trabajar sin red.

[Sources]
https://git-scm.com/book/en/v2/Getting-Started-About-Version-Control
https://git-scm.com/book/en/v2/Git-Basics-Working-with-Remotes
https://github.com/rafex/IB-git/blob/main/ejercicios/03-remotes/README.md
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
Notas del orador:
- Compara “flujo centralizado” con “naturaleza distribuida”.
- Un equipo puede acordar un único remote principal y aun así cada clon conservar todo el historial.
- Demuestra que el alias puede consultarse y que no es una palabra reservada:

~~~bash
git remote -v
git remote get-url origin
git branch -a
~~~

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
Notas del orador:
- Explica origin, upstream, backup y cliente como nombres de conexiones.
- Muestra que los nombres se pueden consultar, añadir o eliminar sin mover commits.

~~~bash
git remote -v
git remote add backup ../origin.git
git remote -v
git remote remove backup
~~~

- Evita presentar origin como “el servidor”; es sólo el nombre más común para una conexión.

[Sources]
https://git-scm.com/docs/git-remote
https://git-scm.com/book/en/v2/Git-Basics-Working-with-Remotes
https://github.com/rafex/IB-git/blob/main/recursos/cheat-sheet.md
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
Notas del orador:
- Explica los cuatro movimientos con una frase y una demostración:

~~~bash
git clone <url> git-taller
git fetch
git pull
git push
~~~

- clone se usa normalmente una vez para obtener la copia inicial.
- fetch trae referencias y no modifica el archivo de trabajo.
- pull hace fetch y después integra en la rama actual.
- push publica commits locales; no publica cambios que aún no tengan commit.

[Sources]
https://git-scm.com/docs/git-fetch
https://git-scm.com/docs/git-pull
https://git-scm.com/docs/git-push
https://github.com/rafex/IB-git/blob/main/recursos/cheat-sheet.md
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
Notas del orador:
- Presenta el ciclo que queremos convertir en hábito:
  1. traer historial reciente;
  2. hacer una unidad pequeña;
  3. revisar;
  4. crear un commit claro;
  5. compartir.

~~~bash
git pull
git status
# editar agenda.txt
git diff
git add agenda.txt
git commit -m "termina una unidad de trabajo"
git push
~~~

- Aclara que subir con frecuencia no significa publicar trabajo roto: significa compartir unidades revisables y con contexto.

[Sources]
https://git-scm.com/book/en/v2/Git-Basics-Recording-Changes-to-the-Repository
https://git-scm.com/book/en/v2/Git-Basics-Working-with-Remotes
https://github.com/rafex/IB-git/blob/main/GUIA-FACILITADOR.md
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
Notas del orador:
- Introduce el ejercicio 04 y pide predecir el resultado antes de integrar.

~~~bash
cd ejercicios/04-merge-rebase
bash setup.sh
cd taller-04
git log --oneline --graph --all
git status
~~~

- Si las ramas tocaron líneas distintas, Git puede combinar C y D automáticamente.
- Si tocaron la misma zona, Git se detiene y la decisión pasa al equipo.

[Sources]
https://git-scm.com/book/en/v2/Git-Branching-Basic-Branching-and-Merging
https://github.com/rafex/IB-git/blob/main/ejercicios/04-merge-rebase/README.md
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
Notas del orador:
- Parte A del ejercicio 04: merge conserva que hubo dos caminos.

~~~bash
git switch main
git merge feature
git log --oneline --graph --all
~~~

- Señala el commit M y sus dos padres.
- Explica que merge suele ser adecuado cuando quieres conservar el contexto de la integración o cuando la rama ya es compartida.

[Sources]
https://git-scm.com/docs/git-merge
https://git-scm.com/book/en/v2/Git-Branching-Basic-Branching-and-Merging
https://github.com/rafex/IB-git/blob/main/ejercicios/04-merge-rebase/README.md
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
Notas del orador:
- Parte B del ejercicio 04: rebase reaplica los commits de una rama sobre una base nueva.

~~~bash
git switch mi-cambio
git rebase main
git log --oneline --graph --all
~~~

- Explica que el contenido puede ser equivalente, pero cambian los padres y los hashes.
- Regla de seguridad: no hagas rebase de una rama que otras personas ya descargaron.
- Si aparece un conflicto durante rebase:

~~~bash
git status
# editar el archivo y quitar los marcadores
git add agenda.txt
git rebase --continue
~~~

[Sources]
https://git-scm.com/docs/git-rebase
https://git-scm.com/book/en/v2/Git-Branching-Rebasing
https://github.com/rafex/IB-git/blob/main/ejercicios/04-merge-rebase/README.md
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
Notas del orador:
- Usa la tabla para convertir la elección en una pregunta de intención:
  - ¿quiero conservar el encuentro? merge;
  - ¿quiero ordenar mi rama todavía privada? rebase;
  - ¿quiero impedir una integración divergente? ff-only.
- Pide al grupo que formule la política de su equipo antes de memorizar comandos.

[Sources]
https://git-scm.com/book/en/v2/Git-Branching-Rebasing
https://git-scm.com/docs/git-merge
https://github.com/rafex/IB-git/blob/main/ejercicios/04-merge-rebase/README.md
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
Notas del orador:
- Parte C del ejercicio 04: ff-only sólo permite avanzar si no hay dos caminos que reconciliar.

~~~bash
git switch main
git merge --ff-only adelante
git log --oneline --graph --all
~~~

- Para demostrar la barrera, crea divergencia y repite el comando.
- El error es útil: obliga a mirar el historial antes de decidir entre merge o rebase.

[Sources]
https://git-scm.com/docs/git-merge
https://github.com/rafex/IB-git/blob/main/ejercicios/04-merge-rebase/README.md
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
Notas del orador:
- Introduce el ejercicio 05: el conflicto se provoca a propósito para aprender a leerlo.

~~~bash
cd ejercicios/05-conflictos
bash setup.sh
cd taller-05
git log --oneline --graph --all
git diff main ana
git diff main luis
git merge ana
git merge luis
~~~

- Lee los marcadores en orden: HEAD, separador y la rama que se intenta integrar.
- No presentes el conflicto como un error de Git: es una decisión que Git no puede inventar.

[Sources]
https://git-scm.com/book/en/v2/Git-Branching-Basic-Branching-and-Merging
https://github.com/rafex/IB-git/blob/main/ejercicios/05-conflictos/README.md
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
Notas del orador:
- Guiar siempre con el mismo flujo: leer, conversar, editar, comprobar y commit.

~~~bash
git status
# editar acuerdos.txt y quitar <<<<<<<, ======= y >>>>>>>
git diff
git add acuerdos.txt
git status
git commit -m "resuelve conflicto: conserva ambas líneas"
git log --oneline --graph --all
~~~

- La resolución no es borrar marcas sin pensar: hay que decidir qué combinación representa al equipo.
- Si se quiere cancelar la integración:

~~~bash
git merge --abort
~~~

[Sources]
https://git-scm.com/book/en/v2/Git-Tools-Advanced-Merging
https://github.com/rafex/IB-git/blob/main/ejercicios/05-conflictos/README.md
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
Notas del orador:
- Pide que el grupo traduzca la cadena causal a una práctica concreta.
- Pregunta: “¿Qué habría podido ver Ana o Luis si hubieran hecho fetch ayer?”

~~~bash
git fetch
git log --oneline main..origin/main
git diff main origin/main
~~~

- Repite que el conflicto grande del viernes es una señal de coordinación atrasada, no una hazaña técnica.

[Sources]
No hay fuente externa; es un modelo causal didáctico construido a partir del problema descrito por el usuario.
https://github.com/rafex/IB-git/blob/main/GUIA-FACILITADOR.md
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
Notas del orador:
- Contrasta el meme con una jornada saludable: traer, trabajar en pequeño, commit, compartir y volver a traer.
- Ejecuta el flujo en el orden mostrado:

~~~bash
git pull
git status
# editar un archivo de texto
git add archivo.txt
git commit -m "termina una unidad nuclear"
git push
~~~

- Define unidad nuclear: un cambio coherente, revisable y que otra persona puede integrar.
- No esperes al final de la semana para compartir el primer estado.

[Sources]
https://git-scm.com/book/en/v2/Git-Basics-Working-with-Remotes
https://github.com/rafex/IB-git/blob/main/recursos/cheat-sheet.md
https://github.com/rafex/IB-git/blob/main/GUIA-FACILITADOR.md
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
Notas del orador:
- Introduce el ejercicio 06 como integración de todo el curso.

~~~bash
cd ejercicios/06-laboratorio
bash setup.sh
cd taller-06
git log --oneline --graph --all
~~~

- Ronda 1: Ana agrega ensalada, hace commit y push; Luis hace pull.
- Ronda 2: Luis reordena el menú, hace commit y push; Ana hace pull.
- Ronda 3: ambos cambian la misma línea; observa cómo aparece el conflicto.

[Sources]
No hay fuentes externas; ejercicio original para el curso.
https://github.com/rafex/IB-git/blob/main/ejercicios/06-laboratorio/README.md
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
Notas del orador:
- Cierra con una lista que el participante pueda repetir en voz alta.
- Comandos mínimos para llevarse:

~~~bash
git pull
git status
git add archivo.txt
git commit -m "mensaje claro"
git push
git log --oneline --graph --all
~~~

- Añade la regla de integración: merge conserva contexto, rebase ordena trabajo no compartido y ff-only impide avanzar a ciegas.
- Invita a consultar recursos/cheat-sheet.md del repositorio IB-git.

[Sources]
https://git-scm.com/book/en/v2/Git-Branching-Branching-Workflows
https://git-scm.com/book/en/v2/Git-Basics-Working-with-Remotes
https://github.com/rafex/IB-git/blob/main/recursos/cheat-sheet.md
-->

---
layout: statement
class: final-slide
---

# El mejor historial es el que el equipo puede entender mañana.

<div class="final-subtitle">Pequeño · frecuente · explícito · compartido</div>

<!--
Notas del orador:
- Haz una pausa después de la frase final y pide una respuesta: “¿qué hábito vas a cambiar mañana?”
- Reafirma: commits pequeños, frecuentes, explícitos y compartidos.
- Comparte el repositorio para continuar con los seis ejercicios:
  https://github.com/rafex/IB-git

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
Notas del orador:
- Invita a clonar el repositorio y practicar el ejercicio que corresponda a la duda de cada persona.
- Sugiere empezar por ejercicios/01-commits y avanzar hasta ejercicios/06-laboratorio.
- Deja visible el enlace al repositorio y ofrece continuar la conversación después del curso.

Enlace de práctica:
https://github.com/rafex/IB-git

[Sources]
Datos de contacto del autor, siguiendo la diapositiva de contacto de Boost Desarrollo.
https://github.com/rafex/IB-git
-->
