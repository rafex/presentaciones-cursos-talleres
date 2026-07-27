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

## Agenda de 90 minutos

| Tiempo | Duración | Bloque | Qué explica la persona facilitadora | Qué hacen las personas participantes |
|---|---:|---|---|---|
| 00:00–00:05 | 5 min | Bienvenida y contexto | Presentar el objetivo. Plantear el mito del “push del viernes” y explicar que Git sirve para colaborar mediante historial. | Compartir experiencias breves y preparar el repositorio. |
| 00:05–00:15 | 10 min | Modelo mental de Git | Explicar working tree, staging area, repositorio local, remote, commits y ramas. Mostrar que Git guarda instantáneas, no una carpeta compartida. | Observar el flujo y predecir qué ocurre al editar, preparar y confirmar un archivo. |
| 00:15–00:25 | 10 min | Ejercicio 01: commits | Demostrar `git status`, `git add`, `git commit`, `git log` y `git show`. Relacionar cada commit con un estado de `agenda.txt`. | Ejecutar los tres commits A, B y C y comprobar el historial. |
| 00:25–00:35 | 10 min | Ejercicio 02: ramas | Explicar que una rama es un marcador. Mostrar `git branch`, `git switch` y el grafo de commits. | Crear la rama `ana`, modificar `agenda.txt`, confirmar el cambio y comparar `ana` contra `main`. |
| 00:35–00:45 | 10 min | Ejercicio 03: remotes | Explicar `clone`, `fetch`, `pull` y `push`. Comparar `origin` con un alias y mostrar que cada clon conserva el historial. | Simular Ana → `push` → Luis → `fetch/pull` → `push` → Ana. Observar cuándo cambia el archivo. |
| 00:45–00:55 | 10 min | Ejercicio 04: integración | Explicar cuándo usar `merge`, `rebase` y `git merge --ff-only`. Mostrar los tres grafos y la regla de no rebasar ramas compartidas. | Ejecutar una integración con `merge`, otra con `rebase` y comprobar el comportamiento de `ff-only`. |
| 00:55–01:05 | 10 min | Ejercicio 05: conflictos | Provocar un conflicto en `acuerdos.txt`. Leer los marcadores y explicar que Git no puede tomar la decisión humana. | Seguir el flujo: leer → conversar → editar → comprobar → `add` → `commit`. Probar `git merge --abort` como alternativa. |
| 01:05–01:15 | 10 min | Ejercicio 06: laboratorio | Integrar todo en un escenario de colaboración con `menu.txt`. Reforzar commits pequeños, `pull` al iniciar y `push` al terminar. | Completar las tres rondas: agregar, reordenar y resolver un conflicto real. |
| 01:15–01:30 | 15 min | Dudas y preguntas | Recapitular las ideas clave y abrir la ronda final. Usar el historial de los ejercicios para responder casos concretos. | Formular preguntas, compartir dificultades y explicar qué práctica aplicarán en su equipo. |

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
