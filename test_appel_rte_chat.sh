#!/bin/bash

response=$(curl -s -X POST "http://127.0.0.1:8000/api/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{"question":"Quelle est la météo du jour ?","date":"2025-09-30"}')

echo "📩 Réponse de l'API :"
echo "$response"