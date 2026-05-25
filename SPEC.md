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
