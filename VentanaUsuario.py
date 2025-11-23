#VentanaUsuario.py 
import tkinter as tk
from tkinter import messagebox, Canvas, Frame, Label, Button, Entry, filedialog, simpledialog
from PIL import Image, ImageTk, ImageDraw
import json
import base64
import io
import re
import datetime
from GameContext import cargar_usuarios, guardar_usuarios
import hashlib

def hash_password(password):
    """Encripta una contraseña usando SHA-256"""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def verificar_password(password_ingresado, password_hash):
    """Verifica si una contraseña coincide con su hash"""
    return hash_password(password_ingresado) == password_hash

class VentanaUsuario:
    
    def __init__(self, parent, palette, username):
        self.parent = parent
        self.palette = palette
        self.username = username
        self.img = [] 
        print(f"CARGANDO PERFIL DE: {username}")
        self.todos_usuarios = cargar_usuarios()
        
        if not self.todos_usuarios or username not in self.todos_usuarios:
            print(f"❌ Error: Usuario '{username}' no encontrado")
            messagebox.showerror("Error", f"El usuario '{username}' no existe en el sistema")
            return
        
        self.mis_datos = self.todos_usuarios[username]
        
        if not isinstance(self.mis_datos, dict):
            print(f"⚠️ ADVERTENCIA: mis_datos no es un diccionario, tipo: {type(self.mis_datos)}")
            self.mis_datos = {}
        
        if 'usuario' not in self.mis_datos:
            self.mis_datos['usuario'] = username
            print(f"ℹ️ Campo 'usuario' agregado con valor: {username}")
        
        self.modo_edicion = False
        self.entries = {}
        self.nueva_foto = None
        
        # Control de tiempo de inactividad (30 minutos)
        self.ultimo_activity = datetime.datetime.now()
        self.timeout_minutos = 30
        
        self.window = tk.Toplevel(parent)
        self.window.title(f"Perfil de {username}")
        self.window.geometry("600x820")
        self.window.resizable(False, False)
        self.window.configure(bg='#f5f5f5')
        
        # Iniciar verificación de timeout
        self.verificar_timeout()
        
        self.centrar_ventana()
        self.crear_interfaz()
        
        campos_importantes = ['nombre', 'apellido', 'correo', 'telefono']
        datos_vacios = all(not str(self.mis_datos.get(campo, '')).strip() for campo in campos_importantes)
        
        if datos_vacios:
            self.window.after(500, self.mostrar_mensaje_datos_vacios)
    
    def verificar_timeout(self):
        """Verificar si la sesión ha expirado por inactividad"""
        try:
            tiempo_inactivo = datetime.datetime.now() - self.ultimo_activity
            
            if tiempo_inactivo.total_seconds() > (self.timeout_minutos * 60):
                print("⏱️ Sesión expirada por inactividad")
                messagebox.showwarning(
                    "Sesión Expirada",
                    f"⏱️ Tu sesión ha expirado por inactividad.\n\n"
                    f"Por seguridad, la ventana se cerrará.\n\n"
                    f"Tiempo de inactividad: {self.timeout_minutos} minutos"
                )
                self.window.destroy()
                return
            
            self.window.after(60000, self.verificar_timeout)
        except:
            pass
    
    def actualizar_activity(self):
        """Actualizar el timestamp de última actividad"""
        self.ultimo_activity = datetime.datetime.now()
    
    def mostrar_mensaje_datos_vacios(self):
        respuesta = messagebox.askyesno(
            "Perfil Incompleto",
            "⚠️ Tu perfil está incompleto.\n\n"
            "No tienes datos personales registrados.\n\n"
            "¿Deseas completar tu perfil ahora?"
        )
        
        if respuesta:
            self.toggle_edicion()
    
    def centrar_ventana(self):
        self.window.update_idletasks()
        ancho = 600
        alto = 820
        x = (self.window.winfo_screenwidth() // 2) - (ancho // 2)
        y = (self.window.winfo_screenheight() // 2) - (alto // 2)
        self.window.geometry(f'{ancho}x{alto}+{x}+{y}')
    
    def crear_interfaz(self):
        # Canvas con scrollbar
        canvas = Canvas(self.window, bg='#f5f5f5', highlightthickness=0)
        scrollbar = tk.Scrollbar(self.window, orient="vertical", command=canvas.yview)
        
        self.frame_principal = Frame(canvas, bg='#f5f5f5')
        
        self.frame_principal.bind(
            '<Configure>',
            lambda e: canvas.configure(scrollregion=canvas.bbox('all'))
        )
        
        canvas.create_window((0, 0), window=self.frame_principal, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        def scroll_mouse(event):
            self.actualizar_activity()
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind("<MouseWheel>", scroll_mouse)
        
        self.window.bind("<Button>", lambda e: self.actualizar_activity())
        self.window.bind("<Key>", lambda e: self.actualizar_activity())
        
        # ✅ CREAR SECCIONES EN ORDEN
        self.crear_seccion_header()
        self.crear_boton_editar_superior()
        self.crear_seccion_info_personal()
        self.crear_seccion_personalizacion()
        
        if not self.mis_datos.get('es_premium', False):
            self.crear_seccion_upgrade()
        
        self.crear_seccion_botones_inferior()
    
    def crear_seccion_header(self):
        """Header con foto y datos básicos - PERFECTAMENTE CENTRADO"""
        header = Frame(self.frame_principal, bg='#8A1C32')
        header.pack(fill='x', pady=(0, 20))
        
        Frame(header, bg='#8A1C32', height=25).pack()
        
        # ✅ Foto CENTRADA
        foto_container = Frame(header, bg='#8A1C32')
        foto_container.pack(anchor='center')
        
        self.canvas_foto = Canvas(foto_container, width=140, height=140, 
                                   bg='#8A1C32', highlightthickness=0, cursor='hand2')
        self.canvas_foto.pack()
        
        try:
            foto_b64 = self.mis_datos.get('foto_perfil_b64', '')
            
            if foto_b64:
                foto_bytes = base64.b64decode(foto_b64)
                img = Image.open(io.BytesIO(foto_bytes))
                img = img.resize((130, 130), Image.LANCZOS)
                
                mask = Image.new('L', (130, 130), 0)
                draw = ImageDraw.Draw(mask)
                draw.ellipse((0, 0, 130, 130), fill=255)
                img.putalpha(mask)
                
                self.foto_actual = ImageTk.PhotoImage(img, master=self.window)
                self.img.append(self.foto_actual)
                
                self.canvas_foto.create_oval(5, 7, 135, 137, fill='#000000', outline='', stipple='gray50')
                self.canvas_foto.create_oval(5, 5, 135, 135, outline='white', width=5)
                self.canvas_foto.create_image(70, 70, image=self.foto_actual)
            else:
                self.mostrar_placeholder_foto()
        except Exception as e:
            print(f"⚠️ Error cargando foto: {e}")
            self.mostrar_placeholder_foto()
        
        self.canvas_foto.bind('<Button-1>', self.cambiar_foto_perfil)
        
        Label(foto_container, text='📸 Haz clic para cambiar tu foto', 
              font=('Segoe UI', 9, 'italic'), bg='#8A1C32', fg='#f0f0f0').pack(pady=(10, 0))
        
        # ✅ Nombre CENTRADO
        nombre = str(self.mis_datos.get('nombre', '')).strip()
        apellido = str(self.mis_datos.get('apellido', '')).strip()
        segundo_apellido = str(self.mis_datos.get('segundo_apellido', '')).strip()
        
        nombre_completo = f"{nombre} {apellido}"
        if segundo_apellido:
            nombre_completo += f" {segundo_apellido}"
        
        if not nombre_completo.strip():
            nombre_completo = "Usuario sin nombre"
        
        Label(header, text=nombre_completo, 
              font=('Segoe UI', 20, 'bold'), bg='#8A1C32', fg='white',
              wraplength=550).pack(pady=(18, 5))
        
        Label(header, text=f"@{self.username}", 
              font=('Segoe UI', 12), bg='#8A1C32', fg='#e0e0e0').pack(pady=(0, 8))
        
        # ✅ Badge CENTRADO
        es_premium = self.mis_datos.get('es_premium', False)
        
        badge_container = Frame(header, bg='#8A1C32')
        badge_container.pack(pady=15)
        
        if es_premium:
            badge = Label(badge_container, text='👑 Cuenta Premium', 
                         font=('Segoe UI', 11, 'bold'), 
                         bg='#D4AF37', fg='white', 
                         padx=25, pady=8, relief='flat')
        else:
            badge = Label(badge_container, text='🎮 Cuenta Gratuita', 
                         font=('Segoe UI', 11, 'bold'), 
                         bg='#4A5568', fg='white', 
                         padx=25, pady=8, relief='flat')
        badge.pack()
        
        Frame(header, bg='#8A1C32', height=20).pack()
    
    def mostrar_placeholder_foto(self):
        """Mostrar placeholder cuando no hay foto"""
        self.canvas_foto.create_oval(5, 7, 135, 137, fill='#000000', outline='', stipple='gray50')
        self.canvas_foto.create_oval(5, 5, 135, 135, fill='#E5E7EB', outline='white', width=5)
        self.canvas_foto.create_text(70, 70, text='👤', font=('Arial', 55))
    
    def cambiar_foto_perfil(self, event=None):
        """Cambiar la foto de perfil del usuario"""
        self.actualizar_activity()
        
        archivo = filedialog.askopenfilename(
            title='Selecciona tu nueva foto de perfil',
            filetypes=[
                ('Imágenes', '*.png;*.jpg;*.jpeg;*.bmp;*.gif'),
                ('Todos los archivos', '*.*')
            ]
        )
        
        if not archivo:
            return
        
        try:
            img = Image.open(archivo)
            img = img.resize((130, 130), Image.LANCZOS)
            
            mask = Image.new('L', (130, 130), 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0, 130, 130), fill=255)
            img.putalpha(mask)
            
            self.nueva_foto = img
            self.foto_actual = ImageTk.PhotoImage(img, master=self.window)
            self.img.append(self.foto_actual)
            self.canvas_foto.delete('all')
            self.canvas_foto.create_oval(5, 7, 135, 137, fill='#000000', outline='', stipple='gray50')
            self.canvas_foto.create_oval(5, 5, 135, 135, outline='white', width=5)
            self.canvas_foto.create_image(70, 70, image=self.foto_actual)
            
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            foto_b64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            self.mis_datos['foto_perfil_b64'] = foto_b64
            
            self.todos_usuarios[self.username] = self.mis_datos
            if guardar_usuarios(self.todos_usuarios):
                messagebox.showinfo("Éxito", "✅ Foto de perfil actualizada correctamente")
                self.registrar_log('foto_perfil_actualizada')
            else:
                messagebox.showerror("Error", "No se pudo guardar la foto")
                
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar la imagen:\n{e}")
    
    def crear_boton_editar_superior(self):
        """✅ Botón editar PERFECTAMENTE CENTRADO"""
        contenedor = Frame(self.frame_principal, bg='#f5f5f5')
        contenedor.pack(fill='x', pady=(0, 20))
        
        self.btn_editar = Button(
            contenedor,
            text='✏️ Editar Perfil',
            font=('Segoe UI', 12, 'bold'),
            bg='#B8405E',
            fg='white',
            command=self.toggle_edicion,
            cursor='hand2',
            relief='flat',
            bd=0,
            width=18,
            padx=25,
            pady=12,
            activebackground='#A03850',
            activeforeground='white'
        )
        self.btn_editar.pack()  # ← Sin anchor, se centra automáticamente

    def crear_seccion_info_personal(self):
        """✅ Sección de información PERFECTAMENTE CENTRADA"""
        # Frame contenedor centrado con ancho fijo
        contenedor = Frame(self.frame_principal, bg='#f5f5f5')
        contenedor.pack(fill='x', pady=(0, 20))
        
        # Frame con ancho fijo para centrar contenido
        frame = Frame(contenedor, bg='white', relief='flat', bd=1)
        frame.pack(padx=30)  # ← Padding igual en ambos lados
        
        # Título
        titulo_frame = Frame(frame, bg='white')
        titulo_frame.pack(fill='x', pady=(18, 5))
        
        Label(titulo_frame, text='📋 Información Personal', 
              font=('Segoe UI', 15, 'bold'), bg='white', fg='#2c3e50').pack()
        
        # Línea decorativa
        Canvas(frame, bg='#8A1C32', height=2, highlightthickness=0).pack(fill='x', padx=40, pady=(5, 15))
        
        # Campos
        campos_container = Frame(frame, bg='white')
        campos_container.pack(pady=(0, 20), padx=30)
        
        campos = [
            ('👤 Usuario', 'usuario', True),
            ('✏️ Nombre', 'nombre', True),
            ('✏️ Apellido', 'apellido', True),
            ('✏️ Segundo Apellido', 'segundo_apellido', True),
            ('📧 Correo Electrónico', 'correo', True),
            ('📱 Teléfono', 'telefono', True),
            ('🌍 Nacionalidad', 'nacionalidad', True),
            ('🗣️ Idioma', 'idioma', True),
            ('🎂 Fecha de Nacimiento', 'fecha_nacimiento', False),
        ]
        
        for etiqueta, clave, editable in campos:
            self.crear_campo_moderno(campos_container, etiqueta, clave, editable)
    
    def crear_campo_moderno(self, parent, etiqueta, clave, editable=True):
        """✅ Campo PERFECTAMENTE CENTRADO"""
        campo_frame = Frame(parent, bg='white')
        campo_frame.pack(pady=5)
        
        # Etiqueta centrada
        Label(campo_frame, text=etiqueta, 
              font=('Segoe UI', 9, 'bold'), bg='white', fg='#34495e',
              width=22, anchor='w').pack()
        
        # Entry
        valor_raw = self.mis_datos.get(clave, '')
        valor_actual = str(valor_raw).strip() if valor_raw is not None else ''
        
        entry = Entry(campo_frame, 
                     font=('Segoe UI', 10), 
                     bg='#f8f9fa', 
                     fg='#2c3e50', 
                     relief='solid', 
                     bd=1,
                     width=38,
                     highlightthickness=2,
                     highlightbackground='#e0e0e0',
                     highlightcolor='#8A1C32',
                     disabledbackground='#f0f0f0',
                     disabledforeground='#7f8c8d',
                     justify='left')  # ← Alineado a la izquierda dentro del entry
        
        entry.pack(ipady=6)
        entry.insert(0, valor_actual)
        
        if not editable:
            entry.config(state='disabled')
        else:
            entry.config(state='readonly')
        
        self.entries[clave] = {'widget': entry, 'editable': editable}
    
    def crear_seccion_personalizacion(self):
        """✅ Personalización PERFECTAMENTE CENTRADA"""
        contenedor = Frame(self.frame_principal, bg='#f5f5f5')
        contenedor.pack(fill='x', pady=(0, 15))
        
        frame = Frame(contenedor, bg='white', relief='flat', bd=1)
        frame.pack(padx=30)
        
        # Título
        titulo_frame = Frame(frame, bg='white')
        titulo_frame.pack(fill='x', pady=(18, 5))
        
        Label(titulo_frame, text='🎨 Personalización del Juego', 
              font=('Segoe UI', 15, 'bold'), bg='white', fg='#2c3e50').pack()
        
        Canvas(frame, bg='#C85A7A', height=2, highlightthickness=0).pack(fill='x', padx=40, pady=(5, 15))
        
        personalizacion = self.mis_datos.get('personalizacion', {})
        
        if not personalizacion or not isinstance(personalizacion, dict):
            personalizacion = {
                'color': '#a4244d',
                'tema': 'claro',
                'cancion': ''
            }
        
        content_frame = Frame(frame, bg='white')
        content_frame.pack(pady=(0, 15))
        
        # Color Favorito
        color_frame = Frame(content_frame, bg='white')
        color_frame.pack(pady=8)
        
        Label(color_frame, text='🎨 Color Favorito:', 
              font=('Segoe UI', 10, 'bold'), bg='white', fg='#34495e').pack()
        
        color = personalizacion.get('color', '#a4244d')
        
        color_display = Frame(color_frame, bg='white')
        color_display.pack(pady=4)
        
        color_canvas = Canvas(color_display, width=50, height=30, bg=color, 
                             highlightthickness=2, highlightbackground='#34495e',
                             relief='raised', bd=1)
        color_canvas.pack(side='left', padx=8)
        
        Label(color_display, text=color, 
              font=('Segoe UI', 9, 'bold'), bg='white', fg='#2c3e50').pack(side='left')
        
        # Tema
        tema_frame = Frame(content_frame, bg='white')
        tema_frame.pack(pady=8)
        
        Label(tema_frame, text='🌓 Tema:', 
              font=('Segoe UI', 10, 'bold'), bg='white', fg='#34495e').pack()
        
        tema = personalizacion.get('tema', 'claro')
        tema_texto = tema.capitalize()
        tema_icono = '☀️' if tema == 'claro' else '🌙' if tema == 'oscuro' else '🌗'
        
        Label(tema_frame, text=f"{tema_icono} {tema_texto}", 
              font=('Segoe UI', 9), bg='white', fg='#2c3e50').pack(pady=4)
        
        # Música
        musica_frame = Frame(content_frame, bg='white')
        musica_frame.pack(pady=8)
        
        Label(musica_frame, text='🎵 Música de Fondo:', 
              font=('Segoe UI', 10, 'bold'), bg='white', fg='#34495e').pack()
        
        cancion = personalizacion.get('cancion', '')
        if not cancion or cancion.strip() == '':
            cancion = '🔇 Ninguna configurada'
        else:
            cancion = f'🎶 {cancion}'
        
        Label(musica_frame, text=cancion, 
              font=('Segoe UI', 9), bg='white', fg='#2c3e50',
              wraplength=400, justify='center').pack(pady=4)
        
        # ✅ Botón centrado
        Button(frame, text='✨ Cambiar Personalización', 
               font=('Segoe UI', 10, 'bold'), 
               bg='#C85A7A', fg='white',
               command=self.abrir_personalizacion, 
               cursor='hand2',
               relief='flat', bd=0, 
               padx=25, pady=10,
               activebackground='#B04868',
               activeforeground='white').pack(pady=(8, 20))
    
    def crear_seccion_upgrade(self):
        """✅ Upgrade Premium PERFECTAMENTE CENTRADO"""
        contenedor = Frame(self.frame_principal, bg='#f5f5f5')
        contenedor.pack(fill='x', pady=(0, 15))
        
        frame = Frame(contenedor, bg='#FFF8E7', relief='flat', bd=1)
        frame.pack(padx=30)
        
        # Título
        titulo_frame = Frame(frame, bg='#FFF8E7')
        titulo_frame.pack(fill='x', pady=(18, 5))
        
        Label(titulo_frame, text='👑 Actualiza a Premium', 
              font=('Segoe UI', 15, 'bold'), bg='#FFF8E7', fg='#8B6914').pack()
        
        Canvas(frame, bg='#D4AF37', height=2, highlightthickness=0).pack(fill='x', padx=40, pady=(5, 15))
        
        # Contenido
        content = Frame(frame, bg='#FFF8E7')
        content.pack(pady=(0, 15), padx=30)
        
        Label(content, text='✨ Beneficios de la Cuenta Premium:', 
              font=('Segoe UI', 10, 'bold'), bg='#FFF8E7', fg='#8B6914').pack(pady=(0, 8))
        
        beneficios = [
            '✅ Acceso ilimitado a todas las funciones',
            '✅ Sin anuncios ni interrupciones',
            '✅ Contenido exclusivo y niveles especiales',
            '✅ Soporte prioritario 24/7'
        ]
        
        for beneficio in beneficios:
            Label(content, text=beneficio, 
                  font=('Segoe UI', 9), bg='#FFF8E7', fg='#8B6914').pack(pady=2)
        
        # Campo de tarjeta
        Label(content, text='💳 Número de tarjeta de crédito:', 
              font=('Segoe UI', 10, 'bold'), bg='#FFF8E7', fg='#8B6914').pack(pady=(12, 6))
        
        self.entry_tarjeta = Entry(content, font=('Segoe UI', 10), 
                                   bg='white', fg='#999',
                                   relief='solid', bd=2,
                                   width=26,
                                   highlightthickness=2,
                                   highlightbackground='#ddd',
                                   highlightcolor='#D4AF37',
                                   justify='center')
        self.entry_tarjeta.insert(0, '1234 5678 9012 3456')
        self.entry_tarjeta.pack(pady=(0, 12), ipady=6)
        
        def on_focus_tarjeta(e):
            self.actualizar_activity()
            if self.entry_tarjeta.get() == '1234 5678 9012 3456':
                self.entry_tarjeta.delete(0, tk.END)
                self.entry_tarjeta.config(fg='black')
        
        def on_focusout_tarjeta(e):
            if self.entry_tarjeta.get().strip() == '':
                self.entry_tarjeta.insert(0, '1234 5678 9012 3456')
                self.entry_tarjeta.config(fg='#999')
        
        self.entry_tarjeta.bind('<FocusIn>', on_focus_tarjeta)
        self.entry_tarjeta.bind('<FocusOut>', on_focusout_tarjeta)
        
        # ✅ Botón centrado
        Button(frame, text='👑 Activar Premium Ahora', 
               font=('Segoe UI', 10, 'bold'), 
               bg='#D4AF37', fg='white',
               command=self.activar_premium, 
               cursor='hand2',
               relief='flat', bd=0, 
               padx=25, pady=10,
               activebackground='#C19B2B',
               activeforeground='white').pack(pady=(0, 20))
    
    def crear_seccion_botones_inferior(self):
        """✅ Botón cerrar PERFECTAMENTE CENTRADO"""
        contenedor = Frame(self.frame_principal, bg='#f5f5f5')
        contenedor.pack(fill='x', pady=(0, 25))
        
        Button(
            contenedor,
            text='✖ Cerrar Ventana',
            font=('Segoe UI', 11, 'bold'),
            bg='#4A5568',
            fg='white',
            command=self.cerrar_ventana,
            cursor='hand2',
            relief='flat',
            bd=0,
            width=18,
            padx=25,
            pady=12,
            activebackground='#3A4555',
            activeforeground='white'
        ).pack()  # ← Sin anchor, se centra automáticamente
    
    def toggle_edicion(self):
        """Alternar modo de edición"""
        self.actualizar_activity()
        
        if self.modo_edicion:
            if self.guardar_cambios():
                self.modo_edicion = False
                self.btn_editar.config(text='✏️ Editar Perfil', bg='#B8405E', activebackground='#A03850')
                
                for clave, entry_info in self.entries.items():
                    widget = entry_info['widget']
                    editable = entry_info['editable']
                    
                    if editable:
                        widget.config(state='readonly', bg='#f8f9fa')
                    else:
                        widget.config(state='disabled', bg='#f0f0f0')
                
                messagebox.showinfo("Éxito", "✅ Los cambios se guardaron correctamente")
        else:
            self.modo_edicion = True
            self.btn_editar.config(text='💾 Guardar Cambios', bg='#2E8B57', activebackground='#27764A')
            
            for clave, entry_info in self.entries.items():
                widget = entry_info['widget']
                editable = entry_info['editable']
                
                if editable:
                    widget.config(state='normal', bg='white')
            
            messagebox.showinfo("Modo Edición", 
                              "✏️ Ahora puedes editar tus datos.\n\n"
                              "Presiona 'Guardar Cambios' cuando termines.")
    
    def verificar_contrasena(self):
        """Solicitar y verificar la contraseña del usuario"""
        contraseña = simpledialog.askstring(
            "Verificación de Seguridad",
            "🔒 Por tu seguridad, ingresa tu contraseña actual:",
            show='*'
        )
        
        if not contraseña:
            return False
        
        contraseña_guardada = self.mis_datos.get('contrasena', '')
        
        # ✅ Verificar con hash
        if not verificar_password(contraseña, contraseña_guardada):
            messagebox.showerror(
                "Error de Seguridad",
                "❌ Contraseña incorrecta.\n\n"
                "No se puede continuar con la operación."
            )
            return False
        
        return True
    
    def validar_username(self, username):
        """Validar formato del username"""
        if not username:
            return False, "El usuario no puede estar vacío"
        
        if len(username) < 3:
            return False, "El usuario debe tener al menos 3 caracteres"
        
        if len(username) > 20:
            return False, "El usuario no puede tener más de 20 caracteres"
        
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            return False, "El usuario solo puede contener letras, números y guión bajo (_)"
        
        return True, "OK"
    
    def registrar_log(self, accion, detalles=''):
        """Registrar acciones importantes en el log de auditoría"""
        try:
            log_entry = {
                'timestamp': datetime.datetime.now().isoformat(),
                'usuario': self.username,
                'accion': accion,
                'detalles': detalles
            }
            
            try:
                with open('logs_auditoria.json', 'r', encoding='utf-8') as f:
                    logs = json.load(f)
            except:
                logs = []
            
            logs.append(log_entry)
            
            with open('logs_auditoria.json', 'w', encoding='utf-8') as f:
                json.dump(logs[-1000:], f, indent=2, ensure_ascii=False)
            
        except Exception as e:
            print(f"⚠️ Error registrando log: {e}")
    
    def guardar_cambios(self):
        """Guardar los cambios realizados en el perfil"""
        self.actualizar_activity()
        
        try:
            valores = {}
            
            for clave, entry_info in self.entries.items():
                widget = entry_info['widget']
                valor = widget.get().strip()
                valores[clave] = valor
            
            # Verificar si se intenta cambiar el usuario
            nuevo_usuario = valores.get('usuario', '').strip()
            usuario_cambio = nuevo_usuario and nuevo_usuario != self.username
            
            if usuario_cambio:
                messagebox.showinfo(
                    "Verificación Requerida",
                    "🔒 Detectamos que intentas cambiar tu usuario.\n\n"
                    "Por seguridad, necesitamos verificar tu identidad."
                )
                
                if not self.verificar_contrasena():
                    return False
                
                es_valido, mensaje = self.validar_username(nuevo_usuario)
                if not es_valido:
                    messagebox.showerror("Usuario Inválido", f"❌ {mensaje}")
                    return False
                
                if nuevo_usuario in self.todos_usuarios:
                    messagebox.showerror("Error", 
                                       f"❌ El nombre de usuario '{nuevo_usuario}' ya existe.\n\n"
                                       "Por favor elige otro nombre de usuario.")
                    return False
            
            # Validar correo electrónico
            correo = valores.get('correo', '')
            patron_correo = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
            
            if not re.match(patron_correo, correo):
                messagebox.showerror("Error", 
                                   "❌ El correo electrónico no es válido.\n\n"
                                   "Formato correcto: usuario@dominio.com")
                return False
            
            # Validar teléfono
            telefono = valores.get('telefono', '')
            
            if not telefono.isdigit():
                messagebox.showerror("Error", 
                                   "❌ El teléfono solo debe contener números.\n\n"
                                   "Ejemplo: 88887777")
                return False
            
            # Validar campos requeridos
            campos_requeridos = ['nombre', 'apellido', 'correo', 'telefono', 
                                'nacionalidad', 'idioma']
            
            for campo in campos_requeridos:
                valor = valores.get(campo, '')
                if not valor:
                    messagebox.showerror("Error", 
                                       f"❌ El campo '{campo}' es obligatorio.\n\n"
                                       "Por favor completa todos los campos.")
                    return False
            
            # Actualizar datos
            for clave, valor in valores.items():
                self.mis_datos[clave] = valor
            
            # Guardar cambios
            if usuario_cambio:
                del self.todos_usuarios[self.username]
                self.todos_usuarios[nuevo_usuario] = self.mis_datos
                
                self.registrar_log('cambio_usuario', 
                                  f"{self.username} → {nuevo_usuario}")
            else:
                self.todos_usuarios[self.username] = self.mis_datos
                self.registrar_log('actualizacion_perfil')
            
            if guardar_usuarios(self.todos_usuarios):
                if usuario_cambio:
                    usuario_anterior = self.username
                    self.username = nuevo_usuario
                    self.window.title(f"Perfil de {nuevo_usuario}")
                    
                    messagebox.showinfo(
                        "✅ Usuario Actualizado", 
                        f"📝 Tu usuario ha sido actualizado exitosamente.\n\n"
                        f"Usuario anterior: {usuario_anterior}\n"
                        f"Usuario nuevo: {nuevo_usuario}\n\n"
                        f"⚠️ IMPORTANTE:\n"
                        f"La próxima vez que inicies sesión, debes usar:\n"
                        f"👉 Usuario: {nuevo_usuario}\n"
                        f"👉 Contraseña: (la misma de siempre)\n\n"
                        f"📋 Este cambio ha sido registrado en el log de auditoría."
                    )
                
                return True
            else:
                messagebox.showerror("Error", 
                                   "❌ No se pudieron guardar los cambios.\n\n"
                                   "Intenta nuevamente.")
                return False
                
        except Exception as e:
            messagebox.showerror("Error", f"❌ Error al guardar:\n\n{str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def activar_premium(self):
        """Activar cuenta premium del usuario"""
        self.actualizar_activity()
        
        tarjeta = self.entry_tarjeta.get().strip()
        
        if not tarjeta or tarjeta == '1234 5678 9012 3456':
            messagebox.showwarning("Advertencia", 
                                 "⚠️ Por favor ingresa un número de tarjeta válido")
            return
        
        if len(tarjeta) < 10:
            messagebox.showerror("Error", 
                               "❌ El número de tarjeta es muy corto.")
            return
        
        messagebox.showinfo(
            "Verificación Requerida",
            "🔒 Por seguridad, necesitamos verificar tu identidad\n"
            "antes de procesar el pago."
        )
        
        if not self.verificar_contrasena():
            return
        
        respuesta = messagebox.askyesno(
            "Confirmar Upgrade",
            "👑 ¿Deseas activar tu cuenta Premium?\n\n"
            "Se te cobrará según los términos del servicio."
        )
        
        if not respuesta:
            return
        
        try:
            self.mis_datos['es_premium'] = True
            self.mis_datos['tarjeta'] = tarjeta
            self.todos_usuarios[self.username] = self.mis_datos
            
            if guardar_usuarios(self.todos_usuarios):
                self.registrar_log('activacion_premium', f'Tarjeta: ****{tarjeta[-4:]}')
                
                messagebox.showinfo(
                    "¡Bienvenido a Premium!",
                    "👑 Tu cuenta ha sido actualizada a Premium exitosamente.\n\n"
                    "🎉 ¡Disfruta de todos los beneficios!"
                )
                self.window.destroy()
                VentanaUsuario(self.parent, self.palette, self.username)
            else:
                messagebox.showerror("Error", "❌ No se pudo activar Premium.")
                
        except Exception as e:
            messagebox.showerror("Error", f"❌ Error: {str(e)}")
    
    def abrir_personalizacion(self):
        """Abrir ventana de personalización"""
        self.actualizar_activity()
        
        respuesta = messagebox.askyesno(
            "Abrir Personalización",
            "✨ ¿Deseas abrir la ventana de personalización?\n\n"
            "Podrás cambiar colores, tema y música."
        )
        
        if not respuesta:
            return
        
        try:
            from ventana_personalizacion import ColorSelectorApp
            
            self.window.withdraw()
            
            personalizacion_root = tk.Tk()
            
            def cuando_cierra_personalizacion():
                """Callback cuando se cierra personalización"""
                personalizacion_root.destroy()
                self.window.deiconify()
                # Recargar datos por si cambió algo
                self.todos_usuarios = cargar_usuarios()
                if self.username in self.todos_usuarios:
                    self.mis_datos = self.todos_usuarios[self.username]
            
            app = ColorSelectorApp(personalizacion_root)
            personalizacion_root.protocol("WM_DELETE_WINDOW", cuando_cierra_personalizacion)
            personalizacion_root.mainloop()
            
        except ImportError as e:
            self.window.deiconify()
            messagebox.showerror(
                "Error",
                f"❌ No se pudo cargar el módulo de personalización.\n\n"
                f"Asegúrate de que el archivo ventana_personalizacion.py existe.\n\n"
                f"Error: {e}"
            )
        except Exception as e:
            self.window.deiconify()
            import traceback
            traceback.print_exc()
            messagebox.showerror("Error", f"❌ Error: {str(e)}")
    
    def cerrar_ventana(self):
        """Cerrar la ventana de perfil"""
        self.actualizar_activity()
        
        if self.modo_edicion:
            respuesta = messagebox.askyesno(
                "Cambios sin guardar",
                "⚠️ Tienes cambios sin guardar.\n\n"
                "¿Estás seguro de que deseas salir?"
            )
            
            if not respuesta:
                return
        
        print(f"\n👋 Cerrando ventana de perfil de {self.username}")
        self.registrar_log('cierre_sesion')
        self.window.destroy()


# ✅ EJEMPLO DE USO
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    
    # Simular paleta de colores (normalmente viene de PaletaColores.py)
    class PaletaMock:
        pass
    
    palette = PaletaMock()
    
    # Abrir ventana de perfil (reemplaza "tu_usuario" con un usuario real)
    try:
        VentanaUsuario(root, palette, "marco")
    except Exception as e:
        print(f"Error: {e}")
        messagebox.showerror("Error", f"No se pudo abrir el perfil:\n{e}")
    
    root.mainloop()