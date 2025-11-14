from fpdf import FPDF
import plotly.io as pio
import pandas as pd
import os
from datetime import datetime
import plotly.graph_objects as go


# ============================================================================
# PDF class
# ============================================================================
class SUSReportPDF(FPDF):

    def header(self):
        # Logo en haut à droite
        logo_path = os.path.abspath(os.path.join(
            os.path.dirname(__file__),
            "..",
            "assets",
            "logo_alterkpi.png"
        ))
        if os.path.exists(logo_path):
            self.image(logo_path, x=175, y=8, w=18)

        # Titre simple
        self.set_xy(10, 10)
        self.set_font("Helvetica", "B", 18)
        self.set_text_color(30, 30, 30)
        self.cell(0, 10, "Rapport d'analyse SUS", ln=True, align="L")

        # Sous-titre
        self.set_font("Helvetica", "", 10)
        self.set_text_color(80, 80, 80)
        self.cell(0, 6, f"Généré le {datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=True, align="L")

        # Ligne de séparation
        self.ln(3)
        self.set_draw_color(170, 170, 170)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(6)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 9)
        self.set_text_color(110, 110, 110)
        self.cell(0, 10, "Alter KPI - www.alter-kpi.com", align="C")


# ============================================================================
# MAIN
# ============================================================================
def generate_sus_pdf(df: pd.DataFrame, figs: dict, output_path: str):

    # Folder for PNG export
    img_dir = "temp_images"
    os.makedirs(img_dir, exist_ok=True)

    img_paths = {}

    # ============================================================================
    # EXPORT DES FIGURES EN PNG (compatible Render)
    # ============================================================================
    for key, fig in figs.items():
        if fig is None:
            continue

        # 🔥 Convertir dict → figure Plotly si nécessaire
        if isinstance(fig, dict):
            fig = go.Figure(fig)

        path = os.path.join(img_dir, key.replace(" ", "_") + ".png")

        # 🔥 Export PNG sans Chrome, sans Kaleido
        png_bytes = fig.to_image(format="png", scale=2)

        with open(path, "wb") as f:
            f.write(png_bytes)

        img_paths[key] = path

    # ============================================================================
    # PDF
    # ============================================================================
    pdf = SUSReportPDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    # ============================================================================
    # PAGE 1 – Résumé + Graphiques principaux
    # ============================================================================
    pdf.add_page()

    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(30, 30, 30)
    pdf.cell(0, 10, "Résumé statistique", ln=True)

    pdf.ln(3)
    pdf.set_draw_color(180, 180, 180)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(6)

    # Statistiques
    pdf.set_font("Helvetica", "", 11)
    stats = {
        "Nombre de réponses": len(df),
        "Score moyen SUS": f"{df['SUS_Score'].mean():.1f}",
        "Réponses >= 70": f"{(df['SUS_Score'] >= 70).mean()*100:.1f}%",
        "Médiane": f"{df['SUS_Score'].median():.1f}",
        "Écart-type": f"{df['SUS_Score'].std():.2f}",
        "Score minimum": f"{df['SUS_Score'].min():.1f}",
        "Score maximum": f"{df['SUS_Score'].max():.1f}",
    }

    for k, v in stats.items():
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(60, 8, k + " :", ln=0)
        pdf.set_font("Helvetica", "", 11)
        pdf.cell(40, 8, str(v), ln=1)

    pdf.ln(5)

    # Ordre des graphiques principaux
    main_order = ["SUS moyen", "Acceptabilite", "Repartition", "Radar"]

    for key in main_order:
        if key not in img_paths:
            continue
        pdf.image(img_paths[key], w=175)
        pdf.ln(10)

    # ============================================================================
    # PAGE 2 – Classes SUS + 4 histogrammes par catégories
    # ============================================================================
    pdf.add_page()

    # --- Classes SUS en haut ---
    if "Classes SUS" in img_paths:
        pdf.ln(2)
        pdf.image(img_paths["Classes SUS"], w=175, h=80)
        pdf.ln(4)

    # Séparateur
    pdf.set_draw_color(200, 200, 200)
    pdf.set_line_width(0.3)
    pdf.line(12, pdf.get_y(), 198, pdf.get_y())
    pdf.ln(3)

    # --- Grille 2x2 ---
    cat_keys = ["Categorie 1", "Categorie 2", "Categorie 3", "Categorie 4"]

    left_x, right_x = 12, 110
    top = pdf.get_y()
    row_height = 70

    positions = [
        (cat_keys[0], left_x,  top),
        (cat_keys[1], right_x, top),
        (cat_keys[2], left_x,  top + row_height),
        (cat_keys[3], right_x, top + row_height),
    ]

    for key, x, y in positions:
        if key not in img_paths:
            continue
        pdf.set_xy(x, y + 6)
        pdf.image(img_paths[key], w=85, h=70)

    # ============================================================================
    # CLEAN
    # ============================================================================
    for p in img_paths.values():
        try:
            os.remove(p)
        except:
            pass

    pdf.output(output_path)
    return output_path
