import streamlit as st
from PIL import Image
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from fpdf import FPDF
from datetime import date
import tempfile

#Paramètres des couleurs

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
st.sidebar.title(labels[lang]["sidebar_title"])

# Choix de la langue
lang = st.sidebar.selectbox(
    labels[lang]["sidebar_language"],
    options=["Français", "English"],
    index=0
)
# Dictionnaire de traduction complet
labels = {
    "Français": {
        "zones_labels": ["Pire imaginable", "Mauvais", "Acceptable", "Bon", "Excellent", "Meilleur imaginable"],
        "stats_labels": [
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
        "title": "📊 Analyse de questionnaire SUS",
        "upload_prompt": "Chargez un fichier **Excel (.xlsx)** contenant une ligne d'en-tête avec les colonnes **Question1** à **Question10**.",
        "upload_label": "Charger le fichier Excel",
        "filters": "### Filtres",
        "questions": "📋 Questions du questionnaire",
        "score": "#### Score SUS :",
        "distribution": "#### Répartition des sujets par résultat",
        "by_category": "#### Score SUS par catégorie",
        "by_question": "#### Score SUS par question",
        "statistics": "#### Statistiques",
        "individual_scores": "#### Scores individuels",
        "download_pdf": "📄 Télécharger le rapport PDF",
        "download_template": "⬇️ Template Excel (SUS)",
        "template_intro": "Template Excel des résultats à charger dans cette application disponible ici :",
        "select_category": "Choisissez une catégorie :",
        "error_columns": "❌ Le fichier doit contenir les colonnes 'Question1' à 'Question10'.",
        "subjects_count": "sujets",
        "sidebar_title": "Paramètres",
        "sidebar_language": "Langue",
        "sidebar_questionnaire": labels[lang]["sidebar_questionnaire"],
        "questionnaire_choices": labels[lang]["questionnaire_choices"]
    },
    "English": {
        "zones_labels": ["Worst imaginable", "Poor", "Acceptable", "Good", "Excellent", "Best imaginable"],
        "stats_labels": [
            "Average SUS score",
            "Sample size",
            "Minimum score",
            "Maximum score",
            "Standard deviation",
            "Median",
            "1st quartile (Q1)",
            "3rd quartile (Q3)",
            "IQR"
        ],
        "title": "📊 SUS Questionnaire Analysis",
        "upload_prompt": "Upload an **Excel (.xlsx)** file with a header row containing **Question1** to **Question10**.",
        "upload_label": "Upload Excel file",
        "filters": "### Filters",
        "questions": "📋 Questionnaire questions",
        "score": "#### SUS Score:",
        "distribution": "#### Distribution of subjects by score",
        "by_category": "#### SUS score by category",
        "by_question": "#### SUS score per question",
        "statistics": "#### Statistics",
        "individual_scores": "#### Individual scores",
        "download_pdf": "📄 Download PDF report",
        "download_template": "⬇️ Excel Template (SUS)",
        "template_intro": "Excel template for results to upload into this application:",
        "select_category": "Select a category:",
        "error_columns": "❌ File must include columns 'Question1' to 'Question10'.",
        "subjects_count": "subjects",
        "sidebar_title": "Settings",
        "sidebar_language": labels[lang]["sidebar_language"],
        "sidebar_questionnaire": "Questionnaire type",
        "questionnaire_choices": ["SUS", "Other (coming soon)"]
    }
}

# Définition dynamique des zones
zone_colors = ["#d9534f", "#f0ad4e", "#f7ec13", "#5bc0de", "#5cb85c", "#3c763d"]
zones = [
    (0, 25, zone_colors[0], labels[lang]["zones_labels"][0]),
    (25, 39, zone_colors[1], labels[lang]["zones_labels"][1]),
    (39, 52, zone_colors[2], labels[lang]["zones_labels"][2]),
    (52, 73, zone_colors[3], labels[lang]["zones_labels"][3]),
    (73, 86, zone_colors[4], labels[lang]["zones_labels"][4]),
    (86, 100, zone_colors[5], labels[lang]["zones_labels"][5])
]


# Choix du questionnaire
questionnaire_type = st.sidebar.radio(
    labels[lang]["sidebar_questionnaire"],
    labels[lang]["questionnaire_choices"]
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

st.title(labels[lang]["title"])
st.markdown(labels[lang]["upload_prompt"])

uploaded_file = st.file_uploader(labels[lang]["upload_label"], type=["xlsx"])

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
            st.error(labels[lang]["error_columns"])
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
            with st.sidebar.expander(labels[lang]["questions"]):
                for i, q in enumerate(questions, 1):
                    st.markdown(f"**Q{i}** : {sus_questions[q][lang]}")


            # Jauge
            st.markdown(f"{labels[lang]['score']} {avg_score:.1f}")
            
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

            
             # Statistiques descriptives
            q1 = df['SUS_Score'].quantile(0.25)
            q3 = df['SUS_Score'].quantile(0.75)
            iqr = q3 - q1
            
            stats_df = pd.DataFrame({
                "Indicateur": labels[lang]["stats_labels"],
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
            
            st.markdown(labels[lang]["statistics"])
            st.table(stats_df)

            avg_score = df['SUS_Score'].mean()

            st.markdown("---")

            # Histogramme
            st.markdown(labels[lang]["distribution"])
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

            # Histogramme des scores SUS par catégorie
            if category_info:
                st.markdown(labels[lang]["by_category"])
            
                if len(category_info) > 1:
                    selected_category = st.selectbox(labels[lang]["select_category"], list(category_info.keys()))
                else:
                    selected_category = list(category_info.keys())[0]
            
                if selected_category:
                    if category_info[selected_category] == "Numérique":
                        try:
                            binned = pd.cut(df[selected_category], bins=5)
                            df["_cat_display"] = binned.astype(str)
                        except Exception as e:
                            st.warning(f"Erreur lors du regroupement par tranches : {e}")
                            df["_cat_display"] = df[selected_category].astype(str)
                    else:
                        df["_cat_display"] = df[selected_category].astype(str)
            
                    # Calcul de la moyenne SUS par groupe
                    group_means = df.groupby("_cat_display", sort=True)["SUS_Score"].mean().sort_index()

                    # Tri croissant par libellé de catégorie
                    #group_means = group_means.sort_index()
            
                    fig_cat, ax_cat = plt.subplots(figsize=(6, 3))
                    fig_cat.patch.set_alpha(0)
                    ax_cat.set_facecolor("none")
            
                    bars = ax_cat.bar(group_means.index, group_means.values, color="#5bc0de")
                    ax_cat.set_ylabel("Score SUS moyen")
            
                    for bar in bars:
                        height = bar.get_height()
                        ax_cat.text(
                            bar.get_x() + bar.get_width() / 2,
                            height + 0.5,
                            f"{height:.1f}",
                            ha='center',
                            fontsize=9,
                            color='white'
                        )
            
                    ax_cat.set_ylim(0, min(100, max(group_means.values) + 10))
                    ax_cat.tick_params(axis='x', rotation=30, colors='white')
                    ax_cat.spines['top'].set_visible(False)
                    ax_cat.spines['right'].set_visible(False)
                    ax_cat.spines['left'].set_color('white')
                    ax_cat.spines['bottom'].set_color('white')
                    ax_cat.yaxis.label.set_color('white')
                    ax_cat.tick_params(axis='y', colors='white')
            
                    fig_cat.tight_layout()
                    st.pyplot(fig_cat)
            
                    # Nettoyage de colonne temporaire
                    df.drop(columns=["_cat_display"], inplace=True, errors="ignore")


            st.markdown("---")

            # Radar - Score SUS par question
            st.markdown(labels[lang]["by_question"])
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
            ax.set_theta_direction(-1)
            
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
            st.markdown(f"{labels[lang]['individual_scores']} : {len(df)} {labels[lang]['subjects_count']}")
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
                label=labels[lang]["download_pdf"],
                data=pdf_bytes,
                file_name="rapport_sus.pdf",
                mime="application/pdf"
            )

    except Exception as e:
        st.error(f"Une erreur est survenue : {str(e)}")

st.markdown("---")
st.markdown(labels[lang]["template_intro"])

with open("template_sus.xlsx", "rb") as f:
    template_bytes = f.read()

st.download_button(
    label=labels[lang]["download_template"],
    data=template_bytes,
    file_name="template_sus.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

# Logo bas de page
logo = Image.open("Logo.png")
st.image(logo, width=80)
