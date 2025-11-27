from dash import Dash, html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
import os
import pandas as pd
from datetime import datetime

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
            html.P(
                "Consultant finance & business intelligence spécialisé en pilotage, "
                "automatisation et création d’outils sur mesure. J’aime transformer "
                "les idées en solutions simples, efficaces et élégantes."
            ),
            html.P(
                "Alter UX est né de cette philosophie : rendre l’analyse de questionnaires "
                "intuitive, rapide et fiable, sans complexité technique."
            ),

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

            # EMAIL
            html.P([
                html.I(className="bi bi-envelope me-2"),
                html.A(
                    "info@alter-kpi.com",
                    href="mailto:info@alter-kpi.com",
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

            # ILLUSTRATION RGPD
            html.Img(
                src="/assets/rgpd_icon.png",
                style={
                    "width": "80px",
                    "height": "80px",
                    "display": "block",
                    "margin": "0 auto 20px auto",
                    "opacity": "0.9"
                }
            ),

            # TEXTE
            html.P(
                "L’application Alter UX traite les fichiers importés uniquement en "
                "mémoire vive (RAM). Aucun fichier n’est enregistré sur disque, "
                "aucune base de données n’est utilisée, et aucune donnée n’est "
                "conservée après l’analyse."
            ),
            html.P(
                "Le serveur est hébergé dans l’Union Européenne (Render – zone "
                "EU Central, Francfort), garantissant l’absence de transfert "
                "vers des pays tiers."
            ),
            html.P(
                "Les données servent uniquement à calculer les statistiques, "
                "générer les visualisations et produire le PDF. Le rapport est "
                "généré en mémoire puis transmis à votre navigateur, sans "
                "stockage permanent."
            ),
            html.P(
                "Vos données disparaissent automatiquement à la fin de la "
                "session ou lors du redémarrage du serveur. Aucun tiers ne peut "
                "y accéder."
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
        dbc.ModalHeader(dbc.ModalTitle("Une remarque, une suggestion ?")),
        dbc.ModalBody([
            
            dbc.Label("Votre email (si vous souhaitez être recontacté)"),
            dbc.Input(
                id="feedback-email",
                type="email",
                placeholder="Ex : nom@domaine.com",
                style={"marginBottom": "10px"}
            ),

            # Zone de message
            dbc.Label("Votre message"),
            dcc.Textarea(
                id="feedback-text",
                placeholder="Votre commentaire...",
                style={"width": "100%", "height": "150px"}
            ),

            html.Div(id="feedback-status", style={"marginTop": "10px", "color": "green"})
        ]),
        dbc.ModalFooter([
            dbc.Button("Envoyer", id="send-feedback", color="primary"),
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
                            style={"width": "120px", "margin": "20px auto", "display": "block"}
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
                        html.A("À propos de l'auteur", id="open-about", style={"cursor": "pointer"}),
                        html.A("Confidentialité & RGPD", id="open-rgpd", style={"cursor": "pointer"}),
                        html.A("Feedback", id="open-feedback", style={"cursor": "pointer"}),
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

import os
import pandas as pd
from datetime import datetime

# Dossier et fichier
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
FEEDBACK_FILE = os.path.join(DATA_DIR, "feedback.csv")

# Crée le dossier s'il n'existe pas
os.makedirs(DATA_DIR, exist_ok=True)

# Crée le fichier s'il n'existe pas OU s'il est vide
if not os.path.exists(FEEDBACK_FILE) or os.path.getsize(FEEDBACK_FILE) == 0:
    pd.DataFrame(columns=["timestamp", "email", "message"]).to_csv(FEEDBACK_FILE, index=False)



@app.callback(
    Output("feedback-status", "children"),
    Input("send-feedback", "n_clicks"),
    State("feedback-email", "value"),
    State("feedback-text", "value"),
    prevent_initial_call=True
)
def save_feedback(n, email, message):

    if not message or message.strip() == "":
        return "⚠️ Merci d'écrire un message."

    df = pd.read_csv(FEEDBACK_FILE)

    new_row = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "email": email.strip() if email else "",
        "message": message.strip()
    }

    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_csv(FEEDBACK_FILE, index=False)

    return "✔️ Merci ! Votre message a bien été envoyé."



# ====================================================
# 7) REGISTER SUS CALLBACKS
# ====================================================
register_sus_callbacks(app)


# ====================================================
# 8) RUN
# ====================================================
if __name__ == "__main__":
    app.run(debug=True, port=8051)
