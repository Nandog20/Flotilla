"""
Pantalla 5 — Mantenimientos.
"""

import customtkinter as ctk
from tkinter import messagebox
import datetime
import database
from gui.dialogs import MaintenanceDialog

class MaintenanceFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller

        self.grid_rowconfigure(3, weight=1)
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
            top, text="🔧  Gestión de Mantenimientos",
            font=ctk.CTkFont(size=22, weight="bold"),
        ).grid(row=0, column=1, sticky="w", padx=10)

        ctk.CTkButton(
            top, text="➕  Registrar", width=130, height=36,
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
            placeholder_text="🔍  Buscar por vehículo, servicio, fecha o descripción…",
            height=38,
        )
        self.entry_search.grid(row=0, column=0, padx=12, pady=10, sticky="ew")
        self.entry_search.bind("<Return>", lambda _: self.refresh())

        ctk.CTkButton(
            search_bar, text="Buscar", width=90,
            command=self.refresh,
        ).grid(row=0, column=1, padx=(0, 12), pady=10)

        # ---- Filtro de fechas ----
        date_filter = ctk.CTkFrame(self, corner_radius=8)
        date_filter.grid(row=2, column=0, sticky="ew", padx=15, pady=(0, 10))

        ctk.CTkLabel(
            date_filter, text="📅  Filtrar por fecha:",
            font=ctk.CTkFont(size=13, weight="bold"),
        ).grid(row=0, column=0, padx=(12, 8), pady=10, sticky="w")

        ctk.CTkLabel(date_filter, text="Desde:", font=ctk.CTkFont(size=12)).grid(
            row=0, column=1, padx=(10, 4), pady=10, sticky="w")

        self.entry_date_from = ctk.CTkEntry(
            date_filter, placeholder_text="DD/MM/AAAA", width=120, height=32)
        self.entry_date_from.grid(row=0, column=2, padx=(0, 10), pady=10)

        ctk.CTkLabel(date_filter, text="Hasta:", font=ctk.CTkFont(size=12)).grid(
            row=0, column=3, padx=(10, 4), pady=10, sticky="w")

        self.entry_date_to = ctk.CTkEntry(
            date_filter, placeholder_text="DD/MM/AAAA", width=120, height=32)
        self.entry_date_to.grid(row=0, column=4, padx=(0, 10), pady=10)

        ctk.CTkButton(
            date_filter, text="Filtrar", width=80, height=32,
            fg_color="#3B82F6", hover_color="#2563EB",
            command=self.refresh,
        ).grid(row=0, column=5, padx=(5, 5), pady=10)

        ctk.CTkButton(
            date_filter, text="Limpiar", width=80, height=32,
            fg_color="#6B7280", hover_color="#4B5563",
            command=self._clear_date_filter,
        ).grid(row=0, column=6, padx=(0, 12), pady=10)

        # ---- Contenedor de tabla ----
        table_container = ctk.CTkFrame(self)
        table_container.grid(row=3, column=0, sticky="nsew", padx=15, pady=(0, 12))

        self.table_scroll = ctk.CTkScrollableFrame(table_container)
        self.table_scroll.pack(fill="both", expand=True, padx=6, pady=6)

    # -----------------------------------------------------------------
    def _parse_filter_date(self, date_str):
        """Convierte DD/MM/AAAA a YYYY-MM-DD para filtros, retorna None si inválido."""
        date_str = date_str.strip()
        if not date_str:
            return None
        try:
            return datetime.datetime.strptime(date_str, "%d/%m/%Y").strftime("%Y-%m-%d")
        except ValueError:
            return None

    def _clear_date_filter(self):
        """Limpia los campos de filtro de fecha y refresca."""
        self.entry_date_from.delete(0, "end")
        self.entry_date_to.delete(0, "end")
        self.refresh()

    def refresh(self):
        for w in self.table_scroll.winfo_children():
            w.destroy()

        headers = ["Vehículo", "Servicio", "Monto", "Fecha Inicio", "Fecha Fin", "Descripción", "Acciones"]
        self._draw_header(headers)

        query = self.entry_search.get()
        date_from = self._parse_filter_date(self.entry_date_from.get())
        date_to = self._parse_filter_date(self.entry_date_to.get())
        rows = database.get_maintenance(self.controller.current_admin_id, query,
                                        date_from=date_from, date_to=date_to)

        if not rows:
            ctk.CTkLabel(
                self.table_scroll, text="No se encontraron mantenimientos.",
                font=ctk.CTkFont(size=14, slant="italic"), text_color="gray",
            ).pack(pady=40)
            return

        for idx, m in enumerate(rows):
            # m = (id, plates, vehicle_name, date, end_date, service_type, description, vehicle_id, amount)
            bg = ("#F8FAFC", "#1E293B") if idx % 2 == 0 else ("#EFF6FF", "#0F172A")
            self._draw_row(bg, m)

    def _draw_header(self, headers):
        frame = ctk.CTkFrame(self.table_scroll, fg_color=("gray85", "gray20"), corner_radius=6)
        frame.pack(fill="x", pady=(0, 4))
        for i in range(len(headers)):
            frame.grid_columnconfigure(i, weight=1 if i < 6 else 0)
        for i, h in enumerate(headers):
            ctk.CTkLabel(frame, text=h, font=ctk.CTkFont(weight="bold")).grid(
                row=0, column=i, padx=6, pady=8, sticky="w")

    def _draw_row(self, bg, row_data):
        m_id, plates, v_name, date, end_date, srv_type, desc, v_id, amount = row_data
        rf = ctk.CTkFrame(self.table_scroll, fg_color=bg, corner_radius=4)
        rf.pack(fill="x", pady=1)
        for i in range(7):
            rf.grid_columnconfigure(i, weight=1 if i < 6 else 0)

        vehicle_str = f"{plates} - {v_name}"
        ctk.CTkLabel(rf, text=vehicle_str, font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=6, pady=6, sticky="w")
        ctk.CTkLabel(rf, text=srv_type).grid(row=0, column=1, padx=6, pady=6, sticky="w")
        
        # Monto
        amount_color = "#10B981" if float(amount) == 0 else ("#DC2626", "#F87171")
        ctk.CTkLabel(rf, text=f"${amount:,.2f}", text_color=amount_color, font=ctk.CTkFont(weight="bold")).grid(row=0, column=2, padx=6, pady=6, sticky="w")
        
        try:
            display_date = datetime.datetime.strptime(date, "%Y-%m-%d").strftime("%d/%m/%Y")
        except Exception:
            display_date = date
        ctk.CTkLabel(rf, text=display_date).grid(row=0, column=3, padx=6, pady=6, sticky="w")
        
        if end_date:
            try:
                display_end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d").strftime("%d/%m/%Y")
            except Exception:
                display_end_date = end_date
        else:
            display_end_date = "N/A"
            
        color_args = {"text_color": "gray"} if not end_date else {}
        ctk.CTkLabel(rf, text=display_end_date, **color_args).grid(row=0, column=4, padx=6, pady=6, sticky="w")
        
        # Truncate description if too long
        display_desc = (desc[:30] + '...') if len(desc) > 30 else desc
        ctk.CTkLabel(rf, text=display_desc).grid(row=0, column=5, padx=6, pady=6, sticky="w")

        actions = ctk.CTkFrame(rf, fg_color="transparent")
        actions.grid(row=0, column=6, padx=4, pady=2, sticky="e")

        ctk.CTkButton(
            actions, text="✏️", width=32, height=26,
            command=lambda mid=m_id: self._open_edit(mid),
        ).grid(row=0, column=0, padx=2)

        ctk.CTkButton(
            actions, text="🗑️", width=32, height=26,
            fg_color="#EF4444", hover_color="#B91C1C",
            command=lambda mid=m_id: self._delete_maint(mid),
        ).grid(row=0, column=1, padx=2)

    # -----------------------------------------------------------------
    def _open_add(self):
        MaintenanceDialog(self.winfo_toplevel(), self.controller.current_admin_id, callback=self.refresh)

    def _open_edit(self, maint_id):
        m = database.get_maintenance_by_id(maint_id, self.controller.current_admin_id)
        if m:
            MaintenanceDialog(self.winfo_toplevel(), self.controller.current_admin_id, maint_data=m, callback=self.refresh)
        else:
            messagebox.showerror("Error", "No se encontró el registro.", parent=self.winfo_toplevel())

    def _delete_maint(self, maint_id):
        if messagebox.askyesno("Confirmar", "¿Eliminar este registro de mantenimiento?", parent=self.winfo_toplevel()):
            ok, msg = database.delete_maintenance(maint_id, self.controller.current_admin_id)
            if ok:
                self.refresh()
            else:
                messagebox.showerror("Error", msg, parent=self.winfo_toplevel())
