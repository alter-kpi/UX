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
        Output('upload-status', 'children'),   # ⭐ nouveau
        Input('upload-data', 'contents'),
        State('upload-data', 'filename'),
        prevent_initial_call=True
    )
    def load_file(contents, filename):

        # Pas de fichier
        if contents is None:
            return "Aucun fichier importé.", None, ""

        # ⭐ Allumer le spinner immédiatement
        upload_msg = "loading"

        try:
            df = parse_upload(contents, filename or "fichier")
            qcols = find_sus_columns(df)

            if len(qcols) != 10:
                return (
                    "❌ Colonnes SUS non détectées (Q1..Q10 / SUS1..SUS10 / 10 numériques).",
                    None,
                    ""     # ⭐ éteindre le spinner
                )

            df = compute_sus(df, qcols)

            info = (
                f"✅ {filename} importé — {len(df)} réponses • "
                f"Score moyen: {np.nanmean(df['SUS_Score']):.1f}"
            )

            return info, df.to_dict('records'), ""   # ⭐ spinner OFF

        except Exception as e:
            return f"❌ Erreur de lecture : {e}", None, ""   # ⭐ spinner OFF




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

        scores = df["SUS_Score"].tolist()
        classes = df["SUS_Class"].value_counts().to_dict() if "SUS_Class" in df else {}

        stats = {
            "Score moyen": round(df["SUS_Score"].mean(), 2),
            "Ecart-type": round(df["SUS_Score"].std(), 2),
            "Min": df["SUS_Score"].min(),
            "Max": df["SUS_Score"].max(),
            "Taille échantillon": len(df)
        }

        categories = {}
        extra_cols = df.columns[11:15]


        if len(extra_cols) > 0:
            for col in extra_cols:
                categories[col] = df[col].value_counts().to_dict()
        else:
            categories = {}

        prompt = ""
        prompt += "Tu es un expert UX senior.\n"
        prompt += "Analyse ce questionnaire SUS de manière claire, pédagogique et utile.\n\n"
        prompt += "Tu réponds en 3000 caractères maximum. RRéponds en utilisant strictement du Markdown.\n\n"
        prompt += "#### pour les titres. **gras** pour les valeurs clés. Des listes à puces pour les points\n\n"
        prompt += "Pas de backticks ni de code blocks. Pas de tableaux\n\n" 
        prompt += "Les titres ne doivent pas être trop gros, ça doit être élégant.\n\n"
        prompt += "Ne renvoie que le texte Markdown.\n\n"

        prompt += "=== SCORE GLOBAL SUS ===\n"
        prompt += f"Scores individuels : {scores}\n"
        prompt += f"Score moyen : {stats['Score moyen']}\n"
        prompt += f"Ecart-type : {stats['Ecart-type']}\n"
        prompt += f"Min : {stats['Min']} - Max : {stats['Max']}\n"
        prompt += f"Taille de l'échantillon : {stats['Taille échantillon']}\n\n"

        prompt += "=== CLASSES SUS ===\n"
        prompt += f"{classes}\n\n"

        prompt += "=== CATEGORIES ===\n"
        prompt += "Les colonnes supplémentaires sont traitées comme des catégories (âge, pays...).\n"
        prompt += f"{categories}\n\n"

        prompt += "=== OBJECTIFS ===\n"
        prompt += "1. Évaluer la satisfaction globale.\n"
        prompt += "2. Identifier les variations importantes.\n"
        prompt += "3. Trouver les sous-populations en difficulté.\n"
        prompt += "4. Décrire les forces du produit.\n"
        prompt += "5. Exposer les points faibles.\n"
        prompt += "6. Proposer des recommandations actionnables.\n"

        return prompt


    @app.callback(
        Output("ai-analysis", "data"),
        Output("ai-processing", "children"),
        Input("file-info", "children"),     # 👈 déclenche TOUJOURS après un import
        State("data-store", "data"),        # 👈 récupère DF
        prevent_initial_call=True
    )
    def run_ai_analysis(_, data):

        if not data:
            return "", ""

        # Spinner
        processing = "loading"

        df = pd.DataFrame(data)

        try:
            prompt = build_ai_prompt(df)
            analysis = generate_ai_analysis(prompt)
        except Exception as e:
            return f"⚠️ Erreur génération IA : {e}", ""

        return analysis, ""




    @app.callback(
        Output("ai-analysis-visible", "children", allow_duplicate=True),
        Input("ai-analysis", "data"),
        Input("sus-tabs", "active_tab"),
        prevent_initial_call=True   # ✅ important avec allow_duplicate
    )
    def sync_ai_visible(ai_text, active_tab):

        # On n'affiche que si on est sur l'onglet IA
        if active_tab != "tab-ia":
            return dash.no_update

        # Dès que ai-analysis est rempli → on affiche le texte
        return ai_text or ""



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



    # ==========================================================
    # 8️⃣ Onglets
    # ==========================================================
    @app.callback(
        Output("tab-dashboard", "style"),
        Output("tab-details", "style"),
        Output("tab-ia", "style"),
        Input("sus-tabs", "active_tab"),
        Input("data-store", "data")
    )
    def show_tabs(active, data):

        is_loaded = data is not None and len(data) > 0

        return (
            # Dashboard
            {"display": "block"} if active == "tab-dashboard" and is_loaded else {"display": "none"},

            # Détails (toujours visible si onglet actif)
            {"display": "block"} if active == "tab-details" else {"display": "none"},

            # IA (toujours visible si onglet actif)
            {"display": "block"} if active == "tab-ia" else {"display": "none"},
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




