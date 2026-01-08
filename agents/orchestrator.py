import json
from langchain_core.messages import SystemMessage, HumanMessage
from prompts.orchestrator_prompt import ORCHESTRATOR_PROMPT
from utils.llms import LLMModel
from utils.language_detector import LanguageDetector


class OrchestratorAgent:
    def __init__(self):
        self.llm = LLMModel().get_model()
        self.language_detector = LanguageDetector()

    def run(self, state: dict):
        """Orchestrator decides which agent to use and detects language"""
        
        # Detect language from user input
        user_input = state.get("user_input", "")
        detected_language = self.language_detector.detect(user_input)
        
        # Store detected language in state
        state["detected_language"] = detected_language
        state["language"] = detected_language  # Also set main language field
        
        # Create multilingual prompt
        multilingual_prompt = self._create_multilingual_prompt(detected_language)
        
        messages = [
            SystemMessage(content=multilingual_prompt),
            HumanMessage(content=user_input)
        ]

        response = self.llm.invoke(messages).content

        try:
            data = json.loads(response)
        except:
            data = {
                "intent": "UNKNOWN",
                "next_agent": "faq_agent",
                "reason": "Fallback"
            }

        state["intent"] = data["intent"]
        state["current_agent"] = data["next_agent"]
        state["orchestrator_reason"] = data.get("reason", "")
        
        return state
    
    def _create_multilingual_prompt(self, language: str) -> str:
        """Create a multilingual version of the orchestrator prompt"""
        
        language_instructions = {
            "en": "The user is speaking English. Analyze their intent in English.",
            "fr": "L'utilisateur parle français. Analysez son intention en français.",
            "ar": "المستخدم يتحدث العربية. قم بتحليل نيته باللغة العربية.",
            "ma": "L'utilisateur parle Darija marocaine. Analyser son intention en Darija."
        }
        
        language_instruction = language_instructions.get(language, language_instructions["en"])
        
        multilingual_prompt = f"""
{language_instruction}

{ORCHESTRATOR_PROMPT}

Important: The user is speaking in {language.upper()}. Consider this when analyzing their intent.
"""
        return multilingual_prompt
