"""
Sistema de juego de aldeas con cuadrícula.
Versión completamente en Tkinter (sin Pygame).
Recibe paletas de colores desde módulos externos.
"""
import tkinter as tk
from tkinter import Canvas


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
        
        # Cuadrícula
        self.grid_bg = self.rgb_to_hex(palette_dict.get('grid_bg', (255, 255, 255)))
        self.grid_lines = self.rgb_to_hex(palette_dict.get('grid_lines', (139, 69, 19)))
        
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
        """Paleta por defecto"""
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
            'grid_bg': (255, 255, 255),
            'grid_lines': (139, 69, 19),
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
        half_size = self.size // 2
        
        # Fondo redondeado (rectángulo con esquinas redondeadas simuladas)
        canvas.create_rectangle(
            self.x - half_size, self.y - half_size,
            self.x + half_size, self.y + half_size,
            fill=self.palette.question_bg,
            outline=self.palette.question_bg
        )
        
        # Signo de interrogación
        canvas.create_text(
            self.x, self.y,
            text="?",
            font=("Arial", 30, "bold"),
            fill=self.palette.question_text
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
    
    def draw(self, canvas):
        # Fondo de la cuadrícula
        canvas.create_rectangle(
            self.x, self.y,
            self.x + self.width, self.y + self.height,
            fill=self.palette.grid_bg,
            outline=self.palette.grid_bg
        )
        
        # Líneas verticales
        for col in range(self.cols + 1):
            x_pos = self.x + col * self.cell_size
            canvas.create_line(
                x_pos, self.y,
                x_pos, self.y + self.height,
                fill=self.palette.grid_lines,
                width=2
            )
        
        # Líneas horizontales
        for row in range(self.rows + 1):
            y_pos = self.y + row * self.cell_size
            canvas.create_line(
                self.x, y_pos,
                self.x + self.width, y_pos,
                fill=self.palette.grid_lines,
                width=2
            )


class VillageGame(tk.Frame):
    """Clase principal del juego de aldeas en Tkinter"""
    def __init__(self, parent, width=500, height=700, initial_palette=None):
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
        
        # Configuración de la cuadrícula
        self.grid_cols = 5
        self.grid_rows = 8
        self.cell_size = 60
        grid_width = self.grid_cols * self.cell_size
        self.grid_x = (self.width - grid_width) // 2
        
        self.grid = Grid(self.grid_x, 120, self.grid_rows, self.grid_cols, 
                        self.cell_size, self.palette)
        
        # Crear casas de la zona segura
        self.safe_houses = []
        num_safe_houses = 6
        house_spacing = grid_width // (num_safe_houses + 1)
        house_y = 45
        
        for i in range(num_safe_houses):
            x_pos = self.grid_x + house_spacing * (i + 1) - 17
            self.safe_houses.append(House(x_pos, house_y, self.palette, is_invader=False))
        
        # Crear elementos UI
        self.user_icon = UserIcon(40, 40, self.palette)
        self.question_btn = QuestionButton(460, 40, self.palette)
        
        # Dibujar todo
        self.draw()
        
        # Iniciar animación
        self.animate()
    
    def draw_zones(self):
        """Dibuja las zonas segura e invasora"""
        # Zona segura
        self.canvas.create_rectangle(
            0, 0, self.width, 115,
            fill=self.palette.safe_zone_bg,
            outline=self.palette.safe_zone_bg,
            tags="zones"
        )
        
        # Zona invasora
        self.canvas.create_rectangle(
            0, 600, self.width, 700,
            fill=self.palette.invader_zone_bg,
            outline=self.palette.invader_zone_bg,
            tags="zones"
        )
    
    def apply_new_palette(self, new_palette_dict):
        """Aplica una nueva paleta de colores y redibuja"""
        self.palette.update_palette(new_palette_dict)
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
    
    def animate(self):
        """Método para animaciones futuras"""
        # Aquí se pueden agregar animaciones
        # Por ahora solo mantiene el loop
        self.after(33, self.animate)  # ~30 FPS


class VillageGameWindow:
    """Ventana independiente del juego"""
    def __init__(self, initial_palette=None):
        self.root = tk.Tk()
        self.root.title("Sistema de Aldeas")
        self.root.geometry("500x700")
        self.root.resizable(False, False)
        
        # Crear el juego
        self.game = VillageGame(self.root, 500, 700, initial_palette)
        self.game.pack()
    
    def run(self):
        """Inicia el loop principal"""
        self.root.mainloop()


if __name__ == "__main__":
    # Ejecutar el juego en modo standalone
    game_window = VillageGameWindow()
    game_window.run()