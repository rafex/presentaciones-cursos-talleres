# Prompt para IDE con IA (Cursor o Void Editor):

---

En la carpeta: `proyecto-taller-upt/`: 
Crea un proyecto de red social sencilla tipo Twitter con scroll infinito. El frontend debe usar HTML, CSS y JavaScript puro; el backend debe implementarse en Python o Java sin frameworks, proporcionando una API REST con un endpoint GET `/messages` para obtener todos los mensajes y POST `/messages` para enviar nuevos mensajes; utiliza SQLite como base de datos; empaqueta todo en contenedores Docker mediante Dockerfile; configura un chart de Helm para desplegarlo en Kubernetes. El taller durará 1 hora y 30 minutos y será práctico, asegurando que los participantes puedan levantar el entorno en Docker y Kubernetes con Helm. Incluye instrucciones paso a paso y ejemplos de código mínimos.

Crear un archivo `README.md` que contenga: 
# Taller ¿IA tú sabes?
## Descripción del taller
En este taller práctico, los participantes aprenderán a crear una aplicación sencilla tipo red social con scroll infinito utilizando tecnologías web básicas y contenedores Docker. El stack tecnológico incluye un frontend con HTML, CSS y JavaScript puro, un backend en Python o Java sin frameworks, una base de datos SQLite, y un despliegue en Kubernetes utilizando Helm. El objetivo es que los participantes puedan levantar el entorno en sus máquinas y llevarse un entregable funcional al finalizar el taller.   

## Objetivos del taller
1. **Familiarizarse con el uso de IA** para generar código y acelerar el desarrollo.
2. **Crear un frontend básico** con HTML, CSS y JavaScript puro.
3. **Implementar un backend sencillo** en Python o Java sin frameworks, con una API REST.
4. **Configurar una base de datos SQLite** para persistencia de datos.
5. **Utilizar Docker** para contenerizar la aplicación y facilitar su despliegue.
6. **Makefile** para automatizar la construcción y ejecución de contenedores.

## Validar
ejecuta el archivo `Makefile` para construir y ejecutar el proyecto. Asegúrate de que todos los comandos funcionen correctamente y que la aplicación se levante sin errores.

---


# Agenda del taller “¿IA tu sabes?” (1 h 30 min)

| Tiempo            | Actividad                                                    | Tarea para participantes                                 | Deliverable parcial                                 |
|-------------------|--------------------------------------------------------------|-----------------------------------------------------------|-----------------------------------------------------|
| **1. Bienvenida e introducción**<br>10 min | • Presentación del taller y objetivos<br>• Explicación del prompt para IA<br>• Demo rápida de generación automática del esqueleto con Cursor/void | — Escuchar y seguir la demo                             | — Entorno de proyecto generado en IDE con IA        |
| **2. Configuración de entorno**<br>10 min | • Clonar repositorio base<br>• Construir imagen Docker<br>• Ejecutar contenedor local | • Clonar y ejecutar `docker build` y `docker run`       | • Contenedor con API levantada en `localhost`       |
| **3. Desarrollo del frontend**<br>20 min  | • Crear página HTML/CSS/JS<br>• Mostrar mensajes iniciales<br>• Implementar scroll infinito con Fetch API | • Escribir HTML básico<br>• Añadir estilos y script JS<br>• Probar carga paginada de mensajes | • Frontend funcionando que llama a GET `/messages`   |
| **4. Desarrollo del backend**<br>20 min   | • Implementar API REST en Python o Java sin frameworks<br>• Conectar SQLite<br>• Habilitar CORS | • Definir rutas GET/POST<br>• Escribir lógica de BD y controladores<br>• Probar con Postman o curl | • API con GET y POST funcionando y persistencia BD   |
| **5. Integración y prueba local**<br>10 min | • Conectar frontend y backend en Docker Compose<br>• Variables de entorno y configuración | • Crear `docker-compose.yml`<br>• Levantar servicios coordinados       | • App end-to-end en contenedores (frontend+API)     |
| **6. Despliegue con Helm en Kubernetes**<br>15 min | • Explorar chart de Helm<br>• Ajustar valores (`values.yaml`)<br>• Desplegar en cluster k8s (minikube/k3s) | • Instalar chart con `helm install`<br>• Verificar Pods y Service | • App accesible en cluster (URL o NodePort)         |
| **7. Cierre y entregables finales**<br>5 min  | • Resumen de aprendizajes<br>• Compartir recursos adicionales | — Subir repositorio completo a GitHub/GitLab           | — Repositorio con frontend, backend, Dockerfiles, Helm chart, README.md |

---

## Entregables finales

1. **Código fuente completo**: Carpeta `frontend/`, carpeta `backend/`, `Dockerfile`, `docker-compose.yml`.
2. **Helm chart**: Directorio `chart/` con `Chart.yaml`, `values.yaml`, plantillas de Deployment, Service e Ingress.
3. **README.md**: Instrucciones para levantar localmente con Docker y desplegar en Kubernetes.
4. **URL o IP** de la aplicación desplegada en el cluster (minikube/k3s).  
5. Captura de pantalla o breve video demostrando el scroll infinito y la creación de un nuevo mensaje.


