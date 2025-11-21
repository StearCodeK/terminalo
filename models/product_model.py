from database import create_connection


class ProductModel:
    def __init__(self):
        self.conn = create_connection()
        self.cursor = self.conn.cursor()

    def get_id_by_name(self, table, name):
        """Obtener ID por nombre de una tabla relacionada SOLO SI ESTÁ ACTIVO"""
        id_column = {
            'marcas': 'id_marca',
            'categorias': 'id_categoria',
            'ubicaciones': 'id_ubicacion'
        }[table]

        try:
            self.cursor.execute(
                f"SELECT {id_column} FROM {table} WHERE nombre = ? AND activo = 1", (name,))
            result = self.cursor.fetchone()
            return result[0] if result else None
        except Exception as e:
            print(f"Error getting ID by name: {e}")
            return None

    def get_products(self, extra_where="", params=()):
        """Obtener todos los productos con filtros opcionales"""
        # CAMBIO: Reemplazar ILIKE por LIKE para SQLite
        query = """
        SELECT 
            p.id_producto, p.codigo, p.nombre, 
            m.nombre as marca, 
            c.nombre as categoria, 
            i.stock, 
            u.nombre as ubicacion, 
            i.estado_stock,
            p.stock_minimo
        FROM productos p
        LEFT JOIN marcas m ON p.id_marca = m.id_marca
        LEFT JOIN categorias c ON p.id_categoria = c.id_categoria
        LEFT JOIN inventario i ON p.id_producto = i.id_producto
        LEFT JOIN ubicaciones u ON i.id_ubicacion = u.id_ubicacion
        WHERE p.activo = 1
        """ + extra_where + " ORDER BY p.nombre ASC"

        try:
            self.cursor.execute(query, params)
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error getting products: {e}")
            return []

    def get_combobox_data(self, table):
        """Obtener datos para comboboxes - SOLO ACTIVOS"""
        try:
            id_column = {
                'ubicaciones': 'id_ubicacion',
                'categorias': 'id_categoria',
                'marcas': 'id_marca'
            }[table]

            # Verificar si la tabla tiene columna 'activo' usando PRAGMA
            self.cursor.execute(f"PRAGMA table_info({table})")
            columns = self.cursor.fetchall()
            has_activo_column = any('activo' in col[1].lower() for col in columns)

            if has_activo_column:
                query = f"SELECT {id_column}, nombre FROM {table} WHERE activo = 1 ORDER BY nombre"
            else:
                query = f"SELECT {id_column}, nombre FROM {table} ORDER BY nombre"

            self.cursor.execute(query)
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error al cargar datos: {e}")
            self.conn.rollback()
            return []

    def update_product_stock_status(self):
        """Actualizar estado de stock de productos considerando stock mínimo"""
        stock_updates = []
        inventario_data = self.get_products()

        for item in inventario_data:
            stock = item[5] if item[5] else 0
            estado = item[7] if item[7] else "disponible"
            
            # Obtener stock mínimo del producto
            self.cursor.execute("SELECT stock_minimo FROM productos WHERE id_producto = ?", (item[0],))
            stock_minimo_result = self.cursor.fetchone()
            stock_minimo = stock_minimo_result[0] if stock_minimo_result else 0

            # Actualizar estado basado en stock y stock mínimo
            if stock == 0:
                nuevo_estado = "agotado"
            elif stock <= stock_minimo:
                nuevo_estado = "stock bajo"
            else:
                nuevo_estado = "disponible"

            if estado != nuevo_estado:
                stock_updates.append((nuevo_estado, item[0]))

        if stock_updates:
            for estado, id_producto in stock_updates:
                try:
                    self.cursor.execute(
                        "UPDATE inventario SET estado_stock = ? WHERE id_producto = ?",
                        (estado, id_producto))
                except Exception as e:
                    print(f"Error updating stock status: {e}")
                    continue

            try:
                self.conn.commit()
            except Exception as e:
                print(f"Error committing stock updates: {e}")
                self.conn.rollback()

        return inventario_data

    def get_product_data(self, product_id):
        """Obtener datos de un producto específico"""
        try:
            self.cursor.execute("""
                SELECT p.id_producto, p.codigo, p.nombre, p.id_marca, p.id_categoria,
                    i.stock, i.id_ubicacion, i.estado_stock, p.stock_minimo
                FROM productos p
                LEFT JOIN inventario i ON p.id_producto = i.id_producto
                WHERE p.id_producto = ?
            """, (product_id,))
            return self.cursor.fetchone()
        except Exception as e:
            print(f"Error getting product data: {e}")
            return None

    def get_ubicacion_id(self, product_id):
        """Obtener ID de ubicación de un producto"""
        try:
            self.cursor.execute(
                "SELECT id_ubicacion FROM inventario WHERE id_producto = ?", (product_id,))
            result = self.cursor.fetchone()
            return result[0] if result else None
        except Exception as e:
            print(f"Error getting ubicacion ID: {e}")
            return None

    def get_old_stock(self, product_id):
        """Obtener stock anterior de un producto"""
        try:
            self.cursor.execute(
                "SELECT stock FROM inventario WHERE id_producto = ?", (product_id,))
            result = self.cursor.fetchone()
            return result[0] if result else 0
        except Exception as e:
            print(f"Error getting old stock: {e}")
            return 0

    def save_product(self, product_data, product_id=None):
        """Guardar o actualizar un producto"""
        try:
            if product_id:
                # Actualizar producto existente
                query = """
                UPDATE productos 
                SET codigo = ?, nombre = ?, id_marca = ?, id_categoria = ?, stock_minimo = ?
                WHERE id_producto = ?
                """
                self.cursor.execute(query, (
                    product_data['codigo'],
                    product_data['nombre'],
                    product_data['marca_id'],
                    product_data['categoria_id'],
                    product_data['stock_minimo'],
                    product_id
                ))

                # Verificar si existe en inventario
                self.cursor.execute(
                    "SELECT id_inventario FROM inventario WHERE id_producto = ?", (product_id,))
                inventario_existe = self.cursor.fetchone()

                if inventario_existe:
                    # Actualizar inventario
                    self.cursor.execute("""
                        UPDATE inventario 
                        SET stock = ?, id_ubicacion = ?, estado_stock = ?
                        WHERE id_producto = ?
                    """, (
                        product_data['stock'],
                        product_data['ubicacion_id'],
                        product_data['estado'],
                        product_id
                    ))
                else:
                    # Insertar en inventario
                    self.cursor.execute("""
                        INSERT INTO inventario 
                        (id_producto, id_ubicacion, stock, estado_stock)
                        VALUES (?, ?, ?, ?)
                    """, (
                        product_id,
                        product_data['ubicacion_id'],
                        product_data['stock'],
                        product_data['estado']
                    ))

                self.conn.commit()
                return product_id

            else:
                # Insertar nuevo producto
                query = """
                INSERT INTO productos 
                (codigo, nombre, id_marca, id_categoria, stock_minimo)
                VALUES (?, ?, ?, ?, ?)
                """
                self.cursor.execute(query, (
                    product_data['codigo'],
                    product_data['nombre'],
                    product_data['marca_id'],
                    product_data['categoria_id'],
                    product_data['stock_minimo']
                ))

                new_product_id = self.cursor.lastrowid

                # Insertar en inventario
                self.cursor.execute("""
                    INSERT INTO inventario 
                    (id_producto, id_ubicacion, stock, estado_stock)
                    VALUES (?, ?, ?, ?)
                """, (
                    new_product_id,
                    product_data['ubicacion_id'],
                    product_data['stock'],
                    product_data['estado']
                ))

                self.conn.commit()
                return new_product_id

        except Exception as e:
            self.conn.rollback()
            raise e

    def delete_product(self, product_id):
        """Marcar producto como inactivo"""
        try:
            self.cursor.execute(
                "UPDATE productos SET activo = 0 WHERE id_producto = ?",
                (product_id,))
            self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            raise e

    def add_stock(self, product_id, quantity):
        """Agregar stock a un producto"""
        try:
            self.cursor.execute(
                "UPDATE inventario SET stock = stock + ? WHERE id_producto = ?",
                (int(quantity), product_id))
            self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            raise e

    def add_new_value(self, table, value):
        """Agregar nuevo valor a una tabla relacionada - RETORNA EL NUEVO VALOR"""
        try:
            id_columns = {
                'ubicaciones': 'id_ubicacion',
                'categorias': 'id_categoria',
                'marcas': 'id_marca'
            }
            id_column = id_columns.get(table, f"id_{table[:-1]}")

            # Insertar el nuevo valor
            self.cursor.execute(
                f"INSERT INTO {table} (nombre) VALUES (?)",
                (value,))

            new_id = self.cursor.lastrowid
            
            # Obtener el registro completo recién insertado
            self.cursor.execute(f"SELECT {id_column}, nombre FROM {table} WHERE {id_column} = ?", (new_id,))
            result = self.cursor.fetchone()
            
            self.conn.commit()
            return result  # Retorna el nuevo valor (id, nombre)
        except Exception as e:
            self.conn.rollback()
            raise e