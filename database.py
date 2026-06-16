"""
Flotilla Control — Capa de persistencia SQLite.
Todas las operaciones de datos filtran por admin_id para aislar
la información de cada administrador.
"""

import sqlite3
import datetime

DB_NAME = "flotilla.db"


def get_connection():
    """Devuelve una conexión con claves foráneas habilitadas."""
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db():
    """Crea las tablas si no existen."""
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS admins (
        id                  INTEGER PRIMARY KEY AUTOINCREMENT,
        username            TEXT    UNIQUE NOT NULL,
        password_hash       TEXT    NOT NULL,
        security_question   TEXT    NOT NULL,
        security_answer_hash TEXT   NOT NULL,
        created_at          TEXT    NOT NULL
    )""")

    c.execute("""
    CREATE TABLE IF NOT EXISTS vehicles (
        id        INTEGER PRIMARY KEY AUTOINCREMENT,
        admin_id  INTEGER NOT NULL,
        brand     TEXT    NOT NULL,
        model     TEXT    NOT NULL,
        year      INTEGER NOT NULL,
        plates    TEXT    UNIQUE NOT NULL,
        vin       TEXT    UNIQUE NOT NULL,
        mileage   INTEGER NOT NULL DEFAULT 0,
        status    TEXT    NOT NULL DEFAULT 'Activo'
                  CHECK(status IN ('Activo', 'Inactivo')),
        FOREIGN KEY (admin_id) REFERENCES admins(id) ON DELETE CASCADE
    )""")

    c.execute("""
    CREATE TABLE IF NOT EXISTS drivers (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        admin_id   INTEGER NOT NULL,
        name       TEXT    NOT NULL,
        phone      TEXT    NOT NULL,
        address    TEXT    DEFAULT '',
        curp       TEXT    UNIQUE NOT NULL,
        status     TEXT    NOT NULL DEFAULT 'Activo'
                   CHECK(status IN ('Activo', 'Suspendido', 'Baja')),
        vehicle_id INTEGER,
        FOREIGN KEY (admin_id)   REFERENCES admins(id)   ON DELETE CASCADE,
        FOREIGN KEY (vehicle_id) REFERENCES vehicles(id) ON DELETE SET NULL
    )""")

    c.execute("""
    CREATE TABLE IF NOT EXISTS maintenance (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        admin_id     INTEGER NOT NULL,
        vehicle_id   INTEGER NOT NULL,
        date         TEXT    NOT NULL,
        service_type TEXT    NOT NULL CHECK(service_type IN (
            'Cambio de aceite', 'Cambio de llantas', 'Afinación',
            'Reparación', 'Mantenimiento completo'
        )),
        description  TEXT    DEFAULT '',
        FOREIGN KEY (admin_id)   REFERENCES admins(id)   ON DELETE CASCADE,
        FOREIGN KEY (vehicle_id) REFERENCES vehicles(id) ON DELETE CASCADE
    )""")

    c.execute("""
    CREATE TABLE IF NOT EXISTS expenses (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        admin_id     INTEGER NOT NULL,
        vehicle_id   INTEGER NOT NULL,
        category     TEXT    NOT NULL CHECK(category IN (
            'Seguro', 'Mantenimiento', 'Llantas', 'Verificación',
            'Tenencia', 'Reparación', 'Otros'
        )),
        concept      TEXT    NOT NULL,
        amount       REAL    NOT NULL,
        date         TEXT    NOT NULL,
        observations TEXT    DEFAULT '',
        FOREIGN KEY (admin_id)   REFERENCES admins(id)   ON DELETE CASCADE,
        FOREIGN KEY (vehicle_id) REFERENCES vehicles(id) ON DELETE CASCADE
    )""")

    conn.commit()
    conn.close()


# =========================================================================
#  VEHÍCULOS — CRUD
# =========================================================================

def add_vehicle(admin_id, brand, model, year, plates, vin, mileage, status):
    try:
        conn = get_connection()
        c = conn.cursor()
        c.execute("""
            INSERT INTO vehicles (admin_id, brand, model, year, plates, vin, mileage, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (admin_id, brand.strip(), model.strip(), int(year),
              plates.upper().strip(), vin.upper().strip(), int(mileage), status))
        conn.commit()
        return True, "Vehículo registrado con éxito."
    except sqlite3.IntegrityError as e:
        if "plates" in str(e).lower():
            return False, "Las placas ya están registradas."
        if "vin" in str(e).lower():
            return False, "El VIN ya está registrado."
        return False, f"Error de integridad: {e}"
    except Exception as e:
        return False, f"Error: {e}"
    finally:
        conn.close()


def get_vehicles(admin_id, search_query=""):
    """Devuelve (id, brand, model, year, plates, vin, mileage, status)."""
    conn = get_connection()
    c = conn.cursor()
    if search_query:
        q = f"%{search_query}%"
        c.execute("""
            SELECT id, brand, model, year, plates, vin, mileage, status
            FROM vehicles WHERE admin_id = ? AND (
                brand LIKE ? OR model LIKE ? OR plates LIKE ? OR
                vin LIKE ? OR status LIKE ? OR CAST(year AS TEXT) LIKE ?
            ) ORDER BY brand, model
        """, (admin_id, q, q, q, q, q, q))
    else:
        c.execute("""
            SELECT id, brand, model, year, plates, vin, mileage, status
            FROM vehicles WHERE admin_id = ? ORDER BY brand, model
        """, (admin_id,))
    rows = c.fetchall()
    conn.close()
    return rows


def get_vehicle_by_id(vehicle_id, admin_id):
    """Devuelve (id, brand, model, year, plates, vin, mileage, status) o None."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT id, brand, model, year, plates, vin, mileage, status
        FROM vehicles WHERE id = ? AND admin_id = ?
    """, (vehicle_id, admin_id))
    row = c.fetchone()
    conn.close()
    return row


def get_vehicles_for_combo(admin_id):
    """Retorna [(id, 'PLACAS - Marca Modelo'), …] para llenar comboboxes."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT id, plates, brand, model FROM vehicles
        WHERE admin_id = ? AND status = 'Activo' ORDER BY plates
    """, (admin_id,))
    rows = c.fetchall()
    conn.close()
    return [(r[0], f"{r[1]} - {r[2]} {r[3]}") for r in rows]


def get_all_vehicles_for_combo(admin_id):
    """Igual que get_vehicles_for_combo pero incluye también los inactivos."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT id, plates, brand, model FROM vehicles
        WHERE admin_id = ? ORDER BY plates
    """, (admin_id,))
    rows = c.fetchall()
    conn.close()
    return [(r[0], f"{r[1]} - {r[2]} {r[3]}") for r in rows]


def update_vehicle(vehicle_id, admin_id, brand, model, year, plates, vin, mileage, status):
    try:
        conn = get_connection()
        c = conn.cursor()
        c.execute("""
            UPDATE vehicles
            SET brand=?, model=?, year=?, plates=?, vin=?, mileage=?, status=?
            WHERE id=? AND admin_id=?
        """, (brand.strip(), model.strip(), int(year), plates.upper().strip(),
              vin.upper().strip(), int(mileage), status, vehicle_id, admin_id))
        conn.commit()
        return True, "Vehículo actualizado con éxito."
    except sqlite3.IntegrityError as e:
        if "plates" in str(e).lower():
            return False, "Las placas ya están en uso por otro vehículo."
        if "vin" in str(e).lower():
            return False, "El VIN ya está en uso por otro vehículo."
        return False, f"Error: {e}"
    except Exception as e:
        return False, f"Error: {e}"
    finally:
        conn.close()


def delete_vehicle(vehicle_id, admin_id):
    try:
        conn = get_connection()
        c = conn.cursor()
        c.execute("DELETE FROM vehicles WHERE id=? AND admin_id=?",
                  (vehicle_id, admin_id))
        conn.commit()
        return True, "Vehículo eliminado con éxito."
    except Exception as e:
        return False, f"Error: {e}"
    finally:
        conn.close()


# =========================================================================
#  CONDUCTORES — CRUD
# =========================================================================

def add_driver(admin_id, name, phone, address, curp, status, vehicle_id):
    try:
        conn = get_connection()
        c = conn.cursor()
        v_id = vehicle_id if vehicle_id else None
        c.execute("""
            INSERT INTO drivers (admin_id, name, phone, address, curp, status, vehicle_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (admin_id, name.strip(), phone.strip(), address.strip(),
              curp.upper().strip(), status, v_id))
        conn.commit()
        return True, "Conductor registrado con éxito."
    except sqlite3.IntegrityError:
        return False, "El CURP ya está registrado."
    except Exception as e:
        return False, f"Error: {e}"
    finally:
        conn.close()


def get_drivers(admin_id, search_query=""):
    """Devuelve (id, name, phone, address, curp, status, vehicle_id, vehicle_info)."""
    conn = get_connection()
    c = conn.cursor()
    base = """
        SELECT d.id, d.name, d.phone, d.address, d.curp, d.status, d.vehicle_id,
               COALESCE(v.plates || ' - ' || v.brand || ' ' || v.model, 'Sin asignar')
        FROM drivers d
        LEFT JOIN vehicles v ON d.vehicle_id = v.id
        WHERE d.admin_id = ?
    """
    params = [admin_id]
    if search_query:
        q = f"%{search_query}%"
        base += " AND (d.name LIKE ? OR d.phone LIKE ? OR d.curp LIKE ? OR d.status LIKE ? OR d.address LIKE ?)"
        params.extend([q, q, q, q, q])
    base += " ORDER BY d.name"
    c.execute(base, params)
    rows = c.fetchall()
    conn.close()
    return rows


def get_driver_by_id(driver_id, admin_id):
    """Devuelve (id, name, phone, address, curp, status, vehicle_id) o None."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT id, name, phone, address, curp, status, vehicle_id
        FROM drivers WHERE id = ? AND admin_id = ?
    """, (driver_id, admin_id))
    row = c.fetchone()
    conn.close()
    return row


def update_driver(driver_id, admin_id, name, phone, address, curp, status, vehicle_id):
    try:
        conn = get_connection()
        c = conn.cursor()
        v_id = vehicle_id if vehicle_id else None
        c.execute("""
            UPDATE drivers
            SET name=?, phone=?, address=?, curp=?, status=?, vehicle_id=?
            WHERE id=? AND admin_id=?
        """, (name.strip(), phone.strip(), address.strip(),
              curp.upper().strip(), status, v_id, driver_id, admin_id))
        conn.commit()
        return True, "Conductor actualizado con éxito."
    except sqlite3.IntegrityError:
        return False, "El CURP ya está registrado por otro conductor."
    except Exception as e:
        return False, f"Error: {e}"
    finally:
        conn.close()


def delete_driver(driver_id, admin_id):
    try:
        conn = get_connection()
        c = conn.cursor()
        c.execute("DELETE FROM drivers WHERE id=? AND admin_id=?",
                  (driver_id, admin_id))
        conn.commit()
        return True, "Conductor eliminado con éxito."
    except Exception as e:
        return False, f"Error: {e}"
    finally:
        conn.close()


# =========================================================================
#  MANTENIMIENTOS — CRUD
# =========================================================================

def add_maintenance(admin_id, vehicle_id, date, service_type, description=""):
    try:
        conn = get_connection()
        c = conn.cursor()
        c.execute("""
            INSERT INTO maintenance (admin_id, vehicle_id, date, service_type, description)
            VALUES (?, ?, ?, ?, ?)
        """, (admin_id, vehicle_id, date.strip(), service_type, description.strip()))
        conn.commit()
        return True, "Mantenimiento registrado con éxito."
    except Exception as e:
        return False, f"Error: {e}"
    finally:
        conn.close()


def get_maintenance(admin_id, search_query="", vehicle_id=None):
    """Devuelve (id, plates, vehicle_name, date, service_type, description, vehicle_id)."""
    conn = get_connection()
    c = conn.cursor()
    base = """
        SELECT m.id, v.plates, v.brand || ' ' || v.model, m.date,
               m.service_type, m.description, m.vehicle_id
        FROM maintenance m
        JOIN vehicles v ON m.vehicle_id = v.id
        WHERE m.admin_id = ?
    """
    params = [admin_id]
    if vehicle_id:
        base += " AND m.vehicle_id = ?"
        params.append(vehicle_id)
    if search_query:
        q = f"%{search_query}%"
        base += " AND (v.plates LIKE ? OR m.service_type LIKE ? OR m.description LIKE ? OR m.date LIKE ?)"
        params.extend([q, q, q, q])
    base += " ORDER BY m.date DESC"
    c.execute(base, params)
    rows = c.fetchall()
    conn.close()
    return rows


def get_maintenance_by_id(maint_id, admin_id):
    """Devuelve (id, vehicle_id, date, service_type, description) o None."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT id, vehicle_id, date, service_type, description
        FROM maintenance WHERE id=? AND admin_id=?
    """, (maint_id, admin_id))
    row = c.fetchone()
    conn.close()
    return row


def update_maintenance(maint_id, admin_id, vehicle_id, date, service_type, description=""):
    try:
        conn = get_connection()
        c = conn.cursor()
        c.execute("""
            UPDATE maintenance SET vehicle_id=?, date=?, service_type=?, description=?
            WHERE id=? AND admin_id=?
        """, (vehicle_id, date.strip(), service_type, description.strip(),
              maint_id, admin_id))
        conn.commit()
        return True, "Mantenimiento actualizado con éxito."
    except Exception as e:
        return False, f"Error: {e}"
    finally:
        conn.close()


def delete_maintenance(maint_id, admin_id):
    try:
        conn = get_connection()
        c = conn.cursor()
        c.execute("DELETE FROM maintenance WHERE id=? AND admin_id=?",
                  (maint_id, admin_id))
        conn.commit()
        return True, "Registro eliminado con éxito."
    except Exception as e:
        return False, f"Error: {e}"
    finally:
        conn.close()


# =========================================================================
#  GASTOS — CRUD
# =========================================================================

def add_expense(admin_id, vehicle_id, category, concept, amount, date, observations=""):
    try:
        conn = get_connection()
        c = conn.cursor()
        c.execute("""
            INSERT INTO expenses
                (admin_id, vehicle_id, category, concept, amount, date, observations)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (admin_id, vehicle_id, category, concept.strip(),
              float(amount), date.strip(), observations.strip()))
        conn.commit()
        return True, "Gasto registrado con éxito."
    except Exception as e:
        return False, f"Error: {e}"
    finally:
        conn.close()


def get_expenses(admin_id, search_query="", vehicle_id=None):
    """Devuelve (id, plates, vehicle_name, category, concept, amount, date, observations, vehicle_id)."""
    conn = get_connection()
    c = conn.cursor()
    base = """
        SELECT e.id, v.plates, v.brand || ' ' || v.model, e.category,
               e.concept, e.amount, e.date, e.observations, e.vehicle_id
        FROM expenses e
        JOIN vehicles v ON e.vehicle_id = v.id
        WHERE e.admin_id = ?
    """
    params = [admin_id]
    if vehicle_id:
        base += " AND e.vehicle_id = ?"
        params.append(vehicle_id)
    if search_query:
        q = f"%{search_query}%"
        base += " AND (v.plates LIKE ? OR e.category LIKE ? OR e.concept LIKE ? OR e.observations LIKE ?)"
        params.extend([q, q, q, q])
    base += " ORDER BY e.date DESC"
    c.execute(base, params)
    rows = c.fetchall()
    conn.close()
    return rows


def get_expense_by_id(expense_id, admin_id):
    """Devuelve (id, vehicle_id, category, concept, amount, date, observations) o None."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT id, vehicle_id, category, concept, amount, date, observations
        FROM expenses WHERE id=? AND admin_id=?
    """, (expense_id, admin_id))
    row = c.fetchone()
    conn.close()
    return row


def update_expense(expense_id, admin_id, vehicle_id, category, concept, amount, date, observations=""):
    try:
        conn = get_connection()
        c = conn.cursor()
        c.execute("""
            UPDATE expenses
            SET vehicle_id=?, category=?, concept=?, amount=?, date=?, observations=?
            WHERE id=? AND admin_id=?
        """, (vehicle_id, category, concept.strip(), float(amount),
              date.strip(), observations.strip(), expense_id, admin_id))
        conn.commit()
        return True, "Gasto actualizado con éxito."
    except Exception as e:
        return False, f"Error: {e}"
    finally:
        conn.close()


def delete_expense(expense_id, admin_id):
    try:
        conn = get_connection()
        c = conn.cursor()
        c.execute("DELETE FROM expenses WHERE id=? AND admin_id=?",
                  (expense_id, admin_id))
        conn.commit()
        return True, "Gasto eliminado con éxito."
    except Exception as e:
        return False, f"Error: {e}"
    finally:
        conn.close()


# =========================================================================
#  DASHBOARD — Estadísticas
# =========================================================================

def get_dashboard_stats(admin_id):
    conn = get_connection()
    c = conn.cursor()

    c.execute("SELECT COUNT(*) FROM vehicles WHERE admin_id = ?", (admin_id,))
    total_vehicles = c.fetchone()[0]

    now = datetime.date.today()
    month_start = now.replace(day=1).isoformat()

    c.execute("""
        SELECT COUNT(*) FROM maintenance
        WHERE admin_id = ? AND date >= ?
    """, (admin_id, month_start))
    month_maintenance = c.fetchone()[0]

    c.execute("""
        SELECT COALESCE(SUM(amount), 0) FROM expenses
        WHERE admin_id = ? AND date >= ?
    """, (admin_id, month_start))
    month_expenses = c.fetchone()[0]

    conn.close()
    return {
        "total_vehicles": total_vehicles,
        "month_maintenance": month_maintenance,
        "month_expenses": month_expenses,
    }


# =========================================================================
#  REPORTES
# =========================================================================

def get_vehicle_report(admin_id):
    """Reporte por vehículo: gasto total, último mantenimiento, total de mants, estado."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT v.id, v.plates, v.brand, v.model, v.status,
            COALESCE((SELECT SUM(e.amount) FROM expenses e
                      WHERE e.vehicle_id = v.id), 0)          AS total_spent,
            (SELECT MAX(m.date) FROM maintenance m
             WHERE m.vehicle_id = v.id)                        AS last_maint,
            (SELECT COUNT(*)    FROM maintenance m
             WHERE m.vehicle_id = v.id)                        AS total_maint
        FROM vehicles v
        WHERE v.admin_id = ?
        ORDER BY v.plates
    """, (admin_id,))
    rows = c.fetchall()
    conn.close()
    return rows


def get_general_report(admin_id):
    conn = get_connection()
    c = conn.cursor()

    c.execute("SELECT COALESCE(SUM(amount), 0) FROM expenses WHERE admin_id = ?",
              (admin_id,))
    total_expense = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM vehicles WHERE admin_id = ? AND status = 'Activo'",
              (admin_id,))
    active_vehicles = c.fetchone()[0]

    conn.close()
    return {
        "total_expense": total_expense,
        "active_vehicles": active_vehicles,
    }
