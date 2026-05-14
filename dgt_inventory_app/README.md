# 🗂️ DGT Inventory Interface App

This app provides an easy-to-use, visual interface for managing our company's inventory data stored in Google Sheets — no advanced data analysis skills required.

## 🚀 Purpose

- Streamline inventory visualization and interaction
- Allow staff to view and work with live inventory data easily
- Remove the need for manual spreadsheet manipulation or technical expertise

## 🛠️ Built With

- [Streamlit](https://streamlit.io/) — Web app framework for Python
- [gspread](https://gspread.readthedocs.io/) — Google Sheets API client
- [oauth2client](https://github.com/googleapis/oauth2client) — Google authentication
- [Google API Python Client](https://github.com/googleapis/google-api-python-client) — Google Drive services

## 📦 Setup Instructions

1. Clone this repository.
2. Create and activate a Python virtual environment (optional but recommended):

    ```bash
    python -m venv venv
    source venv/bin/activate  # Linux/macOS
    venv\Scripts\activate     # Windows
    ```

3. Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

4. Place your `credentials.json` (Google API service account credentials) in the project directory.

5. Run the Streamlit app:

    ```bash
    streamlit run main.py
    ```

## 📄 Requirements

- Google Cloud Platform service account with Sheets and Drive API access
- Access to the company's "Private Inventory Sheet" on Google Sheets

## 📂 Directory Structure

