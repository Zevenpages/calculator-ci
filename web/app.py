from flask import Flask, render_template, request

from app import calculator
from app.numbers import parse_number

app = Flask(__name__, template_folder="../templates")

OPERATIONS = {
    "add": calculator.add,
    "subtract": calculator.subtract,
    "multiply": calculator.multiply,
    "divide": calculator.divide,
}


@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    error = None
    if request.method == "POST":
        op = request.form.get("operation")
        try:
            a = parse_number(request.form.get("a", ""))
            b = parse_number(request.form.get("b", ""))
        except ValueError as exc:
            error = f"Entrada invalida: {exc}"
        else:
            try:
                result = OPERATIONS[op](a, b)
            except ValueError as exc:
                error = str(exc)
            except KeyError:
                error = "Operacion desconocida"
    return render_template("index.html", result=result, error=error)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
