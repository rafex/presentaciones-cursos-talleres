---
marp: true
theme: default
paginate: true
size: 16:9
format: pdf

title: Cómo crear tu propio agente de IA usando solo software libre
description: Taller práctico para construir un agente de IA con herramientas Open Source.
header: Cómo crear tu propio agente de IA usando solo software libre
footer: Raúl González - @rafex
author: Raúl Eduardo González Argote by rafex@rafex.dev
date: 24 junio 2026
---

<!--
Taller: 10:00 - 13:00
Foro de Tecnologías de la Información y Software Libre 2026
Universidad Politécnica de Tlaxcala
Objetivo: que cada asistente entienda y construya un agente funcional con software libre.
-->

# Cómo crear tu propio agente de IA

## usando solo software libre

Raúl Eduardo González Argote

---

## Resultado del taller

Al final tendrás un agente que puede:

* Recibir una tarea
* Razonar un plan corto
* Usar herramientas
* Consultar información local
* Entregar una respuesta verificable

---

## La regla del taller

No venimos a mirar IA.

Venimos a construir con IA.

---

## Stack propuesto

* Linux, macOS o Windows con WSL
* Python
* Ollama
* Modelo abierto
* LangGraph
* MCP
* Git

<!-- notes:
Si el laboratorio no soporta instalación previa, llevar alternativa con entorno prearmado o demo centralizada.
-->

---

## Requisitos técnicos

Antes del taller:

* Laptop
* Git instalado
* Python 3.11+
* Editor de código
* Docker opcional
* Internet estable

---

## Instalación base

```bash
git --version
python3 --version
ollama --version
```

---

## Agenda

* 10:00 - 10:20 | Qué es un agente
* 10:20 - 10:45 | Ambiente y modelo local
* 10:45 - 11:20 | Primer agente
* 11:20 - 12:00 | Herramientas
* 12:00 - 12:35 | Memoria y datos
* 12:35 - 13:00 | Demo final y cierre

---

## 1. Qué es un agente

Un agente no es un chatbot.

Un agente tiene objetivo, herramientas y ciclo de decisión.

---

## Ciclo básico

Usuario

↓

Objetivo

↓

Plan

↓

Herramientas

↓

Respuesta

---

## 2. Modelo local

Primero probamos que la IA responda localmente.

```bash
ollama run llama3.2
```

---

## Ejercicio 1

Pide al modelo:

> Explica qué es un agente de IA usando una analogía para estudiantes de TI.

---

## 3. Primer agente

Objetivo:

Construir un programa que reciba una tarea y devuelva una respuesta estructurada.

---

## Prompt base

```text
Eres un agente técnico.
Tu tarea es ayudar a resolver problemas de desarrollo.
Responde con:
1. Diagnóstico
2. Plan
3. Riesgos
4. Siguiente acción
```

---

## 4. Herramientas

Un agente se vuelve útil cuando puede hacer cosas.

Ejemplos:

* Leer archivos
* Buscar texto
* Ejecutar pruebas
* Consultar una API
* Validar datos

---

## Ejercicio 2

Crear una herramienta:

```text
buscar_en_archivos(query)
```

Debe regresar coincidencias de una carpeta local.

---

## 5. Datos locales

La IA sin datos propios responde generalidades.

Con datos locales puede resolver problemas concretos.

---

## Ejercicio 3

Crear una mini base de conocimiento:

* `docs/reglas.md`
* `docs/proyecto.md`
* `docs/preguntas.md`

El agente debe responder usando esos archivos.

---

## 6. MCP

MCP permite conectar agentes con herramientas de forma estandarizada.

La idea importante:

Modelos diferentes.

Herramientas reutilizables.

---

## Demo guiada

Agente técnico para revisar un proyecto:

* Lee archivos
* Resume estructura
* Detecta riesgos
* Sugiere próximos pasos

---

## Producto final

Cada equipo entrega:

* Repositorio local
* Agente ejecutable
* Una herramienta propia
* Tres documentos de conocimiento
* Demo de una consulta real

---

## Rúbrica rápida

Funciona.

Usa software libre.

Explica sus decisiones.

Se puede mejorar.

---

## Retos extra

* Agregar memoria
* Agregar una API
* Agregar Docker
* Agregar interfaz web
* Cambiar de modelo local

---

## Cierre

No necesitas permiso para empezar.

Necesitas curiosidad, criterio y práctica.

---

## Siguiente paso

Publica tu agente.

Explícalo.

Compártelo.

Mejóralo.
