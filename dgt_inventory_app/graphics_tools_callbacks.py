import gspread
from oauth2client.service_account import ServiceAccountCredentials
from dash import html
import dash_bootstrap_components as dbc
import dash
from dash import Input, Output, State, callback_context

from dgt_inventory_dash_app_test import app

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

@app.callback(
    Output("graphics-tools-section", "children"),
    Output("graphics-tools-state", "data"),
    [Input("graphics-tools-strain-btn", "n_clicks"),
     Input("graphics-tools-preroll-btn", "n_clicks"),
     Input("graphics-tools-display-btn", "n_clicks"),
     Input("graphics-tools-reset-btn", "n_clicks"),
     Input("graphics-tools-sku-input", "n_blur"),
     Input("graphics-tools-sku-input", "n_submit")],
    [State("graphics-tools-state", "data"),
     State("graphics-tools-sku-input", "value")],
    prevent_initial_call=False
)
def update_graphics_tools_section(strain_click, preroll_click, display_click, reset_click, sku_blur, sku_submit, state, sku):
    ctx = callback_context
    if not state:
        state = {}
    # Reset returns to initial
    if reset_click:
        return "", {}
    # If no interaction, show nothing (let initial prompt show)
    if not ctx.triggered:
        return "", state
    trigger = ctx.triggered[0]["prop_id"].split(".")[0]
    # Strain Card button: show SKU input
    if trigger == "graphics-tools-strain-btn":
        state = {"step": "strain-card"}
        return html.Div([
            html.H3("Graphics Tools - Strain Card", className="section-heading"),
            html.Div("Enter SKU to look up product:", className="sku-prompt"),
            dbc.Input(id="graphics-tools-sku-input", placeholder="Enter SKU...", type="text", className="sku-input", autoFocus=True),
            dbc.Button("Close", id="graphics-tools-reset-btn", color="secondary", className="close-btn")
        ]), state
    # SKU input blur or submit: for now, do nothing further
    if trigger == "graphics-tools-sku-input":
        return dash.no_update, state
    # Other buttons: show coming soon
    if trigger == "graphics-tools-preroll-btn":
        return html.Div([
            html.H3("Graphics Tools - Preroll Card", className="section-heading"),
            html.Div("Coming soon...", className="coming-soon-message"),
            dbc.Button("Close", id="graphics-tools-reset-btn", color="secondary", className="close-btn")
        ]), {"step": "preroll-card"}
    if trigger == "graphics-tools-display-btn":
        return html.Div([
            html.H3("Graphics Tools - Display Tags", className="section-heading"),
            html.Div("Coming soon...", className="coming-soon-message"),
            dbc.Button("Close", id="graphics-tools-reset-btn", color="secondary", className="close-btn")
        ]), {"step": "display-tags"}
    return "", state

