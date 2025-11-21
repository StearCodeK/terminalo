# controllers/login_controller.py - MODIFICADO
import hashlib
import secrets
from tkinter import messagebox
from models.user_model import UserModel
from helpers import send_email


class LoginController:
    def __init__(self, app):
        self.app = app
        self.model = UserModel()
        
        

    

    def _is_first_user(self):
        """Verifica si será el primer usuario del sistema"""
        try:
            self.model.cursor.execute("SELECT COUNT(*) FROM usuarios")
            user_count = self.model.cursor.fetchone()[0]
            return user_count == 0
        except Exception as e:
            print(f"Error verificando conteo de usuarios: {e}")
            return False

    def login(self):
        """Autentica al usuario"""
        data = self.app.login_view.get_login_data()
        username = data['username']
        password = data['password']

        if not username or not password:
            messagebox.showwarning(
                "Error", "Usuario y contraseña son requeridos")
            return

        try:
            # Buscar usuario en la base de datos
            user = self.model.find_user_by_username(username)

            if not user:
                messagebox.showwarning("Error", "Usuario no encontrado")
                return

            # Verificar contraseña
            hashed_password = hashlib.sha256(password.encode()).hexdigest()

            if hashed_password != user[2]:
                messagebox.showwarning("Error", "Contraseña incorrecta")
                return

            # Guardar información del usuario INCLUYENDO EL ROL
            class User:
                def __init__(self, id, nombre_completo, rol, email, usuario):
                    self.id = id
                    self.nombre_completo = nombre_completo
                    self.rol = rol
                    self.email = email
                    self.usuario = usuario
                    self.is_admin = (rol == 'admin')

            self.app.current_user = User(
                user[0], user[1], user[3], user[4], user[5])
            
            # Guardar el rol en la app para acceso fácil
            self.app.current_user_role = user[3]

            # Cerrar ventana de login y mostrar la aplicación principal
            self.app.login_view.clear_frames()
            self.app.show_main_content()

        except Exception as e:
            messagebox.showerror("Error", f"Error al iniciar sesión: {str(e)}")

    def show_register(self):
        """Muestra el formulario de registro - SIEMPRE PERMITIDO"""
        self.app.login_view.show_register()

    def show_login(self):
        """Muestra el formulario de login"""
        self.app.login_view.show_login()

    def show_password_recovery(self):
        """Muestra el formulario de recuperación de contraseña"""
        self.app.login_view.show_password_recovery()

    def send_authorization_code(self):
        """Envía el código de autorización por correo electrónico"""
        # SIEMPRE PERMITIDO - No verificar existencia de admin
        data = self.app.login_view.get_register_data()
        email = data['email']

        if not email:
            messagebox.showwarning(
                "Error", "Por favor ingrese su correo electrónico")
            return

        # Genera un código aleatorio de 6 dígitos
        self.auth_code = ''.join([str(secrets.randbelow(10)) for _ in range(6)])

        subject = "Código de Autorización - Registro"
        body = (
            f"Estimado/a usuario\n\n"
            f"Gracias por registrarte en nuestra aplicación de inventario.\n\n"
            f"Para completar tu registro, utiliza el siguiente código de autorización:\n\n"
            f"🔐 Código: {self.auth_code}\n\n"
            f"Este código es válido por un tiempo limitado. Si no solicitaste este registro, puedes ignorar este mensaje.\n\n"
            f"¡Bienvenido/a y gracias por confiar en nosotros!\n\n"
            f"Atentamente,\n"
            f"El equipo de soporte"
        )

        if send_email(email, subject, body):
            messagebox.showinfo(
                "Código de Autorización",
                "El código ha sido enviado a tu correo electrónico."
            )
        else:
            messagebox.showerror(
                "Error", "No se pudo enviar el correo. Verifica tu dirección o conexión."
            )

    def register_user(self):
        """Registra un nuevo usuario con validación de código"""
        data = self.app.login_view.get_register_data()

        fullname = data['fullname']
        email = data['email']
        username = data['username']
        password = data['password']
        confirm_password = data['confirm_password']
        entered_code = data['auth_code']

        # Validaciones básicas
        if not all([fullname, email, username, password, confirm_password, entered_code]):
            messagebox.showwarning(
                "Error", "Todos los campos son obligatorios")
            return

        if password != confirm_password:
            messagebox.showwarning("Error", "Las contraseñas no coinciden")
            return

        if entered_code != self.auth_code:
            messagebox.showwarning(
                "Error", "Código de autorización incorrecto")
            return

        # VERIFICAR SI ES EL PRIMER USUARIO (sin contar el admin automático)
        try:
            self.model.cursor.execute("SELECT COUNT(*) FROM usuarios WHERE usuario != 'admin'")
            user_count = self.model.cursor.fetchone()[0]
            
            # Si es el primer usuario (además del admin automático), hacerlo admin
            # Si user_count == 0, significa que solo existe el admin automático
            role = 'admin' if user_count == 0 else 'usuario'
        except Exception as e:
            print(f"Error determinando rol: {e}")
            role = 'usuario'

        # Registrar usuario
        success, message = self.model.create_user(
            fullname, email, username, password, role)

        if success:
            if role == 'admin':
                messagebox.showinfo(
                    "¡Primer Administrador!",
                    "✅ Registro exitoso.\n\n"
                    "🎉 ¡Felicidades! Eres el primer usuario registrado y has sido asignado como Administrador.\n\n"
                    "🔧 Ahora puedes gestionar todos los usuarios y configuraciones del sistema."
                )
            else:
                messagebox.showinfo("Éxito", "✅ Usuario registrado exitosamente")
            
            self.show_login()
        else:
            messagebox.showwarning("Error", message)

    def send_recovery_code(self):
        """Envía un código para recuperar la contraseña por correo electrónico"""
        email = self.app.login_view.get_recovery_email()

        if not email:
            messagebox.showwarning(
                "Error", "Por favor ingrese su correo electrónico")
            return

        try:
            user = self.model.find_user_by_email(email)
            if not user:
                messagebox.showwarning("Error", "Correo no registrado")
                return

            code = ''.join([str(secrets.randbelow(10)) for _ in range(6)])
            self.recovery_code = code
            self.recovery_email = email

            subject = "Código de Recuperación de Contraseña"
            body = (
                f"Estimado/a usuario\n\n"
                f"Hemos recibido una solicitud para restablecer la contraseña de tu cuenta.\n\n"
                f"Por favor, utiliza el siguiente código para continuar con el proceso:\n\n"
                f"🔐 Código de recuperación: {code}\n\n"
                f"⚠️ Por tu seguridad, no compartas este código ni tu nueva contraseña con nadie.\n"
                f"Si no realizaste esta solicitud, puedes ignorar este mensaje.\n\n"
                f"Atentamente,\n"
                f"El equipo de soporte"
            )

            if send_email(email, subject, body):
                messagebox.showinfo(
                    "Éxito", "El código de recuperación ha sido enviado a tu correo electrónico."
                )
                self.app.login_view.show_reset_password()
            else:
                messagebox.showerror(
                    "Error", "No se pudo enviar el correo. Verifica tu dirección o conexión."
                )

        except Exception as e:
            messagebox.showerror(
                "Error", f"No se pudo enviar el código: {str(e)}")

    def reset_password(self):
        """Restablece la contraseña del usuario"""
        data = self.app.login_view.get_reset_data()
        code = data['code']
        new_pass = data['new_pass']
        confirm_pass = data['confirm_pass']

        if not all([code, new_pass, confirm_pass]):
            messagebox.showwarning(
                "Error", "Todos los campos son obligatorios")
            return

        if new_pass != confirm_pass:
            messagebox.showwarning("Error", "Las contraseñas no coinciden")
            return

        if not hasattr(self, 'recovery_code') or code != self.recovery_code:
            messagebox.showwarning(
                "Error", "Código de verificación incorrecto")
            return

        # Actualizar contraseña
        success, message = self.model.update_password(
            self.recovery_email, new_pass)

        if success:
            messagebox.showinfo("Éxito", message)
            self.show_login()
        else:
            messagebox.showerror("Error", message)

    def logout(self):
        """Cierra la sesión del usuario"""
        if messagebox.askyesno("Cerrar sesión", "¿Está seguro que desea cerrar la sesión?"):
            if hasattr(self.app, 'current_user'):
                del self.app.current_user
            if hasattr(self.app, 'current_user_role'):
                del self.app.current_user_role
            self.model.close_connection()
            self.show_login()