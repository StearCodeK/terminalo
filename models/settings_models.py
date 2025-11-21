# models/settings_models.py
import sqlite3
from database import create_connection


class SettingsModel:
    def __init__(self):
        self.conn = create_connection()
        self.cursor = self.conn.cursor()

    def get_all_data(self, table_name):
        """Obtiene todos los datos de una tabla (incluyendo inactivos)"""
        try:
            if table_name == "solicitantes":
                query = """
                SELECT s.id_solicitante, s.cedula, s.nombre, d.nombre as departamento, s.activo
                FROM solicitantes s
                LEFT JOIN departamentos d ON s.id_departamento = d.id_departamento
                """
            elif table_name == "productos":
                query = """
                SELECT p.id_producto, p.codigo, p.nombre, 
                    COALESCE(m.nombre, 'Sin marca') as marca, 
                    COALESCE(c.nombre, 'Sin categoría') as categoria, 
                    p.stock_minimo, p.activo
                FROM productos p
                LEFT JOIN marcas m ON p.id_marca = m.id_marca AND m.activo = 1
                LEFT JOIN categorias c ON p.id_categoria = c.id_categoria AND c.activo = 1
                """
            elif table_name == "usuarios":
                query = "SELECT id, nombre_completo, email, usuario, rol, activo FROM usuarios"
            elif table_name == "proveedores":
                query = "SELECT id_proveedor, nombre, contacto, telefono, email, direccion, activo FROM proveedores"
            else:
                # Para tablas maestras simples
                try:
                    self.cursor.execute(f"PRAGMA table_info({table_name})")
                    columns = self.cursor.fetchall()
                    has_activo = any('activo' in col[1].lower() for col in columns)
                    
                    if has_activo:
                        query = f"SELECT *, activo FROM {table_name}"
                    else:
                        query = f"SELECT * FROM {table_name}"
                except:
                    query = f"SELECT * FROM {table_name}"

            self.cursor.execute(query)
            return self.cursor.fetchall()
        except Exception as e:
            raise Exception(f"Error al obtener datos: {str(e)}")

    def get_active_data(self, table_name):
        """Obtiene solo los datos activos para combobox"""
        try:
            if table_name == "solicitantes":
                query = """
                SELECT s.id_solicitante, s.cedula, s.nombre, d.nombre as departamento
                FROM solicitantes s
                LEFT JOIN departamentos d ON s.id_departamento = d.id_departamento
                WHERE s.activo = 1 AND d.activo = 1
                """
            elif table_name == "productos":
                query = """
                SELECT p.id_producto, p.codigo, p.nombre, 
                    COALESCE(m.nombre, 'Sin marca') as marca, 
                    COALESCE(c.nombre, 'Sin categoría') as categoria
                FROM productos p
                LEFT JOIN marcas m ON p.id_marca = m.id_marca AND m.activo = 1
                LEFT JOIN categorias c ON p.id_categoria = c.id_categoria AND c.activo = 1
                WHERE p.activo = 1
                """
            elif table_name == "usuarios":
                query = "SELECT id, nombre_completo, email, usuario, rol FROM usuarios WHERE activo = 1"
            else:
                # Verificar si la tabla tiene columna activo
                try:
                    self.cursor.execute(f"PRAGMA table_info({table_name})")
                    columns = self.cursor.fetchall()
                    has_activo = any('activo' in col[1].lower() for col in columns)
                    
                    if has_activo:
                        query = f"SELECT * FROM {table_name} WHERE activo = 1"
                    else:
                        query = f"SELECT * FROM {table_name}"
                except:
                    query = f"SELECT * FROM {table_name}"

            self.cursor.execute(query)
            return self.cursor.fetchall()
        except Exception as e:
            raise Exception(f"Error al obtener datos activos: {str(e)}")

    def get_item_by_id(self, table_name, id_column, item_id):
        """Obtiene un item específico por ID"""
        try:
            query = f"SELECT * FROM {table_name} WHERE {id_column} = ?"
            self.cursor.execute(query, (item_id,))
            return self.cursor.fetchone()
        except Exception as e:
            raise Exception(f"Error al obtener item: {str(e)}")

    def get_related_options(self, table_name):
        """Obtiene opciones ACTIVAS para combobox de tablas relacionadas"""
        try:
            # Mapeo de nombres de tablas a columnas ID y nombres de tabla reales
            table_config = {
                'categoria': {'table': 'categorias', 'id_column': 'id_categoria'},
                'marca': {'table': 'marcas', 'id_column': 'id_marca'},
                'departamento': {'table': 'departamentos', 'id_column': 'id_departamento'},
                'ubicacion': {'table': 'ubicaciones', 'id_column': 'id_ubicacion'},
                'proveedor': {'table': 'proveedores', 'id_column': 'id_proveedor'},
                'solicitante': {'table': 'solicitantes', 'id_column': 'id_solicitante'}
            }
            
            # Determinar la configuración de la tabla
            if table_name in table_config:
                config = table_config[table_name]
                actual_table = config['table']
                id_column = config['id_column']
            elif table_name.endswith('s'):
                actual_table = table_name
                id_column = f"id_{table_name[:-1]}"
            else:
                actual_table = table_name
                id_column = "id"

            # VERIFICACIÓN MÁS ROBUSTA DE LA COLUMNA ACTIVO
            self.cursor.execute(f"PRAGMA table_info({actual_table})")
            columns = self.cursor.fetchall()
            has_activo = any(col[1].lower() == 'activo' for col in columns)
            
            # SIEMPRE filtrar por activo = 1 para combobox
            if has_activo:
                query = f"SELECT {id_column}, nombre FROM {actual_table} WHERE activo = 1 ORDER BY nombre"
            else:
                query = f"SELECT {id_column}, nombre FROM {actual_table} ORDER BY nombre"
                
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except Exception as e:
            raise Exception(f"Error al obtener opciones para {table_name}: {str(e)}")
        
    def insert_item(self, table_name, columns, values):
        """Inserta un nuevo item"""
        try:
            placeholders = ", ".join(["?"] * len(values))
            columns_str = ", ".join(columns)
            query = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"
            
            # Convertir valores para asegurar que los checkboxes se guarden correctamente
            processed_values = []
            for i, (col, val) in enumerate(zip(columns, values)):
                if col == "activo":
                    # Asegurar que el campo activo sea 1 (True) por defecto
                    if val is None or val == "":
                        processed_values.append(1)
                    else:
                        processed_values.append(1 if val else 0)
                else:
                    processed_values.append(val)
            
            self.cursor.execute(query, processed_values)
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            self.conn.rollback()
            raise Exception(f"No se pudo agregar el ítem: {str(e)}")

    def update_item(self, table_name, id_column, item_id, columns, values):
        """Actualiza un item existente"""
        try:
            set_clause = ", ".join([f"{col} = ?" for col in columns])
            query = f"UPDATE {table_name} SET {set_clause} WHERE {id_column} = ?"
            
            # Procesar valores para campos booleanos/activo
            processed_values = []
            for i, (col, val) in enumerate(zip(columns, values)):
                if col == "activo":
                    # Convertir a 1 o 0 para la base de datos
                    if val in (True, 1, "1", "True", "true", "Sí"):
                        processed_values.append(1)
                    else:
                        processed_values.append(0)
                else:
                    processed_values.append(val)
            
            self.cursor.execute(query, processed_values + [item_id])
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            self.conn.rollback()
            raise Exception(f"No se pudo actualizar el ítem: {str(e)}")

    def soft_delete_item(self, table_name, id_column, item_id):
        """Marca un item como inactivo (eliminación lógica)"""
        try:
            # Verificar si la tabla tiene columna activo usando PRAGMA
            self.cursor.execute(f"PRAGMA table_info({table_name})")
            columns = self.cursor.fetchall()
            has_activo = any('activo' in col[1].lower() for col in columns)
            
            if has_activo:
                query = f"UPDATE {table_name} SET activo = 0 WHERE {id_column} = ?"
                self.cursor.execute(query, (item_id,))
                self.conn.commit()
                return True
            else:
                # Si no tiene columna activo, no podemos hacer soft delete
                raise Exception("Esta tabla no soporta eliminación lógica. El registro está siendo usado en otras partes del sistema.")
                
        except sqlite3.Error as e:
            self.conn.rollback()
            raise Exception(f"No se pudo desactivar el ítem: {str(e)}")

    def activate_item(self, table_name, id_column, item_id):
        """Reactiva un item previamente desactivado"""
        try:
            # Verificar si la tabla tiene columna activo usando PRAGMA
            self.cursor.execute(f"PRAGMA table_info({table_name})")
            columns = self.cursor.fetchall()
            has_activo = any('activo' in col[1].lower() for col in columns)
            
            if has_activo:
                query = f"UPDATE {table_name} SET activo = 1 WHERE {id_column} = ?"
                self.cursor.execute(query, (item_id,))
                self.conn.commit()
                
                # Verificar que realmente se actualizó
                self.cursor.execute(f"SELECT activo FROM {table_name} WHERE {id_column} = ?", (item_id,))
                result = self.cursor.fetchone()
                if result and result[0] == 1:
                    return True
                else:
                    return False
            else:
                return False
                
        except sqlite3.Error as e:
            self.conn.rollback()
            raise Exception(f"No se pudo activar el ítem: {str(e)}")

    def delete_item(self, table_name, id_column, item_id):
        """Elimina físicamente un item (solo si no tiene relaciones)"""
        try:
            query = f"DELETE FROM {table_name} WHERE {id_column} = ?"
            self.cursor.execute(query, (item_id,))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError as e:
            self.conn.rollback()
            # Si hay error de integridad referencial, intentar soft delete
            try:
                return self.soft_delete_item(table_name, id_column, item_id)
            except Exception as soft_e:
                raise Exception(f"No se puede eliminar el ítem porque está siendo usado en otras partes del sistema: {str(soft_e)}")
        except sqlite3.Error as e:
            self.conn.rollback()
            raise Exception(f"No se pudo eliminar el ítem: {str(e)}")

    def close_connection(self):
        """Cierra la conexión a la base de datos"""
        if hasattr(self, 'cursor'):
            self.cursor.close()
        if hasattr(self, 'conn'):
            self.conn.close()