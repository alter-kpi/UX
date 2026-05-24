from dash import html, dcc
import dash_bootstrap_components as dbc

# ============================================================
# AttrakDiff 2 — 28 paires d'adjectifs
# ============================================================

ATTRAKDIFF_ITEMS = [
    # (id, label_gauche, label_droite, dimension)
    # PQ — Qualité Pragmatique
    (1,  "Obstructif",           "Aidant",                "PQ"),
    (2,  "Compliqué",            "Simple",                "PQ"),
    (3,  "Imprévisible",         "Prévisible",            "PQ"),
    (4,  "Déroutant",            "Clairement structuré",  "PQ"),
    (5,  "Peu maniable",         "Maniable",              "PQ"),
    (6,  "Peu pratique",         "Pratique",              "PQ"),
    (7,  "Difficile à utiliser", "Facile à utiliser",     "PQ"),
    # HQ-S — Hédonique / Stimulation
    (8,  "Conventionnel",        "Inventif",              "HQ-S"),
    (9,  "Sans imagination",     "Créatif",               "HQ-S"),
    (10, "Prudent",              "Audacieux",             "HQ-S"),
    (11, "Conservateur",         "Innovant",              "HQ-S"),
    (12, "Ennuyeux",             "Captivant",             "HQ-S"),
    (13, "Sans exigence",        "Ambitieux",             "HQ-S"),
    (14, "Ordinaire",            "Inédit",                "HQ-S"),
    # HQ-I — Hédonique / Identité
    (15, "Peu présentable",      "Présentable",           "HQ-I"),
    (16, "Repoussant",           "Accueillant",           "HQ-I"),
    (17, "Isole des autres",     "Intègre aux autres",    "HQ-I"),
    (18, "Non professionnel",    "Professionnel",         "HQ-I"),
    (19, "Vulgaire",             "Stylé",                 "HQ-I"),
    (20, "Amateur",              "Expert",                "HQ-I"),
    (21, "Démodé",               "Tendance",              "HQ-I"),
    # ATT — Attractivité
    (22, "Désagréable",          "Agréable",              "ATT"),
    (23, "Laid",                 "Beau",                  "ATT"),
    (24, "Rebutant",             "Attrayant",             "ATT"),
    (25, "Mauvais",              "Bon",                   "ATT"),
    (26, "Repoussant",           "Séduisant",             "ATT"),
    (27, "Indésirable",          "Désirable",             "ATT"),
    (28, "Décourageant",         "Motivant",              "ATT"),
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
# LAYOUT PRINCIPAL
# ============================================================

layout = dbc.Container([

    dbc.Row([
        dbc.Col([
            html.H3([html.I(className="bi bi-stars me-2"), "AttrakDiff"], className="mb-1"),
            html.P(
                "Évaluez la qualité pragmatique, hédonique et l'attractivité perçue de votre interface.",
                className="text-muted mb-4"
            ),
        ])
    ]),

    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5([html.I(className="bi bi-upload me-2"), "Importer vos données"], className="mb-3"),
                    html.P([
                        "Fichier Excel ou CSV avec ", html.Strong("28 colonnes"),
                        " nommées ", html.Code("item_1"), " à ", html.Code("item_28"),
                        ", une ligne par participant. Valeurs : 1 à 7."
                    ], className="text-muted small mb-3"),
                    dcc.Upload(
                        id="attrakdiff-upload",
                        children=html.Div([
                            html.I(className="bi bi-file-earmark-arrow-up fs-2 text-muted d-block mb-2"),
                            html.Span("Glissez-déposez ou ", className="text-muted"),
                            html.A("parcourez", className="text-primary fw-bold"),
                            html.Span(" votre fichier", className="text-muted"),
                            html.Br(),
                            html.Small(".xlsx · .xls · .csv", className="text-muted"),
                        ]),
                        style={
                            "width": "100%", "minHeight": "130px",
                            "display": "flex", "alignItems": "center", "justifyContent": "center",
                            "borderWidth": "2px", "borderStyle": "dashed", "borderRadius": "8px",
                            "textAlign": "center", "borderColor": "#dee2e6",
                            "backgroundColor": "#f8f9fa", "cursor": "pointer", "padding": "20px",
                        },
                        multiple=False
                    ),
                    html.Div([
                        dbc.Button([html.I(className="bi bi-file-earmark-text me-2"), "Fichier exemple"],
                                   id="attrakdiff-btn-sample", color="outline-secondary",
                                   size="sm", className="mt-3 me-2", n_clicks=0),
                        dbc.Button([html.I(className="bi bi-download me-2"), "Télécharger le modèle"],
                                   id="attrakdiff-btn-template", color="outline-primary",
                                   size="sm", className="mt-3", n_clicks=0),
                    ]),
                    dcc.Download(id="attrakdiff-download-template"),
                    dcc.Download(id="attrakdiff-download-pdf"),
                    # Store pour conserver les données entre callbacks
                    dcc.Store(id="attrakdiff-store"),
                    html.Div(id="attrakdiff-upload-status", className="mt-3"),
                ])
            ])
        ], width=8),

        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H6("Les 4 dimensions", className="mb-3 fw-bold"),
                    *[
                        html.Div([
                            html.Span("●", style={"color": DIM_COLORS[dim], "marginRight": "8px", "fontSize": "18px"}),
                            html.Strong(dim),
                            html.Span(f"  {DIM_LABELS[dim]}", className="text-muted small"),
                            html.Div(style={"height": "8px"}),
                        ])
                        for dim in ["PQ", "HQ-S", "HQ-I", "ATT"]
                    ],
                    html.Hr(className="my-2"),
                    html.Small([html.I(className="bi bi-info-circle me-1"),
                                "28 paires · Échelle 1–7 · Scores –3 à +3"],
                               className="text-muted"),
                ])
            ], className="h-100"),
        ], width=4),
    ], className="mb-4"),

    html.Div(id="attrakdiff-results"),

], fluid=True)


# ============================================================
# HIDDEN LAYOUTS — pour enregistrer les IDs Dash
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
    dbc.Spinner(html.Div(id="attrakdiff-ia-output")),
], id="attrakdiff-ia-hidden")
