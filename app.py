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
st.title("📊 Analyse de questionnaires UX")

st.write("Application d'analyse des questionnaires liés à l’expérience utilisateur (UX). ")
st.write("Après importation du fichier Excel, les résultats sont traités automatiquement, visualisés sous forme de graphiques, "
    "et un rapport PDF peut être généré."
)

st.markdown("---")

# Étapes sans emoji, version professionnelle
st.markdown("##### 1️⃣ Préparer le fichier de réponses")
st.write("Utilisez le modèle ci-dessous pour structurer vos données conformément au format attendu.")

with open("template_sus.xlsx", "rb") as f:
    template_bytes = f.read()

st.download_button(
    label="Télécharger le modèle Excel",
    data=template_bytes,
    file_name="template_sus.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

st.markdown("""
##### 2️⃣ Importer le fichier  
Déposez votre fichier Excel complété sur la plateforme.

##### 3️⃣ Analyser les résultats  
Visualisez automatiquement les scores SUS par participant et les résultats agrégés à l’aide de graphiques interactifs.

##### 4️⃣ Exporter le rapport  
Téléchargez un rapport PDF contenant les résultats pour partage ou archivage.
""")

# Chargement du fichier
st.markdown("---")
uploaded_file = st.file_uploader("Charger le fichier Excel", type=["xlsx"])

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

# Logo
logo = Image.open("Logo.png")
st.sidebar.image(logo, width=100)

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
                    st.markdown(f"**Q{i}** : {sus_questions[q]["Français"]}")

            # Jauge
            st.markdown("---")
            st.markdown(f"#### Score SUS : {avg_score:.1f}")
            
            def create_gauge(avg_score, zones, mode="dark"):
                bg_color = "white" if mode == "white" else "black"
                text_color = "black" if mode == "white" else "white"
            
                fig, ax = plt.subplots(figsize=(6, 1.5))
                fig.patch.set_alpha(0)
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
            
            
            fig_jauge = create_gauge(avg_score, zones, mode="dark")
            st.pyplot(fig_jauge)
            
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

            st.markdown("---")

            # Histogramme
            st.markdown("#### Distribution")
            
            def create_distribution(distribution, colors, mode="dark"):
                bg_color = "white" if mode == "white" else "black"
                text_color = "black" if mode == "white" else "white"
            
                fig, ax = plt.subplots(figsize=(6, 3))
                fig.patch.set_alpha(0)
                ax.set_facecolor("none")
            
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
           
            # Calcul de la distribution
            bins = [0, 25, 39, 52, 73, 86, 100]
            labels = [z[3] for z in zones]
            colors = [z[2] for z in zones]
            
            categories = pd.cut(df['SUS_Score'], bins=bins, labels=labels, include_lowest=True, right=True)
            distribution = categories.value_counts().sort_index()
            
            fig_dist = create_distribution(distribution, colors, mode="dark")
            st.pyplot(fig_dist)
            st.markdown("---")

            # Histogramme des scores SUS par catégorie
            
            def create_category_chart(group_means, mode="dark"):
                bg_color = "white" if mode == "white" else "black"
                text_color = "black" if mode == "white" else "white"
            
                fig, ax = plt.subplots(figsize=(6, 3))
                fig.patch.set_alpha(0)
                ax.set_facecolor("none")
            
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
            
            #Affichage dans Streamlit
            if category_info:
                st.markdown("#### Score SUS par catégorie")
            
                # 1. Sélection de la catégorie
                selected_category = st.selectbox("Choisissez une catégorie :", list(category_info.keys()))
            
                # 2. Préparation des groupes
                if category_info[selected_category] == "Numérique":
                    try:
                        binned = pd.cut(df[selected_category], bins=5)
                        df["_cat_display"] = binned.astype(str)
                    except Exception as e:
                        st.warning(f"Erreur lors du regroupement par tranches : {e}")
                        df["_cat_display"] = df[selected_category].astype(str)
                else:
                    df["_cat_display"] = df[selected_category].astype(str)
            
                # 3. Moyennes par groupe
                group_means = df.groupby("_cat_display", sort=True)["SUS_Score"].mean().sort_index()
            
                # 4. Affichage
                fig_cat = create_category_chart(group_means, mode="dark")
                st.pyplot(fig_cat)
            
                # 5. Nettoyage
                df.drop(columns=["_cat_display"], inplace=True, errors="ignore")

            st.markdown("---")

            # Radar - Score SUS par question
            
            def create_radar_chart(df, questions, mode="dark"):
                bg_color = "white" if mode == "white" else "black"
                text_color = "black" if mode == "white" else "white"
            
                question_means = df[questions].mean()
                radar_labels = [f"Q{i}" for i in range(1, 11)]
                values = question_means.tolist() + [question_means.tolist()[0]]
                angles = np.linspace(0, 2 * np.pi, len(radar_labels), endpoint=False).tolist() + [0]
            
                fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
            
                fig.patch.set_alpha(0)
                ax.set_facecolor("none")
          
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

            st.markdown("#### Score SUS par question")
            fig_radar = create_radar_chart(df, questions, mode="dark")
            st.pyplot(fig_radar)


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

            def generate_sus_pdf(avg_score, num_subjects, df, zones, questions, category_info=None):
                pdf = FPDF()
                pdf.set_auto_page_break(auto=True, margin=12)
                pdf.add_page()
            
                # Titre
                pdf.set_font("Arial", "B", 14)
                pdf.cell(0, 7, "Rapport - Questionnaire SUS", ln=True, align='C')
                pdf.ln(3)
            
                # Informations générales
                pdf.set_font("Arial", "", 9)
                pdf.cell(0, 5, f"Date : {date.today().strftime('%Y-%m-%d')}", ln=True)
                pdf.cell(0, 5, f"Nombre de répondants : {num_subjects}", ln=True)
                pdf.cell(0, 5, f"Score SUS moyen : {avg_score:.1f} / 100", ln=True)
                pdf.ln(3)
            
                # Fonction utilitaire pour ajouter une figure
                def add_figure_inline(fig, title, width=160):
                    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmpfile:
                        fig.savefig(tmpfile.name, format='png', bbox_inches='tight', dpi=200)
                        pdf.set_font("Arial", "B", 11)
                        pdf.cell(0, 6, title, ln=True)
                        pdf.ln(2)
                        x = (pdf.w - width) / 2
                        pdf.image(tmpfile.name, x=x, w=width)
                        pdf.ln(4)
            
                # Création des figures pour le PDF (en mode 'white')
                fig_jauge = create_gauge(avg_score, zones, mode="white")
            
                # Répartition des scores
                bins = [0, 25, 39, 52, 73, 86, 100]
                labels = [z[3] for z in zones]
                colors = [z[2] for z in zones]
                categories = pd.cut(df['SUS_Score'], bins=bins, labels=labels, include_lowest=True, right=True)
                distribution = categories.value_counts().sort_index()
                fig_dist = create_distribution(distribution, colors, mode="white")
            
                # Radar
                fig_radar = create_radar_chart(df, questions, mode="white")
            
                # Catégories
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
            
                # Ajout dans le PDF
                add_figure_inline(fig_jauge, "Évaluation globale (jauge)")
                add_figure_inline(fig_dist, "Répartition des scores")
                if fig_cat:
                    add_figure_inline(fig_cat, "Score SUS par catégorie")
                add_figure_inline(fig_radar, "Analyse moyenne par question (radar)")
            
                try:
                    return pdf.output(dest='S').encode('latin1')
                except UnicodeEncodeError:
                    return None



    except Exception as e:
        st.error(f"Une erreur est survenue : {str(e)}")
