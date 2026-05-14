# BuzzScraper (Playwright)

This is a Chromium-based replacement for the original Selenium `BuzzScraper_V3.py` scraper. It uses Playwright to drive headless Chromium and writes the same CSV format.

## Install

1. Create and activate a Python virtual environment (recommended):

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
pip install -r requirements_playwright.txt
python -m playwright install chromium
```

## Run

```powershell
python BuzzScraper_playwright.py
```

Notes:
- Adjust `output_path` inside `BuzzScraper_playwright.py` if you want a different CSV location.
- If the site changes selectors, update the CSS/XPath in the script accordingly.
