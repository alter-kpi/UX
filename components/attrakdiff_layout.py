from dash import html, dcc
import dash_bootstrap_components as dbc

# ============================================================
# AttrakDiff 2 — 28 paires d'adjectifs
# Ordre : 7 PQ · 7 HQ-S · 7 HQ-I · 7 ATT
# Échelle : 1 (pôle négatif gauche) → 7 (pôle positif droite)
# ============================================================

ATTRAKDIFF_ITEMS = [
    (1,  "Obstructif",          "Aidant",                "PQ"),
    (2,  "Compliqué",           "Simple",                "PQ"),
    (3,  "Imprévisible",        "Prévisible",            "PQ"),
    (4,  "Déroutant",           "Clairement structuré",  "PQ"),
    (5,  "Peu maniable",        "Maniable",              "PQ"),
    (6,  "Peu pratique",        "Pratique",              "PQ"),
    (7,  "Difficile à utiliser","Facile à utiliser",     "PQ"),
    (8,  "Conventionnel",       "Inventif",              "HQ-S"),
    (9,  "Sans imagination",    "Créatif",               "HQ-S"),
    (10, "Prudent",             "Audacieux",             "HQ-S"),
    (11, "Conservateur",        "Innovant",              "HQ-S"),
    (12, "Ennuyeux",            "Captivant",             "HQ-S"),
    (13, "Sans exigence",       "Ambitieux",             "HQ-S"),
    (14, "Ordinaire",           "Inédit",                "HQ-S"),
    (15, "Peu présentable",     "Présentable",           "HQ-I"),
    (16, "Repoussant",          "Accueillant",           "HQ-I"),
    (17, "Isole des autres",    "Intègre aux autres",    "HQ-I"),
    (18, "Non professionnel",   "Professionnel",         "HQ-I"),
    (19, "Vulgaire",            "Stylé",                 "HQ-I"),
    (20, "Amateur",             "Expert",                "HQ-I"),
    (21, "Démodé",              "Tendance",              "HQ-I"),
    (22, "Désagréable",         "Agréable",              "ATT"),
    (23, "Laid",                "Beau",                  "ATT"),
    (24, "Rebutant",            "Attrayant",             "ATT"),
    (25, "Mauvais",             "Bon",                   "ATT"),
    (26, "Repoussant",          "Séduisant",             "ATT"),
    (27, "Indésirable",         "Désirable",             "ATT"),
    (28, "Décourageant",        "Motivant",              "ATT"),
]

DIM_COLORS = {
    "PQ":   "#2196F3",
    "HQ-S": "#4CAF50",
    "HQ-I": "#FF9800",
    "ATT":  "#E91E63",
}

DIM_LABELS = {
    "PQ":   "Qualité Pragmatique",
    "HQ-S": "Stimulation (HQ-S)",
    "HQ-I": "Identité (HQ-I)",
    "ATT":  "Attractivité",
}

# ============================================================
# SECTION DASHBOARD
# ============================================================

attrakdiff_dashboard_section = html.Div([
    html.Div(id="attrakdiff-upload-status", className="mb-2"),
    html.Div(id="attrakdiff-results"),
])

# ============================================================
# SECTION DÉTAILS
# ============================================================

attrakdiff_details_section = html.Div([
    html.Div(
        id="attrakdiff-data-preview",
        style={
            "maxHeight": "85vh",
            "overflowY": "auto",
            "border": "1px solid #ddd",
            "padding": "10px",
            "backgroundColor": "white",
            "borderRadius": "6px"
        }
    )
])

# ============================================================
# SECTION ANALYSE IA
# ============================================================

attrakdiff_ia_section = html.Div([
    dbc.Button(
        "🧠 Générer l'analyse IA",
        id="attrakdiff-btn-ai-tab",
        color="primary",
        style={"padding": "3px 10px", "whiteSpace": "nowrap", "width": "200px", "marginBottom": "20px"}
    ),
    html.P(
        "L'analyse ci-dessous est générée automatiquement par un modèle de "
        "langage avancé (OpenAI GPT-4o). Elle est produite en temps réel à "
        "partir des scores de votre questionnaire et n'est jamais enregistrée.",
        style={
            "fontSize": "14px",
            "color": "#555",
            "marginBottom": "20px",
            "textAlign": "center",
            "maxWidth": "1600px",
            "marginLeft": "auto",
            "marginRight": "auto"
        }
    ),
    dcc.Loading(
        id="attrakdiff-loading-ai",
        type="circle",
        children=dcc.Markdown(
            id="attrakdiff-ia-text",
            style={"whiteSpace": "pre-wrap", "marginTop": "20px"}
        )
    )
])

# ============================================================
# SECTION PDF
# ============================================================

attrakdiff_pdf_section = html.Div([
    dbc.Button(
        "📄 Générer le PDF",
        id="attrakdiff-btn-pdf-tab",
        color="primary",
        style={"marginBottom": "20px"}
    ),
    dcc.Loading(
        id="attrakdiff-loading-pdf",
        type="circle",
        children=html.Div(
            id="attrakdiff-pdf-preview",
            style={
                "height": "75vh",
                "overflowY": "auto",
                "border": "1px solid #ddd",
                "padding": "10px",
                "backgroundColor": "white",
                "borderRadius": "6px"
            }
        )
    ),
    html.Div(id="attrakdiff-pdf-download-zone", style={"marginTop": "20px"})
])

# ============================================================
# MODAL AIDE
# ============================================================

attrakdiff_modal_help = dbc.Modal(
    [
        dbc.ModalHeader(dbc.ModalTitle("Guide d'utilisation AttrakDiff")),
        dbc.ModalBody([
            html.Div([
                html.H5("Sommaire", className="mb-2"),
                html.Ul([
                    html.Li("1. Remplir le fichier Excel", style={"marginBottom": "4px"}),
                    html.Li("2. Les 4 dimensions AttrakDiff", style={"marginBottom": "4px"}),
                    html.Li("3. Calcul des scores", style={"marginBottom": "4px"}),
                    html.Li("4. Lire le diagramme Portfolio", style={"marginBottom": "4px"}),
                    html.Li("5. Analyse IA", style={"marginBottom": "4px"}),
                ], style={"lineHeight": "1.4"})
            ], className="mb-3"),

            html.Div([
                html.H5("1. Remplir le fichier Excel", className="mt-3 mb-2"),
                html.P("• 28 colonnes nommées item_1 à item_28, une ligne par participant."),
                html.P("• Valeurs : entiers de 1 à 7."),
                html.P("• 1 = pôle négatif (gauche), 7 = pôle positif (droite)."),

                html.Hr(className="my-3"),

                html.H5("2. Les 4 dimensions", className="mt-3 mb-2"),
                *[
                    html.P([
                        html.Span("● ", style={"color": DIM_COLORS[dim]}),
                        html.Strong(f"{dim} — {DIM_LABELS[dim]} : "),
                        html.Span(f"items {[i for i,_,_,d in ATTRAKDIFF_ITEMS if d==dim][0]} "
                                  f"à {[i for i,_,_,d in ATTRAKDIFF_ITEMS if d==dim][-1]}")
                    ])
                    for dim in ["PQ", "HQ-S", "HQ-I", "ATT"]
                ],

                html.Hr(className="my-3"),

                html.H5("3. Calcul des scores", className="mt-3 mb-2"),
                html.Div([
                    html.P("1. Moyenne de chaque item par dimension"),
                    html.P("2. Score = moyenne – 4  (ramène l'échelle 1–7 vers –3/+3)"),
                    html.P("3. Score final par dimension : –3 (très négatif) → +3 (très positif)", style={"fontWeight": "bold"}),
                ], style={"border": "1px solid #ddd", "padding": "10px", "borderRadius": "6px", "backgroundColor": "#f9f9f9"}),

                html.Hr(className="my-3"),

                html.H5("4. Lire le diagramme Portfolio", className="mt-3 mb-2"),
                html.P("• Axe X : Qualité Hédonique moyenne (HQ-S + HQ-I) / 2"),
                html.P("• Axe Y : Qualité Pragmatique (PQ)"),
                html.P("• Zone Souhaité (haut droite) : produit utile ET attrayant — idéal"),
                html.P("• Zone Orienté tâche (bas droite) : efficace mais peu stimulant"),
                html.P("• Zone Superflu (haut gauche) : attrayant mais peu utilisable"),
                html.P("• Zone Inutile (bas gauche) : améliorations nécessaires sur tout"),

                html.Hr(className="my-3"),

                html.H5("5. Analyse IA", className="mt-3 mb-2"),
                html.P("• Utilise OpenAI GPT-4o avec les scores par dimension."),
                html.P("• Aucune donnée individuelle n'est transmise au modèle."),
                html.P("• L'analyse n'est jamais stockée."),

            ], style={"maxHeight": "70vh", "overflowY": "auto"})
        ]),
        dbc.ModalFooter(
            dbc.Button("Fermer", id="attrakdiff-close-help", className="ms-auto", color="primary")
        ),
    ],
    id="attrakdiff-modal-help",
    is_open=False,
    size="lg",
)

# ============================================================
# LAYOUT PRINCIPAL
# ============================================================

layout = dbc.Container([

    attrakdiff_modal_help,

    dcc.Download(id="attrakdiff-download-template"),
    dcc.Store(id="attrakdiff-store"),
    dcc.Upload(id="attrakdiff-upload", children=html.Div(), multiple=False,
               style={"display": "none"}),

    # HEADER — titre + boutons
    dbc.Row([
        dbc.Col(
            html.H4("Analyse du questionnaire AttrakDiff", className="mt-3 mb-3"),
            md=6,
            className="d-flex align-items-center"
        ),
        dbc.Col(
            dbc.Row([
                dbc.Col(
                    dcc.Upload(
                        id="attrakdiff-upload-btn",
                        children=dbc.Button(
                            [html.I(className="bi bi-folder2-open me-1"), " Importer"],
                            color="secondary",
                            style={"padding": "3px 5px", "whiteSpace": "nowrap", "width": "140px"}
                        ),
                        multiple=False,
                        style={"cursor": "pointer"}
                    ),
                    width="auto"
                ),
                dbc.Col(
                    dbc.Button(
                        [html.I(className="bi bi-stars me-1"), " Charger exemple"],
                        id="attrakdiff-btn-sample",
                        color="success",
                        style={"padding": "3px 5px", "whiteSpace": "nowrap", "width": "160px"},
                        n_clicks=0
                    ),
                    width="auto"
                ),
                dbc.Col(
                    dbc.Button(
                        [html.I(className="bi bi-trash me-1"), " Reset"],
                        id="attrakdiff-btn-reset",
                        color="danger",
                        style={"padding": "3px 5px", "whiteSpace": "nowrap", "width": "120px"},
                        n_clicks=0
                    ),
                    width="auto"
                ),
                dbc.Col(
                    dbc.Button(
                        [html.I(className="bi bi-download me-1"), " Modèle Excel"],
                        id="attrakdiff-btn-template",
                        color="info",
                        style={"padding": "3px 5px", "whiteSpace": "nowrap", "width": "150px"},
                        n_clicks=0
                    ),
                    width="auto"
                ),
                dbc.Col(
                    dbc.Button(
                        [html.I(className="bi bi-info-circle me-1"), " Aide"],
                        id="attrakdiff-btn-help",
                        color="dark",
                        style={"padding": "3px 5px", "whiteSpace": "nowrap", "width": "100px"},
                        n_clicks=0
                    ),
                    width="auto"
                ),
            ], className="g-2 justify-content-end mt-3"),
            md=6,
            className="d-flex justify-content-end align-items-center"
        ),
    ], className="g-2"),

    # Info fichier
    html.Div(id="attrakdiff-file-info", style={"display": "none"}),

    # ONGLETS
    dbc.Tabs(
        id="attrakdiff-tabs",
        active_tab="tab-dashboard",
        children=[
            dbc.Tab(label="Dashboard",   tab_id="tab-dashboard"),
            dbc.Tab(label="Détails",     tab_id="tab-details"),
            dbc.Tab(label="Analyse IA",  tab_id="tab-ia"),
            dbc.Tab(label="PDF",         tab_id="tab-pdf"),
        ]
    ),

    dbc.Card(
        dbc.CardBody(
            html.Div([
                html.Div(
                    dcc.Loading(type="circle", children=attrakdiff_dashboard_section),
                    id="attrakdiff-tab-dashboard"
                ),
                html.Div(attrakdiff_details_section, id="attrakdiff-tab-details",
                         style={"display": "none"}),
                html.Div(attrakdiff_ia_section,      id="attrakdiff-tab-ia",
                         style={"display": "none"}),
                html.Div(attrakdiff_pdf_section,     id="attrakdiff-tab-pdf",
                         style={"display": "none"}),
            ], style={
                "minHeight": "85vh",
                "maxHeight": "85vh",
                "overflowY": "auto",
                "padding": "5px",
                "overflowX": "hidden"
            })
        ),
        className="shadow-sm",
        style={"padding": "0px", "backgroundColor": "#ffffff", "borderRadius": "0 0 10px 10px"}
    ),

], fluid=True)


# ============================================================
# HIDDEN LAYOUTS — IDs nécessaires pour les callbacks globaux
# ============================================================

dashboard_layout = html.Div([
    dcc.Graph(id="attrakdiff-portfolio-graph"),
    dcc.Graph(id="attrakdiff-radar-graph"),
    dcc.Graph(id="attrakdiff-profile-graph"),
], id="attrakdiff-dashboard-hidden")

details_layout = html.Div([
    html.Div(id="attrakdiff-details-content"),
], id="attrakdiff-details-hidden")

ia_layout = html.Div([
    dbc.Button("Générer l'analyse IA", id="attrakdiff-btn-ai", n_clicks=0),
    html.Div(id="attrakdiff-ia-output"),
], id="attrakdiff-ia-hidden")
