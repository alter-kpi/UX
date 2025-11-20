from fpdf import FPDF
import plotly.io as pio
import plotly.graph_objects as go
import pandas as pd
import os
import tempfile
from datetime import datetime
from PIL import Image

from components.charts import create_category_combined


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

    hex_color = hex_color.lstrip("#")
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)

    return (r, g, b)


# ============================================================================
# PDF CLASS (Roboto Unicode) - ORIENTATION PAYSAGE
# ============================================================================
class SUSReportPDF(FPDF):
    def __init__(self):
        # A4 paysage
        super().__init__(orientation="L")

        font_dir = os.path.join(os.path.dirname(__file__), "..", "assets", "fonts")
        self.add_font("Roboto", "", os.path.join(font_dir, "Roboto-Regular.ttf"), uni=True)
        self.add_font("Roboto", "B", os.path.join(font_dir, "Roboto-Bold.ttf"), uni=True)

    def header(self):
        logo_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "assets", "logo_alterkpi.png")
        )

        if os.path.exists(logo_path):
            # un peu à droite en paysage
            self.image(logo_path, x=self.w - 30, y=8, w=18)

        self.set_xy(10, 10)
        self.set_font("Roboto", "B", 14)
        self.set_text_color(30, 30, 30)
        self.cell(0, 10, "Rapport d'analyse SUS", ln=True)

        self.set_font("Roboto", "", 9)
        self.set_text_color(80, 80, 80)
        self.cell(0, 6, f"Généré le {datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=True)

        self.ln(3)
        self.set_draw_color(170, 170, 170)
        self.line(10, self.get_y(), self.w - 10, self.get_y())
        self.ln(6)

    def footer(self):
        self.set_y(-12)
        self.set_font("Roboto", "", 9)
        self.set_text_color(110, 110, 110)
        self.cell(0, 8, "Alter KPI - www.alter-kpi.com - info@alter-kpi.com", align="C")


# ============================================================================
# KPI compact
# ============================================================================
def draw_kpi(pdf, title, value, x, y, w=70, h=16, bg_color=(247, 247, 247)):
    r, g, b = bg_color
    brightness = (r * 0.299 + g * 0.587 + b * 0.114)
    text_color = (255, 255, 255) if brightness < 150 else (30, 30, 30)

    border_color = (max(r - 40, 0), max(g - 40, 0), max(b - 40, 0))

    # Ombre plus légère
    pdf.set_draw_color(220, 220, 220)
    pdf.set_fill_color(240, 240, 240)
    pdf.rect(x + 0.7, y + 0.7, w, h, style="F")

    # Carte
    pdf.set_draw_color(*border_color)
    pdf.set_fill_color(*bg_color)
    pdf.rect(x, y, w, h, style="DF")

    # Titre
    pdf.set_xy(x, y + 2)
    pdf.set_font("Roboto", "B", 8)
    pdf.set_text_color(*text_color)
    pdf.cell(w, 4, title, align="C", ln=1)

    # Valeur
    pdf.set_xy(x, y + 7)
    pdf.set_font("Roboto", "", 11)
    pdf.cell(w, 6, value, align="C", ln=1)


# ============================================================================
# Utilitaire : sauvegarde d'un fig Plotly en PNG + retour (path, w_img, h_img)
# ============================================================================
def save_fig_to_png(fig_obj, key, img_dir):
    if fig_obj is None:
        return None

    if isinstance(fig_obj, dict):
        fig_obj = go.Figure(fig_obj)

    file_name = f"{key}.png"
    path = os.path.join(img_dir, file_name)

    # export HD
    pio.write_image(fig_obj, path, format="png", scale=2)

    with Image.open(path) as im:
        im = im.convert("RGB")
        w_img, h_img = im.size
        im.save(path, format="PNG")

    return {"path": path, "w": w_img, "h": h_img}


# ============================================================================
# Utilitaire : dessin d'une image SANS déformation, centrée horizontalement
# ============================================================================
def draw_image_centered(pdf, img_info, x_zone, y_zone, max_w, max_h):
    """
    img_info : dict {path, w, h}
    x_zone, y_zone : coin haut-gauche de la zone
    max_w, max_h : taille max dispo
    """
    if not img_info:
        return

    path = img_info["path"]
    w_img = img_info["w"]
    h_img = img_info["h"]

    if w_img == 0 or h_img == 0:
        return

    # scale sans déformation (ratio préservé)
    scale = min(max_w / w_img, max_h / h_img)
    w_display = w_img * scale
    h_display = h_img * scale

    # centrage horizontal dans la zone
    x_img = x_zone + (max_w - w_display) / 2
    y_img = y_zone  # pas de centrage vertical, top align

    pdf.image(path, x=x_img, y=y_img, w=w_display, h=h_display)


# ============================================================================
# MAIN PDF GENERATOR
# ============================================================================
def generate_sus_pdf(df, figs, output_path, ai_text=None, stats_table=None):
    nb_resp = len(df)

    # ------------------------------------------------------------------------
    # 1) Export des figures → PNG + tailles
    #    figs contient : gauge, accept, hist, radar, class
    # ------------------------------------------------------------------------
    img_dir = os.path.join(tempfile.gettempdir(), "sus_temp_images")
    os.makedirs(img_dir, exist_ok=True)

    img_infos = {}

    # Graphes principaux venant du fig-store
    for key in ["gauge", "accept", "hist", "radar", "class"]:
        fig_obj = figs.get(key) if isinstance(figs, dict) else None
        if fig_obj is not None:
            info = save_fig_to_png(fig_obj, key, img_dir)
            if info:
                img_infos[key] = info

    # ------------------------------------------------------------------------
    # 2) Génération des graphes catégories (comme dans l'app)
    #    Colonnes 11:15 comme dans update_categories
    # ------------------------------------------------------------------------
    extra_cols = df.columns[11:15]
    cat_keys = []

    for i, col in enumerate(extra_cols):
        fig_cat = create_category_combined(df, col, i)
        key = f"cat{i+1}"
        cat_keys.append(key)
        info = save_fig_to_png(fig_cat, key, img_dir)
        if info:
            img_infos[key] = info

    # ------------------------------------------------------------------------
    # 3) Création PDF (paysage)
    # ------------------------------------------------------------------------
    pdf = SUSReportPDF()
    # marge un peu plus large pour impression
    pdf.set_auto_page_break(auto=True, margin=25)

    # ========================================================================
    # PAGE 1 — Dashboard (Première moitié)
    # ========================================================================

    pdf.add_page()

    # --- Titre principal ---
    pdf.set_font("Roboto", "B", 12)
    pdf.set_text_color(30, 30, 30)
    pdf.cell(0, 8, "Résumé du questionnaire SUS", ln=True)
    pdf.ln(4)

    # -----------------------------
    # 1) KPI Cards
    # -----------------------------
    y_start = pdf.get_y()
    kpi_w = (pdf.w - 30) / 3   # 3 colonnes pour les KPIs
    kpi_h = 40  # Hauteur des cartes KPI
    kpi_spacing = 10  # Espace entre les cartes

    # Générer les cartes KPI
    draw_kpi(pdf, "Nombre de réponses", f"{nb_resp}", 10, y_start, w=kpi_w)
    y_start += kpi_h + kpi_spacing

    draw_kpi(pdf, "Score SUS moyen", f"{sus_mean:.1f}", kpi_w + 10, y_start, w=kpi_w, bg_color=sus_color)
    y_start += kpi_h + kpi_spacing

    draw_kpi(pdf, "≥ 72 (Acceptable+)", f"{pct_72:.1f}%", 2 * kpi_w + 10, y_start, w=kpi_w)
    y_start += kpi_h + kpi_spacing

    # -----------------------------
    # 2) Graphiques (Partie 1)
    # -----------------------------
    if "gauge" in img_infos:
        draw_image_centered(
            pdf,
            img_infos["gauge"],
            x_zone=(pdf.w - 160) / 2,
            y_zone=y_start,
            max_w=160,
            max_h=30
        )

    y_start += 30 + 10  # Espacement après la jauge

    if "accept" in img_infos:
        draw_image_centered(
            pdf,
            img_infos["accept"],
            x_zone=(pdf.w - 160) / 2,
            y_zone=y_start,
            max_w=160,
            max_h=30
        )
    y_start += 30 + 10

    # -----------------------------
    # 3) Table des Stats
    # -----------------------------
    pdf.set_xy(10, y_start)
    pdf.set_font("Roboto", "", 10)
    pdf.set_text_color(40, 40, 40)
    pdf.set_draw_color(180, 180, 180)  # couleur des bordures
    pdf.set_fill_color(245, 245, 245)  # couleur de fond des cellules
    pdf.set_line_width(0.3)

    for i, row in stats_df.iterrows():
        pdf.cell(50, 5, f"{row['Indicateur']}:", border=1, align="L")
        pdf.cell(30, 5, f"{row['Valeur']}", border=1, align="C")
        pdf.ln(5)

    pdf.ln(10)  # Fin de la page 1

    # ========================================================================
    # PAGE 2 — Dashboard (Seconde moitié)
    # ========================================================================

    pdf.add_page()

    # --- Titre principal ---
    pdf.set_font("Roboto", "B", 12)
    pdf.set_text_color(30, 30, 30)
    pdf.cell(0, 8, "Résumé du questionnaire SUS (Suite)", ln=True)
    pdf.ln(4)

    # -----------------------------
    # 4) Graphiques (Partie 2)
    # -----------------------------
    if "hist" in img_infos:
        draw_image_centered(
            pdf,
            img_infos["hist"],
            x_zone=(pdf.w - 200) / 2,
            y_zone=pdf.get_y(),
            max_w=200,
            max_h=60
        )

    pdf.ln(70)  # Espacement après les graphiques

    if "radar" in img_infos:
        draw_image_centered(
            pdf,
            img_infos["radar"],
            x_zone=(pdf.w - 200) / 2,
            y_zone=pdf.get_y(),
            max_w=200,
            max_h=60
        )

    pdf.ln(70)  # Espacement après le radar

    # -----------------------------
    # 5) Graphique des classes (si nécessaire)
    # -----------------------------
    if "class" in img_infos:
        draw_image_centered(
            pdf,
            img_infos["class"],
            x_zone=(pdf.w - 200) / 2,
            y_zone=pdf.get_y(),
            max_w=200,
            max_h=60
        )

    pdf.ln(70)

    # -----------------------------
    # 6) Les 2 JAUGES (SUS + Acceptabilité) (partie basse)
    # -----------------------------
    y_gauges = pdf.get_y()  # Positionner après les graphiques
    if "gauge" in img_infos:
        draw_image_centered(
            pdf,
            img_infos["gauge"],
            x_zone=(pdf.w - 160) / 2,
            y_zone=y_gauges,
            max_w=160,
            max_h=30
        )

    y_gauges += 30 + 10  # Espacement

    if "accept" in img_infos:
        draw_image_centered(
            pdf,
            img_infos["accept"],
            x_zone=(pdf.w - 160) / 2,
            y_zone=y_gauges,
            max_w=160,
            max_h=30
        )

    pdf.ln(10)

    # --- Fin de la page 2 ---


    # ========================================================================
    # PAGE 3 — ANALYSE IA (texte)
    # ========================================================================
    if ai_text:
        pdf.add_page()

        pdf.set_font("Roboto", "B", 12)
        pdf.cell(0, 8, "Analyse IA", ln=True)

        pdf.ln(2)
        pdf.set_draw_color(180, 180, 180)
        pdf.line(10, pdf.get_y(), pdf.w - 10, pdf.get_y())
        pdf.ln(4)

        pdf.set_font("Roboto", "", 11)
        # Nettoyage minimal : on enlève les marqueurs Markdown lourds
        cleaned = (
            ai_text.replace("####", "")
            .replace("###", "")
            .replace("**", "")
        )

        for line in cleaned.split("\n"):
            if pdf.get_y() > pdf.h - 20:
                pdf.add_page()
                pdf.set_font("Roboto", "", 11)
            pdf.multi_cell(0, 5, line)
            pdf.ln(1)

    # ========================================================================
    # CLEAN TEMP FILES
    # ========================================================================
    for info in img_infos.values():
        try:
            os.remove(info["path"])
        except Exception:
            pass

    pdf.output(output_path)
    return output_path
