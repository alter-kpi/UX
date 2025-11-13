# app.py — Bootstrap + logo cliquable
from dash import Dash, html, dcc, Input, Output
import dash_bootstrap_components as dbc
from components.home_layout import layout as home_layout
from components.sus_layout import layout as sus_layout
from components.sus_callbacks import register_callbacks as register_sus_callbacks



app = Dash(
    __name__,
    suppress_callback_exceptions=True,
    external_stylesheets=[dbc.themes.FLATLY]
)
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
                        style={"width": "80px", "margin": "10px auto", "display": "block"}
                    )
                ], href="https://www.alter-kpi.com", target="_blank"),

                html.Hr(className="text-white"),

                # --- Menu ---
                dbc.Nav([
                    dbc.NavLink("🏠 Accueil", href="/", active="exact", className="text-white"),
                    dbc.NavLink("⚪ Questionnaire SUS", href="/sus", active="exact", className="text-white"),
                ],
                vertical=True, pills=True,
                style={
                    "wordWrap": "break-word",
                    "whiteSpace": "normal",
                    "paddingLeft": "0px"  # 🔹 réduit la marge intérieure
                })
            ], style={
                "backgroundColor": "#2c3e50",
                "height": "100vh",
                "padding": "5px 5px",  # 🔹 marge interne réduite
                "position": "fixed",
                "width": "240px",
                "overflowY": "auto"  # 🔹 scroll si trop de contenu
            }),
            width=2
        ),

        # Contenu principal
        dbc.Col(
            [
                dcc.Location(id="url"),
                html.Div(id="page-content", className="p-4")
            ],
            width=10,
            style={"marginLeft": "240px"}  # ✅ correspond à la largeur sidebar
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
