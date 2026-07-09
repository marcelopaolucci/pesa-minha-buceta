"""Parsing de entrada textual (peso)."""


def parse_weight_to_grams(text: str) -> float:
    """
    Analisa string de peso ('1.5kg', '500g', '10') → gramas.
    Suporta sufixos kg, k, g, gr, gramas.
    Sem unidade: assume KG (compatibilidade).
    """
    text = text.lower().replace(",", ".").strip()

    # KG primeiro (contém 'g' como substring)
    for u in ["quilogramas", "quilos", "kg", "k"]:
        if text.endswith(u):
            val = float(text.replace(u, "").strip()) * 1000.0
            if val <= 0:
                raise ValueError("weight must be positive")
            return val

    # Gramas
    for u in ["gramas", "gr", "g"]:
        if text.endswith(u):
            val = float(text.replace(u, "").strip())
            if val <= 0:
                raise ValueError("weight must be positive")
            return val

    val = float(text) * 1000.0
    if val <= 0:
        raise ValueError("weight must be positive")
    return val
