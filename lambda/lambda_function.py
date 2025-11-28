import logging
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

import google.generativeai as genai

# --- IMPORTS ALEXA CORRIGÉS ---
from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model import Response
# Import des utilitaires pour éviter l'erreur "attribute type"
from ask_sdk_core.utils import is_request_type, is_intent_name

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# --- CONFIGURATION GEMINI ---
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
model = None

if GOOGLE_API_KEY:
    try:
        genai.configure(api_key=GOOGLE_API_KEY)
        model = genai.GenerativeModel('gemini-pro')
    except Exception as e:
        logger.error(f"Erreur init Gemini: {e}")

class LaunchRequestHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        # CORRECTION ICI : Utilisation de is_request_type
        return is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        speak_output = "Bonjour ! Je suis connecté à Gemini. Posez-moi votre question."
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

class AskGeminiIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        # CORRECTION ICI : Utilisation de is_intent_name
        return is_intent_name("AskGeminiIntent")(handler_input)

    def handle(self, handler_input):
        if not model:
            return handler_input.response_builder.speak("Clé API Gemini invalide ou manquante.").response

        # Récupération de la question de manière sécurisée
        try:
            slots = handler_input.request_envelope.request.intent.slots
            user_question = slots["question"].value
        except Exception:
            user_question = None

        if not user_question:
             return handler_input.response_builder.speak("Je n'ai pas compris la question.").ask("Répétez ?").response

        try:
            # Appel à Gemini
            response = model.generate_content(user_question)
            ai_response = response.text
            
            # Nettoyage
            ai_response = ai_response.replace("*", "")
            
            # Limite de longueur
            if len(ai_response) > 800:
                ai_response = ai_response[:800] + "... suite tronquée."

            return (
                handler_input.response_builder
                    .speak(ai_response)
                    .ask("Autre chose ?")
                    .response
            )
        except Exception as e:
            logger.error(f"Erreur Gemini: {e}")
            return handler_input.response_builder.speak("Problème de connexion avec Gemini.").response

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
        # On garde le mode Debug pour l'instant
        error_msg = f"Erreur technique : {str(exception)}"
        return handler_input.response_builder.speak(error_msg).response

# Construction de la Skill
sb = SkillBuilder()
sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(AskGeminiIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()