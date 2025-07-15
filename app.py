
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from fpdf import FPDF
from datetime import datetime
import tempfile
import os

# Dummy data pour test
questions = [f"Question{i}" for i in range(1, 11)]
data = {
    q: np.random.randint(1, 6, 27)
    for q in questions
}
df = pd.DataFrame(data)
df['SUS_Score'] = df.apply(lambda row: sum([(val - 1 if i % 2 == 0 else 5 - val)
                                            for i, val in enumerate(row)]) * 2.5, axis=1)
avg_score = df['SUS_Score'].mean()

# Radar chart
def create_radar(df):
    means = df[questions].mean().tolist()
    means += [means[0]]
    angles = np.linspace(0, 2 * np.pi, len(questions), endpoint=False).tolist()
    angles += [angles[0]]
    fig, ax = plt.subplots(figsize=(4, 4), subplot_kw=dict(polar=True))
    ax.plot(angles, means, 'b-', linewidth=2)
    ax.fill(angles, means, 'b', alpha=0.25)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels([f"Q{i}" for i in range(1, 11)])
    ax.set_yticks([1, 2, 3, 4, 5])
    ax.set_ylim(1, 5)
    return fig

# Gauge chart
def create_gauge(score):
    fig, ax = plt.subplots(figsize=(4, 1))
    ax.barh(0, score, color='skyblue', height=0.3)
    ax.plot(score, 0, 'ro')
    ax.set_xlim(0, 100)
    ax.set_yticks([])
    ax.set_xlabel("Score SUS")
    return fig

# PDF generator
def generate_pdf(path, score, radar_img, gauge_img):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Rapport - Questionnaire SUS", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, f"Date : {datetime.now().strftime('%Y-%m-%d')}", ln=True)
    pdf.cell(0, 10, f"Score moyen : {score:.1f} / 100", ln=True)
    pdf.ln(10)
    pdf.image(gauge_img, w=160)
    pdf.ln(10)
    pdf.image(radar_img, w=160)
    pdf.output(path)

# Streamlit interface
st.title("✅ Test PDF FPDF")

if st.button("📄 Générer PDF"):
    with tempfile.TemporaryDirectory() as tmpdir:
        radar_path = os.path.join(tmpdir, "radar.png")
        gauge_path = os.path.join(tmpdir, "gauge.png")
        fig1 = create_radar(df)
        fig2 = create_gauge(avg_score)
        fig1.savefig(radar_path)
        fig2.savefig(gauge_path)
        plt.close(fig1)
        plt.close(fig2)

        pdf_path = os.path.join(tmpdir, "rapport.pdf")
        generate_pdf(pdf_path, avg_score, radar_path, gauge_path)

        with open(pdf_path, "rb") as f:
            st.download_button("📥 Télécharger le rapport PDF", f.read(), "rapport_sus.pdf", mime="application/pdf")
