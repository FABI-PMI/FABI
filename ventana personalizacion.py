"""
Ventana de personalización con preview del juego en tiempo real.
Versión completa que integra todas las características originales + centrado de ventana.
"""
import tkinter as tk
from tkinter import messagebox
import math
import sys
import os

# Configuración de rutas para importaciones
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Intentar importar módulos del juego
try:
    from PaletaColores import generate_palette
    from VentanaPrincipal import VillageGame
    GAME_AVAILABLE = True
except ImportError as e:
    GAME_AVAILABLE = False


class ColorSelectorApp:
    """
    Aplicación principal de personalización del juego.
    Permite seleccionar color favorito, tema y música, con preview en tiempo real.
    """
    
    def __init__(self, root):
        """
        Inicializa la ventana de personalización.
        
        Args:
            root: Ventana principal de Tkinter
        """
        # Configuración de la ventana principal
        self.root = root
        self.root.title("Personalización - Sistema de Aldeas")
        
        # ==================== SISTEMA DE CENTRADO DE VENTANA ====================
        # Obtener el tamaño de la pantalla
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        
        # Definir tamaño de la ventana
        window_width = 1150
        window_height = 800
        
        # Calcular la posición para centrar la ventana
        position_x = int((screen_width - window_width) / 2)
        position_y = int((screen_height - window_height) / 2)
        
        # Establecer geometría y posición centrada
        self.root.geometry(f"{window_width}x{window_height}+{position_x}+{position_y}")
        self.root.resizable(False, False)
        
        # Color de fondo fijo para toda la aplicación
        self.color_fondo_fijo = '#8a1c32'
        self.root.configure(bg=self.color_fondo_fijo)
        
        # Contenedor principal
        main_container = tk.Frame(root, bg=self.color_fondo_fijo)
        main_container.pack(fill='both', expand=True)
        
        # Crear paneles izquierdo (controles) y derecho (preview)
        self._crear_panel_izquierdo(main_container)
        self._crear_panel_preview(main_container)
        
        # Aplicar tema inicial
        self.cambiar_tema()
        
        # Actualizar paleta del preview si está disponible
        if GAME_AVAILABLE and self.game_preview:
            self.update_game_palette()
    
    def _crear_panel_izquierdo(self, parent):
        """
        Crea el panel izquierdo con todos los controles de personalización.
        Incluye scroll para permitir navegación en pantallas pequeñas.
        
        Args:
            parent: Frame contenedor padre
        """
        # Frame principal del panel izquierdo con ancho fijo
        left_panel = tk.Frame(parent, bg=self.color_fondo_fijo, width=600)
        left_panel.pack(side='left', fill='both', expand=False, padx=10, pady=10)
        left_panel.pack_propagate(False)
        
        # Canvas con scrollbar para contenido desplazable
        left_canvas = tk.Canvas(left_panel, bg=self.color_fondo_fijo, highlightthickness=0)
        scrollbar = tk.Scrollbar(left_panel, orient="vertical", command=left_canvas.yview)
        self.scrollable_frame = tk.Frame(left_canvas, bg=self.color_fondo_fijo)
        
        # Configurar región de scroll según el tamaño del contenido
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: left_canvas.configure(scrollregion=left_canvas.bbox("all"))
        )
        
        # Vincular frame scrollable al canvas
        left_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        left_canvas.configure(yscrollcommand=scrollbar.set)
        
        # Empaquetar canvas y scrollbar
        left_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.main_canvas = left_canvas
        
        # Variables de control para las opciones de personalización
        self.color_favorito = tk.StringVar(value="#a4244d")  # Color inicial
        self.tema_var = tk.StringVar(value="claro")  # Tema inicial: claro
        self.cancion_var = tk.StringVar()  # Nombre de la canción
        
        # Detectar cambios en el tema para actualizar la interfaz
        self.tema_var.trace('w', self.cambiar_tema)
        
        # Crear todas las secciones de personalización
        self._crear_titulo()
        self._crear_seccion_color()
        self._crear_seccion_tema()
        self._crear_seccion_musica()
        
        # Espacio final para mejor visualización
        self.espacio_label = tk.Label(self.scrollable_frame, text="", bg=self.color_fondo_fijo)
        self.espacio_label.pack(pady=10)
    
    def _crear_titulo(self):
        """Crea el título principal de la ventana"""
        self.title_label = tk.Label(
            self.scrollable_frame, 
            text="PERSONALIZACIÓN", 
            font=("Arial", 28, "bold"), 
            bg=self.color_fondo_fijo, 
            fg='#ffffff'
        )
        self.title_label.pack(pady=20)
    
    def _crear_seccion_color(self):
        """
        Crea la sección de selección de color favorito.
        Incluye una rueda de color interactiva y display del color seleccionado.
        """
        # Frame contenedor de la sección de color
        self.color_frame = tk.LabelFrame(
            self.scrollable_frame, 
            text="Seleccione su color favorito",
            font=("Arial", 13, "bold"), 
            bg='#ffffff', 
            fg='#2c3e50', 
            padx=25, 
            pady=20, 
            relief="groove", 
            bd=3
        )
        self.color_frame.pack(pady=10, padx=30, fill='x')
        
        # Canvas para dibujar la rueda de colores
        self.canvas_color = tk.Canvas(
            self.color_frame, 
            width=220, 
            height=220, 
            bg='#ffffff', 
            highlightthickness=0
        )
        self.canvas_color.pack(pady=10)
        
        # Dibujar la rueda de color y vincular evento de clic
        self.dibujar_rueda_color()
        self.canvas_color.bind("<Button-1>", self.seleccionar_color_rueda)
        
        # Frame para mostrar información del color seleccionado
        self.color_info_frame = tk.Frame(self.color_frame, bg='#ffffff')
        self.color_info_frame.pack(pady=10)
        
        # Etiqueta "Color:"
        self.color_info_label = tk.Label(
            self.color_info_frame, 
            text="Color:", 
            font=("Arial", 10), 
            bg='#ffffff', 
            fg='#2c3e50'
        )
        self.color_info_label.pack(side='left', padx=5)
        
        # Display visual del color seleccionado
        self.color_display = tk.Canvas(
            self.color_info_frame, 
            width=60, 
            height=25, 
            bg=self.color_favorito.get(), 
            highlightthickness=2, 
            highlightbackground='#34495e'
        )
        self.color_display.pack(side='left', padx=5)
        
        # Etiqueta con el código hexadecimal del color
        self.color_label = tk.Label(
            self.color_info_frame, 
            text=self.color_favorito.get(), 
            font=("Arial", 10, "bold"), 
            bg='#ffffff', 
            fg='#2c3e50'
        )
        self.color_label.pack(side='left', padx=5)
    
    def _crear_seccion_tema(self):
        """
        Crea la sección de selección de tema (oscuro, claro, medio).
        Los radiobuttons permiten elegir el esquema de colores de la interfaz.
        """
        # Frame contenedor de la sección de tema
        self.tema_frame = tk.LabelFrame(
            self.scrollable_frame, 
            text="Tema", 
            font=("Arial", 13, "bold"),
            bg='#ffffff', 
            fg='#2c3e50', 
            padx=25, 
            pady=20,
            relief="groove", 
            bd=3
        )
        self.tema_frame.pack(pady=10, padx=30, fill='x')
        
        # Frame para organizar los radiobuttons horizontalmente
        self.opciones_frame = tk.Frame(self.tema_frame, bg='#ffffff')
        self.opciones_frame.pack()
        
        # Radiobutton para tema oscuro
        self.rb_oscuro = tk.Radiobutton(
            self.opciones_frame, 
            text="Oscuro", 
            variable=self.tema_var,
            value="oscuro", 
            bg='#ffffff', 
            fg='#2c3e50', 
            selectcolor='#bdc3c7', 
            font=("Arial", 11),
            activebackground='#ffffff'
        )
        self.rb_oscuro.grid(row=0, column=0, padx=25, pady=5)
        
        # Radiobutton para tema claro
        self.rb_claro = tk.Radiobutton(
            self.opciones_frame, 
            text="Claro", 
            variable=self.tema_var,
            value="claro", 
            bg='#ffffff', 
            fg='#2c3e50', 
            selectcolor='#bdc3c7', 
            font=("Arial", 11),
            activebackground='#ffffff'
        )
        self.rb_claro.grid(row=0, column=1, padx=25, pady=5)
        
        # Radiobutton para tema medio
        self.rb_medio = tk.Radiobutton(
            self.opciones_frame, 
            text="Término medio", 
            variable=self.tema_var,
            value="medio", 
            bg='#ffffff', 
            fg='#2c3e50', 
            selectcolor='#bdc3c7', 
            font=("Arial", 11),
            activebackground='#ffffff'
        )
        self.rb_medio.grid(row=0, column=2, padx=25, pady=5)
    
    def _crear_seccion_musica(self):
        """
        Crea la sección de música con entrada de texto y botones de acción.
        Incluye botones para buscar canción e iniciar el juego.
        """
        # Frame contenedor de la sección de música
        self.musica_frame = tk.LabelFrame(
            self.scrollable_frame, 
            text="Música", 
            font=("Arial", 13, "bold"),
            bg='#ffffff', 
            fg='#2c3e50', 
            padx=25, 
            pady=20,
            relief="groove", 
            bd=3
        )
        self.musica_frame.pack(pady=10, padx=30, fill='x')
        
        # Etiqueta para el campo de entrada
        self.musica_label = tk.Label(
            self.musica_frame, 
            text="Nombre de la canción:",
            font=("Arial", 11), 
            bg='#ffffff', 
            fg='#2c3e50'
        )
        self.musica_label.pack(anchor='w', pady=(5, 2))
        
        # Campo de entrada para el nombre de la canción
        self.entry_cancion = tk.Entry(
            self.musica_frame, 
            textvariable=self.cancion_var,
            font=("Arial", 12), 
            width=40, 
            relief="solid", 
            bd=2
        )
        self.entry_cancion.pack(pady=(0, 15), ipady=5)
        
        # Frame para contener los botones
        self.botones_frame = tk.Frame(self.musica_frame, bg='#ffffff')
        self.botones_frame.pack()
        
        # Botón para buscar canción
        self.btn_buscar = tk.Button(
            self.botones_frame, 
            text="Buscar Canción",
            bg='#9b59b6', 
            fg='white', 
            font=("Arial", 11, "bold"),
            padx=25, 
            pady=10, 
            command=self.buscar_cancion,
            cursor="hand2", 
            relief="raised", 
            bd=3, 
            width=18
        )
        self.btn_buscar.pack(pady=8)
        
        # Botón para iniciar el juego con la configuración actual
        self.btn_iniciar = tk.Button(
            self.botones_frame, 
            text="Iniciar Juego",
            bg='#e74c3c', 
            fg='white', 
            font=("Arial", 11, "bold"),
            padx=25, 
            pady=10, 
            command=self.iniciar_juego,
            cursor="hand2", 
            relief="raised", 
            bd=3, 
            width=18
        )
        self.btn_iniciar.pack(pady=8)

    
    def dibujar_rueda_color(self):
        """
        Dibuja una rueda de color interactiva tipo Paint.
        Crea 360 segmentos de colores dispuestos en círculo.
        """
        # Centro y radio de la rueda
        center_x, center_y = 110, 110
        radius = 90
        
        # Número de segmentos de color en la rueda
        num_segments = 360
        
        # Dibujar cada segmento de color
        for i in range(num_segments):
            # Calcular el ángulo del segmento actual
            angle = i * (360 / num_segments)
            hue = angle / 360
            
            # Convertir HSV a RGB para obtener el color
            rgb = self.hsv_to_rgb(hue, 1.0, 1.0)
            color = '#%02x%02x%02x' % rgb
            
            # Calcular coordenadas del inicio y fin del segmento
            angle_rad = math.radians(angle)
            angle_rad_next = math.radians(angle + (360 / num_segments))
            
            x1 = center_x + radius * math.cos(angle_rad)
            y1 = center_y + radius * math.sin(angle_rad)
            x2 = center_x + radius * math.cos(angle_rad_next)
            y2 = center_y + radius * math.sin(angle_rad_next)
            
            # Dibujar línea desde el centro hacia el borde
            self.canvas_color.create_line(
                center_x, center_y, x1, y1, 
                fill=color, width=3, tags="color_wheel"
            )
        
        # Dibujar círculo blanco en el centro para mejor visualización
        inner_radius = 30
        self.canvas_color.create_oval(
            center_x - inner_radius, center_y - inner_radius,
            center_x + inner_radius, center_y + inner_radius,
            fill='white', outline='#34495e', width=2
        )
    
    def hsv_to_rgb(self, h, s, v):
        """
        Convierte un color de HSV (Hue, Saturation, Value) a RGB.
        
        Args:
            h: Matiz (0.0 - 1.0)
            s: Saturación (0.0 - 1.0)
            v: Valor/Brillo (0.0 - 1.0)
        
        Returns:
            Tupla (R, G, B) con valores 0-255
        """
        # Caso especial: sin saturación = escala de grises
        if s == 0.0:
            return (int(v * 255), int(v * 255), int(v * 255))
        
        # Algoritmo de conversión HSV a RGB
        i = int(h * 6.0)
        f = (h * 6.0) - i
        p = v * (1.0 - s)
        q = v * (1.0 - s * f)
        t = v * (1.0 - s * (1.0 - f))
        i = i % 6
        
        # Retornar RGB según el sector del matiz
        if i == 0:
            return (int(v * 255), int(t * 255), int(p * 255))
        if i == 1:
            return (int(q * 255), int(v * 255), int(p * 255))
        if i == 2:
            return (int(p * 255), int(v * 255), int(t * 255))
        if i == 3:
            return (int(p * 255), int(q * 255), int(v * 255))
        if i == 4:
            return (int(t * 255), int(p * 255), int(v * 255))
        if i == 5:
            return (int(v * 255), int(p * 255), int(q * 255))
    
    def seleccionar_color_rueda(self, event):
        """
        Maneja el evento de clic en la rueda de colores.
        Calcula el color según la posición del clic.
        
        Args:
            event: Evento de clic del mouse con coordenadas x, y
        """
        # Centro de la rueda
        center_x, center_y = 110, 110
        
        # Calcular distancia del clic al centro
        dx = event.x - center_x
        dy = event.y - center_y
        distance = math.sqrt(dx**2 + dy**2)
        
        # Verificar si el clic está dentro del anillo de color (entre radio interno y externo)
        if 30 < distance < 90:
            # Calcular ángulo del clic
            angle = math.degrees(math.atan2(dy, dx))
            if angle < 0:
                angle += 360
            
            # Convertir ángulo a matiz y luego a RGB
            hue = angle / 360
            rgb = self.hsv_to_rgb(hue, 1.0, 1.0)
            color_hex = '#%02x%02x%02x' % rgb
            
            # Actualizar el color seleccionado
            self.color_favorito.set(color_hex)
            self.color_display.configure(bg=color_hex)
            self.color_label.configure(text=color_hex)
            
            # Actualizar el preview del juego si está disponible
            if GAME_AVAILABLE and self.game_preview:
                self.update_game_palette()
    
    def cambiar_tema(self, *args):
        """
        Cambia el esquema de colores de todos los frames según el tema seleccionado.
        Se ejecuta automáticamente cuando cambia la variable self.tema_var.
        
        Args:
            *args: Argumentos de la traza de Tkinter (no utilizados)
        """
        tema = self.tema_var.get()
        
        # Definir colores según el tema seleccionado
        if tema == "oscuro":
            bg_frames = '#2d2d2d'  # Fondo gris oscuro
            fg_texto = '#ffffff'   # Texto blanco
        elif tema == "claro":
            bg_frames = '#ffffff'  # Fondo blanco
            fg_texto = '#2c3e50'   # Texto gris oscuro
        else:  # tema == "medio"
            bg_frames = '#bdc3c7'  # Fondo gris medio
            fg_texto = '#2c3e50'   # Texto gris oscuro
        
        # Aplicar colores a todos los frames y widgets
        self.color_frame.configure(bg=bg_frames, fg=fg_texto)
        self.tema_frame.configure(bg=bg_frames, fg=fg_texto)
        self.musica_frame.configure(bg=bg_frames, fg=fg_texto)
        self.canvas_color.configure(bg=bg_frames)
        self.color_info_frame.configure(bg=bg_frames)
        self.color_info_label.configure(bg=bg_frames, fg=fg_texto)
        self.color_label.configure(bg=bg_frames, fg=fg_texto)
        self.musica_label.configure(bg=bg_frames, fg=fg_texto)
        self.opciones_frame.configure(bg=bg_frames)
        self.rb_oscuro.configure(bg=bg_frames, fg=fg_texto, activebackground=bg_frames)
        self.rb_claro.configure(bg=bg_frames, fg=fg_texto, activebackground=bg_frames)
        self.rb_medio.configure(bg=bg_frames, fg=fg_texto, activebackground=bg_frames)
        self.botones_frame.configure(bg=bg_frames)
        
        # Actualizar paleta del preview del juego
        if GAME_AVAILABLE and self.game_preview:
            self.update_game_palette()
    
    def buscar_cancion(self):
        """
        Maneja la búsqueda de canción.
        Valida que se haya ingresado un nombre y muestra mensaje de confirmación.
        """
        cancion = self.cancion_var.get().strip()
        
        # Validar que se haya ingresado un nombre
        if not cancion:
            messagebox.showwarning("Advertencia", "Por favor ingresa el nombre de una canción")
            return
        
        # Mostrar mensaje de confirmación (aquí se implementaría la búsqueda real)
        messagebox.showinfo("Buscar Canción", f"Buscando: {cancion}")
    
    def iniciar_juego(self):
        """
        Inicia el juego en una ventana independiente con la configuración actual.
        Crea una nueva ventana con el juego usando la paleta personalizada.
        """
        # Verificar que los módulos del juego estén disponibles
        if not GAME_AVAILABLE:
            messagebox.showerror(
                "Error", 
                "Los módulos del juego no están disponibles.\n\n"
                "Asegúrate de tener los archivos:\n"
                "- PaletaColores.py\n"
                "- VentanaPrincipal.py"
            )
            return
        
        try:
            # Obtener configuración actual
            color = self.color_favorito.get()
            tema = self.tema_var.get()
            cancion = self.cancion_var.get().strip()
            
            # Generar paleta de colores basada en la configuración
            palette = generate_palette(color, tema)
            
            # Crear ventana independiente para el juego
            game_window = tk.Toplevel(self.root)
            game_window.title("Sistema de Aldeas - Juego")
            game_window.geometry("500x700")
            game_window.resizable(False, False)
            
            # Crear instancia del juego con la paleta personalizada
            game_frame = VillageGame(game_window, width=500, height=700, initial_palette=palette)
            game_frame.pack()
            
            # Preparar mensaje de confirmación
            mensaje = f"Juego iniciado con:\n\nColor: {color}\nTema: {tema}"
            if cancion:
                mensaje += f"\nMúsica: {cancion}"
            
            # Mostrar mensaje de confirmación
            messagebox.showinfo("Juego Iniciado", mensaje)
            
        except Exception as e:
            # Manejar errores al iniciar el juego
            messagebox.showerror("Error", f"No se pudo iniciar el juego:\n{e}")
    
    # ==================== FUNCIONES DE PREVIEW ====================
    
    def _crear_panel_preview(self, parent):
        """
        Crea el panel derecho con el preview del juego en tiempo real.
        Muestra una vista previa del juego que se actualiza automáticamente.
        
        Args:
            parent: Frame contenedor padre
        """
        # Si los módulos del juego no están disponibles, no crear preview
        if not GAME_AVAILABLE:
            self.game_preview = None
            return
        
        # Frame contenedor del preview
        right_panel = tk.Frame(parent, bg='#2c3e50', relief='sunken', bd=3)
        right_panel.pack(side='right', fill='both', expand=True, padx=(0, 10), pady=10)
        
        # Título del panel de preview
        preview_title = tk.Label(
            right_panel, 
            text="PREVIEW DEL JUEGO", 
            font=("Arial", 14, "bold"), 
            bg='#2c3e50', 
            fg='white'
        )
        preview_title.pack(pady=10)
        
        try:
            # Crear instancia del juego para preview
            self.game_preview = VillageGame(right_panel, width=500, height=700)
            self.game_preview.pack(pady=5)
            
        except Exception as e:
            # Si hay error, mostrar mensaje y establecer preview como None
            error_label = tk.Label(
                right_panel, 
                text=f"Error al crear preview:\n{e}",
                bg='#2c3e50', 
                fg='red', 
                font=("Arial", 10)
            )
            error_label.pack(pady=20)
            self.game_preview = None
    
    def update_game_palette(self):
        """
        Actualiza la paleta de colores del preview del juego.
        Se llama automáticamente cuando cambia el color o el tema.
        """
        # Verificar que el preview esté disponible
        if not GAME_AVAILABLE or not self.game_preview:
            return
        
        try:
            # Obtener configuración actual
            color_base = self.color_favorito.get()
            tema = self.tema_var.get()
            
            # Generar nueva paleta y aplicarla al preview
            palette = generate_palette(color_base, tema)
            self.game_preview.apply_new_palette(palette)
            
        except Exception as e:
            # Manejo silencioso de errores (sin imprimir en consola)
            pass


# ==================== PUNTO DE ENTRADA ====================

if __name__ == "__main__":
    # Crear ventana principal e iniciar aplicación
    root = tk.Tk()
    app = ColorSelectorApp(root)
    root.mainloop()