from database import create_connection


class SupplierModel:
    def __init__(self):
        self.conn = create_connection()
        self.cursor = self.conn.cursor()

    def get_all_suppliers(self, category_filter="Todas", rating_filter="Todas", price_filter="Todos"):
        """Obtiene todos los proveedores con filtros opcionales"""
        query = """
            SELECT
                ROW_NUMBER() OVER (ORDER BY p.nombre) as nro,
                p.nombre,
                COALESCE(p.contacto, 'N/A'),
                COALESCE(p.telefono, 'N/A'),
                COALESCE(p.email, 'N/A'),
                CASE
                    WHEN p.valoracion IS NULL THEN 'Sin valoración'
                    WHEN p.valoracion = 1 THEN '1 Estrella'
                    ELSE p.valoracion || ' Estrellas'  -- CORREGIDO: || funciona en SQLite
                END as valoracion_texto,
                COALESCE(p.manejo_precios, 'N/A'),
                COALESCE(
                    (SELECT GROUP_CONCAT(DISTINCT c.nombre)  -- CORREGIDO: solo un argumento
                     FROM (
                         SELECT c.nombre
                         FROM proveedor_categoria pc
                         JOIN categorias c ON pc.id_categoria = c.id_categoria
                         WHERE pc.id_proveedor = p.id_proveedor
                         UNION
                         SELECT DISTINCT c.nombre
                         FROM proveedor_producto pp
                         JOIN productos pr ON pp.id_producto = pr.id_producto
                         JOIN categorias c ON pr.id_categoria = c.id_categoria
                         WHERE pp.id_proveedor = p.id_proveedor
                     ) c
                    ), 'N/A'
                ) as categorias
            FROM proveedores p
            WHERE 1=1
        """

        params = []

        if category_filter != "Todas":
            query += """
                AND (
                    EXISTS (
                        SELECT 1 FROM proveedor_categoria pc
                        JOIN categorias c ON pc.id_categoria = c.id_categoria
                        WHERE pc.id_proveedor = p.id_proveedor AND c.nombre = ?
                    )
                    OR EXISTS (
                        SELECT 1 FROM proveedor_producto pp
                        JOIN productos pr ON pp.id_producto = pr.id_producto
                        JOIN categorias c ON pr.id_categoria = c.id_categoria
                        WHERE pp.id_proveedor = p.id_proveedor AND c.nombre = ?
                    )
                )
            """
            params.extend([category_filter, category_filter])

        if rating_filter != "Todas":
            rating_value = int(rating_filter.split()[0])
            query += " AND p.valoracion = ?"
            params.append(rating_value)

        if price_filter != "Todos":
            query += " AND p.manejo_precios = ?"
            params.append(price_filter)

        query += " ORDER BY p.nombre"
        
        self.cursor.execute(query, params)
        rows = self.cursor.fetchall()
        # CONVERTIR objetos Row a tuplas
        return [tuple(row) for row in rows]

    def get_supplier_by_name(self, supplier_name):
        """Obtiene un proveedor por nombre"""
        self.cursor.execute("""
            SELECT id_proveedor, nombre, contacto, telefono, email, direccion,
                   redes_sociales, valoracion, manejo_precios, comentarios
            FROM proveedores WHERE nombre = ?
        """, (supplier_name,))
        result = self.cursor.fetchone()
        return tuple(result) if result else None

    def get_supplier_by_id(self, supplier_id):
        """Obtiene un proveedor por ID"""
        self.cursor.execute("""
            SELECT nombre, contacto, telefono, email, direccion,
                   redes_sociales, valoracion, manejo_precios, comentarios
            FROM proveedores WHERE id_proveedor = ?
        """, (supplier_id,))
        result = self.cursor.fetchone()
        return tuple(result) if result else None

    def create_supplier(self, data):
        """Crea un nuevo proveedor"""
        self.cursor.execute("""
            INSERT INTO proveedores (
                nombre, contacto, telefono, email, direccion,
                redes_sociales, valoracion, manejo_precios, comentarios
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, data)
        new_id = self.cursor.lastrowid  # CORREGIDO: RETURNING -> lastrowid para SQLite
        self.conn.commit()
        return new_id

    def update_supplier(self, supplier_id, data):
        """Actualiza un proveedor existente"""
        self.cursor.execute("""
            UPDATE proveedores SET
                nombre = ?, contacto = ?, telefono = ?, email = ?,
                direccion = ?, redes_sociales = ?, valoracion = ?,
                manejo_precios = ?, comentarios = ?
            WHERE id_proveedor = ?
        """, data + (supplier_id,))
        self.conn.commit()

    def delete_supplier(self, supplier_name):
        """Elimina un proveedor"""
        self.cursor.execute(
            "DELETE FROM proveedores WHERE nombre = ?", (supplier_name,))
        self.conn.commit()

    def get_supplier_categories(self, supplier_id):
        """Obtiene las categorías de un proveedor"""
        self.cursor.execute("""
            SELECT DISTINCT c.nombre
            FROM (
                SELECT id_categoria FROM proveedor_categoria WHERE id_proveedor = ?
                UNION
                SELECT p.id_categoria FROM proveedor_producto pp
                JOIN productos p ON pp.id_producto = p.id_producto
                WHERE pp.id_proveedor = ?
            ) AS cat_ids
            JOIN categorias c ON cat_ids.id_categoria = c.id_categoria
        """, (supplier_id, supplier_id))
        rows = self.cursor.fetchall()
        categories = [row[0] for row in rows] if rows else ["Ninguna"]
        return categories

    def get_supplier_products(self, supplier_id):
        """Obtiene los productos de un proveedor"""
        self.cursor.execute("""
            SELECT p.nombre, c.nombre as categoria
            FROM proveedor_producto pp
            JOIN productos p ON pp.id_producto = p.id_producto
            JOIN categorias c ON p.id_categoria = c.id_categoria
            WHERE pp.id_proveedor = ?
            ORDER BY p.nombre
        """, (supplier_id,))
        rows = self.cursor.fetchall()
        return [tuple(row) for row in rows]

    def get_available_products(self, supplier_id):
        """Obtiene productos disponibles para agregar al proveedor"""
        self.cursor.execute("""
            SELECT p.id_producto, p.nombre, c.nombre
            FROM productos p
            JOIN categorias c ON p.id_categoria = c.id_categoria
            WHERE p.activo = 1  -- CORREGIDO: TRUE -> 1 para SQLite
            AND p.id_producto NOT IN (
                SELECT id_producto FROM proveedor_producto
                WHERE id_proveedor = ?
            )
            ORDER BY p.nombre
        """, (supplier_id,))
        rows = self.cursor.fetchall()
        return [tuple(row) for row in rows]

    def add_product_to_supplier(self, supplier_id, product_id):
        """Agrega un producto al proveedor"""
        self.cursor.execute("""
            INSERT INTO proveedor_producto (id_proveedor, id_producto)
            VALUES (?, ?)
        """, (supplier_id, product_id))
        self.conn.commit()

    def remove_product_from_supplier(self, supplier_id, product_id):
        """Elimina un producto del proveedor"""
        self.cursor.execute("""
            DELETE FROM proveedor_producto
            WHERE id_proveedor = ? AND id_producto = ?
        """, (supplier_id, product_id))
        self.conn.commit()

    def get_categories(self):
        """Obtiene todas las categorías"""
        self.cursor.execute("SELECT nombre FROM categorias ORDER BY nombre")
        rows = self.cursor.fetchall()
        return [row[0] for row in rows]

    def get_product_id_by_name(self, product_name):
        """Obtiene el ID de un producto por nombre"""
        self.cursor.execute(
            "SELECT id_producto FROM productos WHERE nombre = ?", (product_name,))
        result = self.cursor.fetchone()
        return result[0] if result else None

    def set_supplier_category(self, supplier_id, category_name):
        """Asigna (o reemplaza) la categoría principal de un proveedor."""
        # Normalizar valores vacíos o placeholders
        if not category_name or category_name in ("N/A", "Todas"):
            # Si no hay categoría válida, solo eliminar asociaciones previas
            self.cursor.execute(
                "DELETE FROM proveedor_categoria WHERE id_proveedor = ?", (supplier_id,))
            self.conn.commit()
            return

        # Buscar id_categoria por nombre
        self.cursor.execute(
            "SELECT id_categoria FROM categorias WHERE nombre = ?", (category_name,))
        res = self.cursor.fetchone()
        if not res:
            # No existe la categoría; no hacemos nada
            return

        id_categoria = res[0]

        # Reemplazar asociaciones previas por la nueva
        self.cursor.execute(
            "DELETE FROM proveedor_categoria WHERE id_proveedor = ?", (supplier_id,))

        # Evitar duplicados
        self.cursor.execute(
            "SELECT 1 FROM proveedor_categoria WHERE id_proveedor = ? AND id_categoria = ?",
            (supplier_id, id_categoria)
        )
        if not self.cursor.fetchone():
            self.cursor.execute(
                "INSERT INTO proveedor_categoria (id_proveedor, id_categoria) VALUES (?, ?)",
                (supplier_id, id_categoria)
            )
        self.conn.commit()
    
    def set_supplier_categories(self, supplier_id, categories):
        """Asigna varias categorías a un proveedor."""
        # Elimina asociaciones previas
        self.cursor.execute(
            "DELETE FROM proveedor_categoria WHERE id_proveedor = ?", (supplier_id,))
        # Inserta nuevas asociaciones
        for cat in categories:
            self.cursor.execute(
                "SELECT id_categoria FROM categorias WHERE nombre = ?", (cat,))
            res = self.cursor.fetchone()
            if res:
                id_categoria = res[0]
                self.cursor.execute(
                    "INSERT INTO proveedor_categoria (id_proveedor, id_categoria) VALUES (?, ?)",
                    (supplier_id, id_categoria)
                )
        self.conn.commit()