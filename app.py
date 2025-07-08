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

def calculate_question_stats(df, questions):
    stats = df[questions].agg(['mean', 'median', 'std', 'min', 'max']).T
    stats.columns = ['Moyenne', 'Médiane', 'Écart-type', 'Min', 'Max']
    stats["% de 1"] = df[questions].apply(lambda x: (x == 1).sum() / len(x) * 100).values
    stats["% de 5"] = df[questions].apply(lambda x: (x == 5).sum() / len(x) * 100).values
    return stats.round(2)

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file, sheet_name=0)
        questions = [f"Question{i}" for i in range(1, 11)]

        if not all(col in df.columns for col in questions):
            st.error("❌ Le fichier doit contenir les colonnes 'Question1' à 'Question10'.")
        else:
            df_sus = df[questions]
            def calculate_sus(row):
                return sum([(val - 1) if i % 2 == 0 else (5 - val) for i, val in enumerate(row)]) * 2.5
            df['SUS_Score'] = df_sus.apply(calculate_sus, axis=1)

            avg_score = df['SUS_Score'].mean()
            q1, q3 = df['SUS_Score'].quantile([0.25, 0.75])
            iqr = q3 - q1

            stats_df = pd.DataFrame({
                "Indicateur": ["Score SUS moyen", "Taille de l’échantillon", "Score minimum", "Score maximum", 
                                "Écart-type", "Médiane", "1er quartile (Q1)", "3e quartile (Q3)", "IQR"],
                "Valeur": [f"{avg_score:.1f}", len(df), df["SUS_Score"].min(), df["SUS_Score"].max(),
                           f"{df['SUS_Score'].std():.2f}", f"{df['SUS_Score'].median():.1f}", f"{q1:.1f}", f"{q3:.1f}", f"{iqr:.1f}"]
            })
            st.markdown("---")
            st.markdown("#### Statistiques")
            st.table(stats_df)

            zone_colors = ["#d9534f", "#f0ad4e", "#f7ec13", "#5bc0de", "#5cb85c", "#3c763d"]
            zones = [(0, 25, zone_colors[0], "Pire imaginable"), (25, 39, zone_colors[1], "Mauvais"),
                     (39, 52, zone_colors[2], "Acceptable"), (52, 73, zone_colors[3], "Bon"),
                     (73, 86, zone_colors[4], "Excellent"), (86, 100, zone_colors[5], "Meilleur imaginable")]

            st.markdown("---")
            st.markdown(f"#### Score SUS : {avg_score:.1f}")
            fig, ax = plt.subplots(figsize=(6, 1.5))
            fig.patch.set_alpha(0)
            ax.set_facecolor("none")
            for start, end, color, label in zones:
                ax.barh(0, width=end - start, left=start, color=color, edgecolor='white', height=0.5)
            ax.plot(avg_score, 0, marker='v', color='red', markersize=12)
            ax.text(avg_score, -0.3, f"{avg_score:.1f}", ha='center', fontsize=12,
                    bbox=dict(facecolor='white', edgecolor='red', boxstyle='round,pad=0.2', alpha=0.9))
            for start, end, color, label in zones:
                center = (start + end) / 2
                ax.text(center, 0.35, label, ha='center', fontsize=9, color='white',
                        bbox=dict(facecolor='black', alpha=0.6, edgecolor='none', boxstyle='round,pad=0.2'), rotation=30)
            ax.set_xlim(0, 100)
            ax.set_ylim(-0.7, 0.8)
            ax.axis('off')
            fig.tight_layout()
            st.pyplot(fig, use_container_width=False)

            st.markdown("---")
            st.markdown("#### Répartition des sujets par catégorie")
            bins = [0, 25, 39, 52, 73, 86, 100]
            labels = [z[3] for z in zones]
            colors = [z[2] for z in zones]
            categories = pd.cut(df['SUS_Score'], bins=bins, labels=labels, include_lowest=True, right=True)
            distribution = categories.value_counts().sort_index()
            fig_dist, ax_dist = plt.subplots(figsize=(6, 3))
            fig_dist.patch.set_alpha(0)
            ax_dist.set_facecolor("none")
            bars = ax_dist.bar(distribution.index, distribution.values, color=colors)
            for bar in bars:
                ax_dist.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.2,
                             int(bar.get_height()), ha='center', fontsize=10, color='white')
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
            st.markdown("#### Moyenne par question")
            question_means = df[questions].mean()
            radar_labels = questions
            values = question_means.tolist() + [question_means.tolist()[0]]
            angles = np.linspace(0, 2 * np.pi, len(radar_labels), endpoint=False).tolist() + [0]
            fig_radar, ax = plt.subplots(figsize=(3, 3), subplot_kw=dict(polar=True))
            fig_radar.patch.set_alpha(0)
            ax.set_facecolor("none")
            ax.plot(angles, values, color='cyan', linewidth=1)
            ax.fill(angles, values, color='cyan', alpha=0.25)
            ax.set_xticks(angles[:-1])
            ax.set_xticklabels(radar_labels, fontsize=6, color='white')
            ax.set_yticks([1, 2, 3, 4, 5])
            ax.set_yticklabels(["1", "2", "3", "4", "5"], fontsize=6, color='white')
            ax.set_ylim(1, 5)
            ax.tick_params(colors='white')
            ax.spines['polar'].set_color('white')
            fig_radar.tight_layout()
            st.pyplot(fig_radar, use_container_width=False)

            stats_df_questions = calculate_question_stats(df, questions)
            st.markdown("#### Statistiques par question")
            st.dataframe(stats_df_questions)

            def generate_pdf(avg_score, num_subjects, stats_df, fig_jauge, fig_hist, fig_radar, question_stats_df):
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
                pdf.ln(5)
                pdf.set_font("Arial", "B", 12)
                pdf.cell(0, 10, "Statistiques globales", ln=True)
                pdf.set_font("Arial", "", 10)
                for index, row in stats_df.iterrows():
                    pdf.cell(0, 8, f"{row['Indicateur']} : {row['Valeur']}", ln=True)
                pdf.ln(5)

                def add_fig(fig, title, width):
                    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                        fig.savefig(tmp.name, format='png', bbox_inches='tight', transparent=True)
                        pdf.set_font("Arial", "B", 12)
                        pdf.cell(0, 10, title, ln=True)
                        x = (pdf.w - width) / 2
                        pdf.image(tmp.name, x=x, w=width)
                        pdf.ln(5)

                add_fig(fig_jauge, "Jauge", 180)
                add_fig(fig_hist, "Histogramme", 180)
                add_fig(fig_radar, "Radar - Moyenne par question", 120)

                pdf.add_page()
                pdf.set_font("Arial", "B", 12)
                pdf.cell(0, 10, "Statistiques par question", ln=True)
                pdf.set_font("Arial", "B", 9)
                col_widths = [25, 20, 20, 20, 20, 20, 20]
                for i, col in enumerate(question_stats_df.columns):
                    pdf.cell(col_widths[i], 8, col, border=1, align='C')
                pdf.ln()
                pdf.set_font("Arial", "", 9)
                for idx, row in question_stats_df.iterrows():
                    pdf.cell(col_widths[0], 8, idx, border=1)
                    for i, val in enumerate(row):
                        pdf.cell(col_widths[i+1], 8, str(val), border=1, align='C')
                    pdf.ln()

                return pdf.output(dest='S').encode('latin1')

            pdf_bytes = generate_pdf(avg_score, len(df), stats_df, fig, fig_dist, fig_radar, stats_df_questions)
            st.download_button("📄 Télécharger le rapport PDF", data=pdf_bytes, file_name="rapport_sus.pdf", mime="application/pdf")

    except Exception as e:
        st.error(f"Une erreur est survenue : {str(e)}")

st.markdown("---")
st.markdown("Template Excel des résultats à charger dans cette application disponible ici :")

with open("template_sus.xlsx", "rb") as f:
    st.download_button("⬇️ Template Excel (SUS)", data=f.read(), file_name="template_sus.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

logo = Image.open("Logo.png")
st.image(logo, width=80)
