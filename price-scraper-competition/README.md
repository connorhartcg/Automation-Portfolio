# Generalized Price Comparison to Competitors Webscraper

This project is a flexible, Python-based web scraper and product matcher that allows cannabis retailers to compare their in-house product listings against public competitor menus (e.g., Weedmaps, Buzz Cannabis). It supports brand, category, weight normalization, and fuzzy name matching, and is designed to help identify pricing gaps.

---

## 🔍 Features

- Scrapes competitor product names, brands, and prices
- Extracts standardized categories (e.g., Vape, Edible, Flower) using synonym mapping
- Extracts weight from product names or price fields with deduplication logic
- Identifies special terms like `Rosin`, `T1`, `T2`, etc.
- Fuzzy matching between store products and competitor items
- Deduplicates matched records unless price variants exist
- Outputs structured CSV reports for manual review or automation pipelines

---

## 🧠 Use Case

Perfect for store operators looking to:
- Reprice inventory based on current local competition
- Simplify category and weight classification across multiple vendors
- Feed results into automation tools (like Power Automate or Google Sheets workflows)

---

## 🧰 Requirements

Install the required Python packages with:

```bash
pip install -r requirements.txt

*📎 Notes
#Designed to work with paginated menus and dynamic content (via Selenium).

#Duplicate filtering ensures unique Brand + Category + Weight combinations unless pricing differs.

#Easily extensible to additional competitor sites.