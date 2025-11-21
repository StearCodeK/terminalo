import tkinter as tk
from tkinter import ttk, messagebox
from styles import setup_styles
from helpers import clear_frame
from menu.dashboard import show_dashboard
from menu.productos import show_inventory
from menu.pedidos import show_requests
from menu.compras import show_purchases
from menu.movimientos import show_movements
from models.notificaciones import NotificationManager
from menu.ajustes import show_settings

# Importar la nueva estructura MVC del login
from views.login_view import LoginView
from controllers.login_controller import LoginController


class ModernInventoryApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.iconbitmap("usm.ico")
        self.title("Sistema de Inventario - InventarioUSM")
        self.geometry("1280x720")
        self.minsize(1024, 600)

        # Configuración de colores centralizada
        self._setup_colors()
        
        # Configurar estilos
        setup_styles(self)

        # Vincular eventos de minimizar/restaurar
        self.bind("<Unmap>", self.toggle_window_state)
        self.bind("<Map>", self.toggle_window_state)

        # Configurar grid principal
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Inicializar componentes
        self._initialize_components()

        # Mostrar login primero
        self.show_login()
    
    def _setup_colors(self):
        """Configuración centralizada de colores"""
        self.colors = {
            "primary": "#4f46e5",
            "primary_light": "#6366f1",
            "secondary": "#10b981",
            "background": "#f9fafb",
            "card": "#ffffff",
            "text": "#374151",
            "text_light": "#6b7280",
            "border": "#e5e7eb",
            "hover": "#f3f4f6"
        }

    def _initialize_components(self):
        """Inicializa todos los componentes principales"""
        self.login_controller = LoginController(self)
        self.login_view = LoginView(self, self.login_controller)
        self.notification_manager = NotificationManager(self)

    def toggle_window_state(self, event=None):
        """Centra la ventana cuando se restaura desde minimizado"""
        self.after(100, self._delayed_center)

    def _delayed_center(self):
        """Centra la ventana después de un pequeño delay"""
        if self.state() == 'normal':
            self.center_window()

    def center_window(self):
        """Centra la ventana principal en la pantalla"""
        self.update_idletasks()
        w = self.winfo_width()
        h = self.winfo_height()
        ws = self.winfo_screenwidth()
        hs = self.winfo_screenheight()
        x = (ws // 2) - (w // 2)
        y = (hs // 4) - (h // 4)
        self.geometry(f'{w}x{h}+{x}+{y}')

    def show_login(self):
        """Muestra la pantalla de login usando la nueva estructura MVC"""
        self._clear_all_widgets()
        self.login_view.show_login()

    def show_main_content(self):
        """Muestra la interfaz principal después del login exitoso"""
        # Restablece el tamaño mínimo y la geometría para la ventana principal
        self.minsize(1024, 600)
        self.geometry("1280x720")
        self.state('zoomed')
        
        self._clear_all_widgets()
        self._create_main_interface()

        # Verificar notificaciones
        self.notification_manager.check_low_stock()
        self.after(300000, self.notification_manager.check_low_stock)

        # Mostrar dashboard por defecto
        show_dashboard(self)

    def _clear_all_widgets(self):
        """Limpia todos los widgets de la ventana principal"""
        for widget in self.winfo_children():
            widget.destroy()

    def _create_main_interface(self):
        """Crea la interfaz principal completa"""
        self.create_header()
        self.create_main_menu()
        self.create_status_bar()

    def create_header(self):
        """Crea la barra superior con logo, búsqueda y menú de usuario"""
        header_frame = tk.Frame(self, bg="white", height=70, padx=20)
        header_frame.grid(row=0, column=0, sticky="ew")
        header_frame.grid_columnconfigure(1, weight=1)

        # Logo
        self._create_logo(header_frame)
        
        # Elementos del lado derecho
        self._create_header_right_elements(header_frame)

    def _create_logo(self, parent):
        """Crea el logo en el header"""
        logo_frame = tk.Frame(parent, bg="white")
        logo_frame.grid(row=0, column=0, sticky="w")

        tk.Label(logo_frame, text="📦", font=("Segoe UI", 24),
                 bg="white", fg=self.colors["primary"]).pack(side="left")
        tk.Label(logo_frame, text="InventarioUSM", font=self.title_font,
                 bg="white", fg=self.colors["text"]).pack(side="left", padx=10)

    def _create_header_right_elements(self, parent):
        """Crea los elementos del lado derecho del header"""
        right_frame = tk.Frame(parent, bg="white")
        right_frame.grid(row=0, column=2, sticky="e")

        # Notificaciones
        self._create_notification_bell(right_frame)
        
        # Separador
        tk.Frame(right_frame, bg=self.colors["border"], width=1, height=30).pack(
            side="left", padx=5)
            
        # Menú de usuario
        self._create_user_menu(right_frame)

    def _create_notification_bell(self, parent):
        """Crea la campana de notificaciones"""
        self.bell_icon = tk.Label(parent, text="🔔", font=("Segoe UI", 16),
                                  bg="white", cursor="hand2")
        self.bell_icon.pack(side="left", padx=10)
        self.bell_icon.bind(
            "<Button-1>", lambda e: self.notification_manager.show_notifications())

    def _create_user_menu(self, parent):
        """Crea el menú de usuario"""
        user_frame = tk.Frame(parent, bg="white")
        user_frame.pack(side="left")

        # Avatar
        self._create_user_avatar(user_frame)
        
        # Menú desplegable
        self._create_user_dropdown(user_frame)

    def _create_user_avatar(self, parent):
        """Crea el avatar del usuario"""
        avatar = tk.Canvas(parent, width=36, height=36, bg=self.colors["primary"],
                           bd=0, highlightthickness=0)
        avatar.create_oval(2, 2, 34, 34, fill=self.colors["primary_light"])

        user_initial = self._get_user_initial()
        avatar.create_text(18, 18, text=user_initial, fill="white",
                           font=("Segoe UI", 12, "bold"))
        avatar.pack(side="left", padx=5)

    def _create_user_dropdown(self, parent):
        """Crea el menú desplegable del usuario"""
        user_name = self._get_user_display_name()
        
        user_menu = tk.Menubutton(parent, text=user_name,
                                  font=self.menu_font, bg="white",
                                  fg=self.colors["text"], bd=0,
                                  activebackground=self.colors["hover"])
        user_menu.pack(side="left")

        user_dropdown = tk.Menu(user_menu, tearoff=0,
                                font=self.menu_font,
                                bg="white", fg=self.colors["text"],
                                activebackground=self.colors["hover"],
                                activeforeground=self.colors["primary"])
        user_dropdown.add_command(
            label="👤 Mi perfil", command=self.show_profile)
        user_dropdown.add_separator()
        user_dropdown.add_command(label="🚪 Cerrar sesión",
                                  command=self.logout)
        user_menu.config(menu=user_dropdown)

    def _get_user_initial(self):
        """Obtiene la inicial del usuario actual"""
        if hasattr(self, 'current_user') and self.current_user:
            return self.current_user.nombre_completo[0].upper()
        return "A"

    def _get_user_display_name(self):
        """Obtiene el nombre para mostrar del usuario"""
        if hasattr(self, 'current_user') and self.current_user:
            return self.current_user.nombre_completo.split()[0]
        return "Admin"

    def create_main_menu(self):
        """Crea el menú lateral y el área de contenido principal"""
        main_frame = tk.Frame(self, bg=self.colors["background"])
        main_frame.grid(row=1, column=0, sticky="nsew")
        main_frame.grid_columnconfigure(1, weight=1)
        main_frame.grid_rowconfigure(0, weight=1)

        # Menú lateral
        sidebar = self._create_sidebar(main_frame)
        
        # Área de contenido
        self.content_frame = tk.Frame(main_frame, bg=self.colors["background"])
        self.content_frame.grid(
            row=0, column=1, sticky="nsew", padx=10, pady=10)

    def _create_sidebar(self, parent):
        """Crea la barra lateral de menú"""
        sidebar = tk.Frame(parent, bg="white", width=240, bd=0,
                           highlightthickness=0)
        sidebar.grid(row=0, column=0, sticky="ns")
        sidebar.grid_propagate(False)

        # Espaciador
        tk.Frame(sidebar, height=20, bg="white").pack()

        # Items del menú
        self._create_menu_items(sidebar)
        return sidebar

    def _create_menu_items(self, sidebar):
        """Crea los items del menú lateral"""
        menu_items = [
            ("📊 Dashboard", show_dashboard),
            ("📦 Inventario", show_inventory),
            ("📝 Solicitudes", show_requests),
            ("🛒 Reposiciones", show_purchases),
            ("🔄 Movimientos", show_movements),
            ("⚙️ Ajustes", show_settings)
        ]

        for text, command in menu_items:
            btn = self._create_menu_button(sidebar, text, command)
            self._add_button_hover_effect(btn)

    def _create_menu_button(self, parent, text, command):
        """Crea un botón del menú"""
        btn = tk.Button(parent, text=text, font=self.menu_font,
                        bg="white", fg=self.colors["text"], bd=0,
                        activebackground=self.colors["hover"],
                        activeforeground=self.colors["primary"],
                        command=lambda cmd=command: cmd(self),
                        padx=20, anchor="w")
        btn.pack(fill="x", ipady=10)
        return btn

    def _add_button_hover_effect(self, button):
        """Añade efecto hover a un botón"""
        button.bind("<Enter>", lambda e, b=button: b.config(
            bg=self.colors["hover"]))
        button.bind("<Leave>", lambda e, b=button: b.config(bg="white"))

    def create_status_bar(self):
        """Crea la barra de estado inferior"""
        status_frame = tk.Frame(self, bg="white", height=30)
        status_frame.grid(row=2, column=0, sticky="ew")

        tk.Label(status_frame, text="Sistema de Inventario v2.0",
                 bg="white", fg=self.colors["text_light"], padx=10).pack(side="left")

        tk.Label(status_frame, text="© 2025 Universidad - Todos los derechos reservados",
                 bg="white", fg=self.colors["text_light"], padx=10).pack(side="right")

    def show_profile(self):
        """Muestra el perfil del usuario"""
        clear_frame(self.content_frame)
        title = tk.Label(self.content_frame, text="Mi Perfil",
                         font=self.title_font, bg=self.colors["background"])
        title.pack(pady=20)

        if hasattr(self, 'current_user') and self.current_user:
            user_info = self._format_user_info()
            tk.Label(self.content_frame, text=user_info,
                     bg=self.colors["background"], justify="left").pack()
        else:
            tk.Label(self.content_frame, text="No hay información del usuario disponible",
                     bg=self.colors["background"]).pack()

    def _format_user_info(self):
        """Formatea la información del usuario para mostrar"""
        return f"""
        Nombre: {self.current_user.nombre_completo}
        Usuario: {self.current_user.usuario}
        Email: {self.current_user.email}
        Rol: {self.current_user.rol}
                """

    def logout(self):
        """Cierra la sesión del usuario usando el controlador"""
        self.login_controller.logout()
        self.destroy()