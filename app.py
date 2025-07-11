import streamlit as st
from PIL import Image
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from fpdf import FPDF
from datetime import date
import tempfile

# Menu latéral
st.sidebar.title("Paramètres")

# Choix de la langue
lang = st.sidebar.selectbox(
    "Language",
    options=["Français", "English"],
    index=0
)

# Choix du questionnaire
questionnaire_type = st.sidebar.radio(
    "Type de questionnaire",
    ["SUS", "Autre (à venir)"]
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


st.set_page_config(page_title="AlterUX - Analyse SUS", layout="centered")

st.title("📊 Analyse de questionnaire SUS")
st.markdown("Chargez un fichier **Excel (.xlsx)** contenant une ligne d'en-tête avec les colonnes **Question1** à **Question10**.")

uploaded_file = st.file_uploader("Charger le fichier Excel", type=["xlsx"])

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file, sheet_name=0)

        # Colonnes de questions
        questions = [f"Question{i}" for i in range(1, 11)]

        # Colonnes personnalisables définies dans le template
        potential_custom_columns = ["Category 1", "Category 2", "Category 3", "Category 4"]

        # Conserver uniquement celles qui existent et qui ne sont pas vides
        custom_columns = [col for col in potential_custom_columns if col in df.columns and df[col].notna().any()]

        # Identifier le type : numérique ou texte
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

            # Choix des catégories (sidebar)

            with st.sidebar:
                st.markdown("### Filtres")
                filtered_df = df.copy()  # base de travail pour les filtres
            
                for col in custom_columns:
                    if category_info[col] == "Texte":
                        options = df[col].dropna().unique().tolist()
                        selected = st.multiselect(f"{col} :", options, default=options)
                        filtered_df = filtered_df[filtered_df[col].isin(selected)]
                    else:  # numérique
                        min_val = float(df[col].min())
                        max_val = float(df[col].max())
                        selected_range = st.slider(f"{col} :", min_val, max_val, (min_val, max_val))
                        filtered_df = filtered_df[(df[col] >= selected_range[0]) & (df[col] <= selected_range[1])]

            # Légende des questions
            st.markdown("##### Questions")
            
            legend_df = pd.DataFrame({
                lang: [sus_questions[q][lang] for q in questions]
            })
            
            legend_df.index = range(1, len(legend_df) + 1)
            st.table(legend_df)

            # Jauge
            st.markdown(f"#### Score SUS : {avg_score:.1f}")
            
            fig, ax = plt.subplots(figsize=(6, 1.5))
            fig.patch.set_alpha(0)         # fond transparent
            ax.set_facecolor("none")       # fond transparent
            
            for start, end, color, label in zones:
                ax.barh(0, width=end - start, left=start, color=color, edgecolor='white', height=0.5)
            
            ax.plot(avg_score, 0, marker='v', color='red', markersize=12)
            ax.text(avg_score, -0.3, f"{avg_score:.1f}", ha='center', fontsize=12,
                    bbox=dict(facecolor='white', edgecolor='red', boxstyle='round,pad=0.2', alpha=0.9))
            
            for start, end, color, label in zones:
                center = (start + end) / 2
                ax.text(center, 0.35, label, ha='center', fontsize=9, color='white',
                        bbox=dict(facecolor='black', alpha=0.6, edgecolor='none', boxstyle='round,pad=0.2'),rotation=30)
            
            for start, end, _, _ in zones:
                ax.text(start, -0.6, f"{start}", ha='center', va='top', fontsize=8, color='gray')
            ax.text(100, -0.6, "100", ha='center', va='top', fontsize=8, color='gray')
            
            ax.set_xlim(0, 100)
            ax.set_ylim(-0.7, 0.8)
            ax.axis('off')
            fig.tight_layout()
            
            st.pyplot(fig, use_container_width=False)

            st.markdown("---")
            
             # Statistiques descriptives
            q1 = df['SUS_Score'].quantile(0.25)
            q3 = df['SUS_Score'].quantile(0.75)
            iqr = q3 - q1
            
            stats_df = pd.DataFrame({
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
                    len(df),
                    df["SUS_Score"].min(),
                    df["SUS_Score"].max(),
                    f"{df['SUS_Score'].std():.2f}",
                    f"{df['SUS_Score'].median():.1f}",
                    f"{q1:.1f}",
                    f"{q3:.1f}",
                    f"{iqr:.1f}"
                ]
            })
            stats_df.index = range(1, len(stats_df) + 1)
            
            st.markdown("---")
            
            st.markdown("#### Statistiques")
            st.table(stats_df)

            avg_score = df['SUS_Score'].mean()
            zone_colors = ["#d9534f", "#f0ad4e", "#f7ec13", "#5bc0de", "#5cb85c", "#3c763d"]
            zones = [
                (0, 25, zone_colors[0], "Pire imaginable"),
                (25, 39, zone_colors[1], "Mauvais"),
                (39, 52, zone_colors[2], "Acceptable"),
                (52, 73, zone_colors[3], "Bon"),
                (73, 86, zone_colors[4], "Excellent"),
                (86, 100, zone_colors[5], "Meilleur imaginable")
            ]

            st.markdown("---")

            # Histogramme ---
            st.markdown("#### Répartition des sujets par catégorie")
            bins = [0, 25, 39, 52, 73, 86, 100]
            labels = [z[3] for z in zones]
            colors = [z[2] for z in zones]
            categories = pd.cut(df['SUS_Score'], bins=bins, labels=labels, include_lowest=True, right=True)
            distribution = categories.value_counts().sort_index()
            
            fig_dist, ax_dist = plt.subplots(figsize=(6, 3))
            fig_dist.patch.set_alpha(0)           # fond transparent
            ax_dist.set_facecolor("none")         # fond transparent
            
            bars = ax_dist.bar(distribution.index, distribution.values, color=colors)
            
            for bar in bars:
                height = bar.get_height()
                ax_dist.text(
                    bar.get_x() + bar.get_width() / 2,
                    height + 0.2,
                    int(height),
                    ha='center',
                    fontsize=10,
                    color='white'
                )
            
            ax_dist.set_ylim(0, max(distribution.values) + 2)
            ax_dist.get_yaxis().set_visible(False)
            
            for spine in ['top', 'right', 'left']:
                ax_dist.spines[spine].set_visible(False)
            
            ax_dist.spines['bottom'].set_color('white')
            ax_dist.tick_params(axis='x', colors='white')
            
            plt.xticks(rotation=30)
            
            fig_dist.tight_layout()
            st.pyplot(fig_dist, use_container_width=False)

            st.markdown("---")

            # Radar - Score SUS par question
            st.markdown("#### Score SUS par question")
            question_means = df[questions].mean()
                       
            radar_labels = [f"Q{i}" for i in range(1, 11)]
            values = question_means.tolist() + [question_means.tolist()[0]]
            angles = np.linspace(0, 2 * np.pi, len(radar_labels), endpoint=False).tolist() + [0]
            
            fig_radar, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
            fig_radar.patch.set_alpha(0)
            ax.set_facecolor("none")
            
            ax.plot(angles, values, color='cyan', linewidth=1)
            ax.fill(angles, values, color='cyan', alpha=0.25)
            
            ax.set_xticks(angles[:-1])
            ax.set_xticklabels(radar_labels, fontsize=8, color='white')
            
            ax.set_yticks([1, 2, 3, 4, 5])
            ax.set_yticklabels(["1", "2", "3", "4", "5"], fontsize=6, color='white')
            ax.set_ylim(1, 5)
            
            ax.tick_params(colors='white')
            ax.spines['polar'].set_color('white')
            
            fig_radar.tight_layout()
            st.pyplot(fig_radar, use_container_width=False)


             # Statistiques par question
            with st.container():
            
                stats_df = df[questions].agg(['mean', 'median', 'std', 'min', 'max']).T
                stats_df.columns = ['Moyenne', 'Médiane', 'Écart-type', 'Min', 'Max']
            
                stats_df["% de 1"] = df[questions].apply(lambda x: (x == 1).sum() / len(x) * 100).values
                stats_df["% de 5"] = df[questions].apply(lambda x: (x == 5).sum() / len(x) * 100).values
            
                stats_df = stats_df.round(2)
                st.dataframe(stats_df)
                 
            st.markdown("---")         

            # Scores individuels
            st.markdown(f"#### Scores individuels : {len(df)} sujets")
            st.dataframe(df[['Sujet', 'SUS_Score']] if 'Sujet' in df.columns else df[['SUS_Score']])

            # PDF
            def generate_pdf(avg_score, fig_jauge, fig_dist, fig_radar, num_subjects):
                pdf = FPDF()
                pdf.add_page()
                try:
                    pdf.image("Logo.png", x=10, y=8, w=20)
                except RuntimeError:
                    pass
                pdf.ln(20)
                pdf.set_font("Arial", "B", 16)
                pdf.cell(0, 10, "Rapport - Questionnaire SUS", ln=True, align='C')
                pdf.set_font("Arial", "", 12)
                pdf.cell(0, 10, f"Date : {date.today().strftime('%Y-%m-%d')}", ln=True)
                pdf.cell(0, 10, f"Nombre de sujets : {num_subjects}", ln=True)
                pdf.cell(0, 10, f"Score moyen : {avg_score:.1f} / 100", ln=True)
                pdf.ln(10)

                def add_fig(fig, title, width):
                    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                        fig.savefig(tmp.name, format='png', bbox_inches='tight')
                        pdf.set_font("Arial", "B", 12)
                        pdf.cell(0, 10, title, ln=True)
                        x = (pdf.w - width) / 2
                        pdf.image(tmp.name, x=x, w=width)
                        pdf.ln(5)

                add_fig(fig_jauge, "Jauge", 180)
                add_fig(fig_dist, "Histogramme", 180)
                add_fig(fig_radar, "Radar - Moyenne par question", 120)

                return pdf.output(dest='S').encode('latin1')

            pdf_bytes = generate_pdf(avg_score, fig, fig_dist, fig_radar, len(df))
            st.download_button(
                label="📄 Télécharger le rapport PDF",
                data=pdf_bytes,
                file_name="rapport_sus.pdf",
                mime="application/pdf"
            )

    except Exception as e:
        st.error(f"Une erreur est survenue : {str(e)}")

st.markdown("---")
st.markdown("Template Excel des résultats à charger dans cette application disponible ici :")

with open("template_sus.xlsx", "rb") as f:
    template_bytes = f.read()

st.download_button(
    label="⬇️ Template Excel (SUS)",
    data=template_bytes,
    file_name="template_sus.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

# Logo bas de page
logo = Image.open("Logo.png")
st.image(logo, width=80)
