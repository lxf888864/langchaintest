$ErrorActionPreference = 'Stop'
uvicorn app.backend.api:app --host 0.0.0.0 --port 8001 --reload
