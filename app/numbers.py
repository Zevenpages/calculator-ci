"""Parseo de entrada del usuario a número. Lógica pura, sin Flask."""


def parse_number(text):
    s = (text or "").strip()
    if not s:
        raise ValueError("Entrada vacia")
    if s.count(".") + s.count(",") > 1:
        raise ValueError("Numero invalido: usa un solo separador decimal")
    s = s.replace(",", ".")
    try:
        return float(s)
    except ValueError:
        raise ValueError("Numero invalido")
