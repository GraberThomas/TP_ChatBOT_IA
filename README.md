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
├── cli.py                  # Point d'entrée Terminal : Version légère pour exécution en ligne de commande
├── pyproject.toml          # Gestionnaire de dépendances (uv) et métadonnées du package
└── README.md               # Documentation technique
```

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
