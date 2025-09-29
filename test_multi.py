import requests

url = "http://127.0.0.1:8000/api/v1/multi-chat"
payload = {
    "query": "Je voyage en famille avec 2 enfants, nous visitons la ville demain et voulons optimiser notre journée."
}

resp = requests.post(url, json=payload)
print("Status:", resp.status_code)
print("Response:", resp.json())