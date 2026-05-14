# 🌿 Weedmaps Unverified Product Matching Automation

This automation pipeline streamlines the process of identifying and matching unverified cannabis products in our internal inventory to their verified counterparts listed on Weedmaps.

The workflow reduces manual form-filling and cross-referencing time using Python for scraping and fuzzy matching, and Power Automate Desktop (PAD) for browser automation.

---

## 🧠 Overview

**Goal:**  
Match unverified local product entries to verified Weedmaps listings and automate the submission process.

**Technologies Used:**  
- Python (scraping + matching)
- Power Automate Desktop (form automation)
- Google Sheets (for product management)
- CSV I/O

---

## ⚙️ How It Works

### Step 1: Extract Brand Names
A CSV containing unverified products is parsed to extract all unique brand names that need verification.

### Step 2: Scrape Verified Products from Weedmaps
For each brand:
- The script constructs a URL like `https://weedmaps.com/brands/<brand>/menu`.
- It scrapes all verified product names listed.
- The results are saved in `verified_products.csv`.

### Step 3: Fuzzy Matching
- A second script loads both unverified and verified product lists.
- It uses fuzzy string comparison (`rapidfuzz`) to find best matches.
- The output (`matched_results.csv`) includes confidence scores and recommended matches.

### Step 4: Automate Form Filling with PAD
- PAD reads `matched_results.csv`.
- It inputs matched names into the Weedmaps UI automatically, saving significant manual effort.

---

## 📁 Project Structure

```plaintext
weedmaps_verified_products/
├── python_scripts/
│   ├── weedmaps_unverified_products_scraper.py
│   ├── verify_product_match.py
├── datasheets/
│   ├── unverified_brands.csv
│   ├── weedmaps_products.csv
│   ├── unverified_products_comparison_list.csv
│   ├── unverified_matched_products.csv
│   └── matched_verified_pas_sheet.csv
├── screenshots/
│   └──
├── README.md
├── requirements.txt
└── power_automate/
    └──

📦 Install Dependencies
### Create a virtual environment and install required packages:
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
