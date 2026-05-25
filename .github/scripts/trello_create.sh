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
