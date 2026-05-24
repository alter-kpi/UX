import base64
import io
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from dash import Input, Output, State, html, dcc, callback_context
import dash_bootstrap_components as dbc

from components.attrakdiff_layout import (
    ATTRAKDIFF_ITEMS,
    DIM_COLORS,
    DIM_LABELS,
)

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
    scores = {}
    for dim, vals in dim_vals.items():
        scores[dim] = round(np.mean(vals) - 4, 3) if vals else None
    return scores


def make_sample_df(n=20):
    np.random.seed(42)
    data = {}
    bias = {"PQ": (4.2, 0.9), "HQ-S": (5.1, 0.8), "HQ-I": (4.8, 1.0), "ATT": (5.3, 0.7)}
    for item_id, _, _, dim in ATTRAKDIFF_ITEMS:
        mu, sigma = bias[dim]
        vals = np.random.normal(mu, sigma, n).clip(1, 7).round().astype(int)
        data[f"item_{item_id}"] = vals
    return pd.DataFrame(data)


def make_template_csv():
    cols = [f"item_{i}" for i in range(1, 29)]
    df = pd.DataFrame(columns=cols)
    return df.to_csv(index=False)


# ============================================================
# FIGURES
# ============================================================

def make_portfolio(scores):
    """
    Diagramme Portfolio AttrakDiff :
    X = HQ moyen (HQ-S + HQ-I) / 2   |   Y = PQ
    Zones colorées selon la matrice standard.
    """
    hqs = scores.get("HQ-S") or 0
    hqi = scores.get("HQ-I") or 0
    hq  = (hqs + hqi) / 2
    pq  = scores.get("PQ") or 0

    fig = go.Figure()

    # Zones de fond
    zones = [
        # x0,  y0,   x1,  y1,   label,                couleur
        (-3,   -3,    0,   0,   "Inutile",            "#FFF9C4"),
        (-3,    0,    0,   3,   "Trop centré soi",    "#FCE4EC"),
        ( 0,   -3,    3,   0,   "Orienté tâche",      "#E3F2FD"),
        ( 0,    0,    3,   3,   "Souhaité ✓",         "#E8F5E9"),
        (-1,   -1,    1,   1,   "Neutre",             "#ECEFF1"),
    ]
    for x0, y0, x1, y1, label, color in zones:
        fig.add_shape(
            type="rect", x0=x0, y0=y0, x1=x1, y1=y1,
            fillcolor=color, opacity=0.55, line_width=0, layer="below"
        )
        fig.add_annotation(
            x=(x0 + x1) / 2, y=(y0 + y1) / 2,
            text=label, showarrow=False,
            font=dict(size=10, color="#666"),
        )

    fig.add_hline(y=0, line_dash="dot", line_color="#bbb", line_width=1)
    fig.add_vline(x=0, line_dash="dot", line_color="#bbb", line_width=1)

    # Point produit
    fig.add_trace(go.Scatter(
        x=[hq], y=[pq],
        mode="markers+text",
        marker=dict(size=20, color="#E91E63", symbol="diamond",
                    line=dict(color="white", width=2)),
        text=["Votre produit"],
        textposition="top center",
        textfont=dict(size=12, color="#E91E63"),
        name="Résultat",
        hovertemplate=(
            f"<b>HQ (moy.)</b>: {hq:+.2f}<br>"
            f"<b>PQ</b>: {pq:+.2f}<extra></extra>"
        ),
    ))

    fig.update_layout(
        title=dict(text="Diagramme Portfolio", font=dict(size=15)),
        xaxis=dict(
            title="Qualité Hédonique (HQ-S + HQ-I) / 2",
            range=[-3.2, 3.2], zeroline=False,
            tickvals=[-3, -2, -1, 0, 1, 2, 3],
        ),
        yaxis=dict(
            title="Qualité Pragmatique (PQ)",
            range=[-3.2, 3.2], zeroline=False,
            tickvals=[-3, -2, -1, 0, 1, 2, 3],
        ),
        showlegend=False,
        height=430,
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=60, r=20, t=50, b=60),
    )
    return fig


def make_radar(scores):
    """Radar chart pour les 4 dimensions."""
    dims   = ["PQ", "HQ-S", "HQ-I", "ATT"]
    labels = [DIM_LABELS[d] for d in dims]
    vals   = [scores.get(d) or 0 for d in dims]
    # normalise de [-3, +3] → [0, 100] pour l'affichage
    vals_n = [(v + 3) / 6 * 100 for v in vals]

    fig = go.Figure(go.Scatterpolar(
        r=vals_n + [vals_n[0]],
        theta=labels + [labels[0]],
        fill="toself",
        fillcolor="rgba(33, 150, 243, 0.15)",
        line=dict(color="#2196F3", width=2),
        mode="lines+markers",
        marker=dict(size=8, color=[DIM_COLORS[d] for d in dims] + [DIM_COLORS[dims[0]]]),
        customdata=[f"{v:+.2f}" for v in vals] + [f"{vals[0]:+.2f}"],
        hovertemplate="%{theta} : %{customdata}<extra></extra>",
        text=[f"{v:+.2f}" for v in vals] + [""],
        textposition="top center",
    ))
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100], tickvals=[0, 25, 50, 75, 100],
                            ticktext=["-3", "-1,5", "0", "+1,5", "+3"]),
            angularaxis=dict(direction="clockwise"),
        ),
        title=dict(text="Vue Radar", font=dict(size=15)),
        height=400,
        paper_bgcolor="white",
        showlegend=False,
        margin=dict(l=40, r=40, t=60, b=40),
    )
    return fig


def make_profile(df):
    """
    Profil de mots moyen : barre horizontale pour chaque item,
    regroupé et coloré par dimension.
    """
    rows = []
    for item_id, left, right, dim in ATTRAKDIFF_ITEMS:
        col = f"item_{item_id}"
        if col in df.columns:
            mean_raw = df[col].clip(1, 7).mean()
            mean_score = round(mean_raw - 4, 2)   # –3 à +3
            rows.append({
                "label":      f"{left}  /  {right}",
                "left":       left,
                "right":      right,
                "score":      mean_score,
                "dim":        dim,
                "color":      DIM_COLORS[dim],
                "dim_label":  DIM_LABELS[dim],
            })

    fig = go.Figure()
    for dim in ["PQ", "HQ-S", "HQ-I", "ATT"]:
        sub = [r for r in rows if r["dim"] == dim]
        fig.add_trace(go.Bar(
            x=[r["score"] for r in sub],
            y=[r["label"] for r in sub],
            orientation="h",
            name=DIM_LABELS[dim],
            marker_color=DIM_COLORS[dim],
            marker_opacity=0.8,
            hovertemplate="%{y}<br>Score : %{x:+.2f}<extra></extra>",
        ))

    fig.add_vline(x=0, line_dash="solid", line_color="#aaa", line_width=1)

    fig.update_layout(
        title=dict(text="Profil de mots moyen (–3 → +3)", font=dict(size=15)),
        xaxis=dict(
            title="Score moyen",
            range=[-3.2, 3.2],
            tickvals=[-3, -2, -1, 0, 1, 2, 3],
            zeroline=False,
        ),
        yaxis=dict(autorange="reversed"),
        barmode="relative",
        height=750,
        plot_bgcolor="white",
        paper_bgcolor="white",
        legend=dict(orientation="h", y=1.02, x=0),
        margin=dict(l=220, r=20, t=70, b=50),
    )
    return fig


def make_score_cards(scores, n_participants):
    """4 cartes de score + carte participants."""
    def score_color(v):
        if v is None:  return "#6c757d"
        if v >= 1:     return "#28a745"
        if v >= 0:     return "#ffc107"
        return "#dc3545"

    cards = dbc.Row([
        dbc.Col(
            dbc.Card([
                dbc.CardBody([
                    html.Div([
                        html.Span(
                            "●",
                            style={"color": DIM_COLORS[dim], "fontSize": "20px", "marginRight": "6px"}
                        ),
                        html.Span(dim, className="fw-bold"),
                    ], className="mb-1"),
                    html.H4(
                        f"{scores[dim]:+.2f}" if scores[dim] is not None else "–",
                        style={"color": score_color(scores[dim]), "fontWeight": "700"}
                    ),
                    html.Small(DIM_LABELS[dim], className="text-muted"),
                ])
            ], className="text-center h-100 shadow-sm"),
        )
        for dim in ["PQ", "HQ-S", "HQ-I", "ATT"]
    ] + [
        dbc.Col(
            dbc.Card([
                dbc.CardBody([
                    html.Div([
                        html.I(className="bi bi-people-fill me-2 text-muted"),
                        html.Span("Participants", className="fw-bold"),
                    ], className="mb-1"),
                    html.H4(str(n_participants), style={"color": "#6c757d", "fontWeight": "700"}),
                    html.Small("réponses analysées", className="text-muted"),
                ])
            ], className="text-center h-100 shadow-sm"),
        )
    ], className="g-3 mb-4")
    return cards


def make_results_layout(df, scores):
    """Assemble l'UI complète des résultats en onglets."""
    portfolio = make_portfolio(scores)
    radar     = make_radar(scores)
    profile   = make_profile(df)

    # Rename colonnes pour affichage
    display_df = df[[f"item_{i}" for i in range(1, 29)]].copy()
    display_df.columns = [f"Q{i}" for i in range(1, 29)]

    tabs = dbc.Tabs([
        # Onglet 1 : Portfolio + Radar
        dbc.Tab(
            dbc.Card(dbc.CardBody(
                dbc.Row([
                    dbc.Col(dcc.Graph(figure=portfolio, config={"displayModeBar": False}), width=7),
                    dbc.Col(dcc.Graph(figure=radar,     config={"displayModeBar": False}), width=5),
                ])
            ), className="border-0"),
            label="📊 Portfolio & Radar",
            tab_id="tab-portfolio",
        ),
        # Onglet 2 : Profil de mots
        dbc.Tab(
            dbc.Card(dbc.CardBody(
                dcc.Graph(figure=profile, config={"displayModeBar": False})
            ), className="border-0"),
            label="📋 Profil de mots",
            tab_id="tab-profile",
        ),
        # Onglet 3 : Données brutes
        dbc.Tab(
            dbc.Card(dbc.CardBody([
                html.P(
                    f"{len(df)} participants — aperçu des 30 premières lignes",
                    className="text-muted small mb-2"
                ),
                dbc.Table.from_dataframe(
                    display_df.head(30),
                    striped=True, hover=True, responsive=True, size="sm"
                ),
            ]), className="border-0"),
            label="🔍 Données brutes",
            tab_id="tab-data",
        ),
    ], active_tab="tab-portfolio", className="mt-2")

    return html.Div([
        html.Hr(),
        make_score_cards(scores, len(df)),
        tabs,
    ])


# ============================================================
# REGISTER CALLBACKS
# ============================================================

def register_callbacks(app):

    # --- Upload / Fichier exemple ---
    @app.callback(
        Output("attrakdiff-results",       "children"),
        Output("attrakdiff-upload-status", "children"),
        Input("attrakdiff-upload",         "contents"),
        Input("attrakdiff-btn-sample",     "n_clicks"),
        State("attrakdiff-upload",         "filename"),
        prevent_initial_call=True,
    )
    def handle_data(contents, n_sample, filename):
        ctx = callback_context
        if not ctx.triggered:
            return "", ""
        trigger = ctx.triggered[0]["prop_id"]

        # ---- Fichier exemple ----
        if "btn-sample" in trigger and n_sample:
            df     = make_sample_df(20)
            scores = compute_scores(df)
            return (
                make_results_layout(df, scores),
                dbc.Alert(
                    [html.I(className="bi bi-check-circle me-2"),
                     "Fichier exemple chargé — 20 participants simulés."],
                    color="success", dismissable=True, className="mt-2"
                ),
            )

        # ---- Upload fichier ----
        if "upload" in trigger and contents and filename:
            df, err = parse_file(contents, filename)
            if err:
                return "", dbc.Alert(f"Erreur de lecture : {err}", color="danger")

            # Validation colonnes
            missing = [f"item_{i}" for i in range(1, 29) if f"item_{i}" not in df.columns]
            if missing:
                preview = ", ".join(missing[:6]) + ("…" if len(missing) > 6 else "")
                return "", dbc.Alert(
                    [html.Strong("Colonnes manquantes : "), preview,
                     html.Br(),
                     html.Small("Assurez-vous que vos colonnes s'appellent item_1 à item_28.")],
                    color="warning", dismissable=True
                )

            # Validation valeurs
            for col in [f"item_{i}" for i in range(1, 29)]:
                if not df[col].between(1, 7).all():
                    return "", dbc.Alert(
                        f"La colonne {col} contient des valeurs hors de [1–7]. "
                        "Vérifiez vos données.",
                        color="warning", dismissable=True
                    )

            scores = compute_scores(df)
            return (
                make_results_layout(df, scores),
                dbc.Alert(
                    [html.I(className="bi bi-check-circle me-2"),
                     f"{filename} importé — {len(df)} participants."],
                    color="success", dismissable=True, className="mt-2"
                ),
            )

        return "", ""

    # --- Téléchargement du modèle CSV ---
    @app.callback(
        Output("attrakdiff-download-template", "data"),
        Input("attrakdiff-btn-template",        "n_clicks"),
        prevent_initial_call=True,
    )
    def download_template(n):
        if not n:
            return None
        csv_content = make_template_csv()
        return dict(
            content=csv_content,
            filename="attrakdiff_modele.csv",
            type="text/csv",
        )
