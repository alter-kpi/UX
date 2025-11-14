# components/home_layout.py
from dash import html
import dash_bootstrap_components as dbc

layout = dbc.Container([
    html.Div([
        html.H3("Analyse de questionnaires UX", className="fw-bold mb-3"),
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

        html.H5("Comment ça marche ?", className="fw-bold mb-4"),

        # --- Étapes avec icônes ---
        dbc.Row([
            dbc.Col(html.Div([
                html.Img(src="/assets/step1.png", style={"width": "60px", "marginBottom": "10px"}),
                html.H6("1. Préparez vos données", className="fw-bold"),
                html.P("Téléchargez le modèle Excel et saisissez les réponses de vos participants.")
            ], className="text-center"), md=3),

            dbc.Col(html.Div([
                html.Img(src="/assets/step2.png", style={"width": "60px", "marginBottom": "10px"}),
                html.H6("2. Importez votre fichier", className="fw-bold"),
                html.P("Chargez votre fichier Excel sur la page du questionnaire.")
            ], className="text-center"), md=3),

            dbc.Col(html.Div([
                html.Img(src="/assets/step3.png", style={"width": "60px", "marginBottom": "10px"}),
                html.H6("3. Visualisez vos résultats", className="fw-bold"),
                html.P("Analysez automatiquement les scores à l’aide de graphiques interactifs.")
            ], className="text-center"), md=3),

            dbc.Col(html.Div([
                html.Img(src="/assets/step4.png", style={"width": "60px", "marginBottom": "10px"}),
                html.H6("4. Téléchargez votre rapport", className="fw-bold"),
                html.P("Exportez un rapport PDF contenant les résultats complets à partager ou archiver.")
            ], className="text-center"), md=3),
        ], className="text-center mb-5"),

        html.H5("Détails des étapes :", className="fw-bold mt-4"),
        html.Br(),
        html.P([
            html.B("1️⃣ Préparez vos données — "),
            "Utilisez le modèle Excel fourni pour chaque questionnaire pour préparer vos données conformément au format attendu par l’application. "
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
    ], className="p-4"),

    html.Hr(className="my-4"),

    html.Footer([
        html.H6("🔒 Confidentialité des données", className="fw-bold"),
        html.P(
            "Les fichiers importés sont traités temporairement en mémoire uniquement le temps de l’analyse. "
            "Aucune donnée n’est stockée, enregistrée ni transmise à des tiers.",
            className="text-muted mb-0"
        )
    ], className="text-center small fixed-footer")


], fluid=True)
