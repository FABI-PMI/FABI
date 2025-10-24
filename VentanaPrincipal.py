"""
Sistema visual del juego Avatars vs Rooks 
Este módulo implementa la interfaz gráfica usando Tkinter.
"""
import tkinter as tk
from tkinter import Canvas
import random


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
        
        # Círculo de fondo
        canvas.create_oval(
            self.x - radius, self.y - radius,
            self.x + radius, self.y + radius,
            fill=self.palette.question_bg,
            outline=self.palette.question_bg
        )
        
        # Signo de interrogación (?)
        canvas.create_text(
            self.x, self.y,
            text="?",
            font=("Arial", 30, "bold"),
            fill=self.palette.question_text
        )



class TopRightButton:
    """Botón START rectangular en la esquina superior derecha del grid"""
    def __init__(self, x, y, palette):
        self.x = x
        self.y = y
        self.palette = palette
        # Dimensiones del rectángulo (ancho x alto)
        self.width = 80
        self.height = 40
        self.visible = True
    
    def draw(self, canvas):
        if not self.visible:
            return
        
        # Calcular las esquinas del rectángulo
        x1 = self.x - self.width // 2
        y1 = self.y - self.height // 2
        x2 = self.x + self.width // 2
        y2 = self.y + self.height // 2
        
        # Rectángulo de fondo con color principal (safe_houses)
        canvas.create_rectangle(
            x1, y1, x2, y2,
            fill=self.palette.safe_houses,
            outline=self.palette.safe_houses_roof,
            width=3,
            tags="top_right_button"
        )
        
        # Texto "START" centrado en el rectángulo
        canvas.create_text(
            self.x, self.y,
            text="START",
            font=("Arial", 12, "bold"),
            fill=self.palette.safe_houses_window,
            tags="top_right_button"
        )
    
    def hide(self):
        self.visible = False

class ElementButton:
    """Botones cuadrados temáticos de elementos (arena, roca, agua, fuego)"""
    def __init__(self, x, y, element_type, palette):
        self.x = x
        self.y = y
        self.element_type = element_type  # 'sand', 'rock', 'water', 'fire'
        self.palette = palette
        self.size = 55  # Tamaño del cuadrado
    
    def get_colors(self):
        """Retorna los colores según el tipo de elemento"""
        if self.element_type == 'sand':
            return {
                'bg': '#F4A460',  # Sandy brown
                'accent': '#DEB887',  # Burlywood
                'dots': '#D2691E'  # Chocolate
            }
        elif self.element_type == 'rock':
            return {
                'bg': '#808080',  # Gray base fijo
                'accent': '#696969',  # Dim gray
                'dots': '#404040'  # Grietas oscuras
            }
        elif self.element_type == 'water':
            return {
                'bg': '#4682B4',  # Steel blue
                'accent': '#5F9EA0',  # Cadet blue
                'dots': '#1E90FF'  # Dodger blue
            }
        elif self.element_type == 'fire':
            return {
                'bg': '#FF4500',  # Orange red
                'accent': '#FF6347',  # Tomato
                'dots': '#FFD700'  # Gold
            }
    
    def draw(self, canvas):
        colors = self.get_colors()
        half = self.size // 2
        
        # Cuadrado de fondo
        canvas.create_rectangle(
            self.x - half, self.y - half,
            self.x + half, self.y + half,
            fill=colors['bg'],
            outline='#333333',
            width=2
        )
        
        # Decoración según el elemento
        if self.element_type == 'sand':
            # Puntos aleatorios para simular granos de arena
            import random
            random.seed(self.x + self.y)
            for _ in range(12):
                px = self.x - half + random.randint(5, self.size - 5)
                py = self.y - half + random.randint(5, self.size - 5)
                canvas.create_oval(px-1, py-1, px+1, py+1, fill=colors['dots'], outline=colors['dots'])
            random.seed()
        
        elif self.element_type == 'rock':
            # Grietas oscuras en patrón irregular sobre fondo gris
            # Grieta diagonal principal
            canvas.create_line(
                self.x - 18, self.y - 12,
                self.x + 15, self.y + 18,
                fill=colors['dots'], width=3
            )
            # Grieta secundaria
            canvas.create_line(
                self.x - 10, self.y - 20,
                self.x - 5, self.y + 8,
                fill=colors['dots'], width=2
            )
            # Grieta terciaria
            canvas.create_line(
                self.x + 8, self.y - 15,
                self.x + 20, self.y - 5,
                fill=colors['dots'], width=2
            )
            # Pequeñas grietas adicionales
            canvas.create_line(
                self.x - 15, self.y + 5,
                self.x - 8, self.y + 12,
                fill=colors['accent'], width=2
            )
            canvas.create_line(
                self.x + 5, self.y + 8,
                self.x + 18, self.y + 15,
                fill=colors['accent'], width=2
            )
        
        elif self.element_type == 'water':
            # Ondas horizontales
            for i in range(3):
                y_wave = self.y - half + 15 + (i * 12)
                canvas.create_arc(
                    self.x - half + 5, y_wave - 5,
                    self.x - half + 25, y_wave + 5,
                    start=0, extent=180, style='arc',
                    outline=colors['accent'], width=2
                )
                canvas.create_arc(
                    self.x - 10, y_wave - 5,
                    self.x + 10, y_wave + 5,
                    start=0, extent=180, style='arc',
                    outline=colors['dots'], width=2
                )
                canvas.create_arc(
                    self.x + 5, y_wave - 5,
                    self.x + half - 5, y_wave + 5,
                    start=0, extent=180, style='arc',
                    outline=colors['accent'], width=2
                )
        
        elif self.element_type == 'fire':
            # Diseño de fuego con círculos concéntricos (estilo brasas)
            # Círculo exterior rojo oscuro
            canvas.create_oval(
                self.x - 22, self.y - 18,
                self.x + 22, self.y + 22,
                fill='#8B0000', outline=''
            )
            # Círculo medio rojo
            canvas.create_oval(
                self.x - 16, self.y - 12,
                self.x + 16, self.y + 16,
                fill='#DC143C', outline=''
            )
            # Círculo naranja
            canvas.create_oval(
                self.x - 10, self.y - 6,
                self.x + 10, self.y + 10,
                fill='#FF6347', outline=''
            )
            # Círculo amarillo central (parte más caliente)
            canvas.create_oval(
                self.x - 5, self.y - 2,
                self.x + 5, self.y + 6,
                fill='#FFD700', outline=''
            )



class Grid:
    def __init__(self, x, y, rows, cols, cell_size, palette):
        self.x = x
        self.y = y
        self.rows = rows
        self.cols = cols
        self.cell_size = cell_size
        self.palette = palette
        self.width = cols * cell_size
        self.height = rows * cell_size
        
        # Generar patrón de tablero de ajedrez para el zacate
        self.cell_colors = []
        for row in range(rows):
            row_colors = []
            for col in range(cols):
                # Alternar colores como tablero de ajedrez
                if (row + col) % 2 == 0:
                    row_colors.append(self.palette.grid_bg_light)
                else:
                    row_colors.append(self.palette.grid_bg_dark)
            self.cell_colors.append(row_colors)
    
    def draw(self, canvas):
        # Borde exterior más grueso y oscuro
        border_width = 8
        canvas.create_rectangle(
            self.x - border_width, self.y - border_width,
            self.x + self.width + border_width, self.y + self.height + border_width,
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
                
                # Dibujar celda con su color
                canvas.create_rectangle(
                    x1, y1, x2, y2,
                    fill=self.cell_colors[row][col],
                    outline=self.cell_colors[row][col]
                )
                
                # Agregar textura de zacate (líneas pequeñas)
                self.draw_grass_texture(canvas, x1, y1, x2, y2)
        
        # Líneas de la cuadrícula (más sutiles)
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


class VillageGame(tk.Frame):
    """Clase principal del juego de aldeas en Tkinter"""
    def __init__(self, parent, width=600, height=750, initial_palette=None):
        super().__init__(parent, width=width, height=height)
        self.width = width
        self.height = height
        
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
        # Posición: esquina superior derecha del grid + offset
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
            self.element_buttons.append(ElementButton(element_x, element_y, element, self.palette))
        
        # Vincular eventos del canvas
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        
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
        
        # Dibujar cuadrícula
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
    
    def animate(self):
        """Método para animaciones futuras"""
        # Aquí se pueden agregar animaciones
        # Por ahora solo mantiene el loop
        self.after(33, self.animate)  # ~30 FPS
    
    def on_canvas_click(self, event):
        """Maneja los clics en el canvas"""
        # Verificar si el clic está dentro del rectángulo del botón
        if self.top_right_btn.visible:
            x1 = self.top_right_btn.x - self.top_right_btn.width // 2
            y1 = self.top_right_btn.y - self.top_right_btn.height // 2
            x2 = self.top_right_btn.x + self.top_right_btn.width // 2
            y2 = self.top_right_btn.y + self.top_right_btn.height // 2
            
            # Si el clic está dentro del rectángulo
            if x1 <= event.x <= x2 and y1 <= event.y <= y2:
                self.on_top_right_button_pressed()
    
    def on_top_right_button_pressed(self):
        """Función llamada cuando se presiona el botón START"""
        print("=" * 50)
        print("🎮 ¡JUEGO INICIADO!")
        print("=" * 50)
        print("Botón START presionado - Iniciar lógica del juego")
        print("=" * 50)
        # TODO: Agregar lógica del juego aquí
        self.top_right_btn.hide()
        self.draw()



class VillageGameWindow:
    """Ventana independiente del juego"""
    def __init__(self, initial_palette=None):
        self.root = tk.Tk()
        self.root.title("Sistema de Aldeas")
        self.root.geometry("600x750")
        self.root.resizable(False, False)
        
        # Crear el juego
        self.game = VillageGame(self.root, 600, 750, initial_palette)
        self.game.pack()
    
    def run(self):
        """Inicia el loop principal"""
        self.root.mainloop()


if __name__ == "__main__":
    # Ejecutar el juego en modo standalone
    game_window = VillageGameWindow()
    game_window.run()