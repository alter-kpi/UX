# app.py — Bootstrap + logo cliquable
from dash import Dash, html, dcc, Input, Output
import dash_bootstrap_components as dbc
from components.home_layout import layout as home_layout
from components.sus_layout import layout as sus_layout
from components.sus_callbacks import register_callbacks as register_sus_callbacks


app = Dash(
    __name__,
    suppress_callback_exceptions=True,
    external_stylesheets=[
        dbc.themes.SANDSTONE,
        "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css"
    ]
)

server = app.server   # <-- OBLIGATOIRE pour Render
app.title = "Alter UX"


# === Layout global avec sidebar Bootstrap ===
app.layout = dbc.Container([
    dbc.Row([

        # === Sidebar ===
        dbc.Col(
            html.Div([

                # --- Logo cliquable ---
                html.A([
                    html.Img(
                        src="/assets/logo_alterkpi.png",
                        style={"width": "80px", "margin": "20px auto", "display": "block"}
                    )
                ], href="https://www.alter-kpi.com", target="_blank"),

                html.Hr(className="text-white"),

                # --- Menu ---
                dbc.Nav([
                    dbc.NavLink([
                        html.I(className="bi bi-house-door-fill", style={"color": "white", "marginRight": "8px"}),
                        "Accueil"
                    ], href="/", active="exact"),

                    dbc.NavLink([
                        html.I(className="bi bi-ui-checks-grid", style={"color": "white", "marginRight": "8px"}),
                        "Questionnaire SUS"
                    ], href="/sus", active="exact"),
                ],
                vertical=True, pills=True)

            ], className="sidebar"),
            width=2
        ),

        # === Contenu principal ===
        dbc.Col(
            [
                dcc.Location(id="url"),
                html.Div(id="page-content", className="p-4")
            ],
            width=10,
            style={"marginLeft": "260px"}  # largeur sidebar (240px + padding)
        )
    ], className="g-0")
], fluid=True)


# === Routing ===
@app.callback(Output("page-content", "children"), Input("url", "pathname"))
def render_page(pathname):
    if pathname == "/sus":
        return sus_layout
    elif pathname == "/":
        return home_layout
    return html.Div([html.H3("Page inconnue"), html.P(pathname)])


# === Callbacks SUS ===
register_sus_callbacks(app)


if __name__ == "__main__":
    app.run(debug=True, port=8051)
