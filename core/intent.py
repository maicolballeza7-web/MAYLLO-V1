def interpret_intent(text: str):
    text = (text or "").lower()

    if any(
        k in text
        for k in [
            "abre",
            "abrir",
            "lanza",
            "lanzar",
            "ejecuta",
            "ejecutar",
        ]
    ):
        app = None
        if "spotify" in text:
            app = "spotify"
        elif "vscode" in text or "visual studio code" in text or "código" in text:
            app = "vscode"
        elif any(
            k in text
            for k in ["word", "microsoft word", "procesador de texto"]
        ):
            app = "word"
        elif any(
            k in text
            for k in ["excel", "microsoft excel", "hoja de cálculo", "hoja de calculo"]
        ):
            app = "excel"
        elif any(k in text for k in ["powerpoint", "power point", "presentación"]):
            app = "powerpoint"
        elif any(k in text for k in ["outlook", "correo de microsoft"]):
            app = "outlook"
        elif any(k in text for k in ["onenote", "one note"]):
            app = "onenote"
        elif any(k in text for k in ["access", "base de datos"]):
            app = "access"
        return {"action": "open_application", "app": app, "confidence": 0.7}

    if any(k in text for k in ["busca", "buscar", "investiga", "google"]):
        return {"action": "web_search", "query": text, "confidence": 0.7}

    if any(k in text for k in ["archivo", "carpeta", "documento", "leer"]):
        return {"action": "file_access", "confidence": 0.6}

    return {"action": "chat", "confidence": 1.0}
