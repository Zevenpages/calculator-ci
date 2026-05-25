# CI/CD Calculator Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a complete CI/CD environment around a trivial Python calculator that maps 1:1 to the professor's diagram (VCS, CI server, delivery env, feedback) and earns the SDD extra point through a verifiable spec-first commit history.

**Architecture:** Pure logic in `app/calculator.py`, thin Flask web layer in `web/app.py`, both packaged in one Dockerfile used identically local/CI/prod. GitHub Actions splits into CI (branch: build+lint+test+sonar) and CD (merge to main: Render deploy). Trello cards implement the feedback arrow, non-blocking.

**Tech Stack:** Python 3.11, Flask + gunicorn, pytest + pytest-bdd + pytest-cov, flake8, Docker, GitHub Actions, SonarCloud, Render, Trello API.

---

## File Structure

| File | Responsibility |
|------|----------------|
| `app/calculator.py` | Pure arithmetic logic, no framework imports |
| `app/__init__.py` | Makes `app` a package |
| `web/app.py` | Flask HTTP layer, delegates to calculator |
| `web/__init__.py` | Makes `web` a package |
| `templates/index.html` | Minimal form UI |
| `tests/test_calculator.py` | Unit tests + pytest-bdd step definitions |
| `tests/features/calculator.feature` | Gherkin scenarios (executable spec) |
| `SPEC.md` | Behavior spec, committed before code |
| `conftest.py` | Empty; makes repo root importable by pytest |
| `requirements.txt` | Pinned deps (`==`) |
| `.flake8` | Lint config |
| `.gitignore` | Python ignores |
| `Dockerfile` | `python:3.11-slim`, gunicorn entrypoint |
| `sonar-project.properties` | SonarCloud config |
| `render.yaml` | Render Docker service |
| `.github/scripts/trello_create.sh` | Create card in a list, emit card_id |
| `.github/scripts/trello_move.sh` | Move card to a list |
| `.github/workflows/ci.yml` | Branch/PR pipeline |
| `.github/workflows/cd.yml` | main pipeline (deploy) |

---

## Task 0: Scaffolding + git init

**Files:**
- Create: `.gitignore`, `requirements.txt`, `.flake8`, `conftest.py`, `app/__init__.py`, `web/__init__.py`

- [ ] **Step 1: Init git in the project app folder**

The spec docs live at repo root already. Create the app inside the same repo.

```bash
cd "/Users/mateowendler/Proyectos propios/ICS-Parcial2"
git init
git branch -M main
```

- [ ] **Step 2: Create `.gitignore`**

```gitignore
__pycache__/
*.pyc
.venv/
venv/
reports/
.pytest_cache/
.DS_Store
```

- [ ] **Step 3: Create `requirements.txt`** (pinned)

```text
flask==3.0.3
gunicorn==23.0.0
pytest==8.3.3
pytest-bdd==7.3.0
pytest-cov==5.0.0
flake8==7.1.1
```

- [ ] **Step 4: Create `.flake8`**

```ini
[flake8]
max-line-length = 88
exclude = .git,__pycache__,.venv,venv
```

- [ ] **Step 5: Create empty package + conftest files**

```bash
touch conftest.py app/__init__.py web/__init__.py
mkdir -p app web tests/features templates .github/scripts .github/workflows
touch conftest.py app/__init__.py web/__init__.py
```

- [ ] **Step 6: Create local venv and install**

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```
Expected: installs without error.

- [ ] **Step 7: Commit scaffolding**

```bash
git add .gitignore requirements.txt .flake8 conftest.py app/__init__.py web/__init__.py docs/
git commit -m "chore: scaffolding, deps and tooling config"
```

---

## Task 1: SPEC.md (SDD commit 1 — spec before code)

**Files:**
- Create: `SPEC.md`

- [ ] **Step 1: Write the behavior spec**

```markdown
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
```

- [ ] **Step 2: Commit SPEC alone (no code yet)**

```bash
git add SPEC.md
git commit -m "docs: SPEC define comportamiento antes del codigo (SDD)"
```

---

## Task 2: Gherkin feature (SDD commit 2 — executable spec)

**Files:**
- Create: `tests/features/calculator.feature`

- [ ] **Step 1: Write the feature file** (English keywords, Spanish content for clarity)

```gherkin
Feature: Calculator operations

  Scenario: Add two numbers
    Given the operands 2 and 3
    When I apply the operation "add"
    Then the result is 5

  Scenario: Subtract two numbers
    Given the operands 10 and 4
    When I apply the operation "subtract"
    Then the result is 6

  Scenario: Multiply two numbers
    Given the operands 6 and 7
    When I apply the operation "multiply"
    Then the result is 42

  Scenario: Divide two numbers
    Given the operands 20 and 5
    When I apply the operation "divide"
    Then the result is 4

  Scenario: Divide by zero raises an error
    Given the operands 5 and 0
    When I apply the operation "divide"
    Then it raises an error
```

- [ ] **Step 2: Commit the feature alone**

```bash
git add tests/features/calculator.feature
git commit -m "test: spec en Gherkin ejecutable (SDD)"
```

---

## Task 3: Step definitions + unit tests (SDD commit 3 — RED)

**Files:**
- Create: `tests/test_calculator.py`

- [ ] **Step 1: Write the step definitions and unit tests**

```python
import pytest
from pytest_bdd import scenarios, given, when, then, parsers

from app import calculator

# Bind all scenarios in the feature file
scenarios("features/calculator.feature")


@pytest.fixture
def context():
    return {}


@given(parsers.parse("the operands {a:d} and {b:d}"), target_fixture="context")
def given_operands(a, b):
    return {"a": a, "b": b}


@when(parsers.parse('I apply the operation "{op}"'))
def apply_operation(context, op):
    func = getattr(calculator, op)
    try:
        context["result"] = func(context["a"], context["b"])
    except Exception as exc:  # noqa: BLE001 - we assert on it later
        context["error"] = exc


@then(parsers.parse("the result is {expected:d}"))
def check_result(context, expected):
    assert context["result"] == expected


@then("it raises an error")
def check_error(context):
    assert isinstance(context.get("error"), ValueError)


# Direct unit tests on the pure logic
def test_add():
    assert calculator.add(2, 3) == 5


def test_subtract():
    assert calculator.subtract(10, 4) == 6


def test_multiply():
    assert calculator.multiply(6, 7) == 42


def test_divide():
    assert calculator.divide(20, 5) == 4


def test_divide_by_zero_raises():
    with pytest.raises(ValueError):
        calculator.divide(5, 0)
```

- [ ] **Step 2: Run tests to verify they FAIL (RED)**

Run: `.venv/bin/pytest -v`
Expected: collection/import error — `ModuleNotFoundError: No module named 'app.calculator'` (file does not exist yet). This is the intended red state.

- [ ] **Step 3: Commit the failing tests**

```bash
git add tests/test_calculator.py
git commit -m "test: step definitions y unit tests (RED, sin implementacion)"
```

---

## Task 4: calculator.py (SDD commit 4 — GREEN)

**Files:**
- Create: `app/calculator.py`

- [ ] **Step 1: Write the minimal implementation**

```python
"""Pure arithmetic logic. No framework imports."""


def add(a, b):
    return a + b


def subtract(a, b):
    return a - b


def multiply(a, b):
    return a * b


def divide(a, b):
    if b == 0:
        raise ValueError("No se puede dividir por cero")
    return a / b
```

- [ ] **Step 2: Run tests to verify they PASS (GREEN)**

Run: `.venv/bin/pytest -v`
Expected: all unit tests and all 5 scenarios PASS.

- [ ] **Step 3: Run flake8 to confirm clean**

Run: `.venv/bin/flake8 app web tests`
Expected: no output (exit 0).

- [ ] **Step 4: Commit the implementation**

```bash
git add app/calculator.py
git commit -m "feat: implementa calculadora que satisface la spec (GREEN)"
```

---

## Task 5: Web layer (Flask + template)

**Files:**
- Create: `web/app.py`, `templates/index.html`

- [ ] **Step 1: Write the Flask app**

```python
from flask import Flask, render_template, request

from app import calculator

app = Flask(__name__)

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
            a = float(request.form.get("a", ""))
            b = float(request.form.get("b", ""))
        except ValueError:
            error = "Entrada invalida: ingresa numeros"
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
```

- [ ] **Step 2: Write the template**

```html
<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <title>Calculadora CI/CD</title>
</head>
<body style="font-family: sans-serif; max-width: 420px; margin: 3rem auto;">
  <h1>Calculadora</h1>
  <form method="post">
    <input name="a" placeholder="a" required>
    <select name="operation">
      <option value="add">+</option>
      <option value="subtract">-</option>
      <option value="multiply">*</option>
      <option value="divide">/</option>
    </select>
    <input name="b" placeholder="b" required>
    <button type="submit">=</button>
  </form>
  {% if result is not none %}
    <p><strong>Resultado:</strong> {{ result }}</p>
  {% endif %}
  {% if error %}
    <p style="color: red;">{{ error }}</p>
  {% endif %}
</body>
</html>
```

- [ ] **Step 3: Run the app locally to verify it serves**

Run: `.venv/bin/python -m web.app`
Then open `http://localhost:8000`, do `6 * 7`, expect `42`. Try `5 / 0`, expect the red error message. Ctrl+C to stop.

- [ ] **Step 4: Commit the web layer**

```bash
git add web/app.py templates/index.html
git commit -m "feat: capa web Flask que delega en la logica pura"
```

---

## Task 6: Dockerfile + local container parity check

**Files:**
- Create: `Dockerfile`, `.dockerignore`

- [ ] **Step 1: Write the Dockerfile**

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "web.app:app"]
```

- [ ] **Step 2: Write `.dockerignore`**

```text
.venv
venv
__pycache__
.git
reports
.pytest_cache
docs
```

- [ ] **Step 3: Build the image**

Run: `docker build -t calculator-ci .`
Expected: builds successfully.

- [ ] **Step 4: Run tests inside the container (this is the CI behavior)**

Run: `docker run --rm calculator-ci pytest -v`
Expected: all tests PASS inside the container.

- [ ] **Step 5: Run the app from the container**

Run: `docker run --rm -p 8000:8000 calculator-ci`
Open `http://localhost:8000`, verify `6 * 7 = 42`. Ctrl+C.

- [ ] **Step 6: Commit Docker files**

```bash
git add Dockerfile .dockerignore
git commit -m "build: Dockerfile gunicorn, paridad local/CI/prod"
```

---

## Task 7: Trello scripts

**Files:**
- Create: `.github/scripts/trello_create.sh`, `.github/scripts/trello_move.sh`

- [ ] **Step 1: Write `trello_create.sh`**

```bash
#!/usr/bin/env bash
set -euo pipefail

TITLE="${COMMIT_MSG:-build} [${GITHUB_REF_NAME:-?}]"
DESC="Autor: ${GITHUB_ACTOR:-?} | Run: ${GITHUB_SERVER_URL:-}/${GITHUB_REPOSITORY:-}/actions/runs/${GITHUB_RUN_ID:-}"

RESPONSE=$(curl -s -X POST "https://api.trello.com/1/cards" \
  --data-urlencode "name=${TITLE}" \
  --data-urlencode "desc=${DESC}" \
  -d "idList=${TRELLO_LIST_ID}" \
  -d "key=${TRELLO_API_KEY}" \
  -d "token=${TRELLO_TOKEN}")

CARD_ID=$(printf '%s' "${RESPONSE}" | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])")
echo "card_id=${CARD_ID}" >> "${GITHUB_OUTPUT}"
echo "Created Trello card ${CARD_ID}"
```

- [ ] **Step 2: Write `trello_move.sh`**

```bash
#!/usr/bin/env bash
set -euo pipefail

if [ -z "${CARD_ID:-}" ]; then
  echo "No CARD_ID provided; skipping move."
  exit 0
fi

curl -s -X PUT "https://api.trello.com/1/cards/${CARD_ID}" \
  -d "idList=${TRELLO_LIST_ID}" \
  -d "key=${TRELLO_API_KEY}" \
  -d "token=${TRELLO_TOKEN}" > /dev/null

echo "Moved Trello card ${CARD_ID} to list ${TRELLO_LIST_ID}"
```

- [ ] **Step 3: Make scripts executable + commit**

```bash
chmod +x .github/scripts/trello_create.sh .github/scripts/trello_move.sh
git add .github/scripts/
git commit -m "ci: scripts Trello crear/mover tarjeta"
```

---

## Task 8: CI workflow (branch/PR)

**Files:**
- Create: `.github/workflows/ci.yml`

- [ ] **Step 1: Write `ci.yml`**

```yaml
name: CI

on:
  push:
    branches-ignore: [main]
  pull_request:
    branches: [main]

jobs:
  build-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0  # SonarCloud needs full history

      - name: Trello - crear tarjeta "En progreso"
        id: trello
        continue-on-error: true
        run: bash .github/scripts/trello_create.sh
        env:
          TRELLO_API_KEY: ${{ secrets.TRELLO_API_KEY }}
          TRELLO_TOKEN: ${{ secrets.TRELLO_TOKEN }}
          TRELLO_LIST_ID: ${{ secrets.TRELLO_LIST_INPROGRESS_ID }}
          COMMIT_MSG: ${{ github.event.head_commit.message }}

      - name: Build Docker image
        run: docker build -t calculator-ci .

      - name: Lint (flake8 dentro del container)
        run: docker run --rm calculator-ci flake8 app web tests

      - name: Tests + coverage (pytest dentro del container)
        run: |
          mkdir -p reports
          docker run --rm -v "${{ github.workspace }}/reports:/app/reports" calculator-ci \
            pytest --cov=app --cov-report=xml:reports/coverage.xml -v

      - name: SonarCloud Scan
        uses: SonarSource/sonarcloud-github-action@master
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}

      - name: Trello - mover a "Build OK"
        if: success()
        continue-on-error: true
        run: bash .github/scripts/trello_move.sh
        env:
          CARD_ID: ${{ steps.trello.outputs.card_id }}
          TRELLO_API_KEY: ${{ secrets.TRELLO_API_KEY }}
          TRELLO_TOKEN: ${{ secrets.TRELLO_TOKEN }}
          TRELLO_LIST_ID: ${{ secrets.TRELLO_LIST_BUILDOK_ID }}

      - name: Trello - mover a "Failed"
        if: failure()
        continue-on-error: true
        run: bash .github/scripts/trello_move.sh
        env:
          CARD_ID: ${{ steps.trello.outputs.card_id }}
          TRELLO_API_KEY: ${{ secrets.TRELLO_API_KEY }}
          TRELLO_TOKEN: ${{ secrets.TRELLO_TOKEN }}
          TRELLO_LIST_ID: ${{ secrets.TRELLO_LIST_FAILED_ID }}
```

- [ ] **Step 2: Commit**

```bash
git add .github/workflows/ci.yml
git commit -m "ci: pipeline branch/PR (build+lint+test+sonar+trello)"
```

Note: the `Failed` step runs on any prior failure because of `if: failure()`. The flake8 step failing stops pytest/sonar (fail-fast), then the failure handler fires — correct CI behavior.

---

## Task 9: SonarCloud config

**Files:**
- Create: `sonar-project.properties`

- [ ] **Step 1: Create the SonarCloud project (manual, one-time)**

In `sonarcloud.io`: log in with GitHub, import the repo, note the **organization key** and **project key**. Create `SONAR_TOKEN` under My Account → Security and add it as a GitHub repo secret. Disable "Automatic Analysis" in the SonarCloud project settings (we run CI-based analysis).

- [ ] **Step 2: Write `sonar-project.properties`** (replace placeholders with the real keys from step 1)

```properties
sonar.projectKey=REPLACE_org_calculator-ci
sonar.organization=REPLACE_org
sonar.sources=app,web
sonar.tests=tests
sonar.python.version=3.11
sonar.python.coverage.reportPaths=reports/coverage.xml
```

- [ ] **Step 3: Commit**

```bash
git add sonar-project.properties
git commit -m "ci: configuracion SonarCloud con coverage"
```

---

## Task 10: Render config + CD workflow

**Files:**
- Create: `render.yaml`, `.github/workflows/cd.yml`

- [ ] **Step 1: Write `render.yaml`**

```yaml
services:
  - type: web
    name: calculator-ci
    runtime: docker
    dockerfilePath: ./Dockerfile
    plan: free
```

- [ ] **Step 2: Create the Render service (manual, one-time)**

In `render.com`: New → Web Service → connect the repo → it detects the Dockerfile. Deploy once manually to confirm it serves. Then Settings → Deploy Hook → copy the URL → add as GitHub secret `RENDER_DEPLOY_HOOK_URL`. Turn OFF Render's auto-deploy on push (we trigger via the hook from CD so the CI server owns delivery).

- [ ] **Step 3: Write `cd.yml`**

```yaml
name: CD

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Trigger Render deploy
        run: curl -fsSL -X POST "${{ secrets.RENDER_DEPLOY_HOOK_URL }}"

      - name: Trello - tarjeta "En produccion"
        continue-on-error: true
        run: bash .github/scripts/trello_create.sh
        env:
          TRELLO_API_KEY: ${{ secrets.TRELLO_API_KEY }}
          TRELLO_TOKEN: ${{ secrets.TRELLO_TOKEN }}
          TRELLO_LIST_ID: ${{ secrets.TRELLO_LIST_PROD_ID }}
          COMMIT_MSG: ${{ github.event.head_commit.message }}
```

Note: CD creates a fresh card directly in "En produccion" (the branch CI card lifecycle ended at "Build OK"/"Failed"; this is a different run after merge). This keeps all four columns meaningful.

- [ ] **Step 4: Commit**

```bash
git add render.yaml .github/workflows/cd.yml
git commit -m "cd: deploy a Render por deploy hook tras merge a main"
```

---

## Task 11: GitHub repo, secrets, first end-to-end run

**Files:** none (platform config)

- [ ] **Step 1: Create the GitHub repo and push**

```bash
gh repo create calculator-ci --public --source=. --remote=origin
git push -u origin main
```

- [ ] **Step 2: Set up the Trello board**

Create a board with four lists in order: `En progreso`, `Build OK`, `En producción`, `Failed`. Get each list ID: `curl "https://api.trello.com/1/boards/{boardId}/lists?key=KEY&token=TOKEN"`.

- [ ] **Step 3: Add all GitHub secrets**

```bash
gh secret set RENDER_DEPLOY_HOOK_URL
gh secret set SONAR_TOKEN
gh secret set TRELLO_API_KEY
gh secret set TRELLO_TOKEN
gh secret set TRELLO_LIST_INPROGRESS_ID
gh secret set TRELLO_LIST_BUILDOK_ID
gh secret set TRELLO_LIST_PROD_ID
gh secret set TRELLO_LIST_FAILED_ID
```

- [ ] **Step 4: Verify CI on a branch**

```bash
git checkout -b demo/verify
git commit --allow-empty -m "ci: trigger verification run"
git push -u origin demo/verify
```
Expected: CI workflow runs, goes green, Trello card lands in "Build OK".

- [ ] **Step 5: Verify CD on merge**

Open a PR from `demo/verify` to `main`, merge it. Expected: CD runs, Render redeploys, a card appears in "En producción", the Render URL serves the calculator.

---

## Task 12: Demo rehearsal + slide

**Files:** none (presentation artifact lives outside the repo)

- [ ] **Step 1: Rehearse the break-it demo**

```bash
git checkout -b demo/break
# Edit app/calculator.py: change add to return a - b
git commit -am "demo: introduce intentional bug"
git push -u origin demo/break
```
Expected: CI fails at the pytest step, Trello card → "Failed". This is the live moment. Then revert the change.

- [ ] **Step 2: Prepare the slide**

One slide: the professor's diagram with the tool logos overlaid on each box — GitHub (VCS), GitHub Actions (CI server), Docker + Render (delivery), Trello (feedback), SonarCloud + flake8 (inspection). Keep it to the 5-minute budget.

- [ ] **Step 3: Pre-stage the demo**

Before the exam: one green run already deployed, Render URL open in the browser, Trello board visible. Live action = one `demo/break` push to show red, then explain.

---

## Self-Review

**Spec coverage:**
- C1 repo + ramas/merges → Task 0 (init), Task 11 (push, branch, PR merge) ✓
- C2 CI server → Task 8, Task 11 step 4 ✓
- C3 build local → Task 6 (docker build/run local) ✓
- C4 prueba automatizada → Tasks 3-4 ✓
- C5 build despliega → Task 10 (Render via hook) ✓
- C6 feedback → Task 7, 8, 10 (Trello) ✓
- C7 inspección → Task 8 (flake8) + Task 9 (SonarCloud) ✓
- C8 SDD → Tasks 1-4 in strict commit order ✓ (matches spec §4.1)
- C9 demo 5 min → Task 12 ✓
- Docker paridad → Task 6 (same image tested), Task 8 (tests run in container), Task 10 (Render builds Dockerfile) ✓

**Placeholder scan:** Only intentional placeholders are the SonarCloud org/project keys in `sonar-project.properties` (Task 9), which require real values from the manual SonarCloud setup — flagged with `REPLACE_`. No other TBDs.

**Type consistency:** `calculator.add/subtract/multiply/divide` signatures consistent across `calculator.py` (Task 4), tests (Task 3), web `OPERATIONS` map (Task 5). Trello scripts use a single `TRELLO_LIST_ID` env var, set per-call in workflows (Tasks 8, 10) — consistent. `card_id` output produced in Task 7 (`trello_create.sh`) and consumed in Task 8 (`steps.trello.outputs.card_id`).

**New secret vs spec:** Plan adds `TRELLO_LIST_BUILDOK_ID` (Build OK column) not in the spec's secrets table. This is needed because the spec's own Trello board (§3.4) has four columns including "Build OK". Spec secrets table should be updated to include it.
