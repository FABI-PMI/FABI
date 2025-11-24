"""
Sistema de Paletas Personalizadas por Usuario
"""

import json
import os
from cryptography.fernet import Fernet

# Importar funciones de encriptación
try:
    from encriptar import cargar_clave, ARCHIVO_SALIDA as ARCHIVO_USUARIOS_ENC
except ImportError:
    ARCHIVO_USUARIOS_ENC = "usuarios.json.enc"
    def cargar_clave():
        raise FileNotFoundError("clave.key no encontrada")

ARCHIVO_USUARIOS_JSON = "usuarios.json"


def cargar_usuarios_encriptados():
    """Carga el archivo de usuarios encriptado"""
    try:
        # Intentar cargar archivo encriptado
        if os.path.exists(ARCHIVO_USUARIOS_ENC):
            try:
                clave = cargar_clave()
                fernet = Fernet(clave)
                
                with open(ARCHIVO_USUARIOS_ENC, "rb") as f:
                    datos_encriptados = f.read()
                
                datos = fernet.decrypt(datos_encriptados).decode("utf-8")
                return json.loads(datos)
            except Exception as e:
                print(f"⚠️ Error desencriptando usuarios: {e}")
                return {}
        
        # Fallback: intentar archivo JSON plano
        if os.path.exists(ARCHIVO_USUARIOS_JSON):
            try:
                with open(ARCHIVO_USUARIOS_JSON, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️ Error cargando usuarios (JSON): {e}")
                return {}
        
        return {}
        
    except Exception as e:
        print(f"⚠️ Error: {e}")
        return {}


def convertir_listas_a_tuplas(paleta_dict):
    """
    Convierte valores de lista [R, G, B] a tuplas (R, G, B)
    
    Args:
        paleta_dict (dict): Diccionario con colores como listas
    
    Returns:
        dict: Diccionario con colores como tuplas
    """
    paleta_tuplas = {}
    for key, value in paleta_dict.items():
        if isinstance(value, list) and len(value) == 3:
            # Convertir [R, G, B] → (R, G, B)
            paleta_tuplas[key] = tuple(value)
        else:
            paleta_tuplas[key] = value
    return paleta_tuplas


def cargar_paleta_para_juego(username):
    """
    Función principal para cargar la paleta de colores
    
    Args:
        username (str): Nombre de usuario
    
    Returns:
        dict: Paleta de colores (personalizada o None)
    """
    if not username:
        print("⚠️ No hay usuario, usando paleta default")
        return None
    
    try:
        usuarios = cargar_usuarios_encriptados()
        
        if not usuarios or username not in usuarios:
            print(f"⚠️ Usuario '{username}' no encontrado")
            return None
        
        datos_usuario = usuarios[username]
        
        # Verificar si tiene personalización
        if "personalizacion" not in datos_usuario:
            print(f"ℹ️ Usuario '{username}' sin personalización")
            return None
        
        personalizacion = datos_usuario["personalizacion"]
        
        # Opción 1: Paleta completa ya guardada
        if "colores" in personalizacion:
            colores = personalizacion["colores"]
            if isinstance(colores, dict) and len(colores) > 0:
                # ✅ CONVERTIR LISTAS A TUPLAS
                paleta_convertida = convertir_listas_a_tuplas(colores)
                print(f"✅ Paleta cargada para '{username}' ({len(paleta_convertida)} colores)")
                return paleta_convertida
        
        # Opción 2: Generar desde color base + tema
        if "color" in personalizacion and "tema" in personalizacion:
            try:
                from PaletaColores import generate_palette
                paleta = generate_palette(
                    personalizacion["color"], 
                    personalizacion["tema"]
                )
                # ✅ ASEGURAR QUE SEAN TUPLAS
                paleta_convertida = convertir_listas_a_tuplas(paleta)
                print(f"✅ Paleta generada para '{username}' ({len(paleta_convertida)} colores)")
                return paleta_convertida
            except ImportError:
                print("⚠️ No se pudo importar PaletaColores")
                return None
        
        return None
        
    except Exception as e:
        print(f"⚠️ Error: {e}")
        import traceback
        traceback.print_exc()
        return None


def get_paleta_default():
    """
    Retorna la paleta por defecto del juego
    
    Returns:
        dict: Paleta de colores por defecto
    """
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