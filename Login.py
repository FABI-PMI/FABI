import tkinter as tk
from tkinter import messagebox, ttk
import json
import os
from datetime import datetime, timedelta
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from twilio.rest import Client

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
        print(f"Error enviando el correo: {e}")
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
        with open(ARCHIVO_USUARIOS, "w") as f:
            json.dump(usuarios, f, indent=4)
        return True
    except IOError as e:
        print(f"Error guardando usuarios: {e}")
        messagebox.showerror("Error", "No se pudo guardar la información del usuario.")
        return False

def generar_pin():
    return str(random.randint(1000, 9999))

class LoginApp:
    def __init__(self, root, callback_jugadores_listos, solo_uno=False):
        self.root = root
        self.callback_jugadores_listos = callback_jugadores_listos
        self.solo_uno = solo_uno
        self.usuarios = cargar_usuarios()
        self.usuario_actual = None
        self.jugadores_login = []
        self.pin_generado = None
        self.pin_expira = None
        self.bot_panel_creado = False  # Bandera para controlar la creación del panel del bot

        # Configurar la ventana - reducir tamaño
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
            'primario': '#667eea',
            'secundario': "#0d739e",
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
        style = ttk.Style()
        style.theme_use('clam')
        
        # Estilo para botones - reducir padding
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
            # Gradiente de azul a púrpura
            r1, g1, b1 = 255, 107, 107   # inicio (rojo claro)  -> #ff6b6b
            r2, g2, b2 = 217, 4, 41      # fin (rojo intenso)   -> #d90429

            
            ratio = i / 550
            r = int(r1 + (r2 - r1) * ratio)
            g = int(g1 + (g2 - g1) * ratio)
            b = int(b1 + (b2 - b1) * ratio)
            
            color = f'#{r:02x}{g:02x}{b:02x}'
            self.canvas.create_line(0, i, 450, i, fill=color, width=1)
        
        # Agregar formas decorativas - reducir tamaño
        self.agregar_formas_decorativas()

    def agregar_formas_decorativas(self):
        """Agrega formas decorativas al fondo - reducidas"""
        # Círculo decorativo 1 - reducido
        self.canvas.create_oval(40, 60, 100, 120, fill="#6bd3ff", stipple='gray25', outline='')
        
        # Rectángulo decorativo 2 - reducido
        self.canvas.create_rectangle(300, 120, 340, 160, fill='#4ecdc4', stipple='gray25', outline='')
        
        # Triángulo decorativo 3 - reducido
        self.canvas.create_polygon(60, 350, 100, 350, 80, 320, fill='#f9ca24', stipple='gray25', outline='')
        
        # Círculo decorativo 4 - reducido
        self.canvas.create_oval(280, 380, 330, 430, fill='#45b7d1', stipple='gray25', outline='')

    def crear_contenedor_principal_con_scroll(self):
        """Crea el contenedor principal con efecto glassmorphism y añade funcionalidad de scroll."""
        # Frame que contendrá el Canvas y la Scrollbar
        scroll_container_frame = tk.Frame(self.root, bg='white', relief='flat', bd=0)
        scroll_container_frame.place(x=35, y=50, width=380, height=450)

        # Crear un Canvas dentro del scroll_container_frame
        self.scroll_canvas = tk.Canvas(scroll_container_frame, bg='white', highlightthickness=0)
        self.scroll_canvas.pack(side="left", fill="both", expand=True)

        # Crear una Scrollbar vertical y vincularla al Canvas
        self.scrollbar = ttk.Scrollbar(scroll_container_frame, orient="vertical", command=self.scroll_canvas.yview)
        self.scrollbar.pack(side="right", fill="y")

        # Configurar el Canvas para usar la Scrollbar
        self.scroll_canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scroll_canvas.bind('<Configure>', self._on_canvas_configure)
        self.scroll_canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        # Crear el main_frame dentro del Canvas
        self.main_frame = tk.Frame(self.scroll_canvas, bg='white', relief='flat', bd=0)
        self.main_frame_id = self.scroll_canvas.create_window((0, 0), window=self.main_frame, anchor="nw")

        # Actualizar el scrollregion del Canvas cuando el tamaño del main_frame cambie
        self.main_frame.bind("<Configure>", self._on_frame_configure)

        # Simular sombra - reducida
        shadow_frame = tk.Frame(self.root, bg='#000000', relief='flat', bd=0)
        shadow_frame.place(x=40, y=55, width=380, height=450)
        
        # Enviar scroll_container_frame al frente
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
        # Resetear la bandera del panel del bot
        self.bot_panel_creado = False
        self.root.update_idletasks()
        self.scroll_canvas.configure(scrollregion=self.scroll_canvas.bbox("all"))

    def crear_header(self, titulo, subtitulo=""):
        """Crea el header con icono y títulos - reducido"""
        # Icono del juego - reducido
        icon_frame = tk.Frame(self.main_frame, bg='white')
        icon_frame.pack(pady=5, fill='x')
        
        icon_canvas = tk.Canvas(icon_frame, width=50, height=50, bg=self.colores['acento'],
                               highlightthickness=0, relief='flat')
        icon_canvas.pack(pady=5)
        
        # Crear círculo para el icono - reducido
        icon_canvas.create_oval(3, 3, 47, 47, fill=self.colores['acento'], outline='')
        icon_canvas.create_text(25, 25, text="🧩", font=('Arial', 20), fill='white')
        
        # Título principal - reducido
        titulo_label = tk.Label(self.main_frame, text=titulo, 
                              font=('Segoe UI', 14, 'bold'),
                              fg=self.colores['texto'], bg='white')
        titulo_label.pack(pady=(5, 3), fill='x')
        
        # Subtítulo - reducido
        if subtitulo:
            subtitulo_label = tk.Label(self.main_frame, text=subtitulo, 
                                     font=('Segoe UI', 9),
                                     fg=self.colores['texto_claro'], bg='white')
            subtitulo_label.pack(pady=(0, 10), fill='x')

    def crear_pestanas(self, pestanas, comando_callback):
        """Crea pestañas modernas - reducidas"""
        tabs_frame = tk.Frame(self.main_frame, bg=self.colores['fondo'], relief='flat', bd=0)
        tabs_frame.pack(fill='x', padx=15, pady=(0, 10))
        
        self.botones_pestana = {}
        
        for i, pestana in enumerate(pestanas):
            btn = tk.Button(tabs_frame, text=pestana,
                          font=('Segoe UI', 8, 'bold'),
                          bg=self.colores['fondo'] if i != 0 else self.colores['primario'],
                          fg=self.colores['texto_claro'] if i != 0 else 'white',
                          relief='flat', bd=0, padx=12, pady=5,
                          command=lambda p=pestana: comando_callback(p))
            btn.pack(side='left', fill='x', expand=True, padx=1)
            self.botones_pestana[pestana] = btn
            
            # Efectos hover
            self.agregar_efecto_hover(btn, pestana)

    def agregar_efecto_hover(self, boton, pestana):
        """Agrega efectos hover a los botones"""
        def on_enter(e):
            if boton['bg'] != self.colores['primario']:
                boton.config(bg='#e9ecef')
        
        def on_leave(e):
            if boton['bg'] != self.colores['primario']:
                boton.config(bg=self.colores['fondo'])
        
        boton.bind("<Enter>", on_enter)
        boton.bind("<Leave>", on_leave)

    def activar_pestana(self, pestana_activa):
        """Activa una pestaña específica"""
        for nombre, boton in self.botones_pestana.items():
            if nombre == pestana_activa:
                boton.config(bg=self.colores['primario'], fg='white')
            else:
                boton.config(bg=self.colores['fondo'], fg=self.colores['texto_claro'])

    def crear_campo_entrada(self, parent, label_text, is_password=False, placeholder=""):
        """Crea un campo de entrada moderno - reducido"""
        # Contenedor del campo - reducido
        field_frame = tk.Frame(parent, bg='white')
        field_frame.pack(fill='x', padx=15, pady=4)
        
        # Label - reducido
        label = tk.Label(field_frame, text=label_text, 
                        font=('Segoe UI', 8, 'bold'),
                        fg=self.colores['texto'], bg='white', anchor='w')
        label.pack(fill='x', pady=(0, 2))
        
        # Entry con estilo moderno - reducido
        entry = tk.Entry(field_frame, font=('Segoe UI', 10),
                        relief='flat', bd=0, bg='#f8f9fa',
                        fg=self.colores['texto'], insertbackground=self.colores['primario'])
        if is_password:
            entry.config(show="*")
        
        entry.pack(fill='x', ipady=8, ipadx=10)
        
        # Efectos de focus
        def on_focus_in(e):
            entry.config(bg='white', relief='solid', bd=2, highlightcolor=self.colores['primario'])
        
        def on_focus_out(e):
            entry.config(bg='#f8f9fa', relief='flat', bd=0)
        
        entry.bind("<FocusIn>", on_focus_in)
        entry.bind("<FocusOut>", on_focus_out)
        
        return entry

    def crear_boton_moderno(self, parent, texto, comando, estilo='primario', ancho_completo=True):
        """Crea un botón con estilo moderno - reducido"""
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
        """Muestra los jugadores ya conectados - reducido"""
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

    def menu_principal(self):
        self.limpiar()
        
        # Header
        if self.solo_uno:
            self.crear_header("LOGIN", "Ingresa para continuar")
        else:
            self.crear_header("LOGIN", "TEST")
        
        # Mostrar jugadores conectados
        self.mostrar_jugadores_conectados()
        

        # Contenedor de formularios
        self.form_container = tk.Frame(self.main_frame, bg='white')
        self.form_container.pack(fill='both', expand=True)
        
        # Mostrar formulario de login por defecto
        self.mostrar_login()
        
        # Botones inferiores
        self.crear_boton_moderno(self.main_frame, "¿Olvidaste tu contraseña?", 
                               self.recuperar_contrasena, 'secundario')
        self.crear_boton_moderno(self.main_frame, "Cancelar", 
                               self.cancelar, 'peligro')

    def cambiar_pestana(self, pestana):
        """Cambia entre las pestañas de login y registro"""
        self.activar_pestana(pestana)
        
        # Limpiar contenedor de formularios
        for widget in self.form_container.winfo_children():
            widget.destroy()
        
        if pestana == "Iniciar Sesión":
            self.mostrar_login()

    def mostrar_login(self):
        """Muestra el formulario de login"""
        # Campos de entrada
        self.usuario_entry = self.crear_campo_entrada(self.form_container, "Usuario/Correo/Teléfono:")
        self.contrasena_entry = self.crear_campo_entrada(self.form_container, "Contraseña:", True)
        
        # Botón de login
        self.crear_boton_moderno(self.form_container, "FaceID", self.iniciar_login_facial)
        self.crear_boton_moderno(self.form_container, "ENTRAR", self.verificar_login)
        
        # Focus en el primer campo
        self.usuario_entry.focus()

    def procesar_login_exitoso(self, nombre_detectado):
        # Asegúrate de tener usuarios cargados
        if not self.usuarios:
            self.usuarios = cargar_usuarios()

        # 1) Comprobar si el usuario existe en usuarios.json
        if nombre_detectado not in self.usuarios:
            messagebox.showerror("Error", f"'{nombre_detectado}' no existe en usuarios.json. Regístralo primero con Face ID.")
            return

        # 2) (Opcional) Restringir a usuarios marcados solo_cara
        # if not self.usuarios[nombre_detectado].get("solo_cara", False):
        #     messagebox.showerror("Error", f"'{nombre_detectado}' no está habilitado para login facial.")
        #     return

        # 3) Reutilizar tu flujo de éxito
        if nombre_detectado not in self.jugadores_login:
            self.jugadores_login.append(nombre_detectado)

        messagebox.showinfo("Éxito", f"Sesión iniciada para: {nombre_detectado}")

        if self.solo_uno:
            self.root.destroy()
            self.callback_jugadores_listos(nombre_detectado)
        elif len(self.jugadores_login) == 2:
            self.root.destroy()
            self.callback_jugadores_listos(self.jugadores_login[0], self.jugadores_login[1])
        else:
            self.menu_principal()

    def mostrar_registro(self):
        """Muestra el formulario de registro"""
        # Campos de entrada
        self.nuevo_usuario = self.crear_campo_entrada(self.form_container, "Usuario:")
        self.nuevo_telefono = self.crear_campo_entrada(self.form_container, "Telefono:")
        self.nuevo_correo = self.crear_campo_entrada(self.form_container, "Correo electrónico:")
        self.nueva_contrasena = self.crear_campo_entrada(self.form_container, "Contraseña:", True)
        

        # Focus en el primer campo
        self.nuevo_usuario.focus()

    def verificar_login(self):
        credencial = self.usuario_entry.get().strip()
        contrasena = self.contrasena_entry.get().strip()
        
        # Validar campos vacíos
        if not credencial or not contrasena:
            messagebox.showerror("Error", "Por favor, completa todos los campos.")
            return self.menu_principal()

        # Verificación normal de usuarios
        paso = False
        for usuario, datos in self.usuarios.items():
            if (credencial == usuario or credencial == datos.get("correo") or credencial == datos.get("telefono")) and self.usuarios[usuario]["contrasena"] == contrasena:
                paso = True
                if credencial not in self.jugadores_login:
                    self.jugadores_login.append(credencial)
                    messagebox.showinfo("Éxito", f"Sesión iniciada para: {usuario}")

                    if self.solo_uno:
                        self.root.destroy()
                        self.callback_jugadores_listos(usuario)
                    elif len(self.jugadores_login) == 2:
                        self.root.destroy()
                        self.callback_jugadores_listos(self.jugadores_login[0], self.jugadores_login[1])
                    else:
                        self.menu_principal()
        
        if not paso:
            messagebox.showerror("Error", "Credencial o contraseña incorrectos.")

    def registrar_usuario(self):
        usuario = self.nuevo_usuario.get().strip()
        telefono = self.nuevo_telefono.get().strip()
        correo = self.nuevo_correo.get().strip()
        contrasena = self.nueva_contrasena.get().strip()

        # Validaciones
        if not usuario or not correo or not contrasena or not telefono:
            messagebox.showerror("Error", "Por favor, completa todos los campos.")
            return

        if usuario in self.usuarios:
            messagebox.showerror("Error", "Este usuario ya existe.")
            return

        if "@" not in correo or "." not in correo:
            messagebox.showerror("Error", "Por favor, ingresa un correo electrónico válido.")
            return
        
        if not (telefono and telefono.isdecimal()):   # '' -> False
             messagebox.showerror("Error", "Por favor, ingresa un numero telefonico válido.")
             return


        # Registrar usuario
        self.usuarios[usuario] = {
            "telefono": telefono,
            "correo": correo, 
            "contrasena": contrasena, 
        }
        
        if guardar_usuarios(self.usuarios):
            messagebox.showinfo("Éxito", "Usuario registrado exitosamente.")
            self.cambiar_pestana("Iniciar Sesión")
        else:
            messagebox.showerror("Error", "No se pudo registrar el usuario. Inténtalo de nuevo.")

    def recuperar_contrasena(self):
        self.limpiar()
        
        # Header
        self.crear_header("Recuperar Contraseña")
        
        # Campo de entrada
        self.correo_entrada = self.crear_campo_entrada(self.main_frame, "Correo/Teléfono:")
        
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
            if datos["telefono"] == correo:
                credencial = "telefono"
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
        elif usuario_encontrado and credencial == "telefono":
            self.pin_generado = generar_pin()
            self.pin_expira = datetime.now() + timedelta(minutes=2)
            self.usuario_actual = usuario_encontrado
            
            if enviar_sms(self.usuarios[usuario_encontrado]["telefono"], f"Tu PIN para recuperar la contraseña es: {self.pin_generado}", "PIN de recuperación"):
                messagebox.showinfo("PIN enviado", f"Se ha enviado un PIN al numero {credencial}.")
                self.ingresar_pin()
            else:
                messagebox.showerror("Error", "No se pudo enviar el PIN por correo.")
        else:
            messagebox.showerror("Error", "Correo o numero telefonico no encontrado.")

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
        
        # Campo de entrada
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
        try:
            from OpenCV import login_with_face_gui
            
            def callback_facial(usuario_reconocido):
                if usuario_reconocido:
                    self.procesar_login_exitoso(usuario_reconocido)
            
            login_with_face_gui(callback_facial)
            
        except ImportError:
            messagebox.showerror("Error", "El módulo de reconocimiento facial no está disponible.")
if __name__ == "__main__":
    root = tk.Tk()
    root.resizable(False, False)
    
    def callback_test(*args):
        print("Callback llamado con:", args)
        root.quit()
    
    app = LoginApp(root, callback_test, solo_uno=True)
    root.mainloop()