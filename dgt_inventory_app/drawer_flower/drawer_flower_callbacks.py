from dash import Output, Input, State, callback_context, html
from dgt_inventory_dash_app_test import app
import os
import re
import base64
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from .drawer_flower_utils import fetch_data, get_lineage_options

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

@app.callback(
    Output("fixed-dropdowns", "style"),
    Output("selected-square-store", "data"),
    Output("selected-text", "children"),
    Output("custom-dropdown", "value"),
    Output("lineage-dropdown", "value"),
    Output("selected-square-index-store", "data"),
    [Input({'type': 'square', 'index': 'ALL'}, 'n_clicks'),
     Input("drawerflower-x-btn", "n_clicks")],
    [State({'type': 'square', 'index': 'ALL'}, 'children'),
     State("custom-dropdown", "value"),
     State("lineage-dropdown", "value")],
    prevent_initial_call=True
)
def handle_square_and_reset(square_clicks, x_click, children, custom_value, lineage_value):
    ctx = callback_context
    if not ctx.triggered:
        return html.no_update, html.no_update, html.no_update, html.no_update, html.no_update, html.no_update
    trigger = ctx.triggered[0]['prop_id']
    if trigger == 'drawerflower-x-btn.n_clicks':
        return {"display": "none"}, None, "", None, None, None
    if square_clicks and any(square_clicks):
        max_clicks = max(square_clicks)
        if max_clicks:
            idx = square_clicks.index(max_clicks)
            # idx is already 0-41 for top, 42-83 for bottom (matches grid)
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
    Output("dynamic-grid", "children"),
    Input("top-cells-store", "data"),
    Input("bottom-cells-store", "data"),
    Input("selected-square-index-store", "data"),
    Input("hovered-square-store", "data"),
    Input("selected-square-store", "data"),  # <--- PATCH: force update on selection
)
def update_grid_with_store(top_cells_data, bottom_cells_data, selected_idx, hovered_idx, selected_square):
    # selected_idx is the grid index (0-83), matches make_square logic
    return html.Div([
        html.Div([
            make_square(item, idx, selected_idx, hovered_idx) for idx, item in enumerate(top_cells_data)
        ], className="drawerflower-row-top", style={"display": "flex", "flexDirection": "row", "gap": "10px", "marginBottom": "10px"}),
        html.Div([
            make_square(item, idx+42, selected_idx, hovered_idx) for idx, item in enumerate(bottom_cells_data)
        ], className="drawerflower-row-bottom", style={"display": "flex", "flexDirection": "row", "gap": "10px"})
    ], style={"overflowX": "auto", "display": "block", "width": "100%"})

# --- FIX: Manual Change dropdown options always populated from DrawerData BB column ---
@app.callback(
    Output("custom-dropdown", "options"),
    Input("selected-square-store", "data"),
    prevent_initial_call=False
)
def update_manual_change_dropdown(selected_square):
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
    dropdown_values = drawer_data_sheet.col_values(54)[1:]  # BB is column 54, skip header
    return [{"label": v, "value": v} for v in dropdown_values if v.strip()]
