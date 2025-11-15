from fpdf import FPDF
import plotly.io as pio
import plotly.graph_objects as go
import pandas as pd
import os
import tempfile
from datetime import datetime
from PIL import Image


# ============================================================================
# Couleur dynamique identique à la jauge native charts.py
# ============================================================================
def get_sus_color(score):
    score = float(score)

    if score < 25:
        hex_color = "#FF0000"
    elif score < 39:
        hex_color = "#f0ad4e"
    elif score < 52:
        hex_color = "#f7ec13"
    elif score < 73:
        hex_color = "#5bc0de"
    elif score < 86:
        hex_color = "#5cb85c"
    else:
        hex_color = "#3c763d"

    # hex → RGB
    hex_color = hex_color.lstrip('#')
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)

    return (r, g, b)


# ============================================================================
# PDF CLASS (Roboto Unicode)
# ============================================================================
class SUSReportPDF(FPDF):

    def __init__(self):
        super().__init__()

        font_dir = os.path.join(os.path.dirname(__file__), "..", "assets", "fonts")
        self.add_font("Roboto", "", os.path.join(font_dir, "Roboto-Regular.ttf"), uni=True)
        self.add_font("Roboto", "B", os.path.join(font_dir, "Roboto-Bold.ttf"), uni=True)

    def header(self):
        logo_path = os.path.abspath(os.path.join(
            os.path.dirname(__file__),
            "..",
            "assets",
            "logo_alterkpi.png"
        ))

        if os.path.exists(logo_path):
            self.image(logo_path, x=175, y=8, w=18)

        self.set_xy(10, 10)
        self.set_font("Roboto", "B", 18)
        self.set_text_color(30, 30, 30)
        self.cell(0, 10, "Rapport d'analyse SUS", ln=True)

        self.set_font("Roboto", "", 10)
        self.set_text_color(80, 80, 80)
        self.cell(0, 6, f"Généré le {datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=True)

        self.ln(3)
        self.set_draw_color(170, 170, 170)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(6)

    def footer(self):
        self.set_y(-15)
        self.set_font("Roboto", "", 9)
        self.set_text_color(110, 110, 110)
        self.cell(0, 10, "Alter KPI - www.alter-kpi.com", align="C")


# ============================================================================
# KPI ultra-compacts (premium)
# ============================================================================
def draw_kpi(pdf, title, value, x, y, w=50, h=12, bg_color=(247, 247, 247)):
    # Détermination du texte (fond clair → noir, fond foncé → blanc)
    r, g, b = bg_color
    brightness = (r*0.299 + g*0.587 + b*0.114)
    text_color = (255, 255, 255) if brightness < 150 else (30, 30, 30)

    # Bordure premium
    border_color = (
        max(r-40, 0),
        max(g-40, 0),
        max(b-40, 0)
    )

    # Ombre légère
    pdf.set_draw_color(180, 180, 180)
    pdf.set_fill_color(0, 0, 0)
    pdf.rect(x + 1, y + 1, w, h, style="F")

    # Carte
    pdf.set_draw_color(*border_color)
    pdf.set_fill_color(*bg_color)
    pdf.rect(x, y, w, h, style="DF")

    # Titre compact
    pdf.set_xy(x, y + 1)
    pdf.set_font("Roboto", "B", 9)
    pdf.set_text_color(*text_color)
    pdf.cell(w, 4, title, align="C", ln=1)

    # Valeur compact
    pdf.set_xy(x, y + 5)
    pdf.set_font("Roboto", "", 11)
    pdf.cell(w, 5, value, align="C", ln=1)


# ============================================================================
# MAIN PDF GENERATOR
# ============================================================================
def generate_sus_pdf(df, figs, output_path, ai_text=None, stats_table=None):

    img_dir = os.path.join(tempfile.gettempdir(), "sus_temp_images")
    os.makedirs(img_dir, exist_ok=True)

    img_paths = {}

    # =========================================================================
    # EXPORT DES IMAGES PLOTLY → PNG
    # =========================================================================
    for key, fig in figs.items():
        if fig is None:
            continue

        if isinstance(fig, dict):
            fig = go.Figure(fig)

        file_name = key.replace(" ", "_") + ".png"
        path = os.path.join(img_dir, file_name)

        pio.write_image(fig, path, format="png", scale=2)

        with Image.open(path) as im:
            im = im.convert("RGB")
            im.save(path, format="PNG")

        img_paths[key] = path

    # =========================================================================
    # PDF
    # =========================================================================
    pdf = SUSReportPDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    # =========================================================================
    # PAGE 1 — RESUMÉ + KPI + JAUGES
    # =========================================================================
    pdf.add_page()

    pdf.set_font("Roboto", "B", 14)
    pdf.set_text_color(30, 30, 30)
    pdf.cell(0, 10, "Résumé statistique", ln=True)

    pdf.ln(3)
    pdf.set_draw_color(200, 200, 200)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(6)

    # Tableau des stats
    stats_df = pd.DataFrame(stats_table) if stats_table else pd.DataFrame()

    x_stats = 10
    y_stats = pdf.get_y()

    pdf.set_xy(x_stats, y_stats)
    pdf.set_font("Roboto", "", 11)
    pdf.set_text_color(40, 40, 40)

    for _, row in stats_df.iterrows():
        pdf.set_font("Roboto", "B", 11)
        pdf.cell(70, 6, f"{row['Indicateur']} :", ln=0)
        pdf.set_font("Roboto", "", 11)
        pdf.cell(40, 6, str(row["Valeur"]), ln=1)

    end_table_y = pdf.get_y()

    # KPI compacts
    x_kpi = 130
    y_kpi = y_stats

    sus_mean = df["SUS_Score"].mean()
    sus_color = get_sus_color(sus_mean)

    draw_kpi(pdf, "Score SUS", f"{sus_mean:.1f}", x_kpi, y_kpi, bg_color=sus_color)
    draw_kpi(pdf, "Réponses", str(len(df)), x_kpi, y_kpi + 16)
    draw_kpi(pdf, "≥ 70", f"{(df['SUS_Score'] >= 70).mean()*100:.1f}%", x_kpi, y_kpi + 32)
    draw_kpi(pdf, "≤ 50", f"{(df['SUS_Score'] <= 50).mean()*100:.1f}%", x_kpi, y_kpi + 48)

    # Position sous les KPI
    pdf.set_y(max(end_table_y, y_kpi + 68))

    # Section JAUGES
    pdf.ln(3)
    pdf.set_draw_color(210, 210, 210)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(6)

    pdf.set_font("Roboto", "B", 14)
    pdf.cell(0, 10, "Scores SUS & Acceptabilité", ln=True)

    pdf.ln(3)
    pdf.set_draw_color(200, 200, 200)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(6)

    # Graphes standard ( radar remis taille normale )
    main_order = ["SUS moyen", "Acceptabilite", "Repartition", "Radar"]

    for key in main_order:
        if key in img_paths:
            pdf.image(img_paths[key], w=175)
            pdf.ln(8)

    # =========================================================================
    # PAGE 2 — Classes + Catégories
    # =========================================================================
    pdf.add_page()

    if "Classes SUS" in img_paths:
        pdf.image(img_paths["Classes SUS"], w=175, h=80)
        pdf.ln(4)

    pdf.set_draw_color(200, 200, 200)
    pdf.line(12, pdf.get_y(), 198, pdf.get_y())
    pdf.ln(3)

    cat_keys = ["Categorie 1", "Categorie 2", "Categorie 3", "Categorie 4"]
    left_x, right_x = 12, 110
    top = pdf.get_y()
    row_h = 70

    positions = [
        (cat_keys[0], left_x, top),
        (cat_keys[1], right_x, top),
        (cat_keys[2], left_x, top + row_h),
        (cat_keys[3], right_x, top + row_h),
    ]

    for key, x, y in positions:
        if key in img_paths:
            pdf.set_xy(x, y + 6)
            pdf.image(img_paths[key], w=85, h=70)

    # =========================================================================
    # PAGE 3 — ANALYSE IA
    # =========================================================================
    if ai_text:
        pdf.add_page()

        pdf.set_font("Roboto", "B", 14)
        pdf.cell(0, 10, "Analyse IA", ln=True)

        pdf.ln(3)
        pdf.set_draw_color(180, 180, 180)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(5)

        pdf.set_font("Roboto", "", 11)
        cleaned = ai_text.replace("###", "").replace("**", "")

        for line in cleaned.split("\n"):
            if pdf.get_y() > 260:
                pdf.add_page()
            pdf.multi_cell(0, 5, line)
            pdf.ln(1)

    # =========================================================================
    # CLEAN TEMP FILES
    # =========================================================================
    for p in img_paths.values():
        try:
            os.remove(p)
        except:
            pass

    pdf.output(output_path)
    return output_path
