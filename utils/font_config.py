import customtkinter as ctk

# Configuración global de fuentes
FONT_FAMILY = "Roboto"  # Puedes cambiar esto por la fuente que prefieras
FONT_SIZES = {
    "title": 30,
    "subtitle": 18,
    "normal": 14,
    "small": 12
}

def get_font(size="normal", weight="normal"):
    """
    Obtiene una configuración de fuente predefinida
    :param size: Tamaño de la fuente ("title", "subtitle", "normal", "small")
    :param weight: Peso de la fuente ("normal", "bold")
    :return: Objeto CTkFont configurado
    """
    return ctk.CTkFont(
        family=FONT_FAMILY,
        size=FONT_SIZES.get(size, FONT_SIZES["normal"]),
        weight=weight
    ) 