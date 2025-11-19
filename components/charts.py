import plotly.graph_objects as go
import plotly.express as px
import plotly.io as pio
import pandas as pd
import numpy as np

# 🔥 FIX GLOBAL — éviter les erreurs de template Plotly (pattern shape)
pio.templates.default = "plotly"

CATEGORY_COLOR_LIST = [
    "#2980b9",  # bleu
    "#27ae60",  # vert
    "#e67e22",  # orange
    "#8e44ad",  # violet
]

# ======================================================
# 🎯 Fonction utilitaire — récupère la couleur du segment
# ======================================================
def get_zone_color(score, zones):
    for x0, x1, color, _ in zones:
        if x0 <= score < x1:
            return color
    return zones[-1][2]  # fallback


# ======================================================
# 🚫 Figure vide (utilisée quand pas de données)
# ======================================================
def empty_fig():
    f = go.Figure()
    f.update_layout(
        xaxis={'visible': False},
        yaxis={'visible': False},
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=0, r=0, t=0, b=0),
        height=250
    )
    return f


# ======================================================
# 1️⃣ Jauge principale SUS
# ======================================================
def create_gauge_native(score: float):
    zones = [
        (0, 25, "#FF0000", "Pire<br>imaginable"),
        (25, 39, "#f0ad4e", "Mauvais"),
        (39, 52, "#f7ec13", "Acceptable"),
        (52, 73, "#5bc0de", "Bon"),
        (73, 85, "#5cb85c", "Excellent"),
        (85, 100, "#3c763d", "Meilleur<br>imaginable"),
    ]

    fig = go.Figure()

    # Fond coloré
    for x0, x1, color, label in zones:
        fig.add_shape(
            type="rect", x0=x0, x1=x1, y0=0, y1=0.4,
            fillcolor=color, line=dict(width=0)
        )
        fig.add_annotation(
            x=(x0 + x1) / 2, y=0.68,
            text=label,
            showarrow=False,
            font=dict(size=12, color="black"),
            align="center"
        )

    # 🎯 Couleur dynamique du curseur
    needle_color = get_zone_color(score, zones)

    fig.add_shape(
        type="path",
        path=f"M {score-2} -0.25 L {score+2} -0.25 L {score} -0.05 Z",
        fillcolor=needle_color,
        line=dict(color="black", width=1)

    )

    # Graduation
    for start, _, _, _ in zones:
        fig.add_annotation(x=start, y=-0.6, text=str(start),
                           showarrow=False, font=dict(size=11, color="gray"))
    fig.add_annotation(x=100, y=-0.6, text="100",
                       showarrow=False, font=dict(size=11, color="gray"))

    fig.update_xaxes(range=[0, 100], visible=False)
    fig.update_yaxes(range=[-0.8, 1.0], visible=False)

    fig.update_layout(
    title=dict(
        text="Score SUS — Échelle Bangor (2009)",
        x=0.5,
        y=0.97,
        xanchor="center",
        font=dict(size=14, color="#666")
    ),
    height=180,         # +20 px pour laisser la place du titre
    margin=dict(l=20, r=20, t=45, b=0),  # ↑ top augmenté
    plot_bgcolor="white",
    paper_bgcolor="white",
    showlegend=False,
    )


    return fig


# ======================================================
# 2️⃣ Jauge d’acceptabilité
# ======================================================
def create_acceptability_gauge(score: float):
    segments = [
        (0, 50, "#FF0000", "Non acceptable"),
        (50, 62, "#f39c12", "Probabilité<br>faible"),
        (62, 70, "#f1c40f", "Probabilité<br>élevée"),
        (70, 100, "#27ae60", "Acceptable"),
    ]

    fig = go.Figure()

    # Fond coloré
    for x0, x1, color, label in segments:
        fig.add_shape(type="rect", x0=x0, x1=x1, y0=0, y1=0.4,
                      fillcolor=color, line=dict(width=0))
        fig.add_annotation(
            x=(x0 + x1) / 2, y=0.68,
            text=label,
            showarrow=False,
            font=dict(size=12, color="black"),
            align="center"
        )

    # 🎯 Couleur dynamique du curseur
    needle_color = get_zone_color(score, segments)

    fig.add_shape(
        type="path",
        path=f"M {score-2} -0.25 L {score+2} -0.25 L {score} -0.05 Z",
        fillcolor=needle_color,
        line=dict(color="black", width=1)

    )

    # Graduation
    for start, _, _, _ in segments:
        fig.add_annotation(x=start, y=-0.6, text=str(start),
                           showarrow=False, font=dict(size=11, color="gray"))
    fig.add_annotation(x=100, y=-0.6, text="100",
                       showarrow=False, font=dict(size=11, color="gray"))

    fig.update_xaxes(range=[0, 100], visible=False)
    fig.update_yaxes(range=[-0.8, 1.2], visible=False)

    fig.update_layout(
    title=dict(
        text="Acceptabilité SUS",
        x=0.5,
        y=0.97,
        xanchor="center",
        font=dict(size=13, color="#666")
    ),
    height=180,         # même logique
    margin=dict(l=20, r=20, t=45, b=15),
    plot_bgcolor="white",
    paper_bgcolor="white",
    showlegend=False,
    )


    return fig


# ======================================================
# 3️⃣ Histogramme principal SUS
# ======================================================
def create_main_histogram(df):
    mean_sus = float(np.nanmean(df["SUS_Score"]))

    counts, bins = np.histogram(df["SUS_Score"], bins=20)
    max_count = counts.max()

    fig = px.histogram(
        df,
        x="SUS_Score",
        nbins=20,
        title="Répartition des scores SUS",
        color_discrete_sequence=["#2980b9"],
        text_auto=True
    )

    fig.update_traces(
        marker_line_color="white",
        marker_line_width=1.5,
        opacity=0.85
    )

    fig.add_vline(
        x=mean_sus,
        line_width=2,
        line_dash="dash",
        line_color="#e74c3c"
    )

    fig.add_annotation(
        x=mean_sus,
        y=max_count * 1.12,
        yshift=12,
        text=f"Moyenne : {mean_sus:.1f}",
        showarrow=False,
        font=dict(size=12, color="grey")
    )

    fig.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        xaxis=dict(title="Score SUS", gridcolor="#eee"),
        yaxis=dict(
            title="Nombre de réponses",
            gridcolor="#eee",
            range=[0, max_count * 1.15]
        ),
        title_x=0.5,
        font=dict(size=13),
        margin=dict(l=30, r=30, t=60, b=30),
        height=400
    )

    return fig


# ======================================================
# 4️⃣ Radar
# ======================================================
def create_radar(df):
    qcols = [
        c for c in df.columns
        if (not c.endswith("_adj"))
        and c != "SUS_Score"
        and pd.api.types.is_numeric_dtype(df[c])
    ]

    qcols = qcols[1:10]

    mean_items = df[qcols].mean(numeric_only=True).reset_index()
    mean_items.columns = ["Item", "Score"]

    fig = px.line_polar(
        mean_items,
        r="Score",
        theta="Item",
        line_close=True,
        range_r=[0, 5],
        title="Moyenne par question (1-5)"
    )

    fig.update_traces(
        fill="toself",
        line_color="#2980b9",
        mode="lines+markers",
        marker=dict(size=7)
    )

    fig.update_layout(
        title=dict(
            x=0.5,
            xanchor="center",
            font=dict(size=20, color="#333"),
            pad=dict(t=20)
        ),
        polar=dict(
            radialaxis=dict(showticklabels=True, tickfont=dict(size=12)),
            angularaxis=dict(tickfont=dict(size=12))
        ),
        margin=dict(l=30, r=30, t=60, b=30),
        height=400
    )

    return fig


# ======================================================
# 5️⃣ Histogrammes par catégorie
# ======================================================
def create_category_hist(df, col, idx):

    if df[col].dropna().empty:
        return empty_fig()

    df_cat = df[[col, "SUS_Score"]].dropna()

    # Regroupement si numérique
    if pd.api.types.is_numeric_dtype(df_cat[col]):
        vmin, vmax = df_cat[col].min(), df_cat[col].max()
        amplitude = vmax - vmin
        step = 5
        if amplitude > 50: step = 10
        if amplitude > 200: step = 20
        if amplitude > 500: step = 50
        df_cat["group"] = (df_cat[col] // step * step).astype(int)
        group_field = "group"
    else:
        group_field = col

    grouped = (
        df_cat.groupby(group_field, dropna=True)["SUS_Score"]
            .mean()
            .reset_index()
            .sort_values(group_field)
    )

    if grouped.empty:
        return empty_fig()

    color = CATEGORY_COLOR_LIST[idx % len(CATEGORY_COLOR_LIST)]

    safe_title = str(col).encode("ascii", errors="ignore").decode()

    fig = px.bar(
        grouped,
        x=group_field,
        y="SUS_Score",
        text="SUS_Score",
        title=safe_title
    )

    fig.update_traces(marker_pattern_shape="")

    fig.update_traces(
        texttemplate="%{text:.1f}",
        textposition="outside",
        textfont=dict(size=16),
        marker_line_color="white",
        marker_line_width=1.2,
        opacity=0.85,
        marker_color=color
    )

    max_y = grouped["SUS_Score"].max()
    fig.update_yaxes(range=[0, max_y * 1.25], gridcolor="#eee")

    fig.update_layout(
        title=dict(
            text=safe_title,
            x=0.5,
            xanchor="center",
            y=0.95,
            font=dict(size=20, color="#333")
        ),
        xaxis_title=None,
        yaxis_title=None,
        plot_bgcolor="white",
        paper_bgcolor="white",
        bargap=0.25,
        margin=dict(l=20, r=20, t=80, b=60),
        height=330,
        font=dict(size=14),
        xaxis=dict(tickfont=dict(size=14)),
        yaxis=dict(tickfont=dict(size=14))
    )

    return fig


# ======================================================
# 6️⃣ Statistiques
# ======================================================
def compute_sus_stats(df):
    if df.empty:
        return pd.DataFrame(columns=["Indicateur", "Valeur"])

    sus = df["SUS_Score"]

    Q1 = sus.quantile(0.25)
    Q3 = sus.quantile(0.75)
    IQR = Q3 - Q1

    stats = {
        # Indicateurs centraux
        "Score SUS moyen": round(sus.mean(), 2),
        "Taille de l’échantillon": len(sus),
        "Médiane": round(sus.median(), 1),

        # Étendue
        "Score minimum": round(sus.min(), 1),
        "Score maximum": round(sus.max(), 1),
        "Amplitude (max - min)": round(sus.max() - sus.min(), 1),

        # Dispersion
        "Écart-type": round(sus.std(), 2),
        "Coefficient de variation (%)": round((sus.std() / sus.mean()) * 100, 1),
        "1er quartile (Q1)": round(Q1, 1),
        "3e quartile (Q3)": round(Q3, 1),
        "IQR (Q3 - Q1)": round(IQR, 1),

        # Indicateurs opérationnels
        "% des scores ≥ 70": round((sus >= 70).mean() * 100, 1),
        "% des scores ≤ 50": round((sus <= 50).mean() * 100, 1),
    }

    return pd.DataFrame(stats.items(), columns=["Indicateur", "Valeur"])



# ======================================================
# 7️⃣ Histogramme par classe
# ======================================================
def create_sus_class_histogram(df, score_col="SUS_Score"):
    bins = [0, 25, 39, 52, 73, 86, 100]
    labels = [
        "Pire<br>imaginable",
        "Mauvais",
        "Acceptable",
        "Bon",
        "Excellent",
        "Meilleur<br>imaginable"
    ]
    colors = ["#FF0000", "#f0ad4e", "#f7ec13", "#5bc0de", "#5cb85c", "#3c763d"]

    df = df.copy()
    df["Classe SUS"] = pd.cut(df[score_col], bins=bins, labels=labels, right=False)
    counts = df["Classe SUS"].value_counts().reindex(labels, fill_value=0)

    fig = go.Figure()
    for label, count, color in zip(labels, counts, colors):
        fig.add_trace(go.Bar(
            x=[label],
            y=[count],
            marker_color=color,
            text=[count],
            textposition="outside"
        ))

    fig.update_layout(
        title=dict(
            text="Répartition des scores SUS par classe",
            x=0.5
        ),
        xaxis=dict(
            tickangle=-45,
            tickfont=dict(size=12)
        ),
        yaxis=dict(
            title="Nombre de répondants",
            zeroline=True,
            tickfont=dict(size=12, color="white")
        ),
        height=420,
        margin=dict(l=30, r=30, t=80, b=30),
        plot_bgcolor="white",
        paper_bgcolor="white",
        showlegend=False
    )

    max_y = counts.max()
    fig.update_yaxes(range=[0, max_y * 1.25])

    return fig

# ======================================================
# 5️⃣ TER — Graphique combiné SUS + effectifs
# ======================================================
from plotly.subplots import make_subplots

def create_category_combined(df, col, idx):

    if df[col].dropna().empty:
        return empty_fig()

    df_cat = df[[col, "SUS_Score"]].dropna()

    # Regroupement si numérique
    if pd.api.types.is_numeric_dtype(df_cat[col]):
        vmin, vmax = df_cat[col].min(), df_cat[col].max()
        amplitude = vmax - vmin
        step = 5
        if amplitude > 50: step = 10
        if amplitude > 200: step = 20
        if amplitude > 500: step = 50
        df_cat["group"] = (df_cat[col] // step * step).astype(int)
        group_field = "group"
    else:
        group_field = col

    # Statistiques : SUS + effectifs
    grouped = (
        df_cat.groupby(group_field, dropna=True)
              .agg(SUS_mean=("SUS_Score", "mean"),
                   count=(col, "size"))
              .reset_index()
              .sort_values(group_field)
    )

    if grouped.empty:
        return empty_fig()

    # Couleur SUS
    color = CATEGORY_COLOR_LIST[idx % len(CATEGORY_COLOR_LIST)]
    safe_title = str(col)

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # === 1) Barres SUS (principales) ===
    fig.add_trace(
        go.Bar(
            x=grouped[group_field],
            y=grouped["SUS_mean"],
            name="SUS moyen",
            marker_color=color,
            marker_line_color="white",
            marker_line_width=1.2,
            text=[f"{v:.1f}" for v in grouped["SUS_mean"]],
            textposition="outside",
            opacity=0.9
        ),
        secondary_y=False
    )

    # === 2) Barre fine grise (effectif) ===
    fig.add_trace(
        go.Bar(
            x=grouped[group_field],
            y=grouped["count"],
            name="Effectif",
            marker_color="#7f8c8d",
            opacity=1,
            width=0.25,
            text=grouped["count"],
            textposition="inside",
            textfont=dict(color="white", size=12)
        ),
        secondary_y=True
    )

    # Axes Y
    max_sus = grouped["SUS_mean"].max()
    max_count = grouped["count"].max()

    # Axe SUS → le plus haut, permet textposition="outside"
    fig.update_yaxes(range=[0, max_sus * 1.25], visible=False, secondary_y=False)

    # Axe effectif → toujours plus petit que l'axe SUS
    fig.update_yaxes(range=[0, max_count * 1.7], visible=False, secondary_y=True)


    fig.update_layout(
        title=dict(
            text=safe_title,
            x=0.5,
            font=dict(size=18, color="#333")
        ),
        plot_bgcolor="white",
        paper_bgcolor="white",
        barmode="overlay",
        bargap=0.30,
        margin=dict(l=20, r=20, t=60, b=60),
        height=330,
        font=dict(size=14),
        showlegend=False
    )

    return fig
