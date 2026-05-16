VISUAL_TERMS = [
    "rosto","imagem","foto","aparencia","aparência",
    "humana","futurista","bonita","visual","olhos"
]

def is_visual_followup(message: str) -> bool:
    if not message:
        return False
    m = message.lower()
    return any(t in m for t in VISUAL_TERMS)

def build_visual_reply(message: str, analysis: str) -> str:
    msg = message.lower()

    if "humana" in msg and "futurista" in msg:
        return (
            "Ela parece uma mistura equilibrada entre humano e futurista. "
            + analysis[:700]
        )

    if "rosto" in msg:
        return (
            "O rosto dela transmite bastante presença visual e identidade própria. "
            + analysis[:700]
        )

    return analysis[:900]
