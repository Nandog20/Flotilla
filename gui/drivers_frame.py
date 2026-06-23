"""
Pantalla 4 — Gestión de Conductores.
CRUD completo con tabla scrolleable, búsqueda y asignación de vehículo.
"""

import customtkinter as ctk
from tkinter import messagebox
import database
from gui.dialogs import DriverDialog


class DriversFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller

        self.grid_rowconfigure(2, weight=1)
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
            command=self.controller.show_dashboard,
        ).grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(
            top, text="👷  Gestión de Conductores",
            font=ctk.CTkFont(size=22, weight="bold"),
        ).grid(row=0, column=1, sticky="w", padx=10)

        ctk.CTkButton(
            top, text="➕  Agregar", width=130, height=36,
            fg_color="#10B981", hover_color="#059669",
            font=ctk.CTkFont(weight="bold"),
            command=self._open_add,
        ).grid(row=0, column=2, sticky="e")

        # ---- Barra de búsqueda ----
        search_bar = ctk.CTkFrame(self)
        search_bar.grid(row=1, column=0, sticky="ew", padx=15, pady=(8, 10))
        search_bar.grid_columnconfigure(0, weight=1)

        self.entry_search = ctk.CTkEntry(
            search_bar,
            placeholder_text="🔍  Buscar por nombre, teléfono, CURP o estado…",
            height=38,
        )
        self.entry_search.grid(row=0, column=0, padx=12, pady=10, sticky="ew")
        self.entry_search.bind("<Return>", lambda _: self.refresh())

        ctk.CTkButton(
            search_bar, text="Buscar", width=90,
            command=self.refresh,
        ).grid(row=0, column=1, padx=(0, 12), pady=10)

        # ---- Contenedor de tabla ----
        table_container = ctk.CTkFrame(self)
        table_container.grid(row=2, column=0, sticky="nsew", padx=15, pady=(0, 12))

        self.table_scroll = ctk.CTkScrollableFrame(table_container)
        self.table_scroll.pack(fill="both", expand=True, padx=6, pady=6)

    # -----------------------------------------------------------------
    #  Refrescar tabla
    # -----------------------------------------------------------------

    def refresh(self):
        for w in self.table_scroll.winfo_children():
            w.destroy()

        headers = ["Nombre", "Teléfono", "Dirección", "CURP", "Estado",
                    "Vehículo Asignado", "Acciones"]
        self._draw_header(headers)

        query = self.entry_search.get()
        rows = database.get_drivers(self.controller.current_admin_id, query)

        if not rows:
            ctk.CTkLabel(
                self.table_scroll, text="No se encontraron conductores.",
                font=ctk.CTkFont(size=14, slant="italic"), text_color="gray",
            ).pack(pady=40)
            return

        for idx, d in enumerate(rows):
            d_id, name, phone, address, curp, status, vehicle_id, vehicle_info = d
            bg = ("#F8FAFC", "#1E293B") if idx % 2 == 0 else ("#EFF6FF", "#0F172A")
            self._draw_row(bg, d_id, name, phone, address, curp, status, vehicle_info)

    # -----------------------------------------------------------------

    def _draw_header(self, headers):
        frame = ctk.CTkFrame(
            self.table_scroll, fg_color=("gray85", "gray20"), corner_radius=6)
        frame.pack(fill="x", pady=(0, 4))
        for i in range(len(headers)):
            frame.grid_columnconfigure(i, weight=2 if i < 6 else 1, uniform="drv_cols")
        for i, h in enumerate(headers):
            ctk.CTkLabel(frame, text=h, font=ctk.CTkFont(weight="bold")).grid(
                row=0, column=i, padx=6, pady=8, sticky="w")

    def _draw_row(self, bg, d_id, name, phone, address, curp, status, vehicle_info):
        rf = ctk.CTkFrame(self.table_scroll, fg_color=bg, corner_radius=4)
        rf.pack(fill="x", pady=1)
        for i in range(7):
            rf.grid_columnconfigure(i, weight=2 if i < 6 else 1, uniform="drv_cols")

        ctk.CTkLabel(
            rf, text=name, font=ctk.CTkFont(weight="bold"),
        ).grid(row=0, column=0, padx=6, pady=6, sticky="w")
        ctk.CTkLabel(rf, text=phone).grid(
            row=0, column=1, padx=6, pady=6, sticky="w")
        ctk.CTkLabel(
            rf, text=address or "—", font=ctk.CTkFont(size=12),
        ).grid(row=0, column=2, padx=6, pady=6, sticky="w")
        ctk.CTkLabel(
            rf, text=curp, font=ctk.CTkFont(size=11),
        ).grid(row=0, column=3, padx=6, pady=6, sticky="w")

        # Estado con color
        status_colors = {
            "Activo": "#10B981",
            "Suspendido": "#F59E0B",
            "Baja": "#EF4444",
        }
        ctk.CTkLabel(
            rf, text=status,
            text_color=status_colors.get(status, "white"),
            font=ctk.CTkFont(weight="bold"),
        ).grid(row=0, column=4, padx=6, pady=6, sticky="w")

        # Vehículo asignado
        ctk.CTkLabel(
            rf, text=vehicle_info, font=ctk.CTkFont(size=12),
        ).grid(row=0, column=5, padx=6, pady=6, sticky="w")

        # Acciones
        actions = ctk.CTkFrame(rf, fg_color="transparent")
        actions.grid(row=0, column=6, padx=4, pady=2)

        ctk.CTkButton(
            actions, text="✏️", width=32, height=26,
            command=lambda did=d_id: self._open_edit(did),
        ).grid(row=0, column=0, padx=2)

        ctk.CTkButton(
            actions, text="🗑️", width=32, height=26,
            fg_color="#DC2626", hover_color="#B91C1C",
            command=lambda did=d_id: self._delete(did),
        ).grid(row=0, column=1, padx=2)

    # -----------------------------------------------------------------
    #  Acciones CRUD
    # -----------------------------------------------------------------

    def _open_add(self):
        DriverDialog(
            self, admin_id=self.controller.current_admin_id,
            callback=self.refresh)

    def _open_edit(self, driver_id):
        data = database.get_driver_by_id(driver_id, self.controller.current_admin_id)
        if data:
            DriverDialog(
                self, admin_id=self.controller.current_admin_id,
                driver_data=data, callback=self.refresh)

    def _delete(self, driver_id):
        if messagebox.askyesno(
            "Confirmar Eliminación",
            "¿Eliminar este conductor del registro?",
        ):
            ok, msg = database.delete_driver(
                driver_id, self.controller.current_admin_id)
            if ok:
                self.refresh()
            else:
                messagebox.showerror("Error", msg)
