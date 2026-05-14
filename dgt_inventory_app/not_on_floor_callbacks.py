import gspread
from oauth2client.service_account import ServiceAccountCredentials

def connect_to_google_sheets():
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_name(
        r"C:\\Users\\inven\\OneDrive\\Documents\\automation_and_documentation\\dgt_inventory_app\\credentials\\credentials.json",
        scope
    )
    client = gspread.authorize(creds)
    spreadsheet = client.open("Private Inventory Sheet")
    return spreadsheet

spreadsheet = connect_to_google_sheets()

def fetch_not_on_floor_data():
    sheet = spreadsheet.worksheet("Not On Floor")
    values = sheet.get_all_values()
    if not values or len(values) < 2:
        return [], []
    header = values[0][:9]
    rows = [row[:9] for row in values[1:]]
    data = [dict(zip(header, row)) for row in rows]
    return data, header

def get_unique_options(data, col):
    return sorted(list({row.get(col, "") for row in data if row.get(col, "").strip()}))
