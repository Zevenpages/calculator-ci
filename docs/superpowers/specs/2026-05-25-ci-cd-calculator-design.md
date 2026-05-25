# Spec de Diseño — Entorno CI/CD con Calculadora

**Fecha:** 2026-05-25
**Materia:** Ingeniería de Software — 2da instancia de evaluación (IC/EC)
**Evaluación:** Oral, 5 min, demo en vivo + preguntas teóricas. Evaluador: Doctor en el área.

---

## 1. Objetivo

Construir un entorno de Integración Continua / Entrega Continua completo, que mapee 1:1 al diagrama de referencia del profesor (cinco componentes: equipo, control de versiones, servidor de IC, entornos de entrega, mecanismo de feedback). La aplicación es una calculadora trivial: el foco es el pipeline, no la app. Cada decisión técnica debe ser justificable oralmente en una oración.

### Criterios de éxito

| # | Criterio | Verificable por |
|---|----------|-----------------|
| C1 | Repo de código con ramas y merges | Historial Git, PR mergeado |
| C2 | Servidor de IC corriendo el pipeline | Run verde en GitHub Actions |
| C3 | Entorno dev con build local | `docker build` + `docker run` local funciona |
| C4 | Prueba automatizada | pytest pasa en CI |
| C5 | Build que despliega al entorno de entrega | URL pública de Render sirviendo la app |
| C6 | Mecanismo de feedback | Tarjeta Trello se mueve según resultado |
| C7 | Inspección de código | flake8 gate + SonarCloud dashboard |
| C8 | Spec Driven Development | SPEC.md commiteado antes del código + Gherkin ejecutable |
| C9 | Demo cabe en 5 min | Ensayo de la estrategia de demo |

---

## 2. Mapeo al diagrama del profesor

| Componente del diagrama | Herramienta | Justificación en una oración |
|---|---|---|
| Equipo de desarrollo | Dev + Docker local | El dev corre el mismo container que CI y prod. |
| Control de versiones (Ramas y Merges) | GitHub | Estándar de industria; ramas y merges visibles en la demo. |
| Servidor de IC | GitHub Actions | Integrado al repo, sin infra que mantener. |
| Entornos de entrega | Render | Buildea el Dockerfile de verdad y publica URL pública. |
| Mecanismo de feedback | Trello API | Flecha de feedback visual y demostrable en vivo. |

---

## 3. Arquitectura

### 3.1 Componentes de la aplicación (unidades aisladas)

- **`app/calculator.py`** — Lógica pura. Sin imports de Flask. Funciones puras (`add`, `subtract`, `multiply`, `divide`). Qué hace: opera sobre números. Cómo se usa: import directo. De qué depende: nada (stdlib). Es la unidad que los tests prueban directamente.
- **`web/app.py`** — Capa web Flask. Recibe el request del formulario, valida entrada, delega a `calculator.py`, renderiza resultado. Qué hace: HTTP ↔ lógica. De qué depende: Flask + `app/calculator.py`. En prod corre con gunicorn.
- **`templates/index.html`** — UI mínima: formulario (dos operandos, operación) y resultado. Permite demo visual en browser.

**Frontera clave:** se puede cambiar `calculator.py` sin tocar `web/app.py` y viceversa. Los tests no tocan la capa web.

### 3.2 Pipeline

```
Feature branch → push / PR a main:
    GitHub Actions [ci.yml]:
        ├─ Trello "En progreso"           (continue-on-error)
        ├─ docker build                   (mismo Dockerfile que local)
        ├─ flake8                         (dentro del container, fail-fast)
        ├─ pytest + pytest-bdd            (dentro del container → coverage.xml)
        ├─ SonarCloud scan               (consume coverage.xml)
        └─ [si algo falla] → Trello "Failed"

Merge a main:
    GitHub Actions [cd.yml]:
        ├─ trigger Render deploy hook
        ├─ Render buildea Dockerfile → publica URL
        └─ [si OK] → Trello "En producción"
```

**Split CI/CD:** CI valida en la rama antes de integrar; CD entrega lo ya validado al mergear. Esto materializa el "Ramas y Merges" del diagrama, en lugar de un push directo a main.

**Fail-fast:** orden estricto. flake8 falla → pytest no corre. pytest falla → no hay scan ni deploy. Comportamiento correcto de CI.

### 3.3 Docker como unidad de paridad

El mismo `Dockerfile` (`python:3.11-slim`, `CMD gunicorn`) se usa en tres lugares:

1. **Local** — `docker build && docker run`, el dev ve la app igual que en prod.
2. **CI** — los tests corren *dentro* del container buildeado.
3. **Prod** — Render buildea ese mismo Dockerfile al recibir el deploy hook.

El container testeado es el deployado. Frase ante el evaluador: *"mismo container local, CI y prod"*. Render se eligió sobre Vercel precisamente porque usa el Dockerfile (Vercel lo ignoraría y usaría serverless functions propias), lo que dejaría a Docker como decoración.

### 3.4 Mecanismo de feedback (Trello)

Tablero con cuatro columnas: `En progreso → Build OK → En producción → Failed`.

- Una tarjeta por corrida. Se crea una vez ("En progreso") y se mueve una vez al final ("En producción" o "Failed"). Nunca dos tarjetas por la misma corrida.
- Contenido: mensaje del commit (título), rama, autor, link al run de Actions (descripción).
- Los steps de Trello son **no-bloqueantes** (`continue-on-error: true`): si la API falla en vivo, el build no se rompe por algo ajeno al código.

---

## 4. Spec Driven Development

Dos artefactos:

1. **`SPEC.md`** — define el comportamiento esperado de cada operación (incluyendo casos borde: división por cero, tipos inválidos) **antes** de escribir `calculator.py`. Se commitea en un commit previo al de la implementación. El historial Git evidencia que la spec precedió al código.
2. **`tests/features/calculator.feature`** — scenarios Gherkin que formalizan la spec en lenguaje ejecutable. Step definitions en pytest-bdd (`tests/test_calculator.py`) los conectan con los tests reales.

Vale hasta 1 punto extra. Coherencia = spec verificable antes de implementación en el historial.

### 4.1 Orden de commits obligatorio (SDD genuino, no teatro)

El historial Git debe reflejar el flujo SDD real. Cada paso es un commit separado, en este orden estricto:

1. `commit: SPEC.md` — define el comportamiento de las 4 operaciones + casos borde. Sin código aún.
2. `commit: calculator.feature` — la spec formalizada en Gherkin ejecutable.
3. `commit: step definitions (tests)` — pytest-bdd conecta scenarios con asserts. Los tests **fallan** acá (rojo) porque `calculator.py` no existe.
4. `commit: calculator.py` — implementación que hace pasar los scenarios (verde).

Regla: NO escribir todo junto y reordenar después. El flujo red→green debe ser real y demostrable. Un `git log` debe contar la historia: spec → spec ejecutable → tests rojos → código verde.

---

## 5. Manejo de errores

| Caso | Comportamiento |
|------|----------------|
| División por cero | `calculator.divide` levanta `ValueError`; la web muestra mensaje claro; test cubre el caso. |
| Entrada no numérica | `web/app.py` valida y devuelve error legible; no llega a la lógica. |
| Falla de lint/test en CI | Pipeline corta fail-fast; tarjeta Trello → "Failed". |
| Falla de API Trello | Step no-bloqueante; el build continúa; se loguea el warning. |
| Falla de deploy Render | Job CD falla visible; tarjeta no se mueve a "En producción". |

---

## 6. Estrategia de testing

- **Unitarios** sobre `app/calculator.py` directamente (las 4 operaciones + casos borde).
- **BDD** (`calculator.feature`) ejecutados vía pytest-bdd, cubriendo el comportamiento de la spec.
- **Coverage** exportado a `coverage.xml`, consumido por SonarCloud.
- **Demo rompible:** los casos borde están cubiertos de forma que una modificación incorrecta de la lógica por el evaluador hace fallar el pipeline de forma visible y explicable.

---

## 7. Estructura de carpetas

```
calculator-ci/
├── app/
│   └── calculator.py             # Lógica pura
├── web/
│   └── app.py                    # Flask — solo capa web
├── templates/
│   └── index.html                # UI mínima
├── tests/
│   ├── test_calculator.py        # Unit + step definitions BDD
│   └── features/
│       └── calculator.feature    # Scenarios Gherkin
├── SPEC.md                       # Spec previa al código (SDD)
├── Dockerfile                    # python:3.11-slim, CMD gunicorn
├── requirements.txt              # Versiones fijas con ==
├── .flake8                       # max-line-length = 88
├── sonar-project.properties      # Config SonarCloud
├── render.yaml                   # Config Render (opcional)
└── .github/
    └── workflows/
        ├── ci.yml                # PR/push rama: build + lint + test + sonar
        └── cd.yml                # merge main: deploy Render + Trello "En producción"
```

---

## 8. Secrets en GitHub

| Secret | Origen |
|---|---|
| `RENDER_DEPLOY_HOOK_URL` | Render → Service → Settings → Deploy Hook |
| `SONAR_TOKEN` | sonarcloud.io → My Account → Security |
| `TRELLO_API_KEY` | trello.com/app-key |
| `TRELLO_TOKEN` | misma página, link "Token" |
| `TRELLO_LIST_INPROGRESS_ID` | GET api.trello.com/1/boards/{id}/lists |
| `TRELLO_LIST_BUILDOK_ID` | ídem |
| `TRELLO_LIST_PROD_ID` | ídem |
| `TRELLO_LIST_FAILED_ID` | ídem |

---

## 9. Estrategia de demo (5 minutos)

Pipeline en frío tarda 2-3 min → no correr todo en frío en vivo.

1. **Antes:** run verde ya deployado; URL de Render abierta en el browser; tablero Trello visible.
2. **En vivo:** push en una rama que rompe un test → mostrar rojo en Actions + tarjeta Trello → "Failed". (O al revés: fix → merge → "En producción".)
3. **Slide:** esquema con mapeo 1:1 al diagrama del profesor + logos de las herramientas.

---

## 10. Decisiones explícitas (YAGNI)

- **Sin Terraform, sin staging, sin DB, sin framework JS.** No aportan al objetivo.
- **Versiones fijas** (`==`) en `requirements.txt`; Python 3.11 en Dockerfile y workflows.
- **`requirements.txt` + pip** es el gestor de paquetes (el más débil de los "valorados", pero presente y honesto).

### Upgrade opcional (si sobra tiempo de setup)

CI pushea la imagen a GHCR y Render pull-ea la imagen pre-buildeada → "exactamente el mismo binario", no solo la misma receta. Más setup. Default: Render buildea el Dockerfile (misma receta, reproducible).

---

## 11. Fuera de alcance

- Múltiples entornos (staging + prod).
- Persistencia / base de datos.
- Autenticación de la app.
- Tests de la capa web (los tests prueban la lógica pura; la web es delegación trivial).
