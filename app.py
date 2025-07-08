import streamlit as st
from PIL import Image
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from fpdf import FPDF
from datetime import date
import tempfile

st.set_page_config(page_title="AlterUX - Analyse SUS", layout="centered")

st.title("Analyse de questionnaire SUS")
st.markdown("Chargez un fichier **Excel (.xlsx)** contenant une ligne d'en-tête avec les colonnes **Question1** à **Question10**.")

uploaded_file = st.file_uploader("Charger le fichier Excel", type=["xlsx"])

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file, sheet_name=0)
        st.write("Aperçu des données :", df.head())

        questions = [f"Question{i}" for i in range(1, 11)]
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

            st.subheader(f"Scores individuels : {len(df)} sujets")
            st.dataframe(df[['Sujet', 'SUS_Score']] if 'Sujet' in df.columns else df[['SUS_Score']])

            avg_score = df['SUS_Score'].mean()
            st.subheader(f"Score SUS moyen : **{avg_score:.1f} / 100**")

            zone_colors = ["#d9534f", "#f0ad4e", "#f7ec13", "#5bc0de", "#5cb85c", "#3c763d"]
            zones = [
                (0, 25, zone_colors[0], "Pire imaginable"),
                (25, 39, zone_colors[1], "Mauvais"),
                (39, 52, zone_colors[2], "Acceptable"),
                (52, 73, zone_colors[3], "Bon"),
                (73, 86, zone_colors[4], "Excellent"),
                (86, 100, zone_colors[5], "Meilleur imaginable")
            ]

            # Jauge
            fig, ax = plt.subplots(figsize=(6, 1.5))
            for start, end, color, label in zones:
                ax.barh(0, width=end - start, left=start, color=color, edgecolor='white', height=0.5)
            ax.plot(avg_score, 0, marker='v', color='red', markersize=12)
            ax.text(avg_score, -0.3, f"{avg_score:.1f}", ha='center', fontsize=12,
                    bbox=dict(facecolor='white', edgecolor='red', boxstyle='round,pad=0.2'))
            for start, end, color, label in zones:
                center = (start + end) / 2
                ax.text(center, 0.35, label, ha='center', fontsize=9, color='black',
                        bbox=dict(facecolor='white', alpha=0.8, edgecolor='none', boxstyle='round,pad=0.2'))
            for start, end, _, _ in zones:
                ax.text(start, -0.6, f"{start}", ha='center', va='top', fontsize=8, color='gray')
            ax.text(100, -0.6, "100", ha='center', va='top', fontsize=8, color='gray')
            ax.set_xlim(0, 100)
            ax.set_ylim(-0.7, 0.8)
            ax.axis('off')
            fig.tight_layout()
            st.pyplot(fig, use_container_width=False)

            # Histogramme
            st.subheader("Répartition des sujets par catégorie")
            bins = [0, 25, 39, 52, 73, 86, 100]
            labels = [z[3] for z in zones]
            colors = [z[2] for z in zones]
            categories = pd.cut(df['SUS_Score'], bins=bins, labels=labels, include_lowest=True, right=True)
            distribution = categories.value_counts().sort_index()
            fig_dist, ax_dist = plt.subplots(figsize=(6, 3))
            bars = ax_dist.bar(distribution.index, distribution.values, color=colors)
            for bar in bars:
                height = bar.get_height()
                ax_dist.text(bar.get_x() + bar.get_width()/2, height + 0.2, int(height), ha='center', fontsize=10)
            ax_dist.set_xlabel("Catégories de score")
            ax_dist.set_ylim(0, max(distribution.values) + 2)
            ax_dist.get_yaxis().set_visible(False)
            for spine in ['top', 'right', 'left']:
                ax_dist.spines[spine].set_visible(False)
            fig_dist.tight_layout()
            st.pyplot(fig_dist, use_container_width=False)

            # Radar
            st.subheader("Moyenne par question")
            question_means = df[questions].mean()
            radar_labels = questions
            values = question_means.tolist() + [question_means.tolist()[0]]
            angles = np.linspace(0, 2 * np.pi, len(radar_labels), endpoint=False).tolist() + [0]
            fig_radar, ax = plt.subplots(figsize=(3, 3), subplot_kw=dict(polar=True))
            ax.plot(angles, values, color='b', linewidth=1)
            ax.fill(angles, values, color='b', alpha=0.25)
            ax.set_xticks(angles[:-1])
            ax.set_xticklabels(radar_labels,fontsize=4)
            ax.set_yticks([1, 2, 3, 4, 5])
            ax.set_ylim(1, 5)
            fig_radar.tight_layout()
            st.pyplot(fig_radar, use_container_width=False)

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
