import streamlit as st
import streamlit.components.v1 as components
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
import os
from langdetect import detect
from datetime import datetime, timedelta
import time
import requests
import functools
import threading

# Classe principale du chatbot
class ChatbotApp:
    def __init__(self):
        # Configuration
        self.GROQ_API_KEY = "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"
        self.GROQ_CHAT_URL = "https://api.groq.com/openai/v1/chat/completions"
        self.GROQ_MODEL = "llama-3.3-70b-versatile"
        self.MEMORY_FILE = "chat_memory.json"
        self.MAX_MESSAGES = 20
        self.LEAD_HISTORY_FILE = "lead_history.json"

        # Configuration SMTP
        self.SMTP_SERVER = "smtp.gmail.com"
        self.SMTP_PORT = 465
        self.SENDER_EMAIL = "chedymiled@gmail.com"
        self.SENDER_PASSWORD = "jdhq ltrb lnez rbyq"
        self.DEFAULT_SENDER_NAME = "BID Consulting"
        self.RECIPIENT_EMAIL = "houssemeddinekamkoum@gmail.com"

        # Cache pour les réponses
        self.response_cache = {}
        self.memory_save_needed = False
        self.last_memory_save = datetime.now()
        self.save_interval = timedelta(minutes=2)  # Sauvegarder toutes les 2 minutes max

        # Ensemble de mots-clés pour la vérification de pertinence (plus rapide qu'une liste)
        self.relevant_keywords = {
            # Mots-clés techniques
            "big data", "hadoop", "spark", "data lake", "data warehouse", "nosql",
            "ai", "artificial intelligence", "intelligence artificielle", "ia", "machine learning", "ml",
            "deep learning", "apprentissage profond", "neural network", "réseau de neurones",
            "marketing", "seo", "sem", "référencement", "analytics", "google analytics",
            "bi", "business intelligence", "tableau", "power bi", "dashboard", "tableau de bord",
            "data mining", "fouille de données", "clustering", "classification", "regression",
            "nlp", "natural language processing", "traitement du langage naturel",
            "ai ethics", "éthique de l'ia", "responsible ai", "ia responsable",
            "data science", "science des données", "statistiques", "statistics",

            # Mots-clés spécifiques à BID Consulting
            "bid", "bid consulting", "bidata", "bidata consulting", "bid data",
            "service", "services", "horaire", "horaires", "contact", "adresse",
            "téléphone", "telephone", "email", "mail", "site", "site web", "website",
            "ras jebel", "tunisie", "tunisia", "bourguiba", "habib bourguiba",
            "consulting", "consultant", "consultation", "conseil", "conseiller",
            "digital marketing", "marketing digital", "social media", "réseaux sociaux",
            "seo", "sem", "référencement", "referencement", "publicité", "publicite", "ads",
            "stage", "internship", "formation", "training"
        }

        # Informations sur BID Consulting
        self.bid_info = {
            "general": {
                "name": "BID Consulting",
                "slogan": "Vision to Decision",
                "website": "https://bidata-consulting.tn/",
                "description": "BID Consulting est une entreprise spécialisée dans les solutions de Business Intelligence, d'Intelligence Artificielle et de Marketing Digital."
            },
            "hours": {
                "fr": "Lundi à Samedi : 8h00 - 18h00",
                "en": "Monday to Saturday: 8:00AM - 6:00PM"
            },
            "contact": {
                "phone": "+216 95 63 47 91",
                "email": "contact@bidata-consulting.tn",
                "address": "Av. Habib Bourguiba (en face de l'hôpital), 7070, Ras Jebel - Tunisie"
            },
            "services": {
                "bi": {
                    "title": "Business Intelligence Solutions",
                    "description": "Transformation des données en avantage stratégique",
                    "features": [
                        "Data Warehousing & Management",
                        "Advanced Analytics & Reporting",
                        "Data Governance & Security",
                        "Real-time Dashboards",
                        "System Integration"
                    ]
                },
                "ai": {
                    "title": "AI Solutions",
                    "description": "Transformation des données en actions intelligentes",
                    "features": [
                        "Generative AI Implementation",
                        "Machine Learning Models",
                        "Natural Language Processing",
                        "Computer Vision Solutions",
                        "AI Process Automation"
                    ]
                },
                "marketing": {
                    "title": "Digital Marketing",
                    "description": "Amplification de votre présence en ligne et de votre taux de conversion",
                    "features": [
                        "SEO & Content Strategy",
                        "Targeted Advertising Campaigns",
                        "Social Media Management",
                        "Analytics & Performance Tracking",
                        "Email Marketing Automation"
                    ]
                }
            }
        }

        # Initialisation de l'application
        self.setup_page()
        self.initialize_session()
        self.apply_custom_css()
        self.create_ui()

    def setup_page(self):
        """Configuration de la page Streamlit"""
        st.set_page_config(
            page_title="BID Assistant",
            page_icon="https://i.postimg.cc/YjYPXYFm/logo.png",
            layout="wide"
        )

    def initialize_session(self):
        """Initialisation des variables de session"""
        # Initialiser la mémoire
        user_id = self.get_user_id()
        memory = self.load_memory()

        # Initialiser les messages
        if "messages" not in st.session_state:
            if user_id in memory and "conversation" in memory[user_id]:
                st.session_state.messages = memory[user_id]["conversation"]
            else:
                st.session_state.messages = [
                    {"role": "assistant", "content": "Bonjour ! Je suis l'assistant virtuel de BID Consulting. Je peux vous renseigner sur nos services, nos horaires, nos coordonnées ou répondre à vos questions sur le Big Data, l'IA et le Marketing Digital. Comment puis-je vous aider aujourd'hui ?"}
                ]

        # Initialiser le compteur de questions
        if "question_count" not in st.session_state:
            st.session_state.question_count = 0

        # Initialiser l'état du formulaire
        if "form_submitted" not in st.session_state:
            st.session_state.form_submitted = False

        # Initialiser l'état de la reconnaissance vocale
        if "voice_enabled" not in st.session_state:
            st.session_state.voice_enabled = False

    def apply_custom_css(self):
        """Appliquer le CSS personnalisé"""
        st.markdown("""
        <style>
        /* Style général */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }

        body {
            background: #f5f6fa;
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: flex-end;
            padding: 16px;
        }

        .main .block-container {
            padding: 0 !important;
            max-width: 480px !important;
            margin: 0 auto;
            background: #ffffff;
            border-radius: 20px;
            box-shadow: 0 8px 30px rgba(0, 0, 0, 0.1);
            overflow: hidden;
            display: flex;
            flex-direction: column;
            height: 80vh;
            max-height: 680px;
        }

        /* En-tête personnalisé */
        .header-container {
            background: linear-gradient(135deg, #7b3fe4, #4b1d9e);
            color: #ffffff;
            padding: 14px 20px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            font-size: 16px;
            font-weight: 600;
        }

        .header-container .status {
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .header-container .status::before {
            content: '';
            width: 8px;
            height: 8px;
            background: #34c759;
            border-radius: 50%;
        }

        /* Style pour les messages du chat */
        .stChatContainer {
            padding: 0 !important;
            height: calc(100% - 60px) !important;
        }

        .stChatMessageContainer {
            padding: 20px !important;
            overflow-y: auto !important;
            background: #fafbff !important;
            scroll-behavior: smooth !important;
            height: 100% !important;
        }

        .stChatMessage {
            max-width: 75% !important;
            padding: 12px 16px !important;
            border-radius: 16px !important;
            font-size: 14px !important;
            line-height: 1.5 !important;
            animation: slideIn 0.3s ease !important;
            position: relative !important;
            margin-bottom: 16px !important;
            box-shadow: none !important;
        }

        @keyframes slideIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        /* Style pour les messages de l'assistant */
        .stChatMessage[data-testid="stChatMessage-ASSISTANT"] {
            background: #e8e9ff !important;
            color: #1f2a44 !important;
            align-self: flex-start !important;
            border-bottom-left-radius: 4px !important;
            margin-right: auto !important;
            margin-left: 0 !important;
            position: relative !important;
        }

        .stChatMessage[data-testid="stChatMessage-ASSISTANT"]::before {
            content: 'IA';
            position: absolute;
            top: -16px;
            left: 12px;
            font-size: 10px;
            color: #7b3fe4;
            font-weight: 600;
        }

        /* Style pour les messages de l'utilisateur */
        .stChatMessage[data-testid="stChatMessage-USER"] {
            background: #7b3fe4 !important;
            color: #ffffff !important;
            align-self: flex-end !important;
            border-bottom-right-radius: 4px !important;
            margin-left: auto !important;
            margin-right: 0 !important;
        }

        /* Style pour le champ de saisie */
        .stChatInputContainer {
            display: flex !important;
            padding: 16px !important;
            background: #ffffff !important;
            border-top: 1px solid #ebedf0 !important;
            gap: 12px !important;
            align-items: center !important;
            border-radius: 0 !important;
            box-shadow: none !important;
        }

        /* Style pour le champ de texte */
        .stChatInput {
            flex: 1 !important;
            padding: 12px 16px !important;
            border: none !important;
            background: #f1f2f6 !important;
            border-radius: 24px !important;
            font-size: 14px !important;
            outline: none !important;
            transition: background 0.2s ease !important;
        }

        .stChatInput:focus {
            background: #e8e9ff !important;
            border: none !important;
            box-shadow: none !important;
        }

        /* Style pour le bouton d'envoi */
        .stChatInputContainer button {
            background: #7b3fe4 !important;
            border: none !important;
            border-radius: 24px !important;
            color: #ffffff !important;
            padding: 12px !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            cursor: pointer !important;
            transition: background 0.2s ease !important;
            box-shadow: none !important;
            width: 44px !important;
            height: 44px !important;
        }

        .stChatInputContainer button:hover {
            background: #6a35c7 !important;
            transform: none !important;
        }

        /* Personnalisation de l'icône du bouton d'envoi */
        .stChatInputContainer button svg {
            width: 20px !important;
            height: 20px !important;
        }

        /* Style pour le bouton du microphone */
        #voice-button {
            background: #7b3fe4;
            border: none;
            border-radius: 24px;
            width: 44px;
            height: 44px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            cursor: pointer;
            transition: background 0.2s ease;
            position: absolute;
            right: 70px;
            bottom: 16px;
            z-index: 100;
            box-shadow: 0 2px 8px rgba(123, 63, 228, 0.3);
        }

        #voice-button:hover {
            background: #6a35c7;
        }

        #voice-button.active {
            background: #ff3b3b;
            animation: pulse 1.5s infinite;
            box-shadow: 0 2px 8px rgba(255, 59, 59, 0.3);
        }

        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.1); }
            100% { transform: scale(1); }
        }

        /* Masquer certains éléments Streamlit */
        .stDeployButton, .stToolbar, .stDecoration, header {
            display: none !important;
        }

        /* Style pour le formulaire */
        .form-container {
            background: white;
            border-radius: 16px;
            padding: 20px;
            margin: 20px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
        }

        .form-title {
            color: #7b3fe4;
            font-size: 18px;
            font-weight: 600;
            margin-bottom: 20px;
            text-align: center;
        }

        /* Style pour les champs du formulaire */
        .stTextInput > div > div > input {
            border: 1px solid #e0e0e0;
            border-radius: 12px;
            padding: 10px 15px;
            font-size: 14px;
            transition: all 0.2s ease;
        }

        .stTextInput > div > div > input:focus {
            border-color: #7b3fe4;
            box-shadow: 0 0 0 1px #7b3fe4;
        }

        /* Style pour le bouton du formulaire */
        .stButton > button {
            background: #7b3fe4;
            color: white;
            border: none;
            border-radius: 12px;
            padding: 10px 20px;
            font-weight: 600;
            transition: background 0.2s ease;
            width: 100%;
        }

        .stButton > button:hover {
            background: #6a35c7;
        }

        /* Style pour le footer */
        .custom-footer {
            text-align: center;
            padding: 10px;
            color: #888;
            font-size: 12px;
            border-top: 1px solid #ebedf0;
        }
        </style>
        """, unsafe_allow_html=True)

    def create_ui(self):
        """Créer l'interface utilisateur"""
        # Ajouter le script pour la reconnaissance vocale
        components.html("""
        <script>
        // Fonction pour la reconnaissance vocale
        function setupSpeechRecognition() {
            if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
                console.error('La reconnaissance vocale n\'est pas prise en charge par ce navigateur.');
                return;
            }

            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            const recognition = new SpeechRecognition();
            recognition.continuous = false;
            recognition.interimResults = true;
            recognition.lang = 'fr-FR'; // Langue par défaut

            let finalTranscript = '';

            recognition.onstart = function() {
                console.log('La reconnaissance vocale est activée');
                document.getElementById('voice-button').classList.add('active');
            };

            recognition.onend = function() {
                console.log('La reconnaissance vocale est désactivée');
                document.getElementById('voice-button').classList.remove('active');

                if (finalTranscript) {
                    // Envoyer le texte à Streamlit
                    const textArea = document.querySelector('.stChatInput textarea');
                    if (textArea) {
                        textArea.value = finalTranscript;
                        textArea.dispatchEvent(new Event('input', { bubbles: true }));

                        // Simuler l'appui sur Entrée pour envoyer le message
                        setTimeout(() => {
                            textArea.dispatchEvent(new KeyboardEvent('keydown', {
                                key: 'Enter',
                                code: 'Enter',
                                keyCode: 13,
                                which: 13,
                                bubbles: true
                            }));
                        }, 500);
                    }
                }

                finalTranscript = '';
            };

            recognition.onresult = function(event) {
                let interimTranscript = '';

                for (let i = event.resultIndex; i < event.results.length; ++i) {
                    if (event.results[i].isFinal) {
                        finalTranscript += event.results[i][0].transcript;
                    } else {
                        interimTranscript += event.results[i][0].transcript;
                    }
                }

                console.log('Transcription finale:', finalTranscript);
                console.log('Transcription intérimaire:', interimTranscript);

                // Afficher la transcription en cours dans le champ de texte
                const textArea = document.querySelector('.stChatInput textarea');
                if (textArea) {
                    textArea.value = finalTranscript || interimTranscript;
                    textArea.dispatchEvent(new Event('input', { bubbles: true }));
                }
            };

            recognition.onerror = function(event) {
                console.error('Erreur de reconnaissance vocale:', event.error);
                document.getElementById('voice-button').classList.remove('active');
            };

            // Ajouter le bouton du microphone
            const chatInput = document.querySelector('.stChatInputContainer');
            if (chatInput && !document.getElementById('voice-button')) {
                const voiceButton = document.createElement('button');
                voiceButton.id = 'voice-button';
                voiceButton.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16"><path d="M8 1a3 3 0 0 0-3 3v4a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/><path d="M12.5 10a.5.5 0 0 1-.5.5H4a.5.5 0 0 1 0-1h8a.5.5 0 0 1 .5.5z"/><path d="M8 0a4 4 0 0 0-4 4v4a4 4 0 0 0 8 0V4a4 4 0 0 0-4-4zm0 1a3 3 0 0 1 3 3v4a3 3 0 0 1-6 0V4a3 3 0 0 1 3-3z"/><path d="M10.5 14.5V11h1a.5.5 0 0 0 .5-.5v-1a.5.5 0 0 0-.5-.5h-5a.5.5 0 0 0-.5.5v1a.5.5 0 0 0 .5.5h1v3.5a.5.5 0 0 0 .5.5h2a.5.5 0 0 0 .5-.5z"/></svg>';
                chatInput.appendChild(voiceButton);

                let isRecording = false;

                voiceButton.addEventListener('click', function() {
                    if (isRecording) {
                        recognition.stop();
                        isRecording = false;
                    } else {
                        recognition.start();
                        isRecording = true;
                    }
                });
            }
        }

        // Exécuter la configuration après le chargement de la page
        document.addEventListener('DOMContentLoaded', function() {
            // Attendre que Streamlit soit complètement chargé
            const checkInterval = setInterval(function() {
                if (document.querySelector('.stChatInputContainer')) {
                    clearInterval(checkInterval);
                    setupSpeechRecognition();
                }
            }, 300);
        });
        </script>
        """, height=0)

        # Ajouter l'en-tête personnalisé
        st.markdown("""
        <div class="header-container">
            <div class="status">
                <span>Assistant IA</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Afficher l'historique des messages
        with st.container():
            for msg in st.session_state.messages:
                st.chat_message(msg["role"]).write(msg["content"])

        # Afficher le formulaire après 3 questions si non soumis
        if st.session_state.question_count >= 3 and not st.session_state.form_submitted:
            with st.container():
                st.markdown('<div class="form-container">', unsafe_allow_html=True)
                st.markdown('<div class="form-title">Pour continuer notre conversation</div>', unsafe_allow_html=True)

                name = st.text_input("Nom", placeholder="Votre nom")
                email = st.text_input("Email", placeholder="votre@email.com")
                phone = st.text_input("Téléphone", placeholder="Votre numéro de téléphone")
                submit_button = st.button("Continuer", type="primary")

                if submit_button:
                    if name and email and phone:
                        # Enregistrer l'heure de soumission
                        st.session_state.form_submitted_at = datetime.now()
                        st.session_state.form_submitted = True

                        # Envoyer l'email ou sauvegarder les données
                        success, _ = self.send_lead_email(name, email, phone)

                        if success:
                            # Ajouter un message de confirmation dans le chat
                            st.session_state.messages.append({
                                "role": "assistant",
                                "content": f"Merci {name} pour vos informations ! Nous vous contacterons bientôt à {email}."
                            })

                            # Sauvegarder la conversation mise à jour
                            self.save_memory(self.get_user_id(), st.session_state.messages)

                            # Recharger la page pour afficher le message de confirmation
                            st.rerun()
                    else:
                        st.error("Veuillez remplir tous les champs")

                st.markdown('</div>', unsafe_allow_html=True)

        # Champ de saisie pour le chat
        if prompt := st.chat_input("Posez votre question..."):
            # Ajouter le message de l'utilisateur
            st.session_state.messages.append({"role": "user", "content": prompt})

            # Incrémenter le compteur de questions
            st.session_state.question_count += 1

            # Créer un placeholder pour l'indicateur de chargement
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                message_placeholder.markdown("⏳ *Je réfléchis...*")

            # Détecter la langue de la question (en arrière-plan pour ne pas bloquer l'interface)
            detected_lang = self.detect_language(prompt)

            # Vérifier si la question concerne BID Consulting
            if self.is_bid_question(prompt):
                # Obtenir une réponse spécifique à BID Consulting
                response = self.get_bid_response(prompt, detected_lang)
                print("Question sur BID détectée, réponse générée localement")
            # Vérifier si la question est pertinente pour l'IA
            elif self.is_relevant_question(prompt):
                # Obtenir la réponse de l'IA pour les questions pertinentes
                # Ajouter une instruction pour répondre dans la même langue que la question
                lang_instruction = {
                    "role": "system",
                    "content": f"Please respond in the same language as the user's question. The detected language is: {detected_lang}."
                }

                # Créer une copie des messages avec l'instruction de langue
                messages_with_lang = st.session_state.messages.copy()
                messages_with_lang.insert(0, lang_instruction)

                try:
                    # Essayer d'obtenir une réponse de l'API Groq
                    response = self.chat_with_groq(messages_with_lang)

                    # Vérifier si la réponse contient un message d'erreur
                    if "trouble connecting" in response or "error occurred" in response:
                        # Utiliser une réponse de secours en cas d'erreur
                        response = self.fallback_response(detected_lang)
                except Exception as e:
                    # En cas d'erreur, utiliser la réponse de secours
                    print(f"Erreur lors de l'appel à l'API Groq: {str(e)}")
                    response = self.fallback_response(detected_lang)
            else:
                # Réponse standard pour les questions non pertinentes dans la langue détectée
                response = self.get_not_relevant_message(detected_lang)

            # Supprimer l'indicateur de chargement
            message_placeholder.empty()

            # Ajouter la réponse de l'IA
            st.session_state.messages.append({"role": "assistant", "content": response})

            # Afficher la réponse
            st.chat_message("assistant").write(response)

            # Gérer la longueur de la conversation et sauvegarder
            st.session_state.messages = self.manage_memory(st.session_state.messages)

            # Sauvegarder la mémoire (optimisé pour réduire les écritures sur disque)
            self.save_memory(self.get_user_id(), st.session_state.messages)

            # Recharger la page si nous avons atteint 3 questions pour afficher le formulaire
            if st.session_state.question_count == 3 and not st.session_state.form_submitted:
                st.rerun()

        # Footer plus discret
        st.markdown("""
        <div class="custom-footer">
            © 2024 BID Consulting
        </div>
        """, unsafe_allow_html=True)

    # Méthodes utilitaires
    def detect_language(self, text):
        """Détecter la langue du texte"""
        try:
            lang = detect(text)
            return lang
        except:
            return 'fr'

    def is_relevant_question(self, question):
        """Vérifier si la question est liée aux domaines autorisés ou à BID Consulting"""
        # Utilisation de l'ensemble de mots-clés défini dans __init__ (plus rapide)
        question_lower = question.lower()

        # Vérification rapide pour les questions courtes ou génériques
        if len(question_lower) < 5:
            return True

        # Si la question est très longue, on la considère comme pertinente
        if len(question_lower) > 100:
            return True

        # Vérification par mots-clés
        for keyword in self.relevant_keywords:
            if keyword in question_lower:
                return True

        return False

    def is_bid_question(self, question):
        """Vérifier si la question concerne BID Consulting"""
        question_lower = question.lower()

        # Mots-clés spécifiques à BID Consulting
        bid_keywords = {
            "bid", "bidata", "consulting", "service", "services",
            "horaire", "horaires", "contact", "adresse", "téléphone",
            "telephone", "email", "mail", "site", "site web", "website",
            "ras jebel", "tunisie", "tunisia", "bourguiba"
        }

        # Vérification des mots-clés BID
        for keyword in bid_keywords:
            if keyword in question_lower:
                return True

        return False

    def get_bid_response(self, question, lang="fr"):
        """Générer une réponse concernant BID Consulting"""
        question_lower = question.lower()

        # Vérifier le type de question
        if any(word in question_lower for word in ["horaire", "heure", "ouvert", "fermé", "schedule", "hours", "open"]):
            if lang in ["fr", "fr-fr"]:
                return f"Les horaires d'ouverture de {self.bid_info['general']['name']} sont : {self.bid_info['hours']['fr']}."
            else:
                return f"The opening hours of {self.bid_info['general']['name']} are: {self.bid_info['hours']['en']}."

        elif any(word in question_lower for word in ["contact", "téléphone", "telephone", "appeler", "phone", "call"]):
            if lang in ["fr", "fr-fr"]:
                return f"Vous pouvez contacter {self.bid_info['general']['name']} par téléphone au {self.bid_info['contact']['phone']}."
            else:
                return f"You can contact {self.bid_info['general']['name']} by phone at {self.bid_info['contact']['phone']}."

        elif any(word in question_lower for word in ["email", "mail", "courriel", "e-mail"]):
            if lang in ["fr", "fr-fr"]:
                return f"L'adresse email de {self.bid_info['general']['name']} est : {self.bid_info['contact']['email']}."
            else:
                return f"The email address of {self.bid_info['general']['name']} is: {self.bid_info['contact']['email']}."

        elif any(word in question_lower for word in ["adresse", "où", "ou", "situé", "situe", "location", "where"]):
            if lang in ["fr", "fr-fr"]:
                return f"{self.bid_info['general']['name']} est situé à l'adresse suivante : {self.bid_info['contact']['address']}."
            else:
                return f"{self.bid_info['general']['name']} is located at: {self.bid_info['contact']['address']}."

        elif any(word in question_lower for word in ["service", "services", "offre", "propose", "offer", "provides"]):
            if lang in ["fr", "fr-fr"]:
                services = f"{self.bid_info['general']['name']} propose trois principaux services :\n\n"
                services += f"1. {self.bid_info['services']['bi']['title']} : {self.bid_info['services']['bi']['description']}\n"
                services += f"2. {self.bid_info['services']['ai']['title']} : {self.bid_info['services']['ai']['description']}\n"
                services += f"3. {self.bid_info['services']['marketing']['title']} : {self.bid_info['services']['marketing']['description']}\n\n"
                services += "Pour plus d'informations, visitez notre site web : " + self.bid_info['general']['website']
                return services
            else:
                services = f"{self.bid_info['general']['name']} offers three main services:\n\n"
                services += f"1. {self.bid_info['services']['bi']['title']}: {self.bid_info['services']['bi']['description']}\n"
                services += f"2. {self.bid_info['services']['ai']['title']}: {self.bid_info['services']['ai']['description']}\n"
                services += f"3. {self.bid_info['services']['marketing']['title']}: {self.bid_info['services']['marketing']['description']}\n\n"
                services += "For more information, visit our website: " + self.bid_info['general']['website']
                return services

        elif any(word in question_lower for word in ["bi", "business intelligence"]):
            if lang in ["fr", "fr-fr"]:
                bi_info = f"**{self.bid_info['services']['bi']['title']}** : {self.bid_info['services']['bi']['description']}\n\n"
                bi_info += "Services inclus :\n"
                for feature in self.bid_info['services']['bi']['features']:
                    bi_info += f"- {feature}\n"
                return bi_info
            else:
                bi_info = f"**{self.bid_info['services']['bi']['title']}**: {self.bid_info['services']['bi']['description']}\n\n"
                bi_info += "Included services:\n"
                for feature in self.bid_info['services']['bi']['features']:
                    bi_info += f"- {feature}\n"
                return bi_info

        elif any(word in question_lower for word in ["ai", "ia", "intelligence artificielle", "artificial intelligence"]):
            if lang in ["fr", "fr-fr"]:
                ai_info = f"**{self.bid_info['services']['ai']['title']}** : {self.bid_info['services']['ai']['description']}\n\n"
                ai_info += "Services inclus :\n"
                for feature in self.bid_info['services']['ai']['features']:
                    ai_info += f"- {feature}\n"
                return ai_info
            else:
                ai_info = f"**{self.bid_info['services']['ai']['title']}**: {self.bid_info['services']['ai']['description']}\n\n"
                ai_info += "Included services:\n"
                for feature in self.bid_info['services']['ai']['features']:
                    ai_info += f"- {feature}\n"
                return ai_info

        elif any(word in question_lower for word in ["marketing", "digital marketing", "marketing digital"]):
            if lang in ["fr", "fr-fr"]:
                marketing_info = f"**{self.bid_info['services']['marketing']['title']}** : {self.bid_info['services']['marketing']['description']}\n\n"
                marketing_info += "Services inclus :\n"
                for feature in self.bid_info['services']['marketing']['features']:
                    marketing_info += f"- {feature}\n"
                return marketing_info
            else:
                marketing_info = f"**{self.bid_info['services']['marketing']['title']}**: {self.bid_info['services']['marketing']['description']}\n\n"
                marketing_info += "Included services:\n"
                for feature in self.bid_info['services']['marketing']['features']:
                    marketing_info += f"- {feature}\n"
                return marketing_info

        elif any(word in question_lower for word in ["site", "site web", "website"]):
            if lang in ["fr", "fr-fr"]:
                return f"Vous pouvez visiter le site web de {self.bid_info['general']['name']} à l'adresse suivante : {self.bid_info['general']['website']}"
            else:
                return f"You can visit the {self.bid_info['general']['name']} website at: {self.bid_info['general']['website']}"

        # Réponse générale si aucune catégorie spécifique n'est détectée
        if lang in ["fr", "fr-fr"]:
            general_info = f"{self.bid_info['general']['name']} - {self.bid_info['general']['slogan']}\n\n"
            general_info += f"{self.bid_info['general']['description']}\n\n"
            general_info += f"Horaires : {self.bid_info['hours']['fr']}\n"
            general_info += f"Contact : {self.bid_info['contact']['phone']} / {self.bid_info['contact']['email']}\n"
            general_info += f"Adresse : {self.bid_info['contact']['address']}\n\n"
            general_info += f"Site web : {self.bid_info['general']['website']}"
            return general_info
        else:
            general_info = f"{self.bid_info['general']['name']} - {self.bid_info['general']['slogan']}\n\n"
            general_info += f"{self.bid_info['general']['description']}\n\n"
            general_info += f"Hours: {self.bid_info['hours']['en']}\n"
            general_info += f"Contact: {self.bid_info['contact']['phone']} / {self.bid_info['contact']['email']}\n"
            general_info += f"Address: {self.bid_info['contact']['address']}\n\n"
            general_info += f"Website: {self.bid_info['general']['website']}"
            return general_info

    def get_not_relevant_message(self, lang):
        """Obtenir le message de réponse non pertinente dans la bonne langue"""
        if lang in ['fr', 'fr-fr']:
            return "Je suis désolé, mais je ne peux répondre qu'aux questions concernant le Big Data, l'IA, le Machine Learning, le Business Intelligence, le Marketing Digital, la Data Science et des sujets connexes. N'hésitez pas à me poser une question dans ces domaines."
        elif lang in ['es', 'es-es']:
            return "Lo siento, pero solo puedo responder preguntas sobre Big Data, IA, Machine Learning, Business Intelligence, Marketing Digital, Data Science y temas relacionados. No dude en hacerme una pregunta en estas áreas."
        else:
            return "I'm sorry, but I can only answer questions about Big Data, AI, Machine Learning, Business Intelligence, Digital Marketing, Data Science, and related topics. Feel free to ask me a question in these areas."

    def fallback_response(self, lang):
        """Réponse de secours en cas d'erreur de l'API"""
        if lang in ['fr', 'fr-fr']:
            return "Je suis désolé, mais je rencontre actuellement des problèmes de connexion avec mon service d'IA. Voici quelques informations générales sur le sujet : les technologies de Big Data et d'IA sont en constante évolution. Pour des réponses plus précises, veuillez réessayer plus tard."
        elif lang in ['es', 'es-es']:
            return "Lo siento, pero actualmente estoy experimentando problemas de conexión con mi servicio de IA. Aquí hay alguna información general sobre el tema: las tecnologías de Big Data e IA están en constante evolución. Para respuestas más precisas, por favor intente más tarde."
        else:
            return "I'm sorry, but I'm currently experiencing connection issues with my AI service. Here's some general information on the topic: Big Data and AI technologies are constantly evolving. For more precise answers, please try again later."

    # Décorateur de cache pour les réponses fréquentes
    @functools.lru_cache(maxsize=50)
    def get_cached_response(self, query_key):
        """Version mise en cache des réponses fréquentes"""
        # Cette fonction est utilisée uniquement pour le cache
        return self.response_cache.get(query_key, None)

    def chat_with_groq(self, messages):
        """Communiquer avec l'API Groq pour obtenir des réponses"""
        # Créer une clé de cache basée sur le dernier message utilisateur
        last_user_msg = ""
        for msg in reversed(messages):
            if msg["role"] == "user":
                last_user_msg = msg["content"]
                break

        # Si le message est court, vérifier le cache
        if len(last_user_msg) < 100:
            cache_key = last_user_msg.lower().strip()
            cached_response = self.get_cached_response(cache_key)
            if cached_response:
                print("Réponse trouvée dans le cache")
                return cached_response

        # Limiter le nombre de messages envoyés à l'API pour améliorer les performances
        # Ne garder que les 5 derniers messages + le message système
        if len(messages) > 6:
            system_messages = [msg for msg in messages if msg["role"] == "system"]
            user_assistant_messages = [msg for msg in messages if msg["role"] in ["user", "assistant"]][-5:]
            messages = system_messages + user_assistant_messages

        try:
            headers = {
                "Authorization": f"Bearer {self.GROQ_API_KEY}",
                "Content-Type": "application/json"
            }
            data = {
                "model": self.GROQ_MODEL,
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 800  # Réduire pour accélérer la réponse
            }

            # Réduire le timeout pour éviter les attentes trop longues
            response = requests.post(self.GROQ_CHAT_URL, headers=headers, json=data, timeout=10)
            response.raise_for_status()
            result = response.json()

            if "choices" in result:
                response_text = result["choices"][0]["message"]["content"]

                # Mettre en cache la réponse si le message est court
                if len(last_user_msg) < 100:
                    self.response_cache[last_user_msg.lower().strip()] = response_text

                return response_text

            return "Je n'ai pas pu traiter cette demande. Veuillez réessayer."
        except requests.exceptions.Timeout:
            print("Timeout lors de l'appel à l'API Groq")
            return "Je suis désolé, mais le service d'IA met trop de temps à répondre. Veuillez réessayer avec une question plus courte."
        except Exception as e:
            print(f"API Error: {str(e)}")
            return "Je rencontre des difficultés à me connecter au service d'IA. Veuillez réessayer plus tard."

    def send_lead_email(self, name, email, phone):
        """Envoyer un email avec les informations du lead"""
        try:
            # Créer le message
            message_text = f"""
            Nouveau lead du chatbot:

            Nom: {name}
            Email: {email}
            Téléphone: {phone}
            Timestamp: {str(st.session_state.get("form_submitted_at", ""))}
            """

            # Sauvegarder dans un fichier JSON
            leads_file = os.path.join(os.path.dirname(__file__), "leads.json")

            # Charger les leads existants ou créer une liste vide
            if os.path.exists(leads_file):
                with open(leads_file, "r") as f:
                    try:
                        leads = json.load(f)
                    except:
                        leads = []
            else:
                leads = []

            # Ajouter le nouveau lead
            leads.append({
                "name": name,
                "email": email,
                "phone": phone,
                "timestamp": str(st.session_state.get("form_submitted_at", ""))
            })

            # Sauvegarder les leads
            with open(leads_file, "w") as f:
                json.dump(leads, f, indent=4)

            # Envoyer l'email
            try:
                # Configurer l'email
                msg = MIMEMultipart()
                msg['From'] = f"{self.DEFAULT_SENDER_NAME} <{self.SENDER_EMAIL}>"
                msg['To'] = self.RECIPIENT_EMAIL
                msg['Subject'] = f'Nouveau lead du chatbot: {name}'

                # Ajouter le corps du message
                msg.attach(MIMEText(message_text, 'plain'))

                # Envoyer l'email
                with smtplib.SMTP_SSL(self.SMTP_SERVER, self.SMTP_PORT) as server:
                    server.login(self.SENDER_EMAIL, self.SENDER_PASSWORD)
                    server.send_message(msg)

                print(f"Email envoyé à {self.RECIPIENT_EMAIL}")
                return True, "Email envoyé avec succès"
            except Exception as e:
                print(f"Erreur lors de l'envoi de l'email: {str(e)}")
                return True, "Lead sauvegardé mais email non envoyé"
        except Exception as e:
            print(f"Erreur lors de la sauvegarde du lead: {str(e)}")
            return False, str(e)

    def load_memory(self):
        """Charger l'historique des conversations depuis le fichier"""
        try:
            if os.path.exists(self.MEMORY_FILE):
                with open(self.MEMORY_FILE, 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            print(f"Erreur lors du chargement de la mémoire: {e}")
            return {}

    def save_memory(self, user_id, conversation):
        """Sauvegarder l'historique des conversations"""
        # Marquer qu'une sauvegarde est nécessaire
        self.memory_save_needed = True

        # Vérifier si on doit sauvegarder maintenant (basé sur le temps écoulé)
        now = datetime.now()
        if now - self.last_memory_save < self.save_interval:
            # Pas besoin de sauvegarder maintenant, on le fera plus tard
            return

        # Sauvegarder maintenant
        self._perform_memory_save(user_id, conversation)

    def _perform_memory_save(self, user_id, conversation):
        """Effectue la sauvegarde réelle de la mémoire"""
        try:
            memory = self.load_memory()
            memory[user_id] = {
                "conversation": conversation,
                "last_updated": datetime.now().isoformat()
            }
            with open(self.MEMORY_FILE, 'w') as f:
                json.dump(memory, f, indent=2)

            # Réinitialiser les indicateurs
            self.memory_save_needed = False
            self.last_memory_save = datetime.now()
            print("Mémoire sauvegardée avec succès")
        except Exception as e:
            print(f"Erreur lors de la sauvegarde de la mémoire: {e}")

    def get_user_id(self):
        """Générer un identifiant unique pour la session"""
        if 'user_id' not in st.session_state:
            st.session_state.user_id = str(hash(time.time()))
        return st.session_state.user_id

    def manage_memory(self, messages):
        """Gérer la longueur de l'historique des conversations"""
        if len(messages) > self.MAX_MESSAGES:
            return [messages[0]] + messages[-(self.MAX_MESSAGES-1):]
        return messages

# Fonction pour sauvegarder la mémoire avant de quitter
def save_memory_on_exit(app_instance):
    """Sauvegarde la mémoire avant de quitter l'application"""
    if app_instance.memory_save_needed:
        print("Sauvegarde de la mémoire avant de quitter...")
        if 'user_id' in st.session_state and 'messages' in st.session_state:
            app_instance._perform_memory_save(
                app_instance.get_user_id(),
                st.session_state.messages
            )

# Point d'entrée de l'application
if __name__ == "__main__":
    app = ChatbotApp()

    # Enregistrer la fonction de sauvegarde à exécuter à la fermeture
    import atexit
    atexit.register(save_memory_on_exit, app)
