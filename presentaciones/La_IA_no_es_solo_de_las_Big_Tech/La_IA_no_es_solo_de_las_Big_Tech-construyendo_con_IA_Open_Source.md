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

Repositorio de la charla:
<https://github.com/rafex/presentaciones-cursos-talleres/tree/main/presentaciones/La_IA_no_es_solo_de_las_Big_Tech>

---

## Cómo empezó todo

Cuando estaba en primaria tuve mi primer contacto con **Linux**.

Mi papá trabajaba en un lugar donde usaban:

- **SUSE**

- **Linux PPP**

- **Red Hat**

Ahí me enseñaron algo que para mí parecía magia:

- particiones de disco

- instalación de sistemas

- cómo arrancar Linux

En una máquina usada logré instalar **Red Hat**.

Pero pasó algo curioso.

No supe **qué hacer con él**.

Así que terminé regresando a **Windows**.

Sin embargo, la curiosidad **ya estaba sembrada**.

![bg right:50%](assets/images/rafex_nino.jpeg)

---

## La decisión

Cuando entré a la universidad tomé una decisión muy simple:

> Voy a aprender Linux **sí o sí**.

Incluso si eso significaba:

- tardar más en hacer tareas

- romper cosas

- reinstalar el sistema varias veces

Primero probé:

- **Ubuntu 7.x u 8.x** (no recuerdo exactamente)

Funcionaba bien, pero lo sentía **pesado**.

Así que decidí probar algo más desafiante.

Me cambié a **Debian Sarge**.

Lo odié… por un tiempo.

Cada reinicio pasaba algo:

- el **audio se desconfiguraba**

- algo dejaba de funcionar

Pero cada uno de esos problemas me obligaba a **entender el sistema**.

---

## El momento en que entendí Linux

Hubo un momento que cambió todo.

Cuando **compilé mi primer kernel**.

Fueron noches sin dormir:

- prueba

- error

- recompilar

- volver a probar

Recuerdo activar funcionalidades que aún no estaban en la línea base.

Como **cgroups**.

En ese momento pensé:

> "Esto es increíble."

Estaba construyendo mi propio sistema.

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
