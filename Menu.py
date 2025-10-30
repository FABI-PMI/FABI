import tkinter as tk
from tkinter import messagebox
import json
from cryptography.fernet import Fernet
import os

class Menu:
    def __init__(self, root, username=None):  
        self.root = root  
        self.root.title("Avatars VS Rooks - Menú") 
        self.root.configure(bg="#8A1C32") 
        self.root.geometry("1100x650")        
        self.root.resizable(False, False)
        
        # Centrar ventana
        self.centrar_ventana()
        
        main_container = tk.Frame(root, bg="#8A1C32")  
        main_container.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)
        
        self.DescripcionMenu(main_container)
        self.BotonesNivel(main_container)
        self.BarrasFrecuencia(main_container)
        
        # Variables para almacenar nivel y username
        self.username = username
        self.nivel_seleccionado = None
        
        # Si ya tenemos username, mostrar mensaje de bienvenida
        if self.username:
            print(f"👤 Usuario cargado: {self.username}")
    
    def centrar_ventana(self):
        """Centra la ventana en la pantalla"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def DescripcionMenu(self, parent):
        desc_frame = tk.Frame(parent, bg="#C9C9C9", relief=tk.RAISED, borderwidth=4, width=300)
        desc_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10)
        desc_frame.pack_propagate(False)
        
        title_label = tk.Label(  
            desc_frame,
            text="📜 Instrucciones",
            font=('Georgia', 18, 'bold'),
            bg="#C9C9C9",
            fg="#2C3E50"
        )
        title_label.pack(pady=20)
        
        # Frame para el texto con scrollbar
        text_container = tk.Frame(desc_frame, bg="#C9C9C9")
        text_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
        
        # Scrollbar
        scrollbar = tk.Scrollbar(text_container, bg="#7A7A7A", troughcolor="#C9C9C9")
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.text_area = tk.Text(
            text_container,  
            wrap=tk.WORD,  
            font=('Georgia', 12),  
            bg="#FFFFFF",  
            fg="#333333",  
            relief=tk.FLAT, 
            borderwidth=0,  
            padx=15,  
            pady=15,
            yscrollcommand=scrollbar.set
        )
        self.text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.text_area.yview)
        
        self.text_area.tag_configure("center", justify='center')
        
        mensaje = """
        
BIENVENIDO 
A 
AVATARS VS ROOKS

══════════════════════

En esta parte podrás encontrar la herramientas necesarias para defendete de LOS AVATARS,
las TORRES ELEMENTALES:

⛰️ Arena
🪨 Roca 
💧 Agua 
🔥 Fuego 

Ajusta sus frecuencias de disparo 
según tu estrategia. Cada decisión 
puede marcar la diferencia.

Elige la dificultad y demuestra 
tu habilidad en el campo de batalla,
al selecionarla el juego iniciara inmediatamente.

El destino de nuestra aldea 
está en tus manos.

¡MUCHOS EXITOS EN EL COMBATE! """

        self.text_area.insert('1.0', mensaje) 
        self.text_area.tag_add("center", "1.0", "end")
        self.text_area.config(state=tk.DISABLED)

    
    def BotonesNivel(self, parent): 
        buttons_frame = tk.Frame(parent, bg="#C9C9C9", relief=tk.RAISED, borderwidth=4, width=300)  
        buttons_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10)  
        buttons_frame.pack_propagate(False)
        
        title = tk.Label(  
            buttons_frame, 
            text="⚔️ DIFICULTAD",
            font=('Georgia', 18, 'bold'),  
            bg="#C9C9C9", 
            fg="#2C3E50"
        )
        title.pack(pady=20)
        
        tk.Frame(buttons_frame, bg="#C9C9C9", height=50).pack() 
        
        buttons_config = [ 
            ("DIFÍCIL", self.NivelDificil, "#8B3A3A"),  
            ("MEDIO", self.NivelMedio, "#8B6F47"), 
            ("FÁCIL", self.NivelFacil, "#6B8B3D")  
        ]
        
        for text, command, color in buttons_config:
            btn = tk.Button(
                buttons_frame,
                text=text,
                command=command,
                font=('Georgia', 15, 'bold'), 
                bg=color,  
                fg="white",  
                activebackground=self.darken_color(color), 
                activeforeground="white",  
                relief=tk.RAISED, 
                borderwidth=3,
                padx=20,  
                pady=20,  
                cursor='hand2',  
                width=14
            )
            btn.pack(pady=20) 
            
            btn.bind('<Enter>', lambda e, b=btn, c=color: b.config(bg=self.darken_color(c))) 
            btn.bind('<Leave>', lambda e, b=btn, c=color: b.config(bg=c)) 
    

    def BarrasFrecuencia(self, parent):
        sliders_frame = tk.Frame(parent, bg="#C9C9C9", relief=tk.RAISED, borderwidth=4, width=400)  
        sliders_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10)
        sliders_frame.pack_propagate(False)
        
        title = tk.Label(  
            sliders_frame, 
            text="⚡ FRECUENCIA DISPARO ⚡",
            font=('Georgia', 18, 'bold'),  
            bg="#C9C9C9", 
            fg="#2C3E50"
        )
        title.pack(pady=15) 
        
        sliders_config = [ 
            ("⛰️  TORRE DE ARENA", "#C4A35A", "#A68A4D"), 
            ("🪨  TORRE DE ROCA", "#7A6F5D", "#5C5347"),  
            ("💧 TORRE DE AGUA", "#5B7C8D", "#4A6576"),  
            ("🔥 TORRE DE FUEGO", "#B85450", "#9A4541")
        ]
        
        self.Frecuencias = {} 
        
        for name, color, trough_color in sliders_config:
            self.create_slider(sliders_frame, name, color, trough_color)  
    
    def create_slider(self, parent, name, color, trough_color): 
        container = tk.Frame(parent, bg="#C9C9C9") 
        container.pack(fill=tk.X, padx=20, pady=6)
        
        label = tk.Label(  
            container,  
            text=name,  
            font=('Georgia', 12, 'bold'),  
            bg="#C9C9C9",  
            fg="#2C3E50"
        )
        label.pack(pady=(0, 5))
        
        slider_frame = tk.Frame(container, bg="#7A7A7A", relief=tk.SOLID, borderwidth=2)
        slider_frame.pack(fill=tk.X)
        
        inner_frame = tk.Frame(slider_frame, bg="#FFFFFF")
        inner_frame.pack(fill=tk.X, padx=12, pady=10)
        
        slider = tk.Scale(
            inner_frame,
            from_=0,
            to=10,
            orient=tk.HORIZONTAL,
            showvalue=1,
            bg=color,
            fg="white",
            troughcolor=trough_color,
            highlightthickness=0,
            borderwidth=1,
            relief=tk.RAISED,
            length=280,
            width=22,
            sliderlength=32,
            font=('Georgia', 10, 'bold')
        )
        slider.set(5)
        slider.pack(fill=tk.X)
        
        self.Frecuencias[name] = slider

    # Funciones Aux de las barras de frecuencia 
    def get_frecuencia(self, nombre):
        return self.Frecuencias[nombre].get()

    def get_all_frequencies(self):
        return {nombre: slider.get() for nombre, slider in self.Frecuencias.items()}
    
    def mostrar_frecuencias(self):
        frecuencias = self.get_all_frequencies()
        print("\n" + "="*40)
        print(" FRECUENCIAS DE DISPARO:")
        print("="*40)
        for nombre, valor in frecuencias.items():
            print(f"{nombre}: {valor}")
        print("="*40 + "\n")
    
    # Cambiar el boton de color cuando se va a seleccionar
    def darken_color(self, hex_color):
        hex_color = hex_color.lstrip('#')
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        darkened = tuple(max(0, int(c * 0.75)) for c in rgb)
        return f'#{darkened[0]:02x}{darkened[1]:02x}{darkened[2]:02x}'
    
    # ==================== MÉTODOS PARA PEDIR USERNAME ====================
    
    def _pedir_username(self):
        """Pide el username al usuario para cargar su configuración"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Identificación de Jugador")
        dialog.geometry("450x220")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.configure(bg='#8A1C32')
        
        # Centrar el diálogo
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (450 // 2)
        y = (dialog.winfo_screenheight() // 2) - (220 // 2)
        dialog.geometry(f"+{x}+{y}")
        
        resultado = {'username': None}
        
        # Contenedor principal
        main_frame = tk.Frame(dialog, bg='#C9C9C9', relief=tk.RAISED, bd=4)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Contenido del diálogo
        tk.Label(
            main_frame,
            text="⚔️ IDENTIFICACIÓN ⚔️",
            font=("Georgia", 16, "bold"),
            bg='#C9C9C9',
            fg='#2C3E50'
        ).pack(pady=(15, 5))
        
        tk.Label(
            main_frame,
            text="Ingresa tu nombre de usuario\npara cargar tu configuración:",
            font=("Georgia", 11),
            bg='#C9C9C9',
            fg='#2C3E50'
        ).pack(pady=(5, 15))
        
        username_var = tk.StringVar()
        
        entry_frame = tk.Frame(main_frame, bg='#FFFFFF', relief=tk.SOLID, bd=2)
        entry_frame.pack(pady=10, padx=30, fill=tk.X)
        
        entry = tk.Entry(
            entry_frame,
            textvariable=username_var,
            font=("Georgia", 12),
            bg='#FFFFFF',
            fg='#2C3E50',
            relief=tk.FLAT,
            insertbackground='#8A1C32'
        )
        entry.pack(pady=8, padx=10, fill=tk.X)
        entry.focus()
        
        def aceptar():
            username = username_var.get().strip()
            if not username:
                messagebox.showwarning("Advertencia", "Por favor ingresa tu username", parent=dialog)
                return
            
            # Verificar que el usuario existe
            if not self._verificar_usuario_existe(username):
                messagebox.showerror(
                    "Error", 
                    f"El usuario '{username}' no existe en el sistema.\n\nPor favor verifica el nombre.",
                    parent=dialog
                )
                return
            
            resultado['username'] = username
            dialog.destroy()
        
        def cancelar():
            dialog.destroy()
        
        # Botones
        btn_frame = tk.Frame(main_frame, bg='#C9C9C9')
        btn_frame.pack(pady=(10, 15))
        
        tk.Button(
            btn_frame,
            text="Aceptar",
            command=aceptar,
            bg='#6B8B3D',
            fg='white',
            font=("Georgia", 11, "bold"),
            padx=25,
            pady=8,
            cursor="hand2",
            relief=tk.RAISED,
            bd=3
        ).pack(side='left', padx=10)
        
        tk.Button(
            btn_frame,
            text="Cancelar",
            command=cancelar,
            bg='#8B3A3A',
            fg='white',
            font=("Georgia", 11, "bold"),
            padx=25,
            pady=8,
            cursor="hand2",
            relief=tk.RAISED,
            bd=3
        ).pack(side='left', padx=10)
        
        # Enter para aceptar
        entry.bind('<Return>', lambda e: aceptar())
        
        dialog.wait_window()
        return resultado['username']
    
    def _verificar_usuario_existe(self, username):
        """Verifica si el usuario existe en el archivo encriptado"""
        archivo_encriptado = 'usuarios.json.enc'
        archivo_clave = 'clave.key'
        
        try:
            if not os.path.exists(archivo_clave):
                print("❌ No se encontró el archivo clave.key")
                return False
            
            if not os.path.exists(archivo_encriptado):
                print("❌ No se encontró el archivo usuarios.json.enc")
                return False
            
            # Cargar clave
            with open(archivo_clave, 'rb') as f:
                clave = f.read()
            
            fernet = Fernet(clave)
            
            # Desencriptar archivo de usuarios
            with open(archivo_encriptado, 'rb') as f:
                datos_encriptados = f.read()
            
            datos_desencriptados = fernet.decrypt(datos_encriptados)
            usuarios = json.loads(datos_desencriptados.decode('utf-8'))
            
            # Verificar si el usuario existe
            existe = username in usuarios
            
            if existe:
                print(f"✅ Usuario '{username}' encontrado")
            else:
                print(f"❌ Usuario '{username}' NO encontrado")
            
            return existe
            
        except Exception as e:
            print(f"❌ Error al verificar usuario: {e}")
            return False
    
    def _cargar_datos_usuario(self, username):
        """Carga los datos del usuario desde el archivo encriptado"""
        archivo_encriptado = 'usuarios.json.enc'
        archivo_clave = 'clave.key'
        
        try:
            # Cargar clave
            with open(archivo_clave, 'rb') as f:
                clave = f.read()
            
            fernet = Fernet(clave)
            
            # Desencriptar archivo de usuarios
            with open(archivo_encriptado, 'rb') as f:
                datos_encriptados = f.read()
            
            datos_desencriptados = fernet.decrypt(datos_encriptados)
            usuarios = json.loads(datos_desencriptados.decode('utf-8'))
            
            if username in usuarios:
                print(f"✅ Datos de '{username}' cargados correctamente")
                return usuarios[username]
            else:
                print(f"❌ No se encontraron datos para '{username}'")
                return None
            
        except Exception as e:
            print(f"❌ Error al cargar datos: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _guardar_configuracion_menu(self, username):
        """Guarda las frecuencias del menú en el perfil del usuario"""
        archivo_encriptado = 'usuarios.json.enc'
        archivo_clave = 'clave.key'
        
        try:
            # Cargar clave
            with open(archivo_clave, 'rb') as f:
                clave = f.read()
            
            fernet = Fernet(clave)
            
            # Desencriptar archivo de usuarios
            with open(archivo_encriptado, 'rb') as f:
                datos_encriptados = f.read()
            
            datos_desencriptados = fernet.decrypt(datos_encriptados)
            usuarios = json.loads(datos_desencriptados.decode('utf-8'))
            
            if username not in usuarios:
                print(f"❌ Usuario '{username}' no encontrado")
                return False
            
            # Guardar configuración del menú
            usuarios[username]['menu_config'] = {
                'nivel': self.nivel_seleccionado,
                'frecuencias': self.get_all_frequencies()
            }
            
            # Encriptar y guardar
            datos_json = json.dumps(usuarios, indent=4, ensure_ascii=False)
            datos_encriptados = fernet.encrypt(datos_json.encode('utf-8'))
            
            with open(archivo_encriptado, 'wb') as f:
                f.write(datos_encriptados)
            
            print(f"✅ Configuración guardada para '{username}'")
            print(f"   Nivel: {self.nivel_seleccionado}")
            print(f"   Frecuencias: {self.get_all_frequencies()}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error al guardar configuración: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    # ==================== ELECCIÓN DE NIVEL ====================
    
    def NivelDificil(self): 
        self.nivel_seleccionado = "DIFICIL"
        print(f"🎮 Dificultad {self.nivel_seleccionado} activada")
        self.mostrar_frecuencias()
        
        # Si no hay username, pedirlo
        if not self.username:
            self.username = self._pedir_username()
            if not self.username:
                print("❌ No se ingresó username, cancelando...")
                return
        
        # Guardar configuración
        self._guardar_configuracion_menu(self.username)
        
        # Abrir juego
        self.abrir_principal()

    def NivelMedio(self): 
        self.nivel_seleccionado = "MEDIO"
        print(f"🎮 Dificultad {self.nivel_seleccionado} activada")
        self.mostrar_frecuencias()
        
        # Si no hay username, pedirlo
        if not self.username:
            self.username = self._pedir_username()
            if not self.username:
                print("❌ No se ingresó username, cancelando...")
                return
        
        # Guardar configuración
        self._guardar_configuracion_menu(self.username)
        
        # Abrir juego
        self.abrir_principal()

    def NivelFacil(self):
        self.nivel_seleccionado = "FACIL"
        print(f"🎮 Dificultad {self.nivel_seleccionado} activada")
        self.mostrar_frecuencias()
        
        # Si no hay username, pedirlo
        if not self.username:
            self.username = self._pedir_username()
            if not self.username:
                print("❌ No se ingresó username, cancelando...")
                return
        
        # Guardar configuración
        self._guardar_configuracion_menu(self.username)
        
        # Abrir juego
        self.abrir_principal()

    # ==================== VENTANA PRINCIPAL ====================
    
    def abrir_principal(self):
        """Abre VentanaPrincipal con los datos del usuario"""
        try:
            from VentanaPrincipal import VillageGameWindow
            from PaletaColores import generate_palette
            
            # Cargar datos del usuario
            datos_usuario = self._cargar_datos_usuario(self.username)
            
            if not datos_usuario:
                messagebox.showerror("Error", "No se pudieron cargar los datos del usuario")
                return
            
            # Obtener personalización Y menu_config
            personalizacion = datos_usuario.get('personalizacion', {})
            color = personalizacion.get('color', '#a4244d')
            tema = personalizacion.get('tema', 'claro')
            
            menu_config = datos_usuario.get('menu_config', {})
            nivel = menu_config.get('nivel', self.nivel_seleccionado)
            frecuencias_guardadas = menu_config.get('frecuencias', {})
            
            # Si hay frecuencias guardadas, usarlas; si no, usar las actuales
            frecuencias = frecuencias_guardadas if frecuencias_guardadas else self.get_all_frequencies()
            
            # Generar paleta
            palette = generate_palette(color, tema)
            
            print("\n" + "="*50)
            print("🎮 INICIANDO JUEGO CON CONFIGURACIÓN:")
            print("="*50)
            print(f"👤 Usuario: {self.username}")
            print(f"⚔️  Nivel: {nivel}")
            print(f"🎨 Color: {color}")
            print(f"🌓 Tema: {tema}")
            print(f"⚡ Frecuencias:")
            for nombre, valor in frecuencias.items():
                print(f"   {nombre}: {valor}")
            print("="*50 + "\n")
            
            # Cerrar menú
            self.root.withdraw()
            
            # Abrir juego con VillageGameWindow
            game_window = VillageGameWindow(
                nivel=nivel,
                frecuencias=frecuencias,
                initial_palette=palette
            )
            
            # Iniciar el loop del juego
            game_window.run()
            
            # Destruir menú después
            self.root.after(100, self.root.destroy)
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            messagebox.showerror("Error", f"No se pudo iniciar el juego:\n{e}")
            self.root.deiconify()

def main():
    root = tk.Tk()
    app = Menu(root)
    root.mainloop()

if __name__ == "__main__":
    main()