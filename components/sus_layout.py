from dash import html, dcc, dash_table
import dash_bootstrap_components as dbc

layout = dbc.Container([

    html.H2("Analyse du questionnaire SUS", className="text-center mt-3 mb-4"),

    # === Upload section ===
    dbc.Card([
        dbc.CardBody([
            html.H5("1️⃣ Importer vos réponses"),
            html.P("Chargez un fichier Excel ou CSV contenant 10 questions notées de 1 à 5."),
            html.P([
                "Si besoin, vous pouvez ",
                html.A(
                    "télécharger le modèle Excel ici.",
                    href="/assets/template_sus.xlsx",
                    target="_blank",
                    style={"fontWeight": "bold", "textDecoration": "none", "color": "#2980b9"}
                )
            ]),
            dcc.Upload(
                id="upload-data",
                children=html.Div("📂 Glissez votre fichier ici ou cliquez pour le sélectionner"),
                style={
                    "width": "100%", "height": "80px", "lineHeight": "80px",
                    "borderWidth": "1px", "borderStyle": "dashed",
                    "borderRadius": "8px", "textAlign": "center",
                    "marginBottom": "15px"
                },
                multiple=False
            ),
            html.Div(id="file-info", className="text-muted"),
            dcc.Store(id="data-store")
        ])
    ]),

    html.Hr(),

    # === 1️⃣ Aperçu des données ===
    html.Div(id="data-preview"),

    html.Hr(),

    # === 2️⃣ KPI cards alignés ===
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
            html.H6("≥ 70 (Acceptable+)", className="text-muted mb-1"),
            html.H2(id="kpi_pct70", className="mb-0")
        ], className="p-3 text-center bg-white"), md=4),
    ], className="mb-4 g-3"),


    # === 2️⃣ Tableau des statistiques descriptives ===
    html.Div([
        dash_table.DataTable(
            id="sus-stats-table",
            columns=[
                {"name": "Indicateur", "id": "Indicateur"},
                {"name": "Valeur", "id": "Valeur"}
            ],
            data=[],
            style_cell={"textAlign": "left", "padding": "6px", "fontSize": "13px"},
            style_header={"fontWeight": "bold", "backgroundColor": "#f8f9fa"},
            style_table={"width": "70%", "margin": "auto"},
        ),
    ], className="mb-5"),

    # === 3️⃣ Gauges à gauche / Histogramme par classe à droite ===
    dbc.Row([
        dbc.Col([
            html.Div([
                dcc.Graph(
                    id="gauge-graph",
                    config={"displayModeBar": False, "displaylogo": False},
                    style={"height": "180px", "marginBottom": "0px", "backgroundColor": "white"}
                ),
                dcc.Graph(
                    id="acceptability-graph",
                    config={"displayModeBar": False, "displaylogo": False},
                    style={"height": "180px", "marginTop": "0px", "backgroundColor": "white"}
                )
            ], style={
                "backgroundColor": "white",
                "padding": "0",
                "borderRadius": "6px",
                "boxShadow": "0px 1px 3px rgba(0,0,0,0.1)"
            })
        ], md=6),

        dbc.Col([
            dcc.Graph(
                id="sus-class-hist",
                config={"displayModeBar": False, "displaylogo": False},
                style={"height": "360px"}
            ),
        ], md=6),
    ], className="g-4 mb-5"),

    # === 4️⃣ Histogramme principal (gauche) / Radar (droite) ===
    dbc.Row([
        dbc.Col(
            dcc.Graph(
                id="hist-graph",
                config={"displayModeBar": False, "displaylogo": False},
                style={"height": "400px"}
            ),
            md=6
        ),
        dbc.Col(
            dcc.Graph(
                id="radar-graph",
                config={"displayModeBar": False, "displaylogo": False},
                style={"height": "400px"}
            ),
            md=6
        ),
    ], className="g-4 mb-5"),

    html.Hr(),

    html.H4("Analyse par catégorie", className="mt-4 mb-3 text-center"),
    html.Br(),

    # === 5️⃣ Histogrammes par catégorie ===
    dbc.Row([
        dbc.Col(dcc.Graph(id="cat-graph-1", config={"displayModeBar": False}), md=6, xs=12),
        dbc.Col(dcc.Graph(id="cat-graph-2", config={"displayModeBar": False}), md=6, xs=12),
        dbc.Col(dcc.Graph(id="cat-graph-3", config={"displayModeBar": False}), md=6, xs=12),
        dbc.Col(dcc.Graph(id="cat-graph-4", config={"displayModeBar": False}), md=6, xs=12),
    ], className="g-4 mb-4")
    ,

    html.Hr(),

    # === 6️⃣ Bouton Télécharger ===
    html.Div(className="text-center mt-4", children=[
        dbc.Button("Télécharger le rapport PDF", id="btn-export", color="primary"),
        dcc.Loading(
            id="export-loading",
            type="circle",
            children=html.Div(id="export-status", className="text-muted mt-2")
        ),
        dcc.Download(id="download-pdf"),
    ])
], fluid=True)
