from dash import html, dcc, dash_table
import dash_bootstrap_components as dbc
from not_on_floor_callbacks import fetch_not_on_floor_data, get_unique_options

def not_on_floor_section():
    not_on_floor_data, not_on_floor_header = fetch_not_on_floor_data()
    not_on_floor_brand_options = get_unique_options(not_on_floor_data, "Brand")
    not_on_floor_category_options = get_unique_options(not_on_floor_data, "Category")
    not_on_floor_lineage_options = get_unique_options(not_on_floor_data, "Lineage")
    return html.Div([
        html.H3("\U0001F4CB Not On Floor", className="section-heading"),
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
                    className="nof-name-mode-radio"
                ),
                dcc.Input(
                    id="nof-name-filter",
                    type="text",
                    placeholder="Product Name...",
                    className="nof-name-filter-input"
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
            fixed_rows={"headers": True},
        ),
        dcc.Store(id="not-on-floor-raw-data", data=not_on_floor_data)
    ], className="scroll-container notonfloor-scroll-container")
