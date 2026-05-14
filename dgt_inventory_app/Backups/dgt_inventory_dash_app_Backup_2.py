import dash
from dash import html, dcc, Input, Output, State, callback_context, dash_table
import dash_bootstrap_components as dbc
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import base64
import re
import time

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
_last_fetch = {'time': 0, 'top': [], 'bottom': []}
def fetch_data(sheet):
    now = time.time()
    if now - _last_fetch['time'] < 900 and _last_fetch['top'] and _last_fetch['bottom']:
        return _last_fetch['top'], _last_fetch['bottom']
    all_values = sheet.get_all_values()
    top_cells = []
    bottom_cells = []
    for col in range(1, 166, 4):
        try:
            top_cells.append(all_values[1][col])  # B2, F2, ...
        except IndexError:
            top_cells.append("")
        try:
            bottom_cells.append(all_values[11][col])  # B12, F12, ...
        except IndexError:
            bottom_cells.append("")
    _last_fetch['time'] = now
    _last_fetch['top'] = top_cells
    _last_fetch['bottom'] = bottom_cells
    return top_cells, bottom_cells

top_cells, bottom_cells = fetch_data(sheet)

helper_sheet = spreadsheet.worksheet("Helper Data")
dropdown_values = helper_sheet.col_values(54)[1:]  # BB is column 54, skip header

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

# ---- SQUARE TEMPLATE ----
def get_strain_color(content_upper):
    if "INDICA" in content_upper:
        return "purple"
    elif "SATIVA" in content_upper:
        return "orange"
    elif "HYBRID" in content_upper:
        return "green"
    return "lightgray"

def make_square(content, index, selected_idx=None, hovered_idx=None):
    first_line = content.split('\n')[0]
    brand_name = first_line.split(':')[0].strip().replace(' ', '').upper()
    logo_filename = f"{brand_name}_Logo.png"
    logos_dir = r"C:\\Users\\inven\\OneDrive\\Documents\\automation_and_documentation\\assets\\brand_photos\\Logos\\"
    logo_path = os.path.join(logos_dir, logo_filename)
    logo_img_html = None
    content_upper = content.upper()
    color = "red" if "SALES FLOOR QTY" in content_upper and re.search(r"SALES FLOOR QTY:\s*(\d*)", content_upper) and int(re.search(r"SALES FLOOR QTY:\s*(\d*)", content_upper).group(1) or 0) <= 5 else get_strain_color(content_upper)
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
    }
    if os.path.exists(logo_path):
        with open(logo_path, "rb") as image_file:
            encoded = base64.b64encode(image_file.read()).decode()
            square_style["backgroundImage"] = f"url('data:image/png;base64,{encoded}')"
            square_style["backgroundSize"] = "contain"
            square_style["backgroundPosition"] = "center"
            square_style["backgroundRepeat"] = "no-repeat"
    return html.Div([
        html.Div(content, className="square-content", style={"position": "relative", "zIndex": 1, "width": "100%"})
    ], id={"type": "square", "index": index}, className=classes, n_clicks=0, style={**square_style, "backgroundBlendMode": "normal" if os.path.exists(logo_path) else None, "backgroundColor": color, "opacity": 1})

# ---- RESTOCK SECTION ----
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

restock_data, restock_columns, restock_header = get_restock_data_table()
product_name_color_map = get_product_name_color_map(restock_data)
restock_style_conditional = product_name_style_conditional(product_name_color_map, restock_data)

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

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY], title="DGT Interface")

def render_grid(selected_idx=None, hovered_idx=None):
    return html.Div([
        html.Div([make_square(item, idx, selected_idx, hovered_idx) for idx, item in enumerate(top_cells)], style={"display": "flex", "gap": "10px", "marginBottom": "10px", "marginTop": "10px"}),
        html.Div([make_square(item, idx+42, selected_idx, hovered_idx) for idx, item in enumerate(bottom_cells)], style={"display": "flex", "gap": "10px"})
    ], className="scroll-inner")

app.layout = html.Div([
    html.Div(id="update-feedback", style={"marginTop": "20px", "marginBottom": "0px", "display": "flex", "justifyContent": "center", "position": "fixed", "top": 0, "left": 0, "width": "100%", "zIndex": 9999}),
    dbc.Row([
        dbc.Col(html.Img(src=logo_img_src if logo_img_src else "", style={"width": "100px"}), width=1),
        dbc.Col(html.H1("Dr. Greenthumb's Inventory Interface", style={"marginTop": "20px", "color": "white"}), width=8)
    ], align="center"),
    # --- MENU BAR ---
    html.Div([
        dbc.Button("Drawer Flower", id="menu-drawer-btn", color="secondary", outline=True, style={"marginRight": "12px"}),
        dbc.Button("Restock List", id="menu-restock-btn", color="secondary", outline=True, style={"marginRight": "12px"}),
        dbc.Button("Not On Floor", id="menu-nof-btn", color="secondary", outline=True)
    ], style={"display": "flex", "justifyContent": "center", "marginTop": "10px", "marginBottom": "10px", "gap": "10px"}, className="sticky-menu-bar"),
    dcc.Store(id="scroll-dummy"),  # Dummy store for scroll callback
    dcc.Store(id="active-menu-bar"),
    # --- ANCHOR FOR Drawer Flower ---
    html.Div(id="drawer-flower-section"),
    html.Div([
        html.H3("\U0001F5C2 Drawer Flower", style={"textAlign": "left", "color": "white"}),
        html.Div(id="selected-text", style={"color": "white", "fontSize": "18px", "marginBottom": "20px", "fontWeight": "bold"}),
        html.Div(id="dynamic-grid", children=render_grid())  # Set initial grid
    ], className="scroll-container drawerflower-scroll-container", style={
        "display": "flex",
        "flexDirection": "column",
        "padding": "20px",
        "borderRadius": "20px",
        "marginTop": "20px",
        "backgroundColor": "#181818",
        "overflow": "visible",
        "height": "350px"
    }),
    # --- ANCHOR FOR Restock List ---
    html.Div(id="restock-list-section"),
    html.Div([
        html.H3("\U0001F4E6 Restock List", style={"textAlign": "left", "color": "white", "marginTop": "10px"}),
        dash_table.DataTable(
            id="restock-table",
            columns=restock_columns if restock_columns else [],
            data=restock_data if restock_data else [],
            style_cell={
                "backgroundColor": "#222",
                "color": "#fff",
                "border": "1px solid #444",
                "fontSize": 16,
                "textAlign": "left"
            },
            style_header={"backgroundColor": "#333", "color": "#fff", "fontWeight": "bold"},
            style_table={
                "width": "100%",
                "marginTop": "20px",
                "borderRadius": "12px",
                "overflow": "hidden",
                "height": "500px",
                "overflowY": "auto"
            },
            style_cell_conditional=[
                {"if": {"column_id": "Brand"}, "width": "40px"},
                {"if": {"column_id": "Category"}, "width": "60px"},
                {"if": {"column_id": "Lineage"}, "width": "80px"},
                {"if": {"column_id": "Product Name"}, "width": "80px", "fontWeight": "bold"},
                {"if": {"column_id": "Price"}, "width": "80px"},
                {"if": {"column_id": "Receiving"}, "width": "80px"},
                {"if": {"column_id": "Backstock"}, "width": "80px"},
                {"if": {"column_id": "Sales Floor"}, "width": "80px"},
            ],
            style_data_conditional=restock_style_conditional,
            cell_selectable=True,
            row_selectable=False,
            selected_cells=[],
            page_action="none",
            fixed_rows={"headers": True},
            virtualization=False,
        ),
        html.Div(id="color-picker-ui", style={"marginTop": "10px"}),
        dcc.Store(id="restock-selected-cell"),
        dcc.Store(id="restock-table-color-map", data=product_name_color_map),
    ], className="scroll-container restock-scroll-container", style={
        "display": "flex",
        "flexDirection": "column",
        "padding": "20px",
        "borderRadius": "20px",
        "marginTop": "20px",
        "backgroundColor": "#181818",
        "overflow": "visible",
        "height": "700px"
    }),
    # --- ANCHOR FOR Not On Floor ---
    html.Div(id="not-on-floor-section"),
    html.Div([
        html.H3("\U0001F4CB Not On Floor", style={"textAlign": "left", "color": "white", "marginTop": "10px"}),
        html.Div([
            dcc.Dropdown(
                id="nof-brand-filter",
                options=[{"label": b, "value": b} for b in not_on_floor_brand_options],
                placeholder="Filter by Brand",
                multi=True,
                className="custom-dropdown-style"
            ),
            dcc.Dropdown(
                id="nof-category-filter",
                options=[{"label": c, "value": c} for c in not_on_floor_category_options],
                placeholder="Filter by Category",
                multi=True,
                className="custom-dropdown-style"
            ),
            dcc.Dropdown(
                id="nof-lineage-filter",
                options=[{"label": l, "value": l} for l in not_on_floor_lineage_options],
                placeholder="Filter by Lineage",
                multi=True,
                className="custom-dropdown-style"
            ),
            html.Div([
                dcc.RadioItems(
                    id="nof-name-mode",
                    options=[{"label": "Contains", "value": "contains"}, {"label": "Does Not Contain", "value": "not_contains"}],
                    value="contains",
                    labelStyle={"display": "inline-block", "marginRight": "18px", "color": "#fff"}
                ),
                dcc.Input(
                    id="nof-name-filter",
                    type="text",
                    placeholder="Product Name...",
                    style={"width": "200px"}
                )
            ], className="nof-filter-right")
        ], className="nof-filter-row"),
        dash_table.DataTable(
            id="not-on-floor-table",
            columns=[{"name": col, "id": col} for col in not_on_floor_header],
            data=not_on_floor_data,
            style_cell={
                "backgroundColor": "#222",
                "color": "#fff",
                "border": "1px solid #444",
                "fontSize": 15,
                "textAlign": "left"
            },
            style_header={"backgroundColor": "#333", "color": "#fff", "fontWeight": "bold"},
            style_table={
                "width": "100%",
                "marginTop": "10px",
                "borderRadius": "12px",
                "overflow": "hidden",
                "height": "400px",
                "overflowY": "auto"
            },
            style_cell_conditional=[
                {"if": {"column_id": "Product Name"}, "fontWeight": "bold"},
            ],
            page_action="none",
            virtualization=False,
            fixed_rows={"headers": True},  # Freeze header row
        ),
        dcc.Store(id="not-on-floor-raw-data", data=not_on_floor_data)
    ], className="scroll-container notonfloor-scroll-container", style={
        "display": "flex",
        "flexDirection": "column",
        "padding": "20px",
        "borderRadius": "20px",
        "marginTop": "20px",
        "backgroundColor": "#181818",
        "overflow": "visible",
        "height": "500px"
    }),
    html.Div([
        dbc.Button("Restocked", id="restock-green-btn", color="success", style={"marginRight": "8px"}),
        dbc.Button("No Need", id="restock-yellow-btn", color="warning", style={"marginRight": "8px"}),
        dbc.Button("Can't Find", id="restock-red-btn", color="danger", style={"marginRight": "8px"}),
        dbc.Button("✖", id="restock-deselect-btn", color="secondary", style={"marginLeft": "8px", "backgroundColor": "#444", "border": "none", "fontWeight": "bold"})
    ], id="restock-fixed-btns", style={
        "position": "fixed",
        "bottom": "20px",
        "left": "50%",
        "transform": "translateX(-50%)",
        "backgroundColor": "#181818",
        "padding": "15px",
        "borderRadius": "12px",
        "display": "none",
        "flexDirection": "row",
        "alignItems": "center",
        "gap": "20px",
        "zIndex": 20001
    }),
    html.Div([
        dcc.Dropdown(
            id="custom-dropdown",
            options=[{"label": val, "value": val} for val in dropdown_values],
            placeholder="Manual Change",
            style={"display": "none"},
            className="custom-dropdown-style"
        ),
        dcc.Dropdown(
            id="lineage-dropdown",
            options=[{"label": val, "value": val} for val in dropdown_values],
            placeholder="Lineage Options",
            style={"display": "none"},
            className="custom-dropdown-style"
        ),
        dbc.Button("✅", id="confirm-btn", color="success", className="action-btn confirm-btn"),
        html.Button("✖", id="drawerflower-x-btn", className="action-btn drawerflower-x-btn", style={"color": "#b0b0b0", "background": "none", "border": "none", "fontSize": "1.5rem", "marginLeft": "8px", "marginBottom": "2px", "top": "-2px", "position": "relative", "zIndex": 20001, "cursor": "pointer"}),
    ], id="fixed-dropdowns", style={
        "position": "fixed",
        "bottom": "20px",
        "left": "50%",
        "transform": "translateX(-50%)",
        "backgroundColor": "#181818",
        "padding": "15px",
        "borderRadius": "12px",
        "display": "none",
        "flexDirection": "row",
        "alignItems": "center",
        "gap": "20px",
        "color": "#e0e0e0"
    }),
    dcc.Interval(id="data-refresh-interval", interval=300*1000, n_intervals=0),
    dcc.Interval(id="restock-refresh-interval", interval=30*1000, n_intervals=0),
    dcc.Store(id="top-cells-store", data=top_cells),
    dcc.Store(id="bottom-cells-store", data=bottom_cells),
    dcc.Store(id="restock-data-store", data=restock_data),
    dcc.Store(id="restock-columns-store", data=restock_columns),
    dcc.Store(id="selected-square-store"),
    dcc.Store(id="hovered-square-store"),
    dcc.Store(id="selected-square-index-store"),
    dcc.Store(id="selected-restock-cell"),
    dcc.Store(id="restock-table-color-map", data=product_name_color_map),
], style={"backgroundColor": "#000"})

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
    if square_clicks and any(square_clicks):
        max_clicks = max(square_clicks)
        if max_clicks:
            idx = square_clicks.index(max_clicks)
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
    Output("update-feedback", "children"),
    [Input("confirm-btn", "n_clicks")],
    [State("selected-square-store", "data"),
     State("custom-dropdown", "value"),
     State("lineage-dropdown", "value")],
    prevent_initial_call=True
)
def confirm_update(n, selected_square, custom_value, lineage_value):
    if not selected_square:
        return dash.no_update
    idx = selected_square["index"]
    row = selected_square["row"]
    text = selected_square["text"]
    selected_option = lineage_value or custom_value
    if not selected_option or selected_option == "Manual Change":
        return dbc.Alert("Please select a value from one of the dropdowns.", color="warning")
    try:
        target_col = 'R' if row == "TOP" else 'S'
        target_row = int(idx) % 42 + 2
        target_cell = f"{target_col}{target_row}"
        graphics_tools_sheet.update_acell(target_cell, selected_option)
        return dbc.Alert(f"Successfully updated {target_cell} with '{selected_option}' from square '{text}'", color="success", duration=3000)
    except Exception as e:
        return dbc.Alert(f"Failed to update Google Sheets: {e}", color="danger")

@app.callback(
    Output("dynamic-grid", "children"),
    Input("top-cells-store", "data"),
    Input("bottom-cells-store", "data"),
    Input("selected-square-index-store", "data"),
    Input("hovered-square-store", "data"),
)
def update_grid_with_store(top_cells_data, bottom_cells_data, selected_idx, hovered_idx):
    return html.Div([
        html.Div([make_square(item, idx, selected_idx, hovered_idx) for idx, item in enumerate(top_cells_data)], style={"display": "flex", "gap": "10px", "marginBottom": "10px", "marginTop": "10px"}),
        html.Div([make_square(item, idx+42, selected_idx, hovered_idx) for idx, item in enumerate(bottom_cells_data)], style={"display": "flex", "gap": "10px"})
    ], className="scroll-inner")

@app.callback(
    Output("restock-table", "data"),
    Output("restock-table", "columns"),
    Input("restock-data-store", "data"),
    Input("restock-columns-store", "data"),
    prevent_initial_call=False
)
def update_restock_table(data, columns):
    return data, columns

@app.callback(
    Output("top-cells-store", "data"),
    Output("bottom-cells-store", "data"),
    Input("data-refresh-interval", "n_intervals"),
    prevent_initial_call=False
)
def refresh_grid_data(n):
    top, bottom = fetch_data(sheet)
    return top, bottom

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
    Output("restock-selected-cell", "data"),
    [Input("restock-table", "active_cell"),
     Input("restock-deselect-btn", "n_clicks")],
    State("restock-table", "columns"),
    prevent_initial_call=True
)
def store_selected_restock_cell(active_cell, deselect_click, columns):
    ctx = callback_context
    if ctx.triggered and ctx.triggered[0]["prop_id"].startswith("restock-deselect-btn"):
        return None
    if not active_cell:
        return None
    col_id = columns[active_cell["column_id"]]["id"] if isinstance(active_cell["column_id"], int) else active_cell["column_id"]
    return {
        "row": active_cell["row"],
        "column": col_id
    }

@app.callback(
    Output("restock-table", "style_data_conditional"),
    [Input("restock-selected-cell", "data"), Input("restock-table-color-map", "data")],
    [State("restock-table", "data"), State("restock-table", "columns")],
    prevent_initial_call=True
)
def update_table_colors(selected_cell, color_map, data, columns):
    style = []
    if color_map and data:
        for row_idx, row in enumerate(data):
            pname = row.get("Product Name", "")
            color = color_map.get(pname)
            if color:
                style.append({
                    "if": {"row_index": row_idx, "column_id": "Product Name"},
                    "backgroundColor": color,
                    "color": "#222" if color == "#fbc02d" else "#fff"
                })
    if selected_cell and selected_cell.get("row") is not None and selected_cell.get("column") is not None:
        style.append({
            "if": {"row_index": selected_cell["row"], "column_id": selected_cell["column"]},
            "border": "2px solid #fff"
        })
    return style

@app.callback(
    Output("restock-selected-cell", "clear_data"),
    Output("restock-refresh-interval", "n_intervals"),
    [Input("restock-green-btn", "n_clicks"),
     Input("restock-yellow-btn", "n_clicks"),
     Input("restock-red-btn", "n_clicks")],
    [State("restock-selected-cell", "data"),
     State("restock-data-store", "data"),
     State("restock-refresh-interval", "n_intervals")],
    prevent_initial_call=True
)
def update_restock_color(green_click, yellow_click, red_click, selected_cell, restock_data, n_intervals):
    import time
    ctx = callback_context
    if not ctx.triggered or not selected_cell or not restock_data:
        return dash.no_update, dash.no_update
    btn_id = ctx.triggered[0]["prop_id"].split(".")[0]
    color_name = None
    if btn_id == "restock-green-btn":
        color_name = "Green"
    elif btn_id == "restock-yellow-btn":
        color_name = "Yellow"
    elif btn_id == "restock-red-btn":
        color_name = "Red"
    if color_name is None:
        return dash.no_update, dash.no_update

    row_idx = selected_cell["row"]
    col_id = selected_cell["column"]
    if row_idx is None or row_idx >= len(restock_data):
        return dash.no_update, dash.no_update

    restock_sheet = spreadsheet.worksheet("Restock")
    header = restock_sheet.row_values(1)
    try:
        col_index = header.index(col_id)
    except ValueError:
        return dash.no_update, dash.no_update

    sheet_id = restock_sheet._properties['sheetId']
    start_row = row_idx + 1
    start_col = col_index

    color_rgb = get_color_rgb(color_name)

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
    helper_sheet = spreadsheet.worksheet("Helper Data")
    helper_row = row_idx + 2  # +2 for header and 1-based index
    helper_col = 62  # BJ is column 62
    try:
        helper_sheet.update_cell(helper_row, helper_col, color_name)
    except Exception as e:
        pass  # Optionally log or handle error

    time.sleep(1)  # Wait 1 second before triggering refresh
    return None, (n_intervals or 0) + 1

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
    [Input("restock-selected-cell", "data")],
    prevent_initial_call=True
)
def show_restock_fixed_btns(restock_selected_cell):
    if restock_selected_cell:
        return {"position": "fixed", "bottom": "20px", "left": "50%", "transform": "translateX(-50%)", "backgroundColor": "#181818", "padding": "15px", "borderRadius": "12px", "display": "flex", "flexDirection": "row", "alignItems": "center", "gap": "20px", "zIndex": 20001}
    return {"display": "none"}

# --- CLIENTSIDE CALLBACK FOR SMOOTH SCROLLING ---
app.clientside_callback(
    """
    function(drawer, restock, nof) {
        var mapping = {
            'menu-drawer-btn': 'drawer-flower-section',
            'menu-restock-btn': 'restock-list-section',
            'menu-nof-btn': 'not-on-floor-section'
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
     Input('menu-nof-btn', 'n_clicks')],
    prevent_initial_call=True
)

if __name__ == "__main__":
    from waitress import serve
    serve(app.server, host="0.0.0.0", port=8050)
# To run the app, use the command:
#venv\Scripts\activate
#python dgt_inventory_dash_app.py