from components.export_pdf import generate_sus_pdf
from components.charts import (
    compute_sus_stats, create_gauge_native, create_acceptability_gauge,
    create_sus_class_histogram, empty_fig,
    create_main_histogram, create_radar, create_category_combined
)
from components.ai_text import generate_ai_analysis
from components.sus_layout import dashboard_layout, details_layout, ia_layout
import tempfile
import dash
import os
from dash import Input, Output, State, dash_table, dcc, html
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
import io, base64


callbacks_registered = False

def register_callbacks(app):
    global callbacks_registered
    if callbacks_registered:
        return
    callbacks_registered = True
    ...


# ==============================================================  
# 🔍 Détection colonnes SUS  
# ==============================================================

SUS_PATTERNS = [
    ["Q1","Q2","Q3","Q4","Q5","Q6","Q7","Q8","Q9","Q10"],
    ["SUS1","SUS2","SUS3","SUS4","SUS5","SUS6","SUS7","SUS8","SUS9","SUS10"],
    ["Item1","Item2","Item3","Item4","Item5","Item6","Item7","Item8","Item9","Item10"],
]

def find_sus_columns(df: pd.DataFrame):
    cols = list(df.columns)
    for pattern in SUS_PATTERNS:
        if all(c in cols for c in pattern):
            return pattern
    num_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
    return num_cols[:10] if len(num_cols) >= 10 else []


# ==============================================================

def compute_sus(df: pd.DataFrame, qcols: list[str]) -> pd.DataFrame:
    df = df.copy()
    for i, q in enumerate(qcols, start=1):
        df[q] = pd.to_numeric(df[q], errors="coerce").clip(1, 5)
        df[q + "_adj"] = (df[q] - 1) if i % 2 == 1 else (5 - df[q])
    df["SUS_Score"] = df[[q + "_adj" for q in qcols]].sum(axis=1) * 2.5
    return df


# ==============================================================

def parse_upload(contents, filename):
    ctype, b64 = contents.split(',')
    decoded = base64.b64decode(b64)

    # Excel
    if filename and filename.lower().endswith((".xlsx", ".xls")):
        return pd.read_excel(io.BytesIO(decoded))

    # CSV
    try:
        return pd.read_csv(io.BytesIO(decoded))
    except:
        return pd.read_csv(io.BytesIO(decoded), sep=';')


# ==============================================================

def register_callbacks(app):

    # ==========================================================
    # 1️⃣ Upload fichier
    # ==========================================================

    @app.callback(
        Output('file-info', 'children'),
        Output('data-store', 'data'),
        Output("ai-analysis-visible-store", "data"),   # <- FLAG IA
        Input('upload-data', 'contents'),
        State('upload-data', 'filename'),
        prevent_initial_call=True
    )
    def load_file(contents, filename):

        if contents is None:
            return "Aucun fichier importé.", None, "idle"

        try:
            df = parse_upload(contents, filename or "fichier")
            qcols = find_sus_columns(df)

            if len(qcols) != 10:
                return (
                    "❌ Colonnes SUS non détectées (Q1..Q10 / SUS1..SUS10 / 10 numériques).",
                    None,
                    "idle"
                )

            df = compute_sus(df, qcols)

            info = (
                f"✅ {filename} importé — {len(df)} réponses • "
                f"Score moyen: {np.nanmean(df['SUS_Score']):.1f}"
            )

            # FLAG IA = ON
            return info, df.to_dict('records'), "run"

        except Exception as e:
            return f"❌ Erreur de lecture : {e}", None, "idle"



    # ==========================================================
    # 2️⃣ Table preview
    # ==========================================================

    @app.callback(
        Output('data-preview', 'children'),
        Input('data-store', 'data')
    )
    def show_preview(data):
        if not data:
            return None

        df = pd.DataFrame(data)
        df = df[[c for c in df.columns if not c.endswith("_adj")]]

        return dash_table.DataTable(
            data=df.to_dict("records"),
            columns=[{"name": i, "id": i} for i in df.columns],
            filter_action="native",
            sort_action="native",

            style_table={"overflowY": "auto", "height": "75vh", "border": "none"},
            style_cell={"textAlign": "center", "fontSize": "13px", "padding": "6px", "border": "none"},
            style_header={
                "backgroundColor": "#2c3e50",
                "color": "white",
                "fontWeight": "bold",
                "border": "none"
            },
            style_data_conditional=[
                {"if": {"state": "active"}, "backgroundColor": "#f8f9fa", "border": "none"}
            ],
            page_size=25
        )



    # ==========================================================
    # 3️⃣ Graphiques + KPIs  **(nouvelle version avec fig-store)**
    # ==========================================================

    @app.callback(
        Output("fig-store", "data"),
        Output('kpi_count','children'),
        Output('kpi_mean','children'),
        Output('kpi_pct70','children'),
        Input('data-store','data')
    )
    def update_graphs(data):

        if not data:
            raise dash.exceptions.PreventUpdate

        df = pd.DataFrame(data)

        # --- KPIs ---
        n = len(df)
        mean_sus = df["SUS_Score"].mean()
        pct70 = float((df["SUS_Score"] >= 72).mean() * 100)

        # --- Graphes ---
        figs = {
            "gauge": create_gauge_native(mean_sus),
            "accept": create_acceptability_gauge(mean_sus),
            "hist": create_main_histogram(df),
            "radar": create_radar(df),
            "class": create_sus_class_histogram(df),
        }

        return (
            figs,
            f"{n:,}".replace(",", " "),
            f"{mean_sus:.1f}",
            f"{pct70:.1f}%"
        )



    # ==========================================================
    # 4️⃣ Catégories
    # ==========================================================

    @app.callback(
        Output("cat-graph-1", "figure"),
        Output("cat-graph-2", "figure"),
        Output("cat-graph-3", "figure"),
        Output("cat-graph-4", "figure"),
        Input("data-store", "data")
    )
    def update_categories(data):
        if not data:
            return [empty_fig()] * 4

        df = pd.DataFrame(data)
        extra_cols = df.columns[11:15]

        figs = []
        for i, col in enumerate(extra_cols):
            figs.append(create_category_combined(df, col, i))

        while len(figs) < 4:
            figs.append(empty_fig())

        return figs



    # ==========================================================
    # 5️⃣ Analyse IA
    # ==========================================================
    
    def build_ai_prompt(df):

        # Scores et classes
        scores = df["SUS_Score"].tolist()
        classes = df["SUS_Class"].value_counts().to_dict() if "SUS_Class" in df else {}

        # Statistiques globales avancées
        stats = {
            "Moyenne": round(df["SUS_Score"].mean(), 2),
            "Médiane": round(df["SUS_Score"].median(), 2),
            "Ecart-type": round(df["SUS_Score"].std(), 2),
            "Q1": round(df["SUS_Score"].quantile(0.25), 2),
            "Q3": round(df["SUS_Score"].quantile(0.75), 2),
            "IQR": round(df["SUS_Score"].quantile(0.75) - df["SUS_Score"].quantile(0.25), 2),
            "Min": df["SUS_Score"].min(),
            "Max": df["SUS_Score"].max(),
            "Taille": len(df),
            "% ≥ 80": round((df["SUS_Score"] >= 80).mean() * 100, 1),
            "% < 50": round((df["SUS_Score"] < 50).mean() * 100, 1)
        }

        # Colonnes SUS (Q1..Q10)
        qcols = [c for c in df.columns if c.startswith("Q") and not c.endswith("_adj")]
        per_question_mean = df[qcols].mean().round(2).to_dict()
        per_question_std = df[qcols].std().round(2).to_dict()

        weakest_q = min(per_question_mean, key=per_question_mean.get)
        strongest_q = max(per_question_mean, key=per_question_mean.get)

        # Catégories (âge, pays…)
        categories = {}
        extra_cols = df.columns[11:15]

        if len(extra_cols) > 0:
            for col in extra_cols:
                categories[col] = df.groupby(col)["SUS_Score"].mean().round(2).to_dict()
        else:
            categories = {}

        weakest_cat = {}
        strongest_cat = {}
        gaps = {}

        for col, dist in categories.items():
            if dist:
                weakest_cat[col] = min(dist, key=dist.get)
                strongest_cat[col] = max(dist, key=dist.get)
                gaps[col] = round(
                    dist[max(dist, key=dist.get)] - dist[min(dist, key=dist.get)], 2
                )

        # ===============================================================
        #  PROMPT STRICT + VERSION LONGUE + CONCLUSION
        # ===============================================================
        prompt = f"""
    Tu es un expert UX senior. Rédige une analyse approfondie, détaillée, mais lisible et professionnelle du questionnaire SUS.

    ➡️ **FORMAT STRICT À RESPECTER :**
    - Utilise uniquement du Markdown.
    - Titres : **uniquement** `#### Titre`.
    - Pas d'autres niveaux de titres.
    - Pas de HTML.
    - Pas d’emojis.
    - Pas de tableaux.
    - Pas de blocs de code.
    - Pas de backticks.
    - Pas plus d’une ligne vide à la suite.
    - Longueur volontairement plus développée : analyse complète + contexte + recommandations + conclusion.

    ➡️ **STRUCTURE EXACTE À SUIVRE :**

    #### Score global
    (Analyse détaillée du score SUS global, interprétation, comparaison aux standards UX, nuances)

    #### Analyse de la distribution
    (Analyse du min, max, médiane, quartiles, % extrêmes, compréhension de la dispersion, interprétation du IQR)

    #### Analyse par question
    (Comparer les moyennes par item, identifier forces/faiblesses, expliquer l’impact de la question la plus faible/forte)

    #### Analyse par catégorie
    (Comparer les groupes si présents, expliquer écarts, identifier sous-populations critiques, analyser les gaps)

    #### Recommandations
    (Listes de recommandations actionnables, structurées, priorisées)

    #### Conclusion
    (Conclusion récapitulative, claire, synthétique, orientée décision)

    Tu dois respecter strictement cette structure.

    ---

    ### DONNÉES À ANALYSER

    **Scores individuels :** {scores}

    **Statistiques globales :**
    - Moyenne : {stats['Moyenne']}
    - Médiane : {stats['Médiane']}
    - Ecart-type : {stats['Ecart-type']}
    - Q1 : {stats['Q1']}
    - Q3 : {stats['Q3']}
    - IQR : {stats['IQR']}
    - Min : {stats['Min']} / Max : {stats['Max']}
    - Taille échantillon : {stats['Taille']}
    - % ≥ 80 : {stats['% ≥ 80']}%
    - % < 50 : {stats['% < 50']}%

    **Répartition des classes (A-F) :** {classes}

    **Moyenne par question :** {per_question_mean}
    **Écart-type par question :** {per_question_std}
    - Question la plus faible : {weakest_q}
    - Question la plus forte : {strongest_q}

    **Catégories :** {categories}
    - Catégories les plus faibles : {weakest_cat}
    - Catégories les plus fortes : {strongest_cat}
    - Écarts max entre groupes : {gaps}

    ---

    Rédige maintenant l'analyse en suivant STRICTEMENT le format imposé, avec une longueur développée, des explications approfondies et une conclusion professionnelle.
    """

        return prompt


    @app.callback(
        Output("ai-analysis-visible", "children", allow_duplicate=True),
        Output("ai-analysis-visible-store", "data", allow_duplicate=True),  # FLAG = off
        Input("ai-analysis-visible-store", "data"),
        State("data-store", "data"),
        prevent_initial_call=True
    )
    def run_ai_when_ready(flag, data):

        # Si aucun fichier ou pas de demande IA → ne rien faire
        if flag != "run" or not data:
            raise dash.exceptions.PreventUpdate

        df = pd.DataFrame(data)

        try:
            prompt = build_ai_prompt(df)
            analysis = generate_ai_analysis(prompt)
            return analysis, "done"

        except Exception as e:
            return f"⚠️ Erreur génération IA : {e}", "done"



    




    # ==========================================================
    # 6️⃣ Stats
    # ==========================================================

    @app.callback(
        Output("sus-stats-table", "data"),
        Input("data-store", "data")
    )
    def update_sus_stats(data):
        if not data:
            return []

        df = pd.DataFrame(data)
        stats_df = compute_sus_stats(df)
        return stats_df.to_dict("records")



    # ==========================================================
    # 7️⃣ Export PDF  **(nouvelle version utilisant fig-store)**
    # ==========================================================

    @app.callback(
        Output("export-status", "children"),
        Output("download-pdf", "data"),
        Input("btn-export", "n_clicks"),
        State("data-store", "data"),
        State("fig-store", "data"),
        State("sus-stats-table", "data"),
        State("ai-analysis", "data"),

        prevent_initial_call=True
    )
    def export_pdf(
        n_clicks, data, figs, stats_table, ai_text
    ):
        if not data:
            return "❌ Aucune donnée à exporter", dash.no_update

        df = pd.DataFrame(data)

        output_path = os.path.join(tempfile.gettempdir(), "rapport_SUS.pdf")

        safe_ai = ai_text if isinstance(ai_text, str) else ""

        generate_sus_pdf(df, figs, output_path, safe_ai, stats_table)

        with open(output_path, "rb") as f:
            pdf_bytes = f.read()

        return "✅ PDF généré avec succès", dcc.send_bytes(
            lambda buffer: buffer.write(pdf_bytes),
            "Rapport_SUS.pdf"
        )

    def generate_sus_pdf_bytes(df, figs, stats_table, ai_text):
        """
        Génére un PDF en mémoire et retourne les bytes.
        """
        # Fichier temporaire
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            path = tmp.name

        # Génération via ton script existant
        generate_sus_pdf(df, figs, path, ai_text, stats_table)

        # Lecture en bytes
        with open(path, "rb") as f:
            data = f.read()

        os.remove(path)
        return data


    # ==========================================================
    #  PDF — Génération + Preview + Télécharger
    # ==========================================================
    @app.callback(
        Output("pdf-preview", "children"),
        Output("pdf-download-zone", "children"),
        Input("btn-generate-pdf", "n_clicks"),
        State("data-store", "data"),
        State("fig-store", "data"),
        State("sus-stats-table", "data"),
        State("ai-analysis", "data"),
        prevent_initial_call=True
    )
    def generate_pdf_preview(n_clicks, data, figs, stats_table, ai_text):

        if not data:
            return "Aucune donnée à exporter.", ""

        df = pd.DataFrame(data)

        # 1) Génération PDF en mémoire
        pdf_bytes = generate_sus_pdf_bytes(df, figs, stats_table, ai_text)
        b64 = base64.b64encode(pdf_bytes).decode("utf-8")

        # 2) Preview dans un Iframe
        iframe = html.Iframe(
            src=f"data:application/pdf;base64,{b64}",
            style={
                "width": "100%",
                "height": "100%",
                "border": "none"
            }
        )

        # 3) Bouton Télécharger
        download_button = html.A(
            dbc.Button("Télécharger le PDF", color="success"),
            href=f"data:application/pdf;base64,{b64}",
            download="Rapport_SUS.pdf",
            target="_blank"
        )

        return iframe, download_button


    # ==========================================================
    # 8️⃣ Onglets
    # ==========================================================
    @app.callback(
        Output("tab-dashboard", "style"),
        Output("tab-details", "style"),
        Output("tab-ia", "style"),
        Output("tab-pdf", "style"),
        Input("sus-tabs", "active_tab"),
        Input("data-store", "data")
    )
    def show_tabs(active, data):

        is_loaded = data is not None and len(data) > 0

        return (
            {"display": "block"} if active == "tab-dashboard" and is_loaded else {"display": "none"},
            {"display": "block"} if active == "tab-details" else {"display": "none"},
            {"display": "block"} if active == "tab-ia" else {"display": "none"},
            {"display": "block"} if active == "tab-pdf" else {"display": "none"},
        )




    # ==========================================================
    # 9️⃣ Activation du bouton PDF
    # ==========================================================

    @app.callback(
        Output("btn-export", "disabled"),
        Input("data-store", "data")
    )
    def toggle_pdf_button(data):

        return False if data else True



    # ==========================================================
    # 3B️⃣ Injection des figures stockées vers les graphes visibles
    # ==========================================================

    @app.callback(
        Output("gauge-graph", "figure"),
        Output("acceptability-graph", "figure"),
        Output("hist-graph", "figure"),
        Output("radar-graph", "figure"),
        Output("sus-class-hist", "figure"),
        Input("fig-store", "data")
    )
    def display_figures(figs):

        if not figs:
            return empty_fig(), empty_fig(), empty_fig(), empty_fig(), empty_fig()

        return (
            figs.get("gauge", empty_fig()),
            figs.get("accept", empty_fig()),
            figs.get("hist", empty_fig()),
            figs.get("radar", empty_fig()),
            figs.get("class", empty_fig())
        )
    
    # ==========================================================
    # RESET
    # ==========================================================


    @app.callback(
        Output("ai-analysis-visible", "children", allow_duplicate=True),
        Output("ai-processing", "children", allow_duplicate=True),
        Output("file-info", "children", allow_duplicate=True),
        Output("sus-tabs", "active_tab", allow_duplicate=True),

        Output("data-store", "data", allow_duplicate=True),
        Output("fig-store", "data", allow_duplicate=True),
        Output("ai-analysis", "data", allow_duplicate=True),

        # ⭐ RESET DU BOUTON UPLOAD
        Output("upload-data", "contents", allow_duplicate=True),
        Output("ai-analysis-visible-store", "data", allow_duplicate=True),


        Input("btn-reset", "n_clicks"),
        prevent_initial_call=True
    )
    def reset_all(n):
        return "", "", "", "tab-dashboard", None, None, "", None, ""





