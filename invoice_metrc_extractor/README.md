# Invoice Renamer & Organizer

This Python script automates the process of scanning, renaming, and organizing invoices based on extracted data. It is designed to work in tandem with a Power Automate flow that controls the Kyocera scan software, making mass invoice processing nearly hands-free.

## 🔧 Features

- Monitors a folder for new scanned invoice PDFs.
- Uses OCR and text extraction to find:
  - **METRC Manifest Numbers** (last 6 digits).
  - **Distributor Names** (matched against a known list).
- Renames files in the format: `<DistributorName>_<METRC#>.pdf`.
- Cleans distributor names to remove spaces and special characters.
- Automatically moves renamed files to a target folder.
- Logs progress and errors clearly to the console.

## 📁 Folder Setup

| Folder | Purpose |
|--------|---------|
| `Downloads` | Watch folder for new scanned files (e.g., `kyoScan*.pdf`) |
| `Mass Invoices` | Destination folder for renamed and organized invoices |
| `Automation\DistributorList.csv` | CSV file with one distributor name per row (used for fuzzy matching) |

## 📋 Workflow

1. Place paper invoices in the printer.
2. Start the Power Automate flow (automates scan/start/back actions).
3. Press Enter in the terminal to initiate the script.
4. Each scan is automatically processed, renamed, and filed.
5. After each invoice, press Enter again to proceed with the next one.

## 🛠️ Dependencies

Install required libraries with:

```bash
pip install -r requirements.txt

🔁 Naming Format
The output files will be named like:

ApolloCultivationManagement_123456.pdf

ApolloCultivationManagement is the cleaned distributor name.

123456 is the last six digits of the METRC manifest number.

🧠 Notes
Includes fuzzy matching to identify slightly misspelled or poorly OCR’d distributor names.

Designed for retroactive batch scanning of invoices with minimal user input.

Integrates seamlessly with automated scanner workflows for maximum efficiency.