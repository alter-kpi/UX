
from openai import OpenAI
import os

def generate_ai_analysis(prompt: str) -> str:
    """Retourne le texte généré par GPT à partir du prompt."""
    
    #client = OpenAI(api_key="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")
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
        max_tokens=1000
    )

    return response.choices[0].message.content


