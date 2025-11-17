import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk, ImageDraw
import io
import base64
import os
from Login import cargar_usuarios

class SalonFama:
    def __init__(self, root, top_limit=10):
        self.root = root
        self.top_limit = top_limit  # Variable para cambiar entre top 5, top 10, etc.
        self.root.title(f"Salón de la Fama")
        
        # Configuración de ventana
        self.root.geometry("450x550")
        self.root.resizable(False, False)
        
        # Centrar ventana
        self.centrar_ventana()
        
        # Colores del tema
        self.colores = {
            'primario': "#8A1C32",
            'secundario': "#a10707",
            'acento': "#03a328",
            'fondo': '#f8f9fa',
            'texto': '#2c3e50',
            'texto_claro': "#8d7f7f",
            'blanco': '#ffffff',
            'verde': '#27ae60',
            'oro': '#FFD700',
            'plata': '#C0C0C0',
            'bronce': '#CD7F32'
        }
        
        # Cargar usuarios
        self.usuarios = cargar_usuarios()
        
        # Referencias de imágenes
        self._logo_img = None
        self._foto_perfil_imgs = []
        
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
        # Canvas principal con gradiente
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
        self.canvas.create_oval(40, 60, 100, 120, fill="#FFD700", stipple='gray25', outline='')
        self.canvas.create_rectangle(300, 120, 340, 160, fill='#C0C0C0', stipple='gray25', outline='')
        self.canvas.create_polygon(60, 350, 100, 350, 80, 320, fill='#CD7F32', stipple='gray25', outline='')
        
        # Contenedor con scroll
        scroll_container_frame = tk.Frame(self.root, bg='#C5C5C5', relief='flat', bd=0)
        scroll_container_frame.place(x=35, y=50, width=380, height=450)

        from tkinter import ttk
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
        
        self.crear_contenido()
    
    def _on_frame_configure(self, event):
        self.scroll_canvas.configure(scrollregion=self.scroll_canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        self.scroll_canvas.itemconfig(self.main_frame_id, width=event.width)
        self.scroll_canvas.configure(scrollregion=self.scroll_canvas.bbox("all"))

    def _on_mousewheel(self, event):
        self.scroll_canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def _circularize(self, img, size=(50, 50)):
        """Convierte una imagen a circular con transparencia"""
        img = img.convert('RGBA').resize(size, Image.LANCZOS)
        mask = Image.new('L', size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, size[0], size[1]), fill=255)
        img.putalpha(mask)
        return img

    def cargar_foto_perfil(self, usuario_data, size=(50, 50)):
        """Carga y procesa la foto de perfil del usuario"""
        try:
            foto_b64 = usuario_data.get('foto_perfil_b64', '')
            if foto_b64:
                img_data = base64.b64decode(foto_b64)
                img = Image.open(io.BytesIO(img_data))
                return self._circularize(img, size)
            else:
                # Imagen por defecto (círculo gris)
                img = Image.new('RGBA', size, (229, 231, 235, 255))
                return self._circularize(img, size)
        except Exception as e:
            print(f"Error cargando foto: {e}")
            img = Image.new('RGBA', size, (229, 231, 235, 255))
            return self._circularize(img, size)

    def crear_contenido(self):
        # Logo grande arriba
        logo_container = tk.Frame(self.main_frame, bg='#C5C5C5')
        logo_container.pack(pady=(10, 5))
        
        try:
            logo_path = os.path.join(os.path.dirname(__file__), "Logo.jpg")
            img = Image.open(logo_path).resize((200, 200), Image.LANCZOS)
            self._logo_img = ImageTk.PhotoImage(img, master=self.root)  # ← agrega master
            tk.Label(logo_container, image=self._logo_img, bg='#C5C5C5').pack()

        except Exception as e:
            print(f"No se pudo cargar Logo.jpg: {e}")
            tk.Label(logo_container, text="🏆", font=('Arial', 60), bg='#C5C5C5').pack()
        
        # Título
        tk.Label(self.main_frame, text=f"Salón de la Fama",
                font=('Segoe UI', 14, 'bold'),
                fg=self.colores['texto'], bg='#C5C5C5').pack(pady=(5, 10))
        
        # Obtener top usuarios ordenados por puntos
        usuarios_ordenados = self.obtener_top_usuarios()
        
        if not usuarios_ordenados:
            tk.Label(self.main_frame, text="No hay usuarios registrados aún",
                    font=('Segoe UI', 10),
                    fg=self.colores['texto_claro'], bg='#C5C5C5').pack(pady=20)
            return
        
        # Mostrar cada usuario
        for i, (username, datos) in enumerate(usuarios_ordenados[:self.top_limit], 1):
            self.crear_fila_usuario(i, username, datos)
        
        # Botón cerrar
        btn_cerrar = tk.Button(self.main_frame, text="Cerrar", 
                              command=self.root.destroy,
                              font=('Segoe UI', 9, 'bold'),
                              bg=self.colores['primario'], fg='white',
                              relief='flat', bd=0, pady=8, cursor='hand2')
        btn_cerrar.pack(fill='x', padx=15, pady=15)

    def obtener_top_usuarios(self):
        """Obtiene los usuarios ordenados por puntos"""
        usuarios_con_pts = []
        
        for username, datos in self.usuarios.items():
            if isinstance(datos, dict):
                pts = datos.get('pts', 0)
                usuarios_con_pts.append((username, datos, pts))
        
        # Ordenar por puntos (mayor a menor)
        usuarios_con_pts.sort(key=lambda x: x[2], reverse=True)
        
        # Retornar solo username y datos
        return [(u[0], u[1]) for u in usuarios_con_pts]

    def obtener_color_posicion(self, posicion):
        """Retorna el color según la posición"""
        if posicion == 1:
            return self.colores['oro']
        elif posicion == 2:
            return self.colores['plata']
        elif posicion == 3:
            return self.colores['bronce']
        else:
            return '#6B7280'

    def crear_fila_usuario(self, posicion, username, datos):
        """Crea una fila para un usuario en el ranking"""
        # Frame principal de la fila
        fila_frame = tk.Frame(self.main_frame, bg='white', relief='solid', bd=1)
        fila_frame.pack(fill='x', padx=15, pady=5)
        
        # Color de la posición
        color_pos = self.obtener_color_posicion(posicion)
        
        # Contenedor horizontal
        contenido = tk.Frame(fila_frame, bg='white')
        contenido.pack(fill='both', expand=True, padx=10, pady=8)
        
        # Foto de perfil (izquierda)
        foto_frame = tk.Frame(contenido, bg='white')
        foto_frame.pack(side='left', padx=(0, 10))
        
        foto_img = self.cargar_foto_perfil(datos, size=(50, 50))
        foto_photo = ImageTk.PhotoImage(foto_img, master=self.root)  # ← agrega master
        self._foto_perfil_imgs.append(foto_photo)  # mantiene referencia

                
        foto_label = tk.Label(foto_frame, image=foto_photo, bg='white')
        foto_label.image = foto_photo
        foto_label.pack()
        
        # Información del usuario (centro)
        info_frame = tk.Frame(contenido, bg='white')
        info_frame.pack(side='left', fill='both', expand=True)
        
        # Nombre completo
        nombre_completo = f"{datos.get('nombre', '')} {datos.get('apellido', '')}"
        tk.Label(info_frame, text=nombre_completo,
                font=('Segoe UI', 10, 'bold'),
                fg=self.colores['texto'], bg='white', anchor='w').pack(fill='x')
        
        # Username
        tk.Label(info_frame, text=f"@{username}",
                font=('Segoe UI', 8),
                fg=self.colores['texto_claro'], bg='white', anchor='w').pack(fill='x')
        
        # Puntos (derecha)
        puntos_frame = tk.Frame(contenido, bg='white')
        puntos_frame.pack(side='right', padx=(10, 0))
        
        # Número de posición con círculo de color
        posicion_canvas = tk.Canvas(puntos_frame, width=40, height=40, 
                                    bg='white', highlightthickness=0)
        posicion_canvas.pack()
        
        posicion_canvas.create_oval(5, 5, 35, 35, fill=color_pos, outline='')
        posicion_canvas.create_text(20, 20, text=str(posicion),
                                   font=('Segoe UI', 12, 'bold'),
                                   fill='white')
        
        # Puntos
        pts = datos.get('pts', 0)
        tk.Label(puntos_frame, text=f"{pts} pts",
                font=('Segoe UI', 9, 'bold'),
                fg=color_pos, bg='white').pack()

def main():
    root = tk.Tk()
    
    # Cambiar el número aquí para top 5, top 10, etc.
    app = SalonFama(root, top_limit=10)
    
    root.mainloop()

if __name__ == "__main__":
    print("=" * 50)
    print("🏆 Salón de la Fama - Avatars VS Rooks")
    print("=" * 50)
    main()