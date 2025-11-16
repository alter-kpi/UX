from dash import Dash, html, dcc, Input, Output
import dash_bootstrap_components as dbc

from components.home_layout import layout as home_layout
from components.sus_layout import (
    layout as sus_layout,
    dashboard_layout,
    details_layout,
    ia_layout
)
from components.sus_callbacks import register_callbacks as register_sus_callbacks


# ====================================================
# 1) CREATE APP
# ====================================================
app = Dash(
    __name__,
    suppress_callback_exceptions=True,
    external_stylesheets=[
        dbc.themes.SANDSTONE,
        "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css"
    ]
)

server = app.server
app.title = "Alter UX"


# ====================================================
# 2) GLOBAL LAYOUT (avec SIDEBAR)
# ====================================================
app.layout = html.Div([

    dcc.Location(id="url"),

    # Hidden layouts pour IDs (aucune logique)
    html.Div([
        dashboard_layout,
        details_layout,
        ia_layout
    ], style={"display": "none"}),

    dbc.Container([
        dbc.Row([
            dbc.Col(
                html.Div([

                    html.A([
                        html.Img(
                            src="/assets/logo_alterkpi.png",
                            style={"width": "80px", "margin": "20px auto", "display": "block"}
                        )
                    ], href="https://www.alter-kpi.com", target="_blank"),

                    html.Hr(className="text-white"),

                    dbc.Nav([
                        dbc.NavLink([
                            html.I(className="bi bi-house-door-fill",
                                   style={"color": "white", "marginRight": "8px"}),
                            "Accueil"
                        ], href="/", active="exact"),

                        dbc.NavLink([
                            html.I(className="bi bi-ui-checks-grid",
                                   style={"color": "white", "marginRight": "8px"}),
                            "Questionnaire SUS"
                        ], href="/sus", active="exact"),
                    ],
                    vertical=True, pills=True)

                ], className="sidebar"),
                width=2
            ),

            dbc.Col(
                html.Div(id="page-content", className="p-4"),
                width=10,
                style={"marginLeft": "260px"}
            )

        ], className="g-0")
    ], fluid=True)

])



# ====================================================
# 3) ROUTING
# ====================================================
@app.callback(Output("page-content", "children"),
              Input("url", "pathname"))
def render_page(pathname):

    if pathname == "/sus":
        return sus_layout

    if pathname == "/":
        return home_layout

    return html.Div([html.H3("Page inconnue"), html.P(pathname)])




# ====================================================
# 4) Enregistrement global des callbacks
# ====================================================
register_sus_callbacks(app)



# ====================================================
# 5) RUN
# ====================================================
if __name__ == "__main__":
    app.run(debug=True, port=8051)
