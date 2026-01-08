def build_final_response(state: dict):
    if state.get("current_agent") == "faq_agent":
        return [
            {
                "type": "text",
                "text": state.get("faq_answer", "Voici les informations demandées.")
            }
        ]

    if state.get("available_slots"):
        return [
            {"type": "text", "text": "Voici les créneaux disponibles :"},
            {
                "type": "single-choice",
                "choices": [
                    {"title": s["label"], "value": s["value"]}
                    for s in state["available_slots"]
                ]
            }
        ]

    if state.get("appointment_data"):
        return [
            {"type": "text", "text": "✅ Votre rendez-vous est confirmé."}
        ]

    return [
        {"type": "text", "text": "Comment puis-je vous aider ?"}
    ]
