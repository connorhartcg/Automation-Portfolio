from dash import html, dcc, dash_table
import dash_bootstrap_components as dbc
from restock_callbacks import get_restock_data_table, get_product_name_color_map, product_name_style_conditional

# Fetch data for initial render
restock_data, restock_columns, restock_header = get_restock_data_table()
product_name_color_map = get_product_name_color_map(restock_data)
restock_style_conditional = product_name_style_conditional(product_name_color_map, restock_data)

def restock_section():
    return html.Div([
        html.H3("\U0001F4E6 Restock List", className="section-heading"),
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
        html.Div(id="color-picker-ui", className="color-picker-ui"),
        dcc.Store(id="restock-selected-cell"),
        dcc.Store(id="restock-table-color-map", data=product_name_color_map),
        # Add fixed button bar for restock actions
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
    ], className="scroll-container restock-scroll-container")
