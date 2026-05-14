import gspread
from oauth2client.service_account import ServiceAccountCredentials
from dash import callback_context
from dash.dependencies import Input, Output, State
import dash

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
    helper_sheet = spreadsheet.worksheet("Helper Data")
    return spreadsheet, helper_sheet

spreadsheet, helper_sheet = connect_to_google_sheets()

def get_restock_data_table():
    try:
        restock_sheet = spreadsheet.worksheet("Restock")
        restock_values = restock_sheet.get_all_values()
        if not restock_values:
            return None, None, None
        header = restock_values[0][:8]
        rows = [row[:8] for row in restock_values[1:]]
        data = [dict(zip(header, row)) for row in rows]
        columns = [{"name": col, "id": col} for col in header]
        return data, columns, header
    except Exception:
        return None, None, None

def get_product_name_color_map(restock_data):
    color_names = helper_sheet.col_values(62)[1:]
    product_names = [row.get("Product Name", "") for row in restock_data] if restock_data else []
    color_lookup = {
        "Yellow": "#fbc02d",
        "Green": "#43a047",
        "Red": "#e53935",
    }
    color_map = {}
    for product_name, color_name in zip(product_names, color_names):
        color = color_lookup.get(color_name.strip(), None)
        if color and product_name:
            color_map[product_name] = color
    return color_map

def product_name_style_conditional(color_map, restock_data):
    style_rules = []
    if color_map and restock_data:
        for row_idx, row in enumerate(restock_data):
            pname = row.get("Product Name", "")
            color = color_map.get(pname)
            if color:
                style_rules.append({
                    "if": {"row_index": row_idx, "column_id": "Product Name"},
                    "backgroundColor": color,
                    "color": "#222" if color == "#fbc02d" else "#fff"
                })
    return style_rules

# Add callback for restock color buttons

def register_restock_callbacks(app):
    @app.callback(
        Output("restock-selected-cell", "clear_data"),
        [Input("restock-green-btn", "n_clicks"),
         Input("restock-yellow-btn", "n_clicks"),
         Input("restock-red-btn", "n_clicks")],
        [State("restock-selected-cell", "data"),
         State("restock-table-color-map", "data")],
        prevent_initial_call=True
    )
    def update_restock_color(green_click, yellow_click, red_click, selected_cell, color_map):
        import time
        ctx = callback_context
        if not ctx.triggered or not selected_cell:
            return dash.no_update
        btn_id = ctx.triggered[0]["prop_id"].split(".")[0]
        color_name = None
        if btn_id == "restock-green-btn":
            color_name = "Green"
        elif btn_id == "restock-yellow-btn":
            color_name = "Yellow"
        elif btn_id == "restock-red-btn":
            color_name = "Red"
        if color_name is None:
            return dash.no_update

        row_idx = selected_cell.get("row")
        col_id = selected_cell.get("column")
        if row_idx is None:
            return dash.no_update

        restock_sheet = spreadsheet.worksheet("Restock")
        header = restock_sheet.row_values(1)
        try:
            col_index = header.index(col_id)
        except ValueError:
            return dash.no_update
        sheet_id = restock_sheet._properties['sheetId']
        start_row = row_idx + 1
        start_col = col_index
        color_lookup = {
            "Green": {"red": 0.262, "green": 0.627, "blue": 0.278},
            "Yellow": {"red": 0.984, "green": 0.753, "blue": 0.176},
            "Red": {"red": 0.898, "green": 0.224, "blue": 0.207},
        }
        color_rgb = color_lookup[color_name]
        body = {
            "requests": [
                {
                    "repeatCell": {
                        "range": {
                            "sheetId": sheet_id,
                            "startRowIndex": start_row,
                            "endRowIndex": start_row + 1,
                            "startColumnIndex": start_col,
                            "endColumnIndex": start_col + 1,
                        },
                        "cell": {
                            "userEnteredFormat": {
                                "backgroundColor": color_rgb
                            }
                        },
                        "fields": "userEnteredFormat.backgroundColor"
                    }
                }
            ]
        }
        spreadsheet.batch_update(body)
        # Write color name to Helper Data column BJ (col 62)
        helper_row = row_idx + 2  # +2 for header and 1-based index
        helper_col = 62  # BJ is column 62
        try:
            helper_sheet.update_cell(helper_row, helper_col, color_name)
        except Exception:
            pass
        time.sleep(1)
        return None
