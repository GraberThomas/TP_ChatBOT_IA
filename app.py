from typing import cast
import streamlit as st
from openai.types.chat import ChatCompletionMessageParam
from main import ask_llm, get_available_models

st.set_page_config(page_title="Chatbot", page_icon="💬")
st.title("💬 Mon chatbot (Groq)")

@st.cache_data(ttl=300)
def load_models():
    return get_available_models()

# Initialisation de la session
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Salut ! Comment puis-je t'aider aujourd'hui ?"}
    ]

if "selected_model" not in st.session_state:
    models = load_models()
    if models:
        st.session_state.selected_model = (
            "llama-3.3-70b-versatile" if "llama-3.3-70b-versatile" in models else models[0]
        )

# Barre latérale (Sidebar) simplifiée
with st.sidebar:
    st.header("Configuration")
    
    models = load_models()
    if not models:
        st.error("Aucun modèle disponible.")
        st.stop()

    st.session_state.selected_model = st.selectbox(
        "Modèle utilisé",
        options=models,
        index=models.index(st.session_state.selected_model) 
        if st.session_state.selected_model in models else 0,
    )

    st.divider()

    if st.button("🗑️ Vider la conversation", use_container_width=True):
        st.session_state.messages = [
            {"role": "assistant", "content": "Salut ! Comment puis-je t'aider aujourd'hui ?"}
        ]
        st.rerun()

# Affichage de l'historique
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Zone de saisie
if prompt := st.chat_input("Écris ton message ici..."):
    # Ajouter le message utilisateur
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Générer la réponse
    with st.chat_message("assistant"):
        with st.spinner("Réflexion en cours..."):
            response_text = ask_llm(
                messages=cast(list[ChatCompletionMessageParam], st.session_state.messages),
                model=st.session_state.selected_model,
            )
            st.markdown(response_text)

    # Sauvegarder la réponse de l'assistant
    st.session_state.messages.append({"role": "assistant", "content": response_text})