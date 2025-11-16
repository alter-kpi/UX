# components/home_layout.py
from dash import html
import dash_bootstrap_components as dbc

layout = dbc.Container([

    # ============================================================
    # TITRE PRINCIPAL (descendu)
    # ============================================================
    html.H3("Analyse de questionnaires UX",
            className="fw-bold mb-4",
            style={"marginTop": "45px", "color": "#000"}),
    
    html.Hr(),

    # Texte introductif
    html.P([
        "Cette application est là pour vous aider dans l’",
        html.B("analyse statistique des questionnaires liés à l’expérience utilisateur (UX)"),
        "."
    ]),
    html.P([
        "Pour sa première version, ",
        html.B("l’application est limitée à l’analyse du questionnaire System Usability Scale (SUS)"),
        "."
    ]),
    html.P(
        "Après importation d’un fichier Excel contenant les réponses au questionnaire, "
        "les résultats sont traités automatiquement, visualisés sous forme de graphiques, "
        "et un rapport PDF peut être généré."
    ),

    html.Hr(className="my-4"),

    # ============================================================
    # 4 CARDS — Les étapes
    # ============================================================
    html.H4("Comment ça marche ?", className="fw-bold mb-4"),

    dbc.Row([

        dbc.Col(
            dbc.Card([
                html.I(className="bi bi-file-earmark-spreadsheet h1 text-primary mb-2"),
                html.H5("1. Préparez vos données", className="fw-bold"),
                html.P("Téléchargez le modèle Excel et saisissez les réponses des participants.")
            ], className="text-center p-3 shadow-sm h-100"),
            md=3
        ),

        dbc.Col(
            dbc.Card([
                html.I(className="bi bi-upload h1 text-primary mb-2"),
                html.H5("2. Importez votre fichier", className="fw-bold"),
                html.P("Chargez votre fichier Excel depuis la section Questionnaire SUS.")
            ], className="text-center p-3 shadow-sm h-100"),
            md=3
        ),

        dbc.Col(
            dbc.Card([
                html.I(className="bi bi-bar-chart-line h1 text-primary mb-2"),
                html.H5("3. Visualisez vos résultats", className="fw-bold"),
                html.P("Analysez automatiquement les scores et leurs répartitions.")
            ], className="text-center p-3 shadow-sm h-100"),
            md=3
        ),

        dbc.Col(
            dbc.Card([
                html.I(className="bi bi-file-earmark-pdf h1 text-primary mb-2"),
                html.H5("4. Exportez un rapport PDF", className="fw-bold"),
                html.P("Générez un rapport PDF professionnel, prêt à être partagé.")
            ], className="text-center p-3 shadow-sm h-100"),
            md=3
        ),

    ], className="g-4 mb-5"),

    # ============================================================
    # SECTION — Détails des étapes + IMAGE À DROITE
    # ============================================================
    html.Hr(className="my-4"),

    dbc.Row([

        # -------- Colonne gauche : texte --------
        dbc.Col([
            html.H5("Détails des étapes :", className="fw-bold mt-4"),
            html.Br(),

            html.P([
                html.B("1️⃣ Préparez vos données — "),
                "Utilisez le modèle Excel fourni pour chaque questionnaire pour préparer vos données conformément au format attendu par l’application."
            ]),
            html.P([
                html.B("2️⃣ Importez votre fichier — "),
                "Importez votre fichier Excel sur la page de chaque questionnaire."
            ]),
            html.P([
                html.B("3️⃣ Visualisez vos résultats — "),
                "Les scores sont calculés automatiquement et affichés sous forme de graphiques interactifs."
            ]),
            html.P([
                html.B("4️⃣ Téléchargez votre rapport — "),
                "Un rapport PDF contenant les résultats peut être généré pour archivage ou partage."
            ]),
        ], md=6),

        # -------- Colonne droite : image --------
        dbc.Col([
            html.Img(
                src="/assets/home.png",
                style={
                    "width": "100%",
                    "maxWidth": "500",
                    "display": "block",
                    "margin": "0 auto"
                }
            )
        ], md=6, className="d-flex align-items-center"),

    ], className="mb-5"),


    # ============================================================
    # FOOTER
    # ============================================================
    html.Hr(className="my-4"),

    html.Footer([
        html.H6("🔒 Confidentialité des données", className="fw-bold"),
        html.P(
            "Les fichiers importés sont traités temporairement en mémoire uniquement le temps de l’analyse. "
            "Aucune donnée n’est stockée ni transmise à des tiers.",
            className="text-muted mb-0"
        )
    ], className="text-center small fixed-footer"),

], fluid=True)
