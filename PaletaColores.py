"""
Generador de paletas de colores para el juego de aldeas.
Recibe un color base y genera toda la paleta necesaria.
"""

def hex_to_rgb(hex_color):
    """Convierte color hexadecimal a tupla RGB"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_hex(rgb):
    """Convierte tupla RGB a hexadecimal"""
    return '#%02x%02x%02x' % rgb

def lighten(color, factor):
    """Aclara un color. Factor 0-1 (1 = blanco)"""
    return tuple(int(c + (255 - c) * factor) for c in color)

def darken(color, factor):
    """Oscurece un color. Factor 0-1 (1 = negro)"""
    return tuple(int(c * (1 - factor)) for c in color)

def desaturate(color, factor):
    """Desatura un color hacia gris. Factor 0-1"""
    gray = sum(color) // 3
    return tuple(int(c + (gray - c) * factor) for c in color)

def adjust_brightness(color, factor):
    """Ajusta el brillo. factor < 1 oscurece, factor > 1 aclara"""
    return tuple(max(0, min(255, int(c * factor))) for c in color)

def generate_palette(base_color_hex, theme="claro"):
    """
    Genera una paleta completa basada en un color base y un tema.
    
    Args:
        base_color_hex (str): Color base en formato hexadecimal (#RRGGBB)
        theme (str): "claro", "oscuro", o "medio"
    
    Returns:
        dict: Diccionario con todos los colores necesarios para el juego
    """
    base_color = hex_to_rgb(base_color_hex)
    
    # Colores base segÃºn el tema
    if theme == "oscuro":
        # Tema oscuro - fondos oscuros, elementos visibles
        palette = {
            # Zona segura - tonos oscuros del color base
            'safe_zone_bg': darken(base_color, 0.7),
            'safe_houses': lighten(base_color, 0.3),
            'safe_houses_roof': base_color,
            'safe_houses_door': darken(base_color, 0.4),
            'safe_houses_window': (255, 255, 150),
            
            # Zona invasora - muy oscura y amenazante
            'invader_zone_bg': (20, 20, 25),
            'invader_houses': desaturate(base_color, 0.8),
            'invader_houses_roof': (100, 20, 20),
            'invader_houses_door': (30, 30, 30),
            'invader_houses_window': (120, 80, 80),
            
            # CuadrÃ­cula
            'grid_bg': darken(base_color, 0.5),
            'grid_lines': lighten(base_color, 0.2),
            
            # Elementos UI
            'user_icon_bg': darken(base_color, 0.4),
            'user_icon_border': lighten(base_color, 0.3),
            'user_icon_person': lighten(base_color, 0.4),
            'question_bg': base_color,
            'question_text': (255, 255, 255),
            
            # Fondo general
            'background': darken(base_color, 0.8)
        }
        
    elif theme == "claro":
        # Tema claro - fondos claros, colores vibrantes
        palette = {
            # Zona segura - tonos claros y amigables
            'safe_zone_bg': lighten(base_color, 0.85),
            'safe_houses': base_color,
            'safe_houses_roof': darken(base_color, 0.2),
            'safe_houses_door': darken(base_color, 0.4),
            'safe_houses_window': (255, 255, 200),
            
            # Zona invasora - oscura y contrastante
            'invader_zone_bg': (30, 30, 35),
            'invader_houses': desaturate(base_color, 0.7),
            'invader_houses_roof': (120, 20, 20),
            'invader_houses_door': (40, 40, 40),
            'invader_houses_window': (150, 100, 100),
            
            # CuadrÃ­cula
            'grid_bg': (255, 255, 255),
            'grid_lines': base_color,
            
            # Elementos UI
            'user_icon_bg': (255, 255, 255),
            'user_icon_border': base_color,
            'user_icon_person': base_color,
            'question_bg': lighten(base_color, 0.3),
            'question_text': (255, 255, 255),
            
            # Fondo general
            'background': lighten(base_color, 0.9)
        }
        
    else:  # "medio"
        # Tema tÃ©rmino medio - balance entre claro y oscuro
        palette = {
            # Zona segura - tonos medios
            'safe_zone_bg': lighten(base_color, 0.6),
            'safe_houses': base_color,
            'safe_houses_roof': darken(base_color, 0.25),
            'safe_houses_door': darken(base_color, 0.45),
            'safe_houses_window': (255, 255, 180),
            
            # Zona invasora - oscura pero no tanto
            'invader_zone_bg': (40, 40, 45),
            'invader_houses': desaturate(base_color, 0.6),
            'invader_houses_roof': (110, 30, 30),
            'invader_houses_door': (50, 50, 50),
            'invader_houses_window': (140, 90, 90),
            
            # CuadrÃ­cula
            'grid_bg': (240, 240, 240),
            'grid_lines': base_color,
            
            # Elementos UI
            'user_icon_bg': (240, 240, 240),
            'user_icon_border': base_color,
            'user_icon_person': base_color,
            'question_bg': lighten(base_color, 0.2),
            'question_text': (255, 255, 255),
            
            # Fondo general
            'background': lighten(base_color, 0.7)
        }
    
    return palette