import json
from langchain_core.messages import SystemMessage, HumanMessage
from utils.llms import LLMModel
from prompts.judge_prompt import JUDGE_PROMPT


class JudgeAgent:
    def __init__(self):
        self.llm = LLMModel().get_model()

    def run(self, state: dict):
        """
        Run judge agent and return JSON output
        
        Args:
            state: Current workflow state
            
        Returns:
            dict: JSON output with decision, recommendation, and reason
        """
        
        # Extract relevant context from state
        context = {
            "intent": state.get("intent", "unknown"),
            "current_agent": state.get("current_agent", "unknown"),
            "patient_data": state.get("patient_data", {}),
            "available_slots": state.get("available_slots", []),
            "appointment_data": state.get("appointment_data", {}),
            "user_message": state.get("user_message", state.get("user_input", "")),
            "language": state.get("language", "en"),
            "logs": state.get("logs", [])[-3:]  # Last 3 logs
        }

        messages = [
            SystemMessage(content=JUDGE_PROMPT),
            HumanMessage(content=json.dumps(context, indent=2))
        ]

        response = self.llm.invoke(messages).content

        try:
            data = json.loads(response)
        except Exception as e:
            # Fallback JSON if parsing fails
            data = {
                "decision": "escalate",
                "recommended_agent": "faq_agent",
                "reason": f"JSON parsing error: {str(e)[:50]}",
                "status": "error",
                "timestamp": "N/A"
            }

        # Create comprehensive JSON output
        judge_output = {
            "judge_decision": data.get("decision", "escalate"),
            "judge_recommendation": data.get("recommended_agent", "faq_agent"),
            "judge_reason": data.get("reason", "No reason provided"),
            "judge_status": data.get("status", "processed"),
            "judge_timestamp": data.get("timestamp", "N/A"),
            "original_intent": context["intent"],
            "original_agent": context["current_agent"],
            "language": context["language"]
        }
        
        # Update state with judge output
        state.update(judge_output)
        
        # Also store the full judge response
        state["judge_full_response"] = data
        
        return judge_output
