"""
Pantalla 5 — Mantenimientos (placeholder).
Se implementará completamente en la siguiente fase de desarrollo.
"""

import customtkinter as ctk


class MaintenanceFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # ---- Barra superior ----
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.grid(row=0, column=0, sticky="ew", padx=15, pady=(12, 5))
        top.grid_columnconfigure(1, weight=1)

        ctk.CTkButton(
            top, text="← Inicio", width=100, height=35,
            fg_color="transparent",
            text_color=("#3B82F6", "#60A5FA"),
            hover_color=("gray90", "gray20"),
            font=ctk.CTkFont(size=13),
            command=controller.show_dashboard,
        ).grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(
            top, text="🔧  Mantenimientos",
            font=ctk.CTkFont(size=22, weight="bold"),
        ).grid(row=0, column=1, sticky="w", padx=10)

        # ---- Contenido placeholder ----
        content = ctk.CTkFrame(self)
        content.grid(row=1, column=0, sticky="nsew", padx=15, pady=(8, 15))
        content.grid_rowconfigure(0, weight=1)
        content.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            content,
            text="🚧\n\nMódulo en Desarrollo\n\nEl historial de mantenimientos\nestrá disponible próximamente.",
            font=ctk.CTkFont(size=16),
            text_color="gray",
            justify="center",
        ).grid(row=0, column=0)

    def refresh(self):
        pass
