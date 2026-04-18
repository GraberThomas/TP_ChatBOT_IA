import json
import time
from typing import cast
import streamlit as st
from openai.types.chat import ChatCompletionMessageParam
from src.chatbot.core import ask_llm, get_available_models, get_metrics
from streamlit_local_storage import LocalStorage

st.set_page_config(page_title="Chatbot Pro", page_icon="🤖", layout="wide")

# Initialize LocalStorage component
local_storage = LocalStorage()

# --- Configuration ---
LIMIT_HOUR = 20
LIMIT_DAY = 100

# --- State Synchronization Logic ---
def sync_to_local_storage():
    """Saves critical session state to LocalStorage."""
    if st.session_state.get("logged_in"):
        local_storage.setItem("chatbot_username", st.session_state.username, key="sync_user")
        chats_key = f"chatbot_chats_{st.session_state.username}"
        local_storage.setItem(chats_key, json.dumps(st.session_state.all_user_chats, ensure_ascii=False), key="sync_chats")
        rate_key = f"chatbot_rate_{st.session_state.username}"
        local_storage.setItem(rate_key, json.dumps(st.session_state.rate_timestamps), key="sync_rate")

def init_from_local_storage():
    """Initializes session state from LocalStorage values."""
    if "initialized" not in st.session_state:
        username = local_storage.getItem("chatbot_username")
        if username:
            st.session_state.username = username
            st.session_state.logged_in = True
            chats_key = f"chatbot_chats_{username}"
            raw_chats = local_storage.getItem(chats_key)
            st.session_state.all_user_chats = json.loads(raw_chats) if raw_chats else {}
            rate_key = f"chatbot_rate_{username}"
            raw_rate = local_storage.getItem(rate_key)
            st.session_state.rate_timestamps = json.loads(raw_rate) if raw_rate else []
        else:
            st.session_state.username = ""
            st.session_state.logged_in = False
            st.session_state.all_user_chats = {}
            st.session_state.rate_timestamps = []
        st.session_state.initialized = True

init_from_local_storage()

# --- Rate Limit Helpers ---
def get_rate_metrics():
    now = time.time()
    st.session_state.rate_timestamps = [t for t in st.session_state.rate_timestamps if now - t < 86400]
    used_h = len([t for t in st.session_state.rate_timestamps if now - t < 3600])
    used_d = len(st.session_state.rate_timestamps)
    return used_h, used_d

def check_rate_limits():
    used_h, used_d = get_rate_metrics()
    if used_h >= LIMIT_HOUR: return False, f"Limite horaire atteinte ({LIMIT_HOUR} req/h)."
    if used_d >= LIMIT_DAY: return False, f"Limite journalière atteinte ({LIMIT_DAY} req/j)."
    return True, ""

# --- Chat Management ---
def get_chat_list():
    chats = []
    for chat_id, messages in st.session_state.all_user_chats.items():
        title = "Nouveau chat"
        for msg in messages:
            if msg["role"] == "user":
                title = msg["content"][:40] + ("..." if len(msg["content"]) > 40 else "")
                break
        chats.append({"id": chat_id, "title": title, "timestamp": int(chat_id)})
    chats.sort(key=lambda x: x['timestamp'], reverse=True)
    return chats

def get_time_label(ts):
    now = time.time()
    diff = now - ts
    if diff < 86400: return "Aujourd'hui"
    if diff < 172800: return "Hier"
    if diff < 604800: return "7 derniers jours"
    return "Plus ancien"

# --- Login Screen ---
if not st.session_state.logged_in:
    st.title("🤖 Chatbot Pro")
    with st.popover("🔑 Connexion", use_container_width=True):
        user_input = st.text_input("Pseudo")
        if st.button("Valider", use_container_width=True):
            if user_input.strip():
                st.session_state.username = user_input.strip()
                st.session_state.logged_in = True
                st.session_state.initialized = False
                sync_to_local_storage()
                st.rerun()
    st.info("Veuillez vous connecter pour démarrer.")
    st.stop()

username = st.session_state.username

# --- Sidebar ---
with st.sidebar:
    c_user, c_logout = st.columns([2, 1], vertical_alignment="center")
    c_user.write(f"👤 **{username}**")
    if c_logout.button("Quitter", type="tertiary", help="Déconnexion"):
        local_storage.deleteItem("chatbot_username")
        st.session_state.logged_in = False
        st.rerun()
    
    st.divider()

    if st.button("＋  Nouveau Chat", use_container_width=True, type="primary"):
        new_id = str(int(time.time()))
        st.session_state.current_chat_id = new_id
        st.session_state.all_user_chats[new_id] = [{"role": "assistant", "content": "Nouvelle discussion !"}]
        sync_to_local_storage()
        st.rerun()

    user_chats = get_chat_list()
    if "current_chat_id" not in st.session_state or st.session_state.current_chat_id not in st.session_state.all_user_chats:
        if user_chats: st.session_state.current_chat_id = user_chats[0]['id']
        else:
            new_id = str(int(time.time()))
            st.session_state.current_chat_id = new_id
            st.session_state.all_user_chats[new_id] = [{"role": "assistant", "content": "Comment puis-je t'aider ?"}]
            sync_to_local_storage()

    current_label = ""
    for chat in user_chats:
        time_label = get_time_label(chat['timestamp'])
        if time_label != current_label:
            st.caption(f"{time_label}")
            current_label = time_label
        
        c1, c2 = st.columns([6, 1], vertical_alignment="center")
        is_active = chat['id'] == st.session_state.current_chat_id
        if c1.button(chat['title'], key=f"btn_{chat['id']}", use_container_width=True, type="secondary" if is_active else "tertiary"):
            st.session_state.current_chat_id = chat['id']
            st.rerun()
        if c2.button("🗑️", key=f"del_{chat['id']}", type="tertiary", help="Supprimer"):
            del st.session_state.all_user_chats[chat['id']]
            if st.session_state.current_chat_id == chat['id']: st.session_state.current_chat_id = None
            sync_to_local_storage()
            st.rerun()

    st.divider()
    with st.expander("📊 Métriques & Limites"):
        m = get_metrics()
        used_h, used_d = get_rate_metrics()
        st.write("**Session (Local)**")
        st.write(f"⏱️ Heure : {used_h}/{LIMIT_HOUR}")
        st.progress(used_h / LIMIT_HOUR)
        st.write(f"📅 Jour : {used_d}/{LIMIT_DAY}")
        st.progress(used_d / LIMIT_DAY)
        st.divider()
        st.write("**Serveur (Global)**")
        st.write(f"🚀 Total Req : {m['total_requests']}")
        st.write(f"❌ Erreurs : {m['total_errors']}")
        st.write(f"⏱️ Temps moy : {m['avg_response_time']:.2f}s")
        st.write(f"🚨 Taux erreur : {m['error_rate']:.1f}%")

    st.divider()
    chat_json = json.dumps(st.session_state.all_user_chats.get(st.session_state.current_chat_id, []), indent=2, ensure_ascii=False)
    st.download_button("📥 Exporter le chat (JSON)", chat_json, f"chat_{st.session_state.current_chat_id}.json", "application/json", use_container_width=True)

# --- Chat Header ---
st.divider()
provider = "groq"
h1, h2, h3 = st.columns([4, 2, 2], vertical_alignment="center")

with h1:
    @st.cache_data(ttl=300)
    def load_models(p): return get_available_models(p)
    models = load_models(provider)
    def_idx = models.index("llama-3.1-8b-instant") if models and "llama-3.1-8b-instant" in models else 0
    sel_mod = st.selectbox("Model", options=models, index=def_idx, label_visibility="collapsed") if models else "n/a"

with h2:
    with st.popover("🌡️ Temp", use_container_width=True):
        mode = st.radio("Mode", options=["Fixe", "Normal", "Créatif", "Perso"], index=1)
        temp = 0.0 if mode=="Fixe" else 0.5 if mode=="Normal" else 1.0 if mode=="Créatif" else st.slider("Val", 0.0, 1.0, 0.7)

with h3:
    if st.button("👍 Satisfait", use_container_width=True, help="Simuler une métrique business"):
        st.toast("Merci pour votre retour !", icon="🙏")

# --- Chat Display ---
current_messages = st.session_state.all_user_chats.get(st.session_state.current_chat_id, [])
for message in current_messages:
    with st.chat_message(message["role"]): st.markdown(message["content"])

# --- Chat Input ---
if prompt := st.chat_input("Votre message ici..."):
    allowed, msg = check_rate_limits()
    if not allowed: st.error(msg)
    else:
        current_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("L'IA réfléchit..."):
                try:
                    res = ask_llm(messages=cast(list[ChatCompletionMessageParam], current_messages), 
                                  model=sel_mod, temperature=temp, provider=provider)
                    st.markdown(res)
                    current_messages.append({"role": "assistant", "content": res})
                    st.session_state.rate_timestamps.append(time.time())
                    st.session_state.all_user_chats[st.session_state.current_chat_id] = current_messages
                    sync_to_local_storage()
                    st.rerun()
                except Exception as e:
                    st.error(str(e))

sync_to_local_storage()
