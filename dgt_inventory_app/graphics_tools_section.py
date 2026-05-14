from dash import html, dcc
import dash_bootstrap_components as dbc

def graphics_tools_section():
    return html.Div([
        dcc.Store(id="graphics-tools-state", data={}),
        html.Div(
            [
                html.H3("Graphics Tools", className="section-heading"),
                html.Div("What graphics do you need to make?", className="graphics-tools-prompt"),
                html.Div([
                    dbc.Button("Strain Card", id="graphics-tools-strain-btn", color="primary", className="graphics-tools-btn"),
                    dbc.Button("Preroll Card", id="graphics-tools-preroll-btn", color="secondary", className="graphics-tools-btn"),
                    dbc.Button("Display Tags", id="graphics-tools-display-btn", color="secondary", className="graphics-tools-btn"),
                ], className="graphics-tools-btn-row")
            ],
            id="graphics-tools-section-initial"
        ),
        html.Div(id="graphics-tools-section")
    ], className="scroll-container graphics-tools-scroll-container")

# No relative imports to fix here, but ensure all future imports are absolute.
