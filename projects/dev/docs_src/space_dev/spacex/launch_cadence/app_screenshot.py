"""
Capture screenshots of the Dash dashboard.

Starts the app in a background thread, uses headless Chrome to
capture two views, then exits.

Output:
  images/app_image_01_linkedin_preview.png  — Fixed 1200x627 (LinkedIn optimised)
  images/app_image_02_full_view.png         — Full page including data table

Run with: python app_screenshot.py
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

LINKEDIN_WIDTH = 1200
LINKEDIN_HEIGHT = 627


def main() -> None:
    """Start the Dash server and capture both screenshots."""
    server_thread = threading.Thread(
        target=lambda: app.run(debug=False, use_reloader=False),
        daemon=True,
    )
    server_thread.start()
    time.sleep(2)

    opts = Options()
    opts.add_argument("--headless")
    opts.add_argument("--no-sandbox")
    opts.add_argument(f"--window-size={LINKEDIN_WIDTH},{LINKEDIN_HEIGHT}")
    driver = webdriver.Chrome(options=opts)

    try:
        driver.get("http://127.0.0.1:8050")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "js-plotly-plot"))
        )
        time.sleep(1)

        # Image 1: LinkedIn preview — 1200px wide, height cropped just above
        # the data table heading so only controls + chart are visible.
        # First render at full width to get layout positions.
        driver.set_window_size(LINKEDIN_WIDTH, 1200)
        time.sleep(0.5)
        crop_y = driver.execute_script(
            "const h4 = document.querySelector('h4');"
            "return h4 ? h4.getBoundingClientRect().top : 627;"
        )
        driver.set_window_size(LINKEDIN_WIDTH, int(crop_y))
        time.sleep(0.5)
        out_1 = IMAGES_DIR / "app_image_01_linkedin_preview.png"
        driver.save_screenshot(str(out_1))
        print(f"Saved: {out_1}  ({LINKEDIN_WIDTH}x{int(crop_y)})")

        # Image 2: Full page — expand to capture data table
        page_height = driver.execute_script("return document.body.scrollHeight")
        driver.set_window_size(1400, page_height)
        time.sleep(0.5)
        out_2 = IMAGES_DIR / "app_image_02_full_view.png"
        driver.save_screenshot(str(out_2))
        print(f"Saved: {out_2}")

    finally:
        driver.quit()


if __name__ == "__main__":
    main()
