# CODE-WITNESS

Reproducible software verification for Python artefacts.

## Run

```powershell
pip install -r requirements.txt
uvicorn backend.main:app --reload --port 8000
```

In another terminal:

```powershell
cd frontend
npm run dev
```

Open http://localhost:3000. Submitted Python runs in separate timed subprocesses. This MVP is not a production-grade sandbox.
