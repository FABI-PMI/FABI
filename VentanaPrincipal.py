"""
Sistema de juego de aldeas con cuadricula.
Version completamente en Tkinter (sin Pygame).
Con sistema de puntos y monedas integrado.
VERSION CON SPRITES ANIMADOS: Los avatares alternan entre imagenes de paso
VERSION CON SONIDO: Las torres reproducen sonidos al impactar
"""
import io, base64
import os
import tkinter as tk
from tkinter import Canvas, messagebox
import random
import time
import threading
from PIL import Image, ImageTk

# Importaciones con manejo de errores
try:
    from ptsSalon import pts as pts_salon
except ImportError:
    print("⚠️ No se pudo importar ptsSalon, usando valores por defecto")
    def pts_salon(*args, **kwargs):
        return 0

try:
    from ventana_personalizacion import get_popularidad
except (ImportError, AttributeError) as e:
    print(f"⚠️ No se pudo importar get_popularidad: {e}")
    print("   Usando función por defecto")
    def get_popularidad(*args, **kwargs):
        return 50  # Valor por defecto

try:
    from bpm_live import get_bpm_snapshot
except ImportError:
    print("⚠️ No se pudo importar get_bpm_snapshot, usando valores por defecto")
    def get_bpm_snapshot():
        return 60

try:
    from Login import cargar_usuarios, guardar_usuarios
except ImportError:
    print("⚠️ No se pudo importar Login, usando funciones por defecto")
    def cargar_usuarios():
        return {}
    def guardar_usuarios(*args, **kwargs):
        pass

from RooksClass import RookArena, RookRoca, RookAgua, RookFuego, GestorRooks
from AvatarClass import GestorAvatares
from MoneySystem import SistemaPuntos, SistemaMonedas

# Importar adaptador de control (opcional, con fallback)
try:
    from Controladapter import ControlAdapter, ControlState
    CONTROL_DISPONIBLE = True
    print("✅ Módulo de control importado correctamente")
except ImportError as e:
    print(f"⚠️ No se pudo importar ControlAdapter: {e}")
    print("   El juego funcionará solo con teclado/ratón")
    CONTROL_DISPONIBLE = False
    ControlAdapter = None
    ControlState = None


# ═══════════════════════════════════════════════════════════════════════════
# SISTEMA DE SONIDO PARA TORRES
# ═══════════════════════════════════════════════════════════════════════════

class SoundManager:
    """Gestor de sonidos para las torres"""
    
    def __init__(self):
        """Inicializa el gestor de sonidos"""
        self.sonidos = {}
        self.pygame_disponible = False
        self.cargar_sonidos()
    
    def cargar_sonidos(self):
        """Carga los archivos de sonido de las torres"""
        try:
            import pygame
            pygame.mixer.init()
            self.pygame_disponible = True
            print("✅ Sistema de sonido inicializado con Pygame")
        except ImportError:
            print("⚠️ Pygame no disponible. Los sonidos no funcionarán.")
            print("   Instala: pip install pygame")
            return
        
        # Mapeo de tipos de torre a archivos de sonido
        mapeo_sonidos = {
            'Arena': 'arena_sound.mp3',
            'Roca': 'piedra_sound.mp3',
            'Agua': 'agua_sound.mp3',
            'Fuego': 'fuego_sound.mp3'
        }
        
        extensiones = ['.mp3', '.wav', '.ogg']
        
        for tipo, archivo_base in mapeo_sonidos.items():
            sonido_cargado = False
            
            # Intentar con el nombre exacto primero
            if os.path.exists(archivo_base):
                if self._cargar_sonido_archivo(tipo, archivo_base):
                    sonido_cargado = True
            
            # Si no se cargó, intentar con variaciones
            if not sonido_cargado:
                nombre_sin_ext = archivo_base.rsplit('.', 1)[0]
                for ext in extensiones:
                    path = f"{nombre_sin_ext}{ext}"
                    if os.path.exists(path):
                        if self._cargar_sonido_archivo(tipo, path):
                            sonido_cargado = True
                            break
            
            if not sonido_cargado:
                print(f"⚠️ No se encontró sonido para torre: {tipo} ({archivo_base})")
    
    def _cargar_sonido_archivo(self, tipo, path):
        """Carga un archivo de sonido específico"""
        try:
            if self.pygame_disponible:
                import pygame
                sonido = pygame.mixer.Sound(path)
                self.sonidos[tipo] = sonido
                print(f"✅ Sonido cargado: {path} -> {tipo}")
                return True
        except Exception as e:
            print(f"⚠️ Error cargando {path}: {e}")
            return False
        
        return False
    
    def reproducir(self, tipo_torre):
        """
        Reproduce el sonido de impacto de una torre
        
        Args:
            tipo_torre: Tipo de torre ('Arena', 'Roca', 'Agua', 'Fuego')
        """
        if not self.pygame_disponible or tipo_torre not in self.sonidos:
            return
        
        try:
            sonido = self.sonidos[tipo_torre]
            sonido.play()
        except Exception as e:
            print(f"⚠️ Error reproduciendo sonido {tipo_torre}: {e}")
    
    def detener_todos(self):
        """Detiene todos los sonidos en reproducción"""
        try:
            if self.pygame_disponible:
                import pygame
                pygame.mixer.stop()
        except Exception as e:
            print(f"⚠️ Error deteniendo sonidos: {e}")


# Instancia global del gestor de sonidos
_sound_manager = None

def get_sound_manager():
    """Obtiene la instancia global del gestor de sonidos"""
    global _sound_manager
    if _sound_manager is None:
        _sound_manager = SoundManager()
    return _sound_manager


# ═══════════════════════════════════════════════════════════════════════════
# CLASES DEL JUEGO
# ═══════════════════════════════════════════════════════════════════════════


class ColorPalette:
    """
    Recibe una paleta de colores completa generada externamente.
    Este modulo NO genera colores, solo los organiza y distribuye.
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
        
        # Cuadricula
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


class SpriteManager:
    """Gestor de sprites para los avatares"""
    def __init__(self):
        self.sprites = {}
        self.photo_images = {}
        self.sprite_size = 55
        self.projectile_size = 40  # Más grande para mejor visibilidad
        self.weapon_size = 60  # Tamaño de una casilla completa
        self.collision_size = 40
        self.cargar_sprites()
        self.cargar_proyectiles()
        self.cargar_armas()
        self.cargar_colisiones()
        self.cargar_torres()  # ✅ NUEVO: Cargar sprites de torres
    
    def cargar_sprites(self):
        """Carga todas las imagenes de sprites disponibles"""
        tipos = ['leñador', 'flechador', 'escudero', 'canibal']
        extensiones = ['.png', '.jpg', '.jpeg', '.gif']
        
        for tipo in tipos:
            self.sprites[tipo] = []
            for frame in [0, 1]:
                imagen_cargada = False
                for ext in extensiones:
                    path = f"{tipo}{frame}{ext}"
                    if os.path.exists(path):
                        try:
                            img = Image.open(path).convert("RGBA")
                            img = img.resize((self.sprite_size, self.sprite_size), Image.LANCZOS)
                            self.sprites[tipo].append(img)
                            imagen_cargada = True
                            print(f"✅ Sprite cargado: {path}")
                            break
                        except Exception as e:
                            print(f"⚠️ Error cargando {path}: {e}")
                
                if not imagen_cargada:
                    print(f"⚠️ No se encontro sprite: {tipo}{frame}")
                    self.sprites[tipo].append(None)
    
    def cargar_proyectiles(self):
        """Carga imagenes de proyectiles"""
        self.proyectiles = {}
        extensiones = ['.png', '.jpg', '.jpeg', '.gif']
        
        for ext in extensiones:
            path = f"flecha{ext}"
            if os.path.exists(path):
                try:
                    img = Image.open(path).convert("RGBA")
                    img = img.resize((self.projectile_size, self.projectile_size), Image.LANCZOS)
                    self.proyectiles['flecha'] = img
                    print(f"✅ Proyectil cargado: {path}")
                    break
                except Exception as e:
                    print(f"⚠️ Error cargando {path}: {e}")
        
        for ext in extensiones:
            path = f"escudo{ext}"
            if os.path.exists(path):
                try:
                    img = Image.open(path).convert("RGBA")
                    img = img.resize((self.projectile_size, self.projectile_size), Image.LANCZOS)
                    self.proyectiles['escudo'] = img
                    print(f"✅ Proyectil cargado: {path}")
                    break
                except Exception as e:
                    print(f"⚠️ Error cargando {path}: {e}")
    
    def cargar_armas(self):
        """Carga imagenes de armas para ataques melee"""
        self.armas = {}
        extensiones = ['.png', '.jpg', '.jpeg', '.gif']
        
        self.armas['hacha'] = []
        for frame in [0, 1]:
            imagen_cargada = False
            for ext in extensiones:
                path = f"hacha{frame}{ext}"
                if os.path.exists(path):
                    try:
                        img = Image.open(path).convert("RGBA")
                        img = img.resize((self.weapon_size, self.weapon_size), Image.LANCZOS)
                        self.armas['hacha'].append(img)
                        imagen_cargada = True
                        print(f"✅ Arma cargada: {path}")
                        break
                    except Exception as e:
                        print(f"⚠️ Error cargando {path}: {e}")
            if not imagen_cargada:
                self.armas['hacha'].append(None)
        
        self.armas['palo'] = []
        for frame in [0, 1]:
            imagen_cargada = False
            for ext in extensiones:
                path = f"palo{frame}{ext}"
                if os.path.exists(path):
                    try:
                        img = Image.open(path).convert("RGBA")
                        img = img.resize((self.weapon_size, self.weapon_size), Image.LANCZOS)
                        self.armas['palo'].append(img)
                        imagen_cargada = True
                        print(f"✅ Arma cargada: {path}")
                        break
                    except Exception as e:
                        print(f"⚠️ Error cargando {path}: {e}")
            if not imagen_cargada:
                self.armas['palo'].append(None)
    
    def cargar_colisiones(self):
        """Carga imagenes de animacion de colision"""
        self.colisiones = []
        extensiones = ['.png', '.jpg', '.jpeg', '.gif']
        
        for frame in [0, 1]:
            imagen_cargada = False
            for ext in extensiones:
                path = f"colision{frame}{ext}"
                if os.path.exists(path):
                    try:
                        img = Image.open(path).convert("RGBA")
                        img = img.resize((self.collision_size, self.collision_size), Image.LANCZOS)
                        self.colisiones.append(img)
                        imagen_cargada = True
                        print(f"✅ Colision cargada: {path}")
                        break
                    except Exception as e:
                        print(f"⚠️ Error cargando {path}: {e}")
            if not imagen_cargada:
                self.colisiones.append(None)
    
    def cargar_torres(self):
        """✅ NUEVO: Carga imagenes de torres (Rooks)"""
        self.torres = {}
        extensiones = ['.png', '.jpg', '.jpeg', '.gif']
        
        # Mapeo de archivos a tipos de torre
        mapeo_torres = {
            'Arena': 'R01',    # Torre de Arena -> R01.png
            'Roca': 'R02',     # Torre de Roca -> R02.png
            'Fuego': 'R03',    # Torre de Fuego -> R03.png
            'Agua': 'R04'      # Torre de Agua -> R04.png
        }
        
        for tipo, archivo in mapeo_torres.items():
            imagen_cargada = False
            for ext in extensiones:
                path = f"{archivo}{ext}"
                if os.path.exists(path):
                    try:
                        img = Image.open(path).convert("RGBA")
                        # Ajustar al tamaño de la celda (60x60)
                        img = img.resize((60, 60), Image.LANCZOS)
                        self.torres[tipo] = img
                        print(f"✅ Torre cargada: {path} -> {tipo}")
                        imagen_cargada = True
                        break
                    except Exception as e:
                        print(f"⚠️ Error cargando {path}: {e}")
            
            if not imagen_cargada:
                print(f"⚠️ No se encontró sprite para torre: {tipo}")
                self.torres[tipo] = None
    
    def get_proyectil_sprite(self, tipo_avatar, canvas):
        """Obtiene el sprite del proyectil segun el tipo de avatar"""
        tipo_normalizado = tipo_avatar.lower().strip()
        
        if 'flechador' in tipo_normalizado:
            sprite_key = 'flecha'
        elif 'escudero' in tipo_normalizado:
            sprite_key = 'escudo'
        else:
            return None
        
        if sprite_key not in self.proyectiles:
            return None
        
        pil_img = self.proyectiles[sprite_key]
        cache_key = (sprite_key, 'proyectil', id(canvas))
        if cache_key not in self.photo_images:
            self.photo_images[cache_key] = ImageTk.PhotoImage(pil_img, master=canvas)
        
        return self.photo_images[cache_key]
    
    def get_arma_sprite(self, tipo_avatar, frame_index, canvas):
        """Obtiene el sprite del arma para ataques melee"""
        tipo_normalizado = tipo_avatar.lower().strip()
        
        if 'leñador' in tipo_normalizado:
            arma_key = 'hacha'
        elif 'canibal' in tipo_normalizado:
            arma_key = 'palo'
        else:
            return None
        
        if arma_key not in self.armas or not self.armas[arma_key]:
            return None
        
        if frame_index >= len(self.armas[arma_key]):
            return None
        
        pil_img = self.armas[arma_key][frame_index]
        if pil_img is None:
            return None
        
        cache_key = (arma_key, frame_index, id(canvas))
        if cache_key not in self.photo_images:
            self.photo_images[cache_key] = ImageTk.PhotoImage(pil_img, master=canvas)
        
        return self.photo_images[cache_key]
    
    def get_colision_sprite(self, frame_index, canvas):
        """Obtiene el sprite de la animacion de colision"""
        if not self.colisiones or frame_index >= len(self.colisiones):
            return None
        
        pil_img = self.colisiones[frame_index]
        if pil_img is None:
            return None
        
        cache_key = ('colision', frame_index, id(canvas))
        if cache_key not in self.photo_images:
            self.photo_images[cache_key] = ImageTk.PhotoImage(pil_img, master=canvas)
        
        return self.photo_images[cache_key]
    
    def get_sprite(self, tipo, frame_index, canvas):
        """Obtiene el PhotoImage del sprite para un canvas especifico"""
        tipo_normalizado = tipo.lower().strip()
        
        if 'leñador' in tipo_normalizado or '🪓' in tipo:
            tipo_key = 'leñador'
        elif 'flechador' in tipo_normalizado or '🏹' in tipo:
            tipo_key = 'flechador'
        elif 'escudero' in tipo_normalizado or '🛡' in tipo:
            tipo_key = 'escudero'
        elif 'canibal' in tipo_normalizado or '🗡' in tipo or '💹' in tipo:
            tipo_key = 'canibal'
        else:
            print(f"⚠️ Tipo de avatar no reconocido: '{tipo}'")
            return None
        
        if tipo_key not in self.sprites:
            return None
        
        frames = self.sprites[tipo_key]
        if not frames or frame_index >= len(frames):
            return None
        
        pil_img = frames[frame_index]
        if pil_img is None:
            return None
        
        cache_key = (tipo_key, frame_index, id(canvas))
        if cache_key not in self.photo_images:
            self.photo_images[cache_key] = ImageTk.PhotoImage(pil_img, master=canvas)
        
        return self.photo_images[cache_key]


class House:
    def __init__(self, x, y, palette, is_invader=False):
        self.x = x
        self.y = y
        self.palette = palette
        self.is_invader = is_invader
        self.size = 35
    
    def get_colors(self):
        """Obtiene los colores segun el tipo de casa"""
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
        
        canvas.create_rectangle(
            self.x, self.y + 12,
            self.x + self.size, self.y + self.size,
            fill=colors['body'], outline=colors['body']
        )
        
        roof_points = [
            self.x, self.y + 12,
            self.x + self.size // 2, self.y,
            self.x + self.size, self.y + 12
        ]
        canvas.create_polygon(roof_points, fill=colors['roof'], outline=colors['roof'])
        
        canvas.create_rectangle(
            self.x + 12, self.y + 22,
            self.x + 23, self.y + 40,
            fill=colors['door'], outline=colors['door']
        )
        
        canvas.create_rectangle(
            self.x + 5, self.y + 16,
            self.x + 14, self.y + 25,
            fill=colors['window'], outline=colors['window']
        )


class UserIcon:
    def __init__(self, x, y, palette, size=45):
        self.x = x
        self.y = y
        self.palette = palette
        self.size = size
        self._pil_circular = None
        self._photo_tk = None

    def _circularize(self, pil_img, size):
        pil_img = pil_img.convert("RGBA").resize((size, size), Image.LANCZOS)
        from PIL import ImageDraw, Image as PILImage
        mask = PILImage.new("L", (size, size), 0)
        d = ImageDraw.Draw(mask)
        d.ellipse((0, 0, size, size), fill=255)
        pil_img.putalpha(mask)
        return pil_img

    def load_from_username(self, username):
        """Carga foto_perfil_b64 del usuario (si existe) y la deja lista en PIL."""
        self._pil_circular = None
        self._photo_tk = None
        if not username:
            return
        try:
            usuarios = cargar_usuarios()
            datos = usuarios.get(username, {}) if isinstance(usuarios, dict) else {}
            foto_b64 = datos.get("foto_perfil_b64", "")
            if foto_b64:
                img_data = base64.b64decode(foto_b64)
                from PIL import Image as PILImage
                pil_img = PILImage.open(io.BytesIO(img_data))
                self._pil_circular = self._circularize(pil_img, self.size)
        except Exception:
            self._pil_circular = None

    def draw(self, canvas):
        radius = self.size // 2
        canvas.create_oval(
            self.x - radius, self.y - radius,
            self.x + radius, self.y + radius,
            fill=self.palette.user_icon_bg,
            outline=self.palette.user_icon_border,
            width=3
        )

        if self._pil_circular is not None:
            self._photo_tk = ImageTk.PhotoImage(self._pil_circular, master=canvas)
            canvas.create_image(self.x, self.y, image=self._photo_tk)
        else:
            canvas.create_oval(
                self.x - 8, self.y - 13,
                self.x + 8, self.y + 3,
                fill=self.palette.user_icon_person,
                outline=self.palette.user_icon_person
            )
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
        
        canvas.create_rectangle(
            self.x - half_size, self.y - half_size,
            self.x + half_size, self.y + half_size,
            fill=self.palette.question_bg,
            outline=self.palette.question_bg
        )
        
        canvas.create_text(
            self.x, self.y,
            text=f"${self.presupuesto}",
            font=("Arial", 12, "bold"),
            fill=self.palette.question_text
        )


class TopRightButton:
    """Boton START"""
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
    """Boton para seleccionar torres"""
    def __init__(self, x, y, element_type, palette, game):
        self.x = x
        self.y = y
        self.element_type = element_type
        self.palette = palette
        self.game = game
        self.size = 50
        self.selected = False  # Si está seleccionada
        self.affordable = True  # Si se puede pagar
        
        self.config = {
            'sand': {'color': '#DEB887', 'icon': '⛰️', 'name': 'Arena', 'price': 100, 'class': RookArena},
            'rock': {'color': '#696969', 'icon': '🪨', 'name': 'Roca', 'price': 150, 'class': RookRoca},
            'water': {'color': '#4682B4', 'icon': '💧', 'name': 'Agua', 'price': 120, 'class': RookAgua},
            'fire': {'color': '#FF4500', 'icon': '🔥', 'name': 'Fuego', 'price': 200, 'class': RookFuego}
        }
    
    def draw(self, canvas):
        """Dibuja el botón con indicadores visuales mejorados"""
        cfg = self.config[self.element_type]
        half = self.size // 2
        
        # Actualizar si se puede pagar
        self.affordable = self.game.presupuesto >= cfg['price']
        
        # Determinar colores según estado
        if not self.affordable:
            # No se puede pagar - Gris oscuro con borde rojo
            bg_color = '#404040'
            border_color = '#FF0000'
            border_width = 3
            text_color = '#FF6666'
        elif self.selected:
            # Seleccionada - Borde verde brillante y fondo más claro
            bg_color = cfg['color']
            border_color = '#00FF00'
            border_width = 4
            text_color = 'white'
        else:
            # Normal - Color original
            bg_color = cfg['color']
            border_color = '#333333'
            border_width = 2
            text_color = 'white'
        
        # Rectángulo principal
        canvas.create_rectangle(
            self.x - half, self.y - half,
            self.x + half, self.y + half,
            fill=bg_color,
            outline=border_color,
            width=border_width
        )
        
        # Si está seleccionada, agregar un brillo interno
        if self.selected:
            canvas.create_rectangle(
                self.x - half + 3, self.y - half + 3,
                self.x + half - 3, self.y + half - 3,
                fill='',
                outline='#90EE90',
                width=2
            )
        
        # Icono
        canvas.create_text(
            self.x, self.y - 5,
            text=cfg['icon'],
            font=("Arial", 20)
        )
        
        # Precio con color según estado
        canvas.create_text(
            self.x, self.y + 15,
            text=f"${cfg['price']}",
            font=("Arial", 9, "bold"),
            fill=text_color
        )
        
        # Si no se puede pagar, mostrar X roja
        if not self.affordable:
            canvas.create_text(
                self.x - half + 8, self.y - half + 8,
                text="✗",
                font=("Arial", 12, "bold"),
                fill="#FF0000"
            )

    def is_clicked(self, x, y):
        half = self.size // 2
        return (self.x - half <= x <= self.x + half and 
                self.y - half <= y <= self.y + half)
    
    def on_click(self):
        """Maneja el click en el botón"""
        cfg = self.config[self.element_type]
        
        if self.game.presupuesto >= cfg['price']:
            # Puede pagar - seleccionar
            print(f"🎯 Torre de {cfg['name']} seleccionada (${cfg['price']})")
            
            # Deseleccionar otros botones
            for btn in self.game.element_buttons:
                btn.selected = False
            
            # Seleccionar este
            self.selected = True
            self.game.esperando_colocacion = self.element_type
            self.game.torre_a_colocar = cfg
            self.game.draw()  # Redibujar para mostrar selección
        else:
            # No puede pagar - solo mensaje en consola (sin popup molesto)
            faltante = cfg['price'] - self.game.presupuesto
            print(f"❌ Presupuesto insuficiente para {cfg['name']}")
            print(f"   Necesitas: ${cfg['price']} | Tienes: ${self.game.presupuesto} | Faltan: ${faltante}")

class Grid:
    """Cuadricula del juego"""
    def __init__(self, x, y, rows, cols, cell_size, palette, sprite_manager):
        self.x = x
        self.y = y
        self.rows = rows
        self.cols = cols
        self.cell_size = cell_size
        self.palette = palette
        self.sprite_manager = sprite_manager
        self.width = cols * cell_size
        self.height = rows * cell_size
        self.torres_grid = {}
        self.animation_frame = 0
        self.animation_speed = 0.3
        self.last_animation_time = time.time()
        
        # Sistema de animaciones de colision
        self.colisiones_activas = []
        
        # ═══════════════════════════════════════════════════════════════════════
        # SISTEMA DE IMÁGENES DE MONEDAS
        # ═══════════════════════════════════════════════════════════════════════
        self.moneda_images = {}
        self.cargar_imagenes_monedas()
    
    def cargar_imagenes_monedas(self):
        """Carga y cachea las imágenes de las monedas"""
        from PIL import Image, ImageTk
        import os
        
        # Mapeo de valores a archivos de imagen
        valores_monedas = [10, 20, 30, 50]
        
        for valor in valores_monedas:
            archivo = f"{valor}.png"
            if os.path.exists(archivo):
                try:
                    # Cargar imagen
                    img = Image.open(archivo)
                    # Redimensionar según el tamaño de la moneda
                    # Las monedas más valiosas son un poco más grandes
                    if valor == 10:
                        size = 30
                    elif valor == 20:
                        size = 36
                    elif valor == 30:
                        size = 40
                    else:  # 50
                        size = 44
                    
                    img = img.resize((size, size), Image.Resampling.LANCZOS)
                    # Convertir a PhotoImage
                    photo = ImageTk.PhotoImage(img)
                    self.moneda_images[valor] = photo
                    print(f"✅ Imagen de moneda cargada: ${valor}")
                except Exception as e:
                    print(f"⚠️ Error cargando imagen {archivo}: {e}")
            else:
                print(f"⚠️ Archivo no encontrado: {archivo}")
        
        if not self.moneda_images:
            print("⚠️ No se cargaron imágenes de monedas, se usarán emojis")
    
    def agregar_colision(self, x, y):
        """Agrega una nueva animacion de colision"""
        self.colisiones_activas.append({
            'x': x,
            'y': y,
            'frame': 0,
            'tiempo_inicio': time.time()
        })
    
    def actualizar_colisiones(self):
        """Actualiza y limpia las animaciones de colision"""
        tiempo_actual = time.time()
        colisiones_a_eliminar = []
        
        for i, colision in enumerate(self.colisiones_activas):
            tiempo_transcurrido = tiempo_actual - colision['tiempo_inicio']
            
            if tiempo_transcurrido < 0.1:
                colision['frame'] = 0
            elif tiempo_transcurrido < 0.2:
                colision['frame'] = 1
            else:
                colisiones_a_eliminar.append(i)
        
        for i in reversed(colisiones_a_eliminar):
            self.colisiones_activas.pop(i)
    
    def draw_colisiones(self, canvas):
        """Dibuja las animaciones de colision activas"""
        for colision in self.colisiones_activas:
            sprite = self.sprite_manager.get_colision_sprite(colision['frame'], canvas)
            if sprite:
                canvas.create_image(colision['x'], colision['y'], image=sprite)
    
    def draw(self, canvas):
        canvas.create_rectangle(
            self.x - 4, self.y - 4,
            self.x + self.width + 4, self.y + self.height + 4,
            fill=self.palette.grid_border,
            outline=self.palette.grid_border
        )
        
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
        
        for col in range(self.cols + 1):
            x_pos = self.x + col * self.cell_size
            canvas.create_line(x_pos, self.y, x_pos, self.y + self.height,
                             fill=self.palette.grid_lines, width=2)
        
        for row in range(self.rows + 1):
            y_pos = self.y + row * self.cell_size
            canvas.create_line(self.x, y_pos, self.x + self.width, y_pos,
                             fill=self.palette.grid_lines, width=2)
        
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
        """✅ MODIFICADO: Dibuja una torre usando su sprite correspondiente"""
        x = self.x + col * self.cell_size + self.cell_size // 2
        y = self.y + row * self.cell_size + self.cell_size // 2
        
        # Obtener el sprite de la torre según su tipo
        sprite_img = None
        if hasattr(self.sprite_manager, 'torres') and torre.tipo in self.sprite_manager.torres:
            sprite_img = self.sprite_manager.torres[torre.tipo]
        
        if sprite_img:
            # Dibujar el sprite de la torre
            photo = ImageTk.PhotoImage(sprite_img, master=canvas)
            # Guardar referencia para evitar que se borre
            if not hasattr(self.sprite_manager, 'photo_images_torres'):
                self.sprite_manager.photo_images_torres = {}
            self.sprite_manager.photo_images_torres[f'torre_{row}_{col}'] = photo
            
            canvas.create_image(x, y, image=photo, tags=f"torre_{row}_{col}")
        else:
            # Si no hay sprite, dibujar representación simple con ícono
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
        bar_y = y + 25  # Un poco más abajo para no tapar el sprite
        
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
    
    def update_animation_frame(self):
        """Actualiza el frame de animacion basado en el tiempo"""
        current_time = time.time()
        if current_time - self.last_animation_time >= self.animation_speed:
            self.animation_frame = 1 - self.animation_frame
            self.last_animation_time = current_time
    
    def draw_avatares(self, canvas, avatares):
        """Dibuja los avatares en el grid con sprites animados"""
        self.update_animation_frame()
        
        for avatar in avatares:
            col, row = avatar.posicion
            x = self.x + col * self.cell_size + self.cell_size // 2
            y = self.y + row * self.cell_size + self.cell_size // 2
            
            sprite = self.sprite_manager.get_sprite(avatar.nombre, self.animation_frame, canvas)
            
            if sprite:
                canvas.create_image(x, y, image=sprite)
            else:
                radius = 15
                canvas.create_oval(
                    x - radius, y - radius,
                    x + radius, y + radius,
                    fill=avatar.get_color(),
                    outline='#000000',
                    width=2
                )
                
                canvas.create_text(
                    x, y - 3,
                    text=avatar.get_icono(),
                    font=("Arial", 14)
                )
            
            # Dibujar arma melee si está atacando
            if hasattr(avatar, 'esta_atacando_melee') and avatar.esta_atacando_melee:
                frame_arma = avatar.get_frame_arma()
                if frame_arma is not None:
                    arma_sprite = self.sprite_manager.get_arma_sprite(avatar.nombre, frame_arma, canvas)
                    if arma_sprite:
                        # Posicionar el arma SOBRE el avatar atacante (no sobre el objetivo)
                        # Usar las coordenadas del avatar actual, no de la torre adelante
                        arma_x = x  # Mismo x que el avatar
                        arma_y = y - 35  # Arriba del avatar (35 píxeles para el arma más grande)
                        canvas.create_image(arma_x, arma_y, image=arma_sprite)
            
            vida_percent = avatar.vida / avatar.vida_maxima if avatar.vida_maxima > 0 else 0
            bar_width = 25
            bar_height = 3
            bar_x = x - bar_width // 2
            bar_y = y + 18
            
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
        """Dibuja los proyectiles activos con sprites personalizados"""
        for proyectil in proyectiles:
            if proyectil.activo:
                x, y = proyectil.posicion
                
                sprite = None
                if hasattr(proyectil, 'tipo') and proyectil.tipo:
                    sprite = self.sprite_manager.get_proyectil_sprite(proyectil.tipo, canvas)
                
                if sprite:
                    canvas.create_image(x, y, image=sprite)
                else:
                    radius = 5
                    canvas.create_oval(
                        x - radius, y - radius,
                        x + radius, y + radius,
                        fill=proyectil.color,
                        outline='#000000',
                        width=1
                    )
    
    def draw_monedas(self, canvas, monedas):
        """Dibuja las monedas activas usando imágenes"""
        for moneda in monedas:
            if moneda.activa:
                col, row = moneda.posicion
                x = self.x + col * self.cell_size + self.cell_size // 2
                y = self.y + row * self.cell_size + self.cell_size // 2
                
                # Intentar usar imagen primero
                if moneda.valor in self.moneda_images:
                    # Usar imagen de moneda
                    canvas.create_image(
                        x, y,
                        image=self.moneda_images[moneda.valor],
                        tags="moneda"
                    )
                else:
                    # Fallback: usar el sistema antiguo con emojis
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
    def __init__(self, parent, width=600, height=750, nivel="FACIL", frecuencias=None, initial_palette=None, current_username=None):
        super().__init__(parent, width=width, height=height)
        self.width = width
        self.height = height
        self.current_username = current_username
        self.nivel = nivel
        self.frecuencias = frecuencias or {}
        self.presupuesto = 350
        self.gestor_rooks = GestorRooks()
        
        self.sprite_manager = SpriteManager()
        
        self.gestor_avatares = GestorAvatares(grid_cols=5, nivel=nivel)
        
        self.sistema_puntos = SistemaPuntos()
        self.sistema_monedas = SistemaMonedas(grid_cols=5, grid_rows=9)
        self.sistema_puntos.sistema_monedas = self.sistema_monedas
        self.gestor_avatares.sistema_puntos = self.sistema_puntos
        
        self.gestor_avatares.grid_ref = None
        
        self.esperando_colocacion = None
        self.torre_a_colocar = None
        
        self.juego_activo = False
        self.juego_terminado = False
        self.tiempo_inicio_juego = None
        self.ultimo_tiempo = time.time()
        
        # ═══════════════════════════════════════════════════════════════════════
        # CONTROLES DE TECLADO
        # ═══════════════════════════════════════════════════════════════════════
        self.cursor_fila = 4  # Centro del grid (9 filas -> índice 4)
        self.cursor_columna = 2  # Centro del grid (5 columnas -> índice 2)
        self.modo_menu = False  # Si está en modo navegación de botones
        self.boton_seleccionado = 0  # Índice del botón seleccionado en modo menú

        # ═══════════════════════════════════════════════════════════════════════
        # CONTROL INALÁMBRICO (Raspberry Pi Pico W)
        # ═══════════════════════════════════════════════════════════════════════
        self.control_adapter = None
        self.control_conectado = False
        self.control_habilitado = CONTROL_DISPONIBLE  # Si el módulo está disponible
        
        # Variables para control de movimiento del joystick
        self.ultimo_movimiento_joystick = 0
        self.intervalo_movimiento = 0.2  # Segundos entre movimientos

        
        # Cache para evitar calcular popularidad/tempo en cada frame
        self.ultimo_calculo_stats = 0
        self.tempo_cache = 0.0
        self.popularidad_cache = 0.0
        
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
                        self.cell_size, self.palette, self.sprite_manager)
        
        self.gestor_avatares.grid_ref = self.grid
        
        self.safe_houses = []
        num_safe_houses = 5
        house_spacing = grid_width // (num_safe_houses + 1)
        house_y = 10
        
        for i in range(num_safe_houses):
            x_pos = self.grid_x + house_spacing * (i + 1) - 17
            self.safe_houses.append(House(x_pos, house_y, self.palette, is_invader=False))
        
        self.user_icon = UserIcon(40, 30, self.palette)
        self.user_icon.load_from_username(self.current_username)
        self.question_btn = QuestionButton(self.width - 40, 30, self.palette, self.presupuesto)
        
        grid_right_x = self.grid_x + self.grid.width
        grid_top_y = 100
        button_x = grid_right_x + 70
        button_y = grid_top_y + 20
        self.top_right_btn = TopRightButton(button_x, button_y, self.palette)
        
        self.element_buttons = []
        element_types = ['sand', 'rock', 'water', 'fire']
        element_x = button_x
        start_y = button_y + 110
        spacing = 70
        
        for i, element in enumerate(element_types):
            element_y = start_y + (i * spacing)
            self.element_buttons.append(ElementButton(element_x, element_y, element, self.palette, self))
        
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        
        # ═══════════════════════════════════════════════════════════════════════
        # BIND DE CONTROLES DE TECLADO
        # ═══════════════════════════════════════════════════════════════════════
        self.canvas.bind("<KeyPress>", self.on_key_press)
        self.canvas.focus_set()  # Permitir que el canvas reciba eventos de teclado
        
        if self.frecuencias:
            self.gestor_rooks.actualizar_frecuencias(self.frecuencias)
        
        self.btn_salon_fama = tk.Button(
            self, text="Salon de Fama",
            command=self.abrir_salon_de_la_fama,
            bg=self.palette.safe_houses_roof,
            fg="white",
            font=("Arial", 11, "bold"),
            relief="raised",
            bd=2,
            cursor="hand2",
            padx=12,
            pady=10
        )

        if self.control_habilitado:
            self.after(1500, self._conectar_control_inicial)  # 1.5s para que la red se estabilice
            self.after(100, self._procesar_cola_control)  # Iniciar procesamiento de cola
        
        self.draw()
        self.animate()
    
    def abrir_salon_de_la_fama(self):
        top = tk.Toplevel(self)
        top.transient(self.winfo_toplevel())
        try:
            from SalonFama import SalonFama
            SalonFama(top, top_limit=10)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el Salon de la Fama.\n{e}")

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
    
    
    def draw_control_icon(self):
        """Dibuja un icono de gamepad/control mejorado"""
        if not self.control_habilitado:
            return
        
        # Posición: a la izquierda del icono de moneda
        icon_x = self.width - 80
        icon_y = 30
        
        # Color según estado
        if self.control_conectado:
            # Conectado: Gamepad verde con brillo
            body_color = "#4CAF50"      # Verde
            accent_color = "#66BB6A"    # Verde claro
            shadow_color = "#2E7D32"    # Verde oscuro
            dot_color = "#00FF00"       # Verde brillante
        else:
            # Desconectado: Gamepad gris
            body_color = "#757575"      # Gris
            accent_color = "#9E9E9E"    # Gris claro
            shadow_color = "#424242"    # Gris oscuro
            dot_color = "#BDBDBD"       # Gris claro
        
        # Sombra del gamepad
        self.canvas.create_oval(
            icon_x - 14, icon_y - 9,
            icon_x + 14, icon_y + 11,
            fill=shadow_color, outline=""
        )
        
        # Cuerpo principal del gamepad
        self.canvas.create_oval(
            icon_x - 15, icon_y - 10,
            icon_x + 15, icon_y + 10,
            fill=body_color, outline=accent_color, width=2
        )
        
        # D-Pad (izquierda)
        dpad_x = icon_x - 8
        dpad_y = icon_y
        dpad_size = 2
        
        # D-Pad vertical
        self.canvas.create_rectangle(
            dpad_x - 1, dpad_y - dpad_size - 1,
            dpad_x + 1, dpad_y + dpad_size + 1,
            fill=accent_color, outline=""
        )
        # D-Pad horizontal
        self.canvas.create_rectangle(
            dpad_x - dpad_size - 1, dpad_y - 1,
            dpad_x + dpad_size + 1, dpad_y + 1,
            fill=accent_color, outline=""
        )
        
        # Botones (derecha) - 4 botones en rombo
        btn_x = icon_x + 8
        btn_y = icon_y
        btn_radius = 1.5
        
        # Botón arriba
        self.canvas.create_oval(
            btn_x - btn_radius, btn_y - 4 - btn_radius,
            btn_x + btn_radius, btn_y - 4 + btn_radius,
            fill=accent_color, outline=""
        )
        # Botón abajo
        self.canvas.create_oval(
            btn_x - btn_radius, btn_y + 4 - btn_radius,
            btn_x + btn_radius, btn_y + 4 + btn_radius,
            fill=accent_color, outline=""
        )
        # Botón izquierda
        self.canvas.create_oval(
            btn_x - 4 - btn_radius, btn_y - btn_radius,
            btn_x - 4 + btn_radius, btn_y + btn_radius,
            fill=accent_color, outline=""
        )
        # Botón derecha
        self.canvas.create_oval(
            btn_x + 4 - btn_radius, btn_y - btn_radius,
            btn_x + 4 + btn_radius, btn_y + btn_radius,
            fill=accent_color, outline=""
        )
        
        # Joysticks (dos pequeños círculos)
        # Joystick izquierdo
        self.canvas.create_oval(
            icon_x - 6, icon_y + 4,
            icon_x - 2, icon_y + 8,
            fill=shadow_color, outline=""
        )
        # Joystick derecho
        self.canvas.create_oval(
            icon_x + 2, icon_y + 4,
            icon_x + 6, icon_y + 8,
            fill=shadow_color, outline=""
        )
        
        # Indicador de conexión (LED)
        if self.control_conectado:
            # LED verde brillante cuando conectado
            self.canvas.create_oval(
                icon_x - 2, icon_y - 7,
                icon_x + 2, icon_y - 3,
                fill=dot_color, outline=""
            )
            # Brillo del LED
            self.canvas.create_oval(
                icon_x - 1, icon_y - 6,
                icon_x + 1, icon_y - 4,
                fill="#FFFFFF", outline=""
            )

    def _conectar_control_inicial(self):
        """Intenta conectar el control al iniciar con reintentos automáticos"""
        if self.control_conectado:
            return
        
        # Inicializar contador de reintentos si no existe
        if not hasattr(self, '_intentos_conexion'):
            self._intentos_conexion = 0
            self._max_intentos = 10  # Máximo 10 intentos
            self._delay_entre_intentos = 2000  # 2 segundos entre intentos
        
        self._intentos_conexion += 1
        print(f"🔌 Intento de conexión {self._intentos_conexion}/{self._max_intentos}...")
        
        import threading
        def conectar_async():
            try:
                # Conectar en thread secundario
                exito = self.conectar_control()
                
                if exito:
                    print("✅ ¡Control conectado exitosamente!")
                    self._intentos_conexion = 0  # Resetear contador
                else:
                    # Programar reintento si no se alcanzó el máximo
                    if self._intentos_conexion < self._max_intentos:
                        print(f"⏳ Reintentando en {self._delay_entre_intentos/1000}s...")
                        # Usar variable para que el main loop maneje el reintento
                        self._necesita_reintento = True
                    else:
                        print("⚠️ Control no disponible después de varios intentos")
                        print("   Usando mouse/teclado. Reconecta WiFi y reinicia el juego.")
                        
            except Exception as e:
                print(f"❌ Error: {e}")
                # Reintentar si hay error de red
                if self._intentos_conexion < self._max_intentos:
                    print(f"⏳ Reintentando en {self._delay_entre_intentos/1000}s...")
                    try:
                        self.after(self._delay_entre_intentos, self._conectar_control_inicial)
                    except:
                        pass
        
        thread = threading.Thread(target=conectar_async, daemon=True)
        thread.start()

    def conectar_control(self):
        """Conecta con el control"""
        if not self.control_habilitado:
            return False
        
        if self.control_adapter and self.control_adapter.is_connected():
            return True
        
        try:
            self.control_adapter = ControlAdapter()
            self.control_adapter.on_state_update = self._on_control_update
            conectado = self.control_adapter.connect()
            
            if conectado:
                self.control_conectado = True
                # NO usar self.after aquí - se ejecuta desde thread secundario
                # El procesamiento de cola ya se inicia en __init__
                return True
            return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    

    def _procesar_cola_control(self):
        """Procesa eventos del control desde la cola (thread-safe)"""
        try:
            # DEBUG: Mostrar estado cada 5 segundos
            if not hasattr(self, '_ultimo_debug_print'):
                self._ultimo_debug_print = 0
            import time as t
            if t.time() - self._ultimo_debug_print > 5:
                self._ultimo_debug_print = t.time()
                adapter_ok = self.control_adapter is not None
                conectado = self.control_adapter.is_connected() if adapter_ok else False
                cola_size = self.control_adapter.state_queue.qsize() if adapter_ok and hasattr(self.control_adapter, 'state_queue') else 0
                print(f"🔍 DEBUG: adapter={adapter_ok}, conectado={conectado}, cola={cola_size}, control_conectado={self.control_conectado}")
            
            # Manejar reintentos de conexión si es necesario
            if hasattr(self, '_necesita_reintento') and self._necesita_reintento:
                self._necesita_reintento = False
                self.after(self._delay_entre_intentos, self._conectar_control_inicial)
            
            # Verificar si el adapter existe y está conectado
            if self.control_adapter:
                # Sincronizar estado de conexión
                adapter_conectado = self.control_adapter.is_connected()
                
                if adapter_conectado != self.control_conectado:
                    # Estado cambió - actualizar y redibujar
                    self.control_conectado = adapter_conectado
                    if adapter_conectado:
                        print("🎮 Control activo - procesando inputs")
                    self.draw()
                
                # Procesar cola si está conectado
                if adapter_conectado and hasattr(self.control_adapter, 'process_queue'):
                    self.control_adapter.process_queue()
                    
        except Exception as e:
            print(f"⚠️ Error en procesar_cola: {e}")
        
        # Programar próxima ejecución (cada 16ms ~ 60fps)
        if self.control_habilitado:
            self.after(16, self._procesar_cola_control)
    def _on_control_update(self, state):
        """Callback del control"""
        # DEBUG: Mostrar que se recibió un estado
        if not hasattr(self, '_ultimo_callback_print'):
            self._ultimo_callback_print = 0
        import time as t
        if t.time() - self._ultimo_callback_print > 2:
            self._ultimo_callback_print = t.time()
            print(f"📥 Estado recibido: joystick={state.joystick_dir}, btns=A:{state.btn_a} B:{state.btn_b} C:{state.btn_c}")
        # Control funciona siempre, no solo cuando juego_activo
        # if not self.juego_activo:
        #     return
        
        t = time.time()
        if t - self.ultimo_movimiento_joystick >= self.intervalo_movimiento:
            if state.joystick_dir != "neutro":
                self._mover_cursor_control(state.joystick_dir)
                self.ultimo_movimiento_joystick = t
                self.after(0, self.draw)
        
        if state.get_button_press("joystick"):
            self.after(0, self._forzar_disparo_torre_control)
        if state.get_button_press("a"):
            self.after(0, self._recoger_todas_monedas)
        if state.get_button_press("b"):
            self.after(0, self.abrir_salon_de_la_fama)
        if state.get_button_press("c"):
            self.after(0, lambda: self._colocar_torre_control("water"))
        if state.get_button_press("d"):
            self.after(0, lambda: self._colocar_torre_control("rock"))
        if state.get_button_press("e"):
            self.after(0, lambda: self._colocar_torre_control("sand"))
        if state.get_button_press("f"):
            self.after(0, lambda: self._colocar_torre_control("fire"))
    
    def _mover_cursor_control(self, dir):
        """Mueve cursor"""
        if dir == "arriba" and self.cursor_fila > 0:
            self.cursor_fila -= 1
        elif dir == "abajo" and self.cursor_fila < self.grid_rows - 1:
            self.cursor_fila += 1
        elif dir == "izquierda" and self.cursor_columna > 0:
            self.cursor_columna -= 1
        elif dir == "derecha" and self.cursor_columna < self.grid_cols - 1:
            self.cursor_columna += 1
    
    def _seleccionar_torre_control(self, tipo):
        """Selecciona torre (sin colocar)"""
        for btn in self.element_buttons:
            if btn.element_type == tipo:
                btn.on_click()
                self.draw()
                break
    
    def _colocar_torre_control(self, tipo):
        """Selecciona Y coloca torre automáticamente donde está el cursor"""
        # Buscar el botón del tipo de torre
        btn_torre = None
        for btn in self.element_buttons:
            if btn.element_type == tipo:
                btn_torre = btn
                break
        
        if not btn_torre:
            print(f"❌ Tipo de torre '{tipo}' no encontrado")
            return
        
        cfg = btn_torre.config[tipo]
        
        # Verificar presupuesto
        if self.presupuesto < cfg['price']:
            faltante = cfg['price'] - self.presupuesto
            print(f"❌ Sin presupuesto para {cfg['name']} (${cfg['price']})")
            print(f"   Tienes: ${self.presupuesto} | Faltan: ${faltante}")
            return
        
        # Verificar que la casilla esté vacía
        row, col = self.cursor_fila, self.cursor_columna
        if (row, col) in self.grid.torres_grid:
            print(f"❌ Ya hay una torre en ({col}, {row})")
            return
        
        # Seleccionar la torre
        for btn in self.element_buttons:
            btn.selected = False
        btn_torre.selected = True
        self.esperando_colocacion = tipo
        self.torre_a_colocar = cfg
        
        # Colocar inmediatamente
        self.colocar_torre(row, col)
        print(f"🏗️ Torre {cfg['name']} colocada en ({col}, {row})")
    
    def _forzar_disparo_torre_control(self):
        """Fuerza disparo de la torre bajo el cursor"""
        row, col = self.cursor_fila, self.cursor_columna
        
        # Verificar si hay torre
        if (row, col) not in self.grid.torres_grid:
            print(f"❌ No hay torre en ({col}, {row}) para disparar")
            return
        
        torre = self.grid.torres_grid[(row, col)]
        
        try:
            # Calcular posición de la torre
            posicion_torre = [
                self.grid_x + col * self.cell_size + self.cell_size // 2,
                100 + row * self.cell_size + self.cell_size // 2
            ]
            
            tiempo_actual = time.time()
            
            # Resetear cooldown para forzar disparo
            if hasattr(torre, 'ultimo_disparo'):
                torre.ultimo_disparo = 0
            
            # Disparar
            if hasattr(torre, 'disparar'):
                proyectil = torre.disparar(tiempo_actual, posicion_torre)
                if proyectil:
                    print(f"💥 ¡Disparo forzado! Torre en ({col}, {row})")
                    self.draw()
                else:
                    print(f"⚠️ Torre en ({col}, {row}) no pudo disparar")
            else:
                print(f"⚠️ Torre sin método disparar")
        except Exception as e:
            print(f"❌ Error al forzar disparo: {e}")
    
    def _recoger_todas_monedas(self):
        """Recoge todas las monedas del tablero con botón A"""
        monedas_recogidas = 0
        dinero_total = 0
        
        for row in range(self.grid_rows):
            for col in range(self.grid_cols):
                # Usar el método correcto: intentar_recolectar(col, row)
                dinero = self.sistema_monedas.intentar_recolectar(col, row)
                if dinero > 0:
                    self.presupuesto += dinero
                    dinero_total += dinero
                    monedas_recogidas += 1
        
        if monedas_recogidas > 0:
            print(f"💰 Recogidas {monedas_recogidas} monedas (+${dinero_total}) | Total: ${self.presupuesto}")
            self.draw()

    def draw(self):
        self.canvas.delete("all")
        self.canvas.configure(bg=self.palette.background)
        
        self.draw_zones()
        self.grid.draw(self.canvas)
        
        self.grid.draw_avatares(self.canvas, self.gestor_avatares.get_avatares_activos())
        
        proyectiles_todos = []
        proyectiles_todos += self.gestor_rooks.get_todos_proyectiles()
        proyectiles_todos += self.gestor_avatares.get_todos_proyectiles()
        self.grid.draw_proyectiles(self.canvas, proyectiles_todos)

        self.grid.actualizar_colisiones()
        self.grid.draw_colisiones(self.canvas)

        tiempo_actual = time.time()
        monedas = self.sistema_monedas.get_monedas_activas(tiempo_actual)
        self.grid.draw_monedas(self.canvas, monedas)
        
        for house in self.safe_houses:
            house.draw(self.canvas)
        
        self.question_btn.update_presupuesto(self.presupuesto)
        self.user_icon.draw(self.canvas)
        self.question_btn.draw(self.canvas)

        # Icono de control (junto a la moneda)
        self.draw_control_icon()
        self.top_right_btn.draw(self.canvas)
        
        self.canvas.create_window(
            70, 115,
            window=self.btn_salon_fama,
            width=self.top_right_btn.width + 40,
            height=self.top_right_btn.height,
            anchor="center"
        )

        for element_btn in self.element_buttons:
            element_btn.draw(self.canvas)
        
        # ═══════════════════════════════════════════════════════════════════════
        # INDICADOR VISUAL DEL CURSOR DE TECLADO
        # ═══════════════════════════════════════════════════════════════════════
        if not self.modo_menu:
            # Calcular posición del cursor en píxeles
            cursor_x = self.grid_x + self.cursor_columna * self.cell_size
            cursor_y = 100 + self.cursor_fila * self.cell_size
            
            # Dibujar rectángulo resaltado en la celda del cursor (borde grueso cyan)
            self.canvas.create_rectangle(
                cursor_x, cursor_y,
                cursor_x + self.cell_size, cursor_y + self.cell_size,
                outline='#00FFFF',  # Cyan brillante
                width=4,
                tags="cursor"
            )
            
            # Dibujar un pequeño indicador en el centro de la celda
            center_x = cursor_x + self.cell_size // 2
            center_y = cursor_y + self.cell_size // 2
            
            # Círculo pequeño en el centro
            self.canvas.create_oval(
                center_x - 5, center_y - 5,
                center_x + 5, center_y + 5,
                fill='#00FFFF',
                outline='#FFFFFF',
                width=2,
                tags="cursor"
            )
        
        # Indicador de modo menú
        if self.modo_menu:
            # Resaltar el botón seleccionado en modo menú
            if self.boton_seleccionado == 0:
                # Resaltar botón Salón de Fama (izquierda)
                # El botón está en self.btn_salon_fama
                # Posición aproximada: x=70, y=115
                x_center = 70
                y_center = 115
                box_width = self.top_right_btn.width + 40
                box_height = self.top_right_btn.height
                
                x1 = x_center - box_width // 2 - 5
                y1 = y_center - box_height // 2 - 5
                x2 = x_center + box_width // 2 + 5
                y2 = y_center + box_height // 2 + 5
                
                self.canvas.create_rectangle(
                    x1, y1, x2, y2,
                    outline='#FFFF00',
                    width=4,
                    tags="menu_selection"
                )
                
            elif self.boton_seleccionado == 1:
                # Resaltar botón START (derecha)
                if self.top_right_btn.visible:
                    x1 = self.top_right_btn.x - self.top_right_btn.width // 2 - 5
                    y1 = self.top_right_btn.y - self.top_right_btn.height // 2 - 5
                    x2 = self.top_right_btn.x + self.top_right_btn.width // 2 + 5
                    y2 = self.top_right_btn.y + self.top_right_btn.height // 2 + 5
                    self.canvas.create_rectangle(
                        x1, y1, x2, y2,
                        outline='#FFFF00',
                        width=4,
                        tags="menu_selection"
                    )
            
            # Mostrar texto de modo menú
            self.canvas.create_text(
                self.width // 2, 680,
                text="🎮 MODO MENÚ: A ← Salón | START → D | ENTER: Activar | W/S: Salir",
                font=("Arial", 9, "bold"),
                fill="#FFFF00",
                tags="menu_mode"
            )
        else:
            # Mostrar controles cuando no está en modo menú
            self.canvas.create_text(
                self.width // 2, 680,
                text="⌨️ WASD: Mover | 1-4: Torre | Enter: Colocar | H: Dinero | G: Disparar | Tab: Menú",
                font=("Arial", 9, "bold"),
                fill="#AAAAAA",
                tags="keyboard_hints"
            )
        
        # Mostrar stats durante el juego
        if self.juego_activo:
            self.draw_stats()
        else:
            # Antes del juego, mostrar valores en 0
            self.canvas.create_text(
                self.width // 2, 710,
                text="⏱️ Tiempo: 0:00",
                font=("Arial", 11, "bold"),
                fill="white"
            )
            self.canvas.create_text(
                self.width // 2, 730,
                text="🏆 Puntos: 0",
                font=("Arial", 11, "bold"),
                fill="#FFD700"
            )
    
    def animate(self):
        """Actualizacion completa del juego con proyectiles de avatares"""
        if self.juego_activo and not self.juego_terminado:
            tiempo_actual = time.time()
            dt = tiempo_actual - self.ultimo_tiempo
            self.ultimo_tiempo = tiempo_actual
            
            grid_config = {
                'x': self.grid_x,
                'y': 100,
                'cell_size': self.cell_size,
                'rows': self.grid_rows
            }
            
            self.gestor_rooks.actualizar(dt, tiempo_actual, grid_config)
            
            self.gestor_avatares.actualizar(dt, self.grid.torres_grid, grid_config)
            
            proyectiles_torres = self.gestor_rooks.get_todos_proyectiles()
            self.gestor_avatares.verificar_colisiones_proyectiles(proyectiles_torres)
            
            self.sistema_monedas.update(tiempo_actual)
            
            self.verificar_avatares_en_casas()
            self.limpiar_torres_destruidas()
            self.verificar_fin_juego()
            
            self.draw()
        
        self.after(16, self.animate)
    
    def draw_stats(self):
        """Muestra solo tiempo y puntos calculados con ptsSalonFama"""
        # Calcular tiempo transcurrido
        if self.tiempo_inicio_juego:
            tiempo_transcurrido = time.time() - self.tiempo_inicio_juego
            minutos = int(tiempo_transcurrido // 60)
            segundos = int(tiempo_transcurrido % 60)
            texto_tiempo = f"⏱️ Tiempo: {minutos:02d}:{segundos:02d}"
        else:
            texto_tiempo = "⏱️ Tiempo: 0:00"
        
        # Actualizar caché de tempo/popularidad solo cada segundo (evitar spam de warnings)
        tiempo_actual = time.time()
        if tiempo_actual - self.ultimo_calculo_stats >= 1.0:
            self.ultimo_calculo_stats = tiempo_actual
            
            # Calcular tempo
            try:
                tempo = float(get_bpm_snapshot(4.0))
                self.tempo_cache = tempo if tempo > 0 else 0.0
            except Exception:
                self.tempo_cache = 0.0
            
            # Calcular popularidad
            try:
                pop = get_popularidad()
                self.popularidad_cache = float(pop) if pop is not None else 0.0
            except Exception:
                self.popularidad_cache = 0.0
        
        # Usar valores cacheados
        tempo = self.tempo_cache
        popularidad = self.popularidad_cache
        
        stats = self.gestor_avatares.get_estadisticas()
        stats_puntos = self.sistema_puntos.get_estadisticas()
        
        avatars_matados = int(stats.get('eliminados', 0))
        puntos_avatar = float(stats_puntos.get('puntos_totales', 0))
        limite_maximo = 9999.0
        
        puntos_salon_fama = pts_salon(tempo, popularidad, avatars_matados, puntos_avatar, limite_maximo)
        
        texto_puntos = f"🏆 Puntos: {int(puntos_salon_fama)}"
        
        # Dibujar tiempo
        self.canvas.create_text(
            self.width // 2, 710,
            text=texto_tiempo,
            font=("Arial", 11, "bold"),
            fill="white"
        )
        
        # Dibujar puntos
        self.canvas.create_text(
            self.width // 2, 730,
            text=texto_puntos,
            font=("Arial", 11, "bold"),
            fill="#FFD700"
        )
    
    def verificar_avatares_en_casas(self):
        """Método simplificado - las casas ya no reciben daño"""
        pass
    
    def limpiar_torres_destruidas(self):
        torres_a_eliminar = []
        for pos, torre in self.grid.torres_grid.items():
            if not torre.activa:
                # CRÍTICO: Desactivar todos los proyectiles de esta torre (sin sonido)
                for proyectil in torre.proyectiles:
                    proyectil.desactivar(por_impacto=False)  # ✅ Sin sonido al destruir torre
                torre.proyectiles.clear()
                torres_a_eliminar.append(pos)
        
        for pos in torres_a_eliminar:
            del self.grid.torres_grid[pos]
        
        self.gestor_rooks.eliminar_torres_destruidas()
    
    def verificar_fin_juego(self):
        """Verifica las condiciones de fin de juego"""
        stats = self.gestor_avatares.get_estadisticas()
        
        # PERDER: Si algún avatar pasó arriba
        if stats['llegaron_meta'] > 0:
            self.terminar_juego(victoria=False, razon="avatares_pasaron")
            return
        
        # GANAR: 60 segundos sin que ningún avatar haya pasado
        if self.tiempo_inicio_juego:
            tiempo_transcurrido = time.time() - self.tiempo_inicio_juego
            
            # Si han pasado 60 segundos Y NO ha pasado ningún avatar
            if tiempo_transcurrido >= 60:
                self.terminar_juego(victoria=True)
    
    def _actualizar_pts_salon(self, username: str, nuevo_pts: float):
        try:
            usuarios = cargar_usuarios()
            if not isinstance(usuarios, dict):
                usuarios = {}
        except Exception:
            usuarios = {}

        if username not in usuarios or not isinstance(usuarios[username], dict):
            usuarios[username] = {}

        actual = float(usuarios[username].get('pts', 0) or 0)
        mejor = max(actual, float(nuevo_pts))
        usuarios[username]['pts'] = int(round(mejor))
        guardar_usuarios(usuarios)

    def terminar_juego(self, victoria, razon=None):
        if self.juego_terminado:
            return

        self.juego_terminado = True
        self.gestor_avatares.detener()

        stats = self.gestor_avatares.get_estadisticas()
        stats_puntos = self.sistema_puntos.get_estadisticas()

        if victoria:
            # Calcular ptsSalonFama
            try:
                tempo = float(get_bpm_snapshot(4.0))
            except Exception:
                tempo = 0.0

            try:
                pop = get_popularidad()
                popularidad = float(pop) if pop is not None else 0.0
            except Exception:
                popularidad = 0.0

            avatars_matados = int(stats.get('eliminados', 0))
            puntos_avatar = float(stats_puntos.get('puntos_totales', 0))
            limite_maximo = 9999.0

            puntaje_final = pts_salon(tempo, popularidad, avatars_matados, puntos_avatar, limite_maximo)

            titulo = "🎉 VICTORIA!"
            mensaje = f"¡Sobreviviste 60 segundos sin dejar pasar ningún avatar!\n\n"
            mensaje += f"🏆 Puntos Salón de la Fama: {int(puntaje_final)}\n"
            mensaje += f"💀 Enemigos eliminados: {avatars_matados}"

            if getattr(self, 'current_username', None):
                try:
                    self._actualizar_pts_salon(self.current_username, puntaje_final)
                    print(f"🏆 Salon de la Fama actualizado para @{self.current_username}: {puntaje_final:.0f} pts")
                except Exception as e:
                    print(f"⚠ No se pudo actualizar Salon de la Fama: {e}")
            else:
                print("ℹ No se actualizo Salon de la Fama (username desconocido).")

            self.after(10, lambda: self._abrir_animacion(
                ("win0", "win1", "win2"),
                f"¡Defendiste la aldea!\n{int(puntaje_final)} puntos"
            ))
            return
        else:
            # Calcular ptsSalonFama incluso en derrota
            try:
                tempo = float(get_bpm_snapshot(4.0))
            except Exception:
                tempo = 0.0

            try:
                pop = get_popularidad()
                popularidad = float(pop) if pop is not None else 0.0
            except Exception:
                popularidad = 0.0

            avatars_matados = int(stats.get('eliminados', 0))
            puntos_avatar = float(stats_puntos.get('puntos_totales', 0))
            limite_maximo = 9999.0

            puntaje_final = pts_salon(tempo, popularidad, avatars_matados, puntos_avatar, limite_maximo)
            
            titulo = "💀 DERROTA"
            
            # Mensaje específico según la razón de derrota
            if razon == "avatares_pasaron":
                avatares_pasados = stats.get('llegaron_meta', 0)
                mensaje = f"¡{avatares_pasados} avatar(es) pasaron a tu aldea!\n\n"
            else:
                mensaje = f"Tu aldea fue destruida.\n\n"
            
            mensaje += f"🏆 Puntos Salón de la Fama: {int(puntaje_final)}\n"
            mensaje += f"💀 Enemigos eliminados: {avatars_matados}"
            
            # Actualizar pts incluso en derrota
            if getattr(self, 'current_username', None):
                try:
                    self._actualizar_pts_salon(self.current_username, puntaje_final)
                    print(f"🏆 Salon de la Fama actualizado para @{self.current_username}: {puntaje_final:.0f} pts")
                except Exception as e:
                    print(f"⚠ No se pudo actualizar Salon de la Fama: {e}")
            
            self.after(10, lambda: self._abrir_animacion(
                ("fail0", "fail1", "fail2"),
                f"Tu aldea fue dominada.\n{int(puntaje_final)} puntos"
            ))
        return
    
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
                    messagebox.showinfo("Celda ocupada", "Ya hay una torre aqui")
            return
        
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
    
    def on_key_press(self, event):
        """
        Maneja los controles de teclado del juego.
        
        Controles:
        - 1, 2, 3, 4: Seleccionar tipo de torre
        - Enter: Colocar torre / Activar botón en modo menú
        - H: Recoger dinero de la casilla actual
        - G: Disparar manualmente la torre en la posición actual
        - Tab: Cambiar entre modo juego y modo menú
        
        NOTA: El movimiento del cursor (WASD) ha sido reemplazado por el joystick del control inalámbrico.
        """
        if self.juego_terminado:
            return
        
        tecla = event.keysym.lower()
        
        # TAB: Cambiar entre modo juego y modo menú
        if tecla == 'tab':
            self.modo_menu = not self.modo_menu
            if self.modo_menu:
                self.boton_seleccionado = 0  # 0 = Salón de Fama, 1 = START
                print("🎮 Modo Menú activado")
                print("   A: Salón de Fama | D: START | ENTER: Seleccionar | W/S: Volver")
            else:
                print("🎮 Modo Juego activado - Usa WASD para moverte")
            self.draw()
            return
        
        # ═══════════════════════════════════════════════════════════════════════
        # MODO MENÚ: Solo Salón de Fama y START
        # ═══════════════════════════════════════════════════════════════════════
        if self.modo_menu:
            # W o S: Salir del modo menú
            if tecla in ['w', 's']:
                self.modo_menu = False
                print("🎮 Modo Juego activado - Usa WASD para moverte")
                self.draw()
                return
            
            # A: Ir a Salón de Fama (izquierda)
            elif tecla == 'a':
                self.boton_seleccionado = 0  # Salón de Fama
                print("📍 Salón de Fama seleccionado")
                self.draw()
            
            # D: Ir a START (derecha)
            elif tecla == 'd':
                self.boton_seleccionado = 1  # START
                print("📍 START seleccionado")
                self.draw()
            
            # ENTER: Activar botón seleccionado
            elif tecla == 'return':
                if self.boton_seleccionado == 0:
                    # Salón de Fama
                    print("🏆 Abriendo Salón de la Fama...")
                    self.abrir_salon_de_la_fama()
                    self.modo_menu = False
                elif self.boton_seleccionado == 1:
                    # START
                    if self.top_right_btn.visible:
                        print("▶️ Iniciando juego desde teclado...")
                        self.on_top_right_button_pressed()
                        self.modo_menu = False
                    else:
                        print("⚠️ El juego ya está en marcha")
                self.draw()
            
            return  # En modo menú, no procesar otros controles
        
        # ═══════════════════════════════════════════════════════════════════════
        # MODO JUEGO: Movimiento del cursor y acciones
        # ═══════════════════════════════════════════════════════════════════════
        
        # WASD: ELIMINADO - El control del joystick toma su lugar
        # El movimiento del cursor ahora es exclusivo del control inalámbrico
        
        # 1, 2, 3, 4: Seleccionar tipo de torre
        elif tecla in ['1', '2', '3', '4']:
            tipo_index = int(tecla) - 1
            if tipo_index < len(self.element_buttons):
                print(f"🎯 Seleccionando torre tipo {tecla}...")
                self.element_buttons[tipo_index].on_click()
                self.draw()
        
        # ENTER: Colocar torre en la posición del cursor
        elif tecla == 'return':
            if self.esperando_colocacion:
                row, col = self.cursor_fila, self.cursor_columna
                if (row, col) not in self.grid.torres_grid:
                    print(f"🏰 Colocando torre en ({col}, {row})...")
                    self.colocar_torre(row, col)
                else:
                    print(f"❌ Ya hay una torre en ({col}, {row})")
                    messagebox.showinfo("Celda ocupada", "Ya hay una torre aqui")
            else:
                print("⚠️ No hay torre seleccionada. Presiona 1, 2, 3 o 4 primero")
        
        # H: Recoger dinero
        elif tecla == 'h':
            if self.juego_activo and not self.esperando_colocacion:
                row, col = self.cursor_fila, self.cursor_columna
                dinero = self.sistema_monedas.intentar_recolectar(col, row)
                if dinero > 0:
                    self.presupuesto += dinero
                    print(f"💰 Recogiste ${dinero}! Presupuesto: ${self.presupuesto}")
                    self.draw()
                else:
                    print(f"❌ No hay dinero en ({col}, {row})")
        
        # G: Disparar manualmente
        elif tecla == 'g':
            if self.juego_activo:
                row, col = self.cursor_fila, self.cursor_columna
                # Buscar si hay una torre en esta posición
                if (row, col) in self.grid.torres_grid:
                    torre = self.grid.torres_grid[(row, col)]
                    
                    # DISPARO MANUAL FORZADO - SIEMPRE DISPARA
                    try:
                        # Calcular posición de la torre en píxeles
                        posicion_torre = [
                            self.grid_x + col * self.cell_size + self.cell_size // 2,
                            100 + row * self.cell_size + self.cell_size // 2
                        ]
                        
                        tiempo_actual = time.time()
                        
                        # ✅ FORZAR DISPARO: Resetear cooldown ANTES de disparar
                        if hasattr(torre, 'ultimo_disparo'):
                            # Resetear cooldown para forzar disparo inmediato
                            torre.ultimo_disparo = 0
                        
                        # Ahora disparar (cooldown está reseteado, SIEMPRE dispara)
                        if hasattr(torre, 'disparar'):
                            proyectil = torre.disparar(tiempo_actual, posicion_torre)
                            if proyectil:
                                print(f"💥 ¡Torre en ({col}, {row}) DISPARÓ!")
                            else:
                                # Si retorna None, la torre está muerta
                                print(f"⚠️ Torre en ({col}, {row}) está destruida")
                        else:
                            print(f"⚠️ Torre en ({col}, {row}) no tiene método disparar")
                            
                    except Exception as e:
                        print(f"⚠️ Error al disparar: {e}")
                        print(f"   Tipo de torre: {type(torre)}")
                else:
                    print(f"❌ No hay torre en ({col}, {row})")
    
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
            
            # Crear torre en gestor_rooks y obtener la instancia
            torre_tipo = self.torre_a_colocar['class']().tipo
            torre = self.gestor_rooks.agregar_torre(torre_tipo, row, col)
            
            if torre:  # Si se creó exitosamente
                # Usar la MISMA instancia en el grid
                self.grid.add_torre(torre, row, col)
                
                self.presupuesto -= self.torre_a_colocar['price']
                
                print(f"✅ Torre colocada | Presupuesto: ${self.presupuesto}")
            else:
                print(f"❌ No se pudo colocar la torre")
            
            self.esperando_colocacion = None
                # Deseleccionar botones
            for btn in self.element_buttons:
                    btn.selected = False
            self.torre_a_colocar = None
            
            self.draw()
    
    def on_top_right_button_pressed(self):
        print("\n🎮 JUEGO INICIADO!")
        print(f"Nivel: {self.nivel}")
        print(f"Presupuesto: ${self.presupuesto}")
        
        self.top_right_btn.hide()

        # Intentar conectar el control
        if self.control_habilitado and not self.control_conectado:
            self.conectar_control()

        self.juego_activo = True
        self.tiempo_inicio_juego = time.time()
        self.ultimo_tiempo = time.time()
        
        self.gestor_avatares.iniciar()
        
        self.draw()
    
    def _abrir_animacion(self, basenames, mensaje):
        root = self.winfo_toplevel()
        try:
            root.withdraw()
        except Exception:
            pass
        AnimationWindow(master=root, image_basenames=basenames, message_text=mensaje)

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


class AnimationWindow(tk.Toplevel):
    def __init__(self, master=None, image_basenames=("win0","win1","win2"), message_text=""):
        super().__init__(master)
        self.title("Resultado")
        self.geometry("800x500")
        self.resizable(True, True)

        import os
        from PIL import Image, ImageTk

        self._orig_frames = []
        exts = [".png", ".gif", ".jpg", ".jpeg"]
        for base in image_basenames:
            path = None
            for ext in exts:
                p = base + ext
                if os.path.exists(p):
                    path = p
                    break
            if path:
                try:
                    self._orig_frames.append(Image.open(path).convert("RGBA"))
                except Exception:
                    pass

        self._label = tk.Label(self, borderwidth=0, highlightthickness=0)
        self._label.pack(fill="both", expand=True)

        self._msg = tk.Label(self, text=message_text, font=("Arial", 16, "bold"),
                             bg="#000000", fg="white", padx=10, pady=5)
        self._msg.place(relx=0.5, rely=0.04, anchor="n")

        self._btn = tk.Button(self, text="Cerrar", command=self._on_close)
        self._btn.place(relx=0.5, rely=0.96, anchor="s")

        self._idx = 0
        self._running = True
        self._photo_cache = None
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        self.bind("<Configure>", self._on_resize)

        if not self._orig_frames:
            self._label.configure(text="No se hallaron imagenes para la animacion.")
        else:
            self._tick()

    def _render_current_frame(self):
        if not self._orig_frames:
            return
        w = max(1, self._label.winfo_width())
        h = max(1, self._label.winfo_height())

        pil_img = self._orig_frames[self._idx].resize((w, h), resample=Image.LANCZOS)
        self._photo_cache = ImageTk.PhotoImage(pil_img, master=self)
        self._label.configure(image=self._photo_cache)
        self._label.image = self._photo_cache

    def _tick(self):
        if not self._running or not self._orig_frames:
            return
        self._render_current_frame()
        self._idx = (self._idx + 1) % len(self._orig_frames)
        self.after(1000, self._tick)

    def _on_resize(self, event):
        if self._running and self._orig_frames:
            self._render_current_frame()

    def _on_close(self):
        self._running = False
        self.destroy()


class VillageGameWindow:
    def __init__(self, nivel="FACIL", frecuencias=None, initial_palette=None, current_username=None):
        self.root = tk.Tk()
        self.root.title("Avatars vs Rooks")
        self.root.geometry("600x750")
        self.root.resizable(False, False)

        self.game = VillageGame(
            self.root, 600, 750, nivel, frecuencias, initial_palette,
            current_username=current_username
        )
        self.game.pack()
    
    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    frecuencias_prueba = {
        "⛰️ TORRE DE ARENA": 3,
        "🪨 TORRE DE ROCA": 4,
        "💧 TORRE DE AGUA": 2, 
        "🔥 TORRE DE FUEGO": 5
    }
    game_window = VillageGameWindow(nivel="DIFICIL", frecuencias=frecuencias_prueba)
    game_window.run()