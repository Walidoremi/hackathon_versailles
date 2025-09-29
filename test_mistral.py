import httpx
import os

# Mets directement ta clé ici pour le test (juste pour vérifier)
MISTRAL_API_KEY = "ta_cle_mistral_ici"  

url = "https://api.mistral.ai/v1/chat/completions"
headers = {
    "Authorization": f"Bearer {"AdxzFiqFQsISvSQ7c2mn4sLxhoFTPh0k"}",
    "Content-Type": "application/json",
}
payload = {
    "model": "mistral-small-latest",
    "messages": [{"role": "user", "content": "Bonjour, peux-tu me donner une blague courte ?"}],
    "max_tokens": 50,
    "temperature": 0.7,
}

with httpx.Client(timeout=30.0) as client:
    r = client.post(url, headers=headers, json=payload)
    print("Status code:", r.status_code)
    print("Response:", r.text[:500])  # on affiche juste les 500 premiers caractères
