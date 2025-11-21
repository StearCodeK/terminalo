from datetime import datetime
from database import create_connection


class MovementModel:
    def __init__(self):
        self.conn = create_connection()
        self.cursor = self.conn.cursor()

    def get_all_movements(self, movement_type="Todos", date_from=None, date_to=None):
        """Obtiene todos los movimientos con filtros opcionales"""
        query = """
            SELECT 
                ROW_NUMBER() OVER (ORDER BY m.fecha DESC) as nro,
                strftime('%d/%m/%Y %H:%M', m.fecha) as fecha,  
                m.tipo,
                p.nombre as producto,
                m.cantidad,
                COALESCE(usr.nombre_completo, 'N/A') as responsable,
                COALESCE(m.referencia, 'N/A') as referencia
            FROM movimientos m
            JOIN productos p ON m.id_producto = p.id_producto
            LEFT JOIN usuarios usr ON m.id_responsable = usr.id
            WHERE 1=1
        """

        params = []

        # Aplicar filtro de tipo
        if movement_type != "Todos":
            query += " AND m.tipo = ?"
            params.append(movement_type)

        # Aplicar filtros de fecha
        if date_from:
            query += " AND m.fecha >= ?"
            params.append(date_from)
        if date_to:
            query += " AND m.fecha <= ?"
            params.append(date_to)

        query += " ORDER BY m.fecha DESC"

        self.cursor.execute(query, params)
        rows = self.cursor.fetchall()
        
        # CONVERTIR objetos Row a tuplas para que se muestren en la tabla
        return [tuple(row) for row in rows]

    def register_movement(self, id_producto, tipo, cantidad, id_responsable=None, referencia=None):
        """Registra un movimiento en la base de datos (sin ubicación)"""
        try:
            # Obtener el nombre del producto para la referencia
            self.cursor.execute(
                "SELECT nombre FROM productos WHERE id_producto = ?", (id_producto,))
            result = self.cursor.fetchone()
            producto_nombre = result[0] if result else "Producto Desconocido"

            # Determinar la referencia automática basada en el tipo de movimiento
            if referencia is None:
                if tipo == "Entrada":
                    referencia = f"Entrada de stock - {producto_nombre}"
                elif tipo == "Salida":
                    referencia = f"Salida de stock - {producto_nombre}"
                elif tipo == "Nuevo":
                    referencia = f"Producto nuevo - {producto_nombre}"

            # Validar que el responsable exista si se proporciona
            if id_responsable is not None:
                self.cursor.execute(
                    "SELECT id FROM usuarios WHERE id = ?", (id_responsable,))
                if not self.cursor.fetchone():
                    id_responsable = None

            self.cursor.execute("""
                INSERT INTO movimientos (
                    id_producto, tipo, cantidad, id_responsable, referencia, fecha
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                id_producto,
                tipo,
                cantidad,
                id_responsable,
                referencia,
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Formato SQLite
            ))
            self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            raise e

    def get_product_name(self, product_id):
        """Obtiene el nombre de un producto por ID"""
        self.cursor.execute(
            "SELECT nombre FROM productos WHERE id_producto = ?", (product_id,))
        result = self.cursor.fetchone()
        return result[0] if result else None