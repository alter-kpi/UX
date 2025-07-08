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
                    score += val - 1 if i % 2 == 0 else 5 - val
                return score * 2.5

            df['SUS_Score'] = df_sus.apply(calculate_sus, axis=1)
            avg_score = df['SUS_Score'].mean()
            categories = [
                (0, 25, "#d9534f", "Pire imaginable"),
                (25, 39, "#f0ad4e", "Mauvais"),
                (39, 52, "#f7ec13", "Acceptable"),
                (52, 73, "#5bc0de", "Bon"),
                (73, 86, "#5cb85c", "Excellent"),
                (86, 100, "#3c763d", "Meilleur imaginable")
            ]
            labels = [z[3] for z in categories]
            colors = [z[2] for z in categories]

            # Container - Tableau des scores
            st.    
            with st.container():
                st.write(f"🧮 Scores individuels : {len(df)} sujets")
                st.dataframe(df[['Sujet', 'SUS_Score']] if 'Sujet' in df.columns else df[['SUS_Score']])

            # Container - Score moyen et jauge
            with st.container():
                st.subheader(f"📈 Score SUS moyen : **{avg_score:.1f} / 100**")
                fig_jauge, ax = plt.subplots(figsize=(6, 1.5))
                for start, end, color, label in categories:
                    ax.barh(0, width=end - start, left=start, color=color, edgecolor='white', height=0.5)
                ax.plot(avg_score, 0, marker='v', color='red', markersize=12)
                ax.text(avg_score, -0.3, f"{avg_score:.1f}", ha='center', fontsize=12,
                        bbox=dict(facecolor='white', edgecolor='red', boxstyle='round,pad=0.2'))
                for start, end, color, label in categories:
                    ax.text((start + end)/2, 0.35, label, ha='center', fontsize=9, color='black',
                            bbox=dict(facecolor='white', alpha=0.8, edgecolor='none', boxstyle='round,pad=0.2'))
                for start, end, _, _ in categories:
                    ax.text(start, -0.6, f"{start}", ha='center', fontsize=8, color='gray')
                ax.text(100, -0.6, "100", ha='center', fontsize=8, color='gray')
                ax.set_xlim(0, 100)
                ax.set_ylim(-0.7, 0.8)
                ax.axis('off')
                fig_jauge.tight_layout()
                st.pyplot(fig_jauge, use_container_width=False)

            # Container - Histogramme et Boxplot côte à côte
            with st.container():
                col1, col2 = st.columns(2)

                with col1:
                    st.subheader("📊 Répartition des sujets")
                    bins = [z[0] for z in categories] + [100]
                    distrib = pd.cut(df['SUS_Score'], bins=bins, labels=labels, include_lowest=True)
                    counts = distrib.value_counts().sort_index()
                    fig_dist, ax_dist = plt.subplots(figsize=(5, 3))
                    bars = ax_dist.bar(counts.index, counts.values, color=colors)
                    for bar in bars:
                        ax_dist.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.2, int(bar.get_height()), ha='center')
                    ax_dist.set_title("Par catégorie", fontsize=11)
                    ax_dist.set_xlabel("Catégories")
                    ax_dist.get_yaxis().set_visible(False)
                    for spine in ['top', 'right', 'left']:
                        ax_dist.spines[spine].set_visible(False)
                    fig_dist.tight_layout()
                    st.pyplot(fig_dist, use_container_width=False)

                with col2:
                    st.subheader("📦 Distribution")
                    fig_box, ax_box = plt.subplots(figsize=(2.5, 3.5))
                    ax_box.boxplot(df["SUS_Score"], vert=True, patch_artist=True,
                                   boxprops=dict(facecolor="#5bc0de"))
                    ax_box.set_title("Scores SUS", fontsize=11)
                    ax_box.set_ylabel("Score SUS", fontsize=9)
                    ax_box.set_xticks([1])
                    ax_box.set_xticklabels([""])
                    fig_box.tight_layout()
                    st.pyplot(fig_box, use_container_width=False)

            # Container - Radar
            with st.container():
                st.subheader("📍 Moyenne par question")
                question_means = df[questions].mean()
                values = question_means.tolist() + [question_means.tolist()[0]]
                angles = np.linspace(0, 2 * np.pi, len(questions), endpoint=False).tolist() + [0]
                fig_radar, ax = plt.subplots(figsize=(5, 5), subplot_kw=dict(polar=True))
                ax.plot(angles, values, color='b', linewidth=2)
                ax.fill(angles, values, color='b', alpha=0.25)
                ax.set_xticks(angles[:-1])
                ax.set_xticklabels(questions)
                ax.set_yticks([1, 2, 3, 4, 5])
                ax.set_ylim(1, 5)
                ax.set_title("Moyenne des réponses (1 à 5)", y=1.1)
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

                for title, fig in [("Jauge", fig_jauge), ("Histogramme", fig_dist), ("Radar", fig_radar)]:
                    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                        fig.savefig(tmp.name, format='png', bbox_inches='tight')
                        pdf.set_font("Arial", "B", 12)
                        pdf.cell(0, 10, title, ln=True)
                        image_width = 120
                        x_center = (pdf.w - pdf.l_margin - pdf.r_margin - image_width) / 2 + pdf.l_margin
                        pdf.image(tmp.name, x=x_center, w=image_width)
                        pdf.ln(5)

                return pdf.output(dest='S').encode('latin1')

            pdf_bytes = generate_pdf(avg_score, fig_jauge, fig_dist, fig_radar, len(df))
            st.download_button(
                label="📄 Télécharger le rapport PDF",
                data=pdf_bytes,
                file_name="rapport_sus.pdf",
                mime="application/pdf"
            )

    except Exception as e:
        st.error(f"Une erreur est survenue : {str(e)}")

# --- Footer ---
st.markdown("---")
st.markdown("Template Excel des résultats à charger dans cette application disponible ici :")
with open("template_sus.xlsx", "rb") as f:
    st.download_button("⬇️ Template Excel (SUS)", data=f.read(), file_name="template_sus.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# Logo en bas
st.image(Image.open("Logo.png"), width=80)
