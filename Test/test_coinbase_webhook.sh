#!/bin/bash

# Nastavi svojo Coinbase skrivnost tukaj
WEBHOOK_SECRET="f66556f4-c492-458b-8ebc-1c01ff8cc849"

# Pot do payloada (lahko spremeniš ime datoteke)
PAYLOAD_FILE="body.json"

# Preveri, če payload obstaja
if [ ! -f "$PAYLOAD_FILE" ]; then
  echo "Napaka: Datoteka $PAYLOAD_FILE ne obstaja."
  exit 1
fi

# Izračunaj podpis
SIGNATURE=$(openssl dgst -sha256 -hmac "$WEBHOOK_SECRET" "$PAYLOAD_FILE" | sed 's/^.* //')

# Pošlji curl request
curl -X POST http://localhost:8000/webhook/coinbase/ \
  -H "Content-Type: application/json" \
  -H "X-CC-Webhook-Signature: $SIGNATURE" \
  --data-binary "@$PAYLOAD_FILE"
