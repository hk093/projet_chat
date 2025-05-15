# Chatbot BID Consulting

Un chatbot intelligent spécialisé dans le Big Data, l'IA, le Machine Learning et le Marketing Digital, développé avec Streamlit et l'API Groq.

## 🌟 Fonctionnalités Principales

- Interface utilisateur moderne et professionnelle
- Support multilingue (Français, Anglais, Espagnol)
- Réponses intelligentes basées sur l'IA via l'API Groq
- Système de capture de leads intégré
- Historique des conversations
- Notification par email des nouveaux leads
- Interface popup élégante
- Reconnaissance vocale pour interagir avec le chatbot

## 📚 Documentation Détaillée des Fonctions

### 1. Classe Principale (`main.py`)

La classe `ChatbotApp` gère l'ensemble des fonctionnalités du chatbot :

- `__init__()` : Initialise l'application et ses configurations
- `setup_page()` : Configure la page Streamlit
- `initialize_session()` : Initialise les variables de session
- `apply_custom_css()` : Applique le CSS personnalisé
- `create_ui()` : Crée l'interface utilisateur
- `detect_language()` : Détecte la langue du texte
- `is_relevant_question()` : Vérifie si la question est liée aux domaines autorisés
- `chat_with_groq()` : Communique avec l'API Groq
- `send_lead_email()` : Envoie un email avec les informations du lead
- `load_memory()` : Charge l'historique des conversations
- `save_memory()` : Sauvegarde l'historique des conversations
- `get_user_id()` : Génère un identifiant unique pour la session
- `manage_memory()` : Gère la longueur de l'historique des conversations

### 2. Interface HTML (`chatbot.html`)

L'interface HTML du chatbot offre :

- Un bouton flottant pour ouvrir le chatbot
- Une fenêtre popup élégante
- Un design responsive
- Des animations fluides
- Un support pour la reconnaissance vocale

### 3. Gestion de l'API Groq (intégrée dans `main.py`)

```python
def chat_with_groq(self, messages):
    """
    Communique avec l'API Groq pour obtenir des réponses.
    Args:
        messages (list): Liste des messages de la conversation
    Returns:
        str: Réponse de l'API Groq
    """
```

### 4. Gestion de la Mémoire (intégrée dans `main.py`)

```python
def load_memory(self):
    """
    Charge l'historique des conversations depuis le fichier JSON.
    Returns:
        dict: Historique des conversations
    """
```

```python
def save_memory(self, user_id, conversation):
    """
    Sauvegarde l'historique des conversations.
    Args:
        user_id (str): Identifiant unique de l'utilisateur
        conversation (list): Messages à sauvegarder
    """
```

```python
def manage_memory(self, messages):
    """
    Gère la taille de l'historique des conversations.
    Args:
        messages (list): Liste des messages
    Returns:
        list: Messages filtrés
    """
```

### 5. Configuration

```python
# Variables de Configuration dans la classe ChatbotApp
self.GROQ_API_KEY = "votre_clé_api"  # Clé API Groq
self.GROQ_CHAT_URL = "https://api.groq.com/openai/v1/chat/completions"
self.GROQ_MODEL = "llama-3.3-70b-versatile"  # Modèle IA utilisé
self.MEMORY_FILE = "chat_memory.json"  # Fichier de stockage des conversations
self.MAX_MESSAGES = 20  # Nombre maximum de messages en mémoire
```

## 🔍 Domaines de Connaissances du Chatbot

Le chatbot est spécialisé dans les domaines suivants :

### Big Data
- Hadoop
- Spark
- Data Lake
- Data Warehouse
- NoSQL

### Intelligence Artificielle
- Machine Learning
- Deep Learning
- Réseaux de Neurones
- NLP
- Éthique de l'IA

### Marketing Digital
- SEO/SEM
- Analytics
- Référencement
- Marketing Digital

### Business Intelligence
- Tableau
- Power BI
- Dashboards
- Data Mining
- Statistiques

## 🛠️ Fonctionnalités Techniques

### Système de Détection de Langue
- Détection automatique du français, anglais et espagnol
- Adaptation des réponses à la langue détectée
- Messages d'erreur localisés

### Système de Vérification de Pertinence
- Liste de mots-clés par domaine
- Vérification de la pertinence des questions
- Réponses adaptées pour les questions hors sujet

### Système de Capture de Leads
- Déclenchement après 3 questions
- Validation des données
- Stockage sécurisé
- Notifications email

### Interface Utilisateur
- Mode popup responsive
- Animations fluides
- Adaptation au thème
- Gestion des erreurs

## 🔧 Configuration Avancée

### Configuration Email SMTP
```python
SMTP_CONFIG = {
    "server": "smtp.gmail.com",
    "port": 465,
    "sender": "votre_email@gmail.com",
    "password": "votre_mot_de_passe_app",
    "recipient": "destinataire@email.com"
}
```

### Configuration de la Mémoire
```python
MEMORY_CONFIG = {
    "file": "chat_memory.json",
    "max_messages": 20,
    "leads_file": "leads.json"
}
```



## 📞 Support et Contact

Pour toute question technique ou assistance :
- Email : [votre_email@example.com]
- Issues GitHub : [lien_vers_issues]

## 🔒 Sécurité et Confidentialité

- Stockage sécurisé des clés API
- Protection des données utilisateur
- Validation des entrées
- Gestion sécurisée des emails

## 🤝 Contribution

Les contributions sont les bienvenues ! Voir CONTRIBUTING.md pour les détails.

## 📝 License

Ce projet est sous licence MIT. Voir LICENSE pour plus de détails.

## 📁 Structure du Projet

```
chatbot_site/
├── main.py            # Application principale avec classe ChatbotApp (tout-en-un)
├── chatbot.html       # Interface HTML du chatbot
├── leads.json         # Stockage des leads
├── chat_memory.json   # Historique des conversations
├── requirements.txt   # Dépendances du projet
└── README.md          # Documentation
```

## 🚀 Installation et Démarrage

1. Cloner le dépôt
2. Installer les dépendances :
   ```
   pip install -r requirements.txt
   ```
3. Lancer l'application :
   ```
   streamlit run main.py
   ```

## 🔧 Personnalisation

### Modifier l'apparence

Le design du chatbot peut être personnalisé en modifiant :

1. Le CSS dans la méthode `apply_custom_css()` de `main.py`
2. Le CSS dans le fichier `chatbot.html`

### Configurer l'API Groq

Les paramètres de l'API Groq peuvent être modifiés dans la classe `ChatbotApp` :

```python
self.GROQ_API_KEY = "votre_clé_api"
self.GROQ_MODEL = "modèle_souhaité"
```

## 📱 Intégration

Pour intégrer le chatbot dans un site web existant, incluez le fichier `chatbot.html` et modifiez l'URL Streamlit :

```javascript
const CONFIG = {
  streamlitURL: "https://votre-url-streamlit.com/?embedded=true",
  loadTimeout: 30000,
  retryDelay: 5000
};
```