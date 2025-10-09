#Registro
import tkinter as tk
import re
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk, ImageDraw
from datetime import datetime
from Login import cargar_usuarios, guardar_usuarios
from OpenCV import register_face_gui

class Registro:
    def __init__(self, root):
        self.root = root
        self.root.title("MiJuego - Sistema de Registro")
        
        # Configuración de ventana
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        window_width = int(screen_width * 0.6)
        window_height = int(screen_height * 0.85)
        
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.root.configure(bg='#2D0A0A')
        self.root.resizable(False, False)
        self.root.minsize(900, 650)

        # Variables
        self.imagen_perfil = None
        self.mostrar_pass1 = False
        self.mostrar_pass2 = False
        
        # Variables paso 1
        self.var_nombre = tk.StringVar()
        self.var_apellido = tk.StringVar()
        self.var_segundo_apellido = tk.StringVar()
        self.var_correo = tk.StringVar()
        self.var_username = tk.StringVar()
        self.var_password = tk.StringVar()
        self.var_confirmar_password = tk.StringVar()
        
        # Variables paso 2
        self.var_nacionalidad = tk.StringVar()
        self.var_dia = tk.StringVar()
        self.var_mes = tk.StringVar()
        self.var_anio = tk.StringVar()
        self.var_idioma = tk.StringVar()
        self.var_tarjeta = tk.StringVar()

        self.crear_interfaz()
    
    def crear_interfaz(self):
        # Frame principal con scroll
        self.main_frame = tk.Frame(self.root, bg='#2D0A0A')
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(self.main_frame, bg='#2D0A0A', highlightthickness=0)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(self.main_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        self.content_frame = tk.Frame(self.canvas, bg='#ffffff')
        self.canvas_window = self.canvas.create_window((0, 0), window=self.content_frame, anchor='nw')
        
        self.content_frame.bind('<Configure>',lambda e: self.actualizar_scroll(   
        scrollregion=self.canvas.bbox("all")))
        self.canvas.bind('<Configure>', self.centrar_contenido)
        
        self.inner_frame = tk.Frame(self.content_frame, bg='#ffffff', padx=40, pady=30)
        self.inner_frame.pack(fill=tk.BOTH, expand=True)
        
        self.crear_paso1()
        self.crear_paso2()
        self.mostrar_paso(1)
    
    def actualizar_scroll(self, event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def centrar_contenido(self, event=None):
        canvas_width = event.width if event else self.canvas.winfo_width()
        content_width = self.content_frame.winfo_reqwidth()
        x_position = max(0, (canvas_width - content_width) // 2)
        self.canvas.coords(self.canvas_window, x_position, 0)
    
    def on_mousewheel(self, event):
        if event.num == 5 or event.delta < 0:
            self.canvas.yview_scroll(1, "units")
        elif event.num == 4 or event.delta > 0:
            self.canvas.yview_scroll(-1, "units")

    #Ventana 1

    def crear_paso1(self):
        self.frame_paso1 = tk.Frame(self.inner_frame, bg='#ffffff')
        
        # Botón reconocimiento facial
        btn_face_container = tk.Frame(self.frame_paso1, bg='#ffffff')
        btn_face_container.place(relx=1.0, x=-10, y=10, anchor='ne')
                
        # Botón Face
        tk.Button(
            btn_face_container,
            text="👤",
            font=('Arial', 26),
            bg='#B91C1C',
            fg='white',
            bd=0,
            width=5,
            height=2,
            cursor='hand2',
            command=self.activar_face_recognition
        ).pack()

        tk.Label(
            btn_face_container,
            text="Face Recognition",
            font=('Arial', 9, 'bold'),
            bg='#ffffff',
            fg='#6B7280'
        ).pack(pady=(5, 0))

        # Título
        tk.Label(
            self.frame_paso1,
            text="Crear Cuenta",
            font=('Arial', 24, 'bold'),
            bg='#ffffff',
            fg='#B91C1C'
        ).pack(pady=(0, 15))
        
        # Foto de perfil
        self.frame_foto = tk.Frame(self.frame_paso1, bg='#ffffff')
        self.frame_foto.pack(pady=15)
        
        self.canvas_foto = tk.Canvas(
            self.frame_foto,
            width=100,
            height=100,
            bg='#ffffff',
            highlightthickness=0
        )
        self.canvas_foto.pack()
        self.crear_foto_perfil_inicial()
        self.crear_boton_agregar_foto()
        
        # Campos de nombre (solo letras)
        frame_nombres = tk.Frame(self.frame_paso1, bg='#ffffff')
        frame_nombres.pack(fill=tk.X, pady=8)
        
        self.crear_entrada_letras(frame_nombres, self.var_nombre, "Nombre", 0)
        self.crear_entrada_letras(frame_nombres, self.var_apellido, "Primer Apellido", 1)
        self.crear_entrada_letras(frame_nombres, self.var_segundo_apellido, "Segundo Apellido", 2)
        
        # Correo y username
        self.crear_entrada(self.frame_paso1, self.var_correo, "Correo electrónico")
        self.crear_entrada(self.frame_paso1, self.var_username, "Nombre de usuario")
        
        # Contraseñas
        self.crear_campo_password()
        
        # Mensaje de ayuda para contraseñas - TEXTO LARGO
        tk.Label(
            self.frame_paso1,
            text="⚠️ La contraseña solo puede contener letras y números, sin caracteres especiales",
            font=('Arial', 9),
            bg='#ffffff',
            fg='#6B7280',
            wraplength=500,
            justify='center'
        ).pack(pady=(0, 10))
        
        # Botón Google
        tk.Button(
            self.frame_paso1,
            text="🔒 Continuar con Google",
            font=('Arial', 11, 'bold'),
            bg='#ffffff',
            fg='#1F2937',
            bd=2,
            relief=tk.SOLID,
            cursor='hand2',
            padx=15,
            pady=10
        ).pack(fill=tk.X, pady=8)
        
        # Botón siguiente - ESTIRADO
        tk.Button(
            self.frame_paso1,
            text="Siguiente",
            font=('Arial', 12, 'bold'),
            bg='#B91C1C',
            fg='white',
            bd=0,
            cursor='hand2',
            pady=15,
            command=self.ir_a_ventana2
        ).pack(fill=tk.X, pady=8)
    
    # PASO 2
    def crear_paso2(self):
        self.frame_paso2 = tk.Frame(self.inner_frame, bg='#ffffff')
        
        tk.Label(
            self.frame_paso2,
            text="Información Adicional",
            font=('Arial', 24, 'bold'),
            bg='#ffffff',
            fg='#B91C1C'
        ).pack(pady=(0, 20))
        
        tk.Label(
            self.frame_paso2,
            text="Completa tu perfil para continuar",
            font=('Arial', 11),
            bg='#ffffff',
            fg='#6B7280'
        ).pack(pady=(0, 25))
        
        # Nacionalidad
        self.crear_campo_con_icono(
            self.frame_paso2,
            "🌎",
            "Nacionalidad",
            self.var_nacionalidad,
            es_combobox=True,
            valores=[
                '🇨🇷 Costa Rica', '🇲🇽 México', '🇺🇸 Estados Unidos',
                '🇪🇸 España', '🇦🇷 Argentina', '🇨🇴 Colombia',
                '🇨🇱 Chile', '🇵🇪 Perú', '🇻🇪 Venezuela',
                '🇧🇷 Brasil', '🇵🇹 Portugal', '🇨🇦 Canadá'
            ]
        )
        
        # Fecha de nacimiento
        frame_fecha = tk.Frame(self.frame_paso2, bg='#ffffff')
        frame_fecha.pack(fill=tk.X, pady=15)
        
        frame_label_fecha = tk.Frame(frame_fecha, bg='#ffffff')
        frame_label_fecha.pack(anchor='w', pady=(0, 8))
        
        tk.Label(
            frame_label_fecha,
            text="📅",
            font=('Arial', 16),
            bg='#DC2626',
            fg='white',
            padx=10,
            pady=6
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Label(
            frame_label_fecha,
            text="Fecha de Nacimiento",
            font=('Arial', 11, 'bold'),
            bg='#ffffff',
            fg='#374151'
        ).pack(side=tk.LEFT)
        
        # Contenedor de fecha con etiquetas
        cont_fecha = tk.Frame(frame_fecha, bg='#ffffff')
        cont_fecha.pack(pady=8)
        
        # Día
        frame_dia = tk.Frame(cont_fecha, bg='#ffffff')
        frame_dia.grid(row=0, column=0, padx=(0, 20))
        tk.Label(frame_dia, text="Día", bg='#ffffff', fg='#6B7280', font=('Arial', 10)).pack(pady=(0, 5))
        tk.Entry(
            frame_dia,
            textvariable=self.var_dia,
            width=5,
            font=('Arial', 13),
            justify='center',
            bg='#FEE2E2',
            bd=1,
            relief=tk.SOLID
        ).pack(ipady=5)
        
        # Mes
        frame_mes = tk.Frame(cont_fecha, bg='#ffffff')
        frame_mes.grid(row=0, column=1, padx=20)
        tk.Label(frame_mes, text="Mes", bg='#ffffff', fg='#6B7280', font=('Arial', 10)).pack(pady=(0, 5))
        tk.Entry(
            frame_mes,
            textvariable=self.var_mes,
            width=5,
            font=('Arial', 13),
            justify='center',
            bg='#FEE2E2',
            bd=1,
            relief=tk.SOLID
        ).pack(ipady=5)
        
        # Año
        frame_anio = tk.Frame(cont_fecha, bg='#ffffff')
        frame_anio.grid(row=0, column=2, padx=(20, 0))
        tk.Label(frame_anio, text="Año", bg='#ffffff', fg='#6B7280', font=('Arial', 10)).pack(pady=(0, 5))
        tk.Entry(
            frame_anio,
            textvariable=self.var_anio,
            width=7,
            font=('Arial', 13),
            justify='center',
            bg='#FEE2E2',
            bd=1,
            relief=tk.SOLID
        ).pack(ipady=5)
        
        # Idioma
        self.crear_campo_con_icono(
            self.frame_paso2,
            "🌐",
            "Idioma Preferido",
            self.var_idioma,
            es_combobox=True,
            valores=['🇪🇸 Español', '🇺🇸 Inglés', '🇧🇷 Portugués', '🇫🇷 Francés']
        )

        #Tarjeta de crédito
        tk.Label(
            self.frame_paso2,
            text="Si desea la versión Premium, puede resgstrarse ingresando su tarjeta de crédito (Opcional)",
            font=('Arial', 11, 'bold'),
            bg='#ffffff',
            fg='#374151'
        ).pack(anchor='w', pady=(25, 8))

        frame_tarjeta = tk.Frame(self.frame_paso2, bg='#1F2937', bd=0)
        frame_tarjeta.pack(fill=tk.X, pady=15, ipady=25, ipadx=25)

        tk.Label(
            frame_tarjeta,
            text="◼️",
            font=('Arial', 22),
            bg='#FBBF24',
            fg='#FBBF24',
            padx=18,
            pady=12
        ).pack(anchor='w', pady=(0, 12))

        self.entry_tarjeta = tk.Entry(
            frame_tarjeta,
            textvariable=self.var_tarjeta,
            font=('Arial', 17, 'bold'),
            bg='#1F2937',
            fg='#D1D5DB',
            bd=0,
            insertbackground='white'
        )
        self.entry_tarjeta.pack(fill=tk.X, pady=12, padx=10)
        self.entry_tarjeta.insert(0, "1234 5678 9012 3456")
        self.entry_tarjeta.config(fg='#6B7280')
        self.entry_tarjeta.bind('<FocusIn>',  lambda e: self.on_entry_click_tarjeta())
        self.entry_tarjeta.bind('<FocusOut>', lambda e: self.on_focusout_tarjeta())

        # Validación y autoformato
        vc = (self.root.register(lambda s: all(c.isdigit() or c == " " for c in s) or s == ""), "%P")
        self.entry_tarjeta.config(validate="key", validatecommand=vc)

        def _tarjeta_autofmt(*_):
            raw = "".join(c for c in self.var_tarjeta.get() if c.isdigit())
            g = " ".join(raw[i:i+4] for i in range(0, len(raw), 4))
            if g != self.var_tarjeta.get():
                self.var_tarjeta.set(g)
        self.var_tarjeta.trace_add("write", _tarjeta_autofmt)

        # Banner
        self.frame_version = tk.Frame(self.frame_paso2, bg='#3B82F6')
        self.frame_version.pack(fill=tk.X, pady=(10, 0), ipady=10)

        self.label_version = tk.Label(
            self.frame_version,
            text="🎮 Obtendrá la versión Gratuita de MiJuego",
            font=('Arial', 13, 'bold'),
            bg='#3B82F6',
            fg='white'
        )
        self.label_version.pack()

        #Luego define la función y conecta el trace (ahora sí existe label)
        def _update_version_banner(*_):
            raw = "".join(c for c in self.var_tarjeta.get() if c.isdigit())
            es_premium = 13 <= len(raw) <= 19
            color = '#F59E0B' if es_premium else '#3B82F6'
            texto = "👑 Obtendrá la versión Premium de MiJuego" if es_premium else "🎮 Obtendrá la versión Gratuita de MiJuego"
            self.frame_version.config(bg=color)
            self.label_version.config(text=texto, bg=color)

        self.var_tarjeta.trace_add("write", _update_version_banner)
        _update_version_banner()  # estado inicial


        # Botones
        frame_botones = tk.Frame(self.frame_paso2, bg='#ffffff')
        frame_botones.pack(fill=tk.X, pady=25)
        
        tk.Button(
            frame_botones,
            text="Atrás",
            font=('Arial', 12, 'bold'),
            bg='#E5E7EB',
            fg='#374151',
            bd=0,
            cursor='hand2',
            padx=20,
            pady=15,
            command=self.volver_a_paso1
        ).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        tk.Button(
            frame_botones,
            text="Registrarse",
            font=('Arial', 12, 'bold'),
            bg='#B91C1C',
            fg='white',
            bd=0,
            cursor='hand2',
            padx=20,
            pady=15,
            command=self.registrar_usuario
        ).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
    
    # FUNCIONES AUXILIARES
    def _tarjeta_only_digits(self, s):
        return all(c.isdigit() or c == " " for c in s) or s == ""

    def _tarjeta_autofmt(self, *_):
        raw = "".join(c for c in self.var_tarjeta.get() if c.isdigit())
        g = " ".join(raw[i:i+4] for i in range(0, len(raw), 4))
        if g != self.var_tarjeta.get():
            self.var_tarjeta.set(g)

    def validar_solo_letras(self, texto):
        return texto.isalpha() or texto.replace(" ", "").isalpha() or texto == ""
    
    def crear_entrada_letras(self, parent, variable, placeholder, columna):
        vcmd = (self.root.register(self.validar_solo_letras), '%P')
        entry = tk.Entry(
            parent,
            textvariable=variable,
            font=('Arial', 12),
            bg='#FEE2E2',
            fg='#1F2937',
            bd=1,
            relief=tk.SOLID,
            validate='key',
            validatecommand=vcmd
        )
        entry.grid(row=0, column=columna, padx=5, ipady=10, ipadx=10, sticky='ew')
        parent.columnconfigure(columna, weight=1)
        
        entry.insert(0, placeholder)
        entry.config(fg='#9CA3AF')
        entry.bind('<FocusIn>', lambda e: self.on_entry_click(entry, placeholder))
        entry.bind('<FocusOut>', lambda e: self.on_focusout(entry, placeholder))
        return entry
    
    def crear_entrada(self, parent, variable, placeholder):
        entry = tk.Entry(
            parent,
            textvariable=variable,
            font=('Arial', 12),
            bg='#FEE2E2',
            fg='#1F2937',
            bd=1,
            relief=tk.SOLID
        )
        entry.pack(fill=tk.X, pady=10, ipady=10, ipadx=10)
        entry.insert(0, placeholder)
        entry.config(fg='#9CA3AF')
        entry.bind('<FocusIn>', lambda e: self.on_entry_click(entry, placeholder))
        entry.bind('<FocusOut>', lambda e: self.on_focusout(entry, placeholder))
        return entry
    
    def crear_campo_con_icono(self, parent, icono, texto, variable, es_combobox=False, valores=None):
        frame = tk.Frame(parent, bg='#ffffff')
        frame.pack(fill=tk.X, pady=15)
        
        frame_label = tk.Frame(frame, bg='#ffffff')
        frame_label.pack(anchor='w', pady=(0, 8))
        
        tk.Label(
            frame_label,
            text=icono,
            font=('Arial', 16),
            bg='#B91C1C',
            fg='white',
            padx=10,
            pady=6
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Label(
            frame_label,
            text=texto,
            font=('Arial', 11, 'bold'),
            bg='#ffffff',
            fg='#374151'
        ).pack(side=tk.LEFT)
        
        if es_combobox:
            combo = ttk.Combobox(
                frame,
                textvariable=variable,
                font=('Arial', 12),
                state='readonly',
                values=valores
            )
            combo.pack(fill=tk.X, ipady=12)
            return combo
    
    def crear_campo_password(self):
        # Contraseña 1
        frame_pass1 = tk.Frame(self.frame_paso1, bg='#ffffff')
        frame_pass1.pack(fill=tk.X, pady=8)
        
        self.entry_pass1 = tk.Entry(
            frame_pass1,
            textvariable=self.var_password,
            font=('Arial', 11),
            bg='#FEE2E2',
            fg='#1F2937',
            bd=1,
            relief=tk.SOLID
        )
        self.entry_pass1.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=8, ipadx=8)
        
        # Crear imagen del ojo ABIERTO
        img_abierto = Image.new('RGBA', (24, 24), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img_abierto)
        draw.ellipse([2, 8, 22, 16], fill='#374151')
        draw.ellipse([8, 6, 16, 18], outline='#374151', width=2)
        draw.ellipse([10, 9, 14, 15], fill='#374151')
        
        self.img_ojo_abierto = ImageTk.PhotoImage(img_abierto)
        
        # Imagen ojo CERRADO
        img_cerrado = Image.new('RGBA', (24, 24), (0, 0, 0, 0))
        draw2 = ImageDraw.Draw(img_cerrado)
        draw2.ellipse([2, 8, 22, 16], fill='#374151')
        draw2.ellipse([8, 6, 16, 18], outline='#374151', width=2)
        draw2.ellipse([10, 9, 14, 15], fill='#374151')
        draw2.line([2, 22, 22, 2], fill='#B91C1C', width=3)
        
        self.img_ojo_cerrado = ImageTk.PhotoImage(img_cerrado)
        
        self.btn_ojo1 = tk.Button(
            frame_pass1,
            image=self.img_ojo_cerrado,
            bg='#FEE2E2',
            bd=0,
            cursor='hand2',
            width=40,
            height=32,
            relief=tk.FLAT,
            command=lambda: self.toggle_password(1)
        )
        self.btn_ojo1.pack(side=tk.LEFT, padx=(8, 8))
        
        self.entry_pass1.insert(0, "Contraseña")
        self.entry_pass1.config(fg='#9CA3AF')
        self.entry_pass1.bind('<FocusIn>', lambda e: self.on_entry_click(self.entry_pass1, "Contraseña"))
        self.entry_pass1.bind('<FocusOut>', lambda e: self.on_focusout(self.entry_pass1, "Contraseña"))
        
        # Contraseña 2
        frame_pass2 = tk.Frame(self.frame_paso1, bg='#ffffff')
        frame_pass2.pack(fill=tk.X, pady=8)
        
        self.entry_pass2 = tk.Entry(
            frame_pass2,
            textvariable=self.var_confirmar_password,
            font=('Arial', 11),
            bg='#FEE2E2',
            fg='#1F2937',
            bd=1,
            relief=tk.SOLID
        )
        self.entry_pass2.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=8, ipadx=8)
        
        self.btn_ojo2 = tk.Button(
            frame_pass2,
            image=self.img_ojo_cerrado,
            bg='#FEE2E2',
            bd=0,
            cursor='hand2',
            width=40,
            height=32,
            relief=tk.FLAT,
            command=lambda: self.toggle_password(2)
        )
        self.btn_ojo2.pack(side=tk.LEFT, padx=(8, 8))
        
        self.entry_pass2.insert(0, "Confirmar contraseña")
        self.entry_pass2.config(fg='#9CA3AF')
        self.entry_pass2.bind('<FocusIn>', lambda e: self.on_entry_click(self.entry_pass2, "Confirmar contraseña"))
        self.entry_pass2.bind('<FocusOut>', lambda e: self.on_focusout(self.entry_pass2, "Confirmar contraseña"))
    
    def on_entry_click(self, entry, placeholder):
        if entry.get() == placeholder:
            entry.delete(0, tk.END)
            entry.config(fg='#1F2937')
            if entry in [self.entry_pass1, self.entry_pass2]:
                if not self.mostrar_pass1 and entry == self.entry_pass1:
                    entry.config(show='●')
                if not self.mostrar_pass2 and entry == self.entry_pass2:
                    entry.config(show='●')
    
    def on_entry_click_tarjeta(self):
        if self.entry_tarjeta.get() == "1234 5678 9012 3456":
            self.entry_tarjeta.delete(0, tk.END)
            self.entry_tarjeta.config(fg='#D1D5DB')
    
    def on_focusout_tarjeta(self):
        if self.entry_tarjeta.get() == '':
            self.entry_tarjeta.insert(0, "1234 5678 9012 3456")
            self.entry_tarjeta.config(fg='#6B7280')
    
    def on_focusout(self, entry, placeholder):
        if entry.get() == '':
            entry.insert(0, placeholder)
            entry.config(fg='#9CA3AF')
            if entry in [self.entry_pass1, self.entry_pass2]:
                entry.config(show='')
    
    def crear_foto_perfil_inicial(self):
        img = Image.new('RGBA', (100, 100), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        draw.ellipse([0, 0, 100, 100], fill='#B91C1C')
        
        self.photo_perfil = ImageTk.PhotoImage(img)
        self.canvas_foto.create_image(50, 50, image=self.photo_perfil)
        self.canvas_foto.create_text(50, 50, text="📷", font=('Arial', 40), fill='white')
    
    def crear_boton_agregar_foto(self):
        size = 40
        img_btn = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img_btn)
        draw.ellipse([0, 0, size-1, size-1], fill='#B91C1C')
        line_width = 4
        center = size // 2
        line_length = 14
        draw.line([center, center - line_length//2, center, center + line_length//2], 
                  fill='white', width=line_width)
        draw.line([center - line_length//2, center, center + line_length//2, center], 
                  fill='white', width=line_width)
        
        self.img_agregar = ImageTk.PhotoImage(img_btn)
        
        # Boton canvas
        canvas_btn = tk.Canvas(
            self.frame_foto,
            width=size,
            height=size,
            bg='#ffffff',
            highlightthickness=0,
            cursor='hand2'
        )
        canvas_btn.place(x=65, y=65)
        canvas_btn.create_image(size//2, size//2, image=self.img_agregar)
        canvas_btn.bind('<Button-1>', lambda e: self.seleccionar_imagen())
        
        # Guardar referencia
        self.btn_camara = canvas_btn
    
    def seleccionar_imagen(self):
        archivo = filedialog.askopenfilename(
            title="Seleccionar imagen de perfil",
            filetypes=[("Imágenes", "*.png *.jpg *.jpeg *.gif *.bmp")]
        )
        
        if archivo:
            img = Image.open(archivo).resize((100, 100), Image.Resampling.LANCZOS)
            mask = Image.new('L', (100, 100), 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse([0, 0, 100, 100], fill=255)
            
            output = Image.new('RGB', (100, 100), (255, 255, 255))
            output.paste(img, (0, 0))
            output.putalpha(mask)
            
            self.photo_perfil = ImageTk.PhotoImage(output)
            self.canvas_foto.delete("all")
            self.canvas_foto.create_image(50, 50, image=self.photo_perfil)
            self.imagen_perfil = archivo

    def toggle_password(self, campo):
        if campo == 1:
            self.mostrar_pass1 = not self.mostrar_pass1
            if self.mostrar_pass1:
                self.entry_pass1.config(show='')
                self.btn_ojo1.config(image=self.img_ojo_abierto)
            else:
                self.entry_pass1.config(show='●')
                self.btn_ojo1.config(image=self.img_ojo_cerrado)
        else:
            self.mostrar_pass2 = not self.mostrar_pass2
            if self.mostrar_pass2:
                self.entry_pass2.config(show='')
                self.btn_ojo2.config(image=self.img_ojo_abierto)
            else:
                self.entry_pass2.config(show='●')
                self.btn_ojo2.config(image=self.img_ojo_cerrado)
    
    def mostrar_paso(self, paso):
        if paso == 1:
            self.frame_paso1.pack(fill=tk.BOTH, expand=True)
            self.frame_paso2.pack_forget()
        else:
            self.frame_paso1.pack_forget()
            self.frame_paso2.pack(fill=tk.BOTH, expand=True)
            
        self.content_frame.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self.canvas.yview_moveto(0.0)
        try:
            self._centrar_contenido_estable()
        except Exception:
            try:
                self.centrar_contenido()
            except Exception:
                pass

        
    def ir_a_ventana2(self):
        #validaciones
        if not self.var_nombre.get() or self.var_nombre.get() == "Nombre":
            messagebox.showerror("Error", "Por favor ingrese su nombre")
            return
        
        if not self.var_apellido.get() or self.var_apellido.get() == "Primer Apellido":
            messagebox.showerror("Error", "Por favor ingrese su apellido")
            return
        
        correo = self.var_correo.get().strip()
        if not correo or correo == "Correo electrónico":
            messagebox.showerror("Error", "Por favor ingrese su correo")
            return
        
        patron_correo = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
        if not re.match(patron_correo, correo):
            messagebox.showerror("Error", "Por favor ingrese un correo válido")
            return
        
        if not self.var_username.get() or self.var_username.get() == "Nombre de usuario":
            messagebox.showerror("Error", "Por favor ingrese su nombre de usuario")
            return
        
        password = self.var_password.get()
        if not password or password == "Contraseña":
            messagebox.showerror("Error", "Por favor ingrese una contraseña")
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
            if not isinstance(usuarios, list):
                usuarios = [usuarios] if isinstance(usuarios, dict) else []
            
            correo_nuevo = correo.lower()
            user_nuevo = self.var_username.get().strip().lower()
            
            for u in usuarios:
                if isinstance(u, dict):
                    correo_guardado = (u.get("correo", "") or u.get("email", "")).strip().lower()
                    user_guardado = (u.get("username", "") or u.get("user", "")).strip().lower()
                    
                    if correo_guardado == correo_nuevo:
                        messagebox.showerror("Error", "Este correo ya está registrado")
                        return
                    
                    if user_guardado == user_nuevo:
                        messagebox.showerror("Error", "Este nombre de usuario ya existe")
                        return
        except:
            pass
        
        self.mostrar_paso(2)
        self.actualizar_mensaje_version()
    
    def volver_a_paso1(self):
        self.mostrar_paso(1)
    
    def actualizar_mensaje_version(self):
        tarjeta = self.var_tarjeta.get()
        if tarjeta and tarjeta != "1234 5678 9012 3456" and len(tarjeta) > 10:
            self.frame_version.config(bg='#F59E0B')
            self.label_version.config(text="👑 Obtendrá la versión Premium de MiJuego", bg='#F59E0B')
        else:
            self.frame_version.config(bg='#3B82F6')
            self.label_version.config(text="🎮 Obtendrá la versión Gratuita de MiJuego", bg='#3B82F6')
    
    def registrar_usuario(self):
        # Validar campos
        if not self.var_nacionalidad.get():
            messagebox.showerror("Error", "Por favor seleccione su nacionalidad")
            return
        
        if not self.var_idioma.get():
            messagebox.showerror("Error", "Por favor seleccione un idioma")
            return
        
        # Validar fecha
        dia = self.var_dia.get().strip().zfill(2)
        mes = self.var_mes.get().strip().zfill(2)
        anio = self.var_anio.get().strip()
        
        if not dia or not mes or not anio:
            messagebox.showerror("Error", "Por favor ingrese su fecha de nacimiento completa")
            return
        
        fecha_str = f"{dia}/{mes}/{anio}"
        try:
            datetime.strptime(fecha_str, "%d/%m/%Y")
        except ValueError:
            messagebox.showerror("Error", "La fecha de nacimiento no es válida")
            return
        
        # Verificar si es premium
        raw_tarjeta = "".join(c for c in self.var_tarjeta.get() if c.isdigit())
        es_premium = 13 <= len(raw_tarjeta) <= 19
        if raw_tarjeta:
            masked = ("•" * max(0, len(raw_tarjeta) - 4)) + raw_tarjeta[-4:]
            masked_grouped = " ".join(masked[i:i+4] for i in range(0, len(masked), 4))
        else:
            masked_grouped = ""

        #Crear usuario
        usuario = {
            "nombre": self.var_nombre.get(),
            'apellido': self.var_apellido.get().strip(),
            'segundo_apellido': self.var_segundo_apellido.get().strip(),
            'correo': self.var_correo.get().strip(),
            'username': self.var_username.get().strip(),
            'password': self.var_password.get(),
            'nacionalidad': self.var_nacionalidad.get().strip(),
            'fecha_nacimiento': fecha_str,
            'idioma': self.var_idioma.get().strip(),
            "tarjeta": masked_grouped,
            'es_premium': es_premium,
            'tarjeta': masked_grouped if es_premium else "",
            'fecha_registro': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Guardar
        guardar_usuarios(usuario)
        
        # Mensaje de éxito
        version = "Premium 👑" if es_premium else "Gratuita 🎮"
        messagebox.showinfo(
            "¡Bienvenido a Avatars vs Rooks!",
            f"¡Tu cuenta ha sido creada exitosamente!\n\n"
            f"Usuario: {usuario['username']}\n"
            f"Versión: {version}\n\n"
        )
        
        self.limpiar_formulario()
        self.mostrar_paso(1)
    
    def limpiar_formulario(self):
        for var in [self.var_nombre, self.var_apellido, self.var_segundo_apellido,
                    self.var_correo, self.var_username, self.var_password,
                    self.var_confirmar_password, self.var_nacionalidad,
                    self.var_dia, self.var_mes, self.var_anio,
                    self.var_idioma, self.var_tarjeta]:
            var.set("")
        
        self.canvas_foto.delete("all")
        self.crear_foto_perfil_inicial()
        
        if hasattr(self, 'btn_camara'):
            self.btn_camara.destroy()
        self.crear_boton_agregar_foto()
    
    def activar_face_recognition(self):
        return register_face_gui()
    
# FUNCIÓN PRINCIPAL
def main():
    root = tk.Tk()
    app = Registro(root)
    root.mainloop()

if __name__ == "__main__":
    print("=" * 50)
    print("🎮 Iniciando Sistema de Registro - MiJuego")
    print("=" * 50)
    main()

