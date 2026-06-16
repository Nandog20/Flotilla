"""
Flotilla Control — Módulo de autenticación.
Usa SHA-256 (hashlib) para almacenar contraseñas de forma segura.
Incluye registro, login y recuperación por pregunta de seguridad.
"""

import hashlib
import datetime
import database


def _hash(text: str) -> str:
    """Genera un hash SHA-256 del texto dado."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


# Preguntas de seguridad predefinidas
SECURITY_QUESTIONS = [
    "¿Cuál es el nombre de tu primera mascota?",
    "¿En qué ciudad naciste?",
    "¿Cuál es el apellido de soltera de tu madre?",
    "¿Cuál fue tu primer auto?",
    "¿Cómo se llama tu mejor amigo de la infancia?",
]


def register_user(username, password, security_question, security_answer):
    """Registra un nuevo administrador. Devuelve (success, message)."""
    if not username or not password or not security_question or not security_answer:
        return False, "Todos los campos son obligatorios."
    if len(username.strip()) < 3:
        return False, "El usuario debe tener al menos 3 caracteres."
    if len(password) < 6:
        return False, "La contraseña debe tener al menos 6 caracteres."

    try:
        conn = database.get_connection()
        c = conn.cursor()
        c.execute("""
            INSERT INTO admins
                (username, password_hash, security_question,
                 security_answer_hash, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (
            username.strip().lower(),
            _hash(password),
            security_question,
            _hash(security_answer.strip().lower()),
            datetime.datetime.now().isoformat(),
        ))
        conn.commit()
        return True, "Cuenta creada con éxito. Ya puedes iniciar sesión."
    except Exception as e:
        if "UNIQUE" in str(e).upper():
            return False, "El nombre de usuario ya está en uso."
        return False, f"Error: {e}"
    finally:
        conn.close()


def login_user(username, password):
    """Intenta iniciar sesión. Devuelve (success, admin_id | None, message)."""
    if not username or not password:
        return False, None, "Ingresa usuario y contraseña."

    conn = database.get_connection()
    c = conn.cursor()
    c.execute("SELECT id, password_hash FROM admins WHERE username = ?",
              (username.strip().lower(),))
    row = c.fetchone()
    conn.close()

    if not row:
        return False, None, "Usuario no encontrado."
    if row[1] != _hash(password):
        return False, None, "Contraseña incorrecta."
    return True, row[0], "Inicio de sesión exitoso."


def get_security_question(username):
    """Recupera la pregunta de seguridad. Devuelve (success, question | None, message)."""
    conn = database.get_connection()
    c = conn.cursor()
    c.execute("SELECT security_question FROM admins WHERE username = ?",
              (username.strip().lower(),))
    row = c.fetchone()
    conn.close()

    if not row:
        return False, None, "Usuario no encontrado."
    return True, row[0], ""


def verify_security_answer(username, answer):
    """Verifica la respuesta secreta. Devuelve (success, message)."""
    conn = database.get_connection()
    c = conn.cursor()
    c.execute("SELECT security_answer_hash FROM admins WHERE username = ?",
              (username.strip().lower(),))
    row = c.fetchone()
    conn.close()

    if not row:
        return False, "Usuario no encontrado."
    if row[0] != _hash(answer.strip().lower()):
        return False, "Respuesta incorrecta."
    return True, "Respuesta correcta."


def reset_password(username, new_password):
    """Establece una nueva contraseña. Devuelve (success, message)."""
    if len(new_password) < 6:
        return False, "La contraseña debe tener al menos 6 caracteres."

    try:
        conn = database.get_connection()
        c = conn.cursor()
        c.execute("UPDATE admins SET password_hash = ? WHERE username = ?",
                  (_hash(new_password), username.strip().lower()))
        conn.commit()
        return True, "Contraseña actualizada con éxito."
    except Exception as e:
        return False, f"Error: {e}"
    finally:
        conn.close()
