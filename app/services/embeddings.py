import requests
import os

MISTRAL_API_KEY = "AdxzFiqFQsISvSQ7c2mn4sLxhoFTPh0k"

def mistral_embedding(text: str) -> list:
    url = "https://api.mistral.ai/v1/embeddings"
    headers = {"Authorization": f"Bearer {MISTRAL_API_KEY}"}
    payload = {"model": "mistral-embed", "input": text}
    resp = requests.post(url, json=payload, headers=headers)
    resp.raise_for_status()
    return resp.json()["data"][0]["embedding"]