# Penny Assistant Streamlit App

## Setup

1. Create and activate a Python virtual environment:
   ```bash
   python -m venv .venv && source .venv/bin/activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and fill in your backend URL and Google auth info.

## Running Locally

```bash
streamlit run app.py
```

## Deployment

- See the root cloudbuild.yaml for Cloud Run deployment via CI/CD. 