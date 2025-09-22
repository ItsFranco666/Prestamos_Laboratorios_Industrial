import customtkinter as ctk
from CTkListbox import CTkListbox

class SuggestionBox(ctk.CTkToplevel):
    def __init__(self, parent, entry_widget, callback):
        super().__init__(parent)
        self.entry_widget = entry_widget
        self.callback = callback

        self.overrideredirect(True)
        self.wm_attributes("-topmost", True)

        self.listbox = CTkListbox(self, command=self._on_select)
        self.listbox.pack(expand=True, fill="both")

        self.bind("<FocusOut>", self._on_focus_out)
        self.listbox.bind("<Enter>", self._on_mouse_enter)
        self.listbox.bind("<Leave>", self._on_mouse_leave)
        self._mouse_over = False

    def show(self):
        x = self.entry_widget.winfo_rootx()
        y = self.entry_widget.winfo_rooty() + self.entry_widget.winfo_height()
        width = self.entry_widget.winfo_width()
        self.geometry(f"{width}x150+{x}+{y}")
        self.lift()
        self.deiconify()

    def hide(self):
        self.withdraw()

    def update_suggestions(self, suggestions, format_function):
        try:
            self.listbox.destroy()
            self.listbox = CTkListbox(self, command=self._on_select)
            self.listbox.pack(expand=True, fill="both")
            self.listbox.bind("<Enter>", self._on_mouse_enter)
            self.listbox.bind("<Leave>", self._on_mouse_leave)
        except Exception as e:
            print(f"Error updating listbox: {e}")
            return
        
        if suggestions:
            for item in suggestions:
                try:
                    display_text = format_function(item)
                    self.listbox.insert("end", display_text)
                except Exception as e:
                    print(f"Error adding suggestion {item}: {e}")

    def _on_select(self, selected_item):
        # The first part of the string is assumed to be the identifier
        identifier = selected_item.split(" - ")[0]
        self.callback(identifier)
        self.hide()

    def _on_focus_out(self, event=None):
        if not self.is_mouse_over():
            self.hide()

    def _on_mouse_enter(self, event=None):
        self._mouse_over = True

    def _on_mouse_leave(self, event=None):
        self._mouse_over = False

    def is_mouse_over(self):
        return self._mouse_over
