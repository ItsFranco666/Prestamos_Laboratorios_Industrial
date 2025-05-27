class EquipmentInventoryView(ctk.CTkFrame):
    def __init__(self, parent):
        # ... Similar structure to other views ...
        self.status_icons = {
            'DISPONIBLE': '🟢',
            'DAÑADO': '🔴',
            'EN USO': '🟡'
        }
    
    def load_equipment(self):
        equipment = self.model.get_all_equipment()
        for item in equipment:
            status = self.status_icons.get(item[6], '⚫')
            self.tree.insert("", "end", values=(
                item[0], item[1], item[2], 
                item[3], item[4], item[5], status
            ))