import tkinter as tk
from tkinter import messagebox
import math

class ColorSelectorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Título")
        
        # Obtener el tamaño de la pantalla
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        
        # Calcular el tamaño de la ventana (70% de la pantalla, con límites)
        window_width = min(max(600, int(screen_width * 0.5)), 800)
        window_height = min(max(750, int(screen_height * 0.8)), 900)
        
        # Calcular la posición para centrar la ventana
        position_x = int((screen_width - window_width) / 2)
        position_y = int((screen_height - window_height) / 2)
        
        # Establecer geometría y posición
        self.root.geometry(f"{window_width}x{window_height}+{position_x}+{position_y}")
        self.root.resizable(True, True)  # Permitir redimensionar
        self.root.configure(bg='#a4244d')
        
        # Hacer la ventana scrolleable
        main_canvas = tk.Canvas(root, bg='#a4244d', highlightthickness=0)
        scrollbar = tk.Scrollbar(root, orient="vertical", command=main_canvas.yview)
        self.scrollable_frame = tk.Frame(main_canvas, bg='#a4244d')
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        )
        
        main_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        main_canvas.configure(yscrollcommand=scrollbar.set)
        
        main_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Guardar referencia al canvas principal
        self.main_canvas = main_canvas
        
        # Variables
        self.color_favorito = tk.StringVar(value="#a4244d")
        self.tema_var = tk.StringVar(value="claro")
        self.cancion_var = tk.StringVar()
        
        # Rastrear cuando cambie el tema
        self.tema_var.trace('w', self.cambiar_tema)
        
        # Container central para los elementos
        self.center_container = tk.Frame(self.scrollable_frame, bg='#a4244d')
        self.center_container.pack(expand=True, fill='both', padx=20, pady=20)
        
        # Título principal
        self.title_label = tk.Label(self.center_container, text="Título", font=("Arial", 28, "bold"), 
                              bg='#a4244d', fg='#2c3e50')
        self.title_label.pack(pady=(10, 30))
        
        # ==================== SELECCIONE SU COLOR FAVORITO ====================
        self.color_frame = tk.LabelFrame(self.center_container, text="Seleccione su color favorito",
                                   font=("Arial", 13, "bold"), bg='#ffffff', 
                                   fg='#2c3e50', padx=25, pady=20, relief="groove", bd=3)
        self.color_frame.pack(pady=15, padx=40, anchor='center')
        
        # Rueda de color estilo Paint
        self.canvas_color = tk.Canvas(self.color_frame, width=220, height=220, 
                                     bg='#ffffff', highlightthickness=0)
        self.canvas_color.pack(pady=10)
        
        self.dibujar_rueda_color()
        self.canvas_color.bind("<Button-1>", self.seleccionar_color_rueda)
        
        # Indicador de color seleccionado
        self.color_info_frame = tk.Frame(self.color_frame, bg='#ffffff')
        self.color_info_frame.pack(pady=10)
        
        self.color_info_label = tk.Label(self.color_info_frame, text="Color:", 
                font=("Arial", 10), bg='#ffffff', fg='#2c3e50')
        self.color_info_label.pack(side='left', padx=5)
        
        self.color_display = tk.Canvas(self.color_info_frame, width=60, height=25, 
                                      bg=self.color_favorito.get(), 
                                      highlightthickness=2, highlightbackground='#34495e')
        self.color_display.pack(side='left', padx=5)
        
        self.color_label = tk.Label(self.color_info_frame, text=self.color_favorito.get(), 
                                   font=("Arial", 10, "bold"), bg='#ffffff', fg='#2c3e50')
        self.color_label.pack(side='left', padx=5)
        
        # ==================== TEMA ====================
        self.tema_frame = tk.LabelFrame(self.center_container, text="Tema", font=("Arial", 13, "bold"),
                                  bg='#ffffff', fg='#2c3e50', padx=25, pady=20,
                                  relief="groove", bd=3)
        self.tema_frame.pack(pady=15, padx=40, anchor='center')
        
        # Radio buttons para tema
        self.opciones_frame = tk.Frame(self.tema_frame, bg='#ffffff')
        self.opciones_frame.pack()
        
        self.rb_oscuro = tk.Radiobutton(self.opciones_frame, text="Oscuro", variable=self.tema_var,
                      value="oscuro", bg='#ffffff', fg='#2c3e50', 
                      selectcolor='#bdc3c7', font=("Arial", 11),
                      activebackground='#ffffff')
        self.rb_oscuro.grid(row=0, column=0, padx=25, pady=5)
        
        self.rb_claro = tk.Radiobutton(self.opciones_frame, text="Claro", variable=self.tema_var,
                      value="claro", bg='#ffffff', fg='#2c3e50', 
                      selectcolor='#bdc3c7', font=("Arial", 11),
                      activebackground='#ffffff')
        self.rb_claro.grid(row=0, column=1, padx=25, pady=5)
        
        self.rb_medio = tk.Radiobutton(self.opciones_frame, text="Término medio", variable=self.tema_var,
                      value="medio", bg='#ffffff', fg='#2c3e50', 
                      selectcolor='#bdc3c7', font=("Arial", 11),
                      activebackground='#ffffff')
        self.rb_medio.grid(row=0, column=2, padx=25, pady=5)
        
        # ==================== MÚSICA ====================
        self.musica_frame = tk.LabelFrame(self.center_container, text="Música", font=("Arial", 13, "bold"),
                                    bg='#ffffff', fg='#2c3e50', padx=25, pady=20,
                                    relief="groove", bd=3)
        self.musica_frame.pack(pady=15, padx=40, anchor='center')
        
        # Etiqueta y campo de entrada
        self.musica_label = tk.Label(self.musica_frame, text="Nombre de la canción:",
                font=("Arial", 11), bg='#ffffff', fg='#2c3e50')
        self.musica_label.pack(anchor='w', pady=(5, 2))
        
        self.entry_cancion = tk.Entry(self.musica_frame, textvariable=self.cancion_var,
                                     font=("Arial", 12), width=40, relief="solid", bd=2)
        self.entry_cancion.pack(pady=(0, 15), ipady=5)
        
        # Botones en un frame
        self.botones_frame = tk.Frame(self.musica_frame, bg='#ffffff')
        self.botones_frame.pack()
        
        # Botón Buscar Canción
        self.btn_buscar = tk.Button(self.botones_frame, text="Buscar Canción",
                              bg='#9b59b6', fg='white', font=("Arial", 11, "bold"),
                              padx=25, pady=10, command=self.buscar_cancion,
                              cursor="hand2", relief="raised", bd=3, width=18)
        self.btn_buscar.pack(pady=8)
        
        # Botón Iniciar
        self.btn_iniciar = tk.Button(self.botones_frame, text="Iniciar",
                               bg='#e74c3c', fg='white', font=("Arial", 11, "bold"),
                               padx=25, pady=10, command=self.iniciar_musica,
                               cursor="hand2", relief="raised", bd=3, width=18)
        self.btn_iniciar.pack(pady=8)
        
        # Espacio final
        self.espacio_label = tk.Label(self.center_container, text="", bg='#a4244d')
        self.espacio_label.pack(pady=20)
        
        # Aplicar el tema inicial
        self.cambiar_tema()
    
    def dibujar_rueda_color(self):
        """Dibuja una rueda de color tipo Paint"""
        center_x, center_y = 110, 110
        radius = 90
        
        # Dibujar segmentos de color
        num_segments = 360
        for i in range(num_segments):
            angle = i * (360 / num_segments)
            # Convertir HSV a RGB
            hue = angle / 360
            rgb = self.hsv_to_rgb(hue, 1.0, 1.0)
            color = '#%02x%02x%02x' % rgb
            
            # Calcular posiciones para el segmento
            angle_rad = math.radians(angle)
            angle_rad_next = math.radians(angle + (360 / num_segments))
            
            x1 = center_x + radius * math.cos(angle_rad)
            y1 = center_y + radius * math.sin(angle_rad)
            x2 = center_x + radius * math.cos(angle_rad_next)
            y2 = center_y + radius * math.sin(angle_rad_next)
            
            # Dibujar línea de color
            self.canvas_color.create_line(center_x, center_y, x1, y1, 
                                         fill=color, width=3, tags="color_wheel")
        
        # Círculo blanco en el centro
        inner_radius = 30
        self.canvas_color.create_oval(center_x - inner_radius, center_y - inner_radius,
                                     center_x + inner_radius, center_y + inner_radius,
                                     fill='white', outline='#34495e', width=2)
    
    def hsv_to_rgb(self, h, s, v):
        """Convierte HSV a RGB"""
        if s == 0.0:
            return (int(v * 255), int(v * 255), int(v * 255))
        
        i = int(h * 6.0)
        f = (h * 6.0) - i
        p = v * (1.0 - s)
        q = v * (1.0 - s * f)
        t = v * (1.0 - s * (1.0 - f))
        i = i % 6
        
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
        """Selecciona el color donde el usuario hace clic en la rueda"""
        center_x, center_y = 110, 110
        dx = event.x - center_x
        dy = event.y - center_y
        
        # Calcular distancia del centro
        distance = math.sqrt(dx**2 + dy**2)
        
        # Solo seleccionar si está dentro del radio exterior y fuera del círculo interno
        if 30 < distance < 90:
            # Calcular ángulo
            angle = math.degrees(math.atan2(dy, dx))
            if angle < 0:
                angle += 360
            
            # Convertir ángulo a color
            hue = angle / 360
            rgb = self.hsv_to_rgb(hue, 1.0, 1.0)
            color_hex = '#%02x%02x%02x' % rgb
            
            # Actualizar color
            self.color_favorito.set(color_hex)
            self.color_display.configure(bg=color_hex)
            self.color_label.configure(text=color_hex)
            
            # Cambiar el fondo de la ventana completa
            self.root.configure(bg=color_hex)
            self.main_canvas.configure(bg=color_hex)
            self.scrollable_frame.configure(bg=color_hex)
            self.center_container.configure(bg=color_hex)
            
            # Cambiar el fondo del título al mismo color
            self.title_label.configure(bg=color_hex)
            self.espacio_label.configure(bg=color_hex)
            
            # Aplicar el tema actual para ajustar el color del texto del título
            self.cambiar_tema()
    
    def cambiar_tema(self, *args):
        """Cambia el esquema de colores de los frames según el tema seleccionado"""
        tema = self.tema_var.get()
        
        if tema == "oscuro":
            # Tema oscuro - Frames negros, texto blanco
            bg_frames = '#2d2d2d'
            fg_texto = '#ffffff'
            fg_titulo = '#ffffff'
            
        elif tema == "claro":
            # Tema claro - Frames blancos, texto negro
            bg_frames = '#ffffff'
            fg_texto = '#2c3e50'
            fg_titulo = '#2c3e50'
            
        else:  # medio
            # Tema término medio - Frames grises intermedios
            bg_frames = '#bdc3c7'
            fg_texto = '#2c3e50'
            fg_titulo = '#1a1a1a'
        
        # Aplicar color al texto del título
        self.title_label.configure(fg=fg_titulo)
        
        # Aplicar SOLO a los frames
        self.color_frame.configure(bg=bg_frames, fg=fg_texto)
        self.tema_frame.configure(bg=bg_frames, fg=fg_texto)
        self.musica_frame.configure(bg=bg_frames, fg=fg_texto)
        
        # Aplicar al canvas de color
        self.canvas_color.configure(bg=bg_frames)
        
        # Aplicar a frames internos
        self.color_info_frame.configure(bg=bg_frames)
        
        # Aplicar a labels dentro de los frames
        self.color_info_label.configure(bg=bg_frames, fg=fg_texto)
        self.color_label.configure(bg=bg_frames, fg=fg_texto)
        self.musica_label.configure(bg=bg_frames, fg=fg_texto)
        
        # Aplicar a los radio buttons
        self.opciones_frame.configure(bg=bg_frames)
        self.rb_oscuro.configure(bg=bg_frames, fg=fg_texto, activebackground=bg_frames)
        self.rb_claro.configure(bg=bg_frames, fg=fg_texto, activebackground=bg_frames)
        self.rb_medio.configure(bg=bg_frames, fg=fg_texto, activebackground=bg_frames)
        
        # Aplicar al frame de botones
        self.botones_frame.configure(bg=bg_frames)
    
    def buscar_cancion(self):
        cancion = self.cancion_var.get().strip()
        if not cancion:
            messagebox.showwarning("Advertencia", "Por favor ingresa el nombre de una canción")
            return
        
        messagebox.showinfo("Buscar Canción", f"Buscando: {cancion}")
    
    def iniciar_musica(self):
        """Función placeholder para el botón Iniciar - se implementará más adelante"""
        pass

if __name__ == "__main__":
    root = tk.Tk()
    app = ColorSelectorApp(root)
    root.mainloop()