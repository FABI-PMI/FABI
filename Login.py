import tkinter as tk
from tkinter import messagebox, ttk
import json
import os
from datetime import datetime, timedelta
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from twilio.rest import Client
from PIL import Image, ImageTk
import cv2
import pickle
import numpy as np
from cryptography.fernet import Fernet
from encriptar import cargar_clave, generar_clave, ARCHIVO_SALIDA as ARCHIVO_USUARIOS_ENC

ARCHIVO_USUARIOS = "usuarios.json"

def enviar_sms(destinatario, cuerpo, asunto="Mensaje del sistema"):
    try:
        account_sid = "ACcf2b1d430804735356bdc2ef2cbefa13"
        auth_token = "f1d7fc33096b90ca520115eda8f4f273"

        client = Client(account_sid, auth_token)

        client.api.account.messages.create(
            to=f"+506{destinatario}",
            from_="+12768008011",
            body=cuerpo)
        return True
    except Exception as e:
        print(f"Error enviando el SMS: {e}")
        return False
    
def enviar_correo(destinatario, cuerpo, asunto="Mensaje del sistema"):
    remitente = "ohnono093@gmail.com"
    contrasena = "whlo xaxr bgjf qwsd"

    mensaje = MIMEMultipart()
    mensaje["From"] = remitente
    mensaje["To"] = destinatario
    mensaje["Subject"] = asunto
    mensaje.attach(MIMEText(cuerpo, "plain"))

    try:
        servidor = smtplib.SMTP("smtp.gmail.com", 587)
        servidor.starttls()
        servidor.login(remitente, contrasena)
        servidor.sendmail(remitente, destinatario, mensaje.as_string())
        servidor.quit()
        return True
    except Exception as e:
        print(f"Error enviando el correo: {e}")
        return False

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

def generar_pin():
    return str(random.randint(1000, 9999))

import os, pickle

def cargar_facebank_desde_carpeta(carpeta=None):
    """
    Lee todos los *.pkl de face_data y devuelve:
    { username: {"faces": [np.array, ...], ...}, ... }
    Acepta tanto dicts con clave 'faces' como listas de caras.
    """
    if carpeta is None:
        carpeta = os.path.join(os.path.dirname(os.path.abspath(__file__)), "face_data")

    facebank = {}
    if not os.path.isdir(carpeta):
        return facebank

    for fname in os.listdir(carpeta):
        if not fname.endswith(".pkl"):
            continue
        ruta = os.path.join(carpeta, fname)
        try:
            with open(ruta, "rb") as f:
                data = pickle.load(f)
            base = os.path.splitext(fname)[0]            # p.ej. "marco_face"
            username = base[:-5] if base.endswith("_face") else base  # "marco"

            # Normaliza estructura
            if isinstance(data, dict) and "faces" in data:
                caras = data["faces"]
            elif isinstance(data, list):
                caras = data
                data = {"faces": caras}
            else:
                # Estructura desconocida; intenta ignorar
                continue

            # Asegura lista de np.array
            if not isinstance(caras, list) or len(caras) == 0:
                continue
            facebank[username] = data
        except Exception as e:
            print(f"No se pudo leer {ruta}: {e}")
            continue
    return facebank

def login_facial_directo():
    """Realiza el login facial y devuelve el username reconocido"""
    try:
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
        # === NUEVO: cargar facebank directamente desde face_data/ ===
        usuarios_faceid = cargar_facebank_desde_carpeta()
        if not usuarios_faceid:
            messagebox.showerror("Error", "No hay datos Face ID en la carpeta face_data/")
            return None

        
        # Iniciar cámara
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            messagebox.showerror("Error", "No se pudo acceder a la cámara")
            return None
        
        usuario_reconocido = None
        intentos = 0
        max_intentos = 100  # 100 frames para intentar reconocer
        
        messagebox.showinfo("Face ID Login", "🔍 Se abrira la camara para detectar el rostro...")
        
        while intentos < max_intentos:
            ret, frame = cap.read()
            if not ret:
                break
            
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)
            
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x+w, y+h), (138, 28, 50), 2)
                face_roi = gray[y:y+h, x:x+w]
                
                # Comparar con todos los usuarios registrados
                for username, face_data in usuarios_faceid.items():
                    stored_faces = face_data['faces']
                    
                    # Comparar con las caras almacenadas
                    for stored_face in stored_faces:
                        try:
                            # Redimensionar para comparar
                            face_resized = cv2.resize(face_roi, (stored_face.shape[1], stored_face.shape[0]))
                            
                            # Calcular similitud usando correlación
                            similarity = cv2.matchTemplate(face_resized, stored_face, cv2.TM_CCOEFF_NORMED)[0][0]
                            
                            # Si la similitud es alta, reconocer usuario
                            if similarity > 0.6:  # Umbral de similitud
                                usuario_reconocido = username
                                cv2.putText(frame, f"Reconocido: {username}", (x, y-10),
                                          cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
                                break
                        except:
                            continue
                    
                    if usuario_reconocido:
                        break
                
                if usuario_reconocido:
                    break
            
            # Mostrar contador
            cv2.putText(frame, f"Buscando... {intentos}/{max_intentos}", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (138, 28, 50), 2)
            
            if usuario_reconocido:
                cv2.putText(frame, "RECONOCIDO!", (10, 60),
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            cv2.imshow('Face ID Login', frame)
            
            # Si se reconoció, esperar un momento y salir
            if usuario_reconocido:
                cv2.waitKey(1000)
                break
            
            if cv2.waitKey(1) & 0xFF == 27:  # ESC para cancelar
                break
            
            intentos += 1
        
        cap.release()
        cv2.destroyAllWindows()
        
        return usuario_reconocido
        
    except Exception as e:
        messagebox.showerror("Error", f"Error en Face ID: {str(e)}")
        return None

class LoginApp:
    def __init__(self, root):
        self.root = root
        self.usuarios = cargar_usuarios()
        self.usuario_actual = None
        self.jugadores_login = []
        self.pin_generado = None
        self.pin_expira = None
        self.bot_panel_creado = False

        # Configurar la ventana
        self.root.title("Login - Juego de Memoria")
        self.root.geometry("450x550")
        self.root.resizable(False, False)
        
        # Centrar ventana
        self.centrar_ventana()
        
        # Configurar colores y estilos
        self.configurar_estilos()
        
        # Crear canvas principal con gradiente
        self.crear_canvas_principal()
        
        # Crear contenedor principal con scroll
        self.crear_contenedor_principal_con_scroll()
        
        self.menu_principal()

    def centrar_ventana(self):
        """Centra la ventana en la pantalla"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def configurar_estilos(self):
        """Configura los colores y estilos de la aplicación"""
        self.colores = {
            'primario': "#8A1C32",
            'secundario': "#a10707",
            'acento': "#03a328",
            'fondo': '#f8f9fa',
            'texto': '#2c3e50',
            'texto_claro': "#8d7f7f",
            'blanco': '#ffffff',
            'verde': '#27ae60',
            'rojo': "#3ce753",
            'azul_claro': '#74b9ff'
        }
        
        # Configurar estilo ttk
        style = ttk.Style(self.root)   # ← importante: asociar al root vigente
        style.theme_use('clam')
        
        # Estilo para botones
        style.configure(
            "Moderno.TButton",
            padding=(15, 8),
            font=('Segoe UI', 9, 'bold')
        )

    def crear_canvas_principal(self):
        """Crea el canvas principal con fondo degradado"""
        self.canvas = tk.Canvas(self.root, width=450, height=550, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        
        # Simular gradiente con rectángulos
        for i in range(550):
            r1, g1, b1 = 138, 28, 50
            r2, g2, b2 = 97, 20, 35
            
            ratio = i / 550
            r = int(r1 + (r2 - r1) * ratio)
            g = int(g1 + (g2 - g1) * ratio)
            b = int(b1 + (b2 - b1) * ratio)
            
            color = f'#{r:02x}{g:02x}{b:02x}'
            self.canvas.create_line(0, i, 450, i, fill=color, width=1)
        
        # Agregar formas decorativas
        self.agregar_formas_decorativas()

    def agregar_formas_decorativas(self):
        """Agrega formas decorativas al fondo"""
        self.canvas.create_oval(40, 60, 100, 120, fill="#6bd3ff", stipple='gray25', outline='')
        self.canvas.create_rectangle(300, 120, 340, 160, fill='#4ecdc4', stipple='gray25', outline='')
        self.canvas.create_polygon(60, 350, 100, 350, 80, 320, fill='#f9ca24', stipple='gray25', outline='')
        self.canvas.create_oval(280, 380, 330, 430, fill='#45b7d1', stipple='gray25', outline='')

    def crear_contenedor_principal_con_scroll(self):
        """Crea el contenedor principal con efecto glassmorphism y añade funcionalidad de scroll."""
        scroll_container_frame = tk.Frame(self.root, bg='#C5C5C5', relief='flat', bd=0)
        scroll_container_frame.place(x=35, y=50, width=380, height=450)

        self.scroll_canvas = tk.Canvas(scroll_container_frame, bg='#C5C5C5', highlightthickness=0)
        self.scroll_canvas.pack(side="left", fill="both", expand=True)

        self.scrollbar = ttk.Scrollbar(scroll_container_frame, orient="vertical", command=self.scroll_canvas.yview)
        self.scrollbar.pack(side="right", fill="y")

        self.scroll_canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scroll_canvas.bind('<Configure>', self._on_canvas_configure)
        self.scroll_canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        self.main_frame = tk.Frame(self.scroll_canvas, bg='#C5C5C5', relief='flat', bd=0)
        self.main_frame_id = self.scroll_canvas.create_window((0, 0), window=self.main_frame, anchor="nw")

        self.main_frame.bind("<Configure>", self._on_frame_configure)

        shadow_frame = tk.Frame(self.root, bg='#000000', relief='flat', bd=0)
        shadow_frame.place(x=40, y=55, width=380, height=450)
        
        scroll_container_frame.lift()
    
    def _on_frame_configure(self, event):
        """Configura el scrollregion del Canvas para que coincida con el tamaño del frame interno."""
        self.scroll_canvas.configure(scrollregion=self.scroll_canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        """Ajusta el ancho del main_frame para que coincida con el ancho del canvas."""
        self.scroll_canvas.itemconfig(self.main_frame_id, width=event.width)
        self.scroll_canvas.configure(scrollregion=self.scroll_canvas.bbox("all"))

    def _on_mousewheel(self, event):
        """Permite el desplazamiento con la rueda del ratón."""
        self.scroll_canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def limpiar(self):
        """Limpia el contenido del frame principal"""
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        self.bot_panel_creado = False
        self.root.update_idletasks()
        self.scroll_canvas.configure(scrollregion=self.scroll_canvas.bbox("all"))

    def crear_header(self, titulo, subtitulo="", icon_size=128, bg="#C5C5C5"):
        icon_frame = tk.Frame(self.main_frame, bg=bg)
        icon_frame.pack(pady=8, fill='x')

        try:
            logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Logo.jpg')
            img = Image.open(logo_path).resize((icon_size, icon_size), Image.LANCZOS)
            self._logo_img = ImageTk.PhotoImage(img, master=self.root)
            lbl_logo_tmp = tk.Label(icon_frame, image=self._logo_img, bg=bg)
            lbl_logo_tmp.image = self._logo_img
            lbl_logo_tmp.pack(pady=4)
        except Exception as e:
            print("No se pudo cargar Logo.jpg:", e)

        tk.Label(self.main_frame, text=titulo,
                font=('Segoe UI', 14, 'bold'),
                fg=self.colores['texto'], bg=bg).pack(pady=(6, 3), fill='x')

        if subtitulo:
            tk.Label(self.main_frame, text=subtitulo,
                    font=('Segoe UI', 9),
                    fg=self.colores['texto_claro'], bg=bg).pack(pady=(0, 12), fill='x')

    def crear_campo_entrada(self, parent, label_text, is_password=False, placeholder=""):
        """Crea un campo de entrada moderno"""
        field_frame = tk.Frame(parent, bg='#C5C5C5')
        field_frame.pack(fill='x', padx=15, pady=4)
        
        label = tk.Label(field_frame, text=label_text, 
                        font=('Segoe UI', 8, 'bold'),
                        fg=self.colores['texto'], bg='#C5C5C5', anchor='w')
        label.pack(fill='x', pady=(0, 2))
        
        # Frame contenedor para entry y botón de ojo
        entry_container = tk.Frame(field_frame, bg='#f8f9fa', relief='flat', bd=0)
        entry_container.pack(fill='x')
        
        entry = tk.Entry(entry_container, font=('Segoe UI', 10),
                        relief='flat', bd=0, bg='#f8f9fa',
                        fg=self.colores['texto'], insertbackground=self.colores['primario'])
        
        if is_password:
            entry.config(show="*")
            entry.pack(side='left', fill='both', expand=True, ipady=8, ipadx=10)
            
            # Botón de ojo para mostrar/ocultar contraseña
            eye_btn = tk.Button(entry_container, text="👁", font=('Segoe UI', 10),
                              relief='flat', bd=0, bg='#f8f9fa',
                              fg=self.colores['texto'], cursor='hand2',
                              padx=10)
            eye_btn.pack(side='right', fill='y')
            
            # Variable para rastrear el estado
            show_password = {'visible': False}
            
            def toggle_password(event=None):
                if show_password['visible']:
                    entry.config(show="*")
                    show_password['visible'] = False
                else:
                    entry.config(show="")
                    show_password['visible'] = True
            
            def hide_password(event=None):
                entry.config(show="*")
                show_password['visible'] = False
            
            # Eventos del botón de ojo
            eye_btn.bind("<ButtonPress-1>", toggle_password)
            eye_btn.bind("<ButtonRelease-1>", hide_password)
            
            # Efectos de focus para el contenedor completo
            def on_focus_in(e):
                entry_container.config(bg='white', relief='solid', bd=2)
                entry.config(bg='white')
                eye_btn.config(bg='white')
            
            def on_focus_out(e):
                entry_container.config(bg='#f8f9fa', relief='flat', bd=0)
                entry.config(bg='#f8f9fa')
                eye_btn.config(bg='#f8f9fa')
            
            entry.bind("<FocusIn>", on_focus_in)
            entry.bind("<FocusOut>", on_focus_out)
        else:
            entry.pack(fill='x', ipady=8, ipadx=10)
            
            # Efectos de focus
            def on_focus_in(e):
                entry_container.config(bg='white', relief='solid', bd=2)
                entry.config(bg='white')
            
            def on_focus_out(e):
                entry_container.config(bg='#f8f9fa', relief='flat', bd=0)
                entry.config(bg='#f8f9fa')
            
            entry.bind("<FocusIn>", on_focus_in)
            entry.bind("<FocusOut>", on_focus_out)
        
        return entry

    def crear_boton_moderno(self, parent, texto, comando, estilo='primario', ancho_completo=True):
        """Crea un botón con estilo moderno"""
        if estilo == 'primario':
            bg_color = self.colores['primario']
            fg_color = 'white'
            hover_color = self.colores['secundario']
        elif estilo == 'secundario':
            bg_color = 'white'
            fg_color = self.colores['primario']
            hover_color = '#f8f9fa'
        elif estilo == 'peligro':
            bg_color = self.colores['rojo']
            fg_color = 'white'
            hover_color = '#c0392b'
        else:
            bg_color = self.colores['fondo']
            fg_color = self.colores['texto']
            hover_color = '#e9ecef'
        
        btn = tk.Button(parent, text=texto, command=comando,
                       font=('Segoe UI', 9, 'bold'),
                       bg=bg_color, fg=fg_color,
                       relief='flat', bd=0, pady=8,
                       cursor='hand2')
        
        if ancho_completo:
            btn.pack(fill='x', padx=15, pady=4)
        else:
            btn.pack(pady=4)
        
        # Efectos hover
        def on_enter(e):
            btn.config(bg=hover_color)
        
        def on_leave(e):
            btn.config(bg=bg_color)
        
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        
        return btn

    def mostrar_jugadores_conectados(self):
        """Muestra los jugadores ya conectados"""
        if self.jugadores_login and not self.solo_uno:
            status_frame = tk.Frame(self.main_frame, bg='#d4edda', relief='flat', bd=0)
            status_frame.pack(fill='x', padx=15, pady=(0, 8))
            
            titulo = tk.Label(status_frame, text="✓ Jugadores conectados:", 
                            font=('Segoe UI', 8, 'bold'),
                            fg='#155724', bg='#d4edda')
            titulo.pack(pady=(6, 3))
            
            for jugador in self.jugadores_login:
                jugador_label = tk.Label(status_frame, text=f"• {jugador}", 
                                       font=('Segoe UI', 7),
                                       fg='#155724', bg='#d4edda')
                jugador_label.pack(anchor='w', padx=15)
            
            tk.Label(status_frame, text="", bg='#d4edda').pack(pady=3)

    def abrir_registro(self):
        """Abre Registro en el mismo proceso y cierra Login después"""
        import tkinter as tk
        try:
            from Registro import Registro
        except Exception as e:
            messagebox.showerror('Error', f'No se pudo importar Registro: {e}')
            return
        nueva = tk.Tk()
        try:
            Registro(nueva)
        except Exception as e:
            try:
                nueva.destroy()
            except Exception:
                pass
            messagebox.showerror('Error', f'No se pudo abrir Registro: {e}')
            return
        # cerrar login un instante después para evitar after/bindings residuales
        try:
            self.root.after(50, self.root.destroy)
        except Exception:
            pass
        nueva.mainloop()


    def menu_principal(self):
        self.limpiar()

        # Contenedor principal
        main_container = tk.Frame(self.main_frame, bg='#C5C5C5')
        main_container.pack(fill='both', expand=True, pady=10)
        
        # Botón Registro arriba a la izquierda
        btn_registro_container = tk.Frame(main_container, bg='#C5C5C5')
        btn_registro_container.place(x=15, y=0)
        
        tk.Button(
            btn_registro_container,
            text="✏️ Registro",
            font=('Segoe UI', 8, 'bold'),
            bg=self.colores['primario'],
            fg='white',
            bd=0,
            cursor='hand2',
            padx=12,
            pady=4,
            command=self.abrir_registro
        ).pack()
        
        # Botón Face ID arriba a la derecha
        btn_face_container = tk.Frame(main_container, bg='#C5C5C5')
        btn_face_container.place(relx=1.0, x=-15, y=0, anchor='ne')
        
        tk.Button(
            btn_face_container,
            text="👤",
            font=('Arial', 16),
            bg=self.colores['primario'],
            fg='white',
            bd=0,
            width=2,
            cursor='hand2',
            command=self.iniciar_login_facial
        ).pack()
        
        tk.Label(
            btn_face_container,
            text="Face ID",
            font=('Arial', 6, 'bold'),
            bg='#C5C5C5',
            fg='#2c3e50'
        ).pack(pady=(1, 0))
        
        # Logo y títulos centrados
        header_content = tk.Frame(main_container, bg='#C5C5C5')
        header_content.pack(expand=True, pady=(40, 0))
        
        try:
            logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Logo.jpg')
            img = Image.open(logo_path).resize((128, 128), Image.LANCZOS)
            self._logo_img = ImageTk.PhotoImage(img, master=self.root)
            lbl_logo_tmp = tk.Label(header_content, image=self._logo_img, bg='#C5C5C5')
            lbl_logo_tmp.image = self._logo_img
            lbl_logo_tmp.pack(pady=4)
        except Exception as e:
            print("No se pudo cargar Logo.jpg:", e)
        
        if True:
            tk.Label(header_content, text="Avatars VS Rooks",
                    font=('Segoe UI', 14, 'bold'),
                    fg=self.colores['texto'], bg='#C5C5C5').pack(pady=(6, 3))
            tk.Label(header_content, text="Ingresa para continuar",
                    font=('Segoe UI', 9),
                    fg=self.colores['texto_claro'], bg='#C5C5C5').pack(pady=(0, 12))
        else:
            tk.Label(header_content, text="LOGIN",
                    font=('Segoe UI', 14, 'bold'),
                    fg=self.colores['texto'], bg='#C5C5C5').pack(pady=(6, 3))
            tk.Label(header_content, text="Inicio de Sesión",
                    font=('Segoe UI', 9),
                    fg=self.colores['texto_claro'], bg='#C5C5C5').pack(pady=(0, 12))
        
        # Mostrar jugadores conectados
        self.mostrar_jugadores_conectados()
        
        # Contenedor de formularios
        self.form_container = tk.Frame(self.main_frame, bg='#C5C5C5')
        self.form_container.pack(fill='both', expand=True)
        
        # Mostrar formulario de login
        self.mostrar_login()
        
        # Botones inferiores
        self.crear_boton_moderno(self.main_frame, "¿Olvidaste tu contraseña?", 
                               self.recuperar_contrasena, 'primario')
        self.crear_boton_moderno(self.main_frame, "Cancelar", 
                               self.cancelar, 'primario')

    def mostrar_login(self):
        """Muestra el formulario de login"""
        # Campos de entrada
        self.usuario_entry = self.crear_campo_entrada(self.form_container, "Usuario/Correo/Teléfono:")
        self.contrasena_entry = self.crear_campo_entrada(self.form_container, "Contraseña:", True)
        
        # Botón de login
        self.crear_boton_moderno(self.form_container, "ENTRAR", self.verificar_login)
        
        # Focus en el primer campo
        self.usuario_entry.focus()

    def procesar_login_exitoso(self, nombre_detectado):
        if not self.usuarios:
            self.usuarios = cargar_usuarios()

        if nombre_detectado not in self.usuarios:
            messagebox.showerror("Error", f"'{nombre_detectado}' no existe en usuarios.json. Regístralo primero con Face ID.")
            return

        if nombre_detectado not in self.jugadores_login:
            self.jugadores_login.append(nombre_detectado)

        messagebox.showinfo("Éxito", f"Sesión iniciada para: {nombre_detectado}")

        if True:
            self.abrir_principal(nombre_detectado)


    def abrir_principal(self, usuario):
        from VentanaPrincipal import VillageGameWindow as VP
        VentanaClase = VP
        # ⬇️ Pasar el username al juego
        VentanaClase(current_username=usuario)
        # cerrar login después de lanzar la ventana principal
        self.root.after(50, self.root.destroy)



    def verificar_login(self):
        credencial = self.usuario_entry.get().strip()
        contrasena = self.contrasena_entry.get().strip()
        
        # Validar campos vacíos
        if not credencial or not contrasena:
            messagebox.showerror("Error", "Por favor, completa todos los campos.")
            return

        # Verificación normal de usuarios
        paso = False
        usuario_encontrado = None
        
        for usuario, datos in self.usuarios.items():
            if (credencial == usuario or credencial == datos.get("correo") or credencial == datos.get("telefono")) and self.usuarios[usuario]["contrasena"] == contrasena:
                paso = True
                usuario_encontrado = usuario
                break
        
        if paso and usuario_encontrado:
            if usuario_encontrado not in self.jugadores_login:
                self.jugadores_login.append(usuario_encontrado)
                messagebox.showinfo("Éxito", f"Sesión iniciada para: {usuario_encontrado}")

                if True:
                    self.abrir_principal(usuario_encontrado)


        else:
            messagebox.showerror("Error", "Credencial o contraseña incorrectos.")

    def recuperar_contrasena(self):
        self.limpiar()
        
        # Header
        self.crear_header("Recuperar Contraseña")
        
        # Campo de entrada
        self.correo_entrada = self.crear_campo_entrada(self.main_frame, "Correo electrónico:")
        
        # Botones
        self.crear_boton_moderno(self.main_frame, "ENVIAR PIN", self.enviar_pin)
        self.crear_boton_moderno(self.main_frame, "Volver", self.menu_principal, 'secundario')
        
        # Focus
        self.correo_entrada.focus()

    def enviar_pin(self):
        correo = self.correo_entrada.get().strip()
        
        if not correo:
            messagebox.showerror("Error", "Por favor, ingresa un credencial valido.")
            return
            
        # Buscar usuario por correo
        usuario_encontrado = None
        for usuario, datos in self.usuarios.items():
            if datos["correo"] == correo:
                credencial = "correo"
                usuario_encontrado = usuario
                break
                
        if usuario_encontrado and credencial == "correo":
            self.pin_generado = generar_pin()
            self.pin_expira = datetime.now() + timedelta(minutes=2)
            self.usuario_actual = usuario_encontrado
            
            if enviar_correo(self.usuarios[usuario_encontrado]["correo"], f"Tu PIN para recuperar la contraseña es: {self.pin_generado}", "PIN de recuperación"):
                messagebox.showinfo("PIN enviado", f"Se ha enviado un PIN al correo {correo}.")
                self.ingresar_pin()
            else:
                messagebox.showerror("Error", "No se pudo enviar el PIN por correo.")
        else:
            messagebox.showerror("Error", "Correo invalido o no encontrado.")

    def ingresar_pin(self):
        self.limpiar()
        
        # Header
        self.crear_header("Verificar PIN")
        
        # Campo de entrada
        self.pin_entry = self.crear_campo_entrada(self.main_frame, "PIN recibido:")
        
        # Botones
        self.crear_boton_moderno(self.main_frame, "VERIFICAR", self.verificar_pin)
        self.crear_boton_moderno(self.main_frame, "Volver", self.recuperar_contrasena, 'secundario')
        
        # Focus
        self.pin_entry.focus()

    def verificar_pin(self):
        pin_ingresado = self.pin_entry.get().strip()
        
        if not pin_ingresado:
            messagebox.showerror("Error", "Por favor, ingresa el PIN.")
            return
            
        if datetime.now() > self.pin_expira:
            messagebox.showerror("Error", "El PIN ha expirado. Solicita uno nuevo.")
            self.recuperar_contrasena()
        elif pin_ingresado == self.pin_generado:
            self.nueva_contrasena_input()
        else:
            messagebox.showerror("Error", "PIN incorrecto.")

    def nueva_contrasena_input(self):
        self.limpiar()
        
        # Header
        self.crear_header("Nueva Contraseña")
        
        # Campo de entrada con toggle de contraseña
        self.contra_nueva = self.crear_campo_entrada(self.main_frame, "Nueva contraseña:", True)
        
        # Botones
        self.crear_boton_moderno(self.main_frame, "ACTUALIZAR", self.actualizar_contrasena)
        self.crear_boton_moderno(self.main_frame, "Cancelar", self.menu_principal, 'secundario')
        
        # Focus
        self.contra_nueva.focus()

    def actualizar_contrasena(self):
        nueva_contrasena = self.contra_nueva.get().strip()
        
        if not nueva_contrasena:
            messagebox.showerror("Error", "Por favor, ingresa una contraseña.")
            return
            
        if len(nueva_contrasena) < 4:
            messagebox.showerror("Error", "La contraseña debe tener al menos 4 caracteres.")
            return
            
        self.usuarios[self.usuario_actual]["contrasena"] = nueva_contrasena
        
        if guardar_usuarios(self.usuarios):
            messagebox.showinfo("Éxito", "Contraseña actualizada correctamente.")
            self.menu_principal()
        else:
            messagebox.showerror("Error", "No se pudo actualizar la contraseña.")

    def cancelar(self):
        self.root.destroy()

    def iniciar_login_facial(self):
        """Inicia el proceso de login facial"""
        try:
            # Cerrar temporalmente la ventana de login
            self.root.withdraw()
            
            # Realizar login facial
            usuario_reconocido = login_facial_directo()
            
            # Restaurar ventana de login
            self.root.deiconify()
            
            if usuario_reconocido:
                self.procesar_login_exitoso(usuario_reconocido)
            else:
                messagebox.showwarning("Face ID", "No se pudo reconocer el rostro")
                
        except Exception as e:
            self.root.deiconify()
            messagebox.showerror("Error", f"Error en Face ID: {str(e)}")
            
if __name__ == "__main__":
    root = tk.Tk()
    root.resizable(False, False)
    
    def callback_test(*args):
        print("Callback llamado con:", args)
        root.quit()
    
    app = LoginApp(root)
    root.mainloop()