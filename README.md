# LLM Chat API (squelette)

Squelette FastAPI minimal, extensible et gratuit.

## Démarrer

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python -m uvicorn app.main:app --reload
```

## Endpoints
- GET /api/v1/health
- POST /api/v1/chat
