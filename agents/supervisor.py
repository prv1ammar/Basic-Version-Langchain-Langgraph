import json
from langchain_core.messages import SystemMessage, HumanMessage
from utils.llms import LLMModel
from prompts.supervisor_prompt import SUPERVISOR_PROMPT


class SupervisorAgent:
    def __init__(self):
        self.llm = LLMModel().get_model()

    def run(self, state: dict):

        messages = [
            SystemMessage(content=SUPERVISOR_PROMPT),
            HumanMessage(
                content=f"""
Intent: {state.get("intent")}
User message: {state.get("user_input")}
"""
            )
        ]

        response = self.llm.invoke(messages).content

        try:
            data = json.loads(response)
        except Exception:
            raise ValueError(f"Supervisor invalid JSON: {response}")

        state["current_agent"] = data["next_agent"]
        state["supervisor_reason"] = data["reason"]

        return state
