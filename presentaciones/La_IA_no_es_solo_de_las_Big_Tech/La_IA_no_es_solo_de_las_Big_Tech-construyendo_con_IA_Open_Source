---
marp: true
theme: default
paginate: true
size: 16:9
format: pdf

title: La IA no es solo de las Big Tech
description: Construyendo una PoC funcional con OpenWrt, Raspberry Pi e IA Open Source
header: La IA no es solo de las Big Tech
author: Raúl Eduardo González Argote by rafex@rafex.dev
date: 25 abril 2026
---

![width:620px bg](assets/images/QR.png)

---

# La IA no es solo de las Big Tech
## Construyendo con IA Open Source

- PoC real con hardware accesible
- Router OpenWrt + 3 Raspberry Pi
- Captura de red, análisis local con LLM y dashboard

Repositorio de la charla:
<https://github.com/rafex/presentaciones-cursos-talleres/tree/main/presentaciones/La_IA_no_es_solo_de_las_Big_Tech>

---

## Mensaje central

> No necesitas nube propietaria ni infraestructura millonaria para crear soluciones útiles con IA.

- Puedes construir con software libre
- Puedes ejecutar IA local
- Puedes aprender y enseñar con evidencia práctica

---

## Objetivo de la PoC

Demostrar en un entorno real:

1. Red WiFi abierta en OpenWrt
2. Detección y observabilidad de tráfico en tiempo real
3. Análisis automatizado de riesgo con un LLM local
4. Visualización para demo educativa de ciberseguridad

---

## Arquitectura general

```text
Internet (opcional)
        |
Router OpenWrt (AP + captive + nftables)
        |
        +--> Raspberry Pi 3B #1 (sensor: tshark + agregación)
        |
        +--> Raspberry Pi 4B (k3s + MQTT + llama.cpp + analyzer + dashboard)
        |
        +--> Raspberry Pi 3B #2 (portal cautivo opcional / split topology)
```

---

## Stack 100% Open Source

| Capa | Tecnología |
|---|---|
| Router/AP | OpenWrt 25.x + dnsmasq + nftables |
| Captura de tráfico | tshark / tcpdump |
| Transporte de eventos | MQTT (Mosquitto) |
| Inferencia IA local | llama.cpp + TinyLlama 1.1B Q4 |
| Backend de análisis | Python |
| Orquestación | k3s |
| UI | HTML + endpoints Flask |

---

## Flujo de datos

1. `sensor.py` agrupa tráfico cada 30 segundos
2. Publica batch a `rafexpi/sensor/batch` (MQTT)
3. `ai-analyzer` consume, encola y persiste en SQLite
4. Genera prompt contextual y consulta `llama-server`
5. Clasifica riesgo (`BAJO`, `MEDIO`, `ALTO`)
6. Expone resultados en dashboard y stream en vivo

---

## Lo que demuestra esta PoC

- IA útil en edge computing
- Seguridad de red explicada de forma didáctica
- Integración de hardware viejo + software moderno
- Independencia tecnológica con herramientas abiertas

---

## Demo en vivo (guion)

1. Levantar WiFi abierta en OpenWrt
2. Pedir al público conectarse
3. Mostrar nuevos dispositivos y patrones de tráfico
4. Ejecutar análisis IA local frente a la audiencia
5. Mostrar alertas y recomendaciones en dashboard

Resultado esperado: entender el riesgo real de una red pública en minutos.

---

## Aprendizajes técnicos

- El valor está en integrar piezas, no en usar una sola herramienta
- El diseño de prompts importa incluso en modelos pequeños
- `nftables` + captive portal da control fino para demos de seguridad
- La observabilidad (logs, colas, estado) evita demos frágiles

---

## Retos y límites reales

- CPU/RAM limitadas en Raspberry Pi
- Latencia de inferencia local (segundos por batch)
- Curva de operación en OpenWrt y networking
- Seguridad y ética: no exponer datos sensibles en demos

---

## Próximos pasos

1. Mejorar scoring de riesgo por tipo de evento
2. Añadir más fuentes (`arp-scan`, `nmap`) por ventana controlada
3. Afinar topología split para más resiliencia
4. Publicar guía reproducible para talleres comunitarios

---

# Conclusión

La IA también se construye desde la comunidad.

- Software libre
- Hardware accesible
- Conocimiento compartido

Escanea el QR para revisar el material y replicar la PoC.

![bg right:32% width:350px](assets/images/QR.png)
