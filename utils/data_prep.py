import pandas as pd
from pathlib import Path

def calculate_sus(row):
    score = 0
    for i in range(10):
        val = row[i]
        score += val - 1 if i % 2 == 0 else 5 - val
    return score * 2.5

def prepare_data(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    questions = [f"Question{i}" for i in range(1, 11)]

    missing = [q for q in questions if q not in df.columns]
    if missing:
        raise ValueError(f"Colonnes manquantes : {', '.join(missing)}")

    category_columns = df.columns[11:15]
    custom_columns = [col for col in category_columns if df[col].notna().any()]
    category_info = {
        col: "Numérique" if pd.api.types.is_numeric_dtype(df[col]) else "Texte"
        for col in custom_columns
    }

    df["SUS_Score"] = df[questions].apply(calculate_sus, axis=1)
    return df, category_info

def load_data(filepath: str = "data/data.xlsx"):
    file = Path(filepath)
    df = pd.read_excel(file)
    df = df.astype({"Sujet": "string"}, errors="ignore")
    return prepare_data(df)

