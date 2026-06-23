"""
Pantalla 2 — Dashboard / Panel de Control.
Muestra tarjetas con estadísticas y botones de navegación.
"""

import customtkinter as ctk
import database


class DashboardFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller

        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # ---- Encabezado ----
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=30, pady=(25, 5))

        self.lbl_welcome = ctk.CTkLabel(
            header, text="Bienvenido",
            font=ctk.CTkFont(size=28, weight="bold"),
        )
        self.lbl_welcome.pack(anchor="w")

        self.lbl_subtitle = ctk.CTkLabel(
            header, text="Panel de Control — Resumen de tu flotilla",
            font=ctk.CTkFont(size=13), text_color="gray",
        )
        self.lbl_subtitle.pack(anchor="w", pady=(2, 0))

        # ---- Tarjetas de estadísticas ----
        cards = ctk.CTkFrame(self, fg_color="transparent")
        cards.grid(row=1, column=0, padx=25, pady=(20, 10), sticky="ew")
        cards.grid_columnconfigure((0, 1, 2), weight=1)

        self.card_vehicles = self._make_card(
            cards, "🚗  Vehículos Registrados", "0", "#3B82F6", 0,
        )
        self.card_maint = self._make_card(
            cards, "🔧  Mantenimientos del Mes", "0", "#F59E0B", 1,
        )
        self.card_expenses = self._make_card(
            cards, "💰  Total Gastado", "$0.00", "#10B981", 2,
        )

        # ---- Grid de botones de navegación ----
        nav = ctk.CTkFrame(self, fg_color="transparent")
        nav.grid(row=2, column=0, padx=25, pady=(10, 20), sticky="nsew")
        nav.grid_columnconfigure((0, 1, 2), weight=1)
        nav.grid_rowconfigure((0, 1), weight=1)

        btns = [
            ("🚗\nVehículos",      "#3B82F6", "#2563EB", self.controller.show_vehicles,    0, 0),
            ("👷\nConductores",    "#8B5CF6", "#7C3AED", self.controller.show_drivers,     0, 1),
            ("🔧\nMantenimientos", "#F59E0B", "#D97706", self.controller.show_maintenance, 0, 2),
            ("💰\nGastos",         "#10B981", "#059669", self.controller.show_expenses,    1, 0),
            ("📊\nReportes",       "#06B6D4", "#0891B2", self.controller.show_reports,     1, 1),
            ("🚪\nCerrar Sesión",  "#EF4444", "#DC2626", self.controller.on_logout,        1, 2),
        ]

        for text, fg, hover, cmd, row, col in btns:
            ctk.CTkButton(
                nav, text=text,
                font=ctk.CTkFont(size=16, weight="bold"),
                fg_color=fg, hover_color=hover,
                height=110, corner_radius=14,
                command=cmd,
            ).grid(row=row, column=col, padx=10, pady=10, sticky="nsew")

    # -----------------------------------------------------------------

    def _make_card(self, parent, title, value, accent, col):
        card = ctk.CTkFrame(
            parent, corner_radius=14, height=110,
            border_width=2, border_color=accent,
        )
        card.grid(row=0, column=col, padx=10, pady=5, sticky="nsew")
        card.grid_propagate(False)
        card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            card, text=title,
            font=ctk.CTkFont(size=12), text_color="gray",
        ).grid(row=0, column=0, padx=18, pady=(18, 4), sticky="w")

        lbl_val = ctk.CTkLabel(
            card, text=value,
            font=ctk.CTkFont(size=30, weight="bold"),
        )
        lbl_val.grid(row=1, column=0, padx=18, pady=(0, 18), sticky="w")
        return lbl_val

    def refresh(self):
        name = self.controller.current_username or "Administrador"
        self.lbl_welcome.configure(text=f"Bienvenido, {name}")

        stats = database.get_dashboard_stats(self.controller.current_admin_id)
        self.card_vehicles.configure(text=str(stats["total_vehicles"]))
        self.card_maint.configure(text=str(stats["month_maintenance"]))
        self.card_expenses.configure(text=f"${stats['month_expenses']:,.2f}")
