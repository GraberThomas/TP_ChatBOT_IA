# 🤖 Chatbot IA Robuste - Étude de Cas (Master 2 Learn IT)

Ce projet présente une version industrialisée d'un chatbot basé sur l'API Groq. L'objectif était de transformer un prototype fonctionnel en une application robuste, capable de gérer des contraintes de production (erreurs, limites, monitoring) tout en offrant une expérience utilisateur moderne.

## 🏗️ Architecture et Structure

Le projet adopte une structure professionnelle dite "src layout" pour séparer la logique métier de l'interface utilisateur.

```text
.
├── src/
│   └── chatbot/
│       ├── __init__.py
│       └── core.py          # Cœur logique : Appels API, gestion des métriques techniques et logging
├── logs/
│   └── chatbot.log         # Fichier de logs persistant pour l'audit et le monitoring
├── app.py                  # Point d'entrée Web (Streamlit) : Gestion de l'UI et persistance localStorage
├── pyproject.toml          # Gestionnaire de dépendances (uv) et métadonnées du package
├── requirements.txt        # Dépendances figées (utilisé par Streamlit Cloud / pip)
└── README.md               # Documentation technique
```

---

## ⚙️ Installation et Lancement

### 1. Prérequis
*   **Python 3.12** (voir `.python-version`).
*   Une **clé API Groq** (gratuite) à récupérer sur [console.groq.com/keys](https://console.groq.com/keys).

### 2. Récupération du projet
```bash
git clone <url-du-depot>
cd TP_ChatBOT_IA
```

### 3. Installation des dépendances

#### Option A — avec `uv` (recommandé)
[`uv`](https://docs.astral.sh/uv/) crée automatiquement l'environnement virtuel et installe les versions figées via `uv.lock` :
```bash
uv sync
```

#### Option B — avec `pip`
```bash
python -m venv .venv
source .venv/bin/activate      # Windows : .venv\Scripts\activate
pip install -r requirements.txt
```

### 4. Configuration de la clé API
L'application lit la clé depuis les **secrets Streamlit** en priorité, avec repli sur les **variables d'environnement**.

**Méthode recommandée (secrets Streamlit)** — créez le fichier `.streamlit/secrets.toml` (déjà ignoré par Git) :
```toml
GROQ_API_KEY = "gsk_votre_cle_ici"
```

**Alternative (variable d'environnement)** :
```bash
export GROQ_API_KEY="gsk_votre_cle_ici"   # Windows : set GROQ_API_KEY=...
```

### 5. Lancement de l'application Web (Streamlit)
```bash
uv run streamlit run app.py      # avec uv
# ou, avec l'environnement pip activé :
streamlit run app.py
```
L'interface est alors accessible sur [http://localhost:8501](http://localhost:8501).

> **Déploiement sur Streamlit Cloud** : renseignez `GROQ_API_KEY` dans *Settings → Secrets* de l'application ; `requirements.txt` est utilisé automatiquement pour l'installation.

---

## ✅ Fonctionnalités Implémentées

### Qualité et UX
*   **Interface "GPT-Style"** : Historique des conversations groupé chronologiquement (Aujourd'hui, Hier, etc.).
*   **Multi-Utilisateurs & Multi-Chats** : Gestion de plusieurs sessions par utilisateur avec possibilité de créer, renommer et supprimer des fils de discussion.
*   **Persistance Totale** : Utilisation du `localStorage` navigateur pour sauvegarder les conversations et l'identité utilisateur sans base de données serveur.
*   **Exportation** : Bouton d'export JSON pour récupérer l'historique d'un chat spécifique.

### Robustesse et Technique
*   **Gestion Avancée des Erreurs** : Interception des erreurs API, timeouts (fixés à 30s) et gestion des réponses vides pour éviter tout crash de l'UI.
*   **Rate Limiting** : Implémentation de quotas stricts (20 req/h et 100 req/j) par utilisateur pour protéger les coûts et l'infrastructure.
*   **Monitoring Intégré** : Tableau de bord technique affichant le volume de requêtes, le taux d'erreur et la latence moyenne.

---

## 🛠️ Choix Techniques et Justifications

### 1. Gestion de la Température
Nous avons implémenté quatre modes prédéfinis :
*   **Fixe (0.0)** : Idéal pour l'extraction de données ou le code (réponses déterministes).
*   **Normal (0.5)** : Recommandé pour la discussion générale (équilibre précision/fluidité).
*   **Créatif (1.0)** : Pour la rédaction ou le brainstorming (variabilité maximale).
*   **Perso** : Un slider de précision pour les utilisateurs experts.

### 2. Gestion des Erreurs
Le système utilise un pattern de "Graceful Degradation". En cas d'erreur API (ex: clé invalide ou limite atteinte), l'utilisateur reçoit une notification `st.error` explicite plutôt qu'une erreur Python brute. Un timeout de 30 secondes est imposé pour garantir que l'interface ne reste pas bloquée indéfiniment.

### 3. Persistance (localStorage vs SQLite)
Pour ce TP, le choix du `localStorage` a été privilégié pour permettre un déploiement sur **Streamlit Cloud** sans gestion de volume disque persistant. Cela garantit que chaque utilisateur retrouve ses données sur son propre navigateur sans complexité de backend.

---

## ⚠️ Limites du Travail Actuel
*   **Sécurité des Identifiants** : Le système multi-utilisateur est basé sur un pseudo simple sans mot de passe (pas d'authentification réelle).
*   **Taille de l'Historique** : Le `localStorage` est limité en taille (environ 5MB). Pour des milliers de messages, une base de données SQL serait nécessaire.
*   **Streaming** : Les réponses sont affichées d'un bloc au lieu d'être streamées mot par mot (token streaming).

## 🚀 Pistes d'Amélioration
1.  **RAG (Retrieval Augmented Generation)** : Connecter le chatbot à des documents PDF/Textes locaux.
2.  **Authentification OAuth** : Intégrer Google ou GitHub Login pour une vraie gestion multi-utilisateur sécurisée.
3.  **Backend SQL** : Migrer la persistance vers PostgreSQL pour permettre l'accès à l'historique sur différents appareils.

---

## 📊 Métriques et Logging

### Exemple de Logs Techniques (`logs/chatbot.log`) :
Le système enregistre chaque événement critique pour permettre un audit post-mortem :

```text
2026-04-18 14:20:05 - Chatbot - INFO - Requête réussie: model=llama-3.1-8b-instant, temp=0.5, time=1.42s
2026-04-18 14:21:12 - Chatbot - WARNING - Limite horaire atteinte pour l'utilisateur: Thomas
2026-04-18 14:22:00 - Chatbot - ERROR - Erreur API Groq: Error code: 401 - Invalid API Key
```

### Métriques Business (Simulation)
Le bouton "👍 Satisfait" permet de simuler la collecte de données de satisfaction utilisateur, alimentant ainsi le monitoring business demandé dans le cahier des charges.
