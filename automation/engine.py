import re
import shutil
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
SHOT_DIR = ROOT / "screenshots"
SHOT_DIR.mkdir(exist_ok=True)


@dataclass
class Finding:
    sku: str
    product_name: str
    competitor: str
    url: str
    our_price: float
    competitor_price: float
    stock: str
    gap_percent: float
    opportunity: float
    severity: str
    recommendation: str
    screenshot: str


def _money(text: str) -> float:
    match = re.search(r"([0-9][0-9,]*(?:\.[0-9]{1,2})?)", text.replace("₦", ""))
    if not match:
        raise ValueError(f"No price found in: {text!r}")
    return float(match.group(1).replace(",", ""))


def _recommend(our: float, competitor: float, stock: str) -> tuple[str, str, float, float]:
    gap = ((our - competitor) / our * 100) if our else 0
    if stock == "out":
        return (
            "LOW",
            "Competitor is out of stock — defend margin and promote availability.",
            gap,
            0,
        )
    if competitor <= our * 0.88:
        opportunity = round((our - competitor) * 40, 2)
        return (
            "CRITICAL",
            "Large price disadvantage — review price or bundle value immediately.",
            gap,
            opportunity,
        )
    if competitor < our:
        opportunity = round((our - competitor) * 20, 2)
        return (
            "WATCH",
            "Competitor is cheaper — test a targeted promotion before changing list price.",
            gap,
            opportunity,
        )
    return (
        "GOOD",
        "You are price-competitive — preserve margin and monitor stock movement.",
        gap,
        0,
    )


def _ensure_chromium(executable_path: str) -> None:
    """Install the Playwright Chromium binary if the deploy cache does not contain it."""
    if Path(executable_path).exists():
        return

    try:
        subprocess.run(
            [sys.executable, "-m", "playwright", "install", "chromium"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=180,
        )
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
        output = getattr(exc, "stdout", "") or ""
        raise RuntimeError(
            "Chromium is not installed and automatic Playwright browser installation failed. "
            f"Installer output: {output[-1200:]}"
        ) from exc

    if not Path(executable_path).exists():
        raise RuntimeError(
            "Playwright reported a successful Chromium install, but the expected browser "
            f"executable is still missing at {executable_path}."
        )


def scan_items(
    items: list[dict],
    headless: bool = True,
    record_dir: str | None = None,
) -> list[dict]:
    results = []
    with sync_playwright() as playwright:
        system_chromium = shutil.which("chromium") or shutil.which("chromium-browser")
        if not system_chromium:
            _ensure_chromium(playwright.chromium.executable_path)

        launch_kwargs = {
            "headless": headless,
            "args": ["--disable-dev-shm-usage", "--no-sandbox"],
        }
        if system_chromium:
            launch_kwargs["executable_path"] = system_chromium

        browser = playwright.chromium.launch(**launch_kwargs)
        context_kwargs = {"viewport": {"width": 1440, "height": 900}}
        if record_dir:
            context_kwargs["record_video_dir"] = record_dir
            context_kwargs["record_video_size"] = {"width": 1440, "height": 900}

        context = browser.new_context(**context_kwargs)
        page = context.new_page()

        for item in items:
            url = str(item["url"])
            page.goto(url, wait_until="networkidle", timeout=20000)
            title = page.locator("[data-product-name]").inner_text()
            price_text = page.locator("[data-price]").inner_text()
            stock_text = page.locator("[data-stock]").inner_text().strip().lower()
            price = _money(price_text)
            stock = "out" if "out" in stock_text else "in"
            severity, recommendation, gap, opportunity = _recommend(
                float(item["our_price"]),
                price,
                stock,
            )

            slug = re.sub(r"[^a-z0-9]+", "-", item["sku"].lower()).strip("-")
            shot = SHOT_DIR / f"{slug}.png"
            page.screenshot(path=str(shot), full_page=True)

            finding = Finding(
                sku=item["sku"],
                product_name=title,
                competitor=item["competitor"],
                url=url,
                our_price=float(item["our_price"]),
                competitor_price=price,
                stock=stock,
                gap_percent=round(gap, 2),
                opportunity=opportunity,
                severity=severity,
                recommendation=recommendation,
                screenshot=f"/screenshots/{shot.name}",
            )
            results.append(asdict(finding))

        context.close()
        browser.close()

    return results
