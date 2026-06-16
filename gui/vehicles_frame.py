"""
Pantalla 3 — Gestión de Vehículos.
CRUD completo con tabla scrolleable, búsqueda y botones de acción.
"""

import customtkinter as ctk
from tkinter import messagebox
import database
from gui.dialogs import VehicleDialog


class VehiclesFrame(ctk.CTkFrame):
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
            top, text="🚗  Gestión de Vehículos",
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
            placeholder_text="🔍  Buscar por marca, modelo, placas, VIN o estado…",
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

        headers = ["Marca", "Modelo", "Año", "Placas", "VIN", "Km", "Estado", "Acciones"]
        self._draw_header(headers)

        query = self.entry_search.get()
        rows = database.get_vehicles(self.controller.current_admin_id, query)

        if not rows:
            ctk.CTkLabel(
                self.table_scroll, text="No se encontraron vehículos.",
                font=ctk.CTkFont(size=14, slant="italic"), text_color="gray",
            ).pack(pady=40)
            return

        for idx, v in enumerate(rows):
            v_id, brand, model, year, plates, vin, mileage, status = v
            bg = ("#F8FAFC", "#1E293B") if idx % 2 == 0 else ("#EFF6FF", "#0F172A")
            self._draw_row(bg, v_id, brand, model, year, plates, vin, mileage, status)

    # -----------------------------------------------------------------

    def _draw_header(self, headers):
        frame = ctk.CTkFrame(
            self.table_scroll, fg_color=("gray85", "gray20"), corner_radius=6)
        frame.pack(fill="x", pady=(0, 4))
        for i in range(len(headers)):
            frame.grid_columnconfigure(i, weight=1 if i < 7 else 2)
        for i, h in enumerate(headers):
            ctk.CTkLabel(frame, text=h, font=ctk.CTkFont(weight="bold")).grid(
                row=0, column=i, padx=6, pady=8, sticky="w")

    def _draw_row(self, bg, v_id, brand, model, year, plates, vin, mileage, status):
        rf = ctk.CTkFrame(self.table_scroll, fg_color=bg, corner_radius=4)
        rf.pack(fill="x", pady=1)
        for i in range(8):
            rf.grid_columnconfigure(i, weight=1 if i < 7 else 2)

        ctk.CTkLabel(rf, text=brand).grid(row=0, column=0, padx=6, pady=6, sticky="w")
        ctk.CTkLabel(rf, text=model).grid(row=0, column=1, padx=6, pady=6, sticky="w")
        ctk.CTkLabel(rf, text=str(year)).grid(row=0, column=2, padx=6, pady=6, sticky="w")
        ctk.CTkLabel(
            rf, text=plates, font=ctk.CTkFont(weight="bold"),
        ).grid(row=0, column=3, padx=6, pady=6, sticky="w")
        ctk.CTkLabel(rf, text=vin, font=ctk.CTkFont(size=11)).grid(
            row=0, column=4, padx=6, pady=6, sticky="w")
        ctk.CTkLabel(rf, text=f"{mileage:,} km").grid(
            row=0, column=5, padx=6, pady=6, sticky="w")

        sc = "#10B981" if status == "Activo" else "#EF4444"
        ctk.CTkLabel(
            rf, text=status, text_color=sc, font=ctk.CTkFont(weight="bold"),
        ).grid(row=0, column=6, padx=6, pady=6, sticky="w")

        actions = ctk.CTkFrame(rf, fg_color="transparent")
        actions.grid(row=0, column=7, padx=4, pady=2)

        ctk.CTkButton(
            actions, text="✏️", width=32, height=26,
            command=lambda vid=v_id: self._open_edit(vid),
        ).grid(row=0, column=0, padx=2)

        ctk.CTkButton(
            actions, text="🗑️", width=32, height=26,
            fg_color="#DC2626", hover_color="#B91C1C",
            command=lambda vid=v_id: self._delete(vid),
        ).grid(row=0, column=1, padx=2)

    # -----------------------------------------------------------------
    #  Acciones CRUD
    # -----------------------------------------------------------------

    def _open_add(self):
        VehicleDialog(
            self, admin_id=self.controller.current_admin_id,
            callback=self.refresh)

    def _open_edit(self, vehicle_id):
        data = database.get_vehicle_by_id(vehicle_id, self.controller.current_admin_id)
        if data:
            VehicleDialog(
                self, admin_id=self.controller.current_admin_id,
                vehicle_data=data, callback=self.refresh)

    def _delete(self, vehicle_id):
        if messagebox.askyesno(
            "Confirmar Eliminación",
            "¿Eliminar este vehículo?\n"
            "Se eliminarán también sus mantenimientos y gastos asociados.",
        ):
            ok, msg = database.delete_vehicle(
                vehicle_id, self.controller.current_admin_id)
            if ok:
                self.refresh()
            else:
                messagebox.showerror("Error", msg)
