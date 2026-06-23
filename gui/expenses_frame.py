import customtkinter as ctk
from tkinter import messagebox
import datetime
import database
from gui.dialogs import ExpenseDialog
try:
    from tkcalendar import DateEntry
except ImportError:
    DateEntry = None

class ExpensesFrame(ctk.CTkFrame):
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
            command=controller.show_dashboard,
        ).grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(
            top, text="💰  Gastos",
            font=ctk.CTkFont(size=22, weight="bold"),
        ).grid(row=0, column=1, sticky="w", padx=10)

        ctk.CTkButton(
            top, text="✚ Registrar Gasto",
            width=140, height=35,
            fg_color="#10B981", hover_color="#059669",
            font=ctk.CTkFont(weight="bold"),
            command=self._open_add,
        ).grid(row=0, column=2, sticky="e")

        # ---- Barra de búsqueda ----
        search_bar = ctk.CTkFrame(self, corner_radius=8)
        search_bar.grid(row=1, column=0, sticky="ew", padx=15, pady=(5, 10))
        search_bar.grid_columnconfigure(0, weight=1)

        self.entry_search = ctk.CTkEntry(
            search_bar,
            placeholder_text="🔍  Buscar por vehículo, categoría, concepto...",
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

        self.date_from_var = ctk.StringVar()
        self.date_from_var.trace_add("write", lambda *a: self._filter_date_chars(self.date_from_var))
        self.date_to_var = ctk.StringVar()
        self.date_to_var.trace_add("write", lambda *a: self._filter_date_chars(self.date_to_var))

        if DateEntry:
            self.entry_date_from = DateEntry(date_filter, textvariable=self.date_from_var, width=12, background='darkblue', foreground='white', borderwidth=2, date_pattern='dd/mm/yyyy')
            self.entry_date_from.grid(row=0, column=2, padx=(0, 10), pady=10)
            self.entry_date_from.delete(0, 'end')
        else:
            self.entry_date_from = ctk.CTkEntry(
                date_filter, textvariable=self.date_from_var, placeholder_text="DD/MM/AAAA", width=120, height=32)
            self.entry_date_from.grid(row=0, column=2, padx=(0, 10), pady=10)

        ctk.CTkLabel(date_filter, text="Hasta:", font=ctk.CTkFont(size=12)).grid(
            row=0, column=3, padx=(10, 4), pady=10, sticky="w")

        if DateEntry:
            self.entry_date_to = DateEntry(date_filter, textvariable=self.date_to_var, width=12, background='darkblue', foreground='white', borderwidth=2, date_pattern='dd/mm/yyyy')
            self.entry_date_to.grid(row=0, column=4, padx=(0, 10), pady=10)
            self.entry_date_to.delete(0, 'end')
        else:
            self.entry_date_to = ctk.CTkEntry(
                date_filter, textvariable=self.date_to_var, placeholder_text="DD/MM/AAAA", width=120, height=32)
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

        headers = ["Vehículo", "Conductor", "Categoría", "Concepto", "Monto", "Fecha", "Acciones"]
        self._draw_header(headers)

        query = self.entry_search.get()
        date_from_str = self.entry_date_from.get().strip()
        date_to_str = self.entry_date_to.get().strip()
        
        date_from = self._parse_filter_date(date_from_str)
        date_to = self._parse_filter_date(date_to_str)
        
        if date_from_str and not date_from:
            messagebox.showwarning("Error de fecha", "La fecha 'Desde' tiene un formato inválido. Use DD/MM/AAAA.", parent=self.winfo_toplevel())
            return
        if date_to_str and not date_to:
            messagebox.showwarning("Error de fecha", "La fecha 'Hasta' tiene un formato inválido. Use DD/MM/AAAA.", parent=self.winfo_toplevel())
            return
        if date_from and date_to and date_from > date_to:
            messagebox.showwarning("Fechas incongruentes", "La fecha de inicio ('Desde') debe ser anterior o igual a la fecha de fin ('Hasta').", parent=self.winfo_toplevel())
            return

        rows = database.get_expenses(self.controller.current_admin_id, query,
                                     date_from=date_from, date_to=date_to)

        if not rows:
            ctk.CTkLabel(
                self.table_scroll, text="No se encontraron gastos.",
                font=ctk.CTkFont(size=14, slant="italic"), text_color="gray",
            ).pack(pady=40)
            return

        for idx, e in enumerate(rows):
            # e = (id, plates, vehicle_name, category, concept, amount, date, observations, vehicle_id, maint_id)
            bg = ("#F8FAFC", "#1E293B") if idx % 2 == 0 else ("#EFF6FF", "#0F172A")
            self._draw_row(bg, e)

        # ---- Fila TOTAL al final ----
        total = sum(r[5] for r in rows)
        tf = ctk.CTkFrame(
            self.table_scroll, fg_color=("#D1FAE5", "#064E3B"), corner_radius=6)
        tf.pack(fill="x", pady=(6, 0))
        for i in range(len(headers)):
            tf.grid_columnconfigure(i, weight=1 if i < 6 else 0, uniform="exp_cols")

        ctk.CTkLabel(
            tf, text="TOTAL",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).grid(row=0, column=0, padx=6, pady=10, sticky="w")

        ctk.CTkLabel(
            tf, text=f"${total:,.2f}",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=("#059669", "#34D399"),
        ).grid(row=0, column=4, padx=6, pady=10, sticky="w")

    def _draw_header(self, headers):
        frame = ctk.CTkFrame(self.table_scroll, fg_color=("gray85", "gray20"), corner_radius=6)
        frame.pack(fill="x", pady=(0, 4))
        for i in range(len(headers)):
            frame.grid_columnconfigure(i, weight=1 if i < 6 else 0, uniform="exp_cols")
        for i, h in enumerate(headers):
            ctk.CTkLabel(frame, text=h, font=ctk.CTkFont(weight="bold")).grid(
                row=0, column=i, padx=6, pady=8, sticky="w")

    def _draw_row(self, bg, row_data):
        e_id, plates, v_name, cat, concept, amount, date, obs, v_id, maint_id, driver_name = row_data
        rf = ctk.CTkFrame(self.table_scroll, fg_color=bg, corner_radius=4)
        rf.pack(fill="x", pady=1)
        for i in range(7):
            rf.grid_columnconfigure(i, weight=1 if i < 6 else 0, uniform="exp_cols")

        vehicle_str = f"{plates} - {v_name}"
        ctk.CTkLabel(rf, text=vehicle_str, font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=6, pady=6, sticky="w")

        # Conductor
        display_driver = driver_name if driver_name else "Sin conductor"
        driver_color = {} if driver_name else {"text_color": "gray"}
        ctk.CTkLabel(rf, text=display_driver, font=ctk.CTkFont(size=12), **driver_color).grid(row=0, column=1, padx=6, pady=6, sticky="w")

        # Categoría
        ctk.CTkLabel(rf, text=cat).grid(row=0, column=2, padx=6, pady=6, sticky="w")

        # Concepto
        display_concept = (concept[:25] + '...') if len(concept) > 25 else concept
        ctk.CTkLabel(rf, text=display_concept).grid(row=0, column=3, padx=6, pady=6, sticky="w")

        # Monto
        amount_color = "#10B981" if float(amount) == 0 else ("#DC2626", "#F87171")
        ctk.CTkLabel(rf, text=f"${amount:,.2f}", text_color=amount_color, font=ctk.CTkFont(weight="bold")).grid(row=0, column=4, padx=6, pady=6, sticky="w")

        # Fecha
        try:
            display_date = datetime.datetime.strptime(date, "%Y-%m-%d").strftime("%d/%m/%Y")
        except Exception:
            display_date = date
        ctk.CTkLabel(rf, text=display_date).grid(row=0, column=5, padx=6, pady=6, sticky="w")

        # Acciones
        actions = ctk.CTkFrame(rf, fg_color="transparent")
        actions.grid(row=0, column=6, padx=4, pady=2, sticky="e")

        ctk.CTkButton(
            actions, text="✏️", width=32, height=26,
            command=lambda eid=e_id: self._open_edit(eid),
        ).grid(row=0, column=0, padx=2)

        btn_del = ctk.CTkButton(
            actions, text="🗑️", width=32, height=26,
            fg_color="#EF4444", hover_color="#B91C1C",
            command=lambda eid=e_id: self._delete(eid),
        )
        btn_del.grid(row=0, column=1, padx=2)

        # Si viene de mantenimiento, se bloquea el borrado
        if maint_id is not None:
            btn_del.configure(state="disabled", fg_color="gray", hover_color="gray")

    def _open_add(self):
        ExpenseDialog(self.winfo_toplevel(), self.controller.current_admin_id, callback=self.refresh)

    def _open_edit(self, expense_id):
        # expense_data = (id, vehicle_id, category, concept, amount, date, observations, maint_id)
        data = database.get_expense_by_id(expense_id, self.controller.current_admin_id)
        if data:
            ExpenseDialog(self.winfo_toplevel(), self.controller.current_admin_id, expense_data=data, callback=self.refresh)

    def _delete(self, expense_id):
        ans = messagebox.askyesno("Confirmar", "¿Eliminar este gasto de forma permanente?", parent=self)
        if ans:
            ok, msg = database.delete_expense(expense_id, self.controller.current_admin_id)
            if ok:
                self.refresh()
            else:
                messagebox.showerror("Error", msg, parent=self)

    def _filter_date_chars(self, var):
        val = var.get()
        filtered = ''.join(c for c in val if c.isdigit() or c == '/')
        if val != filtered:
            var.set(filtered)
