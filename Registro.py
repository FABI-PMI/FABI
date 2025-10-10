#Registro
import tkinter as tk
import re
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk, ImageDraw
import io
from datetime import datetime
from Login import cargar_usuarios, guardar_usuarios
import cv2
import os
import pickle
import base64
import numpy as np
from tkcalendar import DateEntry

class Registro:
    def __init__(self, root, callback_abrir_login=None):
        self.root = root
        self.callback_abrir_login = callback_abrir_login
        self.root.title("Registro - Avatars VS Rooks")
        
        # Configuración de ventana - más pequeña y centrada
        self.root.geometry("450x550")
        self.root.resizable(False, False)
        
    
        logo_path = os.path.join(os.path.dirname(__file__), "Logo.jpg")
        img = Image.open(logo_path).resize((128, 128), Image.LANCZOS)
        self._logo_img = ImageTk.PhotoImage(img)
        
        # Centrar ventana
        self.centrar_ventana()
        
        # Colores del tema (mismo que Login)
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
        }

        # Variables
        self.imagen_perfil = None
        self._avatar_photo = None
        self.avatar_canvas = None
        self.mostrar_pass1 = False
        self.mostrar_pass2 = False
        self.face_id_registered = False
        self.face_id_filename = None  # Guardar solo el nombre del archivo
        self.face_canvas = None
        self._face_oval = None
        self._face_icon = None
        
        # Variables paso 1
        self.var_nombre = tk.StringVar()
        self.var_apellido = tk.StringVar()
        self.var_segundo_apellido = tk.StringVar()
        self.var_correo = tk.StringVar()
        self.var_telefono = tk.StringVar()
        self.var_username = tk.StringVar()
        self.var_password = tk.StringVar()
        self.var_confirmar_password = tk.StringVar()
        
        # Variables paso 2
        self.var_nacionalidad = tk.StringVar()
        self.var_idioma = tk.StringVar()
        self.var_tarjeta = tk.StringVar()

        self.crear_interfaz()

    def centrar_ventana(self):
        """Centra la ventana en la pantalla"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def crear_interfaz(self):
        # Canvas principal con gradiente (igual que Login)
        self.canvas = tk.Canvas(self.root, width=450, height=550, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        
        # Gradiente
        for i in range(550):
            r1, g1, b1 = 138, 28, 50
            r2, g2, b2 = 97, 20, 35
            
            ratio = i / 550
            r = int(r1 + (r2 - r1) * ratio)
            g = int(g1 + (g2 - g1) * ratio)
            b = int(b1 + (b2 - b1) * ratio)
            
            color = f'#{r:02x}{g:02x}{b:02x}'
            self.canvas.create_line(0, i, 450, i, fill=color, width=1)
        
        # Formas decorativas
        self.canvas.create_oval(40, 60, 100, 120, fill="#6bd3ff", stipple='gray25', outline='')
        self.canvas.create_rectangle(300, 120, 340, 160, fill='#4ecdc4', stipple='gray25', outline='')
        self.canvas.create_polygon(60, 350, 100, 350, 80, 320, fill='#f9ca24', stipple='gray25', outline='')
        
        # Contenedor con scroll
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
        
        self.crear_paso1()
        self.crear_paso2()
        self.mostrar_paso(1)
    
    def _on_frame_configure(self, event):
        self.scroll_canvas.configure(scrollregion=self.scroll_canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        self.scroll_canvas.itemconfig(self.main_frame_id, width=event.width)
        self.scroll_canvas.configure(scrollregion=self.scroll_canvas.bbox("all"))

    def _on_mousewheel(self, event):
        self.scroll_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def limpiar(self):
        """Limpia el contenido del frame principal"""
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        self.root.update_idletasks()
        self.scroll_canvas.configure(scrollregion=self.scroll_canvas.bbox("all"))

    def crear_campo_entrada(self, parent, label_text, is_password=False, variable=None):
        """Crea un campo de entrada moderno (estilo Login)"""
        field_frame = tk.Frame(parent, bg='#C5C5C5')
        field_frame.pack(fill='x', padx=15, pady=3)
        
        label = tk.Label(field_frame, text=label_text, 
                        font=('Segoe UI', 8, 'bold'),
                        fg=self.colores['texto'], bg='#C5C5C5', anchor='w')
        label.pack(fill='x', pady=(0, 2))
        
        entry_container = tk.Frame(field_frame, bg='#f8f9fa', relief='flat', bd=0)
        entry_container.pack(fill='x')
        
        entry = tk.Entry(entry_container, font=('Segoe UI', 9),
                        relief='flat', bd=0, bg='#f8f9fa',
                        fg=self.colores['texto'], insertbackground=self.colores['primario'],
                        textvariable=variable)
        
        if is_password:
            entry.config(show="*")
            entry.pack(side='left', fill='both', expand=True, ipady=6, ipadx=8)
            
            eye_btn = tk.Button(entry_container, text="👁", font=('Segoe UI', 9),
                              relief='flat', bd=0, bg='#f8f9fa',
                              fg=self.colores['texto'], cursor='hand2',
                              padx=8)
            eye_btn.pack(side='right', fill='y')
            
            show_password = {'visible': False, 'entry': entry}
            
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
            
            eye_btn.bind("<ButtonPress-1>", toggle_password)
            eye_btn.bind("<ButtonRelease-1>", hide_password)
            
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
            entry.pack(fill='x', ipady=6, ipadx=8)
            
            def on_focus_in(e):
                entry_container.config(bg='white', relief='solid', bd=2)
                entry.config(bg='white')
            
            def on_focus_out(e):
                entry_container.config(bg='#f8f9fa', relief='flat', bd=0)
                entry.config(bg='#f8f9fa')
            
            entry.bind("<FocusIn>", on_focus_in)
            entry.bind("<FocusOut>", on_focus_out)
        
        return entry

    def crear_boton_moderno(self, parent, texto, comando, estilo='primario'):
        """Crea un botón con estilo moderno"""
        if estilo == 'primario':
            bg_color = self.colores['primario']
            fg_color = 'white'
            hover_color = self.colores['secundario']
        elif estilo == 'secundario':
            bg_color = 'white'
            fg_color = self.colores['primario']
            hover_color = '#f8f9fa'
        else:
            bg_color = self.colores['fondo']
            fg_color = self.colores['texto']
            hover_color = '#e9ecef'
        
        btn = tk.Button(parent, text=texto, command=comando,
                       font=('Segoe UI', 9, 'bold'),
                       bg=bg_color, fg=fg_color,
                       relief='flat', bd=0, pady=8,
                       cursor='hand2')
        
        btn.pack(fill='x', padx=15, pady=4)
        
        def on_enter(e):
            btn.config(bg=hover_color)
        
        def on_leave(e):
            btn.config(bg=bg_color)
        
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        
        return btn
    
    def validar_solo_letras(self, texto):
        return texto.isalpha() or texto.replace(" ", "").isalpha() or texto == ""

    def crear_entrada_nombre(self, parent, variable, placeholder, columna):
        """Crea entrada para nombres (solo letras)"""
        vcmd = (self.root.register(self.validar_solo_letras), '%P')
        
        frame_container = tk.Frame(parent, bg='#C5C5C5')
        frame_container.grid(row=0, column=columna, padx=3, sticky='ew')
        parent.columnconfigure(columna, weight=1)
        
        tk.Label(frame_container, text=placeholder, 
                font=('Segoe UI', 7, 'bold'),
                fg=self.colores['texto'], bg='#C5C5C5', anchor='w').pack(fill='x', pady=(0, 2))
        
        entry = tk.Entry(
            frame_container,
            textvariable=variable,
            font=('Segoe UI', 9),
            bg='#f8f9fa',
            fg=self.colores['texto'],
            bd=0,
            relief=tk.FLAT,
            validate='key',
            validatecommand=vcmd,
            insertbackground=self.colores['primario']
        )
        entry.pack(fill='x', ipady=6, ipadx=8)
        
        def on_focus_in(e):
            entry.config(bg='white', relief='solid', bd=2)
        
        def on_focus_out(e):
            entry.config(bg='#f8f9fa', relief='flat', bd=0)
        
        entry.bind("<FocusIn>", on_focus_in)
        entry.bind("<FocusOut>", on_focus_out)
        
        return entry

    #Ventana 1
    def crear_paso1(self):
        self.frame_paso1 = tk.Frame(self.main_frame, bg='#C5C5C5')
        
        # Header con botón de Login
        header_container = tk.Frame(self.frame_paso1, bg='#C5C5C5')
        header_container.pack(fill='x', pady=8)
        
                
        # Botón Login arriba a la izquierda
        btn_login_container = tk.Frame(header_container, bg='#C5C5C5')
        btn_login_container.place(x=15, y=0)
        tk.Button(
            btn_login_container,
            text='← Login',
            font=('Segoe UI', 8, 'bold'),
            bg=self.colores['primario'],
            fg='white',
            bd=0,
            cursor='hand2',
            padx=12,
            pady=4,
            command=self.volver_a_login
        ).pack()
                        # Botón Face ID arriba a la derecha (estilo Login, usando pack para que no se 'aplane')
        btn_face_container = tk.Frame(header_container, bg='#C5C5C5')
        btn_face_container.pack(side='right', padx=(0, 15), pady=(4, 0))
        btn_face_container.lift()

        self.btn_face_recognition = tk.Button(
            btn_face_container,
            text='👤',
            font=('Arial', 16),
            bg=self.colores['primario'],
            fg='white',
            bd=0,
            width=2,
            cursor='hand2',
            command=self.activar_face_recognition
        )
        self.btn_face_recognition.pack()

        self.label_face_status = tk.Label(
            btn_face_container,
            text='Face ID',
            font=('Arial', 6, 'bold'),
            bg='#C5C5C5',
            fg='#2c3e50'
        )
        self.label_face_status.pack(pady=(1, 0))
        
                # Avatar circular clickeable (selección de foto)
        avatar_container = tk.Frame(self.frame_paso1, bg='#C5C5C5')
        avatar_container.pack(expand=True, pady=(30, 0))

        self.avatar_canvas = tk.Canvas(
            avatar_container, width=110, height=110,
            bg='#C5C5C5', highlightthickness=0, cursor='hand2'
        )
        self.avatar_canvas.pack()

        # Placeholder inicial
        self.avatar_canvas.create_oval(5, 5, 105, 105, fill='#E5E7EB', outline=self.colores['primario'], width=3)
        self.avatar_canvas.create_text(55, 55, text='＋', font=('Segoe UI', 26, 'bold'), fill=self.colores['primario'])
        self.avatar_canvas.bind('<Button-1>', self.seleccionar_foto)

        tk.Label(
            avatar_container,
            text='Toca el círculo para elegir tu foto',
            font=('Segoe UI', 8),
            bg='#C5C5C5',
            fg=self.colores['texto_claro']
        ).pack(pady=(6, 0))
        
        # Título
        tk.Label(self.frame_paso1, text="Crear Cuenta",
                font=('Segoe UI', 12, 'bold'),
                fg=self.colores['texto'], bg='#C5C5C5').pack(pady=(6, 2))
        
        tk.Label(self.frame_paso1, text="Únete a la aventura",
                font=('Segoe UI', 8),
                fg=self.colores['texto_claro'], bg='#C5C5C5').pack(pady=(0, 10))
        
        # Grid de nombres (3 columnas)
        frame_nombres = tk.Frame(self.frame_paso1, bg='#C5C5C5')
        frame_nombres.pack(fill='x', padx=15, pady=3)
        
        self.entry_nombre = self.crear_entrada_nombre(frame_nombres, self.var_nombre, "Nombre", 0)
        self.entry_apellido = self.crear_entrada_nombre(frame_nombres, self.var_apellido, "Apellido", 1)
        self.entry_segundo_apellido = self.crear_entrada_nombre(frame_nombres, self.var_segundo_apellido, "2° Apellido", 2)
        
        # Campos normales
        self.entry_correo = self.crear_campo_entrada(self.frame_paso1, "Correo:", variable=self.var_correo)
        self.entry_telefono = self.crear_campo_entrada(self.frame_paso1, "Teléfono:", variable=self.var_telefono)
        self.entry_username = self.crear_campo_entrada(self.frame_paso1, "Usuario:", variable=self.var_username)
        self.entry_pass1 = self.crear_campo_entrada(self.frame_paso1, "Contraseña:", is_password=True, variable=self.var_password)
        self.entry_pass2 = self.crear_campo_entrada(self.frame_paso1, "Confirmar:", is_password=True, variable=self.var_confirmar_password)
        
        # Botones
        self.crear_boton_moderno(self.frame_paso1, "Siguiente →", self.ir_a_ventana2)
    
    # PASO 2
    def crear_paso2(self):
        self.frame_paso2 = tk.Frame(self.main_frame, bg='#C5C5C5')
        
        # Header
        tk.Label(self.frame_paso2, text="Información Adicional",
                font=('Segoe UI', 12, 'bold'),
                fg=self.colores['texto'], bg='#C5C5C5').pack(pady=(15, 2))
        
        tk.Label(self.frame_paso2, text="Completa tu perfil",
                font=('Segoe UI', 8),
                fg=self.colores['texto_claro'], bg='#C5C5C5').pack(pady=(0, 10))
        
        # Nacionalidad
        field_frame = tk.Frame(self.frame_paso2, bg='#C5C5C5')
        field_frame.pack(fill='x', padx=15, pady=3)
        
        tk.Label(field_frame, text="Nacionalidad:", 
                font=('Segoe UI', 8, 'bold'),
                fg=self.colores['texto'], bg='#C5C5C5', anchor='w').pack(fill='x', pady=(0, 2))
        
        style = ttk.Style(self.root)   # ← asociar al root de Registro
        style.configure('Custom.TCombobox', fieldbackground='#f8f9fa')
        
        
        combo_nac = ttk.Combobox(
            field_frame,
            textvariable=self.var_nacionalidad,
            font=('Segoe UI', 9),
            state='readonly',
            values=['🇨🇷 Costa Rica', '🇲🇽 México', '🇺🇸 Estados Unidos', '🇪🇸 España', 
                    '🇦🇷 Argentina', '🇨🇴 Colombia', '🇨🇱 Chile', '🇵🇪 Perú'],
            style='Custom.TCombobox'
        )
        combo_nac.pack(fill='x', ipady=6)
        
        # Fecha de nacimiento con calendario
        field_frame = tk.Frame(self.frame_paso2, bg='#C5C5C5')
        field_frame.pack(fill='x', padx=15, pady=3)
        
        tk.Label(field_frame, text="📅 Fecha de Nacimiento:", 
                font=('Segoe UI', 8, 'bold'),
                fg=self.colores['texto'], bg='#C5C5C5', anchor='w').pack(fill='x', pady=(0, 2))
        
        self.date_entry = DateEntry(
            field_frame,
            width=30,
            background=self.colores['primario'],
            foreground='white',
            borderwidth=0,
            font=('Segoe UI', 9),
            date_pattern='dd/mm/yyyy',
            maxdate=datetime.now(),  # No permite fechas futuras
            year=2000,
            month=1,
            day=1
        )
        self.date_entry.pack(fill='x', ipady=6)
        
        # Idioma
        field_frame = tk.Frame(self.frame_paso2, bg='#C5C5C5')
        field_frame.pack(fill='x', padx=15, pady=3)
        
        tk.Label(field_frame, text="Idioma:", 
                font=('Segoe UI', 8, 'bold'),
                fg=self.colores['texto'], bg='#C5C5C5', anchor='w').pack(fill='x', pady=(0, 2))
        
        combo_idioma = ttk.Combobox(
            field_frame,
            textvariable=self.var_idioma,
            font=('Segoe UI', 9),
            state='readonly',
            values=['🇪🇸 Español', '🇺🇸 Inglés', '🇧🇷 Portugués', '🇫🇷 Francés'],
            style='Custom.TCombobox'
        )
        combo_idioma.pack(fill='x', ipady=6)
        
        # Tarjeta de crédito
        tk.Label(
            self.frame_paso2,
            text="💳 Tarjeta de Crédito (Opcional)",
            font=('Segoe UI', 9, 'bold'),
            bg='#C5C5C5',
            fg=self.colores['texto']
        ).pack(anchor='w', padx=15, pady=(10, 5))
        
        frame_tarjeta = tk.Frame(self.frame_paso2, bg='#1F2937', bd=0)
        frame_tarjeta.pack(fill='x', padx=15, pady=5, ipady=15, ipadx=15)
        
        # Chip
        tk.Label(
            frame_tarjeta,
            text="◼️",
            font=('Arial', 20),
            bg='#FBBF24',
            fg='#FBBF24',
            padx=15,
            pady=10
        ).pack(anchor='w', pady=(0, 10))
        
        self.entry_tarjeta = tk.Entry(
            frame_tarjeta,
            textvariable=self.var_tarjeta,
            font=('Arial', 14, 'bold'),
            bg='#1F2937',
            fg='#D1D5DB',
            bd=0,
            insertbackground='white'
        )
        self.entry_tarjeta.pack(fill='x', pady=8)
        self.entry_tarjeta.insert(0, "1234 5678 9012 3456")
        self.entry_tarjeta.config(fg='#6B7280')
        
        def on_tarjeta_click(e):
            if self.entry_tarjeta.get() == "1234 5678 9012 3456":
                self.entry_tarjeta.delete(0, tk.END)
                self.entry_tarjeta.config(fg='#D1D5DB')
        
        def on_tarjeta_focusout(e):
            if self.entry_tarjeta.get() == '':
                self.entry_tarjeta.insert(0, "1234 5678 9012 3456")
                self.entry_tarjeta.config(fg='#6B7280')
            self.actualizar_mensaje_version()
        
        self.entry_tarjeta.bind('<FocusIn>', on_tarjeta_click)
        self.entry_tarjeta.bind('<FocusOut>', on_tarjeta_focusout)
        self.entry_tarjeta.bind('<KeyRelease>', lambda e: self.actualizar_mensaje_version())
        
        # Mensaje premium/gratuito
        self.frame_version = tk.Frame(self.frame_paso2, bg='#3B82F6', bd=0)
        self.frame_version.pack(fill='x', padx=15, pady=15, ipady=15)
        
        self.label_version = tk.Label(
            self.frame_version,
            text="🎮 Obtendrá la versión Gratuita",
            font=('Segoe UI', 10, 'bold'),
            bg='#3B82F6',
            fg='white'
        )
        self.label_version.pack()
        
        # Botones
        frame_botones = tk.Frame(self.frame_paso2, bg='#C5C5C5')
        frame_botones.pack(fill='x', padx=15, pady=15)
        
        tk.Button(frame_botones, text="← Atrás", command=self.volver_a_paso1,
                 font=('Segoe UI', 9, 'bold'), bg='#f8f9fa', fg=self.colores['texto'],
                 relief='flat', bd=0, pady=8, cursor='hand2').pack(side='left', fill='x', expand=True, padx=(0, 4))
        
        tk.Button(frame_botones, text="Registrarse ✓", command=self.registrar_usuario,
                 font=('Segoe UI', 9, 'bold'), bg=self.colores['primario'], fg='white',
                 relief='flat', bd=0, pady=8, cursor='hand2').pack(side='left', fill='x', expand=True, padx=(4, 0))
    
    def actualizar_mensaje_version(self):
        """Actualiza el mensaje según si hay tarjeta o no"""
        tarjeta = self.var_tarjeta.get()
        if tarjeta and tarjeta != "1234 5678 9012 3456" and len(tarjeta) > 10:
            self.frame_version.config(bg='#F59E0B')
            self.label_version.config(text="👑 Obtendrá la versión Premium", bg='#F59E0B')
        else:
            self.frame_version.config(bg='#3B82F6')
            self.label_version.config(text="🎮 Obtendrá la versión Gratuita", bg='#3B82F6')
    
    def mostrar_paso(self, paso):
        if paso == 1:
            self.frame_paso1.pack(fill=tk.BOTH, expand=True)
            self.frame_paso2.pack_forget()
        else:
            self.frame_paso1.pack_forget()
            self.frame_paso2.pack(fill=tk.BOTH, expand=True)
    
    def volver_a_login(self):
        from Login import LoginApp
        ventana = tk.Tk()
        LoginApp(ventana)
        # destruir registro con un pequeño delay para dejar que se procesen 'after' pendientes
        self.root.after(50, self.root.destroy)
        ventana.mainloop()

    
    def activar_face_recognition(self):
        """Activa el reconocimiento facial"""
        username = self.var_username.get().strip()
        if not username:
            messagebox.showwarning("Username Requerido", "Por favor ingrese su nombre de usuario primero")
            self.entry_username.focus_set()
            return
        
        # Verificar que el username no exista
        try:
            usuarios = cargar_usuarios()
            if isinstance(usuarios, dict):
                if username in usuarios:
                    messagebox.showerror("Error", "Este usuario ya existe")
                    return
        except:
            pass
        
        resultado = self.register_face_direct(username)
        
        if resultado:
            self.face_id_registered = True
            self.face_id_filename = resultado  # Solo guardamos el nombre del archivo
            
                        # Recolorear el botón circular cuando Face ID está listo
            if self.face_canvas and self._face_oval and self._face_icon:
                try:
                    self.face_canvas.itemconfig(self._face_oval, outline='#10B981')
                    self.face_canvas.itemconfig(self._face_icon, fill='#10B981')
                except Exception:
                    pass
            self.label_face_status.config(text='✓ OK', fg='#10B981')
            try:
                if hasattr(self, 'btn_face_recognition') and self.btn_face_recognition:
                    self.btn_face_recognition.config(bg='#10B981', activebackground='#10B981')
            except Exception:
                pass
            
            messagebox.showinfo("Face ID", f"✓ Rostro registrado para {username}")
            return True
        else:
            self.face_id_registered = False
            self.face_id_filename = None
            return False
    
    def register_face_direct(self, username):
        """Registra el rostro y devuelve el nombre del archivo"""
        try:
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                messagebox.showerror("Error", "No se pudo acceder a la cámara")
                return None
            
            faces_captured = []
            max_faces = 30
            
            messagebox.showinfo("Face ID", f"📸 Capturando rostro para: {username}\n\nPresiona ESC para cancelar")
            
            while len(faces_captured) < max_faces:
                ret, frame = cap.read()
                if not ret:
                    break
                
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = face_cascade.detectMultiScale(gray, 1.3, 5)
                
                for (x, y, w, h) in faces:
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (138, 28, 50), 2)
                    face_roi = gray[y:y+h, x:x+w]
                    faces_captured.append(face_roi)
                
                progress = len(faces_captured)
                cv2.putText(frame, f"Capturando: {progress}/{max_faces}", (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (138, 28, 50), 2)
                
                cv2.imshow(f'Face ID - {username}', frame)
                
                if cv2.waitKey(1) & 0xFF == 27:
                    cap.release()
                    cv2.destroyAllWindows()
                    return None
            
            cap.release()
            cv2.destroyAllWindows()
            
            if len(faces_captured) < 10:
                messagebox.showerror("Error", "No se capturaron suficientes imágenes")
                return None
            
            # Crear directorio si no existe
            if not os.path.exists('face_data'):
                os.makedirs('face_data')
            
            # Guardar los datos faciales en archivo pickle
            filename = f'face_data/{username}_face.pkl'
            face_data = {
                'username': username,
                'faces': faces_captured,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            with open(filename, 'wb') as f:
                pickle.dump(face_data, f)
            
            # Retornar solo el nombre del archivo (no los datos)
            return filename
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al registrar Face ID: {str(e)}")
            return None
    
    def ir_a_ventana2(self):
        # Validaciones
        if not self.var_nombre.get().strip():
            messagebox.showerror("Error", "Ingrese su nombre")
            return
        
        if not self.var_apellido.get().strip():
            messagebox.showerror("Error", "Ingrese su apellido")
            return
        
        correo = self.var_correo.get().strip()
        if not correo:
            messagebox.showerror("Error", "Ingrese su correo")
            return
        
        patron_correo = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
        if not re.match(patron_correo, correo):
            messagebox.showerror("Error", "Correo inválido")
            return
        
        telefono = self.var_telefono.get().strip()
        if not telefono or not telefono.isdigit():
            messagebox.showerror("Error", "Teléfono inválido")
            return
        
        if not self.var_username.get().strip():
            messagebox.showerror("Error", "Ingrese un usuario")
            return
        
        password = self.var_password.get()
        if not password or len(password) < 4:
            messagebox.showerror("Error", "Contraseña debe tener al menos 4 caracteres")
            return
        
        if not all(c.isalnum() for c in password):
            messagebox.showerror("Error", "La contraseña solo debe contener letras y números")
            return
        
        if password != self.var_confirmar_password.get():
            messagebox.showerror("Error", "Las contraseñas no coinciden")
            return
        
        # Verificar usuarios existentes
        try:
            usuarios = cargar_usuarios()
            if not isinstance(usuarios, dict):
                usuarios = {}
            
            correo_nuevo = correo.lower()
            user_nuevo = self.var_username.get().strip()
            
            if user_nuevo in usuarios:
                messagebox.showerror("Error", "Este usuario ya existe")
                return
            
            for u, data in usuarios.items():
                if isinstance(data, dict) and data.get("correo", "").lower() == correo_nuevo:
                    messagebox.showerror("Error", "Este correo ya está registrado")
                    return
        except:
            pass
        
        self.mostrar_paso(2)
    
    def volver_a_paso1(self):
        self.mostrar_paso(1)
    def _circularize(self, img, size=(100, 100)):
        """Devuelve la imagen recortada en círculo con alfa."""
        img = img.convert('RGBA').resize(size, Image.LANCZOS)
        mask = Image.new('L', size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, size[0], size[1]), fill=255)
        img.putalpha(mask)
        return img

    def _pintar_avatar(self, pil_img=None):
        """Pinta el círculo y la imagen (si hay) en el canvas."""
        if not self.avatar_canvas:
            return
        self.avatar_canvas.delete('all')
        self.avatar_canvas.create_oval(5, 5, 105, 105, outline=self.colores['primario'], width=3)
        if pil_img is None:
            self.avatar_canvas.create_oval(5, 5, 105, 105, fill='#E5E7EB', outline=self.colores['primario'], width=3)
            self.avatar_canvas.create_text(55, 55, text='＋', font=('Segoe UI', 26, 'bold'))
        else:
            self._avatar_photo = ImageTk.PhotoImage(pil_img)
            self.avatar_canvas.create_image(55, 55, image=self._avatar_photo)

    def seleccionar_foto(self, event=None):
        """Abre un selector y coloca la foto circular en el avatar (y la deja en memoria para guardarla)."""
        filetypes = [
            ('Imágenes', '*.png;*.jpg;*.jpeg;*.bmp;*.webp'),
            ('Todos los archivos', '*.*')
        ]
        ruta = filedialog.askopenfilename(title='Selecciona tu foto de perfil', filetypes=filetypes)
        if not ruta:
            return
        try:
            img = Image.open(ruta)
            img_circular = self._circularize(img, size=(100, 100))
            self.imagen_perfil = img_circular  # persistimos en memoria hasta registrar_usuario
            self._pintar_avatar(pil_img=img_circular)
        except Exception as e:
            messagebox.showerror('Error', f'No se pudo cargar la imagen:\n{e}')


    
    def registrar_usuario(self):
        # Validar campos paso 2
        if not self.var_nacionalidad.get():
            messagebox.showerror("Error", "Seleccione nacionalidad")
            return
        
        if not self.var_idioma.get():
            messagebox.showerror("Error", "Seleccione idioma")
            return
        
        # Obtener fecha del calendario
        fecha_nacimiento = self.date_entry.get_date()
        fecha_str = fecha_nacimiento.strftime("%d/%m/%Y")
        
        # Verificar si es premium
        tarjeta = self.var_tarjeta.get()
        es_premium = tarjeta and tarjeta != "1234 5678 9012 3456" and len(tarjeta) > 10
        
        # Crear usuario (SIN GUARDAR DATOS NUMPY - solo referencias)
        username = self.var_username.get().strip()
                # Codificar foto de perfil en base64 (PNG con transparencia) si se seleccionó
        avatar_b64 = ''
        if self.imagen_perfil is not None:
            try:
                buffer = io.BytesIO()
                self.imagen_perfil.save(buffer, format='PNG')
                avatar_b64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            except Exception as e:
                print('No se pudo codificar la foto de perfil:', e)

        usuario = {
            'nombre': self.var_nombre.get().strip(),
            'apellido': self.var_apellido.get().strip(),
            'segundo_apellido': self.var_segundo_apellido.get().strip() if self.var_segundo_apellido.get().strip() else "",
            'telefono': self.var_telefono.get().strip(),
            'correo': self.var_correo.get().strip(),
            'contrasena': self.var_password.get(),
            'nacionalidad': self.var_nacionalidad.get().strip(),
            'fecha_nacimiento': fecha_str,
            'idioma': self.var_idioma.get().strip(),
            'es_premium': bool(es_premium),
            'tarjeta': tarjeta if es_premium else "",
            'face_id': self.face_id_registered,
            'face_id_file': self.face_id_filename if self.face_id_registered else None,  # Solo el nombre del archivo
            'foto_perfil_b64': avatar_b64,
            'fecha_registro': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Cargar usuarios existentes
        try:
            usuarios = cargar_usuarios()
            if not isinstance(usuarios, dict):
                usuarios = {}
        except:
            usuarios = {}
        
        # Agregar nuevo usuario
        usuarios[username] = usuario
        
        # Guardar
        if guardar_usuarios(usuarios):
            face_msg = "🔐 Face ID activado\n" if self.face_id_registered else ""
            version = "Premium 👑" if es_premium else "Gratuita 🎮"
            messagebox.showinfo(
                "¡Bienvenido!",
                f"✓ Cuenta creada exitosamente!\n\n"
                f"Usuario: {username}\n"
                f"Versión: {version}\n"
                f"{face_msg}"
                f"\n¡Gracias por unirte! 🎮"
            )
            
            # Cerrar registro y abrir login
            self.volver_a_login()
        else:
            messagebox.showerror("Error", "No se pudo guardar el usuario")

# FUNCIÓN PRINCIPAL
def main():
    root = tk.Tk()
    
    def abrir_login():
        """Función para abrir el Login después del registro"""
        import subprocess
        import sys
        import os
        script_dir = os.path.dirname(os.path.abspath(__file__))
        login_path = os.path.join(script_dir, 'Login.py')
        subprocess.Popen([sys.executable, login_path])
    
    app = Registro(root, callback_abrir_login=abrir_login)
    root.mainloop()


if __name__ == "__main__":
    print("=" * 50)
    print("🎮 Iniciando Sistema de Registro - Avatars VS Rooks")
    print("=" * 50)
    main()
