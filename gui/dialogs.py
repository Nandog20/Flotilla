"""
Diálogos reutilizables — Ventanas emergentes para Agregar / Editar
registros de Vehículos y Conductores.

NOTA: Se usa self.after(150, self._build_ui) para evitar el bug
conocido de CTkToplevel donde la ventana aparece en blanco si los
widgets se crean directamente en __init__.
"""

import customtkinter as ctk
from tkinter import messagebox
import datetime
import database
try:
    from tkcalendar import DateEntry
except ImportError:
    DateEntry = None


# =====================================================================
#  DIÁLOGO DE VEHÍCULO
# =====================================================================

class VehicleDialog(ctk.CTkToplevel):
    """Popup para agregar o editar un vehículo."""

    def __init__(self, parent, admin_id, vehicle_data=None, callback=None):
        super().__init__(parent)
        self.admin_id = admin_id
        self.vehicle_data = vehicle_data
        self.callback = callback

        self._title_text = "Editar Vehículo" if vehicle_data else "Agregar Vehículo"
        self.title(self._title_text)
        self.geometry("480x520")
        self.resizable(False, False)
        self.transient(parent)

        # Retrasar la construcción de widgets para evitar ventana vacía
        self.after(150, self._build_ui)

    def _build_ui(self):
        self.grab_set()
        self.grid_columnconfigure((0, 1), weight=1)

        # Encabezado
        ctk.CTkLabel(
            self, text=f"🚗  {self._title_text}",
            font=ctk.CTkFont(size=20, weight="bold"),
        ).grid(row=0, column=0, columnspan=2, pady=(25, 22))

        # Campos del formulario
        fields_cfg = [
            ("Marca:",       "entry_brand",   "Ej: Toyota"),
            ("Modelo:",      "entry_model",   "Ej: Hilux"),
            ("Año:",         "entry_year",    f"Ej: {datetime.date.today().year}"),
            ("Placas:",      "entry_plates",  "Ej: ABC-1234"),
            ("VIN:",         "entry_vin",     "17 caracteres"),
            ("Kilometraje:", "entry_mileage", "Ej: 50000"),
        ]

        for i, (label, attr, ph) in enumerate(fields_cfg, start=1):
            ctk.CTkLabel(self, text=label, anchor="w").grid(
                row=i, column=0, padx=30, pady=7, sticky="w")
            
            if attr == "entry_vin":
                frame_vin = ctk.CTkFrame(self, fg_color="transparent")
                frame_vin.grid(row=i, column=1, padx=30, pady=7, sticky="ew")
                frame_vin.grid_columnconfigure(0, weight=1)
                
                entry = ctk.CTkEntry(frame_vin, placeholder_text=ph)
                entry.grid(row=0, column=0, sticky="ew")
                setattr(self, attr, entry)
                
                self.vin_var = ctk.StringVar()
                entry.configure(textvariable=self.vin_var)
                self.lbl_vin_warn = ctk.CTkLabel(frame_vin, text="", font=ctk.CTkFont(size=11, weight="bold"))
                self.lbl_vin_warn.grid(row=0, column=1, padx=(5, 0))
                self.vin_var.trace_add("write", self._validate_vin)
            else:
                entry = ctk.CTkEntry(self, placeholder_text=ph)
                entry.grid(row=i, column=1, padx=30, pady=7, sticky="ew")
                setattr(self, attr, entry)

        # Estado (ComboBox)
        row_status = len(fields_cfg) + 1
        ctk.CTkLabel(self, text="Estado:", anchor="w").grid(
            row=row_status, column=0, padx=30, pady=7, sticky="w")
        self.combo_status = ctk.CTkComboBox(
            self, values=["Activo", "Inactivo"], state="readonly")
        self.combo_status.grid(
            row=row_status, column=1, padx=30, pady=7, sticky="ew")
        self.combo_status.set("Activo")

        # Pre-llenar si estamos editando
        # vehicle_data = (id, brand, model, year, plates, vin, mileage, status)
        if self.vehicle_data:
            self.entry_brand.insert(0, self.vehicle_data[1])
            self.entry_model.insert(0, self.vehicle_data[2])
            self.entry_year.insert(0, str(self.vehicle_data[3]))
            self.entry_plates.insert(0, self.vehicle_data[4])
            self.entry_vin.insert(0, self.vehicle_data[5])
            self.entry_mileage.insert(0, str(self.vehicle_data[6]))
            self.combo_status.set(self.vehicle_data[7])

        # Botones
        btn_row = row_status + 1
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.grid(row=btn_row, column=0, columnspan=2, pady=(25, 20), sticky="ew")
        btn_frame.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkButton(
            btn_frame, text="💾  Guardar", width=140, height=40,
            fg_color="#10B981", hover_color="#059669",
            font=ctk.CTkFont(weight="bold"),
            command=self._save,
        ).grid(row=0, column=0, padx=20)

        ctk.CTkButton(
            btn_frame, text="Cancelar", width=140, height=40,
            fg_color="#6B7280", hover_color="#4B5563",
            command=self.destroy,
        ).grid(row=0, column=1, padx=20)

    def _validate_vin(self, *args):
        val = self.vin_var.get()
        if len(val) > 17:
            self.vin_var.set(val[:17])
            val = val[:17]
        
        if len(val) == 0:
            self.lbl_vin_warn.configure(text="")
        elif len(val) < 17:
            self.lbl_vin_warn.configure(text="⚠️ Incompleto", text_color="#F59E0B")
        else:
            self.lbl_vin_warn.configure(text="✅", text_color="#10B981")

    def _save(self):
        brand = self.entry_brand.get().strip()
        model = self.entry_model.get().strip()
        year_s = self.entry_year.get().strip()
        plates = self.entry_plates.get().strip()
        vin = self.entry_vin.get().strip()
        mileage_s = self.entry_mileage.get().strip()
        status = self.combo_status.get()

        if not all([brand, model, year_s, plates, vin, mileage_s]):
            messagebox.showwarning(
                "Campos vacíos", "Todos los campos son obligatorios.",
                parent=self)
            return

        try:
            year = int(year_s)
            if year < 1900 or year > datetime.date.today().year + 2:
                raise ValueError
        except ValueError:
            messagebox.showwarning(
                "Año inválido", "Ingresa un año válido.", parent=self)
            return

        try:
            mileage = int(mileage_s)
            if mileage < 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning(
                "Kilometraje inválido",
                "Ingresa un número entero positivo.", parent=self)
            return

        if self.vehicle_data:
            ok, msg = database.update_vehicle(
                self.vehicle_data[0], self.admin_id,
                brand, model, year, plates, vin, mileage, status)
        else:
            ok, msg = database.add_vehicle(
                self.admin_id, brand, model, year,
                plates, vin, mileage, status)

        if ok:
            if self.callback:
                self.callback()
            self.destroy()
        else:
            messagebox.showerror("Error", msg, parent=self)


# =====================================================================
#  DIÁLOGO DE CONDUCTOR
# =====================================================================

class DriverDialog(ctk.CTkToplevel):
    """Popup para agregar o editar un conductor."""

    def __init__(self, parent, admin_id, driver_data=None, callback=None):
        super().__init__(parent)
        self.admin_id = admin_id
        self.driver_data = driver_data
        self.callback = callback

        self._title_text = "Editar Conductor" if driver_data else "Agregar Conductor"
        self.title(self._title_text)
        self.geometry("500x520")
        self.resizable(False, False)
        self.transient(parent)

        # Retrasar la construcción de widgets para evitar ventana vacía
        self.after(150, self._build_ui)

    def _build_ui(self):
        self.grab_set()
        self.grid_columnconfigure((0, 1), weight=1)

        # Encabezado
        ctk.CTkLabel(
            self, text=f"👷  {self._title_text}",
            font=ctk.CTkFont(size=20, weight="bold"),
        ).grid(row=0, column=0, columnspan=2, pady=(25, 22))

        # --- Campos ---
        ctk.CTkLabel(self, text="Nombre:", anchor="w").grid(
            row=1, column=0, padx=30, pady=7, sticky="w")
        self.entry_name = ctk.CTkEntry(self, placeholder_text="Nombre completo")
        self.entry_name.grid(row=1, column=1, padx=30, pady=7, sticky="ew")

        ctk.CTkLabel(self, text="Teléfono:", anchor="w").grid(
            row=2, column=0, padx=30, pady=7, sticky="w")
        self.entry_phone = ctk.CTkEntry(self, placeholder_text="10 dígitos")
        self.entry_phone.grid(row=2, column=1, padx=30, pady=7, sticky="ew")

        ctk.CTkLabel(self, text="Dirección:", anchor="w").grid(
            row=3, column=0, padx=30, pady=7, sticky="w")
        self.entry_address = ctk.CTkEntry(self, placeholder_text="Dirección completa")
        self.entry_address.grid(row=3, column=1, padx=30, pady=7, sticky="ew")

        ctk.CTkLabel(self, text="CURP:", anchor="w").grid(
            row=4, column=0, padx=30, pady=7, sticky="w")
        
        frame_curp = ctk.CTkFrame(self, fg_color="transparent")
        frame_curp.grid(row=4, column=1, padx=30, pady=7, sticky="ew")
        frame_curp.grid_columnconfigure(0, weight=1)
        
        self.entry_curp = ctk.CTkEntry(frame_curp, placeholder_text="18 caracteres")
        self.entry_curp.grid(row=0, column=0, sticky="ew")
        
        self.curp_var = ctk.StringVar()
        self.entry_curp.configure(textvariable=self.curp_var)
        self.lbl_curp_warn = ctk.CTkLabel(frame_curp, text="", font=ctk.CTkFont(size=11, weight="bold"))
        self.lbl_curp_warn.grid(row=0, column=1, padx=(5, 0))
        self.curp_var.trace_add("write", self._validate_curp)

        ctk.CTkLabel(self, text="Estado:", anchor="w").grid(
            row=5, column=0, padx=30, pady=7, sticky="w")
        self.combo_status = ctk.CTkComboBox(
            self, values=["Activo", "Suspendido", "Baja"], state="readonly")
        self.combo_status.grid(row=5, column=1, padx=30, pady=7, sticky="ew")
        self.combo_status.set("Activo")

        # --- Vehículo asignado ---
        ctk.CTkLabel(self, text="Vehículo:", anchor="w").grid(
            row=6, column=0, padx=30, pady=7, sticky="w")

        current_driver_id = self.driver_data[0] if self.driver_data else None
        current_vehicle_id = self.driver_data[6] if self.driver_data else None
        vehicles = database.get_vehicles_for_combo(self.admin_id, current_driver_id, current_vehicle_id)
        self.vehicle_map = {"Sin asignar": None}
        combo_vals = ["Sin asignar"]
        for v_id, display in vehicles:
            combo_vals.append(display)
            self.vehicle_map[display] = v_id

        self.combo_vehicle = ctk.CTkComboBox(
            self, values=combo_vals, state="readonly")
        self.combo_vehicle.grid(row=6, column=1, padx=30, pady=7, sticky="ew")
        self.combo_vehicle.set("Sin asignar")

        # Pre-llenar si estamos editando
        # driver_data = (id, name, phone, address, curp, status, vehicle_id)
        if self.driver_data:
            self.entry_name.insert(0, self.driver_data[1])
            self.entry_phone.insert(0, self.driver_data[2])
            self.entry_address.insert(0, self.driver_data[3] or "")
            self.entry_curp.insert(0, self.driver_data[4])
            self.combo_status.set(self.driver_data[5])
            if self.driver_data[6]:
                for display, v_id in self.vehicle_map.items():
                    if v_id == self.driver_data[6]:
                        self.combo_vehicle.set(display)
                        break

        # Botones
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.grid(row=7, column=0, columnspan=2, pady=(25, 20), sticky="ew")
        btn_frame.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkButton(
            btn_frame, text="💾  Guardar", width=140, height=40,
            fg_color="#10B981", hover_color="#059669",
            font=ctk.CTkFont(weight="bold"),
            command=self._save,
        ).grid(row=0, column=0, padx=20)

        ctk.CTkButton(
            btn_frame, text="Cancelar", width=140, height=40,
            fg_color="#6B7280", hover_color="#4B5563",
            command=self.destroy,
        ).grid(row=0, column=1, padx=20)

    def _validate_curp(self, *args):
        val = self.curp_var.get()
        if len(val) > 18:
            self.curp_var.set(val[:18])
            val = val[:18]
        
        if len(val) == 0:
            self.lbl_curp_warn.configure(text="")
        elif len(val) < 18:
            self.lbl_curp_warn.configure(text="⚠️ Incompleto", text_color="#F59E0B")
        else:
            self.lbl_curp_warn.configure(text="✅", text_color="#10B981")

    def _save(self):
        name = self.entry_name.get().strip()
        phone = self.entry_phone.get().strip()
        address = self.entry_address.get().strip()
        curp = self.entry_curp.get().strip()
        status = self.combo_status.get()
        vehicle_str = self.combo_vehicle.get()
        vehicle_id = self.vehicle_map.get(vehicle_str)

        if not name or not phone or not curp:
            messagebox.showwarning(
                "Campos vacíos",
                "Nombre, teléfono y CURP son obligatorios.", parent=self)
            return

        if len(curp) != 18:
            messagebox.showwarning(
                "CURP inválido",
                "El CURP debe tener exactamente 18 caracteres.", parent=self)
            return

        if self.driver_data:
            ok, msg = database.update_driver(
                self.driver_data[0], self.admin_id,
                name, phone, address, curp, status, vehicle_id)
        else:
            ok, msg = database.add_driver(
                self.admin_id, name, phone, address,
                curp, status, vehicle_id)

        if ok:
            if self.callback:
                self.callback()
            self.destroy()
        else:
            messagebox.showerror("Error", msg, parent=self)


# =====================================================================
#  DIÁLOGO DE MANTENIMIENTO
# =====================================================================

class MaintenanceDialog(ctk.CTkToplevel):
    """Popup para registrar o editar un mantenimiento."""

    def __init__(self, parent, admin_id, maint_data=None, callback=None):
        super().__init__(parent)
        self.admin_id = admin_id
        # maint_data = (id, vehicle_id, date, end_date, service_type, description)
        self.maint_data = maint_data
        self.callback = callback

        self._title_text = "Editar Mantenimiento" if maint_data else "Registrar Mantenimiento"
        self.title(self._title_text)
        self.geometry("520x580")
        self.resizable(False, False)
        self.transient(parent)

        self.after(150, self._build_ui)

    def _build_ui(self):
        self.grab_set()
        self.grid_columnconfigure((0, 1), weight=1)

        # Encabezado
        ctk.CTkLabel(
            self, text=f"🔧  {self._title_text}",
            font=ctk.CTkFont(size=20, weight="bold"),
        ).grid(row=0, column=0, columnspan=2, pady=(25, 22))

        # --- Vehículo ---
        ctk.CTkLabel(self, text="Vehículo:", anchor="w").grid(
            row=1, column=0, padx=30, pady=7, sticky="w")

        vehicles = database.get_all_vehicles_for_combo(self.admin_id)
        self.vehicle_map = {}
        combo_vals = []
        for v_id, display in vehicles:
            combo_vals.append(display)
            self.vehicle_map[display] = v_id

        self.combo_vehicle = ctk.CTkComboBox(self, values=combo_vals if combo_vals else ["Sin vehículos disponibles"], state="readonly")
        self.combo_vehicle.grid(row=1, column=1, padx=30, pady=7, sticky="ew")
        if combo_vals:
            self.combo_vehicle.set(combo_vals[0])

        # --- Fecha Inicio ---
        ctk.CTkLabel(self, text="Fecha de Inicio:", anchor="w").grid(
            row=2, column=0, padx=30, pady=7, sticky="w")
        if DateEntry:
            self.entry_date = DateEntry(self, width=12, background='darkblue', foreground='white', borderwidth=2, date_pattern='dd/mm/yyyy')
        else:
            self.entry_date = ctk.CTkEntry(self, placeholder_text="Ej: DD/MM/AAAA")
            
        self.entry_date.grid(row=2, column=1, padx=30, pady=7, sticky="ew")
        if not self.maint_data:
            self.entry_date.delete(0, 'end')
            self.entry_date.insert(0, datetime.date.today().strftime("%d/%m/%Y"))

        # --- Fecha Fin ---
        ctk.CTkLabel(self, text="Fecha Fin (Opcional):", anchor="w").grid(
            row=3, column=0, padx=30, pady=7, sticky="w")
        if DateEntry:
            self.entry_end_date = DateEntry(self, width=12, background='darkblue', foreground='white', borderwidth=2, date_pattern='dd/mm/yyyy')
        else:
            self.entry_end_date = ctk.CTkEntry(self, placeholder_text="Ej: DD/MM/AAAA")
            
        self.entry_end_date.grid(row=3, column=1, padx=30, pady=7, sticky="ew")
        self.entry_end_date.delete(0, 'end') # Start empty since it's optional

        # --- Tipo de Servicio ---
        ctk.CTkLabel(self, text="Tipo de Servicio:", anchor="w").grid(
            row=4, column=0, padx=30, pady=7, sticky="w")
        self.combo_type = ctk.CTkComboBox(
            self, values=["Cambio de aceite", "Cambio de llantas", "Afinación", "Reparación", "Mantenimiento completo"], state="readonly")
        self.combo_type.grid(row=4, column=1, padx=30, pady=7, sticky="ew")
        self.combo_type.set("Mantenimiento completo")

        # --- Descripción ---
        ctk.CTkLabel(self, text="Descripción:", anchor="nw").grid(
            row=5, column=0, padx=30, pady=7, sticky="nw")
        self.textbox_desc = ctk.CTkTextbox(self, height=80)
        self.textbox_desc.grid(row=5, column=1, padx=30, pady=7, sticky="ew")

        # Pre-llenar si editando
        if self.maint_data:
            # (id, vehicle_id, date, end_date, service_type, description)
            v_id = self.maint_data[1]
            for disp, vid in self.vehicle_map.items():
                if vid == v_id:
                    self.combo_vehicle.set(disp)
                    break
            self.entry_date.delete(0, 'end')
            try:
                display_date = datetime.datetime.strptime(self.maint_data[2], "%Y-%m-%d").strftime("%d/%m/%Y")
            except:
                display_date = self.maint_data[2]
            self.entry_date.insert(0, display_date)
            
            if self.maint_data[3]:
                try:
                    display_end_date = datetime.datetime.strptime(self.maint_data[3], "%Y-%m-%d").strftime("%d/%m/%Y")
                except:
                    display_end_date = self.maint_data[3]
                self.entry_end_date.insert(0, display_end_date)
                
            self.combo_type.set(self.maint_data[4])
            self.textbox_desc.insert("0.0", self.maint_data[5])

        # Botones
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.grid(row=6, column=0, columnspan=2, pady=(25, 20), sticky="ew")
        btn_frame.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkButton(
            btn_frame, text="💾  Guardar", width=140, height=40,
            fg_color="#10B981", hover_color="#059669",
            font=ctk.CTkFont(weight="bold"),
            command=self._save,
        ).grid(row=0, column=0, padx=20)

        ctk.CTkButton(
            btn_frame, text="Cancelar", width=140, height=40,
            fg_color="#6B7280", hover_color="#4B5563",
            command=self.destroy,
        ).grid(row=0, column=1, padx=20)

    def _save(self):
        vehicle_str = self.combo_vehicle.get()
        vehicle_id = self.vehicle_map.get(vehicle_str)
        date = self.entry_date.get().strip()
        end_date = self.entry_end_date.get().strip()
        srv_type = self.combo_type.get()
        desc = self.textbox_desc.get("0.0", "end").strip()

        if not vehicle_id:
            messagebox.showwarning("Error", "Debe seleccionar un vehículo válido.", parent=self)
            return
        if not date:
            messagebox.showwarning("Error", "La fecha de inicio es obligatoria.", parent=self)
            return

        try:
            parsed_date = datetime.datetime.strptime(date, "%d/%m/%Y").strftime("%Y-%m-%d")
        except ValueError:
            messagebox.showwarning("Error", "La fecha de inicio debe tener formato DD/MM/AAAA", parent=self)
            return
            
        parsed_end_date = None
        if end_date:
            try:
                parsed_end_date = datetime.datetime.strptime(end_date, "%d/%m/%Y").strftime("%Y-%m-%d")
            except ValueError:
                messagebox.showwarning("Error", "La fecha fin debe tener formato DD/MM/AAAA", parent=self)
                return

        if self.maint_data:
            ok, msg = database.update_maintenance(
                self.maint_data[0], self.admin_id, vehicle_id, parsed_date, srv_type, desc, parsed_end_date)
        else:
            ok, msg = database.add_maintenance(
                self.admin_id, vehicle_id, parsed_date, srv_type, desc, parsed_end_date)

        if ok:
            if self.callback:
                self.callback()
            self.destroy()
        else:
            messagebox.showerror("Error", msg, parent=self)


# =====================================================================
#  DIÁLOGO DE GASTOS
# =====================================================================

class ExpenseDialog(ctk.CTkToplevel):
    """Popup para registrar o editar un gasto."""

    def __init__(self, parent, admin_id, expense_data=None, callback=None):
        super().__init__(parent)
        self.admin_id = admin_id
        # expense_data = (id, vehicle_id, category, concept, amount, date, observations, maint_id)
        self.expense_data = expense_data
        self.callback = callback

        self._title_text = "Editar Gasto" if expense_data else "Registrar Gasto"
        self.title(self._title_text)
        self.geometry("520x650")
        self.resizable(False, False)
        self.transient(parent)

        self.after(150, self._build_ui)

    def _build_ui(self):
        self.grab_set()
        self.grid_columnconfigure((0, 1), weight=1)

        is_linked = bool(self.expense_data and self.expense_data[7])

        # Encabezado
        ctk.CTkLabel(
            self, text=f"💰  {self._title_text}",
            font=ctk.CTkFont(size=20, weight="bold"),
        ).grid(row=0, column=0, columnspan=2, pady=(25, 22))

        # --- Vehículo ---
        ctk.CTkLabel(self, text="Vehículo:", anchor="w").grid(
            row=1, column=0, padx=30, pady=7, sticky="w")
        vehicles = database.get_all_vehicles_for_combo(self.admin_id)
        self.vehicle_map = {}
        combo_vals = []
        for v_id, display in vehicles:
            combo_vals.append(display)
            self.vehicle_map[display] = v_id

        self.combo_vehicle = ctk.CTkComboBox(self, values=combo_vals if combo_vals else ["Sin vehículos disponibles"])
        self.combo_vehicle.grid(row=1, column=1, padx=30, pady=7, sticky="ew")
        if combo_vals:
            self.combo_vehicle.set(combo_vals[0])

        # --- Categoría ---
        ctk.CTkLabel(self, text="Categoría:", anchor="w").grid(
            row=2, column=0, padx=30, pady=7, sticky="w")
        self.combo_cat = ctk.CTkComboBox(
            self, values=["Seguro", "Mantenimiento", "Llantas", "Verificación", "Tenencia", "Reparación", "Otros"])
        self.combo_cat.grid(row=2, column=1, padx=30, pady=7, sticky="ew")
        self.combo_cat.set("Otros")

        # --- Concepto ---
        ctk.CTkLabel(self, text="Concepto:", anchor="w").grid(
            row=3, column=0, padx=30, pady=7, sticky="w")
        self.entry_concept = ctk.CTkEntry(self, placeholder_text="Ej: Cambio de balatas")
        self.entry_concept.grid(row=3, column=1, padx=30, pady=7, sticky="ew")

        # --- Monto ---
        ctk.CTkLabel(self, text="Monto ($):", anchor="w").grid(
            row=4, column=0, padx=30, pady=7, sticky="w")
        self.entry_amount = ctk.CTkEntry(self, placeholder_text="Ej: 1500.50")
        self.entry_amount.grid(row=4, column=1, padx=30, pady=7, sticky="ew")

        # --- Fecha ---
        ctk.CTkLabel(self, text="Fecha:", anchor="w").grid(
            row=5, column=0, padx=30, pady=7, sticky="w")
        if DateEntry:
            self.entry_date = DateEntry(self, width=12, background='darkblue', foreground='white', borderwidth=2, date_pattern='dd/mm/yyyy')
        else:
            self.entry_date = ctk.CTkEntry(self, placeholder_text="Ej: DD/MM/AAAA")
        self.entry_date.grid(row=5, column=1, padx=30, pady=7, sticky="ew")
        if not self.expense_data:
            self.entry_date.delete(0, 'end')
            self.entry_date.insert(0, datetime.date.today().strftime("%d/%m/%Y"))

        # --- Observaciones ---
        ctk.CTkLabel(self, text="Observaciones:", anchor="nw").grid(
            row=6, column=0, padx=30, pady=7, sticky="nw")
        self.textbox_obs = ctk.CTkTextbox(self, height=80)
        self.textbox_obs.grid(row=6, column=1, padx=30, pady=7, sticky="ew")

        if is_linked:
            ctk.CTkLabel(
                self, text="ℹ️ Generado desde mantenimiento. Algunos campos bloqueados.",
                font=ctk.CTkFont(size=11, slant="italic"), text_color="#F59E0B"
            ).grid(row=7, column=0, columnspan=2, pady=(5, 0))

        # Pre-llenar si editando
        if self.expense_data:
            v_id = self.expense_data[1]
            for disp, vid in self.vehicle_map.items():
                if vid == v_id:
                    self.combo_vehicle.set(disp)
                    break
            self.combo_cat.set(self.expense_data[2])
            self.entry_concept.insert(0, self.expense_data[3])
            self.entry_amount.insert(0, str(self.expense_data[4]))
            
            self.entry_date.delete(0, 'end')
            try:
                d_str = datetime.datetime.strptime(self.expense_data[5], "%Y-%m-%d").strftime("%d/%m/%Y")
            except:
                d_str = self.expense_data[5]
            self.entry_date.insert(0, d_str)
            
            self.textbox_obs.insert("0.0", self.expense_data[6])

            if is_linked:
                self.combo_vehicle.configure(state="disabled")
                self.combo_cat.configure(state="disabled")
                self.entry_concept.configure(state="disabled")
                if DateEntry:
                    self.entry_date.configure(state="disabled")
                else:
                    self.entry_date.configure(state="readonly")

        # Botones
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.grid(row=8, column=0, columnspan=2, pady=(25, 20), sticky="ew")
        btn_frame.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkButton(
            btn_frame, text="💾  Guardar", width=140, height=40,
            fg_color="#10B981", hover_color="#059669",
            font=ctk.CTkFont(weight="bold"),
            command=self._save,
        ).grid(row=0, column=0, padx=20)

        ctk.CTkButton(
            btn_frame, text="Cancelar", width=140, height=40,
            fg_color="#6B7280", hover_color="#4B5563",
            command=self.destroy,
        ).grid(row=0, column=1, padx=20)

    def _save(self):
        vehicle_str = self.combo_vehicle.get()
        vehicle_id = self.vehicle_map.get(vehicle_str)
        cat = self.combo_cat.get()
        concept = self.entry_concept.get().strip()
        amount_str = self.entry_amount.get().strip()
        date_str = self.entry_date.get().strip()
        obs = self.textbox_obs.get("0.0", "end").strip()

        if not vehicle_id:
            messagebox.showwarning("Error", "Debe seleccionar un vehículo válido.", parent=self)
            return
        if not concept or not amount_str or not date_str:
            messagebox.showwarning("Error", "Concepto, monto y fecha son obligatorios.", parent=self)
            return

        try:
            amount = float(amount_str)
            if amount < 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Error", "Monto inválido. Ingrese un número positivo.", parent=self)
            return

        try:
            parsed_date = datetime.datetime.strptime(date_str, "%d/%m/%Y").strftime("%Y-%m-%d")
        except ValueError:
            messagebox.showwarning("Error", "La fecha debe tener formato DD/MM/AAAA", parent=self)
            return

        if self.expense_data:
            ok, msg = database.update_expense(
                self.expense_data[0], self.admin_id, vehicle_id, cat, concept, amount, parsed_date, obs)
        else:
            ok, msg = database.add_expense(
                self.admin_id, vehicle_id, cat, concept, amount, parsed_date, obs)

        if ok:
            if self.callback:
                self.callback()
            self.destroy()
        else:
            messagebox.showerror("Error", msg, parent=self)
