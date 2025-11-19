
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

            html.Div([
                dcc.Graph(
                    id="gauge-graph",
                    config={"displayModeBar": False},
                    style={"height": "180px"}
                )
            ], className="mb-4"),

            html.Div([
                dcc.Graph(
                    id="acceptability-graph",
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
    # 👉 Zone où le texte IA doit s’afficher
    dcc.Markdown(
        id="ai-analysis-visible"
    )

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
                                "📄 PDF",
                                id="btn-export",
                                color="primary",
                                disabled=True,
                                style={"whiteSpace": "nowrap", "width": "110px"}
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

    dcc.Loading(
        type="circle",
        fullscreen=False,
            children=dbc.Card(
                dbc.CardBody(
                    html.Div([
                        html.Div(dashboard_layout, id="tab-dashboard"),
                        html.Div(details_layout, id="tab-details", style={"display": "none"}),
                        html.Div(ia_layout, id="tab-ia", style={"display": "none"}),
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
    )
], fluid=True)


