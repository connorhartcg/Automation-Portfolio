# 🧾 Google Sheets Autocrat Generators

This system streamlines the creation of **Strain Cards**, **Preroll Cards**, and **Display Tags** for cannabis retail environments by combining **Google Sheets**, **Autocrat**, and your **POS inventory export data**.

---

## 🚀 Overview

Scan a product SKU from the sales floor into Column A of the appropriate sheet. The rest of the product information—such as strain name, weight, lineage, type, THC/CBD values, and brand—autofills using built-in Google Sheets formulas.

Then, launch the appropriate Autocrat flow:
- **Strain Card Generator**
- **Preroll Card Generator**
- **Display Tag Generator**

Autocrat will auto-generate PDFs or documents for printing and display.

---

## 📂 File Structure

Each label or tag type uses a dedicated Google Sheet with its own Autocrat configuration:

### 1. **Strain Card Generator**
- For **loose flower displays**
- Autofills strain name, lineage, THC%, type, and brand
- Designed to present consumer-facing terpene and genetic info

### 2. **Preroll Card Generator**
- For **preroll trays and bins**
- Displays strain type, size, brand, and quick reference icons
- Optimized for quick shelf recognition and compliance

### 3. **Display Tag Generator**
- For **general retail shelf tags**
- Includes SKU, price, strain name, and size
- Can be used for edibles, cartridges, topicals, and more

---

## 🧠 How It Works

1. **Export** inventory data from your POS system (e.g., Blaze, Meadow, Treez) into the **source sheet**.
2. **Paste or scan** the SKU into Column A of the relevant sheet.
3. Google Sheets **formulas** automatically pull all relevant data from the source sheet.
4. Launch **Autocrat** from the Extensions menu.
5. Run the preconfigured **Autocrat merge flow** (Strain Card, Preroll Card, or Display Tag).
6. Download or print the generated labels from your Google Drive.

---

## 📦 Inputs

- **Column A**: SKU (scanned or typed)
- Data Source: Imported POS CSV or linked tab

Autofilled columns include:
- Product name
- Strain name
- Brand
- Size/weight
- Lineage (if available)
- Product category
- THC/CBD %
- Special terms (e.g., Rosin, T1, T2)

---

## 🛠 Setup Guide

1. Open the relevant Google Sheet.
2. Paste or link the POS export into a raw data tab.
3. Ensure formulas in the tag/card generator tab are working.
4. Confirm Autocrat merge templates are still connected (after duplication or renaming).
5. Customize layouts in the Google Docs Autocrat templates as needed.

---

## 🔄 Autocrat Merge Tips

- Autocrat templates must include `<<merge tags>>` that exactly match the column headers.
- Autocrat can export to PDF, Google Docs, or send to email.
- Set merge conditions so that rows only generate cards when Column A (SKU) is filled.

---

## 🧼 Maintenance Notes

- Update formulas and mappings when your POS product schema changes.
- Refresh your source data regularly for accurate results.
- Test Autocrat templates after duplicating the sheet.

---

## 📈 Benefits

- Save hours of manual formatting
- Ensure consistency across product signage
- Enable budtenders to generate tags instantly on the sales floor
- Easy to train staff on using scanning + Autocrat flow

---

## ❓FAQ

**Q: Do I need to change anything to use this on another computer or account?**  
A: Make sure your POS data is copied into the correct raw data tab and that Autocrat templates are linked under your current Google account.

**Q: What if Autocrat isn’t autofilling the tags?**  
A: Check that your merge tags match column headers exactly. Also verify that SKUs are being matched correctly.

**Q: Can I modify the layout of the cards/tags?**  
A: Yes! Just edit the Google Doc template used in the corresponding Autocrat flow.

---

## 🙌 Credits

This system was developed to integrate seamlessly with existing POS data and optimize retail operations for speed, accuracy, and professionalism.
