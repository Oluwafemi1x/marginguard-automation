import asyncio
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

from app.db import init_db, recent_scans, save_scan
from app.models import ScanRequest
from automation.engine import scan_items
from automation.exporters import export_csv, export_excel

ROOT = Path(__file__).resolve().parents[1]
app = FastAPI(
    title="MarginGuard Automation API",
    version="1.0.0",
    description="Competitive pricing and stock intelligence powered by Playwright automation.",
)
app.mount("/static", StaticFiles(directory=ROOT / "app" / "static"), name="static")
app.mount("/screenshots", StaticFiles(directory=ROOT / "screenshots"), name="screenshots")
app.mount("/demo", StaticFiles(directory=ROOT / "demo_store", html=True), name="demo")


@app.on_event("startup")
def startup() -> None:
    init_db()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "MarginGuard"}


@app.get("/", response_class=HTMLResponse)
def dashboard() -> str:
    return (ROOT / "app" / "templates" / "index.html").read_text(encoding="utf-8")


@app.get("/api/scans")
def scans() -> list[dict]:
    return recent_scans()


@app.post("/api/scan")
async def run_scan(payload: ScanRequest) -> dict:
    try:
        items = [item.model_dump(mode="json") for item in payload.items]
        results = await asyncio.to_thread(scan_items, items)
        scan_id = save_scan(results)
        export_csv(results)
        export_excel(results)
        return {"scan_id": scan_id, "results": results}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Automation failed: {exc}") from exc


@app.get("/api/export/{kind}")
def export(kind: str) -> FileResponse:
    path = ROOT / "outputs" / f"marginguard-report.{kind}"
    if kind not in {"csv", "xlsx"} or not path.exists():
        raise HTTPException(status_code=404, detail="Run a scan first")
    media_type = (
        "text/csv"
        if kind == "csv"
        else "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    return FileResponse(path, media_type=media_type, filename=path.name)
