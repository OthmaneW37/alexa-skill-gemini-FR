import logging
import os
import json
import requests

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.utils import is_request_type, is_intent_name

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# --- CONFIGURATION ---
GOOGLE_API_KEY = "AIzaSyBlDP-UABKY2IhCiiV3OaJcYI_SSricK5U"

# Dernière tentative avec le modèle gemini-1.5-flash
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GOOGLE_API_KEY}"

def call_gemini_api(user_text):
    """Fonction manuelle pour appeler Gemini via HTTP"""
    headers = {'Content-Type': 'application/json'}
    payload = {
        "contents": [{
            "parts": [{"text": user_text}]
        }]
    }
    
    try:
        # On envoie la requête
        response = requests.post(GEMINI_URL, headers=headers, data=json.dumps(payload), timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            # On extrait le texte de la réponse complexe de Google
            try:
                return data['candidates'][0]['content']['parts'][0]['text']
            except (KeyError, IndexError):
                return "Gemini a répondu mais le format est vide."
        else:
            # Si erreur (404, 400, 500), on loggue le détail
            logger.error(f"Erreur HTTP Google: {response.status_code} - {response.text}")
            return f"Erreur Google : {response.status_code}"
            
    except Exception as e:
        logger.error(f"Erreur connection: {e}")
        return "Erreur de connexion internet."


class LaunchRequestHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        speak_output = "Bonjour ! Je suis connecté à Gemini Pro. Posez votre question."
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

class AskGeminiIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("AskGeminiIntent")(handler_input)

    def handle(self, handler_input):
        # 1. Récupération de la question
        try:
            slots = handler_input.request_envelope.request.intent.slots
            user_question = slots["question"].value
        except Exception:
            user_question = None

        if not user_question:
             return handler_input.response_builder.speak("Je n'ai pas compris.").ask("Répétez ?").response

        # 2. Appel à Gemini
        ai_response = call_gemini_api(user_question)

        # 3. Traitement de la réponse
        if ai_response:
            # Nettoyage des caractères spéciaux (markdown)
            ai_response = ai_response.replace("*", "")
            
            # Limite de longueur pour Alexa (SSML limite)
            if len(ai_response) > 800:
                ai_response = ai_response[:800] + "... Je m'arrête là."
                
            return handler_input.response_builder.speak(ai_response).ask("Autre chose ?").response
        else:
            return handler_input.response_builder.speak("Désolé, je n'ai pas réussi à joindre Google.").response

class CancelOrStopIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return (is_intent_name("AMAZON.CancelIntent")(handler_input) or
                is_intent_name("AMAZON.StopIntent")(handler_input))
    def handle(self, handler_input):
        return handler_input.response_builder.speak("Au revoir !").response

class CatchAllExceptionHandler(AbstractExceptionHandler):
    def can_handle(self, handler_input, exception):
        return True
    def handle(self, handler_input, exception):
        logger.error(exception, exc_info=True)
        return handler_input.response_builder.speak(f"Erreur technique : {str(exception)}").response

# Construction de la Skill
sb = SkillBuilder()
sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(AskGeminiIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()
