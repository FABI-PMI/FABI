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
                print(f"✅ Paleta cargada para '{username}'")
                return colores
        
        # Opción 2: Generar desde color base + tema
        if "color" in personalizacion and "tema" in personalizacion:
            try:
                from PaletaColores import generate_palette
                paleta = generate_palette(
                    personalizacion["color"], 
                    personalizacion["tema"]
                )
                print(f"✅ Paleta generada para '{username}'")
                return paleta
            except ImportError:
                print("⚠️ No se pudo importar PaletaColores")
                return None
        
        return None
        
    except Exception as e:
        print(f"⚠️ Error: {e}")
        return None