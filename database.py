import sqlite3
import os
from tkinter import messagebox

def create_connection():
    """Crea y retorna una conexión a SQLite"""
    try:
        # La base de datos se creará en el mismo directorio que la aplicación
        db_path = "inventario_usm.db"
        
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row  # Para acceder a las columnas por nombre
        
        # Crear las tablas si no existen
        create_tables(conn)
        
        return conn
    except sqlite3.Error as e:
        messagebox.showerror("Error de conexión",
                           f"No se pudo conectar a SQLite: {e}")
        return None

def create_tables(conn):
    """Crea todas las tablas necesarias en SQLite"""
    cursor = conn.cursor()
    
    # CATEGORIAS
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS categorias (
            id_categoria INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre VARCHAR(100) NOT NULL UNIQUE,
            activo BOOLEAN DEFAULT TRUE
        )
    ''')
    
    # DEPARTAMENTOS
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS departamentos (
            id_departamento INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre VARCHAR(100) NOT NULL UNIQUE,
            activo BOOLEAN DEFAULT TRUE
        )
    ''')
    
    # UBICACIONES
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ubicaciones (
            id_ubicacion INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre VARCHAR(100) NOT NULL UNIQUE,
            activo BOOLEAN DEFAULT TRUE
        )
    ''')
    
    # MARCAS
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS marcas (
            id_marca INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre VARCHAR(100) NOT NULL UNIQUE,
            activo BOOLEAN DEFAULT TRUE
        )
    ''')
    
    # SOLICITANTES
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS solicitantes (
            id_solicitante INTEGER PRIMARY KEY AUTOINCREMENT,
            cedula VARCHAR(20) NOT NULL UNIQUE,
            nombre VARCHAR(100) NOT NULL,
            id_departamento INTEGER REFERENCES departamentos(id_departamento),
            activo BOOLEAN DEFAULT TRUE
        )
    ''')
    
    # PRODUCTOS
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS productos (
            id_producto INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo VARCHAR(50) NOT NULL UNIQUE,
            nombre VARCHAR(100) NOT NULL,
            id_marca INTEGER REFERENCES marcas(id_marca),
            id_categoria INTEGER REFERENCES categorias(id_categoria),
            activo BOOLEAN DEFAULT TRUE,
            stock_minimo INTEGER DEFAULT 0 CHECK (stock_minimo >= 0)
        )
    ''')
    
    # USUARIOS
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_completo VARCHAR(100) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            usuario VARCHAR(50) UNIQUE NOT NULL,
            password VARCHAR(64) NOT NULL,
            rol VARCHAR(20) DEFAULT 'usuario',
            fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            activo BOOLEAN DEFAULT TRUE
        )
    ''')
    
    # SOLICITUDES
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS solicitudes (
            id_solicitud INTEGER PRIMARY KEY AUTOINCREMENT,
            id_departamento INTEGER REFERENCES departamentos(id_departamento),
            id_solicitante INTEGER REFERENCES solicitantes(id_solicitante),
            numero_memorandum VARCHAR(50) UNIQUE,
            fecha_solicitud TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            comentario TEXT,
            id_responsable_entrega INTEGER REFERENCES usuarios(id),
            activo BOOLEAN DEFAULT TRUE
        )
    ''')
    
    # DETALLE SOLICITUD
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS detalle_solicitud (
            id_detalle_solicitud INTEGER PRIMARY KEY AUTOINCREMENT,
            id_solicitud INTEGER NOT NULL REFERENCES solicitudes(id_solicitud),
            id_producto INTEGER NOT NULL REFERENCES productos(id_producto),
            cantidad INTEGER NOT NULL CHECK (cantidad > 0)
        )
    ''')
    
    # INVENTARIO
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inventario (
            id_inventario INTEGER PRIMARY KEY AUTOINCREMENT,
            id_producto INTEGER NOT NULL REFERENCES productos(id_producto),
            id_ubicacion INTEGER REFERENCES ubicaciones(id_ubicacion),
            stock INTEGER NOT NULL DEFAULT 0,
            estado_stock VARCHAR(20) NOT NULL CHECK (estado_stock IN ('disponible', 'reservado', 'agotado', 'stock bajo'))
        )
    ''')
    
    # SOLICITUDES DE COMPRA
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS solicitudes_compra (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            producto VARCHAR(100) NOT NULL,
            cantidad INTEGER NOT NULL,
            motivo VARCHAR(50) NOT NULL,
            prioridad VARCHAR(20) NOT NULL,
            proveedor VARCHAR(100),
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            estado VARCHAR(20) DEFAULT 'Pendiente'
        )
    ''')
    
    # PROVEEDORES
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS proveedores (
            id_proveedor INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre VARCHAR(100) NOT NULL UNIQUE,
            contacto VARCHAR(100),
            telefono VARCHAR(20),
            email VARCHAR(100),
            direccion TEXT,
            redes_sociales TEXT,
            valoracion INTEGER CHECK (valoracion BETWEEN 1 AND 5),
            manejo_precios VARCHAR(20) CHECK (manejo_precios IN ('Bajo', 'Medio', 'Alto')),
            comentarios TEXT,
            activo BOOLEAN DEFAULT TRUE
        )
    ''')
    
    # PROVEEDOR-CATEGORIA
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS proveedor_categoria (
            id_proveedor INTEGER REFERENCES proveedores(id_proveedor),
            id_categoria INTEGER REFERENCES categorias(id_categoria),
            PRIMARY KEY (id_proveedor, id_categoria)
        )
    ''')
    
    # PROVEEDOR-PRODUCTO
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS proveedor_producto (
            id_proveedor INTEGER REFERENCES proveedores(id_proveedor),
            id_producto INTEGER REFERENCES productos(id_producto),
            PRIMARY KEY (id_proveedor, id_producto)
        )
    ''')
    
    # MOVIMIENTOS
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS movimientos (
            id_movimiento INTEGER PRIMARY KEY AUTOINCREMENT,
            id_producto INTEGER NOT NULL REFERENCES productos(id_producto),
            tipo VARCHAR(10) NOT NULL CHECK (tipo IN ('Entrada', 'Salida')),
            cantidad INTEGER NOT NULL,
            id_responsable INTEGER REFERENCES usuarios(id),
            referencia VARCHAR(100),
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    
    # Crear usuario admin por defecto si no existe
    cursor.execute("SELECT COUNT(*) FROM usuarios WHERE usuario = 'admin'")
    if cursor.fetchone()[0] == 0:
        cursor.execute('''
            INSERT INTO usuarios (nombre_completo, email, usuario, password, rol)
            VALUES ('Administrador', 'admin@usm.edu', 'admin', 
                   '8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918', 'admin')
        ''')  # password: admin (SHA-256)
        conn.commit()