# controllers/settings_controller.py
import tkinter as tk
from tkinter import ttk
from models.settings_models import SettingsModel
from views.settings_views import SettingsView


class SettingsController:
    def __init__(self, app):
        self.app = app
        self.model = SettingsModel()
        self.view = SettingsView(app)
        self.trees = {}  # <--- Agrega esto

        # Configuración de las pestañas - AGREGAR COLUMNA ACTIVO
        self.tabs_config = {
            "categorias": {
                "tab_name": "📦 Categorías",
                "table_name": "categorias",
                "fields_config": [
                    ("nombre", "entry", None),
                    ("activo", "checkbox", None)
                ],
                "display_columns": ["Nro", "Nombre", "Activo"],
                "column_widths": [50, 200, 60],
                "id_column": "id_categoria"
            },
            "departamentos": {
                "tab_name": "🏢 Departamentos",
                "table_name": "departamentos",
                "fields_config": [
                    ("nombre", "entry", None),
                    ("activo", "checkbox", None)
                ],
                "display_columns": ["Nro", "Nombre", "Activo"],
                "column_widths": [50, 200, 60],
                "id_column": "id_departamento"
            },
            "ubicaciones": {
                "tab_name": "📍 Ubicaciones",
                "table_name": "ubicaciones",
                "fields_config": [
                    ("nombre", "entry", None),
                    ("activo", "checkbox", None)
                ],
                "display_columns": ["Nro", "Nombre", "Activo"],
                "column_widths": [50, 200, 60],
                "id_column": "id_ubicacion"
            },
            "marcas": {
                "tab_name": "🏷️ Marcas",
                "table_name": "marcas",
                "fields_config": [
                    ("nombre", "entry", None),
                    ("activo", "checkbox", None)
                ],
                "display_columns": ["Nro", "Nombre", "Activo"],
                "column_widths": [50, 200, 60],
                "id_column": "id_marca"
            },
            "solicitantes": {
                "tab_name": "🙋 Solicitantes",
                "table_name": "solicitantes",
                "fields_config": [
                    ("cedula", "entry", None),
                    ("nombre", "entry", None),
                    ("id_departamento", "combobox", []),
                    ("activo", "checkbox", None)
                ],
                "display_columns": ["Nro", "Cédula", "Nombre", "Departamento", "Activo"],
                "column_widths": [50, 100, 150, 120, 60],
                "id_column": "id_solicitante"
            },
            "proveedores": {
                "tab_name": "👥 Proveedores",
                "table_name": "proveedores",
                "fields_config": [
                    ("nombre", "entry", None),
                    ("contacto", "entry", None),
                    ("telefono", "entry", None),
                    ("email", "entry", None),
                    ("direccion", "entry", None),
                    ("activo", "checkbox", None)
                ],
                "display_columns": ["Nro", "Nombre", "Contacto", "Teléfono", "Email", "Dirección", "Activo"],
                "column_widths": [50, 120, 120, 100, 150, 180, 60],  # Ajusta el ancho de Dirección si lo deseas
                "id_column": "id_proveedor"
            },
            "usuarios": {
                "tab_name": "👤 Usuarios",
                "table_name": "usuarios",
                "fields_config": [
                    ("nombre_completo", "entry", None),
                    ("email", "entry", None),
                    ("usuario", "entry", None),
                    ("rol", "combobox", ["admin", "usuario"]),
                    ("activo", "checkbox", None)
                ],
                "display_columns": ["Nro", "Nombre", "Email", "Usuario", "Rol", "Activo"],
                "column_widths": [50, 120, 150, 100, 80, 60],
                "id_column": "id"
            },
            "productos": {
                "tab_name": "📦 Productos",
                "table_name": "productos",
                "fields_config": [
                    ("codigo", "entry", None),
                    ("nombre", "entry", None),
                    ("id_marca", "combobox", []),
                    ("id_categoria", "combobox", []),
                    ("stock_minimo", "entry", None),  # NUEVO CAMPO
                    ("activo", "checkbox", None)
                ],
                "display_columns": ["Nro", "Código", "Nombre", "Marca", "Categoría", "Stock (m)", "Activo"],
                "column_widths": [50, 80, 150, 100, 100, 80, 60],
                "id_column": "id_producto"
            }
        }
    # controllers/settings_controller.py - MODIFICAR SOLO ESTE MÉTODO
    def show_settings(self):
        """Muestra la interfaz de configuración"""
        notebook = self.view.show_settings()

        # Obtener el rol del usuario actual
        current_user_role = getattr(self.app, 'current_user_role', 'usuario')
        is_admin = current_user_role == 'admin'

        # Crear pestañas según permisos
        for tab_key, config in self.tabs_config.items():
            # Si no es admin, omitir la pestaña de usuarios
            if tab_key == "usuarios" and not is_admin:
                continue
                
            self._create_tab(notebook, tab_key, config)

    def _create_tab(self, notebook, tab_key, config):
        """Crea una pestaña específica"""
        tree, button_frame = self.view.create_settings_tab(notebook, config)
        self.trees[tab_key] = tree  # <--- Guarda el tree por tab_key

        # Crear botones en la View con funcionalidad extendida
        self.view.create_settings_buttons(
            button_frame, 
            tab_key,
            self.add_item_dialog,
            self.edit_item_dialog,
            self.delete_item,
            self.activate_item,  # Nuevo botón para activar
            self.refresh_tab
        )

        # Cargar datos iniciales
        self.refresh_tab(tab_key)

    def refresh_tab(self, tab_key):
        """Refresca los datos de una pestaña"""
        try:
            config = self.tabs_config[tab_key]
            data = self.model.get_all_data(config["table_name"])
            tree = self.trees.get(tab_key)

            display_data = []
            for idx, row in enumerate(data, 1):
                row = list(row)
                display_row = [idx] + row[1:]  # Agregar número y el resto de los datos
                
                # Convertir campo "activo" a "Sí"/"No" si existe en la tabla
                if "activo" in [field[0] for field in config["fields_config"]]:
                    # Encontrar el índice del campo activo en los datos
                    activo_index = None
                    for i, field in enumerate(config["fields_config"]):
                        if field[0] == "activo":
                            # +1 porque display_row empieza con idx
                            activo_index = i + 1  
                            break
                    
                    if activo_index is not None and activo_index < len(display_row):
                        activo_value = display_row[activo_index]
                        # Convertir cualquier representación de booleano a "Sí"/"No"
                        if activo_value in (True, 1, "1", "True", "true", "Sí"):
                            display_row[activo_index] = "Sí"
                        else:
                            display_row[activo_index] = "No"
                
                display_data.append(display_row)

            self.view.load_table_data(tree, display_data)
        except Exception as e:
            self.view.show_message(
                "Error", f"Error al cargar datos: {str(e)}", "error")
        
    def add_item_dialog(self, tab_key):
        """Muestra diálogo para agregar un nuevo ítem"""
        config = self.tabs_config[tab_key]
        
        # Preparar campos para relaciones
        fields_config = self._prepare_fields_config(config["fields_config"])
        
        # Crear diálogo en la View
        dialog, entries, entry_vars, save_btn = self.view.create_settings_dialog(
            f"Agregar {config['tab_name']}", 
            fields_config
        )

        # Configurar opciones para combobox de relaciones
        self._setup_relation_comboboxes(entries, config["fields_config"]) 
        def save_item():
            try:
                values = self.view.get_form_values(fields_config, entry_vars)
                # Convertir nombres de combobox a ids
                for field_name, field_type, _ in fields_config:
                    if field_type == "combobox" and field_name in entries:
                        selected_name = values[field_name]
                        if hasattr(entries[field_name], "name_to_id"):
                            values[field_name] = entries[field_name].name_to_id.get(selected_name, None)
                
                # Validar campos requeridos
                self._validate_required_fields(values, config["fields_config"])
                
                # Asegurar que el campo "activo" sea True por defecto para nuevos registros
                if "activo" in values:
                    if values["activo"] is None or values["activo"] == "":
                        values["activo"] = True
                
                # Preparar datos para inserción
                columns = [field[0] for field in config["fields_config"]]
                values_list = [values[field[0]] for field in config["fields_config"]]
                
                # Insertar en la base de datos
                self.model.insert_item(config["table_name"], columns, values_list)
                
                self.view.show_message("Éxito", "Ítem agregado correctamente", "info")
                dialog.destroy()
                self.refresh_tab(tab_key)
                
            except Exception as e:
                self.view.show_message("Error", str(e), "error")

        # Conectar el botón guardar
        save_btn.configure(command=save_item)

    def edit_item_dialog(self, tab_key):
        config = self.tabs_config[tab_key]
        tree = self.trees[tab_key]
        selected = tree.selection()
        if not selected:
            self.view.show_message("Advertencia", "Seleccione un elemento para editar.", "warning")
            return

        selected_id = tree.item(selected[0])["values"][0]
        try:
            # Obtener datos actuales del modelo
            current_data = self.model.get_item_by_id(
                config["table_name"], config["id_column"], selected_id)
            if not current_data:
                self.view.show_message("Error", "No se encontró el ítem seleccionado", "error")
                return

            # Obtener nombres de columnas
            column_names = [desc[0] for desc in self.model.cursor.description]
            # Mapear los valores actuales por nombre de columna
            current_data_dict = dict(zip(column_names, current_data))
            # Preparar campos y datos actuales en el orden de fields_config
            fields_config = self._prepare_fields_config(config["fields_config"])
            current_values = [current_data_dict.get(field[0]) for field in config["fields_config"]]

            # Crear diálogo en la View
            dialog, entries, entry_vars, save_btn = self.view.create_settings_dialog(
                f"Editar {config['tab_name']}", 
                fields_config, 
                current_values
            )

            # Configurar combobox de relaciones si aplica
            self._setup_relation_comboboxes(entries, config["fields_config"], current_values)

            def update_item():
                try:
                    values = self.view.get_form_values(fields_config, entry_vars)
                    # Convertir nombres de combobox a ids
                    for field_name, field_type, _ in fields_config:
                        if field_type == "combobox" and field_name in entries:
                            selected_name = values[field_name]
                            if hasattr(entries[field_name], "name_to_id"):
                                values[field_name] = entries[field_name].name_to_id.get(selected_name, None)
                    
                    # Validar campos requeridos
                    if not self._validate_required_fields(values, config["fields_config"]):
                        return
                    
                    # Preparar valores para la actualización
                    update_values = [values[field[0]] for field in fields_config]
                    
                    self.model.update_item(
                        config["table_name"], config["id_column"], selected_id,
                        [f[0] for f in fields_config], update_values
                    )
                    
                    self.view.show_message("Éxito", "Ítem actualizado correctamente", "info")
                    dialog.destroy()
                    self.refresh_tab(tab_key)
                    self._notify_product_controller()
                except Exception as e:
                    self.view.show_message("Error", str(e), "error")

            # Conectar el botón guardar - ESTO ES LO MÁS IMPORTANTE
            save_btn.configure(command=update_item)

        except Exception as e:
            self.view.show_message("Error", f"Error al cargar datos: {str(e)}", "error")

    def delete_item(self, tab_key):
        """Elimina/desactiva un ítem seleccionado"""
        selected_data = self.view.get_selected_item_data()
        if not selected_data:
            self.view.show_message(
                "Advertencia", "Por favor seleccione un ítem para eliminar", "warning")
            return

        config = self.tabs_config[tab_key]
        selected_id = selected_data[0]
        item_name = selected_data[1] if len(selected_data) > 1 else selected_id

        # DEBUG: Verificar estado actual antes de desactivar
        try:
            current_state = self.model.get_item_by_id(config["table_name"], config["id_column"], selected_id)
            if current_state:
                column_names = [desc[0] for desc in self.model.cursor.description]
                current_dict = dict(zip(column_names, current_state))
                print(f"DEBUG DELETE: Estado actual en BD - {current_dict}")
        except Exception as e:
            print(f"DEBUG DELETE: Error al obtener estado actual: {e}")

        if self.view.ask_confirmation(
            "Confirmar desactivación",
            f"¿Está seguro que desea desactivar '{item_name}'?\n\n"
            f"✅ El ítem ya no aparecerá en los combobox\n"
            f"📋 Se mantendrá en registros históricos\n"
            f"🔄 Podrá reactivarlo más tarde si es necesario"
        ):
            try:
                # Intentar eliminación lógica primero
                self.model.soft_delete_item(config["table_name"], config["id_column"], selected_id)
                
                # DEBUG: Verificar estado después de desactivar
                try:
                    new_state = self.model.get_item_by_id(config["table_name"], config["id_column"], selected_id)
                    if new_state:
                        column_names = [desc[0] for desc in self.model.cursor.description]
                        new_dict = dict(zip(column_names, new_state))
                        print(f"DEBUG DELETE: Estado después en BD - {new_dict}")
                        print(f"DEBUG DELETE: Valor 'activo' después: {new_dict.get('activo')}")
                except Exception as e:
                    print(f"DEBUG DELETE: Error al obtener nuevo estado: {e}")
                
                self.view.show_message("Éxito", "Ítem desactivado correctamente. Ya no aparecerá en los combobox.", "info")
                self.refresh_tab(tab_key)
                
                # Notificar al controlador de productos para refrescar combobox
                self._notify_product_controller()
                
            except Exception as e:
                self.view.show_message("Error", str(e), "error")
                
    def _notify_product_controller(self):
        """Notificar al controlador de productos para refrescar combobox"""
        try:
            # Buscar el controlador de productos en la app
            if hasattr(self.app, 'product_controller'):
                self.app.product_controller.refresh_comboboxes()
        except Exception as e:
            print(f"Error al notificar controlador de productos: {e}")
                    
    def activate_item(self, tab_key):
        """Reactiva un ítem previamente desactivado"""
        selected_data = self.view.get_selected_item_data()
        if not selected_data:
            self.view.show_message(
                "Advertencia", "Por favor seleccione un ítem para activar", "warning")
            return

        config = self.tabs_config[tab_key]
        selected_id = selected_data[0]
        item_name = selected_data[1] if len(selected_data) > 1 else selected_id

        # DEBUG: Verificar estado actual en BD
        try:
            current_state = self.model.get_item_by_id(config["table_name"], config["id_column"], selected_id)
            print(f"DEBUG: Estado actual en BD - {current_state}")
        except Exception as e:
            print(f"DEBUG: Error al obtener estado actual: {e}")

        if self.view.ask_confirmation(
            "Confirmar activación",
            f"¿Está seguro que desea activar '{item_name}'?\n\n"
            f"✅ El ítem volverá a aparecer en los combobox"
        ):
            try:
                success = self.model.activate_item(config["table_name"], config["id_column"], selected_id)
                print(f"DEBUG: Resultado activación: {success}")
                
                # DEBUG: Verificar estado después de la activación
                try:
                    new_state = self.model.get_item_by_id(config["table_name"], config["id_column"], selected_id)
                    print(f"DEBUG: Estado después en BD - {new_state}")
                except Exception as e:
                    print(f"DEBUG: Error al obtener nuevo estado: {e}")
                
                if success:
                    self.view.show_message("Éxito", "Ítem activado correctamente. Ahora aparecerá en los combobox.", "info")
                    self.refresh_tab(tab_key)
                    
                    # Notificar al controlador de productos para refrescar combobox
                    self._notify_product_controller()
                    
                else:
                    self.view.show_message("Error", "No se pudo activar el ítem", "error")
            except Exception as e:
                print(f"DEBUG: Error en activación: {e}")
                self.view.show_message("Error", str(e), "error")

    def _prepare_fields_config(self, fields_config):
        """Prepara la configuración de campos para el diálogo"""
        prepared_config = []
        for field_name, field_type, options in fields_config:
            if field_name.startswith("id_"):
                # Para campos de relación, usar combobox
                prepared_config.append((field_name, "combobox", []))
            else:
                prepared_config.append((field_name, field_type, options))
        return prepared_config

    def _setup_relation_comboboxes(self, entries, fields_config, current_values=None):
        """Configura los combobox para campos de relación"""
        for i, (field_name, field_type, _) in enumerate(fields_config):
            if field_name.startswith("id_") and field_name in entries:
                related_table = field_name[3:]  # Remueve "id_" del inicio
                try:
                    options = self.model.get_related_options(related_table)
                    
                    # Solo mostrar nombres en el combobox
                    options_dict = {str(row[1]): str(row[0]) for row in options}  # nombre: id
                    display_values = [row[1] for row in options]  # Solo nombres
                    
                    entries[field_name]["values"] = display_values
                    
                    # Establecer valor actual si existe
                    if current_values and i < len(current_values) and current_values[i]:
                        # Buscar el nombre correspondiente al id actual
                        current_id = str(current_values[i])
                        current_name = None
                        for row in options:
                            if str(row[0]) == current_id:
                                current_name = row[1]
                                break
                        if current_name:
                            entries[field_name].set(current_name)
                    
                    # Guardar el mapeo nombre->id para uso posterior
                    entries[field_name].name_to_id = options_dict
                    
                except Exception as e:
                    self.view.show_message(
                        "Error", f"Error al cargar {related_table}: {str(e)}", "error")

    def _validate_required_fields(self, values, fields_config):
        """Valida los campos requeridos"""
        optional_fields = ["contacto", "telefono", "email", "direccion", "activo"]
        
        for field_name, field_type, _ in fields_config:
            if (field_name not in optional_fields and 
                not values.get(field_name) and 
                values.get(field_name) not in [0, False]):
                self.view.show_message("Error", f"El campo {field_name} es requerido", "error")
                return False
        return True

    def close_connections(self):
        """Cierra las conexiones"""
        self.model.close_connection()