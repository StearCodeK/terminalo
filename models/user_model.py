# models/user_model.py - MODIFICADO
import hashlib
from database import create_connection


class UserModel:
    def __init__(self):
        self.conn = create_connection()
        self.cursor = self.conn.cursor()

    def find_user_by_username(self, username):
        """Busca un usuario por nombre de usuario"""
        try:
            self.cursor.execute("""
                SELECT id, nombre_completo, password, rol, email, usuario, activo
                FROM usuarios 
                WHERE usuario = ?
            """, (username,))
            return self.cursor.fetchone()
        except Exception as e:
            raise Exception(f"Error al buscar usuario: {str(e)}")

    def find_user_by_email(self, email):
        """Busca un usuario por email"""
        try:
            self.cursor.execute("""
                SELECT id, nombre_completo, usuario, activo FROM usuarios WHERE email = ?
            """, (email,))
            return self.cursor.fetchone()
        except Exception as e:
            raise Exception(f"Error al buscar email: {str(e)}")

    def create_user(self, fullname, email, username, password, role='usuario'):
        """Crea un nuevo usuario"""
        try:
            # Verificar si el usuario ya existe
            self.cursor.execute(
                "SELECT id FROM usuarios WHERE usuario = ? OR email = ?",
                (username, email)
            )
            if self.cursor.fetchone():
                return False, "El usuario o correo ya está registrado"

            # Hash de la contraseña
            hashed_password = hashlib.sha256(password.encode()).hexdigest()

            # Insertar nuevo usuario
            self.cursor.execute("""
                INSERT INTO usuarios (nombre_completo, email, usuario, password, rol)
                VALUES (?, ?, ?, ?, ?)
            """, (fullname, email, username, hashed_password, role))

            self.conn.commit()
            return True, "Registro completado exitosamente"

        except Exception as e:
            self.conn.rollback()
            return False, f"No se pudo completar el registro: {str(e)}"

    def update_password(self, email, new_password):
        """Actualiza la contraseña de un usuario"""
        try:
            hashed_password = hashlib.sha256(new_password.encode()).hexdigest()

            self.cursor.execute("""
                UPDATE usuarios 
                SET password = ? 
                WHERE email = ?
            """, (hashed_password, email))

            self.conn.commit()
            return True, "Contraseña actualizada exitosamente"

        except Exception as e:
            self.conn.rollback()
            return False, f"No se pudo actualizar la contraseña: {str(e)}"

    def close_connection(self):
        """Cierra la conexión a la base de datos"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()