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
            html.H6("≥ 72 (Acceptable+)", className="text-muted mb-1"),
            html.H2(id="kpi_pct70", className="mb-0")
        ], className="p-3 text-center bg-white"), md=4),
    ], className="mb-4 g-3"),

    # Gauges
    dbc.Row([
        dbc.Col([
            dcc.Graph(id="gauge-graph", config={"displayModeBar": False}, style={"height": "180px", "marginBottom": "15px"}),
            dcc.Graph(id="acceptability-graph", config={"displayModeBar": False}, style={"height": "180px"})
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
    html.H4("Analyse par catégorie", className="mt-4 mb-3 text-center"),
    html.H6("Scores SUS moyens par groupe (effectifs en gris)", className="text-center text-muted mb-3"),

    dbc.Row([
        dbc.Col(dcc.Graph(id="cat-graph-1", config={"displayModeBar": False}), md=6, xs=12),
        dbc.Col(dcc.Graph(id="cat-graph-2", config={"displayModeBar": False}), md=6, xs=12),
        dbc.Col(dcc.Graph(id="cat-graph-3", config={"displayModeBar": False}), md=6, xs=12),
        dbc.Col(dcc.Graph(id="cat-graph-4", config={"displayModeBar": False}), md=6, xs=12),
    ], className="g-4 mb-4"),

])


# ---- Section Détails ----
details_layout = html.Div([

    html.Div(
        id="data-preview",
        style={
            "maxHeight": "82vh",
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
    html.Div(
        dbc.Button(
            "Générer l'analyse",
            id="btn-ai",
            n_clicks=0,
            color="primary",
            className="mb-3"
        ),
        className="text-center"
    ),

    dcc.Loading(
        id="ai-loading",
        type="circle",
        children=dbc.Card(
            dbc.CardBody(
                html.Div(
                    id="ai-analysis-visible",     # ⭐ VERSION AFFICHÉE
                    style={
                        "whiteSpace": "pre-line",
                        "backgroundColor": "white",
                        "padding": "20px",
                        "borderRadius": "8px",
                        "border": "1px solid #eee",
                        "maxHeight": "75vh",
                        "overflowY": "auto",
                        "fontSize": "15px",
                        "lineHeight": "1.5",
                        "minHeight": "75vh"
                    }
                )
            ),
            className="shadow-sm"
        )
    )
])


# === LAYOUT PRINCIPAL ===
layout = dbc.Container([

    # HEADER
    dbc.Row([
        dbc.Col(
            html.H4("Analyse du questionnaire SUS", className="mt-3 mb-3"),
            md=8
        ),

        dbc.Col(
            dbc.Row([
                dbc.Col(
                    dcc.Upload(
                        id="upload-data",
                        children=html.Div(
                            "📂 Importer fichier Excel",
                            className="btn btn-secondary",
                            style={"cursor": "pointer", "fontWeight": "bold", "whiteSpace": "nowrap"}
                        ),
                        multiple=False,
                        style={"cursor": "pointer"}
                    ),
                    width="auto"
                ),

                dbc.Col(
                    html.A(
                        "📥 Télécharger modèle",
                        href="/assets/template_sus.xlsx",
                        target="_blank",
                        className="btn btn-outline-primary",
                        style={"whiteSpace": "nowrap"}
                    ),
                    width="auto"
                ),

                dbc.Col(
                    dbc.Button(
                        "📄 Générer PDF",
                        id="btn-export",
                        color="primary",
                        disabled=True,
                        style={"whiteSpace": "nowrap"}
                    ),
                    width="auto"
                ),
            ],
            className="g-2 justify-content-end mt-3"),
            md=4
        )
    ]),


    # Feedback
    html.Div(id="file-info", style={"display": "none"}),
    dcc.Loading(
        id="export-spinner",
        type="circle",
        children=html.Div(id="export-status", style={"display": "none"})
    ),

    dcc.Download(id="download-pdf"),
    dcc.Store(id="data-store"),
    dcc.Store(id="fig-store"),


    # ⭐ DIV CACHÉ POUR LE PDF (toujours présent)
    html.Div(id="ai-analysis", style={"display": "none"}),

    # Onglets
    dbc.Tabs(
        id="sus-tabs",
        active_tab="tab-dashboard",
        children=[
            dbc.Tab(label="Dashboard", tab_id="tab-dashboard"),
            dbc.Tab(label="Détails", tab_id="tab-details"),
            dbc.Tab(label="Analyse IA", tab_id="tab-ia"),
        ]
    ),

    dbc.Card(
        dbc.CardBody(
            html.Div(
                id="tab-content",
                style={
                    "minHeight": "85vh",
                    "maxHeight": "85vh",
                    "overflowY": "auto",
                    "padding": "5px",
                    "overflowX": "hidden"
                }
            )
        ),
        className="shadow-sm",
        style={"padding": "0px", "backgroundColor": "#ffffff", "borderRadius": "0 0 10px 10px"}
    ),
], fluid=True)

