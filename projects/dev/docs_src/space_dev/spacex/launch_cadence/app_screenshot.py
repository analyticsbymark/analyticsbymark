"""
Capture a full-page screenshot of the Dash dashboard.

Starts the app in a background thread, uses headless Chrome to
screenshot the default view, then exits.

Run with: python app_screenshot.py
Output:   images/app_image_01_default_view.png
"""

import sys
import threading
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from app import app

IMAGES_DIR = Path(__file__).resolve().parent / "images"
IMAGES_DIR.mkdir(exist_ok=True)


def main() -> None:
    """Start the Dash server, screenshot it, and exit."""
    server_thread = threading.Thread(
        target=lambda: app.run(debug=False, use_reloader=False),
        daemon=True,
    )
    server_thread.start()
    time.sleep(2)

    opts = Options()
    opts.add_argument("--headless")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--window-size=1400,900")
    driver = webdriver.Chrome(options=opts)

    try:
        driver.get("http://127.0.0.1:8050")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "js-plotly-plot"))
        )
        time.sleep(1)

        out = IMAGES_DIR / "app_image_01_default_view.png"
        driver.save_screenshot(str(out))
        print(f"Saved: {out}")
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
