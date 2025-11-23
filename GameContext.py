#ventana de contexto
import json
import base64
from tkinter import messagebox, ttk
from encriptar import cargar_clave, generar_clave, ARCHIVO_SALIDA as ARCHIVO_USUARIOS_ENC
from cryptography.fernet import Fernet
import os


ARCHIVO_USUARIOS = "usuarios.json"

def cargar_usuarios():
    # Preferir archivo encriptado si existe
    try:
        if 'ARCHIVO_USUARIOS_ENC' in globals():
            enc_path = ARCHIVO_USUARIOS_ENC
        else:
            enc_path = "usuarios.json.enc"
        if os.path.exists(enc_path):
            try:
                clave = cargar_clave()
            except FileNotFoundError:
                messagebox.showerror("Error", "No se encontró la clave de cifrado (clave.key).")
                return {}
            fernet = Fernet(clave)
            with open(enc_path, "rb") as f:
                datos_encriptados = f.read()
            try:
                datos = fernet.decrypt(datos_encriptados).decode("utf-8")
                return json.loads(datos)
            except Exception as e:
                print(f"Error desencriptando usuarios: {e}")
                messagebox.showerror("Error", "No se pudo desencriptar la base de usuarios.")
                return {}
        # Compatibilidad: si no existe el .enc, intentar el JSON plano legado
        if os.path.exists(ARCHIVO_USUARIOS):
            try:
                with open(ARCHIVO_USUARIOS, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error cargando usuarios (JSON): {e}")
                return {}
    except Exception as e:
        print(f"Error cargando usuarios: {e}")
        return {}
    if os.path.exists(ARCHIVO_USUARIOS):
            try:
                with open(ARCHIVO_USUARIOS, "r") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error cargando usuarios: {e}")
                return {}
    return {}

def guardar_usuarios(usuarios):
    try:
        try:
            clave = cargar_clave()
        except FileNotFoundError:
            clave = generar_clave()
        fernet = Fernet(clave)
        datos_json = json.dumps(usuarios, ensure_ascii=False, indent=4)
        datos_encriptados = fernet.encrypt(datos_json.encode("utf-8"))
        # Guardar cifrado
        enc_path = ARCHIVO_USUARIOS_ENC if "ARCHIVO_USUARIOS_ENC" in globals() else "usuarios.json.enc"
        with open(enc_path, "wb") as f:
            f.write(datos_encriptados)
        # Opcional: eliminar el JSON en claro si existe
        try:
            if os.path.exists(ARCHIVO_USUARIOS):
                os.remove(ARCHIVO_USUARIOS)
        except Exception as e:
            print(f"No se pudo eliminar {ARCHIVO_USUARIOS}: {e}")
        return True
    except Exception as e:
        print(f"Error guardando usuarios: {e}")
        messagebox.showerror("Error", "No se pudo guardar la información del usuario (cifrado).")
        return False

class GameContext:
    """Contexto global del juego.
    Guarda siempre el usuario logeado y toda su información.
    Todas las ventanas deben usar este objeto.
    """

    def __init__(self, username: str):
        self.username = username
        self._usuarios = cargar_usuarios()

        if username not in self._usuarios:
            raise ValueError(f"Usuario '{username}' no existe.")

        self.data = self._usuarios[username]

        # Variables transitorias para el juego
        self.nivel = "FACIL"
        self.frecuencias = {}
        self.paleta = None
        self.bpm = 0
        self.cancion = ""
        self.presupuesto = 350

        # Imagen en memoria (optimiza carga)
        self.cached_foto_pil = None

    # SECCIÓN: FOTO PERFIl
    def get_foto_pil(self):
        """Retorna la foto PIL ya decodificada"""
        import io
        from PIL import Image

        foto_b64 = self.data.get("foto_perfil_b64", "")
        if not foto_b64:
            return None

        if self.cached_foto_pil:
            return self.cached_foto_pil

        try:
            img_data = base64.b64decode(foto_b64)
            img = Image.open(io.BytesIO(img_data))
            self.cached_foto_pil = img
            return img
        except:
            return None

    def set_foto_pil(self, img):
        """Actualiza la foto de perfil y la guarda en el archivo"""
        import io

        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        foto_b64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

        self.data["foto_perfil_b64"] = foto_b64
        self.cached_foto_pil = img
        self._guardar()

    # SECCIÓN: DATOS USUARIO
    def update_user_field(self, key, value):
        self.data[key] = value
        self._guardar()

    def cambiar_username(self, nuevo):
        """Renombra el usuario completo en el JSON"""
        usuarios = self._usuarios

        usuarios[nuevo] = usuarios[self.username]
        del usuarios[self.username]

        self.username = nuevo
        self.data = usuarios[nuevo]

        guardar_usuarios(usuarios)

    # SECCIÓN: GUARDADO
    def _guardar(self):
        self._usuarios[self.username] = self.data
        guardar_usuarios(self._usuarios)