# UBID Mesh Prototype

Simple hackathon prototype that merges duplicate businesses from multiple department CSV files, assigns a Unique Business ID (UBID), and marks businesses as ACTIVE/INACTIVE.

## Folder Structure

```text
PANIAS/
  data/
    shop.csv
    factories.csv
    labour.csv
  api/
    index.py
  ubid_mesh.py
  main.py
  server.py
  requirements.txt
  render.yaml
  vercel.json
  README.md
```

## What It Does

1. Loads `shop.csv`, `factories.csv`, `labour.csv`
2. Normalizes names (lowercase, strips company suffixes like `pvt ltd` / `private limited`)
3. Fuzzy-matches records with same pincode and name similarity threshold (default `85`)
4. Groups matching records into one business
5. Assigns UBID:
   - PAN exists: `KA-PAN-{PAN}`
   - No PAN: `KA-INT-{counter}`
6. Status rule:
   - phone exists in any grouped record -> `ACTIVE`
   - phone missing and oldest record year <= 2021 -> `INACTIVE`

## Local Run

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

### Run API

```bash
uvicorn server:app --reload
```

Open:
- http://127.0.0.1:8000/
- http://127.0.0.1:8000/all
- http://127.0.0.1:8000/search?name=tata
- http://127.0.0.1:8000/status/KA-PAN-AAACT2803M

## Deploy to Render

1. Push this folder to GitHub.
2. In Render, create a new **Web Service** from the repo.
3. Render auto-detects `render.yaml`.
4. Deploy.

If build gets stuck while compiling `pandas`, ensure the service uses Python `3.12` (already pinned via `.python-version` and `render.yaml`).

## Deploy to Vercel

1. Push this folder to GitHub.
2. Import project in Vercel.
3. Framework preset: `Other`.
4. Vercel uses `vercel.json` and serves `api/index.py`.

## Expected Demo Evidence

`TATA STEEL PVT LTD`, `TATA STEEL PRIVATE LIMITED`, and `Tata Steel Pvt. Ltd.` get grouped under a single UBID.
