"""
Capture screenshots of the launch reliability Dash dashboard.

Starts the app in a background thread, uses headless Chrome to
capture two views, then exits.

Output:
  images/app_image_01_linkedin_preview.png  — Dashboard preview (chart + controls)
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

# Preview uses a wider viewport so the chart isn't squeezed by the
# sidebar.  The extra width gives the timeline scatter breathing room
# while still showing the dashboard controls alongside it.
PREVIEW_WIDTH = 1400


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
    opts.add_argument(f"--window-size={PREVIEW_WIDTH},1200")
    driver = webdriver.Chrome(options=opts)

    try:
        driver.get("http://127.0.0.1:8050")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "js-plotly-plot"))
        )
        time.sleep(1)

        # Image 1: Dashboard preview — chart + sidebar controls, cropped
        # just above the data table so the filtering options are visible
        # but the table doesn't dominate the image.
        #
        # The chart column uses flex:1 and height:100% which stretches
        # the Plotly chart to fill the viewport. To get a compact
        # preview, we constrain the flex container and graph to the
        # Plotly layout height (560px), trigger a resize, then measure.
        driver.set_window_size(PREVIEW_WIDTH, 800)
        time.sleep(0.5)
        driver.execute_script(
            "const graph = document.querySelector('.dash-graph');"
            "if (graph) graph.style.height = '560px';"
            "const chartCol = graph && graph.parentElement;"
            "if (chartCol) { chartCol.style.flex = 'none'; chartCol.style.height = 'auto'; }"
            "const flex = chartCol && chartCol.parentElement;"
            "if (flex) flex.style.minHeight = 'auto';"
            "const plot = document.querySelector('.js-plotly-plot');"
            "if (plot && window.Plotly) Plotly.Plots.resize(plot);"
        )
        time.sleep(1)
        # Crop at whichever is lower: the chart or the last sidebar
        # control, ensuring both the full chart and all controls show.
        crop_y = driver.execute_script(
            "const plot = document.querySelector('.js-plotly-plot');"
            "const slider = document.querySelector('.rc-slider');"
            "let bottom = 627;"
            "if (plot) bottom = Math.max(bottom, plot.getBoundingClientRect().bottom);"
            "if (slider) bottom = Math.max(bottom, slider.getBoundingClientRect().bottom);"
            "return Math.ceil(bottom) + 24;"
        )
        driver.set_window_size(PREVIEW_WIDTH, int(crop_y))
        time.sleep(0.5)
        out_1 = IMAGES_DIR / "app_image_01_linkedin_preview.png"
        driver.save_screenshot(str(out_1))
        print(f"Saved: {out_1}  ({PREVIEW_WIDTH}x{int(crop_y)})")

        # Restore flex layout for the full view
        driver.execute_script(
            "const graph = document.querySelector('.dash-graph');"
            "if (graph) graph.style.height = '100%';"
            "const chartCol = graph && graph.parentElement;"
            "if (chartCol) { chartCol.style.flex = '1 1 0%'; chartCol.style.height = ''; }"
            "const flex = chartCol && chartCol.parentElement;"
            "if (flex) flex.style.minHeight = '';"
            "const plot = document.querySelector('.js-plotly-plot');"
            "if (plot && window.Plotly) Plotly.Plots.resize(plot);"
        )
        time.sleep(0.5)

        # Image 2: Full page — expand to capture everything
        page_height = driver.execute_script(
            "return document.body.scrollHeight"
        )
        driver.set_window_size(1400, page_height)
        time.sleep(0.5)
        out_2 = IMAGES_DIR / "app_image_02_full_view.png"
        driver.save_screenshot(str(out_2))
        print(f"Saved: {out_2}")

    finally:
        driver.quit()


if __name__ == "__main__":
    main()
