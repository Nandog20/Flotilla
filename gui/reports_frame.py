"""
Pantalla 7 — Reportes.
Permite seleccionar un vehículo o un conductor específico desde un
dropdown y ver TODOS sus gastos detallados con el total acumulado.
"""

import customtkinter as ctk
import datetime
import database


class ReportsFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        self._current_mode = "vehiculo"
        self._vehicle_map = {}   # display_text -> vehicle_id
        self._driver_list = []   # [name, ...]

        self.grid_rowconfigure(3, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # ---- Row 0: Barra superior ----
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
            top, text="📊  Reportes",
            font=ctk.CTkFont(size=22, weight="bold"),
        ).grid(row=0, column=1, sticky="w", padx=10)

        # ---- Row 1: Selector de modo + ComboBox ----
        selector_bar = ctk.CTkFrame(self, corner_radius=8)
        selector_bar.grid(row=1, column=0, sticky="ew", padx=15, pady=(8, 10))
        selector_bar.grid_columnconfigure(2, weight=1)

        ctk.CTkLabel(
            selector_bar, text="  Reporte por:",
            font=ctk.CTkFont(size=13, weight="bold"),
        ).grid(row=0, column=0, padx=(12, 8), pady=12, sticky="w")

        self.segment_btn = ctk.CTkSegmentedButton(
            selector_bar,
            values=["🚗  Vehículo", "👷  Conductor"],
            command=self._on_mode_change,
            font=ctk.CTkFont(size=13, weight="bold"),
            selected_color="#3B82F6",
            selected_hover_color="#2563EB",
        )
        self.segment_btn.grid(row=0, column=1, padx=(0, 15), pady=12, sticky="w")
        self.segment_btn.set("🚗  Vehículo")

        ctk.CTkLabel(
            selector_bar, text="Seleccionar:",
            font=ctk.CTkFont(size=13),
        ).grid(row=0, column=2, padx=(10, 5), pady=12, sticky="e")

        self.combo_select = ctk.CTkComboBox(
            selector_bar, width=320, height=36,
            state="readonly",
            command=self._on_selection_change,
            font=ctk.CTkFont(size=13),
        )
        self.combo_select.grid(row=0, column=3, padx=(0, 12), pady=12, sticky="e")

        # ---- Filtro de fechas dentro del selector ----
        ctk.CTkLabel(
            selector_bar, text="📅 Desde:",
            font=ctk.CTkFont(size=12),
        ).grid(row=1, column=0, padx=(12, 4), pady=(0, 12), sticky="w")

        self.entry_date_from = ctk.CTkEntry(
            selector_bar, placeholder_text="DD/MM/AAAA", width=120, height=32)
        self.entry_date_from.grid(row=1, column=1, padx=(0, 10), pady=(0, 12), sticky="w")

        ctk.CTkLabel(
            selector_bar, text="Hasta:",
            font=ctk.CTkFont(size=12),
        ).grid(row=1, column=2, padx=(10, 4), pady=(0, 12), sticky="e")

        date_actions = ctk.CTkFrame(selector_bar, fg_color="transparent")
        date_actions.grid(row=1, column=3, padx=(0, 12), pady=(0, 12), sticky="e")

        self.entry_date_to = ctk.CTkEntry(
            date_actions, placeholder_text="DD/MM/AAAA", width=120, height=32)
        self.entry_date_to.grid(row=0, column=0, padx=(0, 8))

        ctk.CTkButton(
            date_actions, text="Filtrar", width=70, height=32,
            fg_color="#3B82F6", hover_color="#2563EB",
            command=lambda: self._on_selection_change(self.combo_select.get()),
        ).grid(row=0, column=1, padx=(0, 5))

        ctk.CTkButton(
            date_actions, text="Limpiar", width=70, height=32,
            fg_color="#6B7280", hover_color="#4B5563",
            command=self._clear_date_filter,
        ).grid(row=0, column=2)

        # ---- Row 2: Tarjetas resumen del seleccionado ----
        cards = ctk.CTkFrame(self, fg_color="transparent")
        cards.grid(row=2, column=0, padx=15, pady=(5, 5), sticky="ew")
        cards.grid_columnconfigure((0, 1), weight=1)

        self.card_total = self._make_card(
            cards, "💰  Total Gastado", "$0.00", "#10B981", 0,
        )
        self.card_count = self._make_card(
            cards, "📝  Número de Gastos", "0", "#3B82F6", 1,
        )

        # ---- Row 3: Tabla de gastos detallados ----
        table_container = ctk.CTkFrame(self)
        table_container.grid(row=3, column=0, sticky="nsew", padx=15, pady=(5, 12))

        self.table_scroll = ctk.CTkScrollableFrame(table_container)
        self.table_scroll.pack(fill="both", expand=True, padx=6, pady=6)

    # -----------------------------------------------------------------
    #  Tarjeta reutilizable
    # -----------------------------------------------------------------

    def _make_card(self, parent, title, value, accent, col):
        card = ctk.CTkFrame(
            parent, corner_radius=14, height=100,
            border_width=2, border_color=accent,
        )
        card.grid(row=0, column=col, padx=10, pady=5, sticky="nsew")
        card.grid_propagate(False)
        card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            card, text=title,
            font=ctk.CTkFont(size=12), text_color="gray",
        ).grid(row=0, column=0, padx=18, pady=(16, 4), sticky="w")

        lbl_val = ctk.CTkLabel(
            card, text=value,
            font=ctk.CTkFont(size=28, weight="bold"),
        )
        lbl_val.grid(row=1, column=0, padx=18, pady=(0, 16), sticky="w")
        return lbl_val

    # -----------------------------------------------------------------
    #  Cambio de modo
    # -----------------------------------------------------------------

    def _on_mode_change(self, value):
        if "Vehículo" in value:
            self._current_mode = "vehiculo"
        else:
            self._current_mode = "conductor"
        self._populate_combo()

    def _populate_combo(self):
        """Llena el ComboBox según el modo actual."""
        admin_id = self.controller.current_admin_id

        if self._current_mode == "vehiculo":
            vehicles = database.get_all_vehicles_for_combo(admin_id)
            self._vehicle_map = {display: v_id for v_id, display in vehicles}
            combo_vals = list(self._vehicle_map.keys())
        else:
            self._driver_list = database.get_drivers_for_report_combo(admin_id)
            combo_vals = self._driver_list

        if combo_vals:
            self.combo_select.configure(values=combo_vals)
            self.combo_select.set(combo_vals[0])
            self._on_selection_change(combo_vals[0])
        else:
            placeholder = "Sin vehículos registrados" if self._current_mode == "vehiculo" else "Sin conductores registrados"
            self.combo_select.configure(values=[placeholder])
            self.combo_select.set(placeholder)
            self._clear_report()

    # -----------------------------------------------------------------
    #  Selección en ComboBox
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
        self._on_selection_change(self.combo_select.get())

    def _on_selection_change(self, value):
        """Se ejecuta cuando el usuario elige un vehículo o conductor."""
        admin_id = self.controller.current_admin_id
        date_from = self._parse_filter_date(self.entry_date_from.get())
        date_to = self._parse_filter_date(self.entry_date_to.get())

        if self._current_mode == "vehiculo":
            vehicle_id = self._vehicle_map.get(value)
            if not vehicle_id:
                self._clear_report()
                return
            rows = database.get_expenses(admin_id, vehicle_id=vehicle_id,
                                         date_from=date_from, date_to=date_to)
        else:
            if value not in self._driver_list:
                self._clear_report()
                return
            rows = database.get_expenses_by_driver(admin_id, value,
                                                   date_from=date_from, date_to=date_to)

        # Calcular resumen
        total = sum(r[5] for r in rows)  # index 5 = amount
        count = len([r for r in rows if r[5] > 0])

        self.card_total.configure(text=f"${total:,.2f}")
        self.card_count.configure(text=str(count))

        # Dibujar tabla
        self._draw_expense_table(rows)

    def _clear_report(self):
        """Limpia tarjetas y tabla."""
        self.card_total.configure(text="$0.00")
        self.card_count.configure(text="0")
        for w in self.table_scroll.winfo_children():
            w.destroy()

    # -----------------------------------------------------------------
    #  Tabla de gastos detallados
    # -----------------------------------------------------------------

    def _draw_expense_table(self, rows):
        for w in self.table_scroll.winfo_children():
            w.destroy()

        # Headers cambian según el modo
        if self._current_mode == "vehiculo":
            headers = ["Fecha", "Categoría", "Concepto", "Conductor", "Monto"]
        else:
            headers = ["Fecha", "Vehículo", "Categoría", "Concepto", "Monto"]

        # Header
        hf = ctk.CTkFrame(
            self.table_scroll, fg_color=("gray85", "gray20"), corner_radius=6)
        hf.pack(fill="x", pady=(0, 4))
        for i in range(len(headers)):
            hf.grid_columnconfigure(i, weight=1)
        for i, h in enumerate(headers):
            ctk.CTkLabel(hf, text=h, font=ctk.CTkFont(weight="bold")).grid(
                row=0, column=i, padx=6, pady=8, sticky="w")

        if not rows:
            ctk.CTkLabel(
                self.table_scroll,
                text="No se encontraron gastos para esta selección.",
                font=ctk.CTkFont(size=14, slant="italic"), text_color="gray",
            ).pack(pady=40)
            return

        # Filas
        for idx, row in enumerate(rows):
            # row = (id, plates, vehicle_name, category, concept, amount, date, observations, vehicle_id, maint_id, driver_name)
            bg = ("#F8FAFC", "#1E293B") if idx % 2 == 0 else ("#EFF6FF", "#0F172A")
            self._draw_expense_row(bg, row)

        # ---- Fila TOTAL al final ----
        total = sum(r[5] for r in rows)
        tf = ctk.CTkFrame(
            self.table_scroll, fg_color=("#D1FAE5", "#064E3B"), corner_radius=6)
        tf.pack(fill="x", pady=(6, 0))
        for i in range(len(headers)):
            tf.grid_columnconfigure(i, weight=1)

        ctk.CTkLabel(
            tf, text="TOTAL",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).grid(row=0, column=0, padx=6, pady=10, sticky="w")

        # Poner el total en la última columna (Monto)
        ctk.CTkLabel(
            tf, text=f"${total:,.2f}",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=("#059669", "#34D399"),
        ).grid(row=0, column=len(headers) - 1, padx=6, pady=10, sticky="w")

    def _draw_expense_row(self, bg, row_data):
        e_id, plates, v_name, cat, concept, amount, date, obs, v_id, maint_id, driver_name = row_data

        rf = ctk.CTkFrame(self.table_scroll, fg_color=bg, corner_radius=4)
        rf.pack(fill="x", pady=1)

        if self._current_mode == "vehiculo":
            num_cols = 5
        else:
            num_cols = 5

        for i in range(num_cols):
            rf.grid_columnconfigure(i, weight=1)

        # Fecha
        try:
            display_date = datetime.datetime.strptime(date, "%Y-%m-%d").strftime("%d/%m/%Y")
        except Exception:
            display_date = date
        ctk.CTkLabel(rf, text=display_date).grid(
            row=0, column=0, padx=6, pady=6, sticky="w")

        if self._current_mode == "vehiculo":
            # Categoría | Concepto | Conductor | Monto
            ctk.CTkLabel(rf, text=cat).grid(
                row=0, column=1, padx=6, pady=6, sticky="w")

            display_concept = (concept[:30] + '...') if len(concept) > 30 else concept
            ctk.CTkLabel(rf, text=display_concept, font=ctk.CTkFont(size=12)).grid(
                row=0, column=2, padx=6, pady=6, sticky="w")

            display_driver = driver_name if driver_name else "—"
            d_color = {} if driver_name else {"text_color": "gray"}
            ctk.CTkLabel(rf, text=display_driver, font=ctk.CTkFont(size=12), **d_color).grid(
                row=0, column=3, padx=6, pady=6, sticky="w")
        else:
            # Vehículo | Categoría | Concepto | Monto
            vehicle_str = f"{plates} - {v_name}"
            ctk.CTkLabel(rf, text=vehicle_str, font=ctk.CTkFont(size=12, weight="bold")).grid(
                row=0, column=1, padx=6, pady=6, sticky="w")

            ctk.CTkLabel(rf, text=cat).grid(
                row=0, column=2, padx=6, pady=6, sticky="w")

            display_concept = (concept[:30] + '...') if len(concept) > 30 else concept
            ctk.CTkLabel(rf, text=display_concept, font=ctk.CTkFont(size=12)).grid(
                row=0, column=3, padx=6, pady=6, sticky="w")

        # Monto (última columna en ambos modos)
        amount_color = "#10B981" if float(amount) == 0 else ("#DC2626", "#F87171")
        ctk.CTkLabel(
            rf, text=f"${amount:,.2f}",
            text_color=amount_color, font=ctk.CTkFont(weight="bold"),
        ).grid(row=0, column=4, padx=6, pady=6, sticky="w")

    # -----------------------------------------------------------------
    #  Refresh (llamado al navegar a esta pantalla)
    # -----------------------------------------------------------------

    def refresh(self):
        self._populate_combo()
