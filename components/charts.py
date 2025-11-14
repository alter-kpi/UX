import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np


CATEGORY_COLOR_LIST = [
    "#2980b9",  # bleu
    "#27ae60",  # vert
    "#e67e22",  # orange
    "#8e44ad",  # violet
]



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
        (73, 86, "#5cb85c", "Excellent"),
        (86, 100, "#3c763d", "Meilleur<br>imaginable"),
    ]

    fig = go.Figure()

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

    fig.add_shape(
        type="path",
        path=f"M {score-2} -0.05 L {score+2} -0.05 L {score} -0.25 Z",
        fillcolor="red",
        line=dict(color="red")
    )

    for start, _, _, _ in zones:
        fig.add_annotation(x=start, y=-0.6, text=str(start),
                           showarrow=False, font=dict(size=11, color="gray"))
    fig.add_annotation(x=100, y=-0.6, text="100",
                       showarrow=False, font=dict(size=11, color="gray"))

    fig.update_xaxes(range=[0, 100], visible=False)
    fig.update_yaxes(range=[-0.8, 1.0], visible=False)

    fig.update_layout(
        height=160,
        margin=dict(l=20, r=20, t=20, b=0),
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
        (62, 72, "#f1c40f", "Probabilité<br>élevée"),
        (72, 100, "#27ae60", "Acceptable"),
    ]

    fig = go.Figure()

    for x0, x1, color, label in segments:
        fig.add_shape(type="rect", x0=x0, x1=x1, y0=0, y1=0.4,
                      fillcolor=color, line=dict(width=0))
        fig.add_annotation(
            x=(x0 + x1) / 2, y=-0.65,
            text=label,
            showarrow=False,
            font=dict(size=12, color="black"),
            align="center"
        )

    fig.add_shape(
        type="path",
        path=f"M {score-2} 0.45 L {score+2} 0.45 L {score} 0.70 Z",
        fillcolor="red",
        line=dict(color="red")
    )

    fig.add_annotation(
        x=score, y=1.0,
        text=f"<b>{score:.1f}</b><span style='font-size:11px;'> /100</span>",
        showarrow=False,
        font=dict(color="black", size=15),
        bgcolor="white",
        bordercolor="red",
        borderwidth=2,
        borderpad=3
    )

    fig.update_xaxes(range=[0, 100], visible=False)
    fig.update_yaxes(range=[-0.8, 1.2], visible=False)

    fig.update_layout(
        height=160,
        margin=dict(l=20, r=20, t=0, b=15),
        plot_bgcolor="white",
        paper_bgcolor="white",
        showlegend=False,
    )

    return fig


# ======================================================
# 3️⃣ Histogramme principal SUS
# ======================================================
def create_main_histogram(df):
    import numpy as np
    import plotly.express as px

    mean_sus = float(np.nanmean(df["SUS_Score"]))

    # === Calcul manuel des counts pour fixer le Y max ===
    counts, bins = np.histogram(df["SUS_Score"], bins=20)
    max_count = counts.max()

    # === Histogramme ===
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

    # === Ligne de moyenne ===
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

    # === Layout ===
    fig.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        xaxis=dict(title="Score SUS", gridcolor="#eee"),
        yaxis=dict(
            title="Nombre de réponses",
            gridcolor="#eee",
            range=[0, max_count * 1.15]  # ★ marge pour le label
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
        title="Moyenne par question (1-5)"   # ← Titre
    )

    fig.update_traces(
        fill="toself",
        line_color="#2980b9",
        mode="lines+markers",   # ← pas de texte
        marker=dict(size=7)
    )

    fig.update_layout(
        title=dict(
            x=0.5,               # 🔥 centre le titre
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
# 5️⃣ Histogrammes par categorie (avec couleur par categorie)
# ======================================================
def create_category_hist(df, col, idx):

    if df[col].dropna().empty:
        return empty_fig()

    df_cat = df[[col, "SUS_Score"]].dropna()

    # Regroupement si numerique
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

    # 🎨 Couleur dynamique selon l'index
    color = CATEGORY_COLOR_LIST[idx % len(CATEGORY_COLOR_LIST)]

    # 🟦 Le titre : on remet le nom de la catégorie dans Plotly
    fig = px.bar(
        grouped,
        x=group_field,
        y="SUS_Score",
        text="SUS_Score",
        title=str(col)  # <<< 🔥 Titre propre visible dans l'app
    )

    fig.update_traces(
        texttemplate="%{text:.1f}",
        textposition="outside",
        textfont=dict(size=16),       # 🔥 valeurs plus grosses
        marker_line_color="white",
        marker_line_width=1.2,
        opacity=0.85,
        marker_color=color            # <<< couleur unique
    )

    # Espace vertical pour éviter collision texte
    max_y = grouped["SUS_Score"].max()
    fig.update_yaxes(range=[0, max_y * 1.25], gridcolor="#eee")

    # Layout amélioré
    fig.update_layout(
        title=dict(
            text=str(col),
            x=0.5,
            xanchor="center",
            y=0.95,
            font=dict(size=20, color="#333")    # 🔥 Titre plus grand
        ),
        xaxis_title=None,
        yaxis_title=None,
        plot_bgcolor="white",
        paper_bgcolor="white",
        bargap=0.25,
        margin=dict(l=20, r=20, t=80, b=60),   # <<< espace pour le titre
        height=330,
        font=dict(size=14),                    # labels plus gros
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
    stats = {
        "Score SUS moyen": round(sus.mean(), 2),
        "Taille de l’échantillon": len(sus),
        "Score minimum": round(sus.min(), 1),
        "Score maximum": round(sus.max(), 1),
        "Écart-type": round(sus.std(), 2),
        "Médiane": round(sus.median(), 1),
        "1er quartile (Q1)": round(sus.quantile(0.25), 1),
        "3e quartile (Q3)": round(sus.quantile(0.75), 1),
        "IQR": round(sus.quantile(0.75) - sus.quantile(0.25), 1),
    }
    return pd.DataFrame(stats.items(), columns=["Indicateur", "Valeur"])


# ======================================================
# 7️⃣ Histogramme par classe
# ======================================================
def create_sus_class_histogram(df, score_col="SUS_Score"):
    """Histogramme du nombre de réponses par classe SUS (mêmes couleurs que la jauge)."""

    # Définition des classes SUS
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
        height=360,
        margin=dict(l=30, r=30, t=80, b=30),
                plot_bgcolor="white",
        paper_bgcolor="white",
        showlegend=False
    )

    max_y = counts.max()
    fig.update_yaxes(range=[0, max_y * 1.25])

    return fig



