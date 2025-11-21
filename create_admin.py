# create_admin.py
import hashlib
from database import create_connection

def create_admin_user():
    """Crea el usuario administrador por defecto"""
    conn = create_connection()
    cursor = conn.cursor()
    
    try:
        # Verificar si ya existe un administrador
        cursor.execute("SELECT id FROM usuarios WHERE rol = 'admin'")
        if cursor.fetchone():
            print("✅ Ya existe un usuario administrador")
            return
        
        # Crear usuario administrador por defecto
        admin_password = "admin123"  # Cambia esta contraseña
        hashed_password = hashlib.sha256(admin_password.encode()).hexdigest()
        
        cursor.execute("""
            INSERT INTO usuarios (nombre_completo, email, usuario, password, rol)
            VALUES (%s, %s, %s, %s, 'admin')
        """, ('Administrador Principal', 'admin@sistema.com', 'admin', hashed_password))
        
        conn.commit()
        print("✅ Usuario administrador creado exitosamente")
        print(f"👤 Usuario: admin")
        print(f"🔑 Contraseña: {admin_password}")
        print("⚠️  Cambia la contraseña después del primer inicio de sesión")
        
    except Exception as e:
        print(f"❌ Error al crear administrador: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    create_admin_user()