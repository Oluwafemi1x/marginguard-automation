import shutil
import subprocess
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).parent
FRAMES = ROOT / "recordings" / "frames"
FRAMES.mkdir(parents=True, exist_ok=True)


def snap(page, number: int) -> None:
    page.screenshot(path=str(FRAMES / f"frame-{number:03}.png"), full_page=False)


server = subprocess.Popen(
    ["uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"],
    cwd=ROOT,
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
)
try:
    time.sleep(2)
    with sync_playwright() as playwright:
        system_chromium = shutil.which("chromium") or shutil.which("chromium-browser")
        launch_kwargs = {"headless": True}
        if system_chromium:
            launch_kwargs["executable_path"] = system_chromium

        browser = playwright.chromium.launch(**launch_kwargs)
        page = browser.new_page(viewport={"width": 1440, "height": 900})
        page.goto("http://127.0.0.1:8000", wait_until="networkidle")
        snap(page, 1)
        page.click("#run")
        page.wait_for_timeout(350)
        snap(page, 2)
        page.wait_for_selector(".finding", timeout=30000)
        snap(page, 3)
        page.locator("#findings").scroll_into_view_if_needed()
        page.wait_for_timeout(300)
        snap(page, 4)
        page.screenshot(path=str(ROOT / "demo-dashboard.png"), full_page=True)
        browser.close()
finally:
    server.terminate()
    server.wait(timeout=5)

sequence = [1, 1, 2, 2, 3, 3, 4, 4]
concat = ROOT / "recordings" / "frames.txt"
concat.write_text(
    "".join(
        f"file '{(FRAMES / f'frame-{number:03}.png').as_posix()}'\nduration 1\n"
        for number in sequence
    )
    + f"file '{(FRAMES / 'frame-004.png').as_posix()}'\n",
    encoding="utf-8",
)
ffmpeg = shutil.which("ffmpeg")
if ffmpeg:
    subprocess.run(
        [
            ffmpeg,
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(concat),
            "-vf",
            "fps=30,format=yuv420p",
            "-movflags",
            "+faststart",
            str(ROOT / "recordings" / "marginguard-demo.mp4"),
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
print("Created demo-dashboard.png and recordings/marginguard-demo.mp4")
