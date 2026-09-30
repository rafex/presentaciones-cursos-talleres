# Cronograma — galaxIA: de una idea a una red

**Duración total:** 45 minutos (35 de charla + 10 de preguntas)
**Público:** técnico y estudiantes
**Formato:** charla con Slidev (`slidev/slides.md`), 36 slides + 7 de respaldo
**Hora de inicio:** ajustable; abajo se usa 10:00 como referencia

## Antes de presentar

- Encender el laboratorio completo (Bastion, Raspberry Pi 4B, Raspberry Pi 3B y
  ThinkPad) y correr `scripts/doctor.sh <url-del-portal>` (repo `galaxIA-gitops`).
- Actualizar la slide **«Lo que funciona hoy»** (slide 25) con lo que muestre
  el diagnóstico: hoy dice que el 30 de septiembre solo respondían el router y
  Bastion.
- Las cifras marcadas «Snapshot 27–28 sep 2026» son del laboratorio completo;
  si cambian, corregir la etiqueta y la cifra.
- Demo en vivo **opcional**, máximo 2 minutos, en la slide 16 («Una misión de
  punta a punta»). Si el laboratorio falla, seguir con el diagrama.

## 10:00 — Portada y ruta (2 min) · slides 1-2

Presentar el objetivo: por qué nació galaxIA, cómo cambió desde la primera
charla del 3 de julio de 2026, qué falta y cómo sumarse.

## 10:02 — Acto 1: Por qué nació y de dónde partimos (9 min) · slides 3-11

- La IA útil se concentró; hay hardware guardado que nadie usa; la pregunta.
- Principios y vocabulario (Star, Satellite, Nova, Atlas, Navigator, Beacon).
- La primera charla: 3 equipos, Registry central, JSON sobre WebSocket.
- Las cuatro promesas de «Qué sigue» (se revisan en el Acto 2).

## 10:11 — Acto 2: Cómo cambió (12 min) · slides 12-23

- Línea de tiempo del 30 de junio a hoy.
- Red sin centro, tabla antes/después y una misión de punta a punta.
- El laboratorio: hardware, puertos, versiones desplegadas.
- La migración a Rust (una métrica), el modelo y los adjuntos por IPFS.
- ¿Cumplimos lo prometido?

## 10:23 — Acto 3: Dónde estamos y qué falta (7 min) · slides 24-30

Lo que funciona hoy y cinco retos: confianza y reputación, privacidad,
disponibilidad y hardware modesto, abrir la red, y que otras personas puedan
entrar.

## 10:30 — Cómo sumarte (5 min) · slides 31-34

Cinco caminos, primer paso (contribuir o armar tu laboratorio) y dónde
encontrarnos.

## 10:35 — Cierre y preguntas (10 min) · slides 35-36

Cierre, contacto y preguntas. Dejar a la vista **«Dónde encontrarnos»**
(slide 34). Las slides de respaldo (37-43) se usan solo si preguntan por
mediciones, modelos, lecciones de las pruebas, la pila P2P, las decisiones o
la configuración de IPFS.
