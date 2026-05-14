from dash import html, dcc
import dash_bootstrap_components as dbc
import os
import re
import base64
from .drawer_flower_utils import fetch_data, get_lineage_options

# ---- SQUARE TEMPLATE ----
def get_strain_color(content_upper):
    if "INDICA" in content_upper:
        return "purple"
    elif "SATIVA" in content_upper:
        return "orange"
    elif "HYBRID" in content_upper:
        return "green"
    return "lightgray"

def drawer_flower_section():
    top_cells, bottom_cells = fetch_data()
    def render_grid(selected_idx=None, hovered_idx=None):
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
            else:
                color = get_strain_color(content_upper)
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
        return html.Div([
            html.Div([make_square(item, idx, selected_idx, hovered_idx) for idx, item in enumerate(top_cells)],
                     className="drawerflower-row-top", style={"display": "flex", "flexDirection": "row", "gap": "10px", "marginBottom": "10px"}),
            html.Div([make_square(item, idx+42, selected_idx, hovered_idx) for idx, item in enumerate(bottom_cells)],
                     className="drawerflower-row-bottom", style={"display": "flex", "flexDirection": "row", "gap": "10px"})
        ], style={"overflowX": "auto", "display": "block", "width": "100%"})
    return html.Div([
        html.H3("\U0001F33C Drawer Flower", className="section-heading"),
        dcc.Store(id="top-cells-store", data=top_cells),
        dcc.Store(id="bottom-cells-store", data=bottom_cells),
        html.Div(id="dynamic-grid", children=render_grid()),
        html.Div(id="selected-text", className="selected-text"),
        # Only show fixed-dropdowns when a square is selected (handled by callback style)
        html.Div([
            dcc.Dropdown(
                id="custom-dropdown",
                options=[],
                placeholder="Manual Change",
                className="custom-dropdown-style drawerflower-dropdown"
            ),
            dcc.Dropdown(
                id="lineage-dropdown",
                options=[],
                placeholder="Lineage Options",
                className="custom-dropdown-style drawerflower-dropdown"
            ),
            dbc.Button("✅", id="confirm-btn", color="success", className="action-btn confirm-btn drawerflower-btn"),
            html.Button("✖", id="drawerflower-x-btn", className="action-btn drawerflower-x-btn drawerflower-btn")
        ], id="fixed-dropdowns", className="fixed-dropdowns drawerflower-fixed-row", style={"display": "none"}),
    ], id="drawer-flower-section", className="scroll-container drawerflower-scroll-container")
