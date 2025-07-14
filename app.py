import streamlit as st
from PIL import Image
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from fpdf import FPDF
from datetime import date
import tempfile

# Configuration de la page
st.set_page_config(page_title="Analyse SUS", layout="centered")
st.title("📊 Analyse de questionnaires UX")
st.write("Application d'analyse des questionnaires liés à l’expérience utilisateur (UX).")
st.write("Après importation du fichier Excel, les résultats sont traités automatiquement, visualisés sous forme de graphiques, et un rapport PDF peut être généré.")
st.markdown("---")

# Upload du fichier
uploaded_file = st.file_uploader("Charger le fichier Excel", type=["xlsx"])

# Définition des couleurs et zones
zone_colors = ["#d9534f", "#f0ad4e", "#f7ec13", "#5bc0de", "#5cb85c", "#3c763d"]
zones = [
    (0, 25, zone_colors[0], "Pire imaginable"),
    (25, 39, zone_colors[1], "Mauvais"),
    (39, 52, zone_colors[2], "Acceptable"),
    (52, 73, zone_colors[3], "Bon"),
    (73, 86, zone_colors[4], "Excellent"),
    (86, 100, zone_colors[5], "Meilleur imaginable")
]

# Fonction de calcul du score SUS
def calculate_sus(row):
    score = 0
    for i in range(10):
        val = row[i]
        if i % 2 == 0:
            score += val - 1
        else:
            score += 5 - val
    return score * 2.5

# Fonction de génération du PDF
def generate_sus_pdf(avg_score, num_subjects, df, zones, questions, stats_df=None, question_stats_df=None):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=12)
    pdf.add_page()

    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 7, "Rapport - Questionnaire SUS", ln=True, align='C')
    pdf.ln(3)

    pdf.set_font("Arial", "", 9)
    pdf.cell(0, 5, f"Date : {date.today().strftime('%Y-%m-%d')}", ln=True)
    pdf.cell(0, 5, f"Nombre de répondants : {num_subjects}", ln=True)
    pdf.cell(0, 5, f"Score SUS moyen : {avg_score:.1f} / 100", ln=True)
    pdf.ln(3)

    def add_stats_table(pdf, df_stats, title):
        pdf.set_font("Arial", "B", 11)
        pdf.cell(0, 6, title, ln=True, align='C')
        pdf.ln(1)

        index_col_width = 60
        col_width = 40
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

    if stats_df is not None:
        add_stats_table(pdf, stats_df, "Statistiques descriptives globales")

    if question_stats_df is not None:
        add_stats_table(pdf, question_stats_df, "Statistiques par question")

    try:
        return pdf.output(dest='S').encode('latin1', 'replace')
    except Exception:
        return None

# Traitement du fichier
if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file, engine="openpyxl")
        questions = [f"Question{i}" for i in range(1, 11)]
        if not all(col in df.columns for col in questions):
            st.error("Le fichier doit contenir les colonnes 'Question1' à 'Question10'.")
        else:
            df_sus = df[questions]
            df["SUS_Score"] = df_sus.apply(calculate_sus, axis=1)
            avg_score = df["SUS_Score"].mean()

            st.markdown("### Score SUS moyen")
            st.write(f"{avg_score:.1f} / 100")

            st.markdown("### Statistiques descriptives")
            q1 = df["SUS_Score"].quantile(0.25)
            q3 = df["SUS_Score"].quantile(0.75)
            iqr = q3 - q1
            stats_df = pd.DataFrame({
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
            }, index=[
                "Score SUS moyen",
                "Taille de l'échantillon",
                "Score minimum",
                "Score maximum",
                "Écart-type",
                "Médiane",
                "1er quartile (Q1)",
                "3e quartile (Q3)",
                "IQR"
            ])

            st.table(stats_df)

            st.markdown("### Statistiques par question")
            question_stats_df = df[questions].agg(['mean', 'median', 'std', 'min', 'max']).T
            question_stats_df.columns = ['Moyenne', 'Médiane', 'Écart-type', 'Min', 'Max']
            question_stats_df["% de 1"] = df[questions].apply(lambda x: (x == 1).sum() / len(x) * 100).values
            question_stats_df["% de 5"] = df[questions].apply(lambda x: (x == 5).sum() / len(x) * 100).values
            question_stats_df = question_stats_df.round(2)
            st.dataframe(question_stats_df)

            if st.button("📄 Générer le rapport PDF"):
                pdf_bytes = generate_sus_pdf(
                    avg_score=avg_score,
                    num_subjects=len(df),
                    df=df,
                    zones=zones,
                    questions=questions,
                    stats_df=stats_df,
                    question_stats_df=question_stats_df
                )
                if pdf_bytes:
                    st.download_button(
                        label="📥 Télécharger le rapport PDF",
                        data=pdf_bytes,
                        file_name="rapport_sus.pdf",
                        mime="application/pdf"
                    )
                else:
                    st.error("Erreur lors de la génération du PDF.")
    except Exception as e:
        st.error(f"Une erreur est survenue : {str(e)}")
