# Secretos con age + sops

## El problema que resuelve

Un `.env` con `LLM_TOKEN=gsk_...` en texto plano es el patrón más común
para manejar API keys — y el más fácil de filtrar por accidente: un
`git add .` distraído, un repo que pasa de privado a público, un
`.gitignore` mal escrito. La alternativa de "no lo subas, mándamelo por
Slack" tampoco escala ni queda auditado.

[age](https://github.com/FiloSottile/age) + [sops](https://github.com/getsops/sops)
permiten **commitear el secreto cifrado** junto al código: el archivo en
git nunca contiene el valor real, solo puede descifrarse con una llave
privada que vive fuera del repo.

## age: llaves simples, sin infraestructura

age es un reemplazo moderno de GPG para cifrado simple de archivo. Una
llave age es un par público/privado:

```bash
age-keygen -o ~/.config/sops/age/keys.txt
```

```
# created: 2026-06-24T00:00:00-06:00
# public key: age1kyupq4um57pmddeuaxm4dtwah9hhmxv3ty5tvjr7detgzlrfl9zsdte4zj
AGE-SECRET-KEY-1...
```

La llave **pública** (`age1...`) es segura de compartir y de poner en un
archivo de configuración versionado — es lo que se usa para *cifrar*. La
llave **privada** (`AGE-SECRET-KEY-...`, en el mismo archivo) es la que
permite *descifrar*, y nunca debe salir de la máquina de quien la generó.

## sops: cifra valores, no el archivo completo

sops envuelve age (o GPG, o KMS de la nube) para cifrar **solo los
valores** de un archivo estructurado (`.env`, YAML, JSON), dejando las
claves legibles. Esto es clave para revisar diffs en PRs: se puede ver qué
variable cambió sin poder ver su valor.

`.sops.yaml` en la raíz del proyecto le dice a sops qué llave(s) usar según
la ruta del archivo:

```yaml
creation_rules:
  - path_regex: secrets/.*\.enc\.env$
    age: age1kyupq4um57pmddeuaxm4dtwah9hhmxv3ty5tvjr7detgzlrfl9zsdte4zj
```

Cualquier archivo bajo `secrets/` que termine en `.enc.env` se cifra
automáticamente para esa llave pública cuando corres:

```bash
sops --encrypt --in-place secrets/groq.enc.env
```

El resultado (lo que se commitea):

```env
LLM_TYPE=openai
LLM_URL=https://api.groq.com/openai
LLM_TOKEN=ENC[AES256_GCM,data:JPYSnVCI02pCpBMEg0KqMfGGpuFvXn02fw/qyj/cLZll,iv:rBH0...,tag:...,type:str]
LLM_MODEL=ENC[AES256_GCM,data:Vs5jAqbZ1UqP8ssyvVoCvof5p+zHlKM=,iv:...,tag:...,type:str]
sops_age__list_0__map_recipient=age1kyupq4um57pmddeuaxm4dtwah9hhmxv3ty5tvjr7detgzlrfl9zsdte4zj
...
```

Las claves (`LLM_TYPE`, `LLM_URL`...) quedan legibles. Los valores
sensibles, no. Sin la llave privada correspondiente, ese archivo es ruido
criptográfico.

## Descifrar solo para el proceso que lo necesita

```bash
export SOPS_AGE_KEY_FILE=~/.config/sops/age/keys.txt

sops exec-env secrets/groq.enc.env \
  "java -jar ether-brain-cli.jar '¿qué clima hay en Tlaxcala?'"
```

`sops exec-env <archivo> <comando>`:

1. Descifra `<archivo>` en memoria (nunca escribe el resultado a disco).
2. Exporta cada clave como variable de entorno, **solo para el proceso
   `<comando>`** y sus hijos.
3. Al terminar `<comando>`, esas variables desaparecen — no contaminan tu
   shell ni quedan en `env | grep`.

Alternativas si necesitas el valor en otro contexto:

```bash
sops --decrypt secrets/groq.enc.env          # imprime todo descifrado a stdout
sops --decrypt --extract '["LLM_TOKEN"]' secrets/groq.enc.env   # solo un campo
```

## Dónde vive la llave privada según el sistema operativo

`SOPS_AGE_KEY_FILE` explícito es la forma portable. Si no la defines, sops
busca en una ruta default que **difiere entre macOS y Linux**:

| SO | Ruta default |
|---|---|
| Linux | `$XDG_CONFIG_HOME/sops/age/keys.txt` (o `~/.config/sops/age/keys.txt`) |
| macOS | `~/Library/Application Support/sops/age/keys.txt` |

Para el taller, exportar `SOPS_AGE_KEY_FILE` explícitamente evita esta
ambigüedad entre máquinas de asistentes con distinto sistema operativo.

## Cómo se replica esto en CI/CD (fuera del taller)

El mismo patrón funciona en GitHub Actions u otro CI: la llave privada age
se guarda como secret de la plataforma (`AGE_PRIVATE_KEY`), un paso del
pipeline la escribe a un archivo temporal, y `sops exec-env` descifra justo
antes de correr el agente — el valor real nunca aparece en los logs del
pipeline ni en el repo.
