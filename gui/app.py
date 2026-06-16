"""
Flotilla Control — Ventana principal y controlador de navegación.
Gestiona la sesión del admin y el ciclo Login → App → Logout.
"""

import customtkinter as ctk
import database

from gui.login_frame import LoginFrame
from gui.dashboard_frame import DashboardFrame
from gui.vehicles_frame import VehiclesFrame
from gui.drivers_frame import DriversFrame
from gui.maintenance_frame import MaintenanceFrame
from gui.expenses_frame import ExpensesFrame
from gui.reports_frame import ReportsFrame

# Configuración visual global
ctk.set_appearance_mode("System")       # System | Dark | Light
ctk.set_default_color_theme("blue")


class App(ctk.CTk):
    """Ventana raíz de la aplicación."""

    def __init__(self):
        super().__init__()

        # Inicializar base de datos
        database.init_db()

        self.title("Flotilla Control — Sistema de Gestión Vehicular")
        self.geometry("1150x720")
        self.minsize(1000, 620)

        # ---- Estado de sesión ----
        self.current_admin_id = None
        self.current_username = None

        # ---- Layout raíz ----
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Login frame (siempre existe)
        self.login_frame = LoginFrame(self, self)
        self.login_frame.grid(row=0, column=0, sticky="nsew")

        # Contenedor de la app (creado al loguearse)
        self.app_container = None
        self.app_frames = {}

    # =================================================================
    #  SESIÓN
    # =================================================================

    def on_login_success(self, admin_id, username):
        """Llamado por LoginFrame al autenticar con éxito."""
        self.current_admin_id = admin_id
        self.current_username = username
        self._build_app()
        self.show_dashboard()

    def on_logout(self):
        """Cierra sesión: destruye frames de la app y muestra el login."""
        self.current_admin_id = None
        self.current_username = None
        if self.app_container:
            self.app_container.destroy()
            self.app_container = None
            self.app_frames = {}
        self.login_frame.clear_fields()
        self.login_frame.tkraise()

    # =================================================================
    #  CONSTRUCCIÓN DE FRAMES
    # =================================================================

    def _build_app(self):
        """Crea el contenedor con todos los frames de la aplicación."""
        if self.app_container:
            self.app_container.destroy()

        self.app_container = ctk.CTkFrame(self, fg_color="transparent")
        self.app_container.grid(row=0, column=0, sticky="nsew")
        self.app_container.grid_rowconfigure(0, weight=1)
        self.app_container.grid_columnconfigure(0, weight=1)

        frame_map = {
            "dashboard":   DashboardFrame,
            "vehicles":    VehiclesFrame,
            "drivers":     DriversFrame,
            "maintenance": MaintenanceFrame,
            "expenses":    ExpensesFrame,
            "reports":     ReportsFrame,
        }

        self.app_frames = {}
        for name, cls in frame_map.items():
            frame = cls(self.app_container, self)
            frame.grid(row=0, column=0, sticky="nsew")
            self.app_frames[name] = frame

    # =================================================================
    #  NAVEGACIÓN
    # =================================================================

    def _show(self, name):
        frame = self.app_frames.get(name)
        if frame:
            frame.refresh()
            frame.tkraise()

    def show_dashboard(self):
        self._show("dashboard")

    def show_vehicles(self):
        self._show("vehicles")

    def show_drivers(self):
        self._show("drivers")

    def show_maintenance(self):
        self._show("maintenance")

    def show_expenses(self):
        self._show("expenses")

    def show_reports(self):
        self._show("reports")
