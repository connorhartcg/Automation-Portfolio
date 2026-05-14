import dash
from dash import html, dcc, Input, Output, State, callback_context, dash_table
import dash_bootstrap_components as dbc
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import base64
import re
import time
from drawer_flower.drawer_flower_section import drawer_flower_section  # updated import for new directory
from restock_callbacks import get_restock_data_table, get_product_name_color_map
from restock_section import restock_section
from not_on_floor_section import not_on_floor_section
from graphics_tools_section import graphics_tools_section

# ---- HELPER FUNCTIONS ----
def rgb_dict_to_hex(bg):
    r = int(round(bg.get('red', 0) * 255))
    g = int(round(bg.get('green', 0) * 255))
    b = int(round(bg.get('blue', 0) * 255))
    return f"#{r:02x}{g:02x}{b:02x}"

def get_color_rgb(color_name):
    color_map = {
        "Green": {"red": 0.262, "green": 0.627, "blue": 0.278},
        "Yellow": {"red": 0.984, "green": 0.753, "blue": 0.176},
        "Red": {"red": 0.898, "green": 0.224, "blue": 0.207},
    }
    return color_map.get(color_name, {"red": 1, "green": 1, "blue": 1})

# ---- GOOGLE SHEETS CONNECTION ----
def connect_to_google_sheets():
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_name(
        r"C:\Users\inven\OneDrive\Documents\automation_and_documentation\dgt_inventory_app\credentials\credentials.json",
        scope
    )
    client = gspread.authorize(creds)
    inventory_sheet = client.open("Private Inventory Sheet")
    drawer_data_sheet = client.open("InventoryQuickSheet").worksheet("DrawerData")
    graphics_tools_sheet = client.open("Graphics Tools").worksheet("DrawerData")
    return inventory_sheet, drawer_data_sheet, graphics_tools_sheet

spreadsheet, drawer_data_sheet, graphics_tools_sheet = connect_to_google_sheets()
sheet = spreadsheet.worksheet("DrawerFlower")

# ---- FETCH DATA ----
# (Moved to drawer_flower_utils.py)
# top_cells, bottom_cells = fetch_data(sheet)

helper_sheet = spreadsheet.worksheet("Helper Data")
dropdown_values = drawer_data_sheet.col_values(54)[1:]  # BB is column 54, skip header

def get_lineage_options(category):
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

indica_options = get_lineage_options("INDICA")
hybrid_options = get_lineage_options("HYBRID")
sativa_options = get_lineage_options("SATIVA")

# ---- RESTOCK SECTION ----
# (Moved to restock_section.py and restock_callbacks.py)

# ---- NOT ON FLOOR SECTION ----
def fetch_not_on_floor_data():
    sheet = spreadsheet.worksheet("Not On Floor")
    values = sheet.get_all_values()
    if not values or len(values) < 2:
        return [], []
    header = values[0][:9]
    rows = [row[:9] for row in values[1:]]
    data = [dict(zip(header, row)) for row in rows]
    return data, header

not_on_floor_data, not_on_floor_header = fetch_not_on_floor_data()

def get_unique_options(data, col):
    return sorted(list({row.get(col, "") for row in data if row.get(col, "").strip()}))

not_on_floor_brand_options = get_unique_options(not_on_floor_data, "Brand")
not_on_floor_category_options = get_unique_options(not_on_floor_data, "Category")
not_on_floor_lineage_options = get_unique_options(not_on_floor_data, "Lineage")

# ---- DASH APP LAYOUT ----
logo_path = r"C:\\Users\\inven\\OneDrive\\Documents\\automation_and_documentation\\assets\\brand_photos\\Logos\\DrGreenthumbs_Logo.png"
logo_img_src = None
if os.path.exists(logo_path):
    with open(logo_path, "rb") as image_file:
        encoded = base64.b64encode(image_file.read()).decode()
        logo_img_src = f"data:image/png;base64,{encoded}"

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY], title="DGT Interface", suppress_callback_exceptions=True)

# --- PAGE HEADER ---
app.layout = html.Div([
    html.Div(id="update-feedback", className="update-feedback"),
    html.Div([
        html.H1(
            "Dr. Greenthumb's Inventory Interface",
            className="main-title page-header-title",
        )
    ], className="page-header"),
    # --- MENU BAR ---
    html.Div([
        dbc.Button("Drawer Flower", id="menu-drawer-btn", color="secondary", outline=True, className="menu-btn"),
        dbc.Button("Restock List", id="menu-restock-btn", color="secondary", outline=True, className="menu-btn"),
        dbc.Button("Not On Floor", id="menu-nof-btn", color="secondary", outline=True, className="menu-btn"),
        dbc.Button("Graphics Tools", id="menu-graphics-tools-btn", color="secondary", outline=True, className="menu-btn")
    ], className="sticky-menu-bar"),
    dcc.Store(id="scroll-dummy"),
    dcc.Store(id="active-menu-bar"),
    dcc.Store(id="selected-square-store"),
    dcc.Store(id="hovered-square-store"),
    dcc.Store(id="selected-square-index-store"),
    # --- ANCHOR FOR Drawer Flower ---
    drawer_flower_section(),  # Now called with no arguments; section handles its own data fetching
    # --- ANCHOR FOR Restock List ---
    html.Div(id="restock-list-section"),
    restock_section(),
    # --- ANCHOR FOR Not On Floor ---
    html.Div(id="not-on-floor-section"),
    not_on_floor_section(),
    # --- ANCHOR FOR Graphics Tools ---
    html.Div(id="graphics-tools-section-anchor"),
    graphics_tools_section(),
], className="main-app-bg")

# Import Drawer Flower callbacks (must be after app/layout definition)
from drawer_flower import drawer_flower_callbacks  # updated import for new directory
from restock_callbacks import *  # Import all restock callbacks
from not_on_floor_callbacks import *  # Import all not on floor callbacks
# Remove the callback for graphics tools section from this file, as it is now in graphics_tools_callbacks.py

# ---- CALLBACKS ----
@app.callback(
    Output("fixed-dropdowns", "style"),
    Output("selected-square-store", "data"),
    Output("selected-text", "children"),
    Output("custom-dropdown", "value"),
    Output("lineage-dropdown", "value"),
    Output("selected-square-index-store", "data"),
    [Input({'type': 'square', 'index': dash.ALL}, 'n_clicks'),
     Input("drawerflower-x-btn", "n_clicks")],
    [State({'type': 'square', 'index': dash.ALL}, 'children'),
     State("custom-dropdown", "value"),
     State("lineage-dropdown", "value")],
    prevent_initial_call=True
)
def handle_square_and_reset(square_clicks, x_click, children, custom_value, lineage_value):
    ctx = callback_context
    if not ctx.triggered:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update
    trigger = ctx.triggered[0]['prop_id']
    if trigger == 'drawerflower-x-btn.n_clicks':
        return {"display": "none"}, None, "", None, None, None
    # Improved: Use triggered input to get the index
    if square_clicks and any(square_clicks):
        # Find which square was just clicked
        for i, (n, t) in enumerate(zip(square_clicks, ctx.inputs_list[0])):
            if ctx.triggered[0]['prop_id'] == f"{{'type':'square','index':{i}}}.n_clicks":
                idx = i
                break
        else:
            idx = square_clicks.index(max(square_clicks))
        content = None
        if children[idx] and isinstance(children[idx], list):
            for child in children[idx]:
                if isinstance(child, dict) and child.get('props', {}).get('className') == 'square-content':
                    content = child['props'].get('children', '')
                    break
        if not content:
            content = ''
        row = "TOP" if idx < 42 else "BOTTOM"
        selected_text = f"Selected: {content}"
        return {"display": "flex"}, {
            "index": int(idx),
            "row": row,
            "text": content
        }, selected_text, None, None, int(idx)
    return {"display": "none"}, None, "", None, None, None

@app.callback(
    Output("lineage-dropdown", "options"),
    Output("lineage-dropdown", "style"),
    Output("custom-dropdown", "style"),
    [Input("selected-square-store", "data"),
     Input("custom-dropdown", "value"),
     Input("lineage-dropdown", "value")],
    prevent_initial_call=True
)
def update_lineage_dropdown(selected_square, custom_value, lineage_value):
    if not selected_square:
        return [], {"display": "none"}, {"minWidth": "180px", "backgroundColor": "#222", "color": "#e0e0e0", "display": "none"}
    text = selected_square.get("text", "").upper()
    opts = []
    show_lineage = False
    show_custom = True
    if "INDICA" in text:
        opts = indica_options
        show_lineage = True
    elif "HYBRID" in text:
        opts = hybrid_options
        show_lineage = True
    elif "SATIVA" in text:
        opts = sativa_options
        show_lineage = True
    if custom_value and custom_value != "Manual Change":
        show_lineage = False
    if lineage_value:
        show_custom = False
    lineage_style = {"display": "inline-block", "minWidth": "180px", "backgroundColor": "#222", "color": "#e0e0e0"} if show_lineage else {"display": "none"}
    custom_style = {"minWidth": "180px", "backgroundColor": "#222", "color": "#e0e0e0", "display": "inline-block" if show_custom else "none"}
    lineage_options = [{"label": o, "value": o} for o in opts] if show_lineage else []
    return lineage_options, lineage_style, custom_style

@app.callback(
    Output("not-on-floor-table", "data"),
    Output("not-on-floor-table", "style_data_conditional"),
    [Input("nof-brand-filter", "value"),
     Input("nof-category-filter", "value"),
     Input("nof-lineage-filter", "value"),
     Input("nof-name-filter", "value"),
     Input("nof-name-mode", "value")],
    State("not-on-floor-raw-data", "data")
)
def filter_not_on_floor_table(brand, category, lineage, name, name_mode, raw_data):
    import datetime
    if not raw_data:
        return [], []
    filtered = raw_data
    # Brand filter
    if brand:
        filtered = [row for row in filtered if row.get("Brand") in brand]
    # Category filter
    if category:
        filtered = [row for row in filtered if row.get("Category") in category]
    # Lineage filter
    if lineage:
        filtered = [row for row in filtered if row.get("Lineage") in lineage]
    # Product Name filter
    if name:
        if name_mode == "contains":
            filtered = [row for row in filtered if name.lower() in row.get("Product Name", "").lower()]
        else:
            filtered = [row for row in filtered if name.lower() not in row.get("Product Name", "").lower()]
    # Highlight Accepted Date > 30 days and sort
    style_conditional = []
    today = datetime.datetime.now().date()
    red_rows = []
    normal_rows = []
    for i, row in enumerate(filtered):
        date_str = row.get("Accepted Date", "")
        try:
            accepted = datetime.datetime.strptime(date_str, "%m/%d/%Y").date()
            if (today - accepted).days > 30:
                red_rows.append(row)
            else:
                normal_rows.append(row)
        except Exception:
            normal_rows.append(row)
    # Now, red_rows first, then normal_rows
    sorted_filtered = red_rows + normal_rows
    # Rebuild style_conditional for sorted_filtered
    for i, row in enumerate(sorted_filtered):
        date_str = row.get("Accepted Date", "")
        try:
            accepted = datetime.datetime.strptime(date_str, "%m/%d/%Y").date()
            if (today - accepted).days > 30:
                style_conditional.append({
                    "if": {"row_index": i},
                    "backgroundColor": "#e53935",
                    "color": "#fff"
                })
        except Exception:
            pass
    return sorted_filtered, style_conditional

app.clientside_callback(
    "(function(n, prev) { return n; })",
    Output("hovered-square-store", "data"),
    [Input({'type': 'square', 'index': dash.ALL}, 'n_mouseover')],
    [State("hovered-square-store", "data")],
    prevent_initial_call=True
)

@app.callback(
    Output("restock-fixed-btns", "style"),
    [Input("restock-table", "selected_cells"), Input("restock-deselect-btn", "n_clicks")],
    prevent_initial_call=True
)
def show_restock_fixed_btns(selected_cells, x_click):
    ctx = callback_context
    if ctx.triggered and ctx.triggered[0]["prop_id"].startswith("restock-deselect-btn"):
        return {"display": "none"}
    if selected_cells and len(selected_cells) > 0:
        return {
            "position": "fixed",
            "bottom": "20px",
            "left": "50%",
            "transform": "translateX(-50%)",
            "backgroundColor": "#181818",
            "padding": "15px",
            "borderRadius": "12px",
            "display": "flex",
            "flexDirection": "row",
            "alignItems": "center",
            "gap": "20px",
            "zIndex": 20001
        }
    return {"display": "none"}

@app.callback(
    Output("restock-data-store", "data"),
    Output("restock-columns-store", "data"),
    Output("restock-table-color-map", "data"),
    Input("restock-refresh-interval", "n_intervals"),
    prevent_initial_call=False
)
def refresh_restock_data(n):
    restock_data_new, restock_columns_new, _ = get_restock_data_table()
    color_map_new = get_product_name_color_map(restock_data_new)
    return restock_data_new, restock_columns_new, color_map_new

@app.callback(
    Output("restock-table", "selected_cells"),  # Deselect after action
    [
        Input("restock-restocked-btn", "n_clicks"),
        Input("restock-noneed-btn", "n_clicks"),
        Input("restock-cantfind-btn", "n_clicks")
    ],
    [
        State("restock-table", "selected_cells"),
        State("restock-data-store", "data"),
    ],
    prevent_initial_call=True
)
def handle_restock_action(restocked_click, noneed_click, cantfind_click, selected_cells, restock_data):
    ctx = callback_context
    if not ctx.triggered or not selected_cells or not restock_data:
        return dash.no_update
    btn_id = ctx.triggered[0]["prop_id"].split(".")[0]
    color_map = {
        "restock-restocked-btn": ("Green", {"red": 0.262, "green": 0.627, "blue": 0.278}),
        "restock-noneed-btn": ("Yellow", {"red": 0.984, "green": 0.753, "blue": 0.176}),
        "restock-cantfind-btn": ("Red", {"red": 0.898, "green": 0.224, "blue": 0.207}),
    }
    if btn_id not in color_map:
        return dash.no_update
    color_name, rgb = color_map[btn_id]
    # Only handle first selected cell
    cell = selected_cells[0]
    row = cell.get("row")
    col = cell.get("column")
    # Get product name from data
    try:
        product_name = restock_data[row]["Product Name"]
    except Exception:
        return dash.no_update
    # Update Google Sheets
    try:
        # Update fill color in Restock sheet
        restock_ws = spreadsheet.worksheet("Restock")
        # Find the row in the sheet for this product
        restock_values = restock_ws.get_all_values()
        header = restock_values[0]
        product_col = header.index("Product Name")
        for i, row_vals in enumerate(restock_values[1:], start=2):
            if row_vals[product_col] == product_name:
                # Color the row (A:Z for now)
                restock_ws.format(f"A{i}:Z{i}", {{"backgroundColor": rgb}})
                break
        # Write color name to Helper Data sheet
        helper_ws = spreadsheet.worksheet("Helper Data")
        helper_values = helper_ws.get_all_values()
        helper_header = helper_values[0]
        product_col_h = helper_header.index("Product Name")
        color_col_h = helper_header.index("Restock Color")
        for j, row_vals in enumerate(helper_values[1:], start=2):
            if row_vals[product_col_h] == product_name:
                helper_ws.update_cell(j, color_col_h + 1, color_name)
                break
    except Exception as e:
        print(f"Restock action error: {e}")
        return dash.no_update
    # Deselect cell after action
    return []

# --- CLIENTSIDE CALLBACK FOR SMOOTH SCROLLING ---
app.clientside_callback(
    """
    function(drawer, restock, nof, graphics) {
        var mapping = {
            'menu-drawer-btn': 'drawer-flower-section',
            'menu-restock-btn': 'restock-list-section',
            'menu-nof-btn': 'not-on-floor-section',
            'menu-graphics-tools-btn': 'graphics-tools-section-anchor'
        };
        var ctx = window.dash_clientside.callback_context;
        if (!ctx.triggered.length) return window.dash_clientside.no_update;
        var btn_id = ctx.triggered[0].prop_id.split('.')[0];
        var anchor_id = mapping[btn_id];
        if (anchor_id) {
            var anchor = document.getElementById(anchor_id);
            if (anchor) {
                anchor.scrollIntoView({behavior: 'smooth', block: 'start'});
            }
        }
        return window.dash_clientside.no_update;
    }
    """,
    Output('scroll-dummy', 'data'),
    [Input('menu-drawer-btn', 'n_clicks'),
     Input('menu-restock-btn', 'n_clicks'),
     Input('menu-nof-btn', 'n_clicks'),
     Input('menu-graphics-tools-btn', 'n_clicks')],
    prevent_initial_call=True
)

if __name__ == "__main__":
    from waitress import serve
    serve(app.server, host="0.0.0.0", port=8051)
# To run the app, use the command:
#.venv\Scripts\activate
#python dgt_inventory_dash_app_test.py