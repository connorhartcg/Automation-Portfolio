import dash
from dash import html, dcc, Input, Output, State, callback_context, dash_table
import dash_bootstrap_components as dbc
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import base64
import re
import time

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
# Add a cache to only refresh data every 15 minutes
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
    # Place logo image as a background using CSS background-image if it exists
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
            square_style["backgroundSize"] = "contain"  # preserve aspect ratio
            square_style["backgroundPosition"] = "center"
            square_style["backgroundRepeat"] = "no-repeat"
            # Do NOT set opacity here, keep text fully opaque
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
        # Only display columns A-H (0-7)
        header = restock_values[0][:8]
        rows = [row[:8] for row in restock_values[1:]]
        data = [dict(zip(header, row)) for row in rows]
        columns = [{"name": col, "id": col} for col in header]
        return data, columns, header
    except Exception as e:
        return None, None, None

# ---- DASH APP LAYOUT ----
# Load company logo as base64 for top left
logo_path = r"C:\\Users\\inven\\OneDrive\\Documents\\automation_and_documentation\\assets\\brand_photos\\Logos\\DrGreenthumbs_Logo.png"
logo_img_src = None
if os.path.exists(logo_path):
    with open(logo_path, "rb") as image_file:
        encoded = base64.b64encode(image_file.read()).decode()
        logo_img_src = f"data:image/png;base64,{encoded}"

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])

def render_grid(selected_idx=None, hovered_idx=None):
    return html.Div([
        html.Div([make_square(item, idx, selected_idx, hovered_idx) for idx, item in enumerate(top_cells)], style={"display": "flex", "gap": "10px", "marginBottom": "10px", "marginTop": "10px"}),
        html.Div([make_square(item, idx+42, selected_idx, hovered_idx) for idx, item in enumerate(bottom_cells)], style={"display": "flex", "gap": "10px"})
    ], className="scroll-inner")

restock_data, restock_columns, restock_header = get_restock_data_table()

app.layout = html.Div([
    html.Div(id="update-feedback", style={"marginTop": "20px", "marginBottom": "0px", "display": "flex", "justifyContent": "center", "position": "fixed", "top": 0, "left": 0, "width": "100%", "zIndex": 9999}),
    # Top logo (served from assets/brand_photos/Logos)
    dbc.Row([
        dbc.Col(html.Img(src=logo_img_src if logo_img_src else "", style={"width": "100px"}), width=1),
        dbc.Col(html.H1("Dr. Greenthumb's Inventory Interface", style={"marginTop": "20px", "color": "white"}), width=8)
    ], align="center"),
    html.Br(),
    html.Div([
        html.H3("\U0001F5C2 Drawer Flower", style={"textAlign": "left", "color": "white"}),
        html.Div(id="selected-text", style={"color": "white", "fontSize": "18px", "marginBottom": "20px", "fontWeight": "bold"}),
        html.Div(id="dynamic-grid")
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
    html.Div([
        html.H3("\U0001F4E6 Restock List", style={"textAlign": "left", "color": "white", "marginTop": "10px"}),
        # Interactive DataTable for restock
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
            style_data_conditional=[],
            cell_selectable=True,
            row_selectable=False,
            selected_cells=[],
            page_action="none",
            fixed_rows={"headers": True},
            virtualization=False,
        ),
        html.Div(id="color-picker-ui", style={"marginTop": "10px"}),
        dcc.Store(id="restock-selected-cell"),
        dcc.Store(id="restock-color-map", data={}),
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
    # Restock color buttons anchored at bottom (hidden by default)
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
    # Consolidated dropdowns and buttons (only one instance)
    html.Div([
        dcc.Dropdown(
            id="custom-dropdown",
            options=[{"label": val, "value": val} for val in dropdown_values],
            placeholder="Manual Change",
            style={"display": "none"},  # Only display controlled by callbacks and CSS
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
        dbc.Button("🔄", id="reset-btn", color="danger", className="action-btn reset-btn")
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
    dcc.Store(id="selected-square-store"),
    dcc.Store(id="hovered-square-store"),
    dcc.Store(id="selected-square-index-store"),
    dcc.Store(id="selected-restock-cell"),
    dcc.Store(id="restock-table-color-map")
], style={"backgroundColor": "#000"})

# ---- CALLBACKS ----
# COMBINED: Reset and Square Click logic to avoid duplicate outputs
@app.callback(
    Output("fixed-dropdowns", "style"),
    Output("selected-square-store", "data"),
    Output("selected-text", "children"),
    Output("custom-dropdown", "value"),
    Output("lineage-dropdown", "value"),
    Output("selected-square-index-store", "data"),
    [Input({'type': 'square', 'index': dash.ALL}, 'n_clicks'),
     Input("reset-btn", "n_clicks")],
    [State({'type': 'square', 'index': dash.ALL}, 'children'),
     State("custom-dropdown", "value"),
     State("lineage-dropdown", "value")],
    prevent_initial_call=True
)
def handle_square_and_reset(square_clicks, reset_click, children, custom_value, lineage_value):
    ctx = callback_context
    if not ctx.triggered:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update
    trigger = ctx.triggered[0]['prop_id']
    if trigger == 'reset-btn.n_clicks':
        return {"display": "none"}, None, "", None, None, None

    # Find the most recently clicked square (the one with the highest n_clicks)
    if square_clicks and any(square_clicks):
        max_clicks = max(square_clicks)
        if max_clicks:
            idx = square_clicks.index(max_clicks)
            # Extract text from .square-content
            content = None
            if children[idx] and isinstance(children[idx], list):
                for child in children[idx]:
                    if isinstance(child, dict) and child.get('props', {}).get('className') == 'square-content':
                        content = child['props'].get('children', '')
                        break
            if not content:
                content = ''
            # Determine row and adjust for new offset
            row = "TOP" if idx < 42 else "BOTTOM"
            # Remove logo existence info from selected_text
            selected_text = f"Selected: {content}"
            return {
                "display": "flex",
                "position": "fixed",
                "bottom": "20px",
                "left": "50%",
                "transform": "translateX(-50%)",
                "backgroundColor": "#181818",
                "padding": "15px",
                "borderRadius": "12px",
                "flexDirection": "row",
                "alignItems": "center",
                "gap": "20px",
                "color": "#e0e0e0"
            }, {
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
    # Only show menus if a square is selected
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
    # If a value is selected in one menu, hide the other
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
    [Input("selected-square-index-store", "data"),
     Input("hovered-square-store", "data")]
)
def update_grid(selected_idx, hovered_idx):
    return render_grid(selected_idx, hovered_idx)

# ---- RESTOCK TABLE INTERACTIVITY ----

# Store selected cell info when a cell is selected in the restock table or X is clicked
@app.callback(
    Output("restock-selected-cell", "data"),
    Output("restock-fixed-btns", "style"),
    [Input("restock-table", "active_cell"),
     Input("restock-deselect-btn", "n_clicks")],
    State("restock-table", "columns"),
    prevent_initial_call=True
)
def store_selected_restock_cell(active_cell, deselect_click, columns):
    style_visible = {
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
    style_hidden = style_visible.copy()
    style_hidden["display"] = "none"
    ctx = callback_context
    if ctx.triggered and ctx.triggered[0]["prop_id"].startswith("restock-deselect-btn"):
        return None, style_hidden
    if not active_cell:
        return None, style_hidden
    col_id = columns[active_cell["column_id"]]["id"] if isinstance(active_cell["column_id"], int) else active_cell["column_id"]
    return {
        "row": active_cell["row"],
        "column": col_id
    }, style_visible

# Color fill button logic
@app.callback(
    Output("restock-color-map", "data"),
    [Input("restock-green-btn", "n_clicks"),
     Input("restock-yellow-btn", "n_clicks"),
     Input("restock-red-btn", "n_clicks")],
    [State("restock-selected-cell", "data"),
     State("restock-color-map", "data")],
    prevent_initial_call=True
)
def fill_restock_cell(green, yellow, red, selected_cell, color_map):
    ctx = callback_context
    if not ctx.triggered or not selected_cell:
        return dash.no_update
    btn_id = ctx.triggered[0]["prop_id"].split(".")[0]
    color = None
    if btn_id == "restock-green-btn":
        color = "#43a047"  # green
    elif btn_id == "restock-yellow-btn":
        color = "#fbc02d"  # yellow
    elif btn_id == "restock-red-btn":
        color = "#e53935"  # red
    if color:
        key = f"{selected_cell['row']}_{selected_cell['column']}"
        color_map = color_map or {}
        color_map[key] = color
        return color_map
    return dash.no_update

@app.callback(
    Output("restock-table", "style_data_conditional"),
    [Input("restock-selected-cell", "data"),
     Input("restock-color-map", "data")],
    [State("restock-table", "data"),
     State("restock-table", "columns")],
    prevent_initial_call=True
)
def update_table_colors(selected_cell, color_map, data, columns):
    style = []
    if color_map:
        for key, color in color_map.items():
            row, col = key.split("_", 1)
            style.append({
                "if": {"row_index": int(row), "column_id": col},
                "backgroundColor": color,
                "color": "#fff"
            })
    # Highlight currently selected cell (on top of color fill)
    if selected_cell and selected_cell.get("row") is not None and selected_cell.get("column") is not None:
        style.append({
            "if": {"row_index": selected_cell["row"], "column_id": selected_cell["column"]},
            "border": "2px solid #fff"
        })
    return style

# Add hover highlighting (clientside callback for performance)
app.clientside_callback(
    "(function(n, prev) { return n; })",
    Output("hovered-square-store", "data"),
    [Input({'type': 'square', 'index': dash.ALL}, 'n_mouseover')],
    [State("hovered-square-store", "data")],
    prevent_initial_call=True
)

if __name__ == "__main__":
    app.run(debug=False)
# To run the app, use the command:
#venv\Scripts\activate
#python dgt_inventory_dash_app.py