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
        self.entry_curp = ctk.CTkEntry(self, placeholder_text="18 caracteres")
        self.entry_curp.grid(row=4, column=1, padx=30, pady=7, sticky="ew")

        ctk.CTkLabel(self, text="Estado:", anchor="w").grid(
            row=5, column=0, padx=30, pady=7, sticky="w")
        self.combo_status = ctk.CTkComboBox(
            self, values=["Activo", "Suspendido", "Baja"], state="readonly")
        self.combo_status.grid(row=5, column=1, padx=30, pady=7, sticky="ew")
        self.combo_status.set("Activo")

        # --- Vehículo asignado ---
        ctk.CTkLabel(self, text="Vehículo:", anchor="w").grid(
            row=6, column=0, padx=30, pady=7, sticky="w")

        vehicles = database.get_vehicles_for_combo(self.admin_id)
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
