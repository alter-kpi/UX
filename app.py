import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from fpdf import FPDF
from PIL import Image
from datetime import date
import tempfile

st.set_page_config(page_title="Analyse SUS", layout="centered")

st.title("Analyse de questionnaire SUS")

uploaded_file = st.file_uploader("Charger un fichier Excel (.xlsx)", type="xlsx")

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file)
        questions = [f"Question{i}" for i in range(1, 11)]

        if not all(col in df.columns for col in questions):
            st.error("Le fichier doit contenir les colonnes 'Question1' à 'Question10'.")
        else:
            df_sus = df[questions]

            def calculate_sus(row):
                score = 0
                for i in range(10):
                    score += row[i] - 1 if i % 2 == 0 else 5 - row[i]
                return score * 2.5

            df["SUS_Score"] = df_sus.apply(calculate_sus, axis=1)
            avg_score = df["SUS_Score"].mean()

            # JAUGE
            zone_colors = ["#d9534f", "#f0ad4e", "#f7ec13", "#5bc0de", "#5cb85c", "#3c763d"]
            zones = [(0, 25), (25, 39), (39, 52), (52, 73), (73, 86), (86, 100)]

            fig_jauge, ax = plt.subplots(figsize=(6, 1.5))
            for i, (start, end) in enumerate(zones):
                ax.barh(0, width=end - start, left=start, color=zone_colors[i], edgecolor='white', height=0.5)
            ax.plot(avg_score, 0, marker='v', color='red', markersize=10)
            ax.set_xlim(0, 100)
            ax.axis('off')
            fig_jauge.tight_layout()
            st.pyplot(fig_jauge, use_container_width=False)

            # RADAR
            question_means = df[questions].mean()
            labels = questions
            values = question_means.tolist() + [question_means.tolist()[0]]
            angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist() + [0]

            fig_radar, ax = plt.subplots(figsize=(4.5, 4.5), subplot_kw=dict(polar=True))
            ax.plot(angles, values, color='b', linewidth=2)
            ax.fill(angles, values, color='b', alpha=0.25)
            ax.set_xticks(angles[:-1])
            ax.set_xticklabels(labels)
            ax.set_yticks([1, 2, 3, 4, 5])
            ax.set_ylim(1, 5)
            fig_radar.tight_layout()
            st.pyplot(fig_radar, use_container_width=False)

            # BOXPLOT
            fig_box, ax_box = plt.subplots(figsize=(2, 3.5))
            ax_box.boxplot(df["SUS_Score"], vert=True, patch_artist=True,
                           boxprops=dict(facecolor="#5bc0de"))
            ax_box.set_ylabel("Score SUS", fontsize=9)
            ax_box.tick_params(axis='y', labelsize=8)
            ax_box.set_xticks([])
            fig_box.tight_layout()
            st.pyplot(fig_box, use_container_width=False)

            # PDF
            def generate_pdf():
                pdf = FPDF()
                pdf.add_page()

                try:
                    pdf.image("Logo.png", x=10, y=8, w=20)
                except RuntimeError:
                    pass

                pdf.set_font("Arial", "B", 14)
                pdf.cell(0, 10, "Rapport - Questionnaire SUS", ln=True, align='C')

                pdf.set_font("Arial", "", 12)
                pdf.cell(0, 10, f"Date : {date.today().strftime('%Y-%m-%d')}", ln=True)
                pdf.cell(0, 10, f"Nombre de sujets : {len(df)}", ln=True)
                pdf.cell(0, 10, f"Score moyen : {avg_score:.1f} / 100", ln=True)
                pdf.ln(10)

                # Jauge
                with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f1:
                    fig_jauge.savefig(f1.name, format='png', bbox_inches='tight')
                    pdf.image(f1.name, x=15, w=180)

                # Radar
                with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f2:
                    fig_radar.savefig(f2.name, format='png', bbox_inches='tight')
                    pdf.image(f2.name, x=45, w=120)

                # Boxplot
                with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f3:
                    fig_box.savefig(f3.name, format='png', bbox_inches='tight')
                    pdf.image(f3.name, x=80, w=50)

                return pdf.output(dest="S").encode("latin1")

            pdf_bytes = generate_pdf()
            st.download_button("Télécharger le PDF", data=pdf_bytes, file_name="rapport_sus.pdf", mime="application/pdf")

    except Exception as e:
        st.error(f"Erreur : {e}")

# Logo bas de page
try:
    logo = Image.open("Logo.png")
    st.image(logo, width=60)
except:
    pass
