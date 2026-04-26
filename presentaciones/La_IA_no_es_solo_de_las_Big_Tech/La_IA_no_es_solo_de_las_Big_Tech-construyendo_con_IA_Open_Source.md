---
marp: true
theme: default
paginate: true
size: 16:9
format: pdf

title: La IA no es solo de las Big Tech - construyendo con IA Open Source
description: Hay pocas tecnologías que se logran proliferar tan rápido como la IA
header: La IA no es solo de las Big Tech - construyendo con IA Open Source
author: Raúl Eduardo González Argote by rafex@rafex.dev
date: 25 abril 2026
---

![width:620px bg](assets/images/QR.png)

---

![width:1080x](assets/images/7163eb05b9e3edf653af967022b64221a41cc708c8394ddcf01662955c76e6b1.png)

---

## ¿Cómo empezó todo?

Cuando estaba en primaria tuve mi primer contacto con **Linux**.

Mi papá trabajaba en un lugar donde usaban:

- **SUSE**

- **Linux PPP**

- **Red Hat**

<!-- notes:
Ahí me enseñaron algo que para mí parecía magia:

- particiones de disco

- instalación de sistemas

- cómo arrancar Linux

En una máquina usada logré instalar **Red Hat**.

Pero pasó algo curioso.

No supe **qué hacer con él**.

Así que terminé regresando a **Windows**.

-->

La curiosidad **ya estaba sembrada**.

![bg right:50%](assets/images/rafex_nino.jpeg)

---

Cuando entré a la universidad tomé una decisión muy simple:

> Voy a aprender Linux **sí o sí**.

Incluso si eso significaba:

- tardar más en hacer tareas

- romper cosas

- reinstalar el sistema varias veces

<!-- notes:

Primero probé:

- **Ubuntu 7.x u 8.x** (no recuerdo exactamente)

Funcionaba bien, pero lo sentía **pesado**.

Así que decidí probar algo más desafiante.

Me cambié a **Debian Sarge**.

Lo odié… por un tiempo.

Cada reinicio pasaba algo:

- el **audio se desconfiguraba**

- algo dejaba de funcionar

-->

Pero cada uno de esos problemas me obligaba a **entender el sistema**.

![bg left:50%](assets/images/4343d7d516e5ae3ff8f3a98dc1a7bd31ee159b94e842bd9e2950e08de307a190.png)

---

Hubo un momento que cambió todo.

Cuando **compilé mi primer kernel**.

Fueron noches sin dormir:
- prueba
- error
- recompilar


<!-- notes:
Recuerdo activar funcionalidades que aún no estaban en la línea base.

Como **cgroups**.
-->

En ese momento pensé:

> "Esto es increíble."

Estaba construyendo mi propio sistema.

![bg right:50%](assets/images/baac5797cc9c8d269efb0ba42d8a88ae775e9fd9e2af90de9af5fa8c6db7c773.png)

---

## Por eso esta charla existe

Linux y yo tenemos historia.

Y esa historia me enseñó algo importante:

El poder del **software libre** es que te permite **entender cómo funcionan las cosas**.

No solo usarlas.

Y hoy estamos viendo algo muy parecido con la **IA**.

La pregunta es:

> ¿Tenemos que depender de la nube y de las Big Tech para usar IA?

¿O podemos **entenderla, ejecutarla y construir con ella nosotros mismos**?

Ahí es donde entra esta **PoC**.

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

## ¿Qué es OpenWrt?

[**OpenWrt**](https://openwrt.org/) es un sistema operativo Linux para routers y dispositivos de red.

A diferencia del firmware propietario que traen la mayoría de los routers:

- es **software libre**
- permite **control total del dispositivo**
- se pueden instalar paquetes como en una distribución Linux

En esta PoC OpenWrt se usa para:

- crear la **red WiFi abierta**
- manejar **DHCP y DNS**
- implementar el **captive portal**
- aplicar reglas de red con **nftables**

<!-- notes:
OpenWrt convierte un router común en un pequeño servidor Linux.
Esto permite instrumentar la red y crear demos educativas de seguridad.
-->

---

## ¿Qué es llama.cpp?

**llama.cpp** es un proyecto open source que permite ejecutar modelos de lenguaje (LLM)
**de forma local**.

Características importantes:

- escrito en **C/C++ altamente optimizado**
- puede ejecutarse en **CPU sin GPU**
- soporta cuantización para reducir memoria

En esta PoC se utiliza para:

- ejecutar un **modelo pequeño (TinyLlama)**
- analizar eventos de red
- generar explicaciones de riesgo

Esto permite tener **IA local en hardware muy pequeño**.

<!-- notes:
La clave es que no estamos llamando a una API externa.
La inferencia ocurre dentro de la Raspberry Pi.
-->

---

## ¿Qué es una Raspberry Pi?

Una **Raspberry Pi** es una computadora de bajo costo del tamaño de una tarjeta de crédito.

Características generales:

- CPU ARM
- bajo consumo eléctrico
- almacenamiento en microSD
- ejecuta distribuciones Linux

Es muy utilizada para:

- educación
- IoT
- prototipos
- laboratorios de redes

En esta PoC se utilizan varias Raspberry Pi para separar responsabilidades del sistema.

---

## Hardware utilizado en la PoC

### Raspberry Pi 3B (sensor)

- CPU: Broadcom BCM2837 Quad‑Core 1.2 GHz
- RAM: 1 GB
- Ethernet 100 Mbps
- WiFi 2.4 GHz

Responsabilidad:

- capturar tráfico de red
- generar resúmenes de actividad
- enviar eventos al backend

---

### Raspberry Pi 3B (portal cautivo)

- CPU: Broadcom BCM2837 Quad-Core 1.2 GHz
- RAM: 1 GB
- Ethernet 100 Mbps
- WiFi 2.4 GHz

Responsabilidad:

- servir el **portal cautivo**
- mostrar la página de acceso a la red
- registrar la aceptación del usuario
- controlar el flujo inicial del usuario en la red

---

### Raspberry Pi 4B (IA y backend)

- CPU: Quad‑Core Cortex‑A72
- RAM: 4 GB
- Ethernet Gigabit
- USB 3.0

Responsabilidad:

- ejecutar **llama.cpp**
- correr **k3s**
- almacenar eventos
- servir el **dashboard**

<!-- notes:
Separar el sensor de la inferencia evita que la captura de red afecte el análisis IA.
Esto también permite escalar el sistema si se desea.
-->

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
