# Penny Assistant Backend

## Setup

1. Create and activate a Python virtual environment:
   ```bash
   python -m venv .venv && source .venv/bin/activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and fill in your Google Cloud credentials and project info.

## Running Locally

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8080
```

## Deployment

- See the root cloudbuild.yaml for Cloud Run deployment via CI/CD. 