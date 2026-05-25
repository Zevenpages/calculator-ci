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
