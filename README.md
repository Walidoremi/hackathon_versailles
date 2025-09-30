🤴 Chatbot Touristique – Château de Versailles
📌 Description

Cette application est un assistant multi-agents conçu pour aider les visiteurs du Château de Versailles à organiser leur séjour.
Elle s’appuie sur plusieurs fichiers CSV (météo, événements, billetterie, logements, restaurants, expositions, etc.) et sur des modèles LLM (Mistral) + une base vectorielle (Qdrant) pour répondre de façon intelligente aux questions.

Fonctionnalités principales :

Génération d’itinéraires personnalisés (avec météo, contraintes, expositions, logements…).

Réponses rapides aux questions ponctuelles (météo, billetterie, événements).

Suggestions de restaurants, activités familles, souvenirs.

Intégration d’une UI web simple (FastAPI + HTML/CSS/JS).

🚀 Installation
1. Cloner le repo
git clone https://github.com/mon-projet/llm_chat_api.git
cd llm_chat_api

2. Créer un environnement virtuel
python -m venv .venv
.\.venv\Scripts\activate     # sous PowerShell

3. Installer les dépendances
pip install -r requirements.txt

🔑 Configuration
Variables d’environnement

Crée un fichier .env à la racine du projet avec :

MISTRAL_API_KEY=ta_cle_mistral
QDRANT_URL=https://xxx.cloud.qdrant.io
QDRANT_API_KEY=ta_cle_qdrant


⚠️ Ces clés sont obligatoires pour que l’agent fonctionne.

▶️ Lancer l’application
API (FastAPI)
uvicorn app.main:app --reload


L’API est dispo sur : http://127.0.0.1:8000

Documentation interactive : http://127.0.0.1:8000/api/docs

UI (front minimaliste)

Rendez-vous sur :
👉 http://127.0.0.1:8000

📂 Données

L’application lit plusieurs fichiers CSV dans le dossier data/ :

weather_forecast.csv → Prévisions météo

versailles_events.csv → Événements & activités

billeterie.csv → Tarifs et billetterie

logement.csv → Hôtels et logements proches

resto.csv → Restaurants

expo.csv → Expositions

activ_famille.csv → Activités familles

prdt_boutique.csv → Produits boutique

📡 Endpoints principaux
Santé
GET /api/v1/health

Évaluation rapide (chat simple)
POST /api/v1/chat
Body :
{
  "question": "Quelle est la météo du jour ?",
  "date": "2025-09-30"
}

Multi-agents (itinéraires, QA, lodging…)
POST /api/v1/multi-chat

🧪 Tests rapides
PowerShell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/chat" -Method Post -Headers @{ "Content-Type"="application/json" } -Body '{"question":"Quelle est la météo du jour ?","date":"2025-09-30"}'

Bash / sh
curl -X POST http://127.0.0.1:8000/api/v1/chat \
     -H "Content-Type: application/json" \
     -d '{"question":"Quelle est la météo du jour ?","date":"2025-09-30"}'

🛠️ Débogage

Si erreur httpx.ConnectError → vérifier la connectivité à Mistral API et Qdrant.

Si CERTIFICATE_VERIFY_FAILED → ajouter verify=False dans QdrantClient.

Vérifier que les CSV sont bien au format attendu.
