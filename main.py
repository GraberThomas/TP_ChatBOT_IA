from typing import Iterable
import os
from dotenv import load_dotenv
from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam

load_dotenv()

api_key = os.environ.get("GROQ_API_KEY")

if not api_key:
    raise ValueError("GROQ_API_KEY n'est pas configuré dans le fichier .env")

client = OpenAI(
    api_key=api_key,
    base_url="https://api.groq.com/openai/v1",
)

def get_available_models() -> list[str]:
    """Récupère la liste des modèles disponibles."""
    models = client.models.list()
    return sorted(model.id for model in models.data)

def ask_llm(messages: Iterable[ChatCompletionMessageParam], model: str) -> str:
    """Envoie la requête et retourne uniquement la réponse textuelle."""
    response = client.chat.completions.create(
        model=model,
        messages=messages,
    )
    return response.choices[0].message.content or ""