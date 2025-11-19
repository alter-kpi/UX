from dash import Dash, html, dcc, Input, Output, State
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
# 2) SIDEBAR — liens + modals
# ====================================================

# Modal À propos (avec photo)
modal_about = dbc.Modal(
    [
        dbc.ModalHeader(dbc.ModalTitle("À propos")),
        dbc.ModalBody([

            # PHOTO
            html.Img(
                src="/assets/photo_frederic.png",
                style={
                    "width": "90px",
                    "height": "90px",
                    "borderRadius": "50%",
                    "display": "block",
                    "margin": "0 auto 20px auto",
                    "objectFit": "cover"
                }
            ),

            # TEXTE
            html.P("Frédéric Michotte — Fondateur Alter KPI"),
            html.P("Expert en Business Intelligence & Finance d’entreprise."),
            html.P("Auteur et développeur de l’application Alter UX."),
            html.Hr(),

            # LINKEDIN
            html.P([
                html.I(className="bi bi-linkedin me-2"),
                html.A(
                    "Mon profil LinkedIn",
                    href="https://www.linkedin.com/in/fr%C3%A9d%C3%A9ric-michotte-03a9081a8/",
                    target="_blank",
                    className="text-decoration-none"
                )
            ]),

            # SITE WEB
            html.P([
                html.I(className="bi bi-globe me-2"),
                html.A(
                    "www.alter-kpi.com",
                    href="https://www.alter-kpi.com",
                    target="_blank",
                    className="text-decoration-none"
                )
            ]),

        ]),
        dbc.ModalFooter(
            dbc.Button("Fermer", id="close-about", className="ms-auto")
        )
    ],
    id="modal-about",
    is_open=False,
)


# Modal RGPD (texte complet)
modal_rgpd = dbc.Modal(
    [
        dbc.ModalHeader(dbc.ModalTitle("Confidentialité / RGPD")),
        dbc.ModalBody([
            html.P(
                "L’application Alter UX traite les fichiers importés uniquement en "
                "mémoire vive (RAM) de son serveur d’exécution. Aucun fichier n’est "
                "enregistré sur disque, aucune base de données n’est utilisée, et "
                "aucune donnée n’est conservée après l’analyse."
            ),
            html.P(
                "Le serveur hébergeant l’application est fourni par Render.com et "
                "localisé dans la zone EU-Central (Francfort, Allemagne), garantissant "
                "un traitement des données au sein de l’Union Européenne sans transfert "
                "vers des pays tiers."
            ),
            html.P(
                "Les données de votre fichier Excel sont utilisées exclusivement pour "
                "calculer les statistiques, afficher les visualisations et générer un "
                "rapport PDF. Ce rapport est produit en mémoire puis transmis à votre "
                "navigateur sans jamais être stocké sur le serveur."
            ),
            html.P(
                "Les données disparaissent automatiquement à la fermeture de la page, "
                "à la fin de la session ou lors du redémarrage du serveur, qui "
                "réinitialise entièrement la mémoire. Aucun tiers ne reçoit ou ne traite "
                "vos données. L’unique finalité du traitement est l’analyse du "
                "questionnaire importé, réalisée avec votre consentement."
            )
        ]),
        dbc.ModalFooter(
            dbc.Button("Fermer", id="close-rgpd", className="ms-auto")
        )
    ],
    id="modal-rgpd",
    is_open=False,
)



# Modal Feedback
modal_feedback = dbc.Modal(
    [
        dbc.ModalHeader(dbc.ModalTitle("Envoyer un feedback")),
        dbc.ModalBody([
            dcc.Textarea(
                id="feedback-text",
                placeholder="Écrivez votre commentaire ici...",
                style={"width": "100%", "height": "150px"}
            ),
        ]),
        dbc.ModalFooter([
            html.A(
                dbc.Button("Envoyer", id="send-feedback", color="primary"),
                id="feedback-mailto",
                href="mailto:info@alter-kpi.com?subject=Feedback%20Alter%20UX&body=",
                target="_blank"
            ),
            dbc.Button("Fermer", id="close-feedback", className="ms-auto")
        ])
    ],
    id="modal-feedback",
    is_open=False,
)


# ====================================================
# 3) GLOBAL LAYOUT
# ====================================================
app.layout = html.Div([

    dcc.Location(id="url"),

    modal_about,
    modal_rgpd,
    modal_feedback,

    html.Div([
        dashboard_layout,
        details_layout,
        ia_layout
    ], style={"display": "none"}),

    dbc.Container([
        dbc.Row([
            dbc.Col(
                html.Div([

                    # LOGO
                    html.A([
                        html.Img(
                            src="/assets/logo_alterkpi.png",
                            style={"width": "80px", "margin": "20px auto", "display": "block"}
                        )
                    ], href="https://www.alter-kpi.com", target="_blank"),

                    html.Hr(className="text-white"),

                    # NAVIGATION
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
                    ], vertical=True, pills=True),

                    # FOOTER-LIKE LINKS
                    html.Div([
                        html.Hr(className="text-white", style={"marginTop": "40px"}),
                        html.A("ℹ️ À propos de l'auteur", id="open-about", style={"cursor": "pointer"}),
                        html.A("🔒 Confidentialité & RGPD", id="open-rgpd", style={"cursor": "pointer"}),
                        html.A("👍 Feedback", id="open-feedback", style={"cursor": "pointer"}),
                    ], className="sidebar-footer-fixed"),

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
# 4) ROUTING
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
# 5) OPEN/CLOSE MODALS CALLBACKS
# ====================================================
@app.callback(
    Output("modal-about", "is_open"),
    Input("open-about", "n_clicks"),
    Input("close-about", "n_clicks"),
    State("modal-about", "is_open"),
    prevent_initial_call=True,
)
def toggle_about(open_click, close_click, is_open):
    return not is_open


@app.callback(
    Output("modal-rgpd", "is_open"),
    Input("open-rgpd", "n_clicks"),
    Input("close-rgpd", "n_clicks"),
    State("modal-rgpd", "is_open"),
    prevent_initial_call=True,
)
def toggle_rgpd(open_click, close_click, is_open):
    return not is_open


@app.callback(
    Output("modal-feedback", "is_open"),
    Input("open-feedback", "n_clicks"),
    Input("close-feedback", "n_clicks"),
    State("modal-feedback", "is_open"),
    prevent_initial_call=True,
)
def toggle_feedback(open_click, close_click, is_open):
    return not is_open


# ====================================================
# 6) UPDATE MAILTO WITH MESSAGE CONTENT
# ====================================================
@app.callback(
    Output("feedback-mailto", "href"),
    Input("feedback-text", "value")
)
def update_mailto_body(text):
    body = (text or "").replace("\n", "%0D%0A")
    return f"mailto:info@alter-kpi.com?subject=Feedback%20Alter%20UX&body={body}"


# ====================================================
# 7) REGISTER SUS CALLBACKS
# ====================================================
register_sus_callbacks(app)


# ====================================================
# 8) RUN
# ====================================================
if __name__ == "__main__":
    app.run(debug=True, port=8051)
