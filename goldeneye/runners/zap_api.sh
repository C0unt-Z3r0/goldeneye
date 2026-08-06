#!/bin/bash
# zap_api.sh - wrapper para API do ZAP
# Uso: zap_api.sh <endpoint> [param1=valor1] [param2=valor2]

ZAP_URL="http://127.0.0.1:8080"
ENDPOINT="$1"
shift

# Construir query string
PARAMS=""
for p in "$@"; do
    if [ -n "$PARAMS" ]; then
        PARAMS="${PARAMS}&"
    fi
    PARAMS="${PARAMS}${p}"
done

if [ -n "$PARAMS" ]; then
    URL="${ZAP_URL}${ENDPOINT}?${PARAMS}"
else
    URL="${ZAP_URL}${ENDPOINT}"
fi

curl -s --max-time 10 "$URL"
