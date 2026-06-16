"""
Pantalla 1 — Login, Registro y Recuperación de Contraseña.
Presenta una tarjeta centrada con tres vistas internas que
se intercambian dinámicamente.
"""

import customtkinter as ctk
from tkinter import messagebox
import auth


class LoginFrame(ctk.CTkFrame):
    """Frame completo que ocupa toda la ventana para la autenticación."""

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Centrar la tarjeta en el frame
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Tarjeta principal
        self.card = ctk.CTkFrame(self, corner_radius=16, width=400)
        self.card.grid(row=0, column=0)

        # Estado para la recuperación
        self._recovery_username = None

        self._show_login_view()

    # -----------------------------------------------------------------
    #  Vistas
    # -----------------------------------------------------------------

    def _clear_card(self):
        for w in self.card.winfo_children():
            w.destroy()

    # ---- VISTA: LOGIN ----
    def _show_login_view(self):
        self._clear_card()

        ctk.CTkLabel(
            self.card, text="🚢",
            font=ctk.CTkFont(size=52),
        ).pack(pady=(35, 4))

        ctk.CTkLabel(
            self.card, text="FLOTILLA CONTROL",
            font=ctk.CTkFont(size=26, weight="bold"),
        ).pack(pady=(0, 2))

        ctk.CTkLabel(
            self.card, text="Sistema de Gestión Vehicular",
            font=ctk.CTkFont(size=13), text_color="gray",
        ).pack(pady=(0, 28))

        self.entry_user = ctk.CTkEntry(
            self.card, placeholder_text="Usuario", width=280, height=42,
        )
        self.entry_user.pack(pady=8, padx=60)

        self.entry_pass = ctk.CTkEntry(
            self.card, placeholder_text="Contraseña", show="•",
            width=280, height=42,
        )
        self.entry_pass.pack(pady=8, padx=60)
        self.entry_pass.bind("<Return>", lambda _: self._do_login())

        self.lbl_error = ctk.CTkLabel(
            self.card, text="", text_color="#EF4444",
            font=ctk.CTkFont(size=12),
        )
        self.lbl_error.pack(pady=(4, 0))

        ctk.CTkButton(
            self.card, text="Iniciar Sesión", width=280, height=42,
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self._do_login,
        ).pack(pady=(16, 8), padx=60)

        ctk.CTkButton(
            self.card, text="Crear una cuenta", width=280,
            fg_color="transparent",
            text_color=("#3B82F6", "#60A5FA"),
            hover_color=("gray90", "gray20"),
            command=self._show_register_view,
        ).pack(pady=2, padx=60)

        ctk.CTkButton(
            self.card, text="¿Olvidaste tu contraseña?", width=280,
            fg_color="transparent",
            text_color=("gray50", "gray60"),
            hover_color=("gray90", "gray20"),
            font=ctk.CTkFont(size=12),
            command=self._show_recover_step1,
        ).pack(pady=(2, 35), padx=60)

    # ---- VISTA: REGISTRO ----
    def _show_register_view(self):
        self._clear_card()

        ctk.CTkLabel(
            self.card, text="📝 Crear Cuenta",
            font=ctk.CTkFont(size=22, weight="bold"),
        ).pack(pady=(30, 20))

        self.reg_user = ctk.CTkEntry(
            self.card, placeholder_text="Nombre de usuario (mín. 3)",
            width=280, height=40,
        )
        self.reg_user.pack(pady=6, padx=60)

        self.reg_pass = ctk.CTkEntry(
            self.card, placeholder_text="Contraseña (mín. 6 caracteres)",
            show="•", width=280, height=40,
        )
        self.reg_pass.pack(pady=6, padx=60)

        self.reg_pass2 = ctk.CTkEntry(
            self.card, placeholder_text="Confirmar contraseña",
            show="•", width=280, height=40,
        )
        self.reg_pass2.pack(pady=6, padx=60)

        ctk.CTkLabel(
            self.card, text="Pregunta de seguridad:", anchor="w",
            font=ctk.CTkFont(size=12),
        ).pack(pady=(12, 2), padx=65, anchor="w")

        self.reg_question = ctk.CTkComboBox(
            self.card, values=auth.SECURITY_QUESTIONS,
            width=280, height=38, state="readonly",
        )
        self.reg_question.pack(pady=4, padx=60)
        self.reg_question.set(auth.SECURITY_QUESTIONS[0])

        self.reg_answer = ctk.CTkEntry(
            self.card, placeholder_text="Tu respuesta secreta",
            width=280, height=40,
        )
        self.reg_answer.pack(pady=6, padx=60)

        self.lbl_reg_error = ctk.CTkLabel(
            self.card, text="", text_color="#EF4444",
            font=ctk.CTkFont(size=12), wraplength=280,
        )
        self.lbl_reg_error.pack(pady=(4, 0))

        ctk.CTkButton(
            self.card, text="Registrarme", width=280, height=42,
            fg_color="#10B981", hover_color="#059669",
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self._do_register,
        ).pack(pady=(14, 8), padx=60)

        ctk.CTkButton(
            self.card, text="← Volver al Login", width=280,
            fg_color="transparent",
            text_color=("#3B82F6", "#60A5FA"),
            hover_color=("gray90", "gray20"),
            command=self._show_login_view,
        ).pack(pady=(2, 30), padx=60)

    # ---- VISTA: RECUPERAR PASO 1 — Pedir usuario ----
    def _show_recover_step1(self):
        self._clear_card()

        ctk.CTkLabel(
            self.card, text="🔑 Recuperar Contraseña",
            font=ctk.CTkFont(size=22, weight="bold"),
        ).pack(pady=(35, 8))

        ctk.CTkLabel(
            self.card, text="Ingresa tu nombre de usuario",
            text_color="gray",
        ).pack(pady=(0, 20))

        self.rec_user = ctk.CTkEntry(
            self.card, placeholder_text="Nombre de usuario",
            width=280, height=42,
        )
        self.rec_user.pack(pady=8, padx=60)

        self.lbl_rec_error = ctk.CTkLabel(
            self.card, text="", text_color="#EF4444",
            font=ctk.CTkFont(size=12),
        )
        self.lbl_rec_error.pack(pady=(4, 0))

        ctk.CTkButton(
            self.card, text="Siguiente →", width=280, height=42,
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self._do_recover_step1,
        ).pack(pady=(16, 8), padx=60)

        ctk.CTkButton(
            self.card, text="← Volver al Login", width=280,
            fg_color="transparent",
            text_color=("#3B82F6", "#60A5FA"),
            hover_color=("gray90", "gray20"),
            command=self._show_login_view,
        ).pack(pady=(2, 35), padx=60)

    # ---- VISTA: RECUPERAR PASO 2 — Responder pregunta ----
    def _show_recover_step2(self, question):
        self._clear_card()

        ctk.CTkLabel(
            self.card, text="🔑 Pregunta de Seguridad",
            font=ctk.CTkFont(size=22, weight="bold"),
        ).pack(pady=(35, 15))

        ctk.CTkLabel(
            self.card, text=question,
            font=ctk.CTkFont(size=14), wraplength=300,
        ).pack(pady=(0, 15), padx=60)

        self.rec_answer = ctk.CTkEntry(
            self.card, placeholder_text="Tu respuesta",
            width=280, height=42,
        )
        self.rec_answer.pack(pady=8, padx=60)

        self.lbl_rec2_error = ctk.CTkLabel(
            self.card, text="", text_color="#EF4444",
            font=ctk.CTkFont(size=12),
        )
        self.lbl_rec2_error.pack(pady=(4, 0))

        ctk.CTkButton(
            self.card, text="Verificar →", width=280, height=42,
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self._do_recover_step2,
        ).pack(pady=(16, 8), padx=60)

        ctk.CTkButton(
            self.card, text="← Volver al Login", width=280,
            fg_color="transparent",
            text_color=("#3B82F6", "#60A5FA"),
            hover_color=("gray90", "gray20"),
            command=self._show_login_view,
        ).pack(pady=(2, 35), padx=60)

    # ---- VISTA: RECUPERAR PASO 3 — Nueva contraseña ----
    def _show_recover_step3(self):
        self._clear_card()

        ctk.CTkLabel(
            self.card, text="🔐 Nueva Contraseña",
            font=ctk.CTkFont(size=22, weight="bold"),
        ).pack(pady=(35, 20))

        self.rec_new_pass = ctk.CTkEntry(
            self.card, placeholder_text="Nueva contraseña (mín. 6)",
            show="•", width=280, height=42,
        )
        self.rec_new_pass.pack(pady=8, padx=60)

        self.rec_new_pass2 = ctk.CTkEntry(
            self.card, placeholder_text="Confirmar nueva contraseña",
            show="•", width=280, height=42,
        )
        self.rec_new_pass2.pack(pady=8, padx=60)

        self.lbl_rec3_error = ctk.CTkLabel(
            self.card, text="", text_color="#EF4444",
            font=ctk.CTkFont(size=12),
        )
        self.lbl_rec3_error.pack(pady=(4, 0))

        ctk.CTkButton(
            self.card, text="Cambiar Contraseña", width=280, height=42,
            fg_color="#10B981", hover_color="#059669",
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self._do_recover_step3,
        ).pack(pady=(16, 35), padx=60)

    # -----------------------------------------------------------------
    #  Acciones
    # -----------------------------------------------------------------

    def _do_login(self):
        user = self.entry_user.get()
        pwd = self.entry_pass.get()
        ok, admin_id, msg = auth.login_user(user, pwd)
        if ok:
            self.controller.on_login_success(admin_id, user.strip().lower())
        else:
            self.lbl_error.configure(text=msg)

    def _do_register(self):
        user = self.reg_user.get()
        pwd = self.reg_pass.get()
        pwd2 = self.reg_pass2.get()
        question = self.reg_question.get()
        answer = self.reg_answer.get()

        if pwd != pwd2:
            self.lbl_reg_error.configure(text="Las contraseñas no coinciden.")
            return

        ok, msg = auth.register_user(user, pwd, question, answer)
        if ok:
            messagebox.showinfo("Cuenta Creada", msg)
            self._show_login_view()
        else:
            self.lbl_reg_error.configure(text=msg)

    def _do_recover_step1(self):
        user = self.rec_user.get()
        ok, question, msg = auth.get_security_question(user)
        if ok:
            self._recovery_username = user
            self._show_recover_step2(question)
        else:
            self.lbl_rec_error.configure(text=msg)

    def _do_recover_step2(self):
        answer = self.rec_answer.get()
        ok, msg = auth.verify_security_answer(self._recovery_username, answer)
        if ok:
            self._show_recover_step3()
        else:
            self.lbl_rec2_error.configure(text=msg)

    def _do_recover_step3(self):
        p1 = self.rec_new_pass.get()
        p2 = self.rec_new_pass2.get()
        if p1 != p2:
            self.lbl_rec3_error.configure(text="Las contraseñas no coinciden.")
            return
        ok, msg = auth.reset_password(self._recovery_username, p1)
        if ok:
            messagebox.showinfo("Contraseña Actualizada", msg)
            self._recovery_username = None
            self._show_login_view()
        else:
            self.lbl_rec3_error.configure(text=msg)

    # -----------------------------------------------------------------
    #  Utilidad
    # -----------------------------------------------------------------

    def clear_fields(self):
        """Restaura la vista de login limpia."""
        self._recovery_username = None
        self._show_login_view()
