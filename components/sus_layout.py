
from dash import html, dcc, dash_table
import dash_bootstrap_components as dbc

# === SECTIONS ===

# ---- Section Dashboard ----
dashboard_layout = html.Div([

    # KPI cards
    dbc.Row([
        dbc.Col(html.Div([
            html.H6("Nombre de réponses", className="text-muted mb-1"),
            html.H2(id="kpi_count", className="mb-0")
        ], className="p-3 text-center bg-white"), md=4),

        dbc.Col(html.Div([
            html.H6("Score moyen SUS", className="text-muted mb-1"),
            html.H2(id="kpi_mean", className="mb-0")
        ], className="p-3 text-center bg-white"), md=4),

        dbc.Col(html.Div([
            html.H6("≥ 80 (Bonne UX)", className="text-muted mb-1"),
            html.H2(id="kpi_pct70", className="mb-0")
        ], className="p-3 text-center bg-white"), md=4),
    ], className="mb-4 g-3"),

    # Gauge
    dbc.Row([
        dbc.Col([
            html.Div([
                dcc.Graph(
                    id="gauge-graph",
                    config={"displayModeBar": False},
                    style={"height": "180px"}
                )
            ])
        ], md=8)
    ], justify="center", className="mb-5"),

    # Stats + histogram
    dbc.Row([
        dbc.Col(
            dash_table.DataTable(
                id="sus-stats-table",
                columns=[
                    {"name": "Indicateur", "id": "Indicateur"},
                    {"name": "Valeur", "id": "Valeur"}
                ],
                data=[],
                style_cell={"textAlign": "left", "padding": "6px", "fontSize": "13px"},
                style_header={"fontWeight": "bold", "backgroundColor": "#f8f9fa"},
            ),
            md=6
        ),
        dbc.Col(
            dcc.Graph(id="sus-class-hist", config={"displayModeBar": False}, style={"height": "420px"}),
            md=6
        ),
    ], className="g-4 mb-5"),

    # Histogramme principal + radar
    dbc.Row([
        dbc.Col(dcc.Graph(id="hist-graph", config={"displayModeBar": False}, style={"height": "400px"}), md=6),
        dbc.Col(dcc.Graph(id="radar-graph", config={"displayModeBar": False}, style={"height": "400px"}), md=6),
    ], className="g-4 mb-5"),

    html.Br(),

    # Categories
    html.Div([
        html.H4("Analyse par catégorie", className="mt-4 mb-3 text-center"),
        html.H6("Scores SUS moyens par groupe (effectifs en gris)", className="text-center text-muted mb-3"),

        dbc.Row([
            dbc.Col(dcc.Graph(id="cat-graph-1", config={"displayModeBar": False}), md=6, xs=12),
            dbc.Col(dcc.Graph(id="cat-graph-2", config={"displayModeBar": False}), md=6, xs=12),
            dbc.Col(dcc.Graph(id="cat-graph-3", config={"displayModeBar": False}), md=6, xs=12),
            dbc.Col(dcc.Graph(id="cat-graph-4", config={"displayModeBar": False}), md=6, xs=12),
        ], className="g-4 mb-4")
    ], id="categories-section", style={"display": "none"})


])


# ---- Section Détails ----
details_layout = html.Div([

    html.Div(
        id="data-preview",
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


# ---- Section Analyse IA (visible) ----
ia_layout = html.Div([

    dcc.Store(id="ai-analysis-visible-store", storage_type="session"),

    # --- Texte explicatif du modèle utilisé ---
    html.P(
        "L’analyse ci-dessous est générée automatiquement par un modèle de "
        "langage avancé (OpenAI GPT-4o). Elle est produite en temps réel à "
        "partir des statistiques de votre questionnaire et n’est jamais "
        "enregistrée.",
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

    # --- Zone où le texte IA s'affiche ---
    dcc.Loading(
        id="loading-ai",
        type="circle",
        children=dcc.Markdown(
            id="ai-analysis-visible",
            style={"whiteSpace": "pre-wrap", "marginTop": "50px"}
        )
    )


])


# LAYOUT ONGLET PDF

pdf_layout = html.Div([

    dbc.Button(
        "📄 Générer le PDF",
        id="btn-generate-pdf",
        color="primary",
        style={"marginBottom": "20px"}
    ),

    dcc.Loading(
        id="loading-pdf",
        type="circle",
        children=html.Div(
            id="pdf-preview",
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

    html.Div(id="pdf-download-zone", style={"marginTop": "20px"})
])





# === LAYOUT PRINCIPAL ===
layout = dbc.Container([

    # HEADER
    dbc.Row(
        [
            # Titre à gauche
            dbc.Col(
                html.H4("Analyse du questionnaire SUS", className="mt-3 mb-3"),
                md=6,
                className="d-flex align-items-center"
            ),

            # Boutons à droite
            dbc.Col(
                dbc.Row(
                    [
                        dbc.Col(
                            dcc.Upload(
                                id="upload-data",
                                children=dbc.Button(
                                    "📂 Importer",
                                    color="secondary",
                                    style={"whiteSpace": "nowrap", "width": "110px"}
                                ),
                                multiple=False,
                                style={"cursor": "pointer"}
                            ),
                            width="auto"
                        ),
                        dbc.Col(
                            dbc.Button(
                                "🗑️ Reset",
                                id="btn-reset",
                                color="danger",
                                style={"whiteSpace": "nowrap", "width": "110px"}
                            ),
                            width="auto"
                        ),

                        dbc.Col(
                            html.A(
                                dbc.Button(
                                    "📥 Modèle",
                                    color="info",
                                    style={"whiteSpace": "nowrap", "width": "110px"}
                                ),
                                href="/assets/template_sus.xlsx",
                                target="_blank"
                            ),
                            width="auto"
                        ),
                        dbc.Col(
                            dbc.Button(
                                "ℹ️ Aide",
                                id="btn-help-template",
                                color="dark",
                                style={"whiteSpace": "nowrap", "width": "110px"}
                            ),
                            width="auto"
                        ),
                        
                    ],
                    className="g-2 justify-content-end mt-3",
                ),


                md=6,
                className="d-flex justify-content-end align-items-center"
            ),
        ],
        className="g-2"
    ),




    # Feedback
    html.Div(id="file-info", style={"display": "none"}),

    dcc.Download(id="download-pdf"),
    dcc.Store(id="data-store", storage_type="session"),
    dcc.Store(id="fig-store", storage_type="session"),
    dcc.Store(id="ai-processing", storage_type="session"),
    dcc.Store(id="ai-analysis", storage_type="session"),

    #Modal Explications template

    # ------------------------------------------------------------
    # MODAL D’AIDE COMPLET ALTER UX
    # ------------------------------------------------------------
    dbc.Modal(
        [
            dbc.ModalHeader(dbc.ModalTitle("Guide d'utilisation Alter UX")),
            dbc.ModalBody(
                [

                    # ==========================
                    # SOMMAIRE
                    # ==========================
                    html.Div([
                        html.H5("Sommaire", className="mb-2"),
                        html.Ul([
                            html.Li(html.A("1. Remplir le fichier Excel", href="#help-excel"),
                                    style={"marginBottom": "4px"}),
                            html.Li(html.A("2. Comprendre les graphiques", href="#help-graphs"),
                                    style={"marginBottom": "4px"}),
                            html.Li(html.A("3. Calcul du score SUS", href="#help-calcul-sus"),
                                    style={"marginBottom": "4px"}),
                            html.Li(html.A("4. Les 10 items officiels du SUS", href="#help-items"),
                                    style={"marginBottom": "4px"}),
                            html.Li(html.A("5. Analyse IA", href="#help-ai"),
                                    style={"marginBottom": "4px"}),
                        ],
                        style={"lineHeight": "1.4"})
                    ], className="mb-3"),

                    # ==========================
                    # CONTENU PRINCIPAL
                    # ==========================
                    html.Div([

                        # ------------------------------------------------
                        # SECTION 1 : REMPLIR L’EXCEL
                        # ------------------------------------------------
                        html.H5("1. Comment remplir le fichier Excel",
                                id="help-excel", className="mt-3 mb-2"),

                        html.P("• Colonne A : identifiant unique du répondant.",
                            style={"marginBottom": "6px"}),
                        html.P("• Colonnes B à K : réponses aux 10 questions (notes de 1 à 5).",
                            style={"marginBottom": "6px"}),
                        html.P("• Colonnes L à O : catégories optionnelles (texte ou nombre).",
                            style={"marginBottom": "6px"}),
                        html.P("• Vous pouvez renommer les en-têtes des catégories ou laisser vide.",
                            style={"marginBottom": "6px"}),

                        html.Img(
                            src="/assets/template.png",
                            style={"width": "100%", "marginTop": "6px", "borderRadius": "6px"}
                        ),

                        html.Hr(className="my-3"),

                        # ------------------------------------------------
                        # SECTION 2 : GRAPHIQUES
                        # ------------------------------------------------
                        html.H5("2. Comment les graphiques sont générés",
                                id="help-graphs", className="mt-3 mb-2"),

                        html.P("• Jauge SUS : basée sur l’échelle de Bangor (2009).",
                            style={"marginBottom": "6px"}),
                        html.P("• Histogramme : distribution des scores SUS sur 20 classes.",
                            style={"marginBottom": "6px"}),
                        html.P("• Radar : moyenne par question, axe forcé entre 1 et 5.",
                            style={"marginBottom": "6px"}),

                        html.P(
                            "• Catégories texte : un graphe par catégorie avec SUS moyen et effectifs.",
                            style={"marginBottom": "6px"}
                        ),

                        html.P(
                            "• Catégories numériques : regroupement automatique en quantiles "
                            "(entre 4 et 8 groupes selon la taille du fichier) afin de garantir "
                            "des graphes lisibles.",
                            style={"marginBottom": "6px"}
                        ),

                        html.Hr(className="my-3"),

                        # ------------------------------------------------
                        # SECTION 3 : CALCUL SUS (SCHÉMA)
                        # ------------------------------------------------
                        html.H5("3. Calcul du score SUS",
                                id="help-calcul-sus", className="mt-3 mb-2"),

                        html.Div([
                            html.P("1. Questions impaires → score = réponse − 1",
                                style={"marginBottom": "4px"}),
                            html.P("2. Questions paires → score = 5 − réponse",
                                style={"marginBottom": "4px"}),
                            html.P("3. Somme des 10 scores ajustés",
                                style={"marginBottom": "4px"}),
                            html.P("4. Score final = somme × 2,5",
                                style={"fontWeight": "bold", "marginBottom": "4px"}),
                        ],
                        style={
                            "border": "1px solid #ddd",
                            "padding": "10px",
                            "borderRadius": "6px",
                            "backgroundColor": "#f9f9f9",
                            "marginBottom": "12px"
                        }),

                        html.P(
                            "Interprétation (Bangor, 2009) : <50 = Mauvais, 50–70 = Acceptable, "
                            "70–80 = Bon, 80–90 = Excellent, >90 = Niveau UX très élevé.",
                            style={"marginBottom": "6px"}
                        ),

                        html.Hr(className="my-3"),

                        # ------------------------------------------------
                        # SECTION 4 : ITEMS OFFICIELS
                        # ------------------------------------------------
                        html.H5("4. Les 10 items officiels du SUS",
                                id="help-items", className="mt-3 mb-2"),

                        html.Ul([
                            html.Li("Q1. Je pense que j’aimerais utiliser ce système fréquemment."),
                            html.Li("Q2. Je trouve le système inutilement complexe."),
                            html.Li("Q3. Le système m’a semblé facile à utiliser."),
                            html.Li("Q4. Je pense qu’un support technique serait nécessaire pour utiliser ce système."),
                            html.Li("Q5. J’ai trouvé que les fonctions du système étaient bien intégrées."),
                            html.Li("Q6. J’ai trouvé qu’il y avait trop d’incohérence dans le système."),
                            html.Li("Q7. Je pense que la plupart des gens apprendraient ce système rapidement."),
                            html.Li("Q8. J’ai trouvé le système très lourd à utiliser."),
                            html.Li("Q9. Je me suis senti très confiant en utilisant le système."),
                            html.Li("Q10. J’ai dû apprendre beaucoup de choses avant d’utiliser le système."),
                        ],
                        style={"lineHeight": "1.4", "marginBottom": "10px"}),

                        html.Hr(className="my-3"),

                        # ------------------------------------------------
                        # SECTION 5 : ANALYSE IA
                        # ------------------------------------------------
                        html.H5("5. Comment fonctionne l’analyse IA",
                                id="help-ai", className="mt-3 mb-2"),

                        html.P(
                            "• L’analyse IA utilise un modèle OpenAI GPT-4o.",
                            style={"marginBottom": "6px"}),
                        html.P(
                            "• Le prompt inclut : score global, distribution, extrêmes, catégories, "
                            "moyennes par question et recommandations.",
                            style={"marginBottom": "6px"}),
                        html.P(
                            "• Seules les statistiques nécessaires sont envoyées au modèle.",
                            style={"marginBottom": "6px"}),
                        html.P(
                            "• Aucune donnée n’est stockée : traitement en mémoire vive uniquement.",
                            style={"marginBottom": "6px"}),
                        html.P(
                            "• Le texte est généré en temps réel.",
                            style={"marginBottom": "6px"}),

                    ],
                    style={"maxHeight": "70vh", "overflowY": "auto"})
                ]
            ),
            dbc.ModalFooter(
                dbc.Button("Fermer", id="close-help-template", className="ms-auto", color="primary")
            ),
        ],
        id="modal-help-template",
        is_open=False,
        size="lg",
    )

    ,



    # Onglets
    dbc.Tabs(
        id="sus-tabs",
        active_tab="tab-dashboard",
        children=[
            dbc.Tab(label="Dashboard", tab_id="tab-dashboard"),
            dbc.Tab(label="Détails", tab_id="tab-details"),
            dbc.Tab(label="Analyse IA", tab_id="tab-ia"),
            dbc.Tab(label="PDF", tab_id="tab-pdf")

        ]
    ),

   dbc.Card(
        dbc.CardBody(
            html.Div([
                html.Div(
                    dcc.Loading(type="circle", children=dashboard_layout),
                    id="tab-dashboard"
                ),
                html.Div(details_layout, id="tab-details", style={"display": "none"}),
                html.Div(ia_layout, id="tab-ia", style={"display": "none"}),
                html.Div(pdf_layout, id="tab-pdf", style={"display": "none"}),

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
    )

], fluid=True)





