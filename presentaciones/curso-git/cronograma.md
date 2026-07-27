# Cronograma — Git para colaborar

**Duración total:** 1 hora 30 minutos  
**Modalidad:** explicación breve + práctica guiada  
**Repositorio:** <https://github.com/rafex/IB-git>  
**Cierre:** 15 minutos para dudas y preguntas

## Preparación previa

Estos pasos se realizan antes de iniciar el cronograma o mientras las personas
se conectan. No forman parte de los 90 minutos del curso.

```bash
git clone https://github.com/rafex/IB-git.git git-taller
cd git-taller
bash setup-global.sh
git --version
```

Cada participante debe tener Git instalado, una terminal y un editor de texto.

## 09:00 — Bienvenida y contexto

Presentar el objetivo del curso y plantear el mito del “push del viernes”. Git
sirve para colaborar mediante un historial de decisiones, no para compartir una
carpeta sin control.

- **Facilitación:** explicar la dinámica y recoger experiencias breves.
- **Participantes:** preparar el repositorio y compartir cómo trabajan hoy.

## 09:05 — Modelo mental de Git

Explicar working tree, staging area, repositorio local, remote, commits y ramas.
Mostrar que Git guarda instantáneas y que cada clon conserva su propio historial.

- **Facilitación:** dibujar el flujo entre archivo, staging, repositorio local y remotes.
- **Participantes:** predecir qué ocurre al editar, preparar y confirmar un archivo.

## 09:15 — Ejercicio 01: commits

Demostrar `git status`, `git add`, `git commit`, `git log` y `git show` usando
los estados de `agenda.txt`.

1. Ejecutar los tres commits A, B y C.
2. Revisar el historial.
3. Comprobar qué cambió en cada commit.

## 09:25 — Ejercicio 02: ramas

Explicar que una rama es un marcador y mostrar `git branch`, `git switch` y el
grafo de commits.

1. Crear la rama `ana`.
2. Modificar `agenda.txt` y confirmar el cambio.
3. Comparar `ana` contra `main`.

## 09:35 — Ejercicio 03: remotes

Explicar `clone`, `fetch`, `pull` y `push`. Comparar `origin` con un alias y
mostrar la colaboración entre repositorios.

1. Simular Ana → `push` → Luis → `fetch/pull` → `push` → Ana.
2. Observar cuándo cambia el archivo.
3. Identificar qué historial existe localmente y cuál está publicado.

## 09:45 — Ejercicio 04: integración

Explicar cuándo usar `merge`, `rebase` y `git merge --ff-only`. Mostrar los
tres grafos y la regla de no rebasar ramas compartidas.

1. Ejecutar una integración con `merge`.
2. Ejecutar otra con `rebase`.
3. Comprobar el comportamiento de `ff-only`.

## 09:55 — Ejercicio 05: conflictos

Provocar un conflicto en `acuerdos.txt` y explicar que Git no puede tomar por
las personas la decisión sobre qué texto conservar.

1. Leer los marcadores del conflicto.
2. Conversar y editar el archivo.
3. Comprobar, ejecutar `add` y confirmar.
4. Probar `git merge --abort` como alternativa.

## 10:05 — Ejercicio 06: laboratorio

Integrar todo en un escenario de colaboración con `menu.txt`. Reforzar commits
pequeños, `pull` al iniciar y `push` al terminar.

1. Agregar una sección.
2. Reordenar el contenido.
3. Resolver un conflicto real.

## 10:15 — Dudas y preguntas

Recapitular las ideas clave y abrir la ronda final de 15 minutos. Usar el
historial de los ejercicios para responder casos concretos.

- **Facilitación:** responder preguntas y conectar cada respuesta con una práctica colaborativa.
- **Participantes:** compartir dificultades y explicar qué práctica aplicarán en su equipo.

## Ritmo recomendado para cada bloque práctico

En los bloques de ejercicios, mantener este patrón para que la práctica ocurra
mientras se explica:

1. **2 minutos:** explicar el objetivo y mostrar el resultado esperado.
2. **5 minutos:** las personas ejecutan los comandos y editan el archivo.
3. **2 minutos:** revisar el historial o comparar resultados.
4. **1 minuto:** conectar el ejercicio con la siguiente idea.

Si el grupo necesita más tiempo, reducir la demostración siguiente y mantener
la práctica. El objetivo es que cada persona vea el cambio en su propio
repositorio.

## Comandos guía por etapa

### Commits

```bash
git status
git add agenda.txt
git commit -m "mensaje claro"
git log --oneline
git show HEAD
```

### Ramas

```bash
git branch
git switch -c ana
git switch main
git log --oneline --graph --all
```

### Remotes

```bash
git remote -v
git fetch
git pull
git push
```

### Integración

```bash
git merge feature
git rebase main
git merge --ff-only origin/main
```

### Conflictos

```bash
git status
git diff
git add acuerdos.txt
git commit -m "resuelve conflicto"
git merge --abort
```

## Mensajes clave para cerrar

- Git no es una carpeta compartida: es un historial distribuido de decisiones.
- `fetch` trae información; `pull` trae e integra; `push` publica commits.
- `merge` conserva contexto; `rebase` ordena trabajo no compartido; `ff-only`
  evita integrar a ciegas.
- Los conflictos se resuelven conversando una decisión, no borrando marcas.
- Los commits pequeños y frecuentes mantienen el historial fresco y facilitan
  el auto-merge.

## Referencias para continuar

- [README del curso](https://github.com/rafex/IB-git)
- [Guía del facilitador](https://github.com/rafex/IB-git/blob/main/GUIA-FACILITADOR.md)
- [Cheat sheet de comandos](https://github.com/rafex/IB-git/blob/main/recursos/cheat-sheet.md)
- [Modelo mental de Git](https://github.com/rafex/IB-git/blob/main/recursos/modelo-mental.md)
