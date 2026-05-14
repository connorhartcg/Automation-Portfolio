from dash import html
import os
import base64
import re

def make_square(content, index, selected_idx=None, hovered_idx=None):
    first_line = content.split('\n')[0]
    brand_name = first_line.split(':')[0].strip().replace(' ', '').upper()
    logo_filename = f"{brand_name}_Logo.png"
    logos_dir = r"C:\\Users\\inven\\OneDrive\\Documents\\automation_and_documentation\\assets\\brand_photos\\Logos\\"
    logo_path = os.path.join(logos_dir, logo_filename)
    content_upper = content.upper()
    qty_match = re.search(r"SALES FLOOR QTY:\s*(\d+)", content_upper)
    qty = int(qty_match.group(1)) if qty_match else None
    if qty is not None and qty <= 3:
        color = "#e53935"
    elif "INDICA" in content_upper:
        color = "#7c4dff"
    elif "SATIVA" in content_upper:
        color = "#ffa726"
    elif "HYBRID" in content_upper:
        color = "#43a047"
    else:
        color = "#bdbdbd"
    classes = "square"
    try:
        idx_int = int(index)
    except Exception:
        idx_int = index
    try:
        sel_idx_int = int(selected_idx) if selected_idx is not None else None
    except Exception:
        sel_idx_int = selected_idx
    try:
        hov_idx_int = int(hovered_idx) if hovered_idx is not None else None
    except Exception:
        hov_idx_int = hovered_idx
    if idx_int >= 42:
        classes += " bottom-row"
    if sel_idx_int is not None and idx_int == sel_idx_int:
        classes += " selected-square"
    elif hov_idx_int is not None and idx_int == hov_idx_int:
        classes += " hovered-square"
    square_style = {
        "backgroundColor": color,
        "position": "relative",
        "overflow": "hidden",
        "color": "white",
        "fontFamily": "Arial, sans-serif",
        "padding": "12px",
        "textAlign": "center",
        "fontSize": "14px",
        "fontWeight": "bold",
        "borderRadius": "8px",
        "width": "108px",
        "height": "108px",
        "display": "flex",
        "alignItems": "center",
        "justifyContent": "center",
        "transition": "transform 0.2s, border 0.2s",
        "cursor": "pointer",
        "backgroundBlendMode": "normal",
        "backgroundRepeat": "no-repeat",
        "backgroundPosition": "center",
        "backgroundSize": "contain"
    }
    if os.path.exists(logo_path):
        with open(logo_path, "rb") as image_file:
            encoded = base64.b64encode(image_file.read()).decode()
            square_style["backgroundImage"] = f"url('data:image/png;base64,{encoded}')"
    return html.Div([
        html.Div(content, className="square-content")
    ], id={"type": "square", "index": index}, className=classes, n_clicks=0, style=square_style)

def render_grid(top_cells, bottom_cells, selected_idx=None, hovered_idx=None):
    return html.Div([
        html.Div([make_square(item, idx, selected_idx, hovered_idx) for idx, item in enumerate(top_cells)],
                 className="drawerflower-row-top", style={"display": "flex", "flexDirection": "row", "gap": "10px", "marginBottom": "10px"}),
        html.Div([make_square(item, idx+42, selected_idx, hovered_idx) for idx, item in enumerate(bottom_cells)],
                 className="drawerflower-row-bottom", style={"display": "flex", "flexDirection": "row", "gap": "10px"})
    ], style={"overflowX": "auto", "display": "block", "width": "100%"})

# ---- FETCH DATA ----
def fetch_data():
    import gspread
    from oauth2client.service_account import ServiceAccountCredentials
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
    sheet = spreadsheet.worksheet("DrawerFlower")
    values = sheet.get_all_values()
    # Get top row (row 2) and bottom row (row 12) using columns B, F, J, ...
    col_indices = [1 + 4*i for i in range(42)]  # B=1, F=5, J=9, ...
    top_row_idx = 1  # Row 2 (0-based index)
    bottom_row_idx = 11  # Row 12 (0-based index)
    top_cells = [values[top_row_idx][col] if col < len(values[top_row_idx]) else '' for col in col_indices]
    bottom_cells = [values[bottom_row_idx][col] if col < len(values[bottom_row_idx]) else '' for col in col_indices]
    return top_cells, bottom_cells

# Helper for lineage options
def get_lineage_options(category):
    import gspread
    from oauth2client.service_account import ServiceAccountCredentials
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_name(
        r"C:\\Users\\inven\\OneDrive\\Documents\\automation_and_documentation\\dgt_inventory_app\\credentials\\credentials.json",
        scope
    )
    client = gspread.authorize(creds)
    drawer_data_sheet = client.open("InventoryQuickSheet").worksheet("DrawerData")
    column_map = {
        "INDICA": 18,
        "SATIVA": 42,
        "HYBRID": 30
    }
    col_num = column_map.get(category)
    if not col_num:
        return []
    values = drawer_data_sheet.col_values(col_num)[1:]
    return [v for v in values if v.strip()]

# Option fetchers (to be called in main app or section)
def get_drawer_flower_options(drawer_data_sheet):
    indica_options = get_lineage_options(drawer_data_sheet, "INDICA")
    hybrid_options = get_lineage_options(drawer_data_sheet, "HYBRID")
    sativa_options = get_lineage_options(drawer_data_sheet, "SATIVA")
    return indica_options, hybrid_options, sativa_options
