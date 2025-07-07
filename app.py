import streamlit as st
from PIL import Image
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from fpdf import FPDF
from datetime import date
import io
import tempfile

st.set_page_config(page_title="AlterUX - Analyse SUS", layout="centered")

# Logo
logo = Image.open("Logo.png")
st.image(logo, width=80)

st.title("Analyse de questionnaire SUS")
st.markdown("Chargez un fichier **Excel (.xlsx)** contenant une ligne d'en-tête avec les colonnes **Question1** à **Question10**.")

with open("template_sus.xlsx", "rb") as f:
    template_bytes = f.read()

st.download_button(
    label="⬇️ Télécharger le modèle Excel (SUS)",
    data=template_bytes,
    file_name="template_sus.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)


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

            st.subheader(f"🧮 Scores individuels : {len(df)} sujets")
            if 'Sujet' in df.columns:
                st.dataframe(df[['Sujet', 'SUS_Score']])
            else:
                st.dataframe(df[['SUS_Score']])

            avg_score = df['SUS_Score'].mean()
            st.subheader(f"📈 Score SUS moyen : **{avg_score:.1f} / 100**")

            # --- Couleurs des zones ---
            zone_colors = [
                "#d9534f",  # Pire
                "#f0ad4e",  # Mauvais
                "#f7ec13",  # Acceptable
                "#5bc0de",  # Bon
                "#5cb85c",  # Excellent
                "#3c763d"   # Meilleur
            ]

            zones = [
                (0, 25, zone_colors[0], "Pire imaginable"),
                (25, 39, zone_colors[1], "Mauvais"),
                (39, 52, zone_colors[2], "Acceptable"),
                (52, 73, zone_colors[3], "Bon"),
                (73, 86, zone_colors[4], "Excellent"),
                (86, 100, zone_colors[5], "Meilleur imaginable")
            ]

            # --- Jauge horizontale ---
            fig, ax = plt.subplots(figsize=(10, 2))
            for start, end, color, label in zones:
                ax.barh(0, width=end - start, left=start, color=color, edgecolor='white', height=0.5)
            
            ax.plot(avg_score, 0, marker='v', color='red', markersize=12)
            ax.text(avg_score, -0.3, f"{avg_score:.1f}", ha='center', fontsize=12,
                    bbox=dict(facecolor='white', edgecolor='red', boxstyle='round,pad=0.2'))
            
            for start, end, color, label in zones:
                center = (start + end) / 2
                ax.text(center, 0.35, label, ha='center', fontsize=9, color='black',
                        bbox=dict(facecolor='white', alpha=0.8, edgecolor='none', boxstyle='round,pad=0.2'))
            
            # Afficher les valeurs de bornes sous la jauge
            for start, end, _, _ in zones:
                ax.text(start, -0.6, f"{start}", ha='center', va='top', fontsize=8, color='gray')
            ax.text(100, -0.6, "100", ha='center', va='top', fontsize=8, color='gray')
            
            ax.set_xlim(0, 100)
            ax.set_ylim(-0.7, 0.8)
            ax.axis('off')
            ax.set_title("Score SUS", fontsize=14, pad=20)
            fig.tight_layout()
            st.pyplot(fig)


            # --- Histogramme de répartition ---
            st.subheader("📊 Répartition des sujets par catégorie")

            bins = [0, 25, 39, 52, 73, 86, 100]
            labels = [z[3] for z in zones]
            colors = [z[2] for z in zones]

            categories = pd.cut(df['SUS_Score'], bins=bins, labels=labels, include_lowest=True, right=True)
            distribution = categories.value_counts().sort_index()

            fig_dist, ax_dist = plt.subplots(figsize=(8, 4))
            bars = ax_dist.bar(distribution.index, distribution.values, color=colors)  # Pas de bord noir
            
            # Ajouter les étiquettes sur les barres
            for bar in bars:
                height = bar.get_height()
                ax_dist.text(bar.get_x() + bar.get_width()/2, height + 0.2, int(height), ha='center', fontsize=10)
            
            # Titres et labels
            ax_dist.set_title("Répartition des sujets par catégorie SUS")
            ax_dist.set_xlabel("Catégories de score")
            ax_dist.set_ylim(0, max(distribution.values) + 2)
            
            # Nettoyage visuel
            ax_dist.get_yaxis().set_visible(False)             # Supprime axe Y
            ax_dist.spines['top'].set_visible(False)
            ax_dist.spines['right'].set_visible(False)
            ax_dist.spines['left'].set_visible(False)
            ax_dist.spines['bottom'].set_visible(True)         # ✅ Affiche uniquement l’axe X
            
            plt.xticks(rotation=20)
            fig_dist.tight_layout()
            st.pyplot(fig_dist)



            # --- PDF : génération via fichiers temporaires ---
            def generate_pdf(avg_score, fig_jauge, fig_dist, num_subjects):
                pdf = FPDF()
                pdf.add_page()
            
                # Logo
                try:
                    pdf.image("Logo.png", x=10, y=8, w=20)
                except RuntimeError:
                    pass
                    
                pdf.ln(20)  # 👈 saute 20 unités pour descendre sous le logo
                
                # Titre (centré)
                pdf.set_font("Arial", "B", 16)
                title = "Rapport - Questionnaire SUS".replace("–", "-")
                pdf.cell(0, 10, title, ln=True, align='C')
            
                # Infos générales (alignées à gauche)
                pdf.set_font("Arial", "", 12)
                pdf.cell(0, 10, f"Date : {date.today().strftime('%Y-%m-%d')}", ln=True)
                pdf.cell(0, 10, f"Nombre de sujets : {num_subjects}", ln=True)
                pdf.cell(0, 10, f"Score moyen : {avg_score:.1f} / 100", ln=True)
                pdf.ln(10)
            
                # Jauge SUS (titre à gauche, image centrée)
                with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f_jauge:
                    fig_jauge.savefig(f_jauge.name, format='png', bbox_inches='tight')
                    pdf.set_font("Arial", "B", 12)
                    pdf.cell(0, 10, "Jauge", ln=True)  # align left
                    pdf.image(f_jauge.name, x=15, w=180)
                    pdf.ln(5)
            
                # Histogramme (titre à gauche, image centrée)
                with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f_dist:
                    fig_dist.savefig(f_dist.name, format='png', bbox_inches='tight')
                    pdf.cell(0, 10, "Histogramme", ln=True)  # align left
                    pdf.image(f_dist.name, x=15, w=180)
            
                return pdf.output(dest='S').encode('latin1')





            pdf_bytes = generate_pdf(avg_score, fig, fig_dist, len(df))
            st.download_button(
                label="📄 Télécharger le rapport PDF",
                data=pdf_bytes,
                file_name="rapport_sus.pdf",
                mime="application/pdf"
            )

    except Exception as e:
        st.error(f"Une erreur est survenue : {str(e)}")
