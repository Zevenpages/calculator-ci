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
