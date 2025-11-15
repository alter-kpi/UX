from components.export_pdf import generate_sus_pdf
from components.charts import compute_sus_stats, create_gauge_native, create_acceptability_gauge, create_sus_class_histogram, create_category_hist, empty_fig, create_main_histogram, create_radar
from components.ai_text import generate_ai_analysis
import tempfile
import dash
import os
from dash import Input, Output, State, dash_table, dcc
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
import io, base64
import plotly.express as px
import plotly.graph_objects as go


# --- Détection colonnes SUS ---
SUS_PATTERNS = [
    ["Q1","Q2","Q3","Q4","Q5","Q6","Q7","Q8","Q9","Q10"],
    ["SUS1","SUS2","SUS3","SUS4","SUS5","SUS6","SUS7","SUS8","SUS9","SUS10"],
    ["Item1","Item2","Item3","Item4","Item5","Item6","Item7","Item8","Item9","Item10"],
]

def find_sus_columns(df: pd.DataFrame):
    cols = list(df.columns)
    for pattern in SUS_PATTERNS:
        if all(c in cols for c in pattern): return pattern
    num_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
    return num_cols[:10] if len(num_cols) >= 10 else []

def compute_sus(df: pd.DataFrame, qcols: list[str]) -> pd.DataFrame:
    df = df.copy()
    for i, q in enumerate(qcols, start=1):
        df[q] = pd.to_numeric(df[q], errors="coerce").clip(1,5)
        df[q+"_adj"] = (df[q]-1) if i%2==1 else (5-df[q])
    df["SUS_Score"] = df[[q+"_adj" for q in qcols]].sum(axis=1)*2.5
    return df

def parse_upload(contents, filename):
    ctype, b64 = contents.split(',')
    decoded = base64.b64decode(b64)
    if filename and filename.lower().endswith((".xlsx",".xls")):
        return pd.read_excel(io.BytesIO(decoded))
    try:
        return pd.read_csv(io.BytesIO(decoded))
    except:
        return pd.read_csv(io.BytesIO(decoded), sep=';')

def register_callbacks(app):

    # 1️⃣ Upload -> compute + store + feedback + enable export
    @app.callback(
        Output('file-info','children'),
        Output('data-store','data'),
        Output('btn-export','disabled'),
        Input('upload-data','contents'),
        State('upload-data','filename'),
        prevent_initial_call=True
    )
    def load_file(contents, filename):
        if contents is None:
            return "Aucun fichier importé.", None, True
        try:
            df = parse_upload(contents, filename or "fichier")
            qcols = find_sus_columns(df)
            if len(qcols) != 10:
                return "❌ Colonnes SUS non détectées (Q1..Q10 / SUS1..SUS10 / 10 numériques).", None, True
            df = compute_sus(df, qcols)
            info = f"✅ {filename} importé — {len(df)} réponses • Score moyen: {np.nanmean(df['SUS_Score']):.1f}"
            return info, df.to_dict('records'), False
        except Exception as e:
            return f"❌ Erreur de lecture : {e}", None, True

    # 2️⃣ Table interactive
    @app.callback(
        Output('data-preview','children'),
        Input('data-store','data')
    )
    def show_preview(data):
        if not data: return None
        df = pd.DataFrame(data)
        df = df[[c for c in df.columns if not c.endswith("_adj")]]

        return dash_table.DataTable(
            data=df.to_dict('records'),
            columns=[{"name": i, "id": i} for i in df.columns],
            filter_action="native",
            sort_action="native",
            page_size=10,
            style_table={
                "overflowY": "auto",
                "height": "400px",
                "border": "1px solid #ddd"
            },
            style_cell={
                "textAlign": "center",
                "fontSize": "13px",
                "padding": "5px",
                "whiteSpace": "normal"
            },
            style_header={
                "backgroundColor": "#2c3e50",
                "color": "white",
                "fontWeight": "bold"
            },
            style_data_conditional=[
                {"if": {"state": "active"},
                 "backgroundColor": "#f8f9fa",
                 "border": "1px solid #2980b9"}
            ]
        )

    # 3️⃣ Graphiques + KPI
    @app.callback(
        Output('kpi_count','children'),
        Output('kpi_mean','children'),
        Output('kpi_pct70','children'),
        Output('gauge-graph','figure'),
        Output('acceptability-graph','figure'),
        Output('hist-graph','figure'),
        Output('radar-graph','figure'),
        Output("sus-class-hist", "figure"),
        Input('data-store','data')
    )

    def update_graphs(data):
        if not data:
            empty = empty_fig()
            return "—", "—", "—", empty, empty, empty, empty, empty

        df = pd.DataFrame(data)

        # KPIs
        n = len(df)
        mean_sus = df["SUS_Score"].mean()
        pct70 = float((df["SUS_Score"] >= 72).mean() * 100)

        kpi_count = f"{n:,}".replace(",", " ")
        kpi_mean = f"{mean_sus:.1f}"
        kpi_pct70 = f"{pct70:.1f}%"

        gauge = create_gauge_native(mean_sus)
        accept = create_acceptability_gauge(mean_sus)

        hist = create_main_histogram(df)
        radar = create_radar(df)
        class_hist = create_sus_class_histogram(df)

        return (
            kpi_count,
            kpi_mean,
            kpi_pct70,
            gauge,
            accept,
            hist,
            radar,
            class_hist
        )

        # === Score SUS par catégorie ===
    @app.callback(
        Output("cat-graph-1", "figure"),
        Output("cat-graph-2", "figure"),
        Output("cat-graph-3", "figure"),
        Output("cat-graph-4", "figure"),
        Input("data-store", "data")
    )
    def update_category_graphs(data):
        if not data:
            return [empty_fig()] * 4

        df = pd.DataFrame(data)

        # Colonnes J K L M = index 11 → 14
        extra_cols = df.columns[11:15]

        figures = []
        for i, col in enumerate(extra_cols):
            figures.append(create_category_hist(df, col, i))

        # Compléter à 4
        while len(figures) < 4:
            figures.append(empty_fig())

        return figures

    
    # PDF

    # === 💾 Export PDF ===
    @app.callback(
        Output("export-status", "children"),
        Output("download-pdf", "data"),
        Input("btn-export", "n_clicks"),
        State("data-store", "data"),
        State("gauge-graph", "figure"),
        State("acceptability-graph", "figure"),
        State("hist-graph", "figure"),
        State("radar-graph", "figure"),
        State("sus-class-hist", "figure"),
        State("cat-graph-1", "figure"),
        State("cat-graph-2", "figure"),
        State("cat-graph-3", "figure"),
        State("cat-graph-4", "figure"),
        State("sus-stats-table", "data"),
        State("ai-analysis", "children"), 
        prevent_initial_call=True
    )
    def export_pdf(n_clicks, data,
                gauge_fig, accept_fig, hist_fig, radar_fig,
                class_fig, cat1, cat2, cat3, cat4,
                stats_table,
                ai_text):         
        if not data:
            return "❌ Aucune donnée à exporter", dash.no_update

        # Status
        status = "⏳ Génération du PDF..."

        df = pd.DataFrame(data)

        figs = {
            "SUS moyen": gauge_fig,
            "Acceptabilite": accept_fig,
            "Repartition": hist_fig,
            "Radar": radar_fig,
            "Classes SUS": class_fig,
            "Categorie 1": cat1,
            "Categorie 2": cat2,
            "Categorie 3": cat3,
            "Categorie 4": cat4,
        }

        # TEMP FILE
        output_path = os.path.join(tempfile.gettempdir(), "rapport_SUS.pdf")

        # ⬅️ ENVOI DE L'ANALYSE IA AU PDF
        generate_sus_pdf(df, figs, output_path, ai_text, stats_table)

        # Lecture binaire pour le download
        with open(output_path, "rb") as f:
            pdf_bytes = f.read()

        return "✅ PDF généré avec succès", dcc.send_bytes(
            lambda buffer: buffer.write(pdf_bytes),
            "Rapport_SUS.pdf"
        )




    @app.callback(
        Output("sus-stats-table", "data"),
        Input("data-store", "data")
    )
    def update_sus_stats(data):
        import pandas as pd
        if not data:
            return []
        df = pd.DataFrame(data)
        stats_df = compute_sus_stats(df)
        return stats_df.to_dict("records")
    
    #Analyse IA

        # Analyse IA

    @app.callback(
        Output("ai-analysis", "children"),
        Input("btn-ai", "n_clicks"),
        State("data-store", "data"),
        prevent_initial_call=True
    )
    def run_ai_analysis(n_clicks, data):
        if not data:
            return "Aucune donnée disponible."

        df = pd.DataFrame(data)

        # --- 1. Statistiques globales SUS ---
        sus = df["SUS_Score"].astype(float)
        n = len(sus)
        sus_mean = float(sus.mean())
        sus_median = float(sus.median())
        sus_min = float(sus.min())
        sus_max = float(sus.max())
        sus_std = float(sus.std())
        q1 = float(sus.quantile(0.25))
        q3 = float(sus.quantile(0.75))
        pct72 = float((sus >= 72).mean() * 100)

        # --- 2. Histogramme (résumé) ---
        counts, bin_edges = np.histogram(sus, bins=10)
        hist_desc = {
            f"{int(bin_edges[i])}-{int(bin_edges[i+1])}": int(counts[i])
            for i in range(len(counts))
            if counts[i] > 0
        }

        # --- 3. Répartition par classes SUS (mêmes bornes que le graphique) ---
        bins = [0, 25, 39, 52, 73, 86, 100]
        labels = [
            "Pire imaginable",
            "Mauvais",
            "Acceptable",
            "Bon",
            "Excellent",
            "Meilleur imaginable"
        ]
        classe = pd.cut(sus, bins=bins, labels=labels, right=False)
        class_counts = (
            classe.value_counts()
            .reindex(labels, fill_value=0)
            .astype(int)
            .to_dict()
        )

        # --- 4. Radar : moyennes par question (1–5) ---
        qcols = [
            c for c in df.columns
            if (not c.endswith("_adj"))
            and c != "SUS_Score"
            and pd.api.types.is_numeric_dtype(df[c])
        ]
        qcols = qcols[1:10]  # comme create_radar
        radar_means = df[qcols].mean().round(2).to_dict() if qcols else {}

        # --- 5. Catégories (colonnes J/K/L/M = index 11 à 14) ---
        cat_cols = df.columns[11:15]
        categories = {}
        for col in cat_cols:
            if col not in df.columns:
                continue
            serie = df[col]
            if serie.dropna().empty:
                continue

            tmp = df[[col, "SUS_Score"]].dropna()

            # Même logique que create_category_hist
            if pd.api.types.is_numeric_dtype(tmp[col]):
                vmin, vmax = tmp[col].min(), tmp[col].max()
                amplitude = vmax - vmin
                step = 5
                if amplitude > 50:
                    step = 10
                if amplitude > 200:
                    step = 20
                if amplitude > 500:
                    step = 50
                tmp["group"] = (tmp[col] // step * step).astype(int)
                group_field = "group"
            else:
                group_field = col

            grouped = (
                tmp.groupby(group_field)["SUS_Score"]
                .mean()
                .round(1)
                .sort_values(ascending=False)
            )

            if grouped.empty:
                continue

            # On ne garde que les 6 groupes principaux pour le prompt
            categories[str(col)] = grouped.head(6).to_dict()

        # --- 6. Construction du prompt structuré ---
        prompt = f"""
            Tu es un expert UX. Analyse les résultats d'un questionnaire System Usability Scale (SUS)
            et rédige un texte structuré en sections numérotées. D'une longueur de 600 caractères max.

            1. Synthèse générale (2 à 3 phrases)
            - Score moyen : {sus_mean:.1f} (n = {n})
            - Médiane : {sus_median:.1f}, min : {sus_min:.1f}, max : {sus_max:.1f}
            - Écart-type : {sus_std:.1f}, Q1 : {q1:.1f}, Q3 : {q3:.1f}
            - Pourcentage de répondants avec un score ≥ 72 : {pct72:.1f}%

            2. Répartition des scores
            - Histogramme approché (intervalle -> nombre de réponses) : {hist_desc}
            - Répartition par classes SUS : {class_counts}
            Explique ce que cela dit de la diversité des expériences et de la présence éventuelle d'utilisateurs très satisfaits ou très insatisfaits.

            3. Analyse par segments (catégories)
            - Pour chaque catégorie, on dispose de la moyenne SUS par groupe :
            {categories}
            Repère les segments les plus satisfaits et ceux qui sont en difficulté,
            et formule 2 à 3 insights clés sur les différences entre groupes.

            4. Forces
            - Liste 3 forces majeures en lien avec les résultats (niveau global, items ou segments).

            5. Faiblesses / points de vigilance
            - Liste 3 axes d'amélioration prioritaires.

            6. Recommandations UX
            - Propose 3 à 5 recommandations concrètes, pragmatiques et priorisées
            pour améliorer le SUS, en t'appuyant sur les forces et faiblesses précédentes.

            Contraintes de style :
            - Écris en français.
            - Ton professionnel, clair et accessible.
            - Pas de jargon inutile.
            - Phrases relativement courtes.
            - Ne répète pas les valeurs brutes, interprète-les.
            """

        # --- 7. Appel OpenAI ---
        try:
            analysis = generate_ai_analysis(prompt)
        except Exception as e:
            return f"⚠️ Erreur génération IA : {e}"

        return analysis

