from app.services.question_engine import StructuredQuestionResult


def generate_natural_language_answer(
    result: StructuredQuestionResult, preferred_language: str
) -> str:
    lang = preferred_language.lower()
    if lang not in {"en", "it", "de"}:
        lang = "en"

    if result.kind == "expenses_total":
        pieces = [f"{total:.2f} {currency}" for currency, total in sorted(result.currency_totals.items())]
        joined = " + ".join(pieces)
        if lang == "it":
            return f"Hai speso {joined}."
        if lang == "de":
            return f"Du hast {joined} ausgegeben."
        return f"You spent {joined}."

    if result.kind == "latest_expense":
        currency, total = next(iter(result.currency_totals.items()))
        if lang == "it":
            return f"La tua ultima spesa e stata {total:.2f} {currency}."
        if lang == "de":
            return f"Deine letzte Ausgabe war {total:.2f} {currency}."
        return f"Your last expense was {total:.2f} {currency}."

    if result.kind == "loan_balances":
        balances = list((result.details or {}).get("balances", []))
        if not balances:
            if lang == "it":
                return "Non ho trovato saldi prestiti rilevanti."
            if lang == "de":
                return "Ich habe keine relevanten Darlehenssalden gefunden."
            return "I could not find relevant loan balances."
        lines: list[str] = []
        for entry in balances:
            person = str(entry.get("person", "")).strip() or "Unknown"
            amount = float(entry.get("amount", 0.0))
            currency = str(entry.get("currency", "CHF"))
            direction = str(entry.get("direction", "owes_you"))
            if direction == "you_owe":
                if lang == "it":
                    lines.append(f"Devi a {person} {amount:.2f} {currency}")
                elif lang == "de":
                    lines.append(f"Du schuldest {person} {amount:.2f} {currency}")
                else:
                    lines.append(f"You owe {person} {amount:.2f} {currency}")
            else:
                if lang == "it":
                    lines.append(f"{person} ti deve {amount:.2f} {currency}")
                elif lang == "de":
                    lines.append(f"{person} schuldet dir {amount:.2f} {currency}")
                else:
                    lines.append(f"{person} owes you {amount:.2f} {currency}")
        return "; ".join(lines) + "."

    if result.kind == "inventory_state":
        states = list((result.details or {}).get("states", []))
        if not states:
            if lang == "it":
                return "Non ho trovato stato inventario rilevante."
            if lang == "de":
                return "Ich habe keinen relevanten Inventarstatus gefunden."
            return "I could not find relevant inventory state."
        lines: list[str] = []
        for entry in states:
            item = str(entry.get("item", "item"))
            location = str(entry.get("location", "unknown"))
            quantity = int(entry.get("quantity", 0))
            lines.append(f"{quantity} {item} in {location}")
        return "; ".join(lines) + "."

    if result.kind == "semantic_match":
        details = result.details or {}
        matched_where = str(details.get("matched_where", "")).strip()
        matched_text = str(details.get("matched_memory", "")).strip()
        if matched_where:
            if lang == "it":
                return f"Dai tuoi ricordi risulta: {matched_where}."
            if lang == "de":
                return f"Aus deinen Erinnerungen ergibt sich: {matched_where}."
            return f"From your memories, it appears to be in {matched_where}."
        if matched_text:
            if lang == "it":
                return f"Ho trovato questo ricordo rilevante: {matched_text}"
            if lang == "de":
                return f"Ich habe diese relevante Erinnerung gefunden: {matched_text}"
            return f"I found this relevant memory: {matched_text}"

    if result.kind == "out_of_scope":
        if lang == "it":
            return "Questa domanda e fuori dallo scope MVP. Posso rispondere solo usando le memorie salvate."
        if lang == "de":
            return "Diese Frage liegt ausserhalb des MVP-Umfangs. Ich antworte nur mit gespeicherten Erinnerungen."
        return "This question is outside MVP scope. I can answer only from your stored memories."

    if result.kind == "no_result":
        if lang == "it":
            return "Non ho trovato memorie rilevanti. Puoi usare Add Memory per registrare queste informazioni."
        if lang == "de":
            return "Ich habe keine passenden Erinnerungen gefunden. Du kannst Add Memory nutzen, um diese Information zu speichern."
        return "I could not find matching memories. You can use Add Memory to record this information."

    if lang == "it":
        return result.clarification_question or "Puoi chiarire meglio la domanda?"
    if lang == "de":
        return result.clarification_question or "Kannst du die Frage bitte praezisieren?"
    return result.clarification_question or "Could you clarify your question?"
