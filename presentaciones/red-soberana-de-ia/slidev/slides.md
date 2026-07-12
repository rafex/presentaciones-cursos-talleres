---
theme: seriph
title: Red soberana e IA local
transition: slide-left
mdc: true
layout: cover
background: /images/bg-portada-soberania.png
class: cover-slide
---

# Red soberana e IA local

Reutilizando equipos antiguos con software libre

<small>Spike Slidev · compatible con el repositorio Marp actual</small>

<!--
  Nota del presentador: este piloto conserva el tema narrativo de la charla
  actual, pero prueba una portada CSS y assets compartidos sin tocar el deck
  Marp original.
-->

---
layout: two-cols
---

# Arquitectura

<v-clicks>

- Nodos locales con hardware reutilizado
- Modelos pequeños cerca de los datos
- Comunicación soberana entre capacidades

</v-clicks>

::right::

<img :src="'./images/modelo-soberana.svg'" class="architecture-image" alt="Red soberana federada" />

<!-- Nota: el layout two-cols y v-clicks son capacidades nativas de Slidev. -->

---

# Un mensaje, varios nodos

```mermaid
%%{init: {"theme": "base", "themeVariables": {"background": "#ffffff", "primaryColor": "#e7f0fb", "primaryBorderColor": "#0b5fae", "primaryTextColor": "#14181c", "lineColor": "#0b5fae"}}}%%
graph TD
  Portal[Portal local] --> Nova[Nova · coordinación]
  Nova --> Star[Star · modelo local]
  Nova --> Satellite[Satellite · OCR]
```

La presentación sigue siendo Markdown versionable; Vue, CSS y demos pueden
entrar sólo donde aporten valor.

<!--
  Nota del presentador: este es el umbral de adopción propuesto. Lo nuevo
  puede aprovechar Mermaid, transiciones y componentes, mientras la fuente
  Marp y su release siguen intactas.
-->

<style>
:root {
  --slidev-theme-primary: #0b5fae;
}

.cover-slide {
  color: white;
  text-shadow: 0 2px 14px rgba(0, 0, 0, 0.7);
}

.cover-slide h1,
.cover-slide p,
.cover-slide small {
  color: white;
  position: relative;
  z-index: 1;
}

.cover-slide h1 {
  max-width: 75%;
  text-align: center;
  font-size: 3.1rem;
  line-height: 1.08;
}

.cover-slide p,
.cover-slide small {
  display: block;
  text-align: center;
}

.cover-slide p {
  font-size: 1.45rem;
}

.cover-slide small {
  color: rgba(255, 255, 255, 0.82);
}

.architecture-image {
  display: block;
  max-height: 65%;
  max-width: 100%;
  margin: 2rem auto;
}
</style>
