import streamlit as st
from PIL import Image
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from fpdf import FPDF
from datetime import date
import tempfile

# Titre et introduction

st.set_page_config(page_title="AlterUX - Analyse SUS", layout="centered")

st.markdown(
    """
    <style>
        :root {
            color-scheme: only light;
        }
        * {
            font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif;
        }
        .stApp,
        .stApp header,
        .stApp [data-testid="stHeader"],
        .stApp [data-testid="stSidebar"],
        .stApp [data-testid="stToolbar"],
        .stApp [data-testid="stSidebar"] > div,
        .stApp [data-testid="block-container"] {
            background-color: #ffffff !important;
            color: #111827 !important;
        }
        .stApp [data-testid="block-container"] {
            padding-top: 2rem;
            padding-bottom: 3rem;
            max-width: 900px;
        }
        .stApp a,
        .stApp label,
        .stApp .stCheckbox,
        .stApp .stRadio,
        .stApp .stSelectbox,
        .stApp .stMarkdown,
        .stApp .stText,
        .stApp .stDataFrame,
        .stApp .stTable {
            color: #111827 !important;
        }
        h1, h2, h3, h4, h5 {
            font-weight: 600 !important;
        }
        .hero {
            background: linear-gradient(135deg, #f7f9ff 0%, #ffffff 60%);
            border: 1px solid #e5e7eb;
            border-radius: 24px;
            padding: 2.8rem 3rem;
            margin-bottom: 2.5rem;
            box-shadow: 0 18px 45px rgba(15, 23, 42, 0.12);
        }
        .hero__eyebrow {
            text-transform: uppercase;
            letter-spacing: 0.2em;
            font-size: 0.8rem;
            color: #6b7280;
            margin-bottom: 0.5rem;
        }
        .hero h1 {
            font-size: clamp(2rem, 4vw, 2.6rem);
            margin-bottom: 1rem;
        }
        .hero p {
            font-size: 1rem;
            line-height: 1.7;
            margin-bottom: 1.5rem;
            color: #374151;
        }
        .hero__chips {
            display: flex;
            flex-wrap: wrap;
            gap: 0.6rem;
            margin-bottom: 1.5rem;
        }
        .hero__chip {
            background: rgba(37, 99, 235, 0.08);
            color: #1d4ed8;
            border-radius: 999px;
            padding: 0.45rem 1rem;
            font-size: 0.85rem;
            font-weight: 500;
        }
        .hero__callout {
            display: grid;
            gap: 0.75rem;
        }
        .hero__card {
            background: rgba(255, 255, 255, 0.85);
            border: 1px solid #e5e7eb;
            border-radius: 20px;
            padding: 1.5rem 1.75rem;
            box-shadow: 0 12px 30px rgba(30, 64, 175, 0.12);
        }
        .hero__card h4 {
            margin-bottom: 0.6rem;
            font-size: 1rem;
        }
        .hero__card ul {
            margin: 0;
            padding-left: 1.1rem;
            color: #374151;
        }
        .section-card {
            background: #ffffff;
            border: 1px solid #e5e7eb;
            border-radius: 20px;
            padding: 2rem 2.2rem;
            margin-bottom: 2rem;
            box-shadow: 0 18px 35px rgba(15, 23, 42, 0.08);
        }
        .section-card h3 {
            margin-top: 0;
            margin-bottom: 0.8rem;
        }
        .section-card p {
            color: #4b5563;
        }
        .step-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1.2rem;
            margin-top: 1.4rem;
        }
        .step-card {
            border: 1px solid #e5e7eb;
            border-radius: 18px;
            padding: 1.4rem;
            background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
            box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.6);
        }
        .step-card strong {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 2.1rem;
            height: 2.1rem;
            border-radius: 999px;
            background: #2563eb;
            color: #ffffff;
            margin-bottom: 0.9rem;
            font-size: 0.9rem;
        }
        .cta-row {
            display: flex;
            flex-wrap: wrap;
            gap: 1rem;
            margin-top: 1.4rem;
        }
        .cta-row > div {
            flex: 1 1 220px;
        }
        .divider {
            height: 1px;
            background: linear-gradient(90deg, rgba(229, 231, 235, 0), rgba(229, 231, 235, 1), rgba(229, 231, 235, 0));
            margin: 2.5rem 0 2rem;
        }
        div[data-testid="stFileUploader"] {
            padding: 1.6rem;
            border-radius: 16px;
            border: 1px dashed #cbd5f5;
            background: #f8fbff;
        }
        div[data-testid="stFileUploader"] label {
            font-weight: 500;
        }
        .stDownloadButton button, .stButton button {
            background: linear-gradient(135deg, #2563eb, #1d4ed8);
            color: #ffffff !important;
            border-radius: 999px;
            padding: 0.75rem 1.7rem;
            border: none;
            font-weight: 600;
            box-shadow: 0 12px 25px rgba(37, 99, 235, 0.25);
        }
        .stDownloadButton button:hover, .stButton button:hover {
            background: linear-gradient(135deg, #1d4ed8, #1e40af);
        }
        .metric-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 1rem;
            margin-top: 1.2rem;
        }
        .metric-card {
            border-radius: 16px;
            padding: 1.2rem 1.3rem;
            border: 1px solid #e5e7eb;
            background: #ffffff;
            box-shadow: inset 0 1px 0 rgba(255,255,255,0.6);
        }
        .metric-card span {
            display: block;
        }
        .metric-card .metric-label {
            font-size: 0.8rem;
            color: #6b7280;
            text-transform: uppercase;
            letter-spacing: 0.08em;
        }
        .metric-card .metric-value {
            font-size: 1.6rem;
            font-weight: 600;
            margin-top: 0.4rem;
        }
        .metric-card .metric-description {
            margin-top: 0.5rem;
            font-size: 0.85rem;
            color: #6b7280;
        }
        .empty-state {
            margin-top: 0.8rem;
            background: #f9fafb;
            border: 1px dashed #d1d5db;
            border-radius: 12px;
            padding: 1rem 1.2rem;
            color: #4b5563;
        }
        .results-section {
            margin-bottom: 2.8rem;
        }
        .stSidebar {
            padding-top: 2rem;
        }
        .stSidebar > div {
            border-left: 1px solid #e5e7eb;
            padding-left: 1rem;
        }
        @media (max-width: 768px) {
            .hero {
                padding: 2.2rem;
            }
            .hero__callout {
                margin-top: 1.6rem;
            }
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero">
        <div class="hero__eyebrow">Plateforme AlterUX</div>
        <h1>📊 Analyse de questionnaires UX</h1>
        <p>Centralisez vos réponses, obtenez une synthèse claire des scores SUS et partagez un rapport élégant en quelques clics. L'interface met en avant les informations clés tout en respectant les standards RGPD.</p>
        <div class="hero__chips">
            <span class="hero__chip">Calculs automatisés</span>
            <span class="hero__chip">Rapport PDF prêt à partager</span>
            <span class="hero__chip">Analyse bilingue des questions</span>
        </div>
        <div class="hero__callout">
            <div class="hero__card">
                <h4>En un coup d'œil</h4>
                <ul>
                    <li>Importez vos réponses au format Excel.</li>
                    <li>Visualisez instantanément les indicateurs clés.</li>
                    <li>Téléchargez un rapport structuré pour vos parties prenantes.</li>
                </ul>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.container():
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.markdown("### Étapes du processus")
    st.markdown(
        """
        <div class="step-grid">
            <div class="step-card">
                <strong>1</strong>
                <h4>Préparer le fichier</h4>
                <p>Dupliquez le modèle AlterUX pour structurer vos données : une ligne par répondant, les dix questions standard et les champs personnalisés facultatifs.</p>
            </div>
            <div class="step-card">
                <strong>2</strong>
                <h4>Importer vos réponses</h4>
                <p>Chargez le fichier complété. Les données restent en mémoire le temps de l’analyse uniquement, sans persistance.</p>
            </div>
            <div class="step-card">
                <strong>3</strong>
                <h4>Explorer les indicateurs</h4>
                <p>Tableaux et visualisations présentent la distribution des scores, les regroupements et le détail des questions.</p>
            </div>
            <div class="step-card">
                <strong>4</strong>
                <h4>Exporter le rapport</h4>
                <p>Générez un PDF soigné pour partager les enseignements avec l’équipe projet ou vos clients.</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with open("template_sus.xlsx", "rb") as f:
        template_bytes = f.read()

    st.markdown("<div class='cta-row'>", unsafe_allow_html=True)
    st.download_button(
        label="Télécharger le modèle Excel",
        data=template_bytes,
        file_name="template_sus.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

with st.container():
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.markdown("### Importer votre fichier")
    st.markdown("Déposez un fichier Excel conforme au modèle pour lancer l’analyse.")
    uploaded_file = st.file_uploader("Charger le fichier Excel", type=["xlsx"])
    st.markdown("</div>", unsafe_allow_html=True)

# Paramètres des couleurs

zone_colors = ["#d9534f", "#f0ad4e", "#f7ec13", "#5bc0de", "#5cb85c", "#3c763d"]
zones = [
    (0, 25, zone_colors[0], "Pire imaginable"),
    (25, 39, zone_colors[1], "Mauvais"),
    (39, 52, zone_colors[2], "Acceptable"),
    (52, 73, zone_colors[3], "Bon"),
    (73, 86, zone_colors[4], "Excellent"),
    (86, 100, zone_colors[5], "Meilleur imaginable")
]

# Menu latéral
st.sidebar.title("Paramètres")

# Choix du questionnaire
questionnaire_type = st.sidebar.radio(
    "Type de questionnaire",
    ["SUS", "Autre (à venir)"]
)

st.sidebar.markdown("---")

# RGPD
with st.sidebar.expander("🔒 Données et confidentialité (RGPD)"):
    st.markdown(
        "Les fichiers que vous importez ne sont **jamais stockés**.\n\n"
        "Ils sont traités **temporairement en mémoire**, uniquement le temps de l’analyse.\n\n"
        "Aucune donnée personnelle n’est conservée ou transmise à des tiers."
    )

st.sidebar.markdown(
    """
    <div style="background:#f8fbff;border:1px solid #dbeafe;border-radius:16px;padding:1rem 1.2rem;margin-top:1.5rem;color:#1f2937;">
        <strong>Astuce</strong><br>
        Importez plusieurs versions de vos tests pour comparer l’évolution du score moyen et documenter facilement vos itérations UX.
    </div>
    """,
    unsafe_allow_html=True,
)

sus_questions = {
    "Question1": {
        "Français": "Je voudrais utiliser ce système fréquemment.",
        "English": "I think that I would like to use this system frequently."
    },
    "Question2": {
        "Français": "Ce système est inutilement complexe.",
        "English": "I found the system unnecessarily complex."
    },
    "Question3": {
        "Français": "Ce système est facile à utiliser.",
        "English": "I thought the system was easy to use."
    },
    "Question4": {
        "Français": "J'aurais besoin du soutien d’un technicien pour être capable d’utiliser ce système.",
        "English": "I think that I would need the support of a technical person to be able to use this system."
    },
    "Question5": {
        "Français": "Les différentes fonctionnalités de ce système sont bien intégrées.",
        "English": "I found the various functions in this system were well integrated."
    },
    "Question6": {
        "Français": "Il y a trop d’incohérences dans ce système.",
        "English": "I thought there was too much inconsistency in this system."
    },
    "Question7": {
        "Français": "La plupart des gens apprendront à utiliser ce système très rapidement.",
        "English": "I would imagine that most people would learn to use this system very quickly."
    },
    "Question8": {
        "Français": "Ce système est très lourd à utiliser.",
        "English": "I found the system very cumbersome to use."
    },
    "Question9": {
        "Français": "Je me suis senti(e) très en confiance en utilisant ce système.",
        "English": "I felt very confident using the system."
    },
    "Question10": {
        "Français": "J’ai eu besoin d’apprendre beaucoup de choses avant de pouvoir utiliser ce système.",
        "English": "I needed to learn a lot of things before I could get going with this system."
    }
}

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file, sheet_name=0)

        # Colonnes de questions
        questions = [f"Question{i}" for i in range(1, 11)]
        # Colonnes de catégories de L à O (index 11 à 14)
        category_columns = df.columns[11:15]
        # Conserver celles qui existent et ne sont pas vides
        custom_columns = [col for col in category_columns if col in df.columns and df[col].notna().any()]
        # Identifier leur type
        category_info = {
            col: "Numérique" if pd.api.types.is_numeric_dtype(df[col]) else "Texte"
            for col in custom_columns
        }

        # Vérification des colonnes de questions
        if not all(col in df.columns for col in questions):
            st.error("❌ Le fichier doit contenir les colonnes 'Question1' à 'Question10'.")
        else:
            df_sus = df[questions]


            def calculate_sus(row):
                score = 0
                for i in range(10):
                    val = row[i]
                    if i % 2 == 0:
                        score += val - 1
                    else:
                        score += 5 - val
                return score * 2.5

            df['SUS_Score'] = df_sus.apply(calculate_sus, axis=1)

            avg_score = df['SUS_Score'].mean()
           
            # Légende des questions dans la sidebar
            with st.sidebar.expander("📋 Questions du questionnaire"):
                for i, q in enumerate(questions, 1):
                    st.markdown(f"**Q{i}** : {sus_questions[q]['Français']}")

            sample_size = len(df)
            median_score = df["SUS_Score"].median()
            std_score = df["SUS_Score"].std()
            min_score = df["SUS_Score"].min()
            max_score = df["SUS_Score"].max()

            overview_html = f"""
            <div class="section-card results-section">
                <h3>Vue d'ensemble</h3>
                <p>Les indicateurs principaux permettent de situer rapidement la performance globale du parcours évalué.</p>
                <div class="metric-grid">
                    <div class="metric-card">
                        <span class="metric-label">Score moyen</span>
                        <span class="metric-value">{avg_score:.1f}</span>
                        <span class="metric-description">sur 100</span>
                    </div>
                    <div class="metric-card">
                        <span class="metric-label">Participants</span>
                        <span class="metric-value">{sample_size}</span>
                        <span class="metric-description">répondants analysés</span>
                    </div>
                    <div class="metric-card">
                        <span class="metric-label">Médiane</span>
                        <span class="metric-value">{median_score:.1f}</span>
                        <span class="metric-description">écart-type {std_score:.2f}</span>
                    </div>
                    <div class="metric-card">
                        <span class="metric-label">Amplitude</span>
                        <span class="metric-value">{min_score:.1f} – {max_score:.1f}</span>
                        <span class="metric-description">valeurs minimum et maximum</span>
                    </div>
                </div>
            </div>
            """
            st.markdown(overview_html, unsafe_allow_html=True)

            def create_gauge(avg_score, zones, mode="white"):
                bg_color = "white" if mode == "white" else "black"
                text_color = "black" if mode == "white" else "white"

                fig, ax = plt.subplots(figsize=(6, 1.5))
                fig.patch.set_facecolor(bg_color)
                ax.set_facecolor(bg_color)

                for start, end, zone_color, label in zones:
                    ax.barh(0, width=end - start, left=start, color=zone_color, edgecolor='white', height=0.5)

                ax.plot(avg_score, 0, marker='v', color='red', markersize=12)
                ax.text(avg_score, -0.3, f"{avg_score:.1f}", ha='center', fontsize=12,
                        bbox=dict(facecolor='white', edgecolor='red', boxstyle='round,pad=0.2', alpha=0.9))

                for start, end, _, label in zones:
                    center = (start + end) / 2
                    ax.text(center, 0.35, label, ha='center', fontsize=9, color=text_color,
                            bbox=dict(facecolor=bg_color, alpha=0, edgecolor='none', boxstyle='round,pad=0.2'), rotation=30)

                for start, end, _, _ in zones:
                    ax.text(start, -0.6, f"{start}", ha='center', va='top', fontsize=8, color=text_color)
                ax.text(100, -0.6, "100", ha='center', va='top', fontsize=8, color=text_color)

                ax.set_xlim(0, 100)
                ax.set_ylim(-0.7, 0.8)
                ax.axis('off')
                fig.tight_layout()
                return fig

            fig_jauge = create_gauge(avg_score, zones, mode="white")

            st.markdown("<div class='section-card results-section'>", unsafe_allow_html=True)
            st.markdown("### Score global SUS")
            st.markdown("Visualisez la position du score moyen par rapport aux zones de performance usuelles du questionnaire SUS.")
            st.pyplot(fig_jauge)
            st.markdown("</div>", unsafe_allow_html=True)

            # Statistiques descriptives
            q1 = df['SUS_Score'].quantile(0.25)
            q3 = df['SUS_Score'].quantile(0.75)
            iqr = q3 - q1

            general_stats_df = pd.DataFrame({
                "Indicateur": [
                    "Score SUS moyen",
                    "Taille de l’échantillon",
                    "Score minimum",
                    "Score maximum",
                    "Écart-type",
                    "Médiane",
                    "1er quartile (Q1)",
                    "3e quartile (Q3)",
                    "IQR"
                ],
                "Valeur": [
                    f"{avg_score:.1f}",
                    sample_size,
                    f"{min_score:.1f}",
                    f"{max_score:.1f}",
                    f"{std_score:.2f}",
                    f"{median_score:.1f}",
                    f"{q1:.1f}",
                    f"{q3:.1f}",
                    f"{iqr:.1f}"
                ]
            })
            general_stats_df.index = range(1, len(general_stats_df) + 1)

            st.markdown("<div class='section-card results-section'>", unsafe_allow_html=True)
            st.markdown("### Statistiques descriptives")
            st.table(general_stats_df)
            st.markdown("</div>", unsafe_allow_html=True)

            # Histogramme
            st.markdown("<div class='section-card results-section'>", unsafe_allow_html=True)
            st.markdown("### Distribution des scores")
            st.markdown("Visualisez la proportion de répondants dans chaque zone de maturité SUS.")

            def create_distribution(distribution, colors, mode="white"):
                bg_color = "white" if mode == "white" else "black"
                text_color = "black" if mode == "white" else "white"

                fig, ax = plt.subplots(figsize=(6, 3))
                fig.patch.set_facecolor(bg_color)
                ax.set_facecolor(bg_color)

                bars = ax.bar(distribution.index, distribution.values, color=colors)

                for bar in bars:
                    height = bar.get_height()
                    ax.text(
                        bar.get_x() + bar.get_width() / 2,
                        height + 0.2,
                        int(height),
                        ha='center',
                        fontsize=10,
                        color=text_color,
                        bbox=dict(facecolor='none', edgecolor='none')
                    )

                ax.set_ylim(0, max(distribution.values) + 2)
                ax.get_yaxis().set_visible(False)

                for spine in ['top', 'right', 'left']:
                    ax.spines[spine].set_visible(False)

                ax.spines['bottom'].set_color(text_color)
                ax.tick_params(axis='x', colors=text_color)
                plt.xticks(rotation=30)

                fig.tight_layout()
                return fig

            bins = [0, 25, 39, 52, 73, 86, 100]
            labels = [z[3] for z in zones]
            colors = [z[2] for z in zones]

            categories = pd.cut(df['SUS_Score'], bins=bins, labels=labels, include_lowest=True, right=True)
            distribution = categories.value_counts().sort_index()

            fig_dist = create_distribution(distribution, colors, mode="white")
            st.pyplot(fig_dist)
            st.markdown("</div>", unsafe_allow_html=True)

            # Histogramme des scores SUS par catégorie
            st.markdown("<div class='section-card results-section'>", unsafe_allow_html=True)
            st.markdown("### Score SUS par catégorie")
            st.markdown("Comparez les moyennes selon vos attributs personnalisés pour identifier les segments à renforcer.")

            def create_category_chart(group_means, mode="white"):
                bg_color = "white" if mode == "white" else "black"
                text_color = "black" if mode == "white" else "white"

                fig, ax = plt.subplots(figsize=(6, 3))
                fig.patch.set_facecolor(bg_color)
                ax.set_facecolor(bg_color)

                bars = ax.bar(group_means.index, group_means.values, color="#5bc0de")
                ax.set_ylabel("Score SUS moyen", color=text_color)

                for bar in bars:
                    height = bar.get_height()
                    ax.text(
                        bar.get_x() + bar.get_width() / 2,
                        height + 0.5,
                        f"{height:.1f}",
                        ha='center',
                        fontsize=9,
                        color=text_color,
                        bbox=dict(facecolor='none', edgecolor='none')
                    )

                ax.set_ylim(0, min(100, max(group_means.values) + 10))
                ax.tick_params(axis='x', rotation=30, colors=text_color)
                ax.tick_params(axis='y', colors=text_color)

                for spine in ['top', 'right']:
                    ax.spines[spine].set_visible(False)
                ax.spines['left'].set_color(text_color)
                ax.spines['bottom'].set_color(text_color)

                fig.tight_layout()
                return fig

            if category_info:
                selected_category = st.selectbox("Choisissez une catégorie :", list(category_info.keys()))

                if category_info[selected_category] == "Numérique":
                    try:
                        binned = pd.cut(df[selected_category], bins=5)
                        df["_cat_display"] = binned.astype(str)
                    except Exception as e:
                        st.warning(f"Erreur lors du regroupement par tranches : {e}")
                        df["_cat_display"] = df[selected_category].astype(str)
                else:
                    df["_cat_display"] = df[selected_category].astype(str)

                group_means = df.groupby("_cat_display", sort=True)["SUS_Score"].mean().sort_index()
                fig_cat = create_category_chart(group_means, mode="white")
                st.pyplot(fig_cat)

                df.drop(columns=["_cat_display"], inplace=True, errors="ignore")
            else:
                st.markdown(
                    "<div class='empty-state'>Ajoutez des colonnes de catégorisation dans le modèle pour visualiser ces regroupements.</div>",
                    unsafe_allow_html=True,
                )

            st.markdown("</div>", unsafe_allow_html=True)

            # Radar - Score SUS par question
            st.markdown("<div class='section-card results-section'>", unsafe_allow_html=True)
            st.markdown("### Score moyen par question")
            st.markdown("Évaluez l’équilibre des dix items du SUS afin de prioriser les actions d’amélioration.")

            def create_radar_chart(df, questions, mode="white"):
                bg_color = "white" if mode == "white" else "black"
                text_color = "black" if mode == "white" else "white"

                question_means = df[questions].mean()
                radar_labels = [f"Q{i}" for i in range(1, 11)]
                values = question_means.tolist() + [question_means.tolist()[0]]
                angles = np.linspace(0, 2 * np.pi, len(radar_labels), endpoint=False).tolist() + [0]

                fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))

                fig.patch.set_facecolor(bg_color)
                ax.set_facecolor(bg_color)

                ax.plot(angles, values, color='cyan', linewidth=1)
                ax.fill(angles, values, color='cyan', alpha=0.25)

                ax.set_xticks(angles[:-1])
                ax.set_xticklabels(radar_labels, fontsize=8, color=text_color)

                ax.set_yticks([1, 2, 3, 4, 5])
                ax.set_yticklabels(["1", "2", "3", "4", "5"], fontsize=8, color=text_color)
                ax.set_ylim(1, 5)
                ax.set_theta_direction(-1)

                ax.tick_params(colors=text_color)
                ax.spines['polar'].set_color(text_color)

                fig.tight_layout()
                return fig

            fig_radar = create_radar_chart(df, questions, mode="white")
            st.pyplot(fig_radar)
            st.markdown("</div>", unsafe_allow_html=True)

            # Statistiques par question
            with st.container():
                st.markdown("<div class='section-card results-section'>", unsafe_allow_html=True)
                st.markdown("### Indicateurs par question")
                st.markdown("Statistiques de tendance centrale et de dispersion pour chaque question du questionnaire.")

                question_stats_df = df[questions].agg(['mean', 'median', 'std', 'min', 'max']).T
                question_stats_df.columns = ['Moyenne', 'Médiane', 'Écart-type', 'Min', 'Max']

                question_stats_df["% de 1"] = df[questions].apply(lambda x: (x == 1).sum() / len(x) * 100).values
                question_stats_df["% de 5"] = df[questions].apply(lambda x: (x == 5).sum() / len(x) * 100).values

                question_stats_df = question_stats_df.round(2)
                st.dataframe(question_stats_df)
                st.markdown("</div>", unsafe_allow_html=True)

            # Scores individuels
            st.markdown("<div class='section-card results-section'>", unsafe_allow_html=True)
            st.markdown(f"### Scores individuels : {len(df)} sujets")
            st.markdown("Examinez les scores détaillés pour repérer rapidement les expériences positives ou critiques.")
            st.dataframe(df[['Sujet', 'SUS_Score']] if 'Sujet' in df.columns else df[['SUS_Score']])
            st.markdown("</div>", unsafe_allow_html=True)
            # PDF            
            def generate_sus_pdf(avg_score, num_subjects, df, zones, questions, category_info=None, stats_df=None):
                pdf = FPDF()
                pdf.set_auto_page_break(auto=True, margin=12)
                pdf.add_page()
            
                # Titre
                pdf.set_font("Arial", "B", 14)
                pdf.cell(0, 7, "Rapport - Questionnaire SUS", ln=True, align='C')
                pdf.ln(3)
            
                # Informations générales
                pdf.set_font("Arial", "", 9)
                pdf.ln(10)  # saute 10 unités de hauteur (≈ 1 ligne)
                pdf.cell(0, 5, f"Date : {date.today().strftime('%Y-%m-%d')}", ln=True)
                pdf.cell(0, 5, f"Nombre de répondants : {num_subjects}", ln=True)
                pdf.cell(0, 5, f"Score SUS moyen : {avg_score:.1f} / 100", ln=True)
                pdf.cell(0, 5, f"Score minimum : {df['SUS_Score'].min()}", ln=True)
                pdf.cell(0, 5, f"Score maximum : {df['SUS_Score'].max()}", ln=True)
                pdf.cell(0, 5, f"Ecart-type : {df['SUS_Score'].std():.2f}", ln=True)
                pdf.cell(0, 5, f"Mediane : {df['SUS_Score'].median():.1f}", ln=True)
                pdf.cell(0, 5, f"1er quartile (Q1) : {q1:.1f}", ln=True)
                pdf.cell(0, 5, f"3e quartile (Q3) : {q3:.1f}", ln=True)
                pdf.cell(0, 5, f"IQR : {iqr:.1f}", ln=True)
                pdf.ln(3)
            
                def add_figure_inline(fig, title, width=160):
                    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmpfile:
                        fig.savefig(tmpfile.name, format='png', bbox_inches='tight', dpi=200)
                        pdf.set_font("Arial", "B", 11)
                        pdf.cell(0, 6, title, ln=True)
                        pdf.ln(2)
                        x = (pdf.w - width) / 2
                        pdf.image(tmpfile.name, x=x, w=width)
                        pdf.ln(4)
                #tableau des stats par question
                def add_stats_table(pdf, df_stats, title):
                    pdf.set_font("Arial", "B", 11)
                    pdf.cell(0, 6, title, ln=True)
                    pdf.ln(1)
            
                    index_col_width = 40
                    col_width = 20
                    row_height = 5
            
                    pdf.set_fill_color(220, 220, 220)
                    pdf.set_font("Arial", "B", 9)
                    pdf.cell(index_col_width, row_height, "", border=1, align="C", fill=True)
                    for col in df_stats.columns:
                        pdf.cell(col_width, row_height, str(col), border=1, align="C", fill=True)
                    pdf.ln()
            
                    pdf.set_font("Arial", "", 9)
                    for idx, row in df_stats.iterrows():
                        pdf.cell(index_col_width, row_height, str(idx), border=1)
                        for val in row:
                            pdf.cell(col_width, row_height, str(val), border=1)
                        pdf.ln()
            
                    pdf.ln(4)
            
                # Figures
                fig_jauge = create_gauge(avg_score, zones, mode="white")
                bins = [0, 25, 39, 52, 73, 86, 100]
                labels = [z[3] for z in zones]
                colors = [z[2] for z in zones]
                categories = pd.cut(df['SUS_Score'], bins=bins, labels=labels, include_lowest=True, right=True)
                distribution = categories.value_counts().sort_index()
                fig_dist = create_distribution(distribution, colors, mode="white")
                fig_radar = create_radar_chart(df, questions, mode="white")
            
                fig_cat = None
                if category_info:
                    first_category = list(category_info.keys())[0]
                    if category_info[first_category] == "Numérique":
                        try:
                            binned = pd.cut(df[first_category], bins=5)
                            df["_cat_display"] = binned.astype(str)
                        except:
                            df["_cat_display"] = df[first_category].astype(str)
                    else:
                        df["_cat_display"] = df[first_category].astype(str)
            
                    group_means = df.groupby("_cat_display", sort=True)["SUS_Score"].mean().sort_index()
                    fig_cat = create_category_chart(group_means, mode="white")
                    df.drop(columns=["_cat_display"], inplace=True, errors="ignore")
            
                # Ajout des éléments au PDF
                pdf.ln(10)  # saute 10 unités de hauteur (≈ 1 ligne)
                add_figure_inline(fig_jauge, "Évaluation globale (jauge)")  
                pdf.ln(10)  # saute 10 unités de hauteur (≈ 1 ligne)
                add_figure_inline(fig_dist, "Répartition des scores")

                pdf.add_page()
                if fig_cat:
                    pdf.ln(10)  # saute 10 unités de hauteur (≈ 1 ligne)
                    add_figure_inline(fig_cat, "Score SUS par catégorie")
                pdf.ln(10)  # saute 10 unités de hauteur (≈ 1 ligne)
                add_figure_inline(fig_radar, "Analyse moyenne par question (radar)")
                pdf.add_page()
                pdf.ln(10)  # saute 10 unités de hauteur (≈ 1 ligne)
                if stats_df is not None:
                    add_stats_table(pdf, stats_df, "Statistiques par question")
            
                try:
                    return pdf.output(dest='S').encode('latin1')
                except UnicodeEncodeError:
                    return None


            # Appel depuis Streamlit
            if st.button("📄 Générer le rapport PDF"):
                pdf_bytes = generate_sus_pdf(
                    avg_score=avg_score,
                    num_subjects=len(df),
                    df=df,
                    zones=zones,
                    questions=questions,
                    category_info=category_info if 'category_info' in locals() else None,
                    stats_df=question_stats_df if 'question_stats_df' in locals() else None
                )
            
                st.download_button(
                    label="📥 Télécharger le rapport PDF",
                    data=pdf_bytes,
                    file_name="rapport_sus.pdf",
                    mime="application/pdf"
                )


    except Exception as e:
        st.error(f"Une erreur est survenue : {str(e)}")
# Logo
logo = Image.open("Logo.png")
st.sidebar.image(logo, width=80)
