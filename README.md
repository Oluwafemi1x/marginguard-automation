# MarginGuard — Competitive Revenue Intelligence Automation

> **A Playwright-powered business automation system that watches competitor product pages, detects price/stock changes, quantifies revenue risk, captures evidence, and turns the findings into Excel/CSV decision reports.**

MarginGuard is intentionally not a CRUD tutorial. It demonstrates browser automation, backend orchestration, business-rule modelling, evidence capture, reporting automation, API design, and a polished operator dashboard in one production-style project.

## Product preview

![MarginGuard dashboard](docs/demo/dashboard.png)

**Demo video:** [`docs/demo/marginguard-demo.mp4`](docs/demo/marginguard-demo.mp4)

## Why this matters
Retail and ecommerce teams often check competitor prices manually, copy results into spreadsheets, and react too late. MarginGuard compresses that workflow into one click: **browse → extract → compare → score → recommend → document**.

## What the demo proves
- Real Chromium automation with **Playwright**
- Price and stock extraction from rendered HTML pages
- Screenshot evidence for every observation
- Revenue-risk / opportunity scoring
- Action recommendations based on competitive gaps
- REST API orchestration with **FastAPI**
- Persistent scan history in SQLite for the demo
- Executive-ready **Excel** and **CSV** exports
- Swagger API documentation at `/docs`
- Responsive operator UI
- Pytest + Ruff CI
- Dockerized runtime based on the official Playwright image

## Architecture
```text
Dashboard / API Client
        │
        ▼
FastAPI control plane ─── Scan history (SQLite)
        │
        ▼
Playwright automation worker
        │
        ├── competitor page extraction
        ├── screenshot evidence
        └── price / stock normalization
        │
        ▼
Business scoring engine
        │
        ├── severity
        ├── opportunity value
        └── recommended action
        │
        ▼
Excel + CSV report generation
```

## Safe deterministic demo
The repository includes a small local competitor storefront under `demo_store/`. This makes the demonstration reproducible and avoids depending on third-party sites, anti-bot rules, or changing markup. The automation engine itself accepts arbitrary permitted URLs with the expected selectors.

## Run locally
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium
uvicorn app.main:app --reload
```
Open `http://127.0.0.1:8000`, then click **Run live scan**.

## Generate the recruiter demo video
```bash
python demo_record.py
```
This launches the app, captures the dashboard while the Playwright scan runs, and produces a demo screenshot plus MP4 when FFmpeg is available.

## API
- `GET /health`
- `GET /api/scans`
- `POST /api/scan`
- `GET /api/export/csv`
- `GET /api/export/xlsx`
- `GET /docs`

## Example scan payload
```json
{
  "items": [{
    "sku": "DESK-001",
    "product_name": "AeroDesk Pro Standing Desk",
    "our_price": 449000,
    "competitor": "Nova Retail",
    "url": "http://127.0.0.1:8000/demo/alpha.html"
  }]
}
```

## Engineering decisions
**Browser automation instead of scraping-only requests.** Many commerce pages render data dynamically; Playwright demonstrates the ability to operate a real browser, not only parse static HTML.

**Evidence-first automation.** Every finding carries a screenshot so decisions can be audited.

**Separation of concerns.** Browser extraction, business scoring, persistence, API orchestration, exports, and UI are separated into focused modules.

**Reproducible demo.** A bundled storefront ensures recruiters can run the project without external credentials.

## Business extensions
The same architecture can support authorized retailer feeds, scheduled scans, email/Slack alerts, ERP integration, FX normalization APIs, catalog matching, historical price charts, distributed workers, PostgreSQL, and role-based multi-user access.

## Tech stack
Python · FastAPI · Playwright · Chromium · REST API · SQLite · OpenPyXL · CSV · JavaScript · HTML/CSS · Pytest · Ruff · Docker · GitHub Actions

## Responsible automation
Use MarginGuard only on websites and data sources you are authorized to access and in accordance with applicable terms, robots policies, and rate limits.

## Author
**Oluwafemi Steven (Pycoder)** — Python Backend Developer · Automation & Debugging

GitHub: https://github.com/Oluwafemi1x
