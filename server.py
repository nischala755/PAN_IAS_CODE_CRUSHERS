from pathlib import Path
from typing import Dict, List

from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse

from ubid_mesh import build_snapshot, normalize_name

app = FastAPI(title="UBID Mesh")
SNAPSHOT = build_snapshot(Path("data"))


@app.get("/", response_class=HTMLResponse)
def home() -> str:
    return """
    <html>
      <head>
        <title>UBID Mesh</title>
        <style>
          @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&display=swap');
          :root {
            --bg: #f5f1e8;
            --card: #fffdf8;
            --ink: #1f1c18;
            --accent: #0e7a54;
            --muted: #6f675d;
          }
          body {
            font-family: 'Space Grotesk', sans-serif;
            margin: 0;
            background:
              radial-gradient(circle at 8% 12%, #fcd9b8 0%, transparent 35%),
              radial-gradient(circle at 90% 85%, #bde8dc 0%, transparent 35%),
              var(--bg);
            color: var(--ink);
          }
          .wrap { max-width: 920px; margin: 48px auto; padding: 0 20px; }
          .hero { padding: 28px; border: 2px solid #d9cdbd; background: var(--card); border-radius: 18px; }
          h1 { margin: 0 0 10px; font-size: 2rem; }
          p { margin: 0 0 16px; color: var(--muted); }
          .grid { display: grid; grid-template-columns: repeat(auto-fit,minmax(210px,1fr)); gap: 12px; }
          a { text-decoration: none; color: var(--ink); border: 1px solid #d9cdbd; border-radius: 10px; padding: 14px; background: #fff; transition: 0.2s; }
          a:hover { transform: translateY(-2px); border-color: var(--accent); }
          code { color: var(--accent); font-weight: 600; }
        </style>
      </head>
      <body>
        <div class="wrap">
          <div class="hero">
            <h1>UBID Mesh</h1>
            <p>Simple duplicate business detection + UBID assignment for hackathon demo.</p>
            <div class="grid">
              <a href="/all"><strong>View all UBIDs</strong><br/><code>/all</code></a>
              <a href="/search?name=tata"><strong>Search sample</strong><br/><code>/search?name=tata</code></a>
              <a href="/status/KA-PAN-AAACT2803M"><strong>Status sample</strong><br/><code>/status/{ubid}</code></a>
            </div>
          </div>
        </div>
      </body>
    </html>
    """


@app.get("/all")
def all_businesses() -> Dict:
    return SNAPSHOT


@app.get("/search")
def search_business(name: str = Query(..., min_length=1)) -> Dict[str, object]:
    needle = normalize_name(name)
    matched = []

    for group in SNAPSHOT["groups"]:
        names = [normalize_name(rec["name"]) for rec in group["records"]]
        if any(needle in n for n in names):
            matched.append(group)

    return {"query": name, "matches": matched}


@app.get("/status/{ubid}")
def business_status(ubid: str) -> Dict:
    for group in SNAPSHOT["groups"]:
        if group["ubid"] == ubid:
            return {"ubid": ubid, "status": group["status"], "records": group["records"]}

    return {"error": "UBID not found", "ubid": ubid}
