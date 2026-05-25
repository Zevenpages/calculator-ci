# SPEC — Calculadora

Define el comportamiento esperado de cada operación ANTES de implementarla.

## Operaciones

| Operación  | Función              | Entrada      | Salida           |
|------------|----------------------|--------------|------------------|
| Suma       | `add(a, b)`          | dos números  | `a + b`          |
| Resta      | `subtract(a, b)`     | dos números  | `a - b`          |
| Multiplic. | `multiply(a, b)`     | dos números  | `a * b`          |
| División   | `divide(a, b)`       | dos números  | `a / b`          |

## Casos borde

- `divide(a, 0)` debe levantar `ValueError` con mensaje "No se puede dividir por cero".
- La capa web debe rechazar entradas no numéricas con un mensaje legible, sin llegar a la lógica.

## Contrato

- `app/calculator.py` contiene SOLO lógica pura. Sin imports de Flask.
- Los tests prueban estas funciones directamente.

## Contrato de la capa web (`web/app.py`)

La capa web es una fachada HTTP fina sobre la lógica pura. Comportamiento esperado:

| Petición                                   | Respuesta esperada                          |
|--------------------------------------------|---------------------------------------------|
| `GET /`                                    | HTML con un `<form` para operar             |
| `POST /` con `a`, `b`, `operation` válidos | el resultado renderizado (ej. `42.0`)       |
| `POST /` con `operation=divide` y `b=0`    | el mensaje "No se puede dividir por cero"   |
| `POST /` con `a` o `b` no numérico         | el mensaje "Entrada invalida"               |

- La capa web NO contiene lógica aritmética: mapea nombres de operación a funciones de `calculator` y delega.
- Estos comportamientos se prueban con el test client de Flask (tests de integración), antes de implementar la capa.

## Contrato de atributos de las cards de Trello (`ci/trello.py`)

El mecanismo de feedback enriquece cada card. La lógica pura (que arma textos y elige etiquetas) vive en `ci/trello.py` y se prueba directamente; la parte de red (HTTP a la API de Trello) es glue fina sobre esas funciones.

### `build_description(author, branch, sha, run_url, when) -> str`

Devuelve la descripción de la card en Markdown, con una línea por atributo y en este orden exacto:

```
**Autor:** <author>
**Rama:** <branch>
**Commit:** <sha[:7]>
**Fecha:** <when>
**Run:** <run_url>
```

- El commit se muestra **acortado a 7 caracteres**.
- Si un valor falta (string vacío o `None`), se reemplaza por `?` y la línea igual aparece.

### `label_for(stage) -> (name, color)`

Mapea el estado del pipeline a una etiqueta de color de Trello:

| stage           | name            | color    |
|-----------------|-----------------|----------|
| `en_progreso`   | `En progreso`   | `blue`   |
| `build_ok`      | `Build OK`      | `green`  |
| `failed`        | `Failed`        | `red`    |
| `en_produccion` | `En produccion` | `purple` |

- Un `stage` desconocido levanta `ValueError`.

### `labels_to_remove(existing, keep_name) -> list[str]`

Al mover una card de estado, debe quedar **un solo** label de estado (el actual). Esta función decide qué labels sacar:

- `existing` es la lista de labels actuales de la card (dicts con `id` y `name`).
- Devuelve los `id` de los labels cuyo `name` es uno de los 4 estados conocidos **y** distinto de `keep_name`.
- Labels que no son de estado (ej. un `bug` que alguien agregó a mano) NO se tocan.

### Atributos aplicados a la card (parte de red, sobre las funciones puras)

- **Descripción** = `build_description(...)`.
- **Label de color** = `label_for(stage)` (etiqueta gratis de Trello, no Custom Field).
- **Attachment** = el `run_url` adjuntado como link clickable (nombre "GitHub Actions run").
