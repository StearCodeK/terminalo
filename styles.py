from tkinter import ttk
from tkinter.font import Font
import tkinter as tk
from helpers import center_window as helpers_center_window


def setup_styles(app):
    """Configura los estilos avanzados para la aplicación"""
    app.style = ttk.Style()
    app.style.theme_use('clam')

    # Fuentes personalizadas
    app.title_font = Font(family="Segoe UI", size=26, weight="bold")  # Aumentar tamaño
    app.subtitle_font = Font(family="Segoe UI", size=16)  # Aumentar tamaño
    app.menu_font = Font(family="Segoe UI", size=14)  # Aumentar tamaño
    app.button_font = Font(family="Segoe UI", size=12, weight="bold")  # Aumentar tamaño
    app.tree_font = Font(family="Segoe UI", size=11)  # Aumentar tamaño

    # OPCIONES GLOBALES DE FUENTES (Tk option database)
    app.option_add('*TCombobox*Listbox.font', app.tree_font)   # dropdown de ttk.Combobox
    app.option_add('*Combobox*Listbox.font', app.tree_font)    # respaldo
    app.option_add('*Label.font', app.menu_font)               # tk.Label por defecto
    app.option_add('*Message.font', app.menu_font)             # tk.Message por defecto

    # Configurar estilos de ttk
    app.style.configure('TLabel', font=app.menu_font)
    app.style.configure('TButton', font=app.button_font)
    app.style.configure('TEntry', font=app.tree_font)
    app.style.configure('TCombobox', font=app.tree_font)
    app.style.configure('Treeview', font=app.tree_font, rowheight=24)
    app.style.configure('Treeview.Heading', font=app.menu_font)

    app.style.configure("TButton",
                        font=app.button_font,
                        borderwidth=1,
                        relief="flat",
                        padding=6,
                        background=app.colors["primary"],
                        foreground="white")

    app.style.map("TButton",
                  background=[("active", app.colors["primary_light"]),
                              ("pressed", app.colors["primary"])],
                  relief=[("pressed", "sunken"), ("!pressed", "flat")])

    app.style.configure("TFrame", background=app.colors["background"])
    app.style.configure("TLabel", background=app.colors["background"],
                        foreground=app.colors["text"])
    app.style.configure("TEntry",
                        fieldbackground="white",
                        foreground=app.colors["text"])
    app.style.configure("Treeview",
                        background="white",
                        fieldbackground="white",
                        foreground=app.colors["text"],
                        font=app.tree_font,
                        rowheight=25,
                        borderwidth=0,
                        highlightthickness=0)
    app.style.map("Treeview", background=[
                  ("selected", app.colors["primary_light"])])

    app.style.configure("Treeview.Heading",
                        background=app.colors["primary"],
                        foreground="white",
                        font=app.button_font,
                        relief="flat")

    # Estilo para las pestañas
    app.style.configure("TNotebook",
                        background=app.colors["background"],
                        borderwidth=0)
    app.style.configure("TNotebook.Tab",
                        padding=[15, 5],
                        background=app.colors["background"],
                        foreground=app.colors["text_light"],
                        font=app.menu_font)
    app.style.map("TNotebook.Tab",
                  background=[("selected", app.colors["card"])],
                  foreground=[("selected", app.colors["primary"])])

    # Estilo para combobox
    app.style.configure("TCombobox",
                        fieldbackground="white",
                        background="white")
    
    app.style.configure("Accent.TButton",
                    font=app.button_font,
                    borderwidth=1,
                    relief="flat",
                    padding=(10, 6),
                    background=app.colors["primary"],
                    foreground="white")

    app.style.map("Accent.TButton",
                background=[("active", app.colors["primary_light"]),
                            ("pressed", app.colors["primary"])],
                relief=[("pressed", "sunken"), ("!pressed", "flat")])


def apply_common_styles(widget, app, widget_type="frame"):
    """Aplica estilos comunes a widgets tkinter normales"""
    bg_color = app.colors["background"]
    fg_color = app.colors["text"]

    if widget_type == "frame":
        widget.configure(bg=bg_color)
    elif widget_type == "label":
        widget.configure(bg=bg_color, fg=fg_color)
    elif widget_type == "entry":
        widget.configure(bg="white", fg=fg_color, insertbackground=fg_color)
    elif widget_type == "button":
        widget.configure(bg=app.colors["primary"], fg="white",
                         relief="flat", bd=1)


def create_filter_frame(parent, app, title=None):
    """Crea un frame de filtros estandarizado"""
    if title:
        frame = tk.LabelFrame(parent, text=title, bg=app.colors["background"],
                              fg=app.colors["text"], font=app.menu_font)
    else:
        frame = tk.Frame(parent, bg=app.colors["background"])
    return frame


def create_action_buttons(parent, app, actions):
    """Crea botones de acción estandarizados"""
    btn_frame = tk.Frame(parent, bg=app.colors["background"])
    buttons = []
    
    for text, command in actions:
        btn = ttk.Button(btn_frame, text=text, command=command)
        btn.pack(side="left", padx=2)
        buttons.append(btn)
        
    return btn_frame, buttons


def create_form_buttons(parent, app):
    """Crea botones de formulario estandarizados (Guardar/Cancelar)"""
    btn_frame = tk.Frame(parent, bg=app.colors["background"])

    save_btn = ttk.Button(btn_frame, text="Guardar", style="TButton")
    save_btn.pack(side="left", padx=10, ipadx=8, ipady=4)

    cancel_btn = ttk.Button(btn_frame, text="Cancelar", style="TButton")
    cancel_btn.pack(side="right", padx=10, ipadx=8, ipady=4)

    return btn_frame, save_btn, cancel_btn


def create_table(parent, app, columns, column_widths=None, height=15):
    """Crea una tabla estandarizada"""
    table_frame = tk.Frame(parent, bg=app.colors["background"])

    tree = ttk.Treeview(
        table_frame,
        columns=columns,
        show="headings",
        height=height
    )

    # Configurar columnas usando la función centralizada
    setup_treeview_columns(tree, columns, column_widths)

    # Scrollbar
    scrollbar = ttk.Scrollbar(
        table_frame,
        orient="vertical",
        command=tree.yview
    )
    tree.configure(yscrollcommand=scrollbar.set)

    tree.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    return table_frame, tree


def setup_treeview_columns(tree, columns, widths=None):
    """Configura las columnas de un Treeview"""
    default_widths = [100] * len(columns)
    widths = widths or default_widths
    
    for col, width in zip(columns, widths):
        tree.heading(col, text=col)
        tree.column(col, width=width, minwidth=50)


def create_main_container(parent, app, **kwargs):
    """Crea un contenedor principal"""
    return tk.Frame(parent, bg=app.colors["background"], **kwargs)


def create_section_frame(parent, app, **kwargs):
    """Crea un frame de sección"""
    return tk.Frame(parent, bg=app.colors["background"], **kwargs)


def create_form_frame(parent, app, text="", **kwargs):
    """Crea un frame de formulario con LabelFrame"""
    return tk.LabelFrame(
        parent,
        text=text,
        padx=20,
        pady=20,
        font=app.menu_font,
        bg=app.colors["background"],
        fg=app.colors["text"],
        **kwargs
    )


def create_modal_window(parent, app, title, size=None):
    """Crea una ventana modal estandarizada"""
    window = tk.Toplevel(parent)
    window.title(title)
    window.resizable(False, False)
    window.configure(bg=app.colors["background"])
    window.grab_set()  # Hacerla modal

    if size:
        window.geometry(size)

    return window