"""Trello feedback integration.

Pure helpers (`build_description`, `label_for`) are unit-tested.
The HTTP glue (`create_card`, `move_card`) wraps them and talks to the
Trello REST API using only the standard library.
"""
import json
import os
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timezone

API = "https://api.trello.com/1"

_LABELS = {
    "en_progreso": ("En progreso", "blue"),
    "build_ok": ("Build OK", "green"),
    "failed": ("Failed", "red"),
    "en_produccion": ("En produccion", "purple"),
}


def _or_q(value):
    return value if value else "?"


def build_description(author, branch, sha, run_url, when):
    return (
        f"**Autor:** {_or_q(author)}\n"
        f"**Rama:** {_or_q(branch)}\n"
        f"**Commit:** {_or_q(sha)[:7]}\n"
        f"**Fecha:** {_or_q(when)}\n"
        f"**Run:** {_or_q(run_url)}"
    )


def label_for(stage):
    try:
        return _LABELS[stage]
    except KeyError:
        raise ValueError(f"stage desconocido: {stage}")


_STAGE_LABEL_NAMES = {name for name, _ in _LABELS.values()}


def labels_to_remove(existing, keep_name):
    return [
        label["id"]
        for label in existing
        if label["name"] in _STAGE_LABEL_NAMES and label["name"] != keep_name
    ]


# --- HTTP glue (no se testea unitariamente; usa las funciones puras) ---

def _auth():
    return {
        "key": os.environ["TRELLO_API_KEY"],
        "token": os.environ["TRELLO_TOKEN"],
    }


def _request(method, path, params):
    data = urllib.parse.urlencode(params).encode() if params else None
    req = urllib.request.Request(f"{API}{path}", data=data, method=method)
    with urllib.request.urlopen(req) as resp:
        body = resp.read().decode()
    return json.loads(body) if body else {}


def _add_label(card_id, stage):
    name, color = label_for(stage)
    _request(
        "POST",
        f"/cards/{card_id}/labels",
        {**_auth(), "name": name, "color": color},
    )


def _card_labels(card_id):
    return _request(
        "GET",
        f"/cards/{card_id}/labels?{urllib.parse.urlencode(_auth())}",
        {},
    )


def _remove_label(card_id, label_id):
    _request(
        "DELETE",
        f"/cards/{card_id}/idLabels/{label_id}?{urllib.parse.urlencode(_auth())}",
        {},
    )


def _add_attachment(card_id, url):
    _request(
        "POST",
        f"/cards/{card_id}/attachments",
        {**_auth(), "url": url, "name": "GitHub Actions run"},
    )


def create_card(list_id, name, desc, stage, run_url):
    card = _request(
        "POST",
        "/cards",
        {**_auth(), "idList": list_id, "name": name, "desc": desc},
    )
    card_id = card["id"]
    _add_label(card_id, stage)
    if run_url and run_url != "?":
        _add_attachment(card_id, run_url)
    return card_id


def move_card(card_id, list_id, stage):
    if not card_id:
        print("No CARD_ID; skipping move.")
        return
    _request("PUT", f"/cards/{card_id}", {**_auth(), "idList": list_id})
    name, _ = label_for(stage)
    for label_id in labels_to_remove(_card_labels(card_id), name):
        _remove_label(card_id, label_id)
    _add_label(card_id, stage)


# --- CLI usada por los workflows ---

def _run_url():
    server = os.environ.get("GITHUB_SERVER_URL", "")
    repo = os.environ.get("GITHUB_REPOSITORY", "")
    run_id = os.environ.get("GITHUB_RUN_ID", "")
    if server and repo and run_id:
        return f"{server}/{repo}/actions/runs/{run_id}"
    return ""


def _now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


def _emit_output(key, value):
    out = os.environ.get("GITHUB_OUTPUT")
    if out:
        with open(out, "a") as handle:
            handle.write(f"{key}={value}\n")


def main(argv):
    cmd = argv[1] if len(argv) > 1 else ""
    stage = os.environ["STAGE"]
    list_id = os.environ["TRELLO_LIST_ID"]
    run_url = _run_url()
    if cmd == "create":
        branch = os.environ.get("GITHUB_REF_NAME", "?")
        name = f"{os.environ.get('COMMIT_MSG', 'build')} [{branch}]"
        desc = build_description(
            author=os.environ.get("GITHUB_ACTOR", ""),
            branch=os.environ.get("GITHUB_REF_NAME", ""),
            sha=os.environ.get("GITHUB_SHA", ""),
            run_url=run_url,
            when=_now(),
        )
        card_id = create_card(list_id, name, desc, stage, run_url)
        _emit_output("card_id", card_id)
        print(f"Created Trello card {card_id}")
    elif cmd == "move":
        move_card(os.environ.get("CARD_ID", ""), list_id, stage)
    else:
        print(f"unknown command: {cmd}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
