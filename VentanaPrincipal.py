"""
Sistema visual del juego Avatars vs Rooks 
Este módulo implementa la interfaz gráfica usando Tkinter.
Con soporte para torres, presupuesto y frecuencias de disparo.
"""
import tkinter as tk
from tkinter import Canvas, messagebox
import random
import time
import threading
from RooksClass import RookArena, RookRoca, RookAgua, RookFuego, GestorRooks


class ColorPalette:
    """
    Recibe una paleta de colores completa generada externamente.
    Este módulo NO genera colores, solo los organiza y distribuye.
    """
    def __init__(self, palette_dict=None):
        if palette_dict is None:
            palette_dict = self.get_default_palette()
        
        self.load_palette(palette_dict)
    
    def load_palette(self, palette_dict):
        """Carga una paleta de colores desde un diccionario"""
        # Zona segura
        self.safe_zone_bg = self.rgb_to_hex(palette_dict.get('safe_zone_bg', (240, 248, 255)))
        self.safe_houses = self.rgb_to_hex(palette_dict.get('safe_houses', (139, 69, 19)))
        self.safe_houses_roof = self.rgb_to_hex(palette_dict.get('safe_houses_roof', (178, 34, 34)))
        self.safe_houses_door = self.rgb_to_hex(palette_dict.get('safe_houses_door', (90, 45, 12)))
        self.safe_houses_window = self.rgb_to_hex(palette_dict.get('safe_houses_window', (255, 255, 200)))
        
        # Zona invasora
        self.invader_zone_bg = self.rgb_to_hex(palette_dict.get('invader_zone_bg', (30, 30, 35)))
        self.invader_houses = self.rgb_to_hex(palette_dict.get('invader_houses', (60, 60, 60)))
        self.invader_houses_roof = self.rgb_to_hex(palette_dict.get('invader_houses_roof', (120, 20, 20)))
        self.invader_houses_door = self.rgb_to_hex(palette_dict.get('invader_houses_door', (40, 40, 40)))
        self.invader_houses_window = self.rgb_to_hex(palette_dict.get('invader_houses_window', (150, 100, 100)))
        
        # Cuadrícula - Colores de zacate
        self.grid_bg_light = self.rgb_to_hex(palette_dict.get('grid_bg_light', (180, 200, 120)))
        self.grid_bg_dark = self.rgb_to_hex(palette_dict.get('grid_bg_dark', (140, 170, 90)))
        self.grid_lines = self.rgb_to_hex(palette_dict.get('grid_lines', (100, 130, 60)))
        self.grid_border = self.rgb_to_hex(palette_dict.get('grid_border', (80, 100, 40)))
        
        # Elementos UI
        self.user_icon_bg = self.rgb_to_hex(palette_dict.get('user_icon_bg', (255, 255, 255)))
        self.user_icon_border = self.rgb_to_hex(palette_dict.get('user_icon_border', (139, 69, 19)))
        self.user_icon_person = self.rgb_to_hex(palette_dict.get('user_icon_person', (139, 69, 19)))
        
        self.question_bg = self.rgb_to_hex(palette_dict.get('question_bg', (255, 165, 0)))
        self.question_text = self.rgb_to_hex(palette_dict.get('question_text', (255, 255, 255)))
        
        # Fondo general
        self.background = self.rgb_to_hex(palette_dict.get('background', (240, 240, 245)))
    
    def rgb_to_hex(self, rgb):
        """Convierte tupla RGB a hexadecimal"""
        return '#%02x%02x%02x' % rgb
    
    def get_default_palette(self):
        """Paleta por defecto con tonos de zacate"""
        return {
            'safe_zone_bg': (240, 248, 255),
            'safe_houses': (139, 69, 19),
            'safe_houses_roof': (178, 34, 34),
            'safe_houses_door': (90, 45, 12),
            'safe_houses_window': (255, 255, 200),
            'invader_zone_bg': (30, 30, 35),
            'invader_houses': (60, 60, 60),
            'invader_houses_roof': (120, 20, 20),
            'invader_houses_door': (40, 40, 40),
            'invader_houses_window': (150, 100, 100),
            'grid_bg_light': (180, 200, 120),
            'grid_bg_dark': (140, 170, 90),
            'grid_lines': (100, 130, 60),
            'grid_border': (80, 100, 40),
            'user_icon_bg': (255, 255, 255),
            'user_icon_border': (139, 69, 19),
            'user_icon_person': (139, 69, 19),
            'question_bg': (255, 165, 0),
            'question_text': (255, 255, 255),
            'background': (240, 240, 245)
        }
    
    def update_palette(self, new_palette_dict):
        """Actualiza la paleta con nuevos colores"""
        self.load_palette(new_palette_dict)


class House:
    def __init__(self, x, y, palette, is_invader=False):
        self.x = x
        self.y = y
        self.palette = palette
        self.is_invader = is_invader
        self.size = 35
    
    def get_colors(self):
        """Obtiene los colores según el tipo de casa"""
        if self.is_invader:
            return {
                'body': self.palette.invader_houses,
                'roof': self.palette.invader_houses_roof,
                'door': self.palette.invader_houses_door,
                'window': self.palette.invader_houses_window
            }
        else:
            return {
                'body': self.palette.safe_houses,
                'roof': self.palette.safe_houses_roof,
                'door': self.palette.safe_houses_door,
                'window': self.palette.safe_houses_window
            }
    
    def draw(self, canvas):
        colors = self.get_colors()
        
        # Cuerpo de la casa (rectángulo)
        canvas.create_rectangle(
            self.x, self.y + 12,
            self.x + self.size, self.y + self.size,
            fill=colors['body'], outline=colors['body']
        )
        
        # Techo triangular (polígono)
        roof_points = [
            self.x, self.y + 12,
            self.x + self.size // 2, self.y,
            self.x + self.size, self.y + 12
        ]
        canvas.create_polygon(roof_points, fill=colors['roof'], outline=colors['roof'])
        
        # Puerta
        canvas.create_rectangle(
            self.x + 12, self.y + 22,
            self.x + 23, self.y + 40,
            fill=colors['door'], outline=colors['door']
        )
        
        # Ventana
        canvas.create_rectangle(
            self.x + 5, self.y + 16,
            self.x + 14, self.y + 25,
            fill=colors['window'], outline=colors['window']
        )


class UserIcon:
    def __init__(self, x, y, palette):
        self.x = x
        self.y = y
        self.palette = palette
        self.size = 45
    
    def draw(self, canvas):
        radius = self.size // 2
        
        # Círculo de fondo
        canvas.create_oval(
            self.x - radius, self.y - radius,
            self.x + radius, self.y + radius,
            fill=self.palette.user_icon_bg,
            outline=self.palette.user_icon_border,
            width=3
        )
        
        # Cabeza de la persona
        canvas.create_oval(
            self.x - 8, self.y - 13,
            self.x + 8, self.y + 3,
            fill=self.palette.user_icon_person,
            outline=self.palette.user_icon_person
        )
        
        # Cuerpo de la persona (arco simulado con óvalo parcial)
        canvas.create_arc(
            self.x - 12, self.y,
            self.x + 12, self.y + 20,
            start=0, extent=180,
            outline=self.palette.user_icon_person,
            width=4, style='arc'
        )


class QuestionButton:
    def __init__(self, x, y, palette):
        self.x = x
        self.y = y
        self.palette = palette
        self.size = 45
    
    def draw(self, canvas):
        radius = self.size // 2
        
        # Círculo de fondo con el presupuesto actual
        canvas.create_oval(
            self.x - radius, self.y - radius,
            self.x + radius, self.y + radius,
            fill=self.palette.question_bg,
            outline=self.palette.question_bg
        )
        
        # Signo de interrogación ($)
        canvas.create_text(
            self.x, self.y,
            text="$",
            font=("Arial", 30, "bold"),
            fill=self.palette.question_text
        )


class TopRightButton:
    """Botón START rectangular en la esquina superior derecha del grid"""
    def __init__(self, x, y, palette):
        self.x = x
        self.y = y
        self.palette = palette
        self.width = 110
        self.height = 45
        self.visible = True
    
    def draw(self, canvas):
        if not self.visible:
            return
        
        # Rectángulo del botón
        canvas.create_rectangle(
            self.x - self.width // 2, self.y - self.height // 2,
            self.x + self.width // 2, self.y + self.height // 2,
            fill="#28a745",  # Verde brillante
            outline="#1e7e34",  # Verde oscuro para borde
            width=3
        )
        
        # Texto del botón
        canvas.create_text(
            self.x, self.y,
            text="START",
            font=("Arial", 18, "bold"),
            fill="white"
        )
    
    def hide(self):
        """Oculta el botón"""
        self.visible = False


class ElementButton:
    """Botón para los elementos (arena, roca, agua, fuego) ACTUALIZADO CON FUNCIONALIDAD DE COMPRA"""
    def __init__(self, x, y, element_type, palette, game_ref):
        self.x = x
        self.y = y
        self.element_type = element_type
        self.palette = palette
        self.size = 50
        self.game = game_ref  # Referencia al juego para crear torres
        
        # Configuración por tipo de elemento
        self.configs = {
            'sand': {
                'emoji': '⛰️', 
                'color': '#C4A35A', 
                'name': 'Arena',
                'price': 50,
                'class': RookArena
            },
            'rock': {
                'emoji': '🪨', 
                'color': '#7A6F5D', 
                'name': 'Roca',
                'price': 100,
                'class': RookRoca
            },
            'water': {
                'emoji': '💧', 
                'color': '#5B7C8D', 
                'name': 'Agua',
                'price': 150,
                'class': RookAgua
            },
            'fire': {
                'emoji': '🔥', 
                'color': '#B85450', 
                'name': 'Fuego',
                'price': 150,
                'class': RookFuego
            }
        }
        
        self.config = self.configs.get(element_type)
    
    def draw(self, canvas):
        if not self.config:
            return
        
        radius = self.size // 2
        
        # Círculo de fondo
        canvas.create_oval(
            self.x - radius, self.y - radius,
            self.x + radius, self.y + radius,
            fill=self.config['color'],
            outline='#333333',
            width=2,
            tags=(f"element_{self.element_type}", "element_button")
        )
        
        # Emoji del elemento
        canvas.create_text(
            self.x, self.y - 5,
            text=self.config['emoji'],
            font=("Arial", 24),
            tags=(f"element_{self.element_type}_text", "element_button")
        )
        
        # Precio
        canvas.create_text(
            self.x, self.y + 18,
            text=f"${self.config['price']}",
            font=("Arial", 10, "bold"),
            fill="white",
            tags=(f"element_{self.element_type}_price", "element_button")
        )
    
    def is_clicked(self, x, y):
        """Verifica si el botón fue clickeado"""
        distance = ((x - self.x) ** 2 + (y - self.y) ** 2) ** 0.5
        return distance <= self.size // 2
    
    def on_click(self):
        """Maneja el click en el botón"""
        if self.game.presupuesto >= self.config['price']:
            # Pedir coordenadas para colocar la torre
            self.game.esperando_colocacion = self.element_type
            self.game.torre_a_colocar = self.config
            print(f"Selecciona una celda para colocar la torre de {self.config['name']}")
        else:
            messagebox.showwarning("Sin fondos", 
                                  f"No tienes suficiente presupuesto. Necesitas ${self.config['price']}, tienes ${self.game.presupuesto}")


class Grid:
    """Clase para la cuadrícula del juego"""
    def __init__(self, x, y, rows, cols, cell_size, palette):
        self.x = x
        self.y = y
        self.rows = rows
        self.cols = cols
        self.cell_size = cell_size
        self.palette = palette
        self.width = cols * cell_size
        self.height = rows * cell_size
        self.torres_grid = {}  # Diccionario para almacenar torres por posición
    
    def draw(self, canvas):
        # Borde de la cuadrícula
        canvas.create_rectangle(
            self.x - 4, self.y - 4,
            self.x + self.width + 4, self.y + self.height + 4,
            fill=self.palette.grid_border,
            outline=self.palette.grid_border
        )
        
        # Dibujar celdas con patrón de tablero
        for row in range(self.rows):
            for col in range(self.cols):
                x1 = self.x + col * self.cell_size
                y1 = self.y + row * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                
                # Alternar colores
                if (row + col) % 2 == 0:
                    color = self.palette.grid_bg_light
                else:
                    color = self.palette.grid_bg_dark
                
                canvas.create_rectangle(
                    x1, y1, x2, y2,
                    fill=color,
                    outline=self.palette.grid_lines
                )
                
                # Agregar textura de zacate
                self.draw_grass_texture(canvas, x1, y1, x2, y2)
        
        # Dibujar líneas de la cuadrícula
        for col in range(self.cols + 1):
            x_pos = self.x + col * self.cell_size
            canvas.create_line(
                x_pos, self.y,
                x_pos, self.y + self.height,
                fill=self.palette.grid_lines,
                width=2
            )
        
        for row in range(self.rows + 1):
            y_pos = self.y + row * self.cell_size
            canvas.create_line(
                self.x, y_pos,
                self.x + self.width, y_pos,
                fill=self.palette.grid_lines,
                width=2
            )
        
        # Dibujar las torres
        for (row, col), torre in self.torres_grid.items():
            self.draw_torre(canvas, torre, row, col)
    
    def draw_grass_texture(self, canvas, x1, y1, x2, y2):
        """Dibuja pequeñas líneas para simular textura de zacate"""
        # Seed basado en posición para que sea consistente
        random.seed(int(x1 * y1))
        
        # Dibujar algunas líneas pequeñas
        for _ in range(3):
            x_rand = random.randint(int(x1) + 5, int(x2) - 5)
            y_rand = random.randint(int(y1) + 5, int(y2) - 5)
            length = random.randint(3, 8)
            
            # Línea vertical pequeña
            canvas.create_line(
                x_rand, y_rand,
                x_rand, y_rand + length,
                fill=self.palette.grid_lines,
                width=1
            )
        
        random.seed()  # Reset seed
    
    def draw_torre(self, canvas, torre, row, col):
        """Dibuja una torre en la posición especificada"""
        x = self.x + col * self.cell_size + self.cell_size // 2
        y = self.y + row * self.cell_size + self.cell_size // 2
        
        # Círculo base de la torre
        radius = 20
        canvas.create_oval(
            x - radius, y - radius,
            x + radius, y + radius,
            fill=torre.color,
            outline='#333333',
            width=2
        )
        
        # Icono de la torre
        canvas.create_text(
            x, y - 3,
            text=torre.icono,
            font=("Arial", 18)
        )
        
        # Barra de vida
        vida_percent = torre.vida_actual / torre.vida_maxima
        bar_width = 30
        bar_height = 4
        bar_x = x - bar_width // 2
        bar_y = y + radius + 3
        
        # Fondo de la barra (rojo)
        canvas.create_rectangle(
            bar_x, bar_y,
            bar_x + bar_width, bar_y + bar_height,
            fill='#cc0000',
            outline='#333333'
        )
        
        # Vida actual (verde)
        if vida_percent > 0:
            canvas.create_rectangle(
                bar_x, bar_y,
                bar_x + (bar_width * vida_percent), bar_y + bar_height,
                fill='#00cc00',
                outline=''
            )
    
    def get_cell_from_coords(self, x, y):
        """Obtiene la celda (row, col) de las coordenadas del click"""
        if x < self.x or x > self.x + self.width:
            return None
        if y < self.y or y > self.y + self.height:
            return None
        
        col = int((x - self.x) / self.cell_size)
        row = int((y - self.y) / self.cell_size)
        
        if 0 <= row < self.rows and 0 <= col < self.cols:
            return (row, col)
        return None
    
    def add_torre(self, torre, row, col):
        """Agrega una torre a la cuadrícula"""
        self.torres_grid[(row, col)] = torre


class VillageGame(tk.Frame):
    """Clase principal del juego de aldeas en Tkinter"""
    def __init__(self, parent, width=600, height=750, nivel="FACIL", frecuencias=None, initial_palette=None):
        super().__init__(parent, width=width, height=height)
        self.width = width
        self.height = height
        
        # Configuración del juego
        self.nivel = nivel
        self.frecuencias = frecuencias or {}
        self.presupuesto = 600  # Presupuesto inicial
        self.gestor_rooks = GestorRooks()  # Gestor de torres
        self.esperando_colocacion = None  # Para el sistema de colocación
        self.torre_a_colocar = None
        self.prueba_activa = False
        self.tiempo_inicio_prueba = None
        
        # Sistema de colores
        self.palette = ColorPalette(initial_palette)
        
        # Crear canvas principal
        self.canvas = Canvas(
            self,
            width=self.width,
            height=self.height,
            bg=self.palette.background,
            highlightthickness=0
        )
        self.canvas.pack()
        
        # Configuración de la cuadrícula (ahora 5x9)
        self.grid_cols = 5
        self.grid_rows = 9
        self.cell_size = 60
        grid_width = self.grid_cols * self.cell_size
        self.grid_x = (self.width - grid_width) // 2
        
        self.grid = Grid(self.grid_x, 100, self.grid_rows, self.grid_cols, 
                        self.cell_size, self.palette)
        
        # Crear casas de la zona segura (5 casas con más espacio)
        self.safe_houses = []
        num_safe_houses = 5
        house_spacing = grid_width // (num_safe_houses + 1)
        house_y = 10
        
        for i in range(num_safe_houses):
            x_pos = self.grid_x + house_spacing * (i + 1) - 17
            self.safe_houses.append(House(x_pos, house_y, self.palette, is_invader=False))
        
        # Crear elementos UI
        self.user_icon = UserIcon(40, 30, self.palette)
        self.question_btn = QuestionButton(self.width - 40, 30, self.palette)
        
        # Crear botón en la esquina superior derecha del grid (fuera del grid)
        grid_right_x = self.grid_x + self.grid.width
        grid_top_y = 100
        button_x = grid_right_x + 70  # Más separado para evitar traslape
        button_y = grid_top_y + 20  # Alineado con la altura de la cuadrícula
        self.top_right_btn = TopRightButton(button_x, button_y, self.palette)
        
        # Crear botones de elementos al lado derecho de la cuadrícula
        self.element_buttons = []
        element_types = ['sand', 'rock', 'water', 'fire']
        element_x = button_x  # Usar la misma X del botón START para centrarlos
        start_y = button_y + 110  # Empezar más abajo del botón START
        spacing = 70  # Espacio entre botones
        
        for i, element in enumerate(element_types):
            element_y = start_y + (i * spacing)
            self.element_buttons.append(ElementButton(element_x, element_y, element, self.palette, self))
        
        # Vincular eventos del canvas
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        
        # Crear etiqueta para mostrar el presupuesto
        self.presupuesto_label = tk.Label(
            self,
            text=f"Presupuesto: ${self.presupuesto}",
            font=("Arial", 14, "bold"),
            bg=self.palette.background
        )
        self.presupuesto_label.place(x=10, y=60)
        
        # Aplicar frecuencias del menú
        if self.frecuencias:
            self.gestor_rooks.actualizar_frecuencias(self.frecuencias)
            print("\nFrecuencias aplicadas desde el menú:")
            for nombre, freq in self.frecuencias.items():
                print(f"  {nombre}: {freq}")
        
        # Dibujar todo
        self.draw()
        
        # Iniciar animación
        self.animate()
    
    def draw_zones(self):
        """Dibuja las zonas segura e invasora"""
        # Zona segura
        self.canvas.create_rectangle(
            self.grid_x - 8, 0, self.grid_x + self.grid_cols * self.cell_size + 8, 60,
            fill=self.palette.safe_zone_bg,
            outline=self.palette.safe_zone_bg,
            tags="zones"
        )
        
        # Zona invasora
        self.canvas.create_rectangle(
            self.grid_x - 8, 690, self.grid_x + self.grid_cols * self.cell_size + 8, 750,
            fill=self.palette.invader_zone_bg,
            outline=self.palette.invader_zone_bg,
            tags="zones"
        )
    
    def apply_new_palette(self, new_palette_dict):
        """Aplica una nueva paleta de colores y redibuja"""
        self.palette.update_palette(new_palette_dict)
        # Recrear la cuadrícula con los nuevos colores
        self.grid = Grid(self.grid_x, 100, self.grid_rows, self.grid_cols, 
                        self.cell_size, self.palette)
        self.draw()
    
    def draw(self):
        """Dibuja todos los elementos"""
        # Limpiar canvas
        self.canvas.delete("all")
        
        # Fondo general
        self.canvas.configure(bg=self.palette.background)
        
        # Dibujar zonas
        self.draw_zones()
        
        # Dibujar cuadrícula y torres
        self.grid.draw(self.canvas)
        
        # Dibujar casas seguras
        for house in self.safe_houses:
            house.draw(self.canvas)
        
        # Dibujar elementos UI
        self.user_icon.draw(self.canvas)
        self.question_btn.draw(self.canvas)
        self.top_right_btn.draw(self.canvas)
        
        # Dibujar botones de elementos
        for element_btn in self.element_buttons:
            element_btn.draw(self.canvas)
        
        # Actualizar etiqueta de presupuesto
        self.presupuesto_label.config(text=f"Presupuesto: ${self.presupuesto}")
    
    def animate(self):
        """Método para animaciones y actualización del juego"""
        # Actualizar torres si hay una prueba activa
        if self.prueba_activa and self.tiempo_inicio_prueba:
            tiempo_actual = time.time() - self.tiempo_inicio_prueba
            self.gestor_rooks.update(tiempo_actual)
            
            # Redibujar para mostrar cambios
            self.draw()
        
        # Continuar el loop
        self.after(33, self.animate)  # ~30 FPS
    
    def on_canvas_click(self, event):
        """Maneja los clics en el canvas"""
        # Si estamos esperando colocar una torre
        if self.esperando_colocacion:
            cell = self.grid.get_cell_from_coords(event.x, event.y)
            if cell:
                row, col = cell
                # Verificar si la celda está vacía
                if (row, col) not in self.grid.torres_grid:
                    self.colocar_torre(row, col)
                else:
                    messagebox.showinfo("Celda ocupada", "Ya hay una torre en esta posición")
            return
        
        # Verificar clics en botones de elementos
        for btn in self.element_buttons:
            if btn.is_clicked(event.x, event.y):
                btn.on_click()
                return
        
        # Verificar si el clic está dentro del rectángulo del botón START
        if self.top_right_btn.visible:
            x1 = self.top_right_btn.x - self.top_right_btn.width // 2
            y1 = self.top_right_btn.y - self.top_right_btn.height // 2
            x2 = self.top_right_btn.x + self.top_right_btn.width // 2
            y2 = self.top_right_btn.y + self.top_right_btn.height // 2
            
            # Si el clic está dentro del rectángulo
            if x1 <= event.x <= x2 and y1 <= event.y <= y2:
                self.on_top_right_button_pressed()
    
    def colocar_torre(self, row, col):
        """Coloca una torre en la posición especificada"""
        if self.torre_a_colocar and self.presupuesto >= self.torre_a_colocar['price']:
            # Obtener la frecuencia correspondiente
            mapeo_frecuencias = {
                'sand': self.frecuencias.get("⛰️  TORRE DE ARENA", 5),
                'rock': self.frecuencias.get("🪨  TORRE DE ROCA", 5),
                'water': self.frecuencias.get("💧 TORRE DE AGUA", 5),
                'fire': self.frecuencias.get("🔥 TORRE DE FUEGO", 5)
            }
            
            frecuencia = mapeo_frecuencias.get(self.esperando_colocacion, 5)
            
            # Crear la torre
            posicion = [col * self.cell_size, row * self.cell_size]
            torre = self.torre_a_colocar['class'](posicion, frecuencia)
            
            # Agregar al gestor y a la cuadrícula
            self.gestor_rooks.torres.append(torre)
            self.grid.add_torre(torre, row, col)
            
            # Actualizar presupuesto
            self.presupuesto -= self.torre_a_colocar['price']
            
            print(f"✅ Torre de {self.torre_a_colocar['name']} colocada | Presupuesto: ${self.presupuesto}")
            
            # Prueba automática desactivada - descomentar la siguiente línea para pruebas
            # self.iniciar_prueba_torre(torre)
            
            # Limpiar estado
            self.esperando_colocacion = None
            self.torre_a_colocar = None
            
            # Redibujar
            self.draw()
    
    def iniciar_prueba_torre(self, torre):
        """Inicia una prueba de disparo para la torre especificada"""
        def ejecutar_prueba():
            print(f"\n{'='*50}")
            print(f"🎯 INICIANDO PRUEBA DE TORRE DE {torre.tipo.upper()}")
            print(f"{'='*50}")
            print(f"Frecuencia de disparo: {torre.frecuencia_disparo} segundos")
            print(f"Daño por proyectil: {torre.damage_proyectil}")
            print(f"Vida: {torre.vida_actual}/{torre.vida_maxima}")
            print(f"{'='*50}\n")
            
            tiempo_inicio = time.time()
            duracion = 15  # Prueba de 15 segundos
            ultimo_segundo = -1
            
            while time.time() - tiempo_inicio < duracion:
                tiempo_actual = time.time() - tiempo_inicio
                segundo_actual = int(tiempo_actual)
                
                # Mostrar progreso cada segundo
                if segundo_actual != ultimo_segundo:
                    ultimo_segundo = segundo_actual
                    print(f"⏱️ Segundo {segundo_actual + 1}/15")
                
                # Intentar disparar
                proyectil = torre.disparar(tiempo_actual)
                if proyectil:
                    print(f"   💥 ¡DISPARO! Torre de {torre.tipo} → Daño: {proyectil.damage}")
                
                time.sleep(0.1)
            
            print(f"\n{'='*50}")
            print(f"✅ PRUEBA COMPLETADA")
            print(f"Torre de {torre.tipo} - Estado final: {torre.vida_actual}/{torre.vida_maxima} HP")
            print(f"{'='*50}\n")
        
        # Ejecutar en un thread separado para no bloquear la UI
        thread = threading.Thread(target=ejecutar_prueba)
        thread.daemon = True
        thread.start()
    
    def on_top_right_button_pressed(self):
        """Función llamada cuando se presiona el botón START"""
        print("🎮 ¡JUEGO INICIADO!")
        print(f"Nivel: {self.nivel} | Presupuesto: ${self.presupuesto}")
        
        self.top_right_btn.hide()
        self.prueba_activa = True
        self.tiempo_inicio_prueba = time.time()
        self.draw()


class VillageGameWindow:
    """Ventana independiente del juego"""
    def __init__(self, nivel="FACIL", frecuencias=None, initial_palette=None):
        self.root = tk.Tk()
        self.root.title(f"Sistema de Aldeas - Nivel {nivel}")
        self.root.geometry("600x750")
        self.root.resizable(False, False)
        
        # Guardar configuración del juego
        self.nivel = nivel
        self.frecuencias = frecuencias or {}
        
        # Crear el juego con las configuraciones
        self.game = VillageGame(self.root, 600, 750, nivel, frecuencias, initial_palette)
        self.game.pack()
    
    def run(self):
        """Inicia el loop principal"""
        self.root.mainloop()


if __name__ == "__main__":
    # Ejecutar el juego en modo standalone con valores de prueba
    frecuencias_prueba = {
        "⛰️  TORRE DE ARENA": 3,
        "🪨  TORRE DE ROCA": 4,
        "💧 TORRE DE AGUA": 2,
        "🔥 TORRE DE FUEGO": 5
    }
    game_window = VillageGameWindow(nivel="PRUEBA", frecuencias=frecuencias_prueba)
    game_window.run()