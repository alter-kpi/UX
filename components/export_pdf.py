from fpdf import FPDF
import plotly.io as pio
pio.kaleido.scope.default_format = "png"
import plotly.graph_objects as go
import pandas as pd
import os
import io
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
    elif score < 51:
        hex_color = "#f0ad4e"
    elif score < 68:
        hex_color = "#f7ec13"
    elif score < 80:
        hex_color = "#5bc0de"
    elif score < 84:
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
        self.cell(0, 10, "Alter UX - Rapport d'analyse SUS", ln=True)

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
        self.cell(0, 8, "Alter UX - www.alter-ux.com - info@alter-kpi.com", align="C")


# ============================================================================
# KPI compact
# ============================================================================
def draw_kpi(pdf, title, value, x, y, w=70, h=16, bg_color=(247, 247, 247)):
    r, g, b = bg_color
    brightness = (r * 0.299 + g * 0.587 + b * 0.114)
    text_color = (255, 255, 255) if brightness < 150 else (30, 30, 30)

    border_color = (max(r - 40, 0), max(g - 40, 0), max(b - 40, 0))

    # Ombre plus légère
   # pdf.set_draw_color(220, 220, 220)
   # pdf.set_fill_color(240, 240, 240)
   # pdf.rect(x + 0.7, y + 0.7, w, h, style="F")

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

    # rendu léger (stable Render)
    png_bytes = fig_obj.to_image(format="png", width=800, height=500)

    file_name = f"{key}.png"
    path = os.path.join(img_dir, file_name)

    with open(path, "wb") as f:
        f.write(png_bytes)

    im = Image.open(io.BytesIO(png_bytes))
    w_img, h_img = im.size

    return {"path": path, "w": w_img, "h": h_img}


# ============================================================================
# Utilitaire : dessin d'une image SANS déformation, centrée horizontalement
# ============================================================================
def draw_image_centered(pdf, img_info, x_zone, y_zone, max_w, max_h, shadow_offset=0.2, shadow_color=(200, 200, 200)):
    """
    img_info : dict {path, w, h}
    x_zone, y_zone : coin haut-gauche de la zone
    max_w, max_h : taille max disponible
    shadow_offset : décalage pour l'ombre tout autour
    shadow_color : couleur de l'ombre (en RGB)
    """
    if not img_info:
        return

    path = img_info["path"]
    w_img = img_info["w"]
    h_img = img_info["h"]

    if w_img == 0 or h_img == 0:
        return

    # Calcul de l'échelle pour conserver le ratio
    scale = min(max_w / w_img, max_h / h_img)
    w_display = w_img * scale
    h_display = h_img * scale

    # Calcul du positionnement
    x_img = x_zone + (max_w - w_display) / 2
    y_img = y_zone  # Pas de centrage vertical, aligné en haut

    # Dessiner l'ombre tout autour de l'image
    pdf.set_fill_color(*shadow_color)  # Définir la couleur de l'ombre

    # Ombre tout autour (haut, bas, gauche, droite)
    pdf.rect(x_img - shadow_offset, y_img - shadow_offset, w_display + 2*shadow_offset, h_display + 2*shadow_offset, 'F')

    # Dessiner l'image principale au-dessus de l'ombre
    pdf.image(path, x=x_img, y=y_img, w=w_display, h=h_display)  # Image principale




# ============================================================================
# MAIN PDF GENERATOR
# ============================================================================
def generate_sus_pdf(df, figs, output_path, ai_text=None, stats_table=None):

    # ------------------------------------------------------------------------
    # 1) Export des figures → PNG + tailles
    #    figs contient : gauge, accept, hist, radar, class
    # ------------------------------------------------------------------------
    img_dir = os.path.join(tempfile.gettempdir(), "sus_temp_images")
    os.makedirs(img_dir, exist_ok=True)

    img_infos = {}

    # Graphes principaux venant du fig-store
    for key in ["gauge", "hist", "radar", "class"]:
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
    # PAGE 1 — Résumé + KPIs + Graph Classes + 2 JAUGES
    # ========================================================================

    pdf.add_page()

    # --- Titre principal ---
    pdf.ln(1)
    pdf.set_font("Roboto", "B", 11)
    pdf.set_text_color(30, 30, 30)
    pdf.cell(0, 2, "Résumé du questionnaire SUS", ln=True)
    #pdf.ln(4)

    # -----------------------------
    # 1) Colonnes : Stats / KPI / Classes
    # -----------------------------

    # Données stats
    stats_df = pd.DataFrame(stats_table) if stats_table else pd.DataFrame()

    # -----------------------------
    # 1.1) Colonne STATISTIQUES (gauche)
    # -----------------------------
    pdf.set_xy(10, 50)  # Position de départ du tableau
    pdf.set_font("Roboto", "", 6)
    pdf.set_text_color(40, 40, 40)

    # Dessiner l'en-tête du tableau (titres des colonnes)
    pdf.set_font("Roboto", "B", 10)
    pdf.cell(50, 5, "Indicateur", border=1, align="C", ln=False)  # Colonne "Indicateur"
    pdf.cell(30, 5, "Valeur", border=1, align="C", ln=True)       # Colonne "Valeur" (avec retour à la ligne)

    # Remplir les lignes du tableau avec les données du DataFrame
    pdf.set_font("Roboto", "", 10)
    for _, row in stats_df.iterrows():
        pdf.set_xy(10, pdf.get_y())  # Réinitialise la position Y pour chaque ligne
        pdf.cell(50, 5, f"{row['Indicateur']}", border=1, align="C", ln=False)  # Indicateur
        pdf.cell(30, 5, str(row["Valeur"]), border=1, align="C", ln=True)        # Valeur (avec retour à la ligne)


    # -----------------------------
    # 1.2) Colonne KPI (centre)
    # -----------------------------
    sus_mean = df["SUS_Score"].mean()
    sus_color = get_sus_color(sus_mean)
    nb_resp = len(df)
    pct80 = float((df["SUS_Score"] >= 80).mean() * 100)

    draw_kpi(pdf, "Nombre de réponses", f"{nb_resp}", 105, 55, w=40)
    draw_kpi(pdf, "Score SUS moyen", f"{sus_mean:.1f}", 105, 75, w=40, bg_color=sus_color)
    draw_kpi(pdf, "≥ 80 (Bonne UX)", f"{pct80:.1f}%", 105, 95, w=40)


    # -----------------------------
    # 1.3) Colonne GRAPH CLASSES (droite)
    # -----------------------------
    if "class" in img_infos:
        draw_image_centered(
            pdf,
            img_infos["class"],
            x_zone=160,
            y_zone=50,
            max_w=120,
            max_h=100
        )

    
    # ========================================================================
    # 2) JAUGES (SUS + Acceptabilité)
    # ========================================================================
    pdf.set_xy(10, 135)
    pdf.set_font("Roboto", "B", 11)
    pdf.cell(0, 2, "Scores SUS & Acceptabilité", ln=True)



    margin_x = (pdf.w - 300) / 2

    # Jauge SUS (haut)
    if "gauge" in img_infos:
        draw_image_centered(
            pdf,
            img_infos["gauge"],
            x_zone=margin_x,
            y_zone=145,
            max_w=300,
            max_h=40
        )


    # ========================================================================
    # PAGE 2 — 
    # ========================================================================

    pdf.add_page()

    # ---- TITRE ----
    pdf.ln(1)
    pdf.set_font("Roboto", "B", 12)
    pdf.set_text_color(30, 30, 30)
    pdf.cell(0, 8, "Répartition des scores & Radar", ln=True)

    # ---- GRAPHE HISTOGRAMME (gauche) ----
    if "hist" in img_infos:
        draw_image_centered(
            pdf,
            img_infos["hist"],
            x_zone=10,     # Coin haut-gauche
            y_zone=70,
            max_w= (pdf.w / 2) - 15,   # moitié de la largeur
            max_h=150                 # hauteur fixe
        )

    # ---- GRAPHE RADAR (droite) ----
    if "radar" in img_infos:
        draw_image_centered(
            pdf,
            img_infos["radar"],
            x_zone=(pdf.w / 2) + 5,   # moitié droite
            y_zone=70,
            max_w=(pdf.w / 2) - 15,
            max_h=150
        )

   
    # ========================================================================
    # PAGE 3 — Graphiques par catégorie (affichée uniquement si ≥ 1 catégorie)
    # ========================================================================

    # ------------------------------------------------------------
    # 1. Détection des catégories comme dans l'app
    # ------------------------------------------------------------
    cols = list(df.columns)

    try:
        q10_index = cols.index("Q10")
        raw_cat_cols = cols[q10_index + 1 : q10_index + 5]
    except ValueError:
        raw_cat_cols = []

    valid_categories = []

    for col in raw_cat_cols:
        # Exclure colonnes _adj
        if col.endswith("_adj"):
            continue
        # Exclure colonnes vides
        if df[col].dropna().empty:
            continue
        valid_categories.append(col)

    # Garder max 4
    valid_categories = valid_categories[:4]

    # ------------------------------------------------------------
    # 2. Si aucune catégorie → NE PAS créer la page
    # ------------------------------------------------------------
    if len(valid_categories) == 0:
        # Rien du tout : on ne crée aucune page 3
        pass

    else:
        # --------------------------------------------------------
        # 3. Générer uniquement les figures valides
        # --------------------------------------------------------
        for i, col in enumerate(valid_categories):
            fig_cat = create_category_combined(df, col, i)
            key = f"cat{i+1}"
            info = save_fig_to_png(fig_cat, key, img_dir)
            if info:
                img_infos[key] = info

        # --------------------------------------------------------
        # 4. Affichage sur une page 3 (2×2 max)
        # --------------------------------------------------------
        pdf.add_page()
        pdf.ln(1)
        pdf.set_font("Roboto", "B", 12)
        pdf.set_text_color(30, 30, 30)
        pdf.cell(0, 8, "Analyse par catégorie", ln=True)

        coords = [
            (10, 45),
            ((pdf.w / 2) + 5, 45),
            (10, 120),
            ((pdf.w / 2) + 5, 120),
        ]
        MAX_W = (pdf.w / 2) - 20
        MAX_H = 80

        # Placement propre
        for i, key in enumerate([f"cat{i+1}" for i in range(len(valid_categories))]):
            if key in img_infos:
                x_zone, y_zone = coords[i]
                draw_image_centered(
                    pdf,
                    img_infos[key],
                    x_zone=x_zone,
                    y_zone=y_zone,
                    max_w=MAX_W,
                    max_h=MAX_H
                )

    # ========================================================================
    # PAGE 4 — Analyse IA (style proche CSS + Markdown enrichi)
    # ========================================================================

    pdf.add_page()

    # ---- CONFIG STYLE ----
    LEFT = 20
    RIGHT = pdf.w - 20
    MAX_W = RIGHT - LEFT

    LINE = 5.2
    TITLE_LINE = 7

    pdf.set_text_color(40, 40, 40)

    def write_paragraph(text):
        pdf.set_x(LEFT)
        pdf.multi_cell(MAX_W, LINE, text)
        pdf.ln(1.5)

    def write_title(text):
        pdf.set_x(LEFT)
        pdf.set_font("Roboto", "B", 12)
        pdf.set_text_color(30, 30, 30)
        pdf.multi_cell(MAX_W, TITLE_LINE, text)
        pdf.ln(2)
        pdf.set_font("Roboto", "", 10)
        pdf.set_text_color(40, 40, 40)

    def write_subtitle(text):
        pdf.set_x(LEFT)
        pdf.set_font("Roboto", "B", 11)
        pdf.set_text_color(35, 35, 35)
        pdf.multi_cell(MAX_W, LINE, text)
        pdf.ln(1)
        pdf.set_font("Roboto", "", 10)
        pdf.set_text_color(40, 40, 40)


    # ---- TITRE PAGE ----
    write_title("Analyse IA détaillée")

    # Ligne sous titre
    pdf.set_draw_color(170, 170, 170)
    pdf.line(LEFT, pdf.get_y(), RIGHT, pdf.get_y())
    pdf.ln(4)


    # ---- RENDU MARKDOWN MANUEL ----
    if ai_text:
        clean = ai_text.split("\n")

        for line in clean:

            # TITRE (####)
            if line.startswith("#### "):
                write_subtitle(line.replace("#### ", ""))

            # Saut de section
            elif line.strip() == "":
                pdf.ln(2)

            # Paragraphe normal
            else:
                write_paragraph(line)

    else:
        write_paragraph("Aucune analyse IA n’a été générée.")

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






