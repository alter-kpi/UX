import base64
import io
import os
import tempfile
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
from dash import Input, Output, State, html, dcc, callback_context, no_update
import dash_bootstrap_components as dbc

from components.attrakdiff_layout import ATTRAKDIFF_ITEMS, DIM_COLORS, DIM_LABELS


# ============================================================
# HELPERS — parsing & scoring
# ============================================================

def parse_file(contents, filename):
    _, content_string = contents.split(",")
    decoded = base64.b64decode(content_string)
    try:
        if filename.lower().endswith(".csv"):
            df = pd.read_csv(io.StringIO(decoded.decode("utf-8")))
        else:
            df = pd.read_excel(io.BytesIO(decoded))
        return df, None
    except Exception as e:
        return None, str(e)


def compute_scores(df):
    """
    Calcule les scores par dimension.
    Entrée  : colonnes item_1..item_28, valeurs 1–7.
    Sortie  : dict {dim: score_-3_to_+3}
    """
    dim_vals = {d: [] for d in ["PQ", "HQ-S", "HQ-I", "ATT"]}
    for item_id, _, _, dim in ATTRAKDIFF_ITEMS:
        col = f"item_{item_id}"
        if col in df.columns:
            dim_vals[dim].append(df[col].clip(1, 7).mean())
    return {dim: round(np.mean(vals) - 4, 3) if vals else None
            for dim, vals in dim_vals.items()}


def make_sample_df(n=20):
    np.random.seed(42)
    bias = {"PQ": (4.2, 0.9), "HQ-S": (5.1, 0.8), "HQ-I": (4.8, 1.0), "ATT": (5.3, 0.7)}
    data = {}
    for item_id, _, _, dim in ATTRAKDIFF_ITEMS:
        mu, sigma = bias[dim]
        data[f"item_{item_id}"] = np.random.normal(mu, sigma, n).clip(1, 7).round().astype(int)
    return pd.DataFrame(data)


def make_template_csv():
    return pd.DataFrame(columns=[f"item_{i}" for i in range(1, 29)]).to_csv(index=False)


# ============================================================
# FIGURES
# ============================================================

def make_portfolio(scores):
    hq  = ((scores.get("HQ-S") or 0) + (scores.get("HQ-I") or 0)) / 2
    pq  = scores.get("PQ") or 0
    fig = go.Figure()
    zones = [
        (-3, -3,  0,  0, "Inutile",         "#FFF9C4"),
        (-3,  0,  0,  3, "Trop centré soi", "#FCE4EC"),
        ( 0, -3,  3,  0, "Orienté tâche",   "#E3F2FD"),
        ( 0,  0,  3,  3, "Souhaité ✓",      "#E8F5E9"),
        (-1, -1,  1,  1, "Neutre",          "#ECEFF1"),
    ]
    for x0, y0, x1, y1, label, color in zones:
        fig.add_shape(type="rect", x0=x0, y0=y0, x1=x1, y1=y1,
                      fillcolor=color, opacity=0.55, line_width=0, layer="below")
        fig.add_annotation(x=(x0+x1)/2, y=(y0+y1)/2, text=label,
                           showarrow=False, font=dict(size=10, color="#666"))
    fig.add_hline(y=0, line_dash="dot", line_color="#bbb", line_width=1)
    fig.add_vline(x=0, line_dash="dot", line_color="#bbb", line_width=1)
    fig.add_trace(go.Scatter(
        x=[hq], y=[pq], mode="markers+text",
        marker=dict(size=20, color="#E91E63", symbol="diamond", line=dict(color="white", width=2)),
        text=["Votre produit"], textposition="top center",
        textfont=dict(size=12, color="#E91E63"),
        hovertemplate=f"<b>HQ (moy.)</b>: {hq:+.2f}<br><b>PQ</b>: {pq:+.2f}<extra></extra>",
    ))
    fig.update_layout(
        title=dict(text="Diagramme Portfolio", font=dict(size=15)),
        xaxis=dict(title="Qualité Hédonique (HQ-S + HQ-I) / 2", range=[-3.2, 3.2],
                   zeroline=False, tickvals=[-3,-2,-1,0,1,2,3]),
        yaxis=dict(title="Qualité Pragmatique (PQ)", range=[-3.2, 3.2],
                   zeroline=False, tickvals=[-3,-2,-1,0,1,2,3]),
        showlegend=False, height=430, plot_bgcolor="white", paper_bgcolor="white",
        margin=dict(l=60, r=20, t=50, b=60),
    )
    return fig


def make_radar(scores):
    dims   = ["PQ", "HQ-S", "HQ-I", "ATT"]
    labels = [DIM_LABELS[d] for d in dims]
    vals   = [scores.get(d) or 0 for d in dims]
    vals_n = [(v + 3) / 6 * 100 for v in vals]
    fig = go.Figure(go.Scatterpolar(
        r=vals_n + [vals_n[0]], theta=labels + [labels[0]],
        fill="toself", fillcolor="rgba(33,150,243,0.15)",
        line=dict(color="#2196F3", width=2), mode="lines+markers",
        marker=dict(size=8, color=[DIM_COLORS[d] for d in dims] + [DIM_COLORS[dims[0]]]),
        customdata=[f"{v:+.2f}" for v in vals] + [f"{vals[0]:+.2f}"],
        hovertemplate="%{theta} : %{customdata}<extra></extra>",
        text=[f"{v:+.2f}" for v in vals] + [""], textposition="top center",
    ))
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0,100], tickvals=[0,25,50,75,100],
                            ticktext=["-3","-1,5","0","+1,5","+3"]),
            angularaxis=dict(direction="clockwise"),
        ),
        title=dict(text="Vue Radar", font=dict(size=15)),
        height=400, paper_bgcolor="white", showlegend=False,
        margin=dict(l=40, r=40, t=60, b=40),
    )
    return fig


def make_profile(df):
    rows = []
    for item_id, left, right, dim in ATTRAKDIFF_ITEMS:
        col = f"item_{item_id}"
        if col in df.columns:
            rows.append({
                "label": f"{left}  /  {right}",
                "score": round(df[col].clip(1,7).mean() - 4, 2),
                "dim":   dim,
            })
    fig = go.Figure()
    for dim in ["PQ", "HQ-S", "HQ-I", "ATT"]:
        sub = [r for r in rows if r["dim"] == dim]
        fig.add_trace(go.Bar(
            x=[r["score"] for r in sub], y=[r["label"] for r in sub],
            orientation="h", name=DIM_LABELS[dim],
            marker_color=DIM_COLORS[dim], marker_opacity=0.85,
            hovertemplate="%{y}<br>Score : %{x:+.2f}<extra></extra>",
        ))
    fig.add_vline(x=0, line_dash="solid", line_color="#aaa", line_width=1)
    fig.update_layout(
        title=dict(text="Profil de mots moyen (–3 → +3)", font=dict(size=15)),
        xaxis=dict(title="Score moyen", range=[-3.2, 3.2],
                   tickvals=[-3,-2,-1,0,1,2,3], zeroline=False),
        yaxis=dict(autorange="reversed"),
        barmode="relative", height=750, plot_bgcolor="white", paper_bgcolor="white",
        legend=dict(orientation="h", y=1.02, x=0),
        margin=dict(l=220, r=20, t=70, b=50),
    )
    return fig


# ============================================================
# PDF GENERATION
# ============================================================

def generate_pdf(scores, n_participants, product_name="", ai_text=""):
    """Génère un rapport PDF AttrakDiff avec fpdf2 + kaleido."""
    from fpdf import FPDF

    fig_portfolio = make_portfolio(scores)
    fig_radar     = make_radar(scores)

    def fig_to_tmp(fig, width=700, height=420):
        img_bytes = fig.to_image(format="png", width=width, height=height, scale=2)
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        tmp.write(img_bytes)
        tmp.close()
        return tmp.name

    path_portfolio = fig_to_tmp(fig_portfolio, 700, 420)
    path_radar     = fig_to_tmp(fig_radar, 500, 400)

    class PDF(FPDF):
        def header(self):
            self.set_fill_color(33, 37, 41)
            self.rect(0, 0, 210, 18, "F")
            self.set_font("Helvetica", "B", 12)
            self.set_text_color(255, 255, 255)
            self.set_xy(10, 4)
            self.cell(0, 10, "Alter UX - Rapport AttrakDiff", ln=False)
            self.set_xy(0, 4)
            self.set_font("Helvetica", "", 9)
            self.cell(200, 10, datetime.now().strftime("%d/%m/%Y"), align="R")
            self.set_text_color(0, 0, 0)
            self.ln(14)

        def footer(self):
            self.set_y(-12)
            self.set_font("Helvetica", "I", 8)
            self.set_text_color(150, 150, 150)
            self.cell(0, 10, f"alter-ux.com  -  Page {self.page_no()}", align="C")

    pdf = PDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Titre
    title = f"AttrakDiff{' - ' + product_name if product_name else ''}"
    pdf.set_font("Helvetica", "B", 20)
    pdf.set_text_color(33, 37, 41)
    pdf.cell(0, 10, title, ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 6, f"{n_participants} participants  ·  {datetime.now().strftime('%d %B %Y')}", ln=True)
    pdf.ln(4)

    # Scores
    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(33, 37, 41)
    pdf.cell(0, 8, "Scores par dimension", ln=True)
    pdf.ln(2)

    dim_rgb = {
        "PQ":   (33, 150, 243),
        "HQ-S": (76, 175, 80),
        "HQ-I": (255, 152, 0),
        "ATT":  (233, 30, 99),
    }

    col_w = 45
    for dim in ["PQ", "HQ-S", "HQ-I", "ATT"]:
        r, g, b = dim_rgb[dim]
        pdf.set_fill_color(r, g, b)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(col_w, 7, f" {dim}", fill=True, border=0)

    pdf.ln(7)
    for dim in ["PQ", "HQ-S", "HQ-I", "ATT"]:
        score = scores.get(dim)
        score_txt = f"{score:+.2f}" if score is not None else "–"
        pdf.set_fill_color(245, 245, 245)
        pdf.set_text_color(33, 37, 41)
        pdf.set_font("Helvetica", "B", 14)
        pdf.cell(col_w, 10, score_txt, fill=True, border=0, align="C")

    pdf.ln(10)
    for dim in ["PQ", "HQ-S", "HQ-I", "ATT"]:
        pdf.set_text_color(100, 100, 100)
        pdf.set_font("Helvetica", "", 8)
        pdf.cell(col_w, 5, DIM_LABELS[dim], align="C")

    pdf.ln(10)

    # Interprétation rapide
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(80, 80, 80)
    hq_mean = ((scores.get("HQ-S") or 0) + (scores.get("HQ-I") or 0)) / 2
    pq_val  = scores.get("PQ") or 0
    if hq_mean > 1 and pq_val > 1:
        zone = "Souhaite - le produit est percu comme utile ET attrayant."
    elif hq_mean > 1 and pq_val < 0:
        zone = "Superflu - qualite hedonique elevee mais utilisabilite a ameliorer."
    elif hq_mean < 0 and pq_val > 1:
        zone = "Oriente tache - efficace mais peu stimulant ou identitaire."
    elif hq_mean < 0 and pq_val < 0:
        zone = "Inutile - des ameliorations sont necessaires sur toutes les dimensions."
    else:
        zone = "Neutre - le produit se situe dans la zone centrale du portfolio."
    pdf.multi_cell(0, 6, f"Zone portfolio : {zone}")
    pdf.ln(4)

    # Portfolio
    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(33, 37, 41)
    pdf.cell(0, 8, "Diagramme Portfolio", ln=True)
    pdf.image(path_portfolio, x=10, w=120)
    pdf.ln(4)

    # Radar
    pdf.cell(0, 8, "Vue Radar", ln=True)
    pdf.image(path_radar, x=35, w=90)
    pdf.ln(4)

    # Détail items
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(33, 37, 41)
    pdf.cell(0, 8, "Detail par dimension", ln=True)
    pdf.ln(2)

    for dim in ["PQ", "HQ-S", "HQ-I", "ATT"]:
        r, g, b = dim_rgb[dim]
        pdf.set_fill_color(r, g, b)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Helvetica", "B", 10)
        score_val = scores.get(dim)
        score_str = f"{score_val:+.2f}" if score_val is not None else "N/A"
        pdf.cell(0, 7, f"  {dim} - {DIM_LABELS[dim]}  (score : {score_str})", fill=True, ln=True)

        items_dim = [(i, l, r2) for i, l, r2, d in ATTRAKDIFF_ITEMS if d == dim]
        for item_id, left, right in items_dim:
            pdf.set_fill_color(250, 250, 250)
            pdf.set_text_color(60, 60, 60)
            pdf.set_font("Helvetica", "", 9)
            pdf.cell(0, 5, f"   item_{item_id}   {left}  /  {right}", fill=True, ln=True)
        pdf.ln(3)

    # Analyse IA
    if ai_text and ai_text.strip():
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 13)
        pdf.set_text_color(33, 37, 41)
        pdf.cell(0, 8, "Analyse IA", ln=True)
        pdf.ln(2)
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(50, 50, 50)
        # Rendu ligne par ligne pour gérer les titres markdown
        for line in ai_text.split("\n"):
            if line.startswith("#### "):
                pdf.set_font("Helvetica", "B", 11)
                pdf.multi_cell(0, 6, line.replace("#### ", ""))
                pdf.set_font("Helvetica", "", 10)
            elif line.strip() == "":
                pdf.ln(2)
            else:
                pdf.multi_cell(0, 5, line)

    os.unlink(path_portfolio)
    os.unlink(path_radar)

    return bytes(pdf.output())


# ============================================================
# UI RÉSULTATS
# ============================================================

def make_score_cards(scores, n_participants):
    def color(v):
        if v is None: return "#6c757d"
        if v >= 1:    return "#28a745"
        if v >= 0:    return "#ffc107"
        return "#dc3545"

    cols = [
        dbc.Col(dbc.Card([dbc.CardBody([
            html.Div([
                html.Span("●", style={"color": DIM_COLORS[dim], "fontSize": "20px", "marginRight": "6px"}),
                html.Span(dim, className="fw-bold"),
            ], className="mb-1"),
            html.H4(f"{scores[dim]:+.2f}" if scores[dim] is not None else "–",
                    style={"color": color(scores[dim]), "fontWeight": "700"}),
            html.Small(DIM_LABELS[dim], className="text-muted"),
        ])], className="text-center h-100 shadow-sm"))
        for dim in ["PQ", "HQ-S", "HQ-I", "ATT"]
    ] + [
        dbc.Col(dbc.Card([dbc.CardBody([
            html.Div([html.I(className="bi bi-people-fill me-2 text-muted"),
                      html.Span("Participants", className="fw-bold")], className="mb-1"),
            html.H4(str(n_participants), style={"color": "#6c757d", "fontWeight": "700"}),
            html.Small("réponses analysées", className="text-muted"),
        ])], className="text-center h-100 shadow-sm"))
    ]
    return dbc.Row(cols, className="g-3 mb-3")


def make_action_bar():
    return dbc.Row([
        dbc.Col([
            dbc.Button([html.I(className="bi bi-filetype-pdf me-2"), "Télécharger le rapport PDF"],
                       id="attrakdiff-btn-pdf", color="danger", outline=True, size="sm", n_clicks=0),
        ], width="auto"),
        dbc.Col([
            dbc.Button([html.I(className="bi bi-stars me-2"), "Générer l'analyse IA"],
                       id="attrakdiff-btn-ai", color="primary", outline=True, size="sm", n_clicks=0),
        ], width="auto"),
    ], className="mb-3 g-2")


def make_results_layout(df, scores):
    portfolio = make_portfolio(scores)
    radar     = make_radar(scores)
    profile   = make_profile(df)
    display_df = df[[f"item_{i}" for i in range(1, 29)]].copy()
    display_df.columns = [f"Q{i}" for i in range(1, 29)]

    tabs = dbc.Tabs([
        dbc.Tab(
            dbc.Card(dbc.CardBody(dbc.Row([
                dbc.Col(dcc.Graph(figure=portfolio, config={"displayModeBar": False}), width=7),
                dbc.Col(dcc.Graph(figure=radar,     config={"displayModeBar": False}), width=5),
            ])), className="border-0"),
            label="📊 Portfolio & Radar", tab_id="tab-portfolio",
        ),
        dbc.Tab(
            dbc.Card(dbc.CardBody(
                dcc.Graph(figure=profile, config={"displayModeBar": False})
            ), className="border-0"),
            label="📋 Profil de mots", tab_id="tab-profile",
        ),
        dbc.Tab(
            dbc.Card(dbc.CardBody([
                html.P(f"{len(df)} participants - aperçu des 30 premières lignes",
                       className="text-muted small mb-2"),
                dbc.Table.from_dataframe(display_df.head(30),
                                         striped=True, hover=True, responsive=True, size="sm"),
            ]), className="border-0"),
            label="🔍 Données", tab_id="tab-data",
        ),
        dbc.Tab(
            dbc.Card(dbc.CardBody([
                html.Div(id="attrakdiff-ia-output",
                         children=html.P("Cliquez sur « Générer l'analyse IA » pour obtenir "
                                         "une interprétation automatique de vos résultats.",
                                         className="text-muted")),
            ]), className="border-0"),
            label="🤖 Analyse IA", tab_id="tab-ia",
        ),
    ], active_tab="tab-portfolio", className="mt-2")

    return html.Div([
        html.Hr(),
        make_score_cards(scores, len(df)),
        make_action_bar(),
        tabs,
    ])


# ============================================================
# REGISTER CALLBACKS
# ============================================================

def register_callbacks(app):

    # ── 1. Upload / Fichier exemple → store + résultats ──────
    @app.callback(
        Output("attrakdiff-results",       "children"),
        Output("attrakdiff-upload-status", "children"),
        Output("attrakdiff-store",         "data"),
        Input("attrakdiff-upload",         "contents"),
        Input("attrakdiff-btn-sample",     "n_clicks"),
        State("attrakdiff-upload",         "filename"),
        prevent_initial_call=True,
    )
    def handle_data(contents, n_sample, filename):
        ctx = callback_context
        if not ctx.triggered:
            return no_update, no_update, no_update
        trigger = ctx.triggered[0]["prop_id"]

        if "btn-sample" in trigger and n_sample:
            df     = make_sample_df(20)
            scores = compute_scores(df)
            store  = {"scores": scores, "df_json": df.to_json(), "n": len(df)}
            return (
                make_results_layout(df, scores),
                dbc.Alert([html.I(className="bi bi-check-circle me-2"),
                           "Fichier exemple chargé - 20 participants simulés."],
                          color="success", dismissable=True, className="mt-2"),
                store,
            )

        if "upload" in trigger and contents and filename:
            df, err = parse_file(contents, filename)
            if err:
                return no_update, dbc.Alert(f"Erreur de lecture : {err}", color="danger"), no_update

            missing = [f"item_{i}" for i in range(1, 29) if f"item_{i}" not in df.columns]
            if missing:
                preview = ", ".join(missing[:6]) + ("…" if len(missing) > 6 else "")
                return no_update, dbc.Alert(
                    [html.Strong("Colonnes manquantes : "), preview],
                    color="warning", dismissable=True), no_update

            # Validation valeurs
            for col in [f"item_{i}" for i in range(1, 29)]:
                if col in df.columns and not df[col].between(1, 7).all():
                    return no_update, dbc.Alert(
                        f"La colonne {col} contient des valeurs hors de [1–7]. "
                        "Vérifiez vos données.",
                        color="warning", dismissable=True), no_update

            scores = compute_scores(df)
            store  = {"scores": scores, "df_json": df.to_json(), "n": len(df)}
            return (
                make_results_layout(df, scores),
                dbc.Alert([html.I(className="bi bi-check-circle me-2"),
                           f"{filename} importé - {len(df)} participants."],
                          color="success", dismissable=True, className="mt-2"),
                store,
            )

        return no_update, no_update, no_update

    # ── 2. Téléchargement du modèle CSV ──────────────────────
    @app.callback(
        Output("attrakdiff-download-template", "data"),
        Input("attrakdiff-btn-template",        "n_clicks"),
        prevent_initial_call=True,
    )
    def download_template(n):
        if not n:
            return no_update
        return dict(content=make_template_csv(), filename="attrakdiff_modele.csv", type="text/csv")

    # ── 3. Export PDF ─────────────────────────────────────────
    @app.callback(
        Output("attrakdiff-download-pdf", "data"),
        Input("attrakdiff-btn-pdf",        "n_clicks"),
        State("attrakdiff-store",          "data"),
        prevent_initial_call=True,
    )
    def download_pdf(n, store):
        if not n or not store:
            return no_update
        scores  = store.get("scores", {})
        n_part  = store.get("n", 0)
        ai_text = store.get("ai_text", "")
        pdf_bytes = generate_pdf(scores, n_part, ai_text=ai_text)
        return dcc.send_bytes(pdf_bytes, "rapport_attrakdiff.pdf")

    # ── 4. Analyse IA ─────────────────────────────────────────
    @app.callback(
        Output("attrakdiff-ia-output", "children"),
        Output("attrakdiff-store",     "data", allow_duplicate=True),
        Input("attrakdiff-btn-ai",     "n_clicks"),
        State("attrakdiff-store",      "data"),
        prevent_initial_call=True,
    )
    def generate_ai(n, store):
        if not n or not store:
            return no_update, no_update

        scores = store.get("scores", {})
        n_part = store.get("n", 0)

        prompt = f"""Tu es un expert en UX research et en méthodes d'évaluation de l'expérience utilisateur.

Voici les résultats d'un questionnaire AttrakDiff 2 portant sur {n_part} participants :

- PQ  (Qualité Pragmatique)     : {scores.get('PQ', 'N/A'):+.2f}  (échelle –3 à +3)
- HQ-S (Stimulation hédonique)  : {scores.get('HQ-S', 'N/A'):+.2f}
- HQ-I (Identité hédonique)     : {scores.get('HQ-I', 'N/A'):+.2f}
- ATT  (Attractivité)           : {scores.get('ATT', 'N/A'):+.2f}

Qualité Hédonique moyenne (HQ-S + HQ-I / 2) : {((scores.get('HQ-S') or 0) + (scores.get('HQ-I') or 0)) / 2:+.2f}

Rappel des zones du diagramme portfolio AttrakDiff :
- Souhaité  : HQ > +1 et PQ > +1  (idéal)
- Orienté tâche : HQ < 0 et PQ > +1
- Superflu  : HQ > +1 et PQ < 0
- Inutile   : HQ < 0 et PQ < 0
- Neutre    : zone centrale

Fournis une analyse structurée et professionnelle en français incluant :
1. La zone portfolio dans laquelle se situe le produit et ce que cela signifie
2. L'interprétation de chaque dimension (forces et points à améliorer)
3. 3 recommandations UX concrètes et priorisées pour améliorer l'expérience
4. Une conclusion synthétique en 2-3 phrases

Format : utilise uniquement #### pour les titres, pas d'emojis, pas de tableaux.
"""

        try:
            from openai import OpenAI
            client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1200,
                temperature=0.5,
            )
            ai_text = response.choices[0].message.content.strip()
        except Exception as e:
            return dbc.Alert(
                [html.Strong("Erreur IA : "), str(e),
                 html.Br(),
                 html.Small("Vérifiez que la variable d'environnement OPENAI_API_KEY est définie.")],
                color="danger"), no_update

        # Sauvegarder dans le store pour inclusion dans le PDF
        updated_store = {**store, "ai_text": ai_text}

        # Affichage formaté
        paragraphs = [p.strip() for p in ai_text.split("\n") if p.strip()]
        output = html.Div([
            dbc.Alert(
                [html.I(className="bi bi-stars me-2"), "Analyse générée avec succès"],
                color="success", className="mb-3"
            ),
            *[html.P(p, className="mb-2") for p in paragraphs],
            html.Hr(),
            html.Small([
                html.I(className="bi bi-info-circle me-1"),
                "Cette analyse a été générée par IA et doit être interprétée par un expert UX."
            ], className="text-muted"),
        ])
        return output, updated_store
