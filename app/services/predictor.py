import re

def predict_intent_and_format(keyword):
    keyword_lower = keyword.lower()

    if any(word in keyword_lower for word in ["comprar", "cotizar", "precio", "solicitar", "contratar", "mejor"]):
        intent = "transaccional"
    elif any(word in keyword_lower for word in ["qué es", "cómo", "guía", "explicación", "información"]):
        intent = "informacional"
    elif any(word in keyword_lower for word in ["saldo simple", "sat", "fovissste", "infonavit"]):
        intent = "navegacional"
    else:
        intent = "informacional"

    if "simulador" in keyword_lower or "calculadora" in keyword_lower:
        recommended_format = "herramienta"
    elif intent == "transaccional":
        recommended_format = "comparador o landing page"
    elif intent == "informacional":
        recommended_format = "artículo educativo"
    else:
        recommended_format = "página de marca o guía"

    title = f"{keyword.capitalize()} – sugerencia SEO"

    return {
        "intent": intent,
        "recommended_format": recommended_format,
        "title_suggestion": title
    }
