# In university_management/utils/font_config.py
import customtkinter as ctk

def get_font(size_category="normal", weight="normal"):
    """
    Retorna un objeto de CTkFont dependiendo del tipo de texto
    """
    size = 18  # Default normal size
    if size_category == "title":
        size = 28
    elif size_category == "subtitle":
        size = 20
    elif size_category == "large":
        size = 24
    elif size_category == "small":
        size = 18

    return ctk.CTkFont(family="Roboto", size=size, weight=weight)

# Example usage (optional, for testing):
if __name__ == '__main__':
    # This part will only run if you execute font_config.py directly
    # It's not needed for the main application
    root = ctk.CTk()
    root.geometry("300x200")

    label_title = ctk.CTkLabel(root, text="Title Font", font=get_font("title", "bold"))
    label_title.pack(pady=5)

    label_subtitle = ctk.CTkLabel(root, text="Subtitle Font", font=get_font("subtitle"))
    label_subtitle.pack(pady=5)

    label_normal = ctk.CTkLabel(root, text="Normal Font", font=get_font())
    label_normal.pack(pady=5)
    
    label_small_italic = ctk.CTkLabel(root, text="Small Italic Font", font=get_font("small", "italic"))
    label_small_italic.pack(pady=5)

    root.mainloop()