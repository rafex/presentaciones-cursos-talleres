---
marp: true
theme: default
paginate: true
size: 16:9
format: pdf

title: La IA no es solo de las Big Tech: construyendo con IA Open Source
description: Hay pocas tecnologías que se logran proliferar tan rápido como la IA, pero ¿es necesario depender de la nube y las Big Tech para crear soluciones útiles? En esta charla se presenta una prueba de concepto real que demuestra cómo construir con IA Open Source usando hardware accesible. Con un router OpenWrt y dos Raspberry Pi, se captura el tráfico de una red WiFi abierta, se analiza localmente con un LLM y se muestra en un dashboard educativo. El mensaje central es claro: no necesitas infraestructura millonaria para crear soluciones útiles con IA.
header: La IA no es solo de las Big Tech: construyendo con IA Open Source
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

## Repositorio analizado

La PoC vive en:

<https://github.com/rafex/poc-openwrt-dietpi-raspi3b-raspi4b>

Estructura principal:

| Directorio | Responsabilidad |
|---|---|
| `scripts/` | Instalación, health checks, cambios de topología |
| `sensor/` | Captura y agregación de tráfico desde Pi 3B |
| `backend/` | Portal cautivo y analizador IA |
| `k8s/` | Manifiestos para k3s, Traefik, servicios e ingress |
| `docs/` | Arquitectura, setup, LLM, portales y software libre |

---

## Arquitectura general

![width:1050px](assets/images/arquitectura-general.svg)

<!-- notes: Explicar que el router no solo da red: también aplica la política de acceso. La Pi 3B observa, la Pi 4B razona y sirve la UI, y la tercera Pi permite separar el portal en una topología más limpia. -->

---

## Responsabilidades por nodo

| Nodo | Qué hace |
|---|---|
| OpenWrt | AP WiFi, DHCP, DNS captive, reglas `nftables`, allowlist |
| Pi 3B sensor | `tshark`, agregación cada 30s, enriquecimiento con datos del router |
| Pi 4B IA | Mosquitto, `llama-server`, k3s, `ai-analyzer`, SQLite, dashboard |
| Pi 3B portal | Portal cautivo opcional en topología `split_portal` |

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

## Software libre como sistema

![width:980px](assets/images/software-libre-stack.svg)

<!-- notes: Este slide conecta la charla con software libre: no es una lista aislada de tecnologías, es una cadena completa de piezas abiertas colaborando. -->

---

## Flujo captive portal

![width:960px](assets/images/flujo-captive.svg)

<!-- notes: Poner énfasis en que OpenWrt decide el acceso con nftables. El portal no es solo una página, es el punto donde el backend registra y autoriza temporalmente al cliente. -->

---

## Flujo de datos

![width:980px](assets/images/flujo-ia.svg)

<!-- notes: Explicar que el LLM no ve paquetes crudos. Recibe una síntesis: top emisores, puertos, DNS, HTTP hosts, conexiones y anomalías. Eso reduce costo y hace viable correr en Raspberry. -->

---

## Cómo piensa el analizador

1. `sensor.py` genera un resumen de red, no un volcado completo
2. `ai-analyzer` lo guarda como batch pendiente
3. Un worker procesa un batch a la vez para no saturar la Pi 4B
4. El prompt pide tres puntos breves y un riesgo: `BAJO`, `MEDIO`, `ALTO`
5. El resultado queda consultable por dashboard, historial y stream SSE

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

## Por qué Mermaid pre-renderizado

Para esta presentación conviene convertir Mermaid a SVG antes de exportar:

- Marp PDF no depende de JavaScript en tiempo de render
- El diagrama queda versionado junto al markdown
- El resultado es reproducible en PDF, HTML y ODP

Flujo usado:

```bash
mmdc -i assets/diagrams/arquitectura-general.mmd -o assets/images/arquitectura-general.svg
```

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
