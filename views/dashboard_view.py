import customtkinter as ctk
from tkinter import ttk
import sqlite3
from datetime import datetime, timedelta
import threading
import time
from utils.font_config import get_font
from database.connection import DatabaseManager
from PIL import Image, ImageTk
import os
import math
from database.models import DashboardModel

class DashboardView(ctk.CTkScrollableFrame):
    def __init__(self, parent, main_window=None):
        super().__init__(parent, fg_color="transparent")
        self.parent = parent
        self.main_window = main_window
        self.dashboard_model = DashboardModel()
        
        # Auto-refresh control
        self.auto_refresh = True
        self.refresh_thread = None
        
        self.create_widgets()
        self.load_data()
        self.start_auto_refresh()
        
    def create_widgets(self):
        # Main container
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Top metrics row
        self.create_top_metrics()
        
        # Middle section with charts and alerts
        self.create_middle_section()
        
        # Bottom section with active loans
        self.create_bottom_section()
        
        # Refresh controls
        self.create_refresh_controls()
    
    def create_top_metrics(self):
        # Metrics frame
        metrics_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        metrics_frame.pack(fill="x", pady=(0, 20))
        
        # Configure grid for 4 equal columns
        for i in range(4):
            metrics_frame.grid_columnconfigure(i, weight=1)
        
        # Room usage metric
        self.room_usage_card = self.create_metric_card(
            metrics_frame, "Uso de Salas", "0%", "", "#4CAF50"
        )
        self.room_usage_card.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        # Equipment usage metric
        self.equipment_usage_card = self.create_metric_card(
            metrics_frame, "Uso de Equipos", "0%", "", "#FF9800"
        )
        self.equipment_usage_card.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        
        # Active loans metric
        self.active_loans_card = self.create_metric_card(
            metrics_frame, "Préstamos Activos", "0", "En curso", "#2196F3"
        )
        self.active_loans_card.grid(row=0, column=2, padx=10, pady=10, sticky="ew")
        
        # Alerts metric
        self.alerts_card = self.create_metric_card(
            metrics_frame, "⚠️ Alertas", "0", "Pendientes", "#F44336"
        )
        self.alerts_card.grid(row=0, column=3, padx=10, pady=10, sticky="ew")
    
    def create_metric_card(self, parent, title, value, subtitle, color):
        card = ctk.CTkFrame(parent, height=120, fg_color=("#ffffff", "#2b2b2b"))
        card.pack_propagate(False)
        
        # Title
        title_label = ctk.CTkLabel(card, text=title, font=get_font("small"), text_color=("#666666", "#cccccc"))
        title_label.pack(pady=(15, 5))
        
        # Value
        value_label = ctk.CTkLabel(card, text=value, font=get_font("title", "bold"), text_color=color)
        value_label.pack(pady=(0, 5))
        
        # Subtitle
        subtitle_label = ctk.CTkLabel(card, text=subtitle, font=get_font("small"), text_color=("#888888", "#aaaaaa"))
        subtitle_label.pack(pady=(0, 15))
        
        # Store references for updating
        card.value_label = value_label
        card.subtitle_label = subtitle_label
        
        return card
    
    def create_middle_section(self):
        # Middle container
        middle_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        middle_frame.pack(fill="x", pady=(0, 20))
        
        # Configure grid for 2 equal columns
        middle_frame.grid_columnconfigure(0, weight=1)
        middle_frame.grid_columnconfigure(1, weight=1)
        
        # Room status visualization
        self.create_room_status_card(middle_frame)
        
        # Alerts section
        self.create_alerts_section(middle_frame)
    
    def create_room_status_card(self, parent):
        # Room status card
        room_card = ctk.CTkFrame(parent, fg_color=("#ffffff", "#2b2b2b"))
        room_card.grid(row=0, column=0, padx=(0, 10), pady=10, sticky="nsew")
        
        # Title
        title_label = ctk.CTkLabel(room_card, text="Estado de Salas", font=get_font("subtitle", "bold"))
        title_label.pack(pady=(20, 10))
        
        # Progress bars frame
        progress_frame = ctk.CTkFrame(room_card, fg_color="transparent")
        progress_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        # Available rooms progress
        available_label = ctk.CTkLabel(progress_frame, text="Salas Disponibles", font=get_font("normal"))
        available_label.pack(anchor="w", pady=(0, 5))
        
        self.available_rooms_progress = ctk.CTkProgressBar(progress_frame, height=20, progress_color="#4CAF50")
        self.available_rooms_progress.pack(fill="x", pady=(0, 10))
        self.available_rooms_progress.set(0)
        
        self.available_rooms_label = ctk.CTkLabel(progress_frame, text="0 / 0", font=get_font("small"))
        self.available_rooms_label.pack(anchor="w", pady=(0, 15))
        
        # Occupied rooms progress
        occupied_label = ctk.CTkLabel(progress_frame, text="Salas Ocupadas", font=get_font("normal"))
        occupied_label.pack(anchor="w", pady=(0, 5))
        
        self.occupied_rooms_progress = ctk.CTkProgressBar(progress_frame, height=20, progress_color="#FF5722")
        self.occupied_rooms_progress.pack(fill="x", pady=(0, 10))
        self.occupied_rooms_progress.set(0)
        
        self.occupied_rooms_label = ctk.CTkLabel(progress_frame, text="0 / 0", font=get_font("small"))
        self.occupied_rooms_label.pack(anchor="w", pady=(0, 20))
    
    def create_alerts_section(self, parent):
        # Alerts card
        alerts_card = ctk.CTkFrame(parent, fg_color=("#ffffff", "#2b2b2b"))
        alerts_card.grid(row=0, column=1, padx=(10, 0), pady=10, sticky="nsew")
        
        # Title
        title_label = ctk.CTkLabel(alerts_card, text="⚠️ Alertas de Mantenimiento", font=get_font("subtitle", "bold"))
        title_label.pack(pady=(20, 10))
        
        # Alerts container
        self.alerts_container = ctk.CTkScrollableFrame(alerts_card, height=200, fg_color="transparent")
        self.alerts_container.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Empty state label
        self.no_alerts_label = ctk.CTkLabel(
            self.alerts_container,
            text="✅ No hay alertas pendientes",
            font=get_font("normal"),
            text_color=("#4CAF50", "#4CAF50")
        )
        self.no_alerts_label.pack(pady=50)
    
    def create_bottom_section(self):
        # Active loans section
        loans_frame = ctk.CTkFrame(self.main_container, fg_color=("#ffffff", "#2b2b2b"))
        loans_frame.pack(fill="x", pady=(0, 20))
        
        # Header with title centered
        header_frame = ctk.CTkFrame(loans_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        title_label = ctk.CTkLabel(header_frame, text="Préstamos Activos", font=get_font("subtitle", "bold"))
        title_label.pack(fill="x", expand=True)
        title_label.configure(anchor="center", justify="center")
        
        # Loans table
        self.create_loans_table(loans_frame)
    
    def create_loans_table(self, parent):
        # Table frame
        table_frame = ctk.CTkFrame(parent, fg_color="transparent")
        table_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Treeview for loans
        columns = ("type", "borrower", "item", "date", "status")
        self.loans_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=8, style="Modern.Treeview")
        
        # Configure columns
        self.loans_tree.heading("type", text="Tipo")
        self.loans_tree.heading("borrower", text="Solicitante")
        self.loans_tree.heading("item", text="Elemento")
        self.loans_tree.heading("date", text="Fecha")
        self.loans_tree.heading("status", text="Estado")
        
        # Column widths adjusted to likely need a horizontal scroll
        self.loans_tree.column("type", width=120, anchor="center")
        self.loans_tree.column("borrower", width=250, anchor="w")
        self.loans_tree.column("item", width=250, anchor="w")
        self.loans_tree.column("date", width=180, anchor="center")
        self.loans_tree.column("status", width=120, anchor="center")
        
        # Scrollbar vertical
        self.v_scrollbar = ctk.CTkScrollbar(table_frame, command=self.loans_tree.yview, corner_radius=8, width=12)
        self.loans_tree.configure(yscrollcommand=self.v_scrollbar.set)
        
        # Nuevo: Scrollbar horizontal
        self.h_scrollbar = ctk.CTkScrollbar(table_frame, command=self.loans_tree.xview, corner_radius=8, height=12, orientation="horizontal")
        self.loans_tree.configure(xscrollcommand=self.h_scrollbar.set)
        
        # Pack layout: vertical scrollbar on the right, horizontal on the bottom
        self.v_scrollbar.pack(side="right", fill="y")
        self.h_scrollbar.pack(side="bottom", fill="x")
        self.loans_tree.pack(side="left", fill="both", expand=True)

        # Empty state label (se gestionará su visibilidad en update_active_loans)
        self.no_loans_label = ctk.CTkLabel(
            table_frame,
            text="📋 No hay préstamos activos",
            font=get_font("normal"),
            text_color=("#888888", "#aaaaaa")
        )
    
    def create_refresh_controls(self):
        # Refresh controls
        controls_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        controls_frame.pack(fill="x", pady=(0, 20))
        
        # Last updated label
        self.last_updated_label = ctk.CTkLabel(
            controls_frame,
            text="Última actualización: --",
            font=get_font("small"),
            text_color=("#666666", "#cccccc")
        )
        self.last_updated_label.pack(side="left")
        
        # Auto-refresh toggle
        self.auto_refresh_var = ctk.BooleanVar(value=True)
        self.auto_refresh_checkbox = ctk.CTkCheckBox(
            controls_frame,
            text="Actualización automática (30s)",
            variable=self.auto_refresh_var,
            command=self.toggle_auto_refresh,
            font=get_font("small")
        )
        self.auto_refresh_checkbox.pack(side="right", padx=(0, 10))
        
        # Manual refresh button (naranja, más espaciado)
        self.refresh_button = ctk.CTkButton(
            controls_frame,
            text="Actualizar",
            command=self.load_data,
            font=get_font("small"),
            width=120,
            height=32,
            fg_color=("#ffa154", "#c95414"),
            hover_color=("#ff8c33", "#b34a0e"),
            corner_radius=8
        )
        self.refresh_button.pack(side="right", padx=(0, 24))
    
    def load_data(self):
        """Load and update all dashboard data"""
        try:
            # Métricas de salas
            room_metrics = self.dashboard_model.get_room_metrics()
            self.update_room_metrics(room_metrics)
            # Métricas de equipos
            equipment_metrics = self.dashboard_model.get_equipment_metrics()
            self.update_equipment_metrics(equipment_metrics)
            # Préstamos activos
            active_loans = self.dashboard_model.get_active_loans()
            self.update_active_loans(active_loans)
            # Alertas
            alerts = self.dashboard_model.get_alerts()
            self.update_alerts(alerts)
            # Actualizar hora
            self.last_updated_label.configure(text=f"Última actualización: {datetime.now().strftime('%H:%M:%S')}")
        except Exception as e:
            print(f"Error loading dashboard data: {e}")
    
    def update_room_metrics(self, room_metrics):
        try:
            total_rooms = room_metrics['total']
            occupied_rooms = room_metrics['occupied']
            available_rooms = room_metrics['available']
            if total_rooms > 0:
                occupied_percentage = (occupied_rooms / total_rooms) * 100
                available_percentage = (available_rooms / total_rooms) * 100
            else:
                occupied_percentage = 0
                available_percentage = 0
            self.room_usage_card.value_label.configure(text=f"{occupied_percentage:.1f}%")
            self.available_rooms_progress.set(available_percentage / 100)
            self.available_rooms_label.configure(text=f"{available_rooms} / {total_rooms}")
            self.occupied_rooms_progress.set(occupied_percentage / 100)
            self.occupied_rooms_label.configure(text=f"{occupied_rooms} / {total_rooms}")
        except Exception as e:
            print(f"Error updating room metrics: {e}")
    
    def update_equipment_metrics(self, equipment_metrics):
        try:
            total_equipment = equipment_metrics['total']
            in_use_equipment = equipment_metrics['in_use']
            if total_equipment > 0:
                usage_percentage = (in_use_equipment / total_equipment) * 100
            else:
                usage_percentage = 0
            self.equipment_usage_card.value_label.configure(text=f"{usage_percentage:.1f}%")
        except Exception as e:
            print(f"Error updating equipment metrics: {e}")
    
    def update_active_loans(self, active_loans):
        try:
            # Limpiar datos anteriores de la tabla
            for item in self.loans_tree.get_children():
                self.loans_tree.delete(item)

            total_active = len(active_loans)
            self.active_loans_card.value_label.configure(text=str(total_active))

            if active_loans:
                # Si hay préstamos, ocultar la etiqueta y mostrar la tabla/scrollbars
                self.no_loans_label.pack_forget()
                self.loans_tree.pack(side="left", fill="both", expand=True)
                self.v_scrollbar.pack(side="right", fill="y")
                self.h_scrollbar.pack(side="bottom", fill="x")
                
                for loan in active_loans:
                    loan_type, borrower, item, date_str, status = loan
                    try:
                        date_obj = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
                        formatted_date = date_obj.strftime('%d/%m/%Y %H:%M')
                    except (ValueError, TypeError):
                        formatted_date = date_str
                    
                    # El truncado de texto ya no es necesario con el scroll horizontal
                    # if len(borrower) > 25: ...
                    # if len(item) > 25: ...

                    self.loans_tree.insert("", "end", values=(loan_type, borrower, item, formatted_date, status))
            else:
                # Si no hay préstamos, ocultar la tabla/scrollbars y mostrar la etiqueta
                self.loans_tree.pack_forget()
                self.v_scrollbar.pack_forget()
                self.h_scrollbar.pack_forget()
                self.no_loans_label.pack(pady=50, expand=True)
                
        except Exception as e:
            print(f"Error updating active loans: {e}")
    
    def update_alerts(self, alerts):
        try:
            for widget in self.alerts_container.winfo_children():
                widget.destroy()
            damaged_equipment = alerts['damaged']
            review_equipment = alerts['review']
            alert_list = []
            for eq in damaged_equipment:
                alert_list.append({
                    'type': 'DAÑADO',
                    'severity': 'high',
                    'title': f'Equipo Dañado: {eq[0]}',
                    'description': eq[1],
                    'timestamp': 'Reporte permanente',
                    'color': '#F44336'
                })
            for eq in review_equipment:
                alert_list.append({
                    'type': 'REVISAR',
                    'severity': 'medium',
                    'title': f'Revisar Equipo: {eq[0]}',
                    'description': f"{eq[1]} - {eq[3]}",
                    'timestamp': 'Últimos 7 días',
                    'color': '#FF9800'
                })
            self.alerts_card.value_label.configure(text=str(len(alert_list)))
            if alert_list:
                self.no_alerts_label.pack_forget()
                for alert in alert_list:
                    self.create_alert_widget(alert)
            else:
                self.no_alerts_label.pack(pady=50)
        except Exception as e:
            print(f"Error updating alerts: {e}")
    
    def create_alert_widget(self, alert):
        """Create a clickable alert widget"""
        alert_frame = ctk.CTkFrame(self.alerts_container, fg_color=("#f5f5f5", "#3a3a3a"))
        alert_frame.pack(fill="x", pady=5)
        
        # Severity indicator (más pequeño y solo a la izquierda del texto)
        severity_colors = {
            'high': '#F44336',
            'medium': '#FF9800',
            'low': '#4CAF50'
        }
        # Hacemos el recuadro más pequeño (alto fijo, no fill="y")
        severity_frame = ctk.CTkFrame(alert_frame, width=8, height=48, fg_color=severity_colors.get(alert['severity'], '#4CAF50'))
        severity_frame.pack(side="left", padx=(0, 10), pady=8)
        severity_frame.pack_propagate(False)
        
        # Content
        content_frame = ctk.CTkFrame(alert_frame, fg_color="transparent")
        content_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        
        # Title
        title_label = ctk.CTkLabel(content_frame, text=alert['title'], font=get_font("normal", "bold"), anchor="w")
        title_label.pack(fill="x")
        
        # Description
        desc_label = ctk.CTkLabel(content_frame, text=alert['description'], font=get_font("small"), anchor="w", text_color=("#666666", "#cccccc"))
        desc_label.pack(fill="x")
        
        # Timestamp
        time_label = ctk.CTkLabel(content_frame, text=alert['timestamp'], font=get_font("small"), anchor="w", text_color=("#999999", "#999999"))
        time_label.pack(fill="x")
    
    def start_auto_refresh(self):
        """Start the auto-refresh thread"""
        if self.refresh_thread is None or not self.refresh_thread.is_alive():
            self.refresh_thread = threading.Thread(target=self.auto_refresh_worker, daemon=True)
            self.refresh_thread.start()
    
    def auto_refresh_worker(self):
        """Worker thread for auto-refresh"""
        while self.auto_refresh:
            time.sleep(30)  # 30 seconds interval
            if self.auto_refresh and self.auto_refresh_var.get():
                # Schedule UI update in main thread
                self.after(0, self.load_data)
    
    def toggle_auto_refresh(self):
        """Toggle auto-refresh functionality"""
        self.auto_refresh = self.auto_refresh_var.get()
        if self.auto_refresh:
            self.start_auto_refresh()
    
    def on_theme_change(self):
        """Handle theme changes"""
        self.load_data()
    
    def destroy(self):
        """Clean up when destroying the widget"""
        self.auto_refresh = False
        if self.refresh_thread and self.refresh_thread.is_alive():
            self.refresh_thread.join(timeout=1)
        super().destroy()