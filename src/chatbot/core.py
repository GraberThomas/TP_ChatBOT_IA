import time
import logging
from typing import Iterable, Optional, Dict, Any
import os
import streamlit as st
from openai import OpenAI, OpenAIError
from openai.types.chat import ChatCompletionMessageParam

# Configuration du logging
LOG_DIR = "logs"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(LOG_DIR, "chatbot.log")),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("Chatbot")

# Métriques globales (simulées pour le TP)
metrics = {
    "total_requests": 0,
    "total_errors": 0,
    "total_response_time": 0.0,
}

def get_client(provider: str = "groq") -> OpenAI:
    """Retourne le client API approprié en utilisant st.secrets."""
    if provider == "groq":
        # Priorité aux secrets Streamlit, fallback sur variables d'environnement
        try:
            api_key = st.secrets.get("GROQ_API_KEY")
        except:
            api_key = os.environ.get("GROQ_API_KEY")
            
        if not api_key:
            raise ValueError("GROQ_API_KEY n'est pas configuré")
        return OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")
    else:
        raise ValueError(f"Fournisseur inconnu : {provider}")

def get_available_models(provider: str = "groq") -> list[str]:
    """Récupère la liste des modèles disponibles pour un fournisseur."""
    try:
        client = get_client(provider)
        models = client.models.list()
        return sorted(model.id for model in models.data)
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des modèles ({provider}): {e}")
        return []

def ask_llm(
    messages: Iterable[ChatCompletionMessageParam], 
    model: str, 
    temperature: float = 0.7,
    provider: str = "groq"
) -> str:
    """
    Envoie la requête et retourne uniquement la réponse textuelle.
    Gère les erreurs et enregistre les métriques.
    """
    global metrics
    start_time = time.time()
    metrics["total_requests"] += 1
    
    try:
        client = get_client(provider)
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            timeout=30.0 # Timeout de 30 secondes
        )
        
        content = response.choices[0].message.content
        if not content:
            raise ValueError("Réponse vide de l'API")
            
        elapsed_time = time.time() - start_time
        metrics["total_response_time"] += elapsed_time
        
        logger.info(f"Requête réussie: model={model}, temp={temperature}, time={elapsed_time:.2f}s")
        return content

    except OpenAIError as e:
        metrics["total_errors"] += 1
        logger.error(f"Erreur API OpenAI/Groq: {e}")
        raise Exception(f"Désolé, une erreur est survenue avec l'API : {str(e)}")
    except Exception as e:
        metrics["total_errors"] += 1
        logger.error(f"Erreur inattendue: {e}")
        raise Exception(f"Une erreur inattendue est survenue : {str(e)}")

def get_metrics() -> Dict[str, Any]:
    """Retourne les métriques actuelles."""
    avg_response_time = 0
    if metrics["total_requests"] > 0:
        avg_response_time = metrics["total_response_time"] / metrics["total_requests"]
        
    return {
        **metrics,
        "avg_response_time": avg_response_time,
        "error_rate": (metrics["total_errors"] / metrics["total_requests"] * 100) if metrics["total_requests"] > 0 else 0
    }
