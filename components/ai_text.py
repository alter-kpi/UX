
from openai import OpenAI
import os

def generate_ai_analysis(prompt: str) -> str:
    """Retourne le texte généré par GPT à partir du prompt."""
    
    client = OpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
        project="proj_yasnkE8HrI6TfxWLX1kGERi3"
    )

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Tu es un expert UX concis et professionnel."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=2000
    )

    return response.choices[0].message.content
