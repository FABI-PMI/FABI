"""
Sistema de juego de aldeas con cuadrícula.
Versión completamente en Tkinter (sin Pygame).
Con sistema de puntos y monedas integrado.
VERSIÓN CORREGIDA: Avatares visibles y torres disparan hacia abajo
"""
import tkinter as tk
from tkinter import Canvas, messagebox
import random
import time
import threading
from RooksClass import RookArena, RookRoca, RookAgua, RookFuego, GestorRooks
from AvatarClass import GestorAvatares
from MoneySystem import SistemaPuntos, SistemaMonedas


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
        self.grid_bg_light = self.rgb_to_hex(palette_dict.get('grid_bg_light', (144, 238, 144)))
        self.grid_bg_dark = self.rgb_to_hex(palette_dict.get('grid_bg_dark', (34, 139, 34)))
        self.grid_lines = self.rgb_to_hex(palette_dict.get('grid_lines', (139, 69, 19)))
        self.grid_border = self.rgb_to_hex(palette_dict.get('grid_border', (101, 67, 33)))
        
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
            'grid_bg_light': (144, 238, 144),
            'grid_bg_dark': (34, 139, 34),
            'grid_lines': (139, 69, 19),
            'grid_border': (101, 67, 33),
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
        
        # Sistema de vida
        self.vida_maxima = 100
        self.vida_actual = 100
    
    def recibir_daño(self, daño):
        """Reduce la vida de la casa"""
        self.vida_actual = max(0, self.vida_actual - daño)
    
    def esta_destruida(self):
        """Verifica si la casa está destruida"""
        return self.vida_actual <= 0
    
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
        
        # Cuerpo de la casa
        canvas.create_rectangle(
            self.x, self.y + 12,
            self.x + self.size, self.y + self.size,
            fill=colors['body'], outline=colors['body']
        )
        
        # Techo triangular
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
        
        # Barra de vida
        if not self.is_invader:
            vida_percent = self.vida_actual / self.vida_maxima
            bar_width = self.size
            bar_height = 4
            bar_x = self.x
            bar_y = self.y + self.size + 3
            
            # Fondo rojo
            canvas.create_rectangle(
                bar_x, bar_y,
                bar_x + bar_width, bar_y + bar_height,
                fill='#cc0000',
                outline='#333333'
            )
            
            # Vida actual verde
            if vida_percent > 0:
                canvas.create_rectangle(
                    bar_x, bar_y,
                    bar_x + (bar_width * vida_percent), bar_y + bar_height,
                    fill='#00cc00',
                    outline=''
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
        
        # Cuerpo de la persona
        canvas.create_arc(
            self.x - 12, self.y,
            self.x + 12, self.y + 20,
            start=0, extent=180,
            outline=self.palette.user_icon_person,
            width=4, style='arc'
        )


class QuestionButton:
    def __init__(self, x, y, palette, presupuesto=0):
        self.x = x
        self.y = y
        self.palette = palette
        self.size = 45
        self.presupuesto = presupuesto
    
    def update_presupuesto(self, presupuesto):
        """Actualiza el presupuesto mostrado"""
        self.presupuesto = presupuesto
    
    def draw(self, canvas):
        half_size = self.size // 2
        
        # Fondo redondeado
        canvas.create_rectangle(
            self.x - half_size, self.y - half_size,
            self.x + half_size, self.y + half_size,
            fill=self.palette.question_bg,
            outline=self.palette.question_bg
        )
        
        # Mostrar presupuesto
        canvas.create_text(
            self.x, self.y,
            text=f"${self.presupuesto}",
            font=("Arial", 12, "bold"),
            fill=self.palette.question_text
        )


class TopRightButton:
    """Botón START"""
    def __init__(self, x, y, palette):
        self.x = x
        self.y = y
        self.palette = palette
        self.width = 80
        self.height = 40
        self.visible = True
    
    def draw(self, canvas):
        if not self.visible:
            return
        
        half_w = self.width // 2
        half_h = self.height // 2
        
        canvas.create_rectangle(
            self.x - half_w, self.y - half_h,
            self.x + half_w, self.y + half_h,
            fill='#00cc00',
            outline='#009900',
            width=3
        )
        
        canvas.create_text(
            self.x, self.y,
            text="START",
            font=("Arial", 14, "bold"),
            fill="white"
        )
    
    def hide(self):
        self.visible = False


class ElementButton:
    """Botón para seleccionar torres"""
    def __init__(self, x, y, element_type, palette, game):
        self.x = x
        self.y = y
        self.element_type = element_type
        self.palette = palette
        self.game = game
        self.size = 50
        
        self.config = {
            'sand': {'color': '#DEB887', 'icon': '⛰️', 'name': 'Arena', 'price': 100, 'class': RookArena},
            'rock': {'color': '#696969', 'icon': '🪨', 'name': 'Roca', 'price': 150, 'class': RookRoca},
            'water': {'color': '#4682B4', 'icon': '💧', 'name': 'Agua', 'price': 120, 'class': RookAgua},
            'fire': {'color': '#FF4500', 'icon': '🔥', 'name': 'Fuego', 'price': 200, 'class': RookFuego}
        }
    
    def draw(self, canvas):
        cfg = self.config[self.element_type]
        half = self.size // 2
        
        canvas.create_rectangle(
            self.x - half, self.y - half,
            self.x + half, self.y + half,
            fill=cfg['color'],
            outline='#333333',
            width=2
        )
        
        canvas.create_text(
            self.x, self.y - 5,
            text=cfg['icon'],
            font=("Arial", 20)
        )
        
        canvas.create_text(
            self.x, self.y + 15,
            text=f"${cfg['price']}",
            font=("Arial", 9, "bold"),
            fill="white"
        )
    
    def is_clicked(self, x, y):
        half = self.size // 2
        return (self.x - half <= x <= self.x + half and 
                self.y - half <= y <= self.y + half)
    
    def on_click(self):
        cfg = self.config[self.element_type]
        
        if self.game.presupuesto >= cfg['price']:
            print(f"💰 Seleccionaste Torre de {cfg['name']} (${cfg['price']})")
            self.game.esperando_colocacion = self.element_type
            self.game.torre_a_colocar = cfg
        else:
            messagebox.showwarning("Sin presupuesto", 
                f"Necesitas ${cfg['price']} para Torre de {cfg['name']}\n" +
                f"Tu presupuesto: ${self.game.presupuesto}")


class Grid:
    """Cuadrícula del juego"""
    def __init__(self, x, y, rows, cols, cell_size, palette):
        self.x = x
        self.y = y
        self.rows = rows
        self.cols = cols
        self.cell_size = cell_size
        self.palette = palette
        self.width = cols * cell_size
        self.height = rows * cell_size
        self.torres_grid = {}
    
    def draw(self, canvas):
        # Borde
        canvas.create_rectangle(
            self.x - 4, self.y - 4,
            self.x + self.width + 4, self.y + self.height + 4,
            fill=self.palette.grid_border,
            outline=self.palette.grid_border
        )
        
        # Celdas
        for row in range(self.rows):
            for col in range(self.cols):
                x1 = self.x + col * self.cell_size
                y1 = self.y + row * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                
                color = self.palette.grid_bg_light if (row + col) % 2 == 0 else self.palette.grid_bg_dark
                
                canvas.create_rectangle(
                    x1, y1, x2, y2,
                    fill=color,
                    outline=self.palette.grid_lines
                )
                
                self.draw_grass_texture(canvas, x1, y1, x2, y2)
        
        # Líneas del grid
        for col in range(self.cols + 1):
            x_pos = self.x + col * self.cell_size
            canvas.create_line(x_pos, self.y, x_pos, self.y + self.height,
                             fill=self.palette.grid_lines, width=2)
        
        for row in range(self.rows + 1):
            y_pos = self.y + row * self.cell_size
            canvas.create_line(self.x, y_pos, self.x + self.width, y_pos,
                             fill=self.palette.grid_lines, width=2)
        
        # Dibujar torres
        for (row, col), torre in self.torres_grid.items():
            self.draw_torre(canvas, torre, row, col)
    
    def draw_grass_texture(self, canvas, x1, y1, x2, y2):
        random.seed(int(x1 * y1))
        for _ in range(3):
            x_rand = random.randint(int(x1) + 5, int(x2) - 5)
            y_rand = random.randint(int(y1) + 5, int(y2) - 5)
            length = random.randint(3, 8)
            canvas.create_line(x_rand, y_rand, x_rand, y_rand + length,
                             fill=self.palette.grid_lines, width=1)
        random.seed()
    
    def draw_torre(self, canvas, torre, row, col):
        x = self.x + col * self.cell_size + self.cell_size // 2
        y = self.y + row * self.cell_size + self.cell_size // 2
        
        radius = 20
        canvas.create_oval(
            x - radius, y - radius,
            x + radius, y + radius,
            fill=torre.color,
            outline='#333333',
            width=2
        )
        
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
        
        canvas.create_rectangle(
            bar_x, bar_y,
            bar_x + bar_width, bar_y + bar_height,
            fill='#cc0000',
            outline='#333333'
        )
        
        if vida_percent > 0:
            canvas.create_rectangle(
                bar_x, bar_y,
                bar_x + (bar_width * vida_percent), bar_y + bar_height,
                fill='#00cc00',
                outline=''
            )
    
    def draw_avatares(self, canvas, avatares):
        """MÉTODO CORREGIDO: Usa get_color() y get_icono()"""
        for avatar in avatares:
            col, row = avatar.posicion
            x = self.x + col * self.cell_size + self.cell_size // 2
            y = self.y + row * self.cell_size + self.cell_size // 2
            
            radius = 15
            canvas.create_oval(
                x - radius, y - radius,
                x + radius, y + radius,
                fill=avatar.get_color(),  # ✅ CORREGIDO: usar método
                outline='#000000',
                width=2
            )
            
            canvas.create_text(
                x, y - 3,
                text=avatar.get_icono(),  # ✅ CORREGIDO: usar método
                font=("Arial", 14)
            )
            
            # Barra de vida
            vida_percent = avatar.vida / avatar.vida_maxima if avatar.vida_maxima > 0 else 0
            bar_width = 25
            bar_height = 3
            bar_x = x - bar_width // 2
            bar_y = y + radius + 2
            
            canvas.create_rectangle(
                bar_x, bar_y,
                bar_x + bar_width, bar_y + bar_height,
                fill='#cc0000',
                outline=''
            )
            
            if vida_percent > 0:
                canvas.create_rectangle(
                    bar_x, bar_y,
                    bar_x + (bar_width * vida_percent), bar_y + bar_height,
                    fill='#00cc00',
                    outline=''
                )
    
    def draw_proyectiles(self, canvas, proyectiles):
        for proyectil in proyectiles:
            if proyectil.activo:
                x, y = proyectil.posicion
                radius = 5
                canvas.create_oval(
                    x - radius, y - radius,
                    x + radius, y + radius,
                    fill=proyectil.color,
                    outline='#000000',
                    width=1
                )
    
    def draw_monedas(self, canvas, monedas):
        """Dibuja las monedas activas"""
        for moneda in monedas:
            if moneda.activa:
                col, row = moneda.posicion
                x = self.x + col * self.cell_size + self.cell_size // 2
                y = self.y + row * self.cell_size + self.cell_size // 2
                
                size = moneda.get_size()
                canvas.create_oval(
                    x - size, y - size,
                    x + size, y + size,
                    fill=moneda.get_color(),
                    outline='#000000',
                    width=2,
                    tags="moneda"
                )
                
                canvas.create_text(
                    x, y,
                    text=moneda.get_icono(),
                    font=("Arial", 14),
                    tags="moneda"
                )
    
    def get_cell_from_coords(self, x, y):
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
        self.torres_grid[(row, col)] = torre


class VillageGame(tk.Frame):
    """Clase principal del juego"""
    def __init__(self, parent, width=600, height=750, nivel="FACIL", frecuencias=None, initial_palette=None):
        super().__init__(parent, width=width, height=height)
        self.width = width
        self.height = height
        
        self.nivel = nivel
        self.frecuencias = frecuencias or {}
        self.presupuesto = 600
        self.gestor_rooks = GestorRooks()
        
        # Gestor de avatares
        self.gestor_avatares = GestorAvatares(grid_cols=5, nivel=nivel)
        
        # Sistema de puntos y monedas
        self.sistema_puntos = SistemaPuntos()
        self.sistema_monedas = SistemaMonedas(grid_cols=5, grid_rows=9)
        self.sistema_puntos.sistema_monedas = self.sistema_monedas
        self.gestor_avatares.sistema_puntos = self.sistema_puntos
        
        self.esperando_colocacion = None
        self.torre_a_colocar = None
        
        # Estado del juego
        self.juego_activo = False
        self.juego_terminado = False
        self.tiempo_inicio_juego = None
        
        self.palette = ColorPalette(initial_palette)
        
        self.canvas = Canvas(
            self,
            width=self.width,
            height=self.height,
            bg=self.palette.background,
            highlightthickness=0
        )
        self.canvas.pack()
        
        self.grid_cols = 5
        self.grid_rows = 9
        self.cell_size = 60
        grid_width = self.grid_cols * self.cell_size
        self.grid_x = (self.width - grid_width) // 2
        
        self.grid = Grid(self.grid_x, 100, self.grid_rows, self.grid_cols, 
                        self.cell_size, self.palette)
        
        # Crear casas
        self.safe_houses = []
        num_safe_houses = 5
        house_spacing = grid_width // (num_safe_houses + 1)
        house_y = 10
        
        for i in range(num_safe_houses):
            x_pos = self.grid_x + house_spacing * (i + 1) - 17
            self.safe_houses.append(House(x_pos, house_y, self.palette, is_invader=False))
        
        # UI
        self.user_icon = UserIcon(40, 30, self.palette)
        self.question_btn = QuestionButton(self.width - 40, 30, self.palette, self.presupuesto)
        
        grid_right_x = self.grid_x + self.grid.width
        grid_top_y = 100
        button_x = grid_right_x + 70
        button_y = grid_top_y + 20
        self.top_right_btn = TopRightButton(button_x, button_y, self.palette)
        
        # Botones de elementos
        self.element_buttons = []
        element_types = ['sand', 'rock', 'water', 'fire']
        element_x = button_x
        start_y = button_y + 110
        spacing = 70
        
        for i, element in enumerate(element_types):
            element_y = start_y + (i * spacing)
            self.element_buttons.append(ElementButton(element_x, element_y, element, self.palette, self))
        
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        
        if self.frecuencias:
            self.gestor_rooks.actualizar_frecuencias(self.frecuencias)
        
        self.draw()
        self.animate()
    
    def draw_zones(self):
        self.canvas.create_rectangle(
            self.grid_x - 8, 0, self.grid_x + self.grid_cols * self.cell_size + 8, 60,
            fill=self.palette.safe_zone_bg,
            outline=self.palette.safe_zone_bg,
            tags="zones"
        )
        
        self.canvas.create_rectangle(
            self.grid_x - 8, 690, self.grid_x + self.grid_cols * self.cell_size + 8, 750,
            fill=self.palette.invader_zone_bg,
            outline=self.palette.invader_zone_bg,
            tags="zones"
        )
    
    def draw(self):
        self.canvas.delete("all")
        self.canvas.configure(bg=self.palette.background)
        
        self.draw_zones()
        self.grid.draw(self.canvas)
        
        # Dibujar avatares
        self.grid.draw_avatares(self.canvas, self.gestor_avatares.get_avatares_activos())
        
        # Dibujar proyectiles
        self.grid.draw_proyectiles(self.canvas, self.gestor_rooks.proyectiles_activos)
        
        # Dibujar monedas
        tiempo_actual = time.time()
        monedas = self.sistema_monedas.get_monedas_activas(tiempo_actual)
        self.grid.draw_monedas(self.canvas, monedas)
        
        for house in self.safe_houses:
            house.draw(self.canvas)
        
        self.question_btn.update_presupuesto(self.presupuesto)
        self.user_icon.draw(self.canvas)
        self.question_btn.draw(self.canvas)
        self.top_right_btn.draw(self.canvas)
        
        for element_btn in self.element_buttons:
            element_btn.draw(self.canvas)
        
        if self.juego_activo:
            self.draw_stats()
    
    def animate(self):
        if self.juego_activo and not self.juego_terminado:
            tiempo_actual = time.time()
            
            self.gestor_rooks.update(tiempo_actual)
            self.gestor_avatares.actualizar(tiempo_actual, self.grid.torres_grid)
            self.sistema_monedas.update(tiempo_actual)
            
            self.gestor_avatares.verificar_colisiones_proyectiles(
                self.gestor_rooks.proyectiles_activos
            )
            
            self.verificar_avatares_en_casas()
            self.limpiar_torres_destruidas()
            self.verificar_fin_juego()
            
            self.draw()
        
        self.after(100, self.animate)
    
    def draw_stats(self):
        stats_avatares = self.gestor_avatares.get_estadisticas()
        stats_puntos = self.sistema_puntos.get_estadisticas()
        
        texto1 = f"👾: {stats_avatares['spawneados']} | 💀: {stats_avatares['eliminados']} | 🏠: {stats_avatares['llegaron_meta']} | ⚡: {stats_avatares['activos']}"
        
        progreso = int(stats_puntos['progreso_spawn'] * 100)
        texto2 = f"🎯 Puntos: {stats_puntos['puntos_totales']} | 💰 Próximo: {stats_puntos['puntos_para_spawn']}/30 ({progreso}%) | 💵 ${stats_puntos['dinero_spawneado']}"
        
        self.canvas.create_text(
            self.width // 2, 710,
            text=texto1,
            font=("Arial", 9, "bold"),
            fill="white"
        )
        
        self.canvas.create_text(
            self.width // 2, 730,
            text=texto2,
            font=("Arial", 9, "bold"),
            fill="#FFD700"
        )
    
    def verificar_avatares_en_casas(self):
        for avatar in self.gestor_avatares.get_avatares_activos():
            if avatar.posicion[1] == 0:
                col = avatar.posicion[0]
                for house in self.safe_houses:
                    house_col = int((house.x - self.grid_x + 17) / (self.grid.width / len(self.safe_houses)))
                    if abs(house_col - col) <= 0:
                        house.recibir_daño(avatar.ataque)
                        if house.esta_destruida():
                            print(f"   💥 ¡Casa destruida!")
    
    def limpiar_torres_destruidas(self):
        torres_a_eliminar = []
        for pos, torre in self.grid.torres_grid.items():
            if not torre.activa:
                torres_a_eliminar.append(pos)
        
        for pos in torres_a_eliminar:
            del self.grid.torres_grid[pos]
        
        self.gestor_rooks.eliminar_torres_destruidas()
    
    def verificar_fin_juego(self):
        casas_vivas = sum(1 for house in self.safe_houses if not house.esta_destruida())
        if casas_vivas == 0:
            self.terminar_juego(victoria=False)
            return
        
        stats = self.gestor_avatares.get_estadisticas()
        if stats['eliminados'] >= 50:
            self.terminar_juego(victoria=True)
    
    def terminar_juego(self, victoria):
        if self.juego_terminado:
            return
        
        self.juego_terminado = True
        self.gestor_avatares.detener()
        
        stats = self.gestor_avatares.get_estadisticas()
        stats_puntos = self.sistema_puntos.get_estadisticas()
        
        if victoria:
            titulo = "🎉 ¡VICTORIA!"
            mensaje = f"¡Has defendido tu aldea!\n\n"
            mensaje += f"Enemigos eliminados: {stats['eliminados']}\n"
            mensaje += f"Puntos: {stats_puntos['puntos_totales']}\n"
            mensaje += f"Dinero: ${stats_puntos['dinero_spawneado']}"
        else:
            titulo = "💀 DERROTA"
            mensaje = f"Tu aldea fue destruida...\n\n"
            mensaje += f"Enemigos eliminados: {stats['eliminados']}\n"
            mensaje += f"Puntos: {stats_puntos['puntos_totales']}"
        
        messagebox.showinfo(titulo, mensaje)
    
    def on_canvas_click(self, event):
        if self.juego_terminado:
            return
        
        if self.esperando_colocacion:
            cell = self.grid.get_cell_from_coords(event.x, event.y)
            if cell:
                row, col = cell
                if (row, col) not in self.grid.torres_grid:
                    self.colocar_torre(row, col)
                else:
                    messagebox.showinfo("Celda ocupada", "Ya hay una torre aquí")
            return
        
        # Recolectar moneda
        if self.juego_activo and not self.esperando_colocacion:
            cell = self.grid.get_cell_from_coords(event.x, event.y)
            if cell:
                row, col = cell
                dinero = self.sistema_monedas.intentar_recolectar(col, row)
                if dinero > 0:
                    self.presupuesto += dinero
                    self.draw()
                    return
        
        for btn in self.element_buttons:
            if btn.is_clicked(event.x, event.y):
                btn.on_click()
                return
        
        if self.top_right_btn.visible:
            x1 = self.top_right_btn.x - self.top_right_btn.width // 2
            y1 = self.top_right_btn.y - self.top_right_btn.height // 2
            x2 = self.top_right_btn.x + self.top_right_btn.width // 2
            y2 = self.top_right_btn.y + self.top_right_btn.height // 2
            
            if x1 <= event.x <= x2 and y1 <= event.y <= y2:
                self.on_top_right_button_pressed()
    
    def colocar_torre(self, row, col):
        if self.torre_a_colocar and self.presupuesto >= self.torre_a_colocar['price']:
            mapeo_frecuencias = {
                'sand': self.frecuencias.get("⛰️  TORRE DE ARENA", 5),
                'rock': self.frecuencias.get("🪨  TORRE DE ROCA", 5),
                'water': self.frecuencias.get("💧 TORRE DE AGUA", 5),
                'fire': self.frecuencias.get("🔥 TORRE DE FUEGO", 5)
            }
            
            frecuencia = mapeo_frecuencias.get(self.esperando_colocacion, 5)
            
            posicion = [
                self.grid_x + col * self.cell_size + self.cell_size // 2,
                100 + row * self.cell_size + self.cell_size // 2
            ]
            torre = self.torre_a_colocar['class'](posicion, frecuencia)
            
            self.gestor_rooks.torres.append(torre)
            self.grid.add_torre(torre, row, col)
            
            self.presupuesto -= self.torre_a_colocar['price']
            
            print(f"✅ Torre colocada | Presupuesto: ${self.presupuesto}")
            
            self.esperando_colocacion = None
            self.torre_a_colocar = None
            
            self.draw()
    
    def on_top_right_button_pressed(self):
        print("\n🎮 ¡JUEGO INICIADO!")
        print(f"Nivel: {self.nivel}")
        print(f"Presupuesto: ${self.presupuesto}")
        
        self.top_right_btn.hide()
        self.juego_activo = True
        self.tiempo_inicio_juego = time.time()
        
        self.gestor_avatares.iniciar()
        
        self.draw()
    
    def apply_new_palette(self, new_palette_dict):
        """Aplica una nueva paleta de colores al juego en tiempo real"""
        self.palette.update_palette(new_palette_dict)
        self.grid.palette = self.palette
        
        for house in self.safe_houses:
            house.palette = self.palette
        
        self.user_icon.palette = self.palette
        self.question_btn.palette = self.palette
        self.top_right_btn.palette = self.palette
        
        for element_btn in self.element_buttons:
            element_btn.palette = self.palette
        
        self.draw()


class VillageGameWindow:
    """Ventana del juego"""
    def __init__(self, nivel="FACIL", frecuencias=None, initial_palette=None):
        self.root = tk.Tk()
        self.root.title("Avatars vs Rooks")
        self.root.geometry("600x750")
        self.root.resizable(False, False)
        
        self.game = VillageGame(self.root, 600, 750, nivel, frecuencias, initial_palette)
        self.game.pack()
    
    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    frecuencias_prueba = {
        "⛰️  TORRE DE ARENA": 3,
        "🪨  TORRE DE ROCA": 4,
        "💧 TORRE DE AGUA": 2,
        "🔥 TORRE DE FUEGO": 5
    }
    game_window = VillageGameWindow(nivel="FACIL", frecuencias=frecuencias_prueba)
    game_window.run()